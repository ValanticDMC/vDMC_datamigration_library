Module vdmc_salesforce_migration.utils.cleaning
===============================================

Functions
---------

`clean_emails(df: pandas.core.frame.DataFrame, field_name: str) ‑> pandas.core.frame.DataFrame`
:   Ensure field contains valid single emails only.

`clean_numeric_fields(df: pandas.core.frame.DataFrame) ‑> pandas.core.frame.DataFrame`
:   Coerce numeric-looking columns into clean floats and replace invalid values.

`clear_fields(df: pandas.core.frame.DataFrame) ‑> pandas.core.frame.DataFrame`
:   Apply sanitization to all object fields and clean numerics.

`convert_datetime(df: pandas.core.frame.DataFrame, fieldname: str) ‑> pandas.core.frame.DataFrame`
:   Converts a datetime column into Salesforce-compatible UTC ISO format.

`extract_email(value: Any) ‑> List[str]`
:   Extract valid email addresses from a string.

`extract_email_from_field(df: pandas.core.frame.DataFrame, field: str) ‑> pandas.core.frame.DataFrame`
:   Extract an email address from a specific field.

`join_related_fields(row: Dict[str, Any], fields: List[str], lookup: Dict[str, str]) ‑> str`
:   Joins multiple fields into one string.

`replace_ids_in_list(value: Any, id_map: Dict[str, str]) ‑> str`
:   Replace semicolon-separated values using a lookup map.

`replace_text(text: Any, mapping: Dict[str, str]) ‑> str`
:   Replaces text based on a mapping dictionary.

`sanitize_field(value: Any) ‑> str`
:   Remove invalid characters, normalize spacing, and strip.