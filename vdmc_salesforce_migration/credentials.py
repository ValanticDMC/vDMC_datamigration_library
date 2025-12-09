import os
from dotenv import load_dotenv
from pathlib import Path

class CredentialError(Exception):
    pass

def load_credentials(env: str = None) -> dict:
    """
    Loads Salesforce credentials from environment variables.
    Supports multiple environments, e.g.: dev, stage, preview, prod.
    """

    # Determine environment
    env = env or os.getenv("SF_ENV")
    env_file = f".env.{env}"

    # Determine the project root
    package_dir = Path(__file__).resolve().parent
    project_root = package_dir.parent
    env_path = project_root / env_file

    # Load File
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        raise CredentialError(f"Environment file '{env_file}' not found.")

    # Validate the env variables
    username = os.getenv("SF_USERNAME")
    password = os.getenv("SF_PASSWORD")
    token = os.getenv("SF_SECURITY_TOKEN")
    login_domain = os.getenv("SF_LOGIN_DOMAIN", "login")
    instance_url = os.getenv("SF_INSTANCE_URL")

    required = {
        "SF_USERNAME": username,
        "SF_PASSWORD": password,
        "SF_SECURITY_TOKEN": token
    }

    missing = [key for key, value in required.items() if not value]
    if missing:
        raise CredentialError(
            f"Missing required environment variables for '{env}': {missing}"
        )

    return {
        "env": env,
        "username": username,
        "password": password,
        "security_token": token,
        "domain": login_domain,
        "instance_url": instance_url,
    }