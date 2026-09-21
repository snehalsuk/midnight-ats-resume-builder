import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("GROQ_API_KEY", "")
# Production-tuned auth rate limits would make the test suite flaky (it's
# well within a single window at the process's actual call volume) — tests
# exercise correctness, not throttling, so use a limit high enough it can
# never trip. Rate limiting itself is covered directly in test_rate_limiting.py.
os.environ.setdefault("LOGIN_RATE_LIMIT", "1000/minute")
os.environ.setdefault("REGISTER_RATE_LIMIT", "1000/minute")

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 register models on Base.metadata
from app.core.db import Base, engine
from app.main import app

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    test_db_path = Path(__file__).parent.parent / "test.db"
    if test_db_path.exists():
        test_db_path.unlink()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()  # release SQLite's file lock before deleting it (Windows)
    if test_db_path.exists():
        test_db_path.unlink()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_resume_pdf_bytes() -> bytes:
    return (FIXTURES_DIR / "sample_resume.pdf").read_bytes()


@pytest.fixture
def auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "pytest@example.com", "password": "testpass123", "firstName": "Py", "lastName": "Test"},
    )
    r = client.post("/api/v1/auth/login", json={"email": "pytest@example.com", "password": "testpass123"})
    token = r.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}
