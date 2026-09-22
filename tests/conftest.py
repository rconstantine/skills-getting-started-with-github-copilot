from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    original_activities = deepcopy(app_module.activities)

    try:
        with TestClient(app_module.app) as test_client:
            yield test_client
    finally:
        app_module.activities.clear()
        app_module.activities.update(original_activities)
