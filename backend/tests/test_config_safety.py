import pytest

from app.core.config import Settings


def test_refuses_insecure_default_secret_in_production():
    with pytest.raises(ValueError, match="insecure placeholder"):
        Settings(environment="production", jwt_secret_key="change-me-in-.env", _env_file=None)


def test_allows_default_secret_in_development():
    settings = Settings(environment="development", jwt_secret_key="change-me-in-.env", _env_file=None)
    assert settings.is_production is False


def test_allows_real_secret_in_production():
    settings = Settings(environment="production", jwt_secret_key="a-real-random-secret", _env_file=None)
    assert settings.is_production is True


def test_docs_auto_disabled_in_production_unless_overridden():
    prod_default = Settings(environment="production", jwt_secret_key="a-real-random-secret", _env_file=None)
    assert prod_default.docs_enabled is False

    prod_forced_on = Settings(environment="production", jwt_secret_key="a-real-random-secret", enable_docs=True, _env_file=None)
    assert prod_forced_on.docs_enabled is True

    dev_default = Settings(environment="development", _env_file=None)
    assert dev_default.docs_enabled is True
