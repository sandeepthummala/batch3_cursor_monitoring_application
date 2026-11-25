import os
from pathlib import Path

from sqlalchemy.pool import StaticPool

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base config. SECRET_KEY from env; demo fallback for local only."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'monitoring.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED = True
    # Demo seed credentials (hashed on first run; plaintext only for local docs)
    DEMO_ADMIN_USERNAME = "admin"
    DEMO_ADMIN_PASSWORD = os.environ.get("DEMO_ADMIN_PASSWORD", "admin")
    SSH_CONNECT_TIMEOUT = 8
    SSH_COMMAND_TIMEOUT = 10


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    SECRET_KEY = "test-secret-key"
    DEMO_ADMIN_PASSWORD = "admin"
