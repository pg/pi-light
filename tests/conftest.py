import pytest
from requests import Session
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def common_client() -> Session:
    app.router.on_startup = []
    app.router.on_shutdown = []

    with TestClient(app) as c:
        return c


@pytest.fixture(scope="class")
def client(request, common_client) -> None:
    request.cls.client = common_client
