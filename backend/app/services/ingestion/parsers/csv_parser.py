from pathlib import Path

import pandas as pd

from app.services.ingestion.parsers.base import (
    DatasetParseError,
    DatasetParser,
)


class CSVParser(DatasetParser):
    def read_frame(self, path: Path, *, max_rows: int) -> pd.DataFrame:
        try:
            return pd.read_csv(path, nrows=max_rows + 1, low_memory=False)
        except (OSError, UnicodeError, pd.errors.ParserError, ValueError) as exc:
            raise DatasetParseError("The CSV file could not be parsed") from exc
