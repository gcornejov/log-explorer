from collections.abc import Generator
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Final

from log_filter.parser import filter_parser, FilterArgs

LOG_DATE_FMT: Final [str] = "%d/%m/%Y:%H:%M:%S +0000"


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


def valid_file(path: Path) -> bool:
    if path.is_file():
        return True

    print("Please provide a valid file path.")
    exit(0)


def main():
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
