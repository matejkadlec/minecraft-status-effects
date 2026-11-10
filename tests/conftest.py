import json
import warnings

import pytest

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fastapi.testclient import TestClient

from status_effects import config
from status_effects.app import app
from status_effects.data import Dataset


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def dataset() -> Dataset:
    return Dataset.load()


@pytest.fixture(scope="session")
def raw_effects() -> list[dict]:
    return json.loads(config.EFFECTS_FILE.read_text(encoding="utf-8"))["effects"]


@pytest.fixture(scope="session")
def raw_mods() -> dict:
    return json.loads(config.MODS_FILE.read_text(encoding="utf-8"))
