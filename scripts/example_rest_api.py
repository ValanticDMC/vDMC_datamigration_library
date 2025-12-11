"""
Example Migration Script: Accounts

This script demonstrates how to:
- load mapping files
- load and map CSV data
- clean fields
- merge custom tables
- map Salesforce IDs using SOQL helper functions
- sanitize emails and dates
- upload Accounts using the REST API

Environment is automatically chosen from config.json.
"""

import pandas as pd

from vdmc_salesforce_migration import (
    get_salesforce_client,
    load_mapping,
    load_file_with_mapping,
    clear_fields,
    convert_datetime,
    clean_emails,
    get_field_map,
    get_record_types,
    upload_to_sf_rest
)


# ------------------------------------------------------
# 0) Configuration
# ------------------------------------------------------
pattern = "accounts_20"
map_path = "accounts.json"


# ------------------------------------------------------
# 1) Load Mapping File
# ------------------------------------------------------
mapping = load_mapping(map_path)


# ------------------------------------------------------
# 2) Initialize Salesforce Client
#     → environment is taken automatically from config.json
# ------------------------------------------------------
client = get_salesforce_client()


# ------------------------------------------------------
# 3) Load and map CSV input files
# ------------------------------------------------------
df = load_file_with_mapping(pattern, map_path, "field_map")


# ------------------------------------------------------
# 4) Cleaning and preprocessing
# ------------------------------------------------------
df = clear_fields(df)


# ------------------------------------------------------
# 5) Convert datetime fields to Salesforce ISO format
# ------------------------------------------------------
for field in ["CreatedDate", "LastModifiedDate"]:
    if field in df.columns:
        df = convert_datetime(df, field)


# ------------------------------------------------------
# 6) Map User IDs (CreatedById, OwnerId, etc.)
# ------------------------------------------------------
user_map = get_field_map(
    client,
    object_name="User",
    key_field="external_id_field",
    value_field="Id"
)

for field in ["CreatedById", "LastModifiedById", "OwnerId"]:
    if field in df.columns:
        df[field] = df[field].map(user_map)


# ------------------------------------------------------
# 7) Record Type Mapping
# ------------------------------------------------------
record_types = get_record_types(client, "Account")

# map via mapping['recordtype_map'] first → then to actual SF IDs
df["RecordTypeId"] = (
    df["Type"]
    .map(mapping["recordtype_map"])
    .map(record_types)
)


# ------------------------------------------------------
# 8) Email Cleanup
# ------------------------------------------------------
if "vDMC_Email__c" in df.columns:
    df = clean_emails(df, "vDMC_Email__c")


# ------------------------------------------------------
# 9) Convert DataFrame to dicts for upload
# ------------------------------------------------------
records = df.to_dict("records")


# ------------------------------------------------------
# 10) Upload to Salesforce (REST API)
# ------------------------------------------------------
upload_to_sf_rest(
    client=client,
    object_name="Account",
    data=records
)

print("Account migration completed successfully.")
