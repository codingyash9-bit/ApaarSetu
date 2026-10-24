"""
Application configuration for APAAR Nexus.
Supports development, testing, and production environments.
Loads variables from .env via python-dotenv.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_DEV_SECRET = "dev-secret-key-change-in-production-12345"


class Config:
    """Base configuration shared across environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_DEV_SECRET)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/apaar_nexus.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Demo accounts and auth
    DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "Demo@12345")

    # Ingestion and upload limits
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "2"))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024
    MAX_CSV_ROWS = int(os.getenv("MAX_CSV_ROWS", "5000"))

    # Credential key storage
    SIGNING_KEY_DIR = os.getenv("SIGNING_KEY_DIR", "instance/keys")

    # Session cookie hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() in ("true", "1", "yes")

    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Demo reset toggle
    ALLOW_DEMO_RESET = os.getenv("ALLOW_DEMO_RESET", "true").lower() in ("true", "1", "yes")

    # App metadata
    APP_NAME = "APAAR Nexus"
    APP_VERSION = "1.0.0-prototype"
    SYNTHETIC_NOTICE = "Prototype — synthetic data only. Not connected to AICTE, APAAR, UIDAI or DigiLocker."

    @classmethod
    def init_app(cls, app):
        """Optional hook for extra initialization."""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # CSRF configurable, disabled by default for simpler client test invocations
    WTF_CSRF_ENABLED = os.getenv("TEST_WTF_CSRF_ENABLED", "false").lower() in ("true", "1", "yes")


class ProductionConfig(Config):
    """Production configuration with strict security checks."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        secret = os.getenv("SECRET_KEY")
        if not secret or secret == DEFAULT_DEV_SECRET:
            raise RuntimeError(
                "CRITICAL: ProductionConfig requires a strong, unique SECRET_KEY environment variable."
            )
        if os.getenv("DEMO_PASSWORD", "Demo@12345") == "Demo@12345":
            raise RuntimeError(
                "CRITICAL: ProductionConfig refuses to run with default DEMO_PASSWORD."
            )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
