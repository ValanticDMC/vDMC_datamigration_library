Module vdmc_salesforce_migration.utils.file_io
==============================================

Functions
---------

`get_latest_file(folder: pathlib.Path, pattern: str) ‑> str`
:   Find the newest file in a folder matching a pattern.
    Example: pattern="account" finds latest account*.csv file.

`load_file_with_mapping(pattern: str, mapping_file: str, table_name: str) ‑> pandas.core.frame.DataFrame`
:   Load the newest CSV file matching pattern and apply a mapping.

`load_mapping(name: str) ‑> dict`
:   Load a JSON mapping file from the /mappings folder at project root.

`load_table_mapping(mapping_file: str, table_name: str) ‑> dict`
:   Load a single mapping for a specific table.
    Example: returns mapping['Account'] from account.json

`project_root() ‑> pathlib.Path`
:   Return the project root directory (one level above package).

Classes
-------

`FileLoadError(*args, **kwargs)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException