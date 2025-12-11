Module vdmc_salesforce_migration.utils.soql
===========================================

Functions
---------

`get_external_by_sf_id(client: simple_salesforce.api.Salesforce, object_name: str, external_id_field: str = 'vDMC_SugarExternalId__c') ‑> Dict[Any, Any]`
:   Returns mapping[SalesforceId] = external_id.
    Useful for reverse lookup or delta loads.

`get_field_map(client: simple_salesforce.api.Salesforce, object_name: str, key_field: str, value_field: str, where: str = None) ‑> Dict[Any, Any]`
:   Universal helper:
    Returns mapping[key_field] = value_field for any object.
    
    Examples:
    get_field_map(client, "Product2", "StockKeepingUnit", "Id")

`get_record_types(client: simple_salesforce.api.Salesforce, object_name: str) ‑> Dict[str, str]`
:   Returns mapping[DeveloperName] = RecordTypeId for a given sObject.

`get_sf_id_by_external(client: simple_salesforce.api.Salesforce, object_name: str, external_id_field: str = 'vDMC_SugarExternalId__c') ‑> Dict[Any, Any]`
:   Returns mapping[external_id] = SalesforceId.
    Works for any object + any external ID field.

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

Classes
-------

`SOQLMappingError(*args, **kwargs)`
:   Raised when a SOQL mapping operation fails or fields are missing.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException