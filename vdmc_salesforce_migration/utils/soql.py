from typing import Dict, Any
from simple_salesforce import Salesforce


class SOQLMappingError(Exception):
    """Raised when a SOQL mapping operation fails or fields are missing."""
    pass


def _extract_field(record: Dict[str, Any], field_path: str):
    """
    Extract nested SOQL results using dot notation.
    Example: record["ProductSellingModel"]["PricingTermUnit"]
    """
    parts = field_path.split(".")
    value = record
    for part in parts:
        try:
            value = value[part]
        except Exception:
            raise SOQLMappingError(f"Field '{field_path}' not found in record: {record}")
    return value


def query_to_map(
    client: Salesforce,
    soql: str,
    key_field: str,
    value_field: str
) -> Dict[Any, Any]:
    """
    Execute SOQL and return a dict mapping {key_field: value_field}.
    Supports nested fields using dot notation.
    """
    results = client.query_all(soql)
    mapping = {}

    for rec in results["records"]:
        key = _extract_field(rec, key_field)
        value = _extract_field(rec, value_field)
        mapping[key] = value

    return mapping


def query_to_nested_map(
    client: Salesforce,
    soql: str,
    outer_key: str,
    inner_key: str,
    value_field: str
) -> Dict[Any, Dict[Any, Any]]:
    """
    Execute SOQL and return nested mapping:
        {
            outer_key_value: {
                inner_key_value: value
            }
        }
    """
    results = client.query_all(soql)
    mapping: Dict[Any, Dict[Any, Any]] = {}

    for rec in results["records"]:
        outer = _extract_field(rec, outer_key)
        inner = _extract_field(rec, inner_key)
        value = _extract_field(rec, value_field)

        if outer not in mapping:
            mapping[outer] = {}

        mapping[outer][inner] = value

    return mapping


def get_field_map(
    client: Salesforce,
    object_name: str,
    key_field: str,
    value_field: str,
    where: str = None
) -> Dict[Any, Any]:
    """
    Universal helper:
    Returns mapping[key_field] = value_field for any object.

    Examples:
    get_field_map(client, "Product2", "StockKeepingUnit", "Id")
    """
    where_clause = f" WHERE {where}" if where else ""
    soql = f"SELECT {key_field}, {value_field} FROM {object_name}{where_clause}"

    return query_to_map(client, soql, key_field, value_field)


def get_sf_id_by_external(
    client: Salesforce,
    object_name: str,
    external_id_field: str = "vDMC_SugarExternalId__c"
) -> Dict[Any, Any]:
    """
    Returns mapping[external_id] = SalesforceId.
    Works for any object + any external ID field.
    """
    soql = f"SELECT Id, {external_id_field} FROM {object_name}"
    return query_to_map(client, soql, external_id_field, "Id")


def get_external_by_sf_id(
    client: Salesforce,
    object_name: str,
    external_id_field: str = "vDMC_SugarExternalId__c"
) -> Dict[Any, Any]:
    """
    Returns mapping[SalesforceId] = external_id.
    Useful for reverse lookup or delta loads.
    """
    soql = f"SELECT Id, {external_id_field} FROM {object_name}"
    return query_to_map(client, soql, "Id", external_id_field)


def get_record_types(client: Salesforce, object_name: str) -> Dict[str, str]:
    """
    Returns mapping[DeveloperName] = RecordTypeId for a given sObject.
    """
    soql = (
        "SELECT Id, DeveloperName "
        "FROM RecordType "
        f"WHERE SObjectType = '{object_name}'"
    )
    return query_to_map(client, soql, "DeveloperName", "Id")
