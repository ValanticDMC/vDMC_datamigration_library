from simple_salesforce import Salesforce
from pathlib import Path
from typing import List, Dict, Any
from vdmc_salesforce_migration.utils.logging import (
    get_log_file,
    init_csv_log,
    append_csv_row
)
from vdmc_salesforce_migration.utils.config_loader import get_log_dir, get_default_env, get_default_batch_size
from vdmc_salesforce_migration.api.auth import get_salesforce_client
from vdmc_salesforce_migration import query_all_records
import requests
import math
from concurrent.futures import ThreadPoolExecutor

root_dir = Path(__file__).resolve().parent.parent.parent
log_dir = root_dir / get_log_dir()
env = get_default_env()
default_batch_size = get_default_batch_size()

# ---------------------------------------------------------------------------
# REST API upload (single-record operations, slow but precise)
# ---------------------------------------------------------------------------
def upload_to_sf_rest(
    client: Salesforce,
    object_name: str,
    data: List[Dict[str, Any]],
    external_identifier: str = None,
    id_field: str = None,
):
    """
    Uploads records using the REST API (simple_salesforce) as some objects are not supported via BULK.
    Writes success/error rows to a per-env log file.
    """

    log_base = Path(log_dir)
    log_file = get_log_file(
        base_dir=log_base,
        object_name=object_name,
        prefix="id_write",
        env=env
    )
    init_csv_log(log_file, ["external_id", "sf_id", "success", "errors"])

    sf_object = getattr(client, object_name)

    for index, record in enumerate(data, start=1):

        external_value = record.get(id_field, "") if id_field else ""

        # Remove the external id field from payload
        payload = {k: v for k, v in record.items() if k != id_field and v not in ["", None]}

        try:
            if external_identifier:
                result = sf_object.upsert(
                    record_id=external_identifier,
                    data=payload
                )
            else:
                result = sf_object.create(payload)

        except Exception as e:
            append_csv_row(log_file, [external_value, "", False, f"Exception: {e}"])
            if "REQUEST_LIMIT_EXCEEDED" in str(e) or "429" in str(e):
                raise
            continue

        sf_id = result.get("id")
        success = result.get("success", True)
        errors = ";".join(result.get("errors", []))

        append_csv_row(log_file, [external_value, sf_id, success, errors])

    print(f"[REST] Upload done for {object_name}. Log file: {log_file}")


# ---------------------------------------------------------------------------
# BULK API 2.0 upsert or insert
# ---------------------------------------------------------------------------
def upload_to_sf_bulk(
    client: Salesforce,
    object_name: str,
    data: List[Dict[str, Any]],
    external_identifier: str = None,
    batch_size: int = default_batch_size,
):
    """
    Uploads records using the BULK API 2.0 (simple_salesforce.bulk2).
    Logs failed rows to error CSVs.
    """

    sf_object = client.bulk2.__getattr__(object_name)

    if external_identifier:
        results = sf_object.upsert(records=data, external_id_field=external_identifier, batch_size=batch_size)
    else:
        results = sf_object.insert(records=data, batch_size=batch_size)

    # Log failures
    log_base = Path(log_dir)

    for job in results:
        job_id = job["job_id"]
        error_file = get_log_file(log_base, object_name, "errors", env)
        sf_object.get_failed_records(job_id, file=str(error_file))

    print(f"[BULK] Upload done for {object_name}. Errors logged to {log_dir}/{env}/")


# ---------------------------------------------------------------------------
# BULK update
# ---------------------------------------------------------------------------
def update_to_sf_bulk(
    client: Salesforce,
    object_name: str,
    data: List[Dict[str, Any]],
    external_identifier: str = None,
    batch_size: int = default_batch_size,
):
    """
    Bulk update via Bulk API 2.0.
    """

    sf_object = client.bulk2.__getattr__(object_name)

    if external_identifier:
        results = sf_object.update(records=data, external_id_field=external_identifier, batch_size=batch_size)
    else:
        results = sf_object.update(records=data, batch_size=batch_size)

    log_base = Path(log_dir)

    for job in results:
        job_id = job["job_id"]
        error_file = get_log_file(log_base, object_name, "errors", env)
        sf_object.get_failed_records(job_id, file=str(error_file))

    print(f"[BULK] Update done for {object_name}. Errors logged to {log_dir}/{env}/")


def _get_salesforce_base_url(client) -> str:
    """
    Extracts the base Salesforce instance URL from the simple_salesforce client.
    Works for:
      - Production
      - Sandboxes
      - Hyperforce PODs
    """
    # client.base_url = "<instance>/services/data/vXX.X/"
    return client.base_url.split("/services")[0]


