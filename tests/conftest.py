"""Shared fixtures and the opt-in gate for live tests."""

import json
import os

import pytest

from app import config
from app.product_store import ProductStore


def pytest_collection_modifyitems(items):
    """Skip tests marked ``live`` unless HEALF_RUN_LIVE is set."""
    if os.environ.get("HEALF_RUN_LIVE"):
        return
    skip_live = pytest.mark.skip(reason="live; set HEALF_RUN_LIVE=1 to run")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture(scope="session")
def products():
    return ProductStore(config.PRODUCTS_PATH)


@pytest.fixture(scope="session")
def catalogue():
    return json.loads(config.PRODUCTS_PATH.read_text())


@pytest.fixture(scope="session")
def corpus_docs():
    paths = sorted(config.CORPUS_DIR.glob("*.json"))
    return [json.loads(path.read_text()) for path in paths]


@pytest.fixture(scope="session")
def profile():
    return json.loads(config.CUSTOMER_PATH.read_text())
