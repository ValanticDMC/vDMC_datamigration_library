# vDMC Salesforce Migration Library

A Python-based internal toolkit for performing data migrations to Salesforce using Simple Salesforce. It supports:

- Bulk API 2.0  
- REST API  
- Multi-threaded REST inserts/upserts  
- Data cleaning utilities  
- Mapping and lookup helpers  
- Logging for auditability  

This library supports repeatable, controlled migration processes for customer implementations and internal tooling.

---

## Features

### Salesforce API  
- Automatic credential loading via `.env.<environment>`  
- Environment selection via `config.json`  
- Consistent API version handling over all scripts

### Supported CRUD Scenarios  
- **Bulk API 2.0** inserts, updates, upserts  
- (Chained) **Bulk API 2.0** deletes to clean a complete org with all related objects
- **REST API** inserts/upserts  
- **Parallel REST Uploads** using multithreading for scenarios where objects are not supported by BULK API (e.g. ContentNotes)
- **Asset Activation API** (Order → Asset transformation)

### Data Utilities  
- Field mapping and column renaming  
- ID reference lookups (SOQL → Python dict)  
- String sanitization  
- Email extraction & validation  
- Datetime normalization to Salesforce format  
- Numeric cleaning  
- Field replacement helper functions  

### Logging  
Each upload generates log files with:

- Input IDs  
- Salesforce IDs  
- Success flags  
- Errors  

---

## Installation

### 1. Clone the repository
~~~bash
git clone <your-repo-url>
cd vdmc-salesforce-migration
~~~

### 2. Create and activate a virtual environment
~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

### 3. Install the library and its dependencies
~~~bash
pip install -e ".[dev]"
~~~

### 4. Configure environment variables
Create environment files (e.g. .env.develop, .env.preview, .env.prod) in the project root:
~~~bash
SF_USERNAME=your-username
SF_PASSWORD=your-password
SF_TOKEN=your-security-token
SF_DOMAIN=test
SF_INSTANCE_URL=https://your-instance-url.my.salesforce.com
~~~

### 5. Configure global settings
Edit config.json in the project root:
~~~bash
input:
  directory: "input"

mappings:
  directory: "mappings"

logging:
  directory: "logs"

salesforce:
  default_batch_size: 10000
  environment: "develop"
  api-version: 63
~~~

---

## Documentation

The docstring documentation is generated into the "docs" folder via pdoc.

---

## Examples
Please also refer some example implementations in the "scripts" folder.

### 1. Connect to Salesforce
```python
from vdmc_salesforce_migration import get_salesforce_client

client = get_salesforce_client()
```

### 2. Load CSV files and map columns based on mapping JSON
```python
from vdmc_salesforce_migration import load_file_with_mapping, load_mapping

df = load_file_with_mapping("accounts_20", "accounts.json", "field_map")
```

### 3. Clean and prepare data
```python
from vdmc_salesforce_migration import clear_fields, convert_datetime

df = clear_fields(df)
df = convert_datetime(df, "CreatedDate")
records = df.to_dict("records")
```

### 4. Upload data to Salesforce (REST or Bulk API)
REST Upload:
```python
from vdmc_salesforce_migration import upload_to_sf_rest

upload_to_sf_rest(
    client,
    object_name="Account",
    data=records,
    external_identifier="External_Id__c",
    id_field="external_id"
)
```

Bulk Upload:
```python
from vdmc_salesforce_migration import upload_to_sf_bulk

upload_to_sf_bulk(
    client,
    object_name="Contact",
    data=records,
    external_identifier="External_Id__c"
)
```

Multithreading REST Upload:
```python
from vdmc_salesforce_migration import upload_rest_parallel

upload_rest_parallel(
    object_name="Contact",
    data=records,
    external_identifier="External_Id__c"
)
```

### 5. Execute SOQL lookups
```python
from vdmc_salesforce_migration import get_field_map

record_types = get_field_map(
    object_name="Account",
    key_field="DeveloperName",
    value_field="Id",
    where_clause="SObjectType = 'Account'"
)
```

### 6. Activate Assets from Orders (Salesforce Standard Action)
```python
from vdmc_salesforce_migration import activate_assets_via_api

order_ids = ["801XXXXXXXXXXXX", "801YYYYYYYYYYYY"]
activate_assets_via_api(client, order_ids)
```

### 7. Bulk Delete all Data in a chain
Bulk Delete:
```python
from vdmc_salesforce_migration import get_salesforce_client, cleanup_sobject

client = get_salesforce_client()

for obj in objects:
    cleanup_sobject(client, obj)
```

---

## API Reference – Key Functions

This section documents the main public functions provided by the vdmc_salesforce_migration library.
All examples assume:

```python
from vdmc_salesforce_migration import *
```

## Authentication & Client Handling
### get_salesforce_client(env: str | None = None) -> Salesforce

Creates and returns an authenticated Salesforce client using environment settings from config.json and .env.<env>.

**Features**

- Automatically loads credentials based on configured environment
- Chooses correct domain (login/test)
- No credentials required in user scripts

**Example**
```python
client = get_salesforce_client()_
```

### get_session_id(env: str | None = None) -> (session_id, instance_url)

Returns a Salesforce Session ID, mainly for:

- Postman testing
- Calling unsupported REST endpoints
- Debugging

**Example**
```python
session_id, instance = get_session_id("develop")
```

## Upload & Processing Functions
### upload_rest_parallel(object_name, data, external_identifier=None, id_field=None, num_threads=4, env=None)

Parallel REST uploader for objects not supported or unstable in Bulk API.

**Features**

- REST API
- Thread pool
- Logging per environment
- External ID upsert support

**Example**
```python
upload_rest_parallel(
    "Account",
    records,
    external_identifier="External_Id__c",
    id_field="external_id",
    num_threads=8
)
```

