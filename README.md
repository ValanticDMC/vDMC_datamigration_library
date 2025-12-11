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

