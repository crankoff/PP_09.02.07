"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    host: str = "127.0.0.1"
    port: int = 8000
    database_path: Path = ROOT_DIR / "data" / "flowboard.db"
    secret_key: str = "development-only-change-me"
    cookie_secure: bool = False
    demo_email: str = "demo@example.com"
    demo_password: str = "Demo123!"
    demo_name: str = "Демо пользователь"

    @classmethod
    def from_env(cls) -> "Config":
        environment = os.getenv("APP_ENV", "development").strip().lower()
        return cls(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            database_path=Path(
                os.getenv("DATABASE_PATH", str(ROOT_DIR / "data" / "flowboard.db"))
            ).expanduser(),
            secret_key=os.getenv("SECRET_KEY", "development-only-change-me"),
            cookie_secure=os.getenv(
                "COOKIE_SECURE", "1" if environment == "production" else "0"
            ).lower()
            in {"1", "true", "yes"},
            demo_email=os.getenv("DEMO_EMAIL", "demo@example.com"),
            demo_password=os.getenv("DEMO_PASSWORD", "Demo123!"),
            demo_name=os.getenv("DEMO_NAME", "Демо пользователь"),
        )