### cleanup_sobject(client, object_name)
Deletes all records of a Salesforce object using Bulk API 2.0.
Handles automatic bulk-size reduction (10k → 100 → 10 → 1) to bypass DELETE limits.

**Example**
```python
cleanup_sobject(client, "Quote")
```

### update_to_sf_bulk(client, object_name, data, external_identifier=None, batch_size=10000)
Bulk API update operation.

**Example**
```python
update_to_sf_bulk(client, "Account", updates)
```

### activate_assets_via_api(client, order_ids)
Calls Salesforce standard action createOrUpdateAssetFromOrder for each Order.

**Use Cases**
- Migrating Orders + generating Assets
- Regenerating broken asset structures

**Example**
```python
activate_assets_via_api(client, ["801XXXXXXXXXXXX", "801YYYYYYYYYYYY"])
```

## File Loading & Mapping
### load_mapping(file_path)
Loads a JSON mapping file and returns its dictionary.

**Example**
```python
mapping = load_mapping("accounts.json")
```

### load_file_with_mapping(pattern, mapping_path, table_name)
Loads a CSV file whose filename matches a prefix pattern and applies a mapping from the mapping JSON.

**Features**
- Automatically selects newest matching file
- Renames columns using mapping rules
- Drops unmapped columns

**Example**
```python
df = load_file_with_mapping("accounts_20", "accounts.json", "field_map")
```

## Data Cleaning Functions
### convert_datetime(df, field_name)
Converts datetime fields into Salesforce-compatible "YYYY-MM-DDThh:mm:ssZ" strings.

**Example**
```python
df = convert_datetime(df, "CreatedDate")
```

### extract_email_from_field(df, field)
Extracts all valid email addresses from a column and compresses them into comma-separated form.

**Example**
```python
df = extract_email_from_field(df, "Description")
```

### clean_emails(df, field_name)
Ensures a field contains only valid, normalized email addresses.

**Example**
```python
df = clean_emails(df, "vDMC_Email__c")
```

### clean_numeric_fields(df)
Ensures numerical fields are properly formatted for Salesforce imports.

**Example**
```python
df = clean_numeric_fields(df)
```

### join_related_fields(row, fields, lookup)
Converts multiple related values into a lookup field list using an ID map.

**Example**
```python
df["RelatedAccounts"] = df.apply(
    lambda row: join_related_fields(row, ["Acc1", "Acc2"], account_map),
    axis=1
)
```

### replace_ids_in_list(value, id_map)
Replaces semicolon-separated IDs with Salesforce IDs.

**Example**
```python
df["Contacts"] = df["Contacts"].apply(lambda x: replace_ids_in_list(x, contact_map))
```

### clear_fields(df)
Full cleaning pipeline:
- Remove invalid UTF-8 chars
- Normalize whitespace
- Remove problematic CSV separators
- Clean numbers
- Normalize empty values
- Recommended before every upload.

```python
df = clear_fields(df)
```

### replace_text(text, mapping)
Simple string replacement helper.

```python
df["Description"] = df["Description"].apply(lambda x: replace_text(x, {"old": "new"}))
```

## SOQL Helper Functions
These functions wrap SOQL queries into reusable, consistent mapping utilities.

### get_record_types(client, object_name)
Returns mapping { DeveloperName → RecordTypeId }.

**Example**
```python
rt_map = get_record_types(client, "Account")
```

### query_all_records(client, object_name)
Returns all object records as a list of dicts.

**Example**
```python
records = query_all_records(client, "Account")
```

### get_external_by_sf_id(client, object_name, external_field)
Returns { SalesforceId → ExternalId }.

**Example**
```python
map_sf_to_ext = get_external_by_sf_id(client, "Account", "External_Id__c")
```

### get_sf_id_by_external(client, object_name, external_field)
Returns { ExternalId → SalesforceId }.

**Example**
```python
map_ext_to_sf = get_sf_id_by_external(client, "Account", "External_Id__c")
```

### get_field_map(client, object_name, key_field, value_field, where_clause=None)
Generic wrapper for:
```SQL
SELECT Id, Name FROM Object
But fully customizable.
```

**Example**
```python
user_map = get_field_map(
    client,
    "User",
    key_field="vDMC_SugarExternalId__c",
    value_field="Id"
)
```

### query_to_nested_map(client, soql, parent_field, key_field, value_field)
Groups values by parent key:
```python
{
   "EUR": { Product2Id → PBEId },
   "USD": { Product2Id → PBEId }
}
```

### query_to_map(client, soql, key_field, value_field)
Generic SOQL → Python dict mapper.

Example
```python
map = query_to_map(
    client,
    "SELECT Id, Name FROM Product2",
    "Name",
    "Id"
)
```

---

## How to collaborate
We welcome contributions from developers working on Salesforce data migration projects. 
If you plan to do changes outside of projects, let the CoE Salesforce know what you want to change and we will take it into our planning. 

### Branching strategy
- Create feature branches from `main`.
- Use meaningful branch names:
  - `feature/<short-description>`
  - `fix/<short-description>`

### Pull requests
- Include a clear description of the change.
- Reference related Jira tickets if applicable.
- Ensure your code passes:
  - `pytest`
  - `ruff` linting
  - `black` formatting

### Code style
We follow:
- **Black** for formatting
- **Ruff** for linting
- Type hints where reasonable
- Docstrings for all public methods

### Adding new utilities
- Place data cleaning functions in `utils/cleaning.py`.
- Place file-related functions in `utils/file_io.py`.
- SOQL helpers belong in `utils/soql.py`.
- Upload and Salesforce-related logic go into `api/`.

### Before submitting
- Update documentation if the public API changes.
- Add or update tests for new functionality.
- Ensure backwards compatibility where possible.