def activate_assets_via_api(
    client,
    order_ids: list
):
    """
    Triggers Salesforce standard action createOrUpdateAssetFromOrder
    for a list of OrderIds.

    Logs failures to logs/<env>/order_to_asset_<timestamp>.csv.
    """

    # -------------------------------------------------------------
    # Use existing authenticated client session (NO second login!)
    # -------------------------------------------------------------
    session_id = client.session_id

    # client.base_url is always correct (sandbox / prod / hyperforce)
    base_url = client.base_url.split("/services")[0]
    endpoint = f"{base_url}/services/data/v65.0/actions/standard/createOrUpdateAssetFromOrder"

    headers = {
        "Authorization": f"Bearer {session_id}",
        "Content-Type": "application/json"
    }

    # -------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------
    log_file = get_log_file(
        base_dir=Path(log_dir),
        object_name="order_to_asset",
        prefix="errors",
        env=env
    )
    init_csv_log(log_file, ["order_id", "errors"])

    total = len(order_ids)

    # -------------------------------------------------------------
    # Loop over orders
    # -------------------------------------------------------------
    for idx, order_id in enumerate(order_ids, start=1):
        print(f"{idx}/{total} ({idx / total:.1%}) – Order {order_id}")

        payload = { "inputs": [ { "orderId": order_id } ] }

        response = requests.post(endpoint, headers=headers, json=payload)

        # Error logging
        if response.status_code >= 300:
            append_csv_row(log_file, [order_id, response.text])

    print(f"[Asset Activation] Complete. Errors logged to {log_file}")


def chunk_data(data, num_chunks):
    """
    Split data evenly into <num_chunks> chunks.
    """
    size = math.ceil(len(data) / num_chunks)
    return [data[i:i+size] for i in range(0, len(data), size)]

def upload_rest_chunk(env, chunk, object_name, external_id, id_field):
    """
    Worker function run in a thread.
    Creates its own Salesforce client and uploads a chunk.
    """
    client = get_salesforce_client(env)
    upload_to_sf_rest(
        client=client,
        object_name=object_name,
        data=chunk,
        external_identifier=external_id,
        id_field=id_field,
        env=env
    )


def upload_rest_parallel(
    object_name: str,
    data: list,
    external_identifier: str = None,
    id_field: str = None,
    num_threads: int = 4,
    env: str = None
):
    """
    Parallel REST upload using multiple threads.
    """
    if env is None:
        env = get_default_env()

    chunks = chunk_data(data, num_threads)

    print(f"▶ Starting parallel REST upload with {num_threads} threads…")
    print(f"▶ Total records: {len(data)} | Chunks: {len(chunks)}")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(
                upload_rest_chunk,
                env,
                chunk,
                object_name,
                external_identifier,
                id_field
            )
            for chunk in chunks
        ]

        for i, future in enumerate(futures, start=1):
            try:
                future.result()
                print(f"✔ Chunk {i}/{num_threads} done")
            except Exception as e:
                print(f"❌ Error in chunk {i}: {e}")

    print("✔ Parallel REST upload complete.")


def deactivate_records(client, object_name, data):
    """
    Bulk-update Order records to Status = Draft before deletion.
    (Legacy logic preserved)
    """
    if object_name.lower() == 'order':
        for record in data:
            record["Status"] = "Draft"

    # Bulk update (external ID = None)
    update_to_sf_bulk(client, object_name, data, external_identifier=None)


def cleanup_sobject(
    client: Salesforce,
    object_name: str,
):
    """
    Full cleanup flow for an sObject:
      1. Query all records
      2. Deactivate (Order only)
      3. Bulk delete with decreasing batch sizes:
         10k → 100 → 10 → 1
      4. Log progress consistently
    """

    print(f"\n=== CLEANUP: {object_name} ===")

    # Query
    records = query_all_records(client, object_name)
    if not records:
        print(f"[CLEANUP] No records found for {object_name}")
        return

    # Deactivate Orders
    if object_name.lower() == "order":
        print("[CLEANUP] Deactivating Orders before deletion…")
        deactivate_records(client, object_name, records)

    # 3) Delete with batch sizes
    batch_sizes = [10000, 100, 10, 1]

    remaining = {"records": records}  # initial placeholder

    for bs in batch_sizes:
        if not remaining["records"]:
            break

        remaining = delete_from_sf_bulk(
            client=client,
            object_name=object_name,
            data=records,
            batch_size=bs
        )

    print(f"[CLEANUP] Finished cleanup for {object_name}")


def delete_from_sf_bulk(
    client: Salesforce,
    object_name: str,
    data: List[Dict[str, Any]],
    batch_size: int = default_batch_size,
):
    """
    Bulk delete via Bulk API 2.0.

    Writes failed rows into a CSV file in logs/<env>/errors_<object>_<timestamp>.csv
    """

    print(f"[BULK-DELETE] Starting delete for {object_name} (batch_size={batch_size})")

    sf_object = client.bulk2.__getattr__(object_name)
    results = sf_object.delete(records=data, batch_size=batch_size)

    # Log failures
    log_base = Path(log_dir)
    error_file = get_log_file(
        base_dir=log_base,
        object_name=object_name,
        prefix="errors",
        env=env
    )

    for job in results:
        job_id = job["job_id"]
        sf_object.get_failed_records(job_id, file=str(error_file))

    # Re-query
    remaining = client.query_all(f"SELECT Id FROM {object_name}")
    count_remaining = len(remaining["records"])

    print(
        f"[BULK-DELETE] Done for {object_name}. "
        f"{count_remaining} records remain. Errors logged to: {error_file}"
    )

    return remaining
