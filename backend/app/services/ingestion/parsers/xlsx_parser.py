from pathlib import Path
from xml.etree.ElementTree import ParseError
from zipfile import BadZipFile

import pandas as pd
from openpyxl.utils.exceptions import InvalidFileException

from app.services.ingestion.parsers.base import (
    DatasetParseError,
    DatasetParser,
)


class XLSXParser(DatasetParser):
    def read_frame(self, path: Path, *, max_rows: int) -> pd.DataFrame:
        try:
            return pd.read_excel(path, engine="openpyxl", nrows=max_rows + 1)
        except (
            OSError,
            ValueError,
            KeyError,
            BadZipFile,
            InvalidFileException,
            ParseError,
        ) as exc:
            raise DatasetParseError("The XLSX file could not be parsed") from exc
