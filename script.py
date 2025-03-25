import os
import sys
from datetime import datetime
from glob import glob
from typing import Any, Final

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


if __name__ == "__main__":
    cmd_args: list[str] = sys.argv[1:]
    filter_args: dict[str, Any] = {
        "log_level": [ level.upper() for level in cmd_args[0].split(",") ], # map(str.upper, cmd_args[0].split(","))
        "initial_timestamp": datetime.strptime(cmd_args[1], DATE_FMT),
        "final_timestamp": datetime.strptime(cmd_args[2], DATE_FMT),
        "logs_path": cmd_args[3],
    }

    logs_file_pattern: str = os.path.join(filter_args["logs_path"], "*.log")
    log_files: list[str] = glob(logs_file_pattern)
    
    logs: list[LogEntry] = []
    for file in log_files:
        with open(file) as f:
            logs.extend(
                [ LogEntry(entry) for entry in f.readlines() ]
            )

    logs = filter_log_level(logs, filter_args["log_level"])
    logs = filter_timestamp_between(logs, filter_args["initial_timestamp"], filter_args["final_timestamp"])

    print("\n".join(map(str, logs)))
    print(len(logs))
