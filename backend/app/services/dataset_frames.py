from pathlib import Path

import pandas as pd

from app.core.config import Settings
from app.db.models import Dataset
from app.services.ingestion.parsers import build_parser_registry
from app.services.ingestion.parsers.base import DatasetParseError


class DatasetFrameLoader:
    """Load a previously accepted dataset using the configured safety limits."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.parsers = build_parser_registry()

    def load(self, dataset: Dataset) -> pd.DataFrame:
        storage = self.settings.upload_dir.expanduser().resolve()
        filename = Path(dataset.stored_filename).name
        if filename != dataset.stored_filename:
            raise DatasetParseError("Stored dataset filename is unsafe")
        path = storage / filename
        if not path.is_file():
            raise DatasetParseError("Stored dataset file is missing")
        frame = self.parsers[dataset.file_type].read_frame(
            path,
            max_rows=self.settings.dataset_max_rows,
        )
        if len(frame.index) > self.settings.dataset_max_rows:
            raise DatasetParseError("Stored dataset exceeds the configured row limit")
        return frame
