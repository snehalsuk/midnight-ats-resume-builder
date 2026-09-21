from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT_JWT_SECRET = "change-me-in-.env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Midnight ATS Resume Builder"
    api_v1_prefix: str = "/api/v1"

    # "development" | "production" — gates the insecure-secret check below
    # and whether interactive API docs are exposed.
    environment: str = "development"
    enable_docs: bool | None = None  # None = auto (on in dev, off in prod)
    log_format: str = "text"  # "text" | "json" — JSON recommended in production

    database_url: str = "mysql+pymysql://resume_user:resume_pass@localhost:3306/resume_builder"

    jwt_secret_key: str = _INSECURE_DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 * 7

    ai_provider: str = "groq"
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"

    max_upload_size_bytes: int = 5 * 1024 * 1024  # 5MB
    allowed_upload_mime_types: tuple[str, ...] = (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    )

    cors_origins: tuple[str, ...] = ("http://localhost:5173",)

    # Rate limits (spec §37 — protect auth endpoints from brute force)
    login_rate_limit: str = "10/minute"
    register_rate_limit: str = "5/minute"

    # One-page engine safe limits
    min_font_size_pt: float = 10.0
    max_font_size_pt: float = 11.5
    min_margin_in: float = 0.4
    max_margin_in: float = 0.85
    one_page_max_iterations: int = 8

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def docs_enabled(self) -> bool:
        return self.enable_docs if self.enable_docs is not None else not self.is_production

    @model_validator(mode="after")
    def _refuse_insecure_secret_in_production(self) -> "Settings":
        if self.is_production and self.jwt_secret_key == _INSECURE_DEFAULT_JWT_SECRET:
            raise ValueError(
                "JWT_SECRET_KEY is still the insecure placeholder value while ENVIRONMENT=production. "
                "Set a real random secret (e.g. `openssl rand -hex 32`) in your production .env before starting."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
