"""Rate limiting is wired via app.state.limiter + SlowAPIMiddleware, with
LOGIN_RATE_LIMIT/REGISTER_RATE_LIMIT raised to a very high value for the
test process (see conftest.py) so the rest of the suite isn't flaky at
whatever call volume it happens to produce. That means this file can't
exercise a real 429 in-process without a second process using production
limits — instead it verifies the wiring and the 429 response shape
directly, which is what would actually break if this regressed.
"""

import asyncio
import subprocess
import sys
import textwrap

from app.exceptions.handlers import rate_limit_exceeded_handler
from app.main import app


def test_limiter_is_registered_on_the_app():
    assert hasattr(app.state, "limiter")


def test_register_endpoint_actually_throttles_in_isolation():
    """Runs in a fresh subprocess with a strict limit and its own SQLite
    file — this process's own limiter state is shared (and deliberately
    permissive, see conftest.py) across the whole suite, so a real
    throttling assertion has to happen somewhere that won't disturb it.
    """
    script = textwrap.dedent("""
        import os, pathlib
        db_path = pathlib.Path("rate_limit_probe.db")
        db_path.unlink(missing_ok=True)
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        os.environ["GROQ_API_KEY"] = ""
        os.environ["REGISTER_RATE_LIMIT"] = "3/minute"

        import app.models  # noqa: F401
        from app.core.db import Base, engine
        Base.metadata.create_all(bind=engine)

        from fastapi.testclient import TestClient
        from app.main import app as fastapi_app
        client = TestClient(fastapi_app)

        statuses = []
        for i in range(5):
            r = client.post("/api/v1/auth/register", json={"email": f"probe{i}@example.com", "password": "testpass123"})
            statuses.append(r.status_code)

        engine.dispose()
        db_path.unlink(missing_ok=True)
        assert statuses == [201, 201, 201, 429, 429], statuses
        print("THROTTLE_OK")
    """)
    result = subprocess.run([sys.executable, "-c", script], cwd=".", capture_output=True, text=True, timeout=60)
    assert "THROTTLE_OK" in result.stdout, result.stdout + result.stderr


def test_rate_limit_exceeded_returns_structured_429():
    # the handler never inspects `request`/`exc` — it always returns the
    # same structured 429, so a bare object stands in for both here.
    response = asyncio.run(rate_limit_exceeded_handler(None, None))
    assert response.status_code == 429
    body = response.body.decode()
    assert '"success":false' in body
    assert '"errorCode":"RATE_LIMITED"' in body
