from app.domain.enums import DatasetFileType
from app.services.ingestion.parsers.base import DatasetParser
from app.services.ingestion.parsers.csv_parser import CSVParser
from app.services.ingestion.parsers.json_parser import JSONParser
from app.services.ingestion.parsers.xlsx_parser import XLSXParser


def build_parser_registry() -> dict[DatasetFileType, DatasetParser]:
    return {
        DatasetFileType.CSV: CSVParser(),
        DatasetFileType.JSON: JSONParser(),
        DatasetFileType.XLSX: XLSXParser(),
    }


__all__ = ["DatasetParser", "build_parser_registry"]
