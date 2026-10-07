from pathlib import Path

import pandas as pd

from app.services.ingestion.parsers.base import (
    DatasetParseError,
    DatasetParser,
)


class JSONParser(DatasetParser):
    def read_frame(self, path: Path, *, max_rows: int) -> pd.DataFrame:
        try:
            frame = pd.read_json(path)
        except ValueError:
            try:
                frame = pd.read_json(path, lines=True, nrows=max_rows + 1)
            except (OSError, UnicodeError, ValueError) as exc:
                raise DatasetParseError("The JSON file could not be parsed") from exc
        except (OSError, UnicodeError) as exc:
            raise DatasetParseError("The JSON file could not be parsed") from exc
        return frame
