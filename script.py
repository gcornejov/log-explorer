from collections.abc import Generator
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Final

LOG_DATE_FMT: Final [str] = "%d/%m/%Y:%H:%M:%S +0000"
DATE_FMT: Final[str] = "%Y/%m/%d"

class LogEntry:
    raw_entry: str
    timestamp: datetime
    log_level: str
    message: str

    def __init__(self, raw_log_entry: str):
        self.raw_entry = raw_log_entry[:-1]

        raw_log_entry = self.raw_entry.replace('"', "")
        _, raw_log_entry = raw_log_entry.split(" - - [")

        raw_timestamp, raw_log_entry = raw_log_entry.split("] ")
        self.timestamp = datetime.strptime(raw_timestamp, LOG_DATE_FMT)

        (
            *_,
            self.log_level,
            self.message
        ) = raw_log_entry.split(" ", maxsplit=6)
    
    def __repr__(self):
        return self.raw_entry


def filter_log_level(log_entries: list[LogEntry], log_level: list[str]) -> list[LogEntry]:
    if not log_level:
        return log_entries

    return [entry for entry in log_entries if entry.log_level in log_level]


def filter_timestamp_gt(log_entries: list[LogEntry], timestamp: datetime) -> list[LogEntry]:
    return [entry for entry in log_entries if entry.timestamp >= timestamp]


def filter_timestamp_lt(log_entries: list[LogEntry], timestamp: datetime) -> list[LogEntry]:
    return [entry for entry in log_entries if entry.timestamp <= timestamp]


def filter_timestamp_between(log_entries: list[LogEntry], initial_ts: datetime, final_ts: datetime) -> list[LogEntry]:
    return [entry for entry in log_entries if (initial_ts <= entry.timestamp <= final_ts)]


class FilterArgs():
    logs_path: Path
    single_file: bool
    log_level: list[str]
    initial_timestamp: datetime
    final_timestamp: datetime

    def __init__(self):
        self.log_level = []


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


class LogLevel(Enum):
    DEBUG: str = "DEBUG"
    INFO: str = "INFO"
    WARNING: str = "WARNING"
    ERROR: str = "ERROR"

    @classmethod
    def get_items(cls) -> list[str]:
        return [cls.DEBUG.value, cls.INFO.value, cls.WARNING.value, cls.ERROR.value]


def valid_file(path: Path) -> bool:
    if path.is_file():
        return True

    print("Please provide a valid file path.")
    exit(0)


if __name__ == "__main__":
    parser: ArgumentParser = filter_parser()
    filter_args: FilterArgs = parser.parse_args(namespace=FilterArgs())

    log_files: tuple[Path] | Generator[Path] = []
    if filter_args.single_file and valid_file(filter_args.logs_path):
        log_files = (filter_args.logs_path,)
    else:
        log_files = filter_args.logs_path.glob("*.log")
    
    logs: list[LogEntry] = []
    for file in log_files:
        with open(file) as f:
            logs.extend(
                [ LogEntry(entry) for entry in f.readlines() ]
            )

    logs = filter_log_level(logs, filter_args.log_level)
    logs = filter_timestamp_between(logs, filter_args.initial_timestamp, filter_args.final_timestamp)

    print("\n".join(map(str, logs)))
    print(len(logs))
