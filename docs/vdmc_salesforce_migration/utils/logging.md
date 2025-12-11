Module vdmc_salesforce_migration.utils.logging
==============================================

Functions
---------

`append_csv_row(file_path: pathlib.Path, row: list)`
:   Append one row to an existing CSV file.

`ensure_directory(path: pathlib.Path)`
:   Ensure a directory exists, create it if missing.

`get_log_file(base_dir: pathlib.Path, object_name: str, prefix: str, env: str) ‑> pathlib.Path`
:   Construct a log file path like:
      logs/preview/id_write_Account_1712345678.csv

`init_csv_log(file_path: pathlib.Path, header: list)`
:   Create a CSV file with header (only if missing).