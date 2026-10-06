import logging
from logging.config import dictConfig
from typing import Any


def configure_logging(level: str = "INFO") -> None:
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"handlers": ["default"], "level": level},
    }
    dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
