import os
from collections.abc import Sequence
from datetime import datetime
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


def filter_log_level(log_entries: list[LogEntry], log_level: str | Sequence[str]) -> list[LogEntry]:
    if isinstance(log_level, str):
        log_level: tuple[str] = (log_level, )

    return [entry for entry in log_entries if entry.log_level in log_level]

def filter_timestamp_gt(log_entries: list[LogEntry], timestamp: str | datetime) -> list[LogEntry]:
    if isinstance(timestamp, str):
        timestamp: datetime = datetime.strptime(timestamp, DATE_FMT)

    return [entry for entry in log_entries if entry.timestamp >= timestamp]

def filter_timestamp_lt(log_entries: list[LogEntry], timestamp: str | datetime) -> list[LogEntry]:
    if isinstance(timestamp, str):
        timestamp: datetime = datetime.strptime(timestamp, DATE_FMT)

    return [entry for entry in log_entries if entry.timestamp <= timestamp]


def filter_timestamp_between(log_entries: list[LogEntry], initial_ts: str | datetime, final_ts: str | datetime) -> list[LogEntry]:
    if isinstance(initial_ts, str):
        initial_ts: datetime = datetime.strptime(initial_ts, DATE_FMT)
    
    if isinstance(final_ts, str):
        final_ts: datetime = datetime.strptime(final_ts, DATE_FMT)

    return [entry for entry in log_entries if (initial_ts <= entry.timestamp <= final_ts)]


if __name__ == "__main__":
    logs_dir: str = "logs"
    logs_file_pattern: str = os.path.join(logs_dir, "*.log")

    log_files: list[str] = glob(logs_file_pattern)
    logs: list[LogEntry] = []
    for file in log_files:
        with open(file) as f:
            logs.extend(
                [ LogEntry(entry) for entry in f.readlines() ]
            )

    logs = filter_log_level(logs, ("INFO", "ERROR"))
    logs = filter_timestamp_between(logs, "2025/03/22", "2025/03/24")

    print("\n".join(map(str, logs)))
    print(len(logs))
