import pandas as pd
import re
from typing import List, Dict, Any


# ---------------------------------------------------------------------------
# Datetime Handling
# ---------------------------------------------------------------------------
def convert_datetime(df: pd.DataFrame, fieldname: str) -> pd.DataFrame:
    """
    Converts a datetime column into Salesforce-compatible UTC ISO format.
    """
    df[fieldname] = pd.to_datetime(df[fieldname], errors='coerce')

    if df[fieldname].dt.tz is None:
        df[fieldname] = df[fieldname].dt.tz_localize('UTC')
    else:
        df[fieldname] = df[fieldname].dt.tz_convert('UTC')

    df[fieldname] = df[fieldname].dt.strftime('%Y-%m-%dT%H:%M:%SZ').fillna('')
    return df


# ---------------------------------------------------------------------------
# Email cleaning and extraction
# ---------------------------------------------------------------------------
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

def extract_email(value: Any) -> List[str]:
    """Extract valid email addresses from a string."""
    if pd.isna(value):
        return []
    return EMAIL_REGEX.findall(str(value))


def extract_email_from_field(df: pd.DataFrame, field: str) -> pd.DataFrame:
    """
    Extract an email address from a specific field.
    """
    df[field] = df[field].apply(lambda x: ",".join(extract_email(x)))
    return df


def clean_emails(df: pd.DataFrame, field_name: str) -> pd.DataFrame:
    """Ensure field contains valid single emails only."""
    email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    def _validate_email(x):
        if isinstance(x, str) and email_pattern.match(x):
            return x.replace("..", ".")
        return ""

    df[field_name] = df[field_name].apply(_validate_email)
    return df


# ---------------------------------------------------------------------------
# Numeric Cleaning
# ---------------------------------------------------------------------------
def clean_numeric_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce numeric-looking columns into clean floats and replace invalid values.
    """
    numeric_cols = [
        col for col in df.columns
        if pd.api.types.is_numeric_dtype(df[col])
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df


# ---------------------------------------------------------------------------
# Lookup / ID Helpers
# ---------------------------------------------------------------------------
def join_related_fields(row: Dict[str, Any], fields: List[str], lookup: Dict[str, str]) -> str:
    """
    Joins multiple fields into one string.
    """
    values = []
    for f in fields:
        v = row.get(f)
        if pd.isna(v):
            continue
        v = str(v).strip()
        if v in lookup:
            values.append(lookup[v])
    return ",".join(values)


def replace_ids_in_list(value: Any, id_map: Dict[str, str]) -> str:
    """Replace semicolon-separated values using a lookup map."""
    if pd.isna(value) or value == "":
        return ""

    ids = str(value).split(";")
    mapped = [id_map.get(i.strip(), "") for i in ids]
    return ",".join([m for m in mapped if m])


# ---------------------------------------------------------------------------
# String Cleaning
# ---------------------------------------------------------------------------
def sanitize_field(value: Any) -> str:
    """Remove invalid characters, normalize spacing, and strip."""
    if pd.isna(value):
        return ""

    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    else:
        value = str(value).encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")

    value = value.replace('"', "'")
    value = re.sub(r'[\r\n\t]+', ' ', value)
    value = re.sub(r'[^\x20-\x7EäöüÄÖÜß€°²³]', '', value)
    value = re.sub(r'\s{2,}', ' ', value)
    value = value.replace(";", "·")

    return value.strip()


def clear_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply sanitization to all object fields and clean numerics.
    """
    object_cols = df.select_dtypes(include="object").columns

    for col in object_cols:
        df[col] = df[col].apply(sanitize_field)

    # Normalize empty-like values
    df = df.replace(["nan", "NaN", "None", "NONE", "null", "NULL"], "")

    df = clean_numeric_fields(df)
    return df


# ---------------------------------------------------------------------------
# Generic text replacement
# ---------------------------------------------------------------------------
def replace_text(text: Any, mapping: Dict[str, str]) -> str:
    """
    Replaces text based on a mapping dictionary.
    """
    if pd.isna(text):
        return ""
    result = str(text)
    for old, new in mapping.items():
        result = result.replace(old, new)
    return result
