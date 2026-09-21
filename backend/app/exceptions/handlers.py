import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.ai.base import AIProviderError
from app.exceptions.errors import AppError

logger = logging.getLogger("app")


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "errorCode": "RATE_LIMITED",
            "message": "Too many requests — please wait a moment and try again.",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Our own code raises HTTPException with an already-structured detail
        # dict (see security/deps.py); framework-raised ones (e.g. FastAPI's
        # OAuth2PasswordBearer "Not authenticated") only have a plain string,
        # so normalize those to the same {success, errorCode, message} shape.
        if isinstance(exc.detail, dict) and "success" in exc.detail:
            content = exc.detail
        else:
            content = {"success": False, "errorCode": "HTTP_ERROR", "message": str(exc.detail)}
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "errorCode": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(AIProviderError)
    async def ai_error_handler(request: Request, exc: AIProviderError):
        logger.warning("AI provider error: %s", exc)
        return JSONResponse(
            status_code=502,
            content={"success": False, "errorCode": "AI_PROVIDER_ERROR", "message": str(exc)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "errorCode": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error")
        return JSONResponse(
            status_code=500,
            content={"success": False, "errorCode": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
        )
