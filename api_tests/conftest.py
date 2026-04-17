from pathlib import Path
from typing import Dict, List

import pytest

from common.config_manager import all_customers, get_customer_config
from common.db_client import DbClient
from common.http_client import HttpClient
from common.yaml_loader import load_yaml


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def pytest_addoption(parser):
    parser.addoption("--customer", action="store", default="TT客户", help="customer name in environments.yaml")


@pytest.fixture(scope="session")
def customer_name(pytestconfig) -> str:
    return pytestconfig.getoption("--customer")


@pytest.fixture(scope="session")
def env_config(customer_name) -> Dict:
    if customer_name not in all_customers():
        raise ValueError(f"unknown customer: {customer_name}")
    return get_customer_config(customer_name)


@pytest.fixture(scope="session")
def http_client(env_config) -> HttpClient:
    return HttpClient(base_url=env_config["base_url"])


@pytest.fixture(scope="session")
def api_http_client(env_config) -> HttpClient:
    return HttpClient(base_url=env_config["api_url"])


@pytest.fixture(scope="session")
def credentials(env_config) -> Dict:
    return env_config.get("credentials", {})


@pytest.fixture(scope="function")
def db_guard(env_config):
    db_cfg = env_config.get("database", {})
    if not db_cfg:
        yield
        return
    client = DbClient(db_cfg)
    pre_sql: List[str] = db_cfg.get("pre_sql", [])
    rollback_sql: List[str] = db_cfg.get("rollback_sql", [])
    try:
        if pre_sql:
            client.execute_many(pre_sql)
        yield
    finally:
        if rollback_sql:
            client.execute_many(rollback_sql)
        client.close()


def load_case_file(file_name: str) -> List[Dict]:
    data = load_yaml(str(DATA_DIR / file_name))
    return data.get("cases", [])
