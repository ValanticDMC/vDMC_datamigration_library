import os
import requests
from simple_salesforce import Salesforce, SalesforceLogin
from ..credentials import load_credentials
from vdmc_salesforce_migration.utils.config_loader import get_default_env

class SalesforceConnectionError(Exception):
    pass


def get_salesforce_client():
    """
    Creates a Salesforce client using only environment variables.
    Automatically detects sandbox vs production.
    Automatically fetches the latest API version.
    """

    # Load credentials (from env)
    env = get_default_env()
    creds = load_credentials(env)

    username = creds["username"]
    password = creds["password"]
    token = creds.get("security_token")
    domain = creds.get("domain", "login")  # login = prod, test = sandbox
    instance_url = creds.get("instance_url", "login")

    # Get the latest API version to avoid unsupported objects from new releases
    version = _fetch_latest_api_version(domain)
    print(f"Using Salesforce API version {version}")

    # Init Client
    try:
        client = Salesforce(
            username=username,
            password=password,
            security_token=token,
            domain=domain,
            version=version,
            instance_url=instance_url
        )
    except Exception as e:
        raise SalesforceConnectionError(f"Failed to connect to Salesforce: {e}")

    # 3. Test query to validate successful connection
    try:
        test = client.query("SELECT Id FROM User LIMIT 1")
        print("Connection to Salesforce established.")
    except Exception as e:
        raise SalesforceConnectionError(f"Connected but failed test query: {e}")

    return client


def _fetch_latest_api_version(domain: str) -> str:
    """
    Fetch the latest API version from Salesforce.
    Example endpoint:
    https://login.salesforce.com/services/data/
    This returns a list, we take the highest version.
    """
    base_url = f"https://{domain}.salesforce.com/services/data/"

    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
    except Exception as e:
        raise SalesforceConnectionError(f"Failed to fetch Salesforce API versions: {e}")

    versions = response.json()
    if not versions:
        raise SalesforceConnectionError("No API versions returned by Salesforce.")

    # Versions returned as a list
    latest = versions[-1]["version"]
    return latest

def get_session_id():
    """
    Returns a Salesforce session ID and instance URL.
    Useful for Postman or manual API testing.
    """

    env = get_default_env()
    creds = load_credentials(env)

    username = creds["username"]
    password = creds["password"]
    token = creds.get("security_token")
    domain = creds.get("domain", "login")  # login=prod, test=sandbox
    instance_url = creds.get("instance_url", "login")

    session_id, instance_url = SalesforceLogin(
        username=username,
        password=password,
        security_token=token,
        domain=domain,
        instance_url=instance_url
    )

    return session_id, instance_url