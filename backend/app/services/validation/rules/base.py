from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

import pandas as pd

from app.domain.enums import ValidationSeverity


@dataclass(frozen=True)
class ValidationContext:
    field_sources: dict[str, str]
    unknown_columns: tuple[str, ...] = ()
    max_examples: int = 5

    def source_for(self, canonical_field: str) -> str | None:
        return self.field_sources.get(canonical_field)


@dataclass(frozen=True)
class ValidationResult:
    rule: str
    severity: ValidationSeverity
    field: str | None
    message: str
    affected_rows: frozenset[int] = field(default_factory=frozenset)
    examples: tuple[dict[str, Any], ...] = ()

    @property
    def affected_count(self) -> int:
        return len(self.affected_rows)


class ValidationRule(ABC):
    @abstractmethod
    def validate(
        self, dataframe: pd.DataFrame, context: ValidationContext
    ) -> list[ValidationResult]:
        raise NotImplementedError


def build_result(
    *,
    dataframe: pd.DataFrame,
    mask: pd.Series,
    context: ValidationContext,
    rule: str,
    severity: ValidationSeverity,
    field: str | None,
    message: str,
) -> ValidationResult | None:
    positions = frozenset(
        position for position, affected in enumerate(mask) if affected
    )
    if not positions:
        return None
    examples = tuple(
        {
            str(column): _json_safe(value)
            for column, value in dataframe.iloc[position].items()
        }
        for position in sorted(positions)[: context.max_examples]
    )
    return ValidationResult(rule, severity, field, message, positions, examples)


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (datetime, date, pd.Timestamp)):
        return value.isoformat()
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, str | int | float | bool):
        return value
    return str(value)


def nonblank(series: pd.Series) -> pd.Series:
    return series.notna() & series.astype(str).str.strip().ne("")
