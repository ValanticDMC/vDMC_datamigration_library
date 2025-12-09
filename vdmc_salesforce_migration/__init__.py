"""
vdmc_salesforce_migration
Internal Salesforce migration helper library for VDMC.
"""

from .credentials import load_credentials
from .api.auth import get_salesforce_client, get_session_id

__all__ = [
    "load_credentials",
    "get_salesforce_client",
    "get_session_id"
]
