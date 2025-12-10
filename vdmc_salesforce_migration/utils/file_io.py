import os
import json
from pathlib import Path
import pandas as pd
from vdmc_salesforce_migration.utils.config_loader import get_input_dir, get_mappings_dir
input_dir = get_input_dir()
mappings_dir = get_mappings_dir()

class FileLoadError(Exception):
    pass


def project_root() -> Path:
    """Return the project root directory (one level above package)."""
    return Path(__file__).resolve().parent.parent.parent


def load_mapping(name: str) -> dict:
    """
    Load a JSON mapping file from the /mappings folder at project root.
    """
    mapping_path = project_root() / mappings_dir / name

    if not mapping_path.exists():
        raise FileLoadError(f"Mapping file not found: {mapping_path}")

    with open(mapping_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_latest_file(folder: Path, pattern: str) -> str:
    """
    Find the newest file in a folder matching a pattern.
    Example: pattern="account" finds latest account*.csv file.
    """
    files = [f for f in folder.iterdir() if pattern in f.name]

    if not files:
        raise FileLoadError(f"No files found in {folder} matching pattern '{pattern}'")

    latest = max(files, key=lambda x: x.stat().st_mtime)
    return latest


def load_table_mapping(mapping_file: str, table_name: str) -> dict:
    """
    Load a single mapping for a specific table.
    Example: returns mapping['Account'] from account.json
    """

    mapping = load_mapping(mapping_file)

    if table_name not in mapping:
        raise FileLoadError(
            f"Table '{table_name}' not found in mapping file '{mapping_file}'. "
            f"Available tables: {list(mapping.keys())}"
        )

    return mapping[table_name]


def load_file_with_mapping(pattern: str, mapping_file: str, table_name: str) -> pd.DataFrame:
    """
    Load the newest CSV file matching pattern and apply a mapping.
    """

    input_path = project_root() / input_dir
    newest_file = get_latest_file(input_path, pattern)

    df = pd.read_csv(newest_file)

    # Extract only the mapping for the specific table
    mapping = load_table_mapping(mapping_file, table_name)

    # Restrict to the keys that exist in the mapping
    source_fields = list(mapping.keys())

    missing_fields = [f for f in source_fields if f not in df.columns]
    if missing_fields:
        raise FileLoadError(f"Missing fields in CSV: {missing_fields}")

    df = df[source_fields]

    # Apply Salesforce renaming
    df = df.rename(columns=mapping)

    return df
