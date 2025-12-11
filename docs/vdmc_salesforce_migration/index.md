Module vdmc_salesforce_migration
================================
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

Sub-modules
-----------
* vdmc_salesforce_migration.api
* vdmc_salesforce_migration.credentials
* vdmc_salesforce_migration.utils

Functions
---------

`activate_assets_via_api(client, order_ids: list)`
:   Triggers Salesforce standard action createOrUpdateAssetFromOrder
    for a list of OrderIds.
    
    Logs failures to logs/<env>/order_to_asset_<timestamp>.csv.

`clean_emails(df: pandas.core.frame.DataFrame, field_name: str) ‑> pandas.core.frame.DataFrame`
:   Ensure field contains valid single emails only.

`clean_numeric_fields(df: pandas.core.frame.DataFrame) ‑> pandas.core.frame.DataFrame`
:   Coerce numeric-looking columns into clean floats and replace invalid values.

`cleanup_sobject(client: simple_salesforce.api.Salesforce, object_name: str)`
:   Full cleanup flow for an sObject:
      1. Query all records
      2. Deactivate (Order only)
      3. Bulk delete with decreasing batch sizes:
         10k → 100 → 10 → 1
      4. Log progress consistently

`clear_fields(df: pandas.core.frame.DataFrame) ‑> pandas.core.frame.DataFrame`
:   Apply sanitization to all object fields and clean numerics.

`convert_datetime(df: pandas.core.frame.DataFrame, fieldname: str) ‑> pandas.core.frame.DataFrame`
:   Converts a datetime column into Salesforce-compatible UTC ISO format.

`deactivate_records(client, object_name, data)`
:   Bulk-update Order records to Status = Draft before deletion.
    (Legacy logic preserved)

`extract_email(value: Any) ‑> List[str]`
:   Extract valid email addresses from a string.

`extract_email_from_field(df: pandas.core.frame.DataFrame, field: str) ‑> pandas.core.frame.DataFrame`
:   Extract an email address from a specific field.

`get_default_env() ‑> str`
:   

`get_external_by_sf_id(client: simple_salesforce.api.Salesforce, object_name: str, external_id_field: str = 'vDMC_SugarExternalId__c') ‑> Dict[Any, Any]`
:   Returns mapping[SalesforceId] = external_id.
    Useful for reverse lookup or delta loads.

`get_field_map(client: simple_salesforce.api.Salesforce, object_name: str, key_field: str, value_field: str, where: str = None) ‑> Dict[Any, Any]`
:   Universal helper:
    Returns mapping[key_field] = value_field for any object.
    
    Examples:
    get_field_map(client, "Product2", "StockKeepingUnit", "Id")

`get_latest_file(folder: pathlib.Path, pattern: str) ‑> str`
:   Find the newest file in a folder matching a pattern.
    Example: pattern="account" finds latest account*.csv file.

`get_record_types(client: simple_salesforce.api.Salesforce, object_name: str) ‑> Dict[str, str]`
:   Returns mapping[DeveloperName] = RecordTypeId for a given sObject.

`get_salesforce_client()`
:   Creates a Salesforce client using only environment variables.
    Automatically detects sandbox vs production.
    Automatically fetches the latest API version.

`get_session_id()`
:   Returns a Salesforce session ID and instance URL.
    Useful for Postman or manual API testing.

`get_sf_id_by_external(client: simple_salesforce.api.Salesforce, object_name: str, external_id_field: str = 'vDMC_SugarExternalId__c') ‑> Dict[Any, Any]`
:   Returns mapping[external_id] = SalesforceId.
    Works for any object + any external ID field.

`join_related_fields(row: Dict[str, Any], fields: List[str], lookup: Dict[str, str]) ‑> str`
:   Joins multiple fields into one string.

`load_config()`
:   Loads config.yaml from the package root directory and caches it.

`load_file_with_mapping(pattern: str, mapping_file: str, table_name: str) ‑> pandas.core.frame.DataFrame`
:   Load the newest CSV file matching pattern and apply a mapping.

`load_mapping(name: str) ‑> dict`
:   Load a JSON mapping file from the /mappings folder at project root.

`query_all_records(client, object_name)`
:   Queries all Ids from an sObject and structures them for Bulk API.

`query_to_map(client: simple_salesforce.api.Salesforce, soql: str, key_field: str, value_field: str) ‑> Dict[Any, Any]`
:   Execute SOQL and return a dict mapping {key_field: value_field}.
    Supports nested fields using dot notation.

`query_to_nested_map(client: simple_salesforce.api.Salesforce, soql: str, outer_key: str, inner_key: str, value_field: str) ‑> Dict[Any, Dict[Any, Any]]`
:   Execute SOQL and return nested mapping:
        {
            outer_key_value: {
                inner_key_value: value
            }
        }

`replace_ids_in_list(value: Any, id_map: Dict[str, str]) ‑> str`
:   Replace semicolon-separated values using a lookup map.

`replace_text(text: Any, mapping: Dict[str, str]) ‑> str`
:   Replaces text based on a mapping dictionary.

`sanitize_field(value: Any) ‑> str`
:   Remove invalid characters, normalize spacing, and strip.

`update_to_sf_bulk(client: simple_salesforce.api.Salesforce, object_name: str, data: List[Dict[str, Any]], external_identifier: str = None, batch_size: int = 10000)`
:   Bulk update via Bulk API 2.0.

`upload_rest_parallel(object_name: str, data: list, external_identifier: str = None, id_field: str = None, num_threads: int = 4, env: str = None)`
:   Parallel REST upload using multiple threads.

`upload_to_sf_bulk(client: simple_salesforce.api.Salesforce, object_name: str, data: List[Dict[str, Any]], external_identifier: str = None, batch_size: int = 10000)`
:   Uploads records using the BULK API 2.0 (simple_salesforce.bulk2).
    Logs failed rows to error CSVs.

`upload_to_sf_rest(client: simple_salesforce.api.Salesforce, object_name: str, data: List[Dict[str, Any]], external_identifier: str = None, id_field: str = None)`
:   Uploads records using the REST API (simple_salesforce) as some objects are not supported via BULK.
    Writes success/error rows to a per-env log file.