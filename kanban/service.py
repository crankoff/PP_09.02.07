"""FlowBoard business rules and database operations."""

from __future__ import annotations

import sqlite3
from datetime import date
from typing import Any

from .database import Database
from .security import (
    hash_password,
    normalize_email,
    validate_email,
    validate_password,
    verify_password,
)


VALID_STATUSES = {"backlog", "in_progress", "done"}
VALID_PRIORITIES = {"low", "medium", "high"}


class ValidationError(ValueError):
    pass


class NotFoundError(LookupError):
    pass


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


class BoardService:
    def __init__(self, database: Database):
        self.database = database

    def register(self, email: str, password: str, display_name: str) -> dict[str, Any]:
        normalized = normalize_email(email)
        name = display_name.strip()
        if not validate_email(normalized):
            raise ValidationError("Укажите корректный email")
        password_problems = validate_password(password)
        if password_problems:
            raise ValidationError("Пароль должен содержать: " + ", ".join(password_problems))
        if not 2 <= len(name) <= 80:
            raise ValidationError("Имя должно содержать от 2 до 80 символов")
        try:
            with self.database.transaction() as connection:
                cursor = connection.execute(
                    "INSERT INTO users(email, password_hash, display_name) VALUES (?, ?, ?)",
                    (normalized, hash_password(password), name),
                )
                user_id = int(cursor.lastrowid)
                connection.execute(
                    "INSERT INTO activities(user_id, action, details) VALUES (?, ?, ?)",
                    (user_id, "registered", "Учётная запись создана"),
                )
        except sqlite3.IntegrityError as error:
            if "users.email" in str(error):
                raise ValidationError("Такой email уже зарегистрирован") from error
            raise
        return {"id": user_id, "email": normalized, "display_name": name, "role": "user"}

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT id, email, password_hash, display_name, role FROM users WHERE email = ?",
                (normalize_email(email),),
            ).fetchone()
        if not row or not verify_password(password, row["password_hash"]):
            return None
        return {
            "id": row["id"],
            "email": row["email"],
            "display_name": row["display_name"],
            "role": row["role"],
        }

    def get_user(self, user_id: int) -> dict[str, Any] | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT id, email, display_name, role, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_tasks(
        self,
        user_id: int,
        query: str = "",
        status: str = "",
        priority: str = "",
    ) -> list[dict[str, Any]]:
        clauses = ["user_id = ?"]
        params: list[Any] = [user_id]
        cleaned_query = query.strip()
        if cleaned_query:
            clauses.append("(title LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\')")
            escaped = cleaned_query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            params.extend([f"%{escaped}%", f"%{escaped}%"])
        if status:
            if status not in VALID_STATUSES:
                raise ValidationError("Неизвестный статус")
            clauses.append("status = ?")
            params.append(status)
        if priority:
            if priority not in VALID_PRIORITIES:
                raise ValidationError("Неизвестный приоритет")
            clauses.append("priority = ?")
            params.append(priority)
        sql = f"""
            SELECT id, title, description, status, priority, due_date, position,
                   version, created_at, updated_at
            FROM tasks
            WHERE {' AND '.join(clauses)}
            ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
                     position ASC, updated_at DESC, id DESC
        """
        with self.database.connect() as connection:
            return [dict(row) for row in connection.execute(sql, params)]

    def create_task(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        values = self._validate_task(payload, partial=False)
        with self.database.transaction() as connection:
            next_position = connection.execute(
                "SELECT COALESCE(MAX(position), 0) + 10 FROM tasks WHERE user_id = ? AND status = ?",
                (user_id, values["status"]),
            ).fetchone()[0]
            cursor = connection.execute(
                """
                INSERT INTO tasks(user_id, title, description, status, priority, due_date, position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    values["title"],
                    values["description"],
                    values["status"],
                    values["priority"],
                    values["due_date"],
                    next_position,
                ),
            )
            task_id = int(cursor.lastrowid)
            connection.execute(
                "INSERT INTO activities(user_id, task_id, action, details) VALUES (?, ?, ?, ?)",
                (user_id, task_id, "task_created", values["title"]),
            )
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
            ).fetchone()
        return dict(row)

    def update_task(self, user_id: int, task_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        with self.database.transaction() as connection:
            current = connection.execute(
                "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
            ).fetchone()
            if not current:
                raise NotFoundError("Задача не найдена")
            values = self._validate_task(payload, partial=True, current=dict(current))
            expected_version = payload.get("version")
            if expected_version is not None and int(expected_version) != current["version"]:
                raise ValidationError("Задача уже изменена. Обновите доску")
            position = payload.get("position", current["position"])
            try:
                position = max(0, min(1_000_000, int(position)))
            except (TypeError, ValueError) as error:
                raise ValidationError("Позиция должна быть целым числом") from error
            connection.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, status = ?, priority = ?, due_date = ?,
                    position = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (
                    values["title"],
                    values["description"],
                    values["status"],
                    values["priority"],
                    values["due_date"],
                    position,
                    task_id,
                    user_id,
                ),
            )
            action = "task_moved" if values["status"] != current["status"] else "task_updated"
            connection.execute(
                "INSERT INTO activities(user_id, task_id, action, details) VALUES (?, ?, ?, ?)",
                (user_id, task_id, action, values["title"]),
            )
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
            ).fetchone()
        return dict(row)

    def delete_task(self, user_id: int, task_id: int) -> None:
        with self.database.transaction() as connection:
            row = connection.execute(
                "SELECT title FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
            ).fetchone()
            if not row:
                raise NotFoundError("Задача не найдена")
            connection.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
            connection.execute(
                "INSERT INTO activities(user_id, action, details) VALUES (?, ?, ?)",
                (user_id, "task_deleted", row["title"]),
            )

    def stats(self, user_id: int) -> dict[str, int]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT status, COUNT(*) AS count FROM tasks WHERE user_id = ? GROUP BY status",
                (user_id,),
            )
            values = {row["status"]: row["count"] for row in rows}
            overdue = connection.execute(
                """
                SELECT COUNT(*) FROM tasks
                WHERE user_id = ? AND due_date < date('now') AND status != 'done'
                """,
                (user_id,),
            ).fetchone()[0]
        return {
            "total": sum(values.values()),
            "backlog": values.get("backlog", 0),
            "in_progress": values.get("in_progress", 0),
            "done": values.get("done", 0),
            "overdue": overdue,
        }

    def activity(self, user_id: int, limit: int = 10) -> list[dict[str, Any]]:
        safe_limit = max(1, min(50, int(limit)))
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT action, details, created_at FROM activities
                WHERE user_id = ? ORDER BY id DESC LIMIT ?
                """,
                (user_id, safe_limit),
            )
            return [dict(row) for row in rows]

    @staticmethod
    def _validate_task(
        payload: dict[str, Any],
        partial: bool,
        current: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        base = current or {
            "title": "",
            "description": "",
            "status": "backlog",
            "priority": "medium",
            "due_date": None,
        }
        title = str(payload.get("title", base["title"])).strip()
        description = str(payload.get("description", base["description"])).strip()
        status = str(payload.get("status", base["status"])).strip()
        priority = str(payload.get("priority", base["priority"])).strip()
        due_date = payload.get("due_date", base["due_date"])
        due_date = str(due_date).strip() if due_date else None
        if not title and not partial:
            raise ValidationError("Укажите название задачи")
        if not 1 <= len(title) <= 120:
            raise ValidationError("Название должно содержать от 1 до 120 символов")
        if len(description) > 1000:
            raise ValidationError("Описание не должно превышать 1000 символов")
        if status not in VALID_STATUSES:
            raise ValidationError("Неизвестный статус")
        if priority not in VALID_PRIORITIES:
            raise ValidationError("Неизвестный приоритет")
        if due_date:
            try:
                date.fromisoformat(due_date)
            except ValueError as error:
                raise ValidationError("Срок должен быть датой в формате ГГГГ-ММ-ДД") from error
        return {
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "due_date": due_date,
        }
