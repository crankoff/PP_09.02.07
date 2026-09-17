#!/usr/bin/env python3
"""SQLite administration utility for FlowBoard."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kanban.config import Config
from kanban.database import Database


def backup(source: Database, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.connect() as source_connection, sqlite3.connect(destination) as target:
        source_connection.backup(target)
    print(f"Резервная копия: {destination}")


def restore(target: Database, source_path: Path, force: bool) -> None:
    if not force:
        raise SystemExit("Восстановление перезапишет БД. Добавьте --force после проверки файла")
    if not source_path.is_file():
        raise SystemExit(f"Файл не найден: {source_path}")
    with sqlite3.connect(source_path) as source_connection:
        result = source_connection.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise SystemExit(f"Резервная копия повреждена: {result}")
        target.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(target.path) as target_connection:
            source_connection.backup(target_connection)
    print(f"База восстановлена из {source_path}")


def show_stats(database: Database) -> None:
    with database.connect() as connection:
        users = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        tasks = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        activity = connection.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
    print(f"Пользователи: {users}\nЗадачи: {tasks}\nЗаписи журнала: {activity}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Администрирование базой FlowBoard")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init", help="применить миграции")
    subparsers.add_parser("check", help="проверить целостность")
    subparsers.add_parser("stats", help="показать статистику")
    backup_parser = subparsers.add_parser("backup", help="создать резервную копию")
    backup_parser.add_argument("path", nargs="?", type=Path)
    restore_parser = subparsers.add_parser("restore", help="восстановить резервную копию")
    restore_parser.add_argument("path", type=Path)
    restore_parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config = Config.from_env()
    database = Database(config.database_path)
    if args.command == "init":
        applied = database.migrate()
        print("Миграции: " + (", ".join(applied) if applied else "актуально"))
    elif args.command == "check":
        print(f"Целостность: {database.integrity_check()}")
    elif args.command == "stats":
        show_stats(database)
    elif args.command == "backup":
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        destination = args.path or Path("backups") / f"flowboard-{timestamp}.db"
        backup(database, destination)
    elif args.command == "restore":
        restore(database, args.path, args.force)


if __name__ == "__main__":
    main()
