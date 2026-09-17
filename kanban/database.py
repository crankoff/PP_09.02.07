"""SQLite connection, migrations and demo data."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .security import hash_password, normalize_email


class Database:
    def __init__(self, path: Path, migrations_dir: Path | None = None):
        self.path = Path(path)
        self.migrations_dir = migrations_dir or Path(__file__).resolve().parent.parent / "migrations"

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def migrate(self) -> list[str]:
        applied: list[str] = []
        with self.transaction() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            existing = {
                row["version"]
                for row in connection.execute("SELECT version FROM schema_migrations")
            }
            for migration in sorted(self.migrations_dir.glob("*.sql")):
                if migration.name in existing:
                    continue
                connection.executescript(migration.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations(version) VALUES (?)", (migration.name,)
                )
                applied.append(migration.name)
        return applied

    def seed_demo(self, email: str, password: str, name: str) -> bool:
        normalized_email = normalize_email(email)
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT id FROM users WHERE email = ?", (normalized_email,)
            ).fetchone()
            if existing:
                return False
            cursor = connection.execute(
                "INSERT INTO users(email, password_hash, display_name) VALUES (?, ?, ?)",
                (normalized_email, hash_password(password), name.strip()),
            )
            user_id = int(cursor.lastrowid)
            connection.executemany(
                """
                INSERT INTO tasks(user_id, title, description, status, priority, due_date, position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        user_id,
                        "Изучить требования практики",
                        "Сверить README, отчёт и чек-лист сдачи.",
                        "done",
                        "high",
                        None,
                        10,
                    ),
                    (
                        user_id,
                        "Проверить API",
                        "Запустить автотесты и проверить сценарии в браузере.",
                        "in_progress",
                        "medium",
                        None,
                        10,
                    ),
                    (
                        user_id,
                        "Подготовить демо",
                        "Показать создание и перемещение карточки между колонками.",
                        "backlog",
                        "low",
                        None,
                        10,
                    ),
                ],
            )
            connection.execute(
                "INSERT INTO activities(user_id, action, details) VALUES (?, ?, ?)",
                (user_id, "demo_seeded", "Создан демо-набор данных"),
            )
        return True

    def integrity_check(self) -> str:
        with self.connect() as connection:
            return str(connection.execute("PRAGMA integrity_check").fetchone()[0])
