import csv
import datetime
from pathlib import Path

def ensure_directory(path: Path):
    """
    Ensure a directory exists, create it if missing.
    """
    path.mkdir(parents=True, exist_ok=True)


def get_log_file(base_dir: Path, object_name: str, prefix: str, env: str) -> Path:
    """
    Construct a log file path like:
      logs/preview/id_write_Account_1712345678.csv
    """
    timestamp = int(datetime.datetime.now().timestamp())
    env_dir = base_dir / env

    ensure_directory(env_dir)

    filename = f"{prefix}_{object_name}_{timestamp}.csv"
    return env_dir / filename


def init_csv_log(file_path: Path, header: list):
    """
    Create a CSV file with header (only if missing).
    """
    if not file_path.exists():
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)


def append_csv_row(file_path: Path, row: list):
    """
    Append one row to an existing CSV file.
    """
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)
