import pytest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with (
        patch("app.main.init_db"),
        patch("app.main.close_db"),
        patch("app.main.configure_cloudinary"),
    ):
        from app.main import app

        with TestClient(app) as test_client:
            yield test_client
