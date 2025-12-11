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

---

## Usage

---

## Testing

