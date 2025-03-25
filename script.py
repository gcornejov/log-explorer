import os
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from enum import Enum
from glob import glob
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
    return [entry for entry in log_entries if entry.log_level in log_level]


def filter_timestamp_gt(log_entries: list[LogEntry], timestamp: datetime) -> list[LogEntry]:
    return [entry for entry in log_entries if entry.timestamp >= timestamp]


def filter_timestamp_lt(log_entries: list[LogEntry], timestamp: datetime) -> list[LogEntry]:
    return [entry for entry in log_entries if entry.timestamp <= timestamp]


def filter_timestamp_between(log_entries: list[LogEntry], initial_ts: datetime, final_ts: datetime) -> list[LogEntry]:
    return [entry for entry in log_entries if (initial_ts <= entry.timestamp <= final_ts)]


class FilterArgs():
    logs_path: str
    log_level: list[str]
    initial_timestamp: datetime
    final_timestamp: datetime

    def __init__(self):
        self.log_level = []


def filter_parser() -> ArgumentParser:
    def cast_date(raw_date: str) -> datetime:
        try:
            return datetime.strptime(raw_date, DATE_FMT)
        except ValueError:
            raise ArgumentTypeError(f"not a valid date: {raw_date!r}")

    parser = ArgumentParser(prog="log_filter")

    parser.add_argument("logs_path", help="Path where the log files are located")
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
        help="Earlier date when to search logs. YYYY/MM/DD",
    )
    parser.add_argument(
        "--final_timestamp",
        "-fts",
        dest="final_timestamp",
        type=cast_date,
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


if __name__ == "__main__":
    parser: ArgumentParser = filter_parser()
    filter_args: FilterArgs = parser.parse_args(namespace=FilterArgs())

    logs_file_pattern: str = os.path.join(filter_args.logs_path, "*.log")
    log_files: list[str] = glob(logs_file_pattern)
    
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
