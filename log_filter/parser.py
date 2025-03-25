from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from enum import Enum
from pathlib import Path

from log_filter import DATE_FMT


def filter_parser() -> ArgumentParser:
    def cast_path(raw_path: str) -> Path:
        path = Path(raw_path)
        if path.exists():
            return path

        raise ArgumentTypeError(f"Path {raw_path} wasn't found. It doesn't exist or you may need to grant read permissions to directory/file")

    def cast_date(raw_date: str) -> datetime:
        try:
            return datetime.strptime(raw_date, DATE_FMT)
        except ValueError:
            raise ArgumentTypeError(f"not a valid date: {raw_date!r}")

    parser = ArgumentParser(prog="log_filter")

    parser.add_argument("logs_path", type=cast_path, help="Path where the logs are located")
    parser.add_argument(
        "--single_file",
        "-f",
        action="store_true",
        dest="single_file",
        help="Use a single file (instead of a directory) to load the logs",
    )
    parser.add_argument(
        "--level",
        action="append",
        dest="log_level",
        type=str.upper,
        choices=LogLevel.get_items(),
        help="Level of the log.",
    )
    parser.add_argument(
        "--initial_timestamp",
        "-its",
        dest="initial_timestamp",
        type=cast_date,
        default="0001/01/01",
        help="Earlier date when to search logs. YYYY/MM/DD",
    )
    parser.add_argument(
        "--final_timestamp",
        "-fts",
        dest="final_timestamp",
        type=cast_date,
        default="9999/12/31",
        help="Later date when to search logs. YYYY/MM/DD",
    )

    return parser


class FilterArgs():
    logs_path: Path
    single_file: bool
    log_level: list[str]
    initial_timestamp: datetime
    final_timestamp: datetime

    def __init__(self):
        self.log_level = []


class LogLevel(Enum):
    DEBUG: str = "DEBUG"
    INFO: str = "INFO"
    WARNING: str = "WARNING"
    ERROR: str = "ERROR"

    @classmethod
    def get_items(cls) -> list[str]:
        return [cls.DEBUG.value, cls.INFO.value, cls.WARNING.value, cls.ERROR.value]
