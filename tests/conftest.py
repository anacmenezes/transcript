
import pytest

from fastapi.testclient import TestClient

from src.transcript.api.main import app


@pytest.fixture
def client():
    """Cliente HTTP para testar a API sem iniciar um servidor externo."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def override_db():
    """Permite substituir a dependência do banco em cada teste."""
    from src.transcript.db.session import get_db

    overrides = app.dependency_overrides.copy()

    yield get_db

    app.dependency_overrides.clear()
    app.dependency_overrides.update(overrides)
