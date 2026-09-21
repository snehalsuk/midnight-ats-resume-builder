import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.core.rate_limit import limiter
from app.exceptions.handlers import rate_limit_exceeded_handler, register_exception_handlers

settings = get_settings()
configure_logging()

logger = logging.getLogger("app")
logger.info("Starting %s (environment=%s, docs_enabled=%s)", settings.app_name, settings.environment, settings.docs_enabled)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health():
    """Liveness + DB connectivity check — a production health check must
    verify its real dependencies, not just that the process is running."""
    from sqlalchemy import text

    from app.core.db import SessionLocal

    db_ok = True
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except Exception:  # noqa: BLE001
        db_ok = False
        logger.exception("Health check: database connectivity failed")

    return {"status": "ok" if db_ok else "degraded", "database": "ok" if db_ok else "unreachable"}
