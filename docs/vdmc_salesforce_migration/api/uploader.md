Module vdmc_salesforce_migration.api.uploader
=============================================

Functions
---------

`activate_assets_via_api(client, order_ids: list)`
:   Triggers Salesforce standard action createOrUpdateAssetFromOrder
    for a list of OrderIds.
    
    Logs failures to logs/<env>/order_to_asset_<timestamp>.csv.

`chunk_data(data, num_chunks)`
:   Split data evenly into <num_chunks> chunks.

`cleanup_sobject(client: simple_salesforce.api.Salesforce, object_name: str)`
:   Full cleanup flow for an sObject:
      1. Query all records
      2. Deactivate (Order only)
      3. Bulk delete with decreasing batch sizes:
         10k → 100 → 10 → 1
      4. Log progress consistently

`deactivate_records(client, object_name, data)`
:   Bulk-update Order records to Status = Draft before deletion.
    (Legacy logic preserved)

`delete_from_sf_bulk(client: simple_salesforce.api.Salesforce, object_name: str, data: List[Dict[str, Any]], batch_size: int = 10000)`
:   Bulk delete via Bulk API 2.0.
    
    Writes failed rows into a CSV file in logs/<env>/errors_<object>_<timestamp>.csv

`update_to_sf_bulk(client: simple_salesforce.api.Salesforce, object_name: str, data: List[Dict[str, Any]], external_identifier: str = None, batch_size: int = 10000)`
:   Bulk update via Bulk API 2.0.

`upload_rest_chunk(env, chunk, object_name, external_id, id_field)`
:   Worker function run in a thread.
    Creates its own Salesforce client and uploads a chunk.

`upload_rest_parallel(object_name: str, data: list, external_identifier: str = None, id_field: str = None, num_threads: int = 4, env: str = None)`
:   Parallel REST upload using multiple threads.

`upload_to_sf_bulk(client: simple_salesforce.api.Salesforce, object_name: str, data: List[Dict[str, Any]], external_identifier: str = None, batch_size: int = 10000)`
:   Uploads records using the BULK API 2.0 (simple_salesforce.bulk2).
    Logs failed rows to error CSVs.

`upload_to_sf_rest(client: simple_salesforce.api.Salesforce, object_name: str, data: List[Dict[str, Any]], external_identifier: str = None, id_field: str = None)`
:   Uploads records using the REST API (simple_salesforce) as some objects are not supported via BULK.
    Writes success/error rows to a per-env log file.