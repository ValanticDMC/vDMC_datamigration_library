import yaml
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def load_config():
    """
    Loads config.yaml from the package root directory and caches it.
    """
    root_dir = Path(__file__).resolve().parent.parent
    config_path = root_dir / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"config.yaml not found at {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Access helper functions
# ---------------------------------------------------------------------------
def get_log_dir() -> str:
    cfg = load_config()
    return cfg.get("logging", {}).get("directory", "logs")


def get_input_dir() -> str:
    cfg = load_config()
    return cfg.get("input", {}).get("directory", "input")


def get_mappings_dir() -> str:
    cfg = load_config()
    return cfg.get("mappings", {}).get("directory", "mappings")


def get_default_batch_size() -> int:
    cfg = load_config()
    return cfg.get("salesforce", {}).get("default_batch_size", 10000)


def get_default_env() -> str:
    cfg = load_config()
    return cfg.get("salesforce", {}).get("environment", "develop")
