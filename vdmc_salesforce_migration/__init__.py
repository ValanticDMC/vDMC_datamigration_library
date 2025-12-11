"""
vdmc_salesforce_migration
Internal Salesforce migration helper library for VDMC.

This file exposes the public API for:
- Authentication
- Config access
- File loading
- Data cleaning
- SOQL lookup helpers
- Uploading (REST, Bulk, parallel)
- Asset activation API
"""

# ------------------------------------------------------
# Authentication
# ------------------------------------------------------
from .api.auth import (
    get_salesforce_client,
    get_session_id,
)

# ------------------------------------------------------
# Config
# ------------------------------------------------------
from .utils.config_loader import (
    load_config,
    get_default_env,
)

# ------------------------------------------------------
# File Handling
# ------------------------------------------------------
from .utils.file_io import (
    load_mapping,
    load_file_with_mapping,
    get_latest_file,
)

# ------------------------------------------------------
# Data Cleaning
# ------------------------------------------------------
from .utils.cleaning import (
    clear_fields,
    convert_datetime,
    clean_emails,
    sanitize_field,
    extract_email,
    extract_email_from_field,
    clean_numeric_fields,
    replace_text,
    replace_ids_in_list,
    join_related_fields,
)

# ------------------------------------------------------
# SOQL Utilities
# ------------------------------------------------------
from .utils.soql import (
    query_to_nested_map,
    query_to_map,
    get_field_map,
    get_external_by_sf_id,
    get_sf_id_by_external,
    get_record_types,
    query_all_records
)

# ------------------------------------------------------
# Upload Utilities
# ------------------------------------------------------
from .api.uploader import (
    upload_to_sf_rest,
    upload_to_sf_bulk,
    update_to_sf_bulk,
    upload_rest_parallel,
    activate_assets_via_api,
    deactivate_records,
    cleanup_sobject
)

# ------------------------------------------------------
# Public API
# ------------------------------------------------------
__all__ = [
    # Authentication
    "get_salesforce_client",
    "get_session_id",

    # Config
    "load_config",
    "get_default_env",

    # File IO
    "load_mapping",
    "load_file_with_mapping",
    "get_latest_file",

    # Cleaning
    "clear_fields",
    "convert_datetime",
    "clean_emails",
    "sanitize_field",
    "extract_email",
    "extract_email_from_field",
    "clean_numeric_fields",
    "replace_text",
    "replace_ids_in_list",
    "join_related_fields",

    # SOQL
    "query_to_nested_map",
    "query_to_map",
    "get_field_map",
    "get_external_by_sf_id",
    "get_sf_id_by_external",
    "get_record_types",
    "query_all_records",

    # Upload
    "upload_to_sf_rest",
    "upload_to_sf_bulk",
    "update_to_sf_bulk",
    "upload_rest_parallel",
    "activate_assets_via_api",
    "deactivate_records",
    "cleanup_sobject"
]
