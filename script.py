import os
from argparse import ArgumentParser, Namespace
from datetime import datetime
from glob import glob
from textwrap import dedent
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


class FilterArgs:
    log_level: list[str]
    initial_timestamp: datetime
    final_timestamp: datetime
    logs_path: str

    def __init__(self, cmd_args: list[str]):
        try:
            self.log_level = [ level.upper() for level in cmd_args[0].split(",") ] # map(str.upper, cmd_args[0].split(","))
            self.initial_timestamp = datetime.strptime(cmd_args[1], DATE_FMT)
            self.final_timestamp = datetime.strptime(cmd_args[2], DATE_FMT)
            self.logs_path = cmd_args[3]
        except (IndexError, ValueError):
            print(
                dedent("""
                    Missing arguments or incorrect format, pass them as follows:
                        LOG_LEVEL1[,LOG_LEVEL2,...] initial_timestamp final_timestamp logs_path

                        * Date format: YYYY/MM/DD
                """)
            )
            exit(1)


def filter_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="log_filter")

    parser.add_argument("logs_path", help="Path where the log files are located")
    parser.add_argument(
        "--level",
        dest="log_level",
        help="Level of the log.",
    )
    parser.add_argument(
        "--initial_timestamp",
        "-its",
        dest="initial_timestamp",
        help="Earlier date when to search logs. YYYY/MM/DD",
    )
    parser.add_argument(
        "--final_timestamp",
        "-fts",
        dest="final_timestamp",
        help="Later date when to search logs. YYYY/MM/DD",
    )

    return parser


if __name__ == "__main__":
    parser: ArgumentParser = filter_parser()
    filter_args: Namespace = parser.parse_args()

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
