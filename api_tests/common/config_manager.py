from pathlib import Path
from typing import Any, Dict, List

from common.yaml_loader import load_yaml


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "config" / "environments.yaml"


def all_customers() -> List[str]:
    data = load_yaml(str(ENV_FILE))
    envs = data.get("environments", [])
    return [item.get("name", "") for item in envs if item.get("name")]


def get_customer_config(customer_name: str) -> Dict[str, Any]:
    data = load_yaml(str(ENV_FILE))
    envs = data.get("environments", [])
    for item in envs:
        if item.get("name") == customer_name:
            return item
    raise ValueError(f"Customer config not found: {customer_name}")
