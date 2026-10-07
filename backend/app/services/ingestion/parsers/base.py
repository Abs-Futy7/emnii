from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api import types as pandas_types


class DatasetParseError(ValueError):
    pass


class DatasetRowLimitError(DatasetParseError):
    pass


@dataclass(frozen=True)
class ParsedColumn:
    source_name: str
    detected_type: str
    sample_values: list[Any]
    null_count: int
    unique_count: int


@dataclass(frozen=True)
class ParsedDataset:
    row_count: int
    column_count: int
    columns: list[ParsedColumn]


class DatasetParser(ABC):
    def parse(
        self,
        path: Path,
        *,
        max_rows: int,
        sample_size: int,
    ) -> ParsedDataset:
        frame = self.read_frame(path, max_rows=max_rows)
        return self.analyze_frame(
            frame,
            max_rows=max_rows,
            sample_size=sample_size,
        )

    @abstractmethod
    def read_frame(self, path: Path, *, max_rows: int) -> pd.DataFrame:
        raise NotImplementedError

    def analyze_frame(
        self,
        frame: pd.DataFrame,
        *,
        max_rows: int,
        sample_size: int,
    ) -> ParsedDataset:
        if len(frame.index) > max_rows:
            raise DatasetRowLimitError(
                f"Dataset exceeds the maximum of {max_rows:,} rows"
            )
        if len(frame.columns) == 0:
            raise DatasetParseError("Dataset does not contain any columns")

        columns: list[ParsedColumn] = []
        for position, raw_name in enumerate(frame.columns):
            source_name = str(raw_name)
            if not source_name or len(source_name) > 255:
                raise DatasetParseError(
                    "Column names must contain between 1 and 255 characters"
                )
            series = frame.iloc[:, position]
            samples = [
                self._json_value(value)
                for value in series.dropna().head(sample_size).tolist()
            ]
            columns.append(
                ParsedColumn(
                    source_name=source_name,
                    detected_type=self._detect_type(series),
                    sample_values=samples,
                    null_count=int(series.isna().sum()),
                    unique_count=int(series.nunique(dropna=True)),
                )
            )

        return ParsedDataset(
            row_count=len(frame.index),
            column_count=len(frame.columns),
            columns=columns,
        )

    @staticmethod
    def _detect_type(series: pd.Series) -> str:
        dtype = series.dtype
        if pandas_types.is_bool_dtype(dtype):
            return "boolean"
        if pandas_types.is_integer_dtype(dtype):
            return "integer"
        if pandas_types.is_float_dtype(dtype):
            return "number"
        if pandas_types.is_datetime64_any_dtype(dtype):
            return "datetime"
        if pandas_types.is_string_dtype(dtype):
            return "string"
        return "object"

    @staticmethod
    def _json_value(value: Any) -> Any:
        if isinstance(value, (datetime, date, pd.Timestamp)):
            return value.isoformat()
        if hasattr(value, "item"):
            value = value.item()
        if isinstance(value, str | int | float | bool) or value is None:
            return value
        return str(value)
