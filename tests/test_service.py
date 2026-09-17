import tempfile
import unittest
from pathlib import Path

from kanban.database import Database
from kanban.service import BoardService, NotFoundError, ValidationError


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp_dir.name) / "test.db")
        self.database.migrate()
        self.service = BoardService(self.database)
        self.user = self.service.register("one@example.com", "Password1", "Первый")
        self.other = self.service.register("two@example.com", "Password2", "Второй")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register_and_authenticate(self):
        authenticated = self.service.authenticate("ONE@example.com", "Password1")
        self.assertEqual(authenticated["id"], self.user["id"])
        self.assertIsNone(self.service.authenticate("one@example.com", "WrongPass1"))

    def test_duplicate_email_is_rejected(self):
        with self.assertRaisesRegex(ValidationError, "уже зарегистрирован"):
            self.service.register("ONE@example.com", "Password1", "Дубль")

    def test_task_lifecycle_and_stats(self):
        task = self.service.create_task(
            self.user["id"],
            {"title": "Новая", "description": "Описание", "priority": "high"},
        )
        self.assertEqual(task["status"], "backlog")
        changed = self.service.update_task(
            self.user["id"], task["id"], {"status": "done", "version": task["version"]}
        )
        self.assertEqual(changed["status"], "done")
        self.assertEqual(changed["version"], 2)
        self.assertEqual(self.service.stats(self.user["id"])["done"], 1)
        self.service.delete_task(self.user["id"], task["id"])
        self.assertEqual(self.service.stats(self.user["id"])["total"], 0)

    def test_users_cannot_access_each_others_tasks(self):
        task = self.service.create_task(self.user["id"], {"title": "Секрет"})
        self.assertEqual(self.service.list_tasks(self.other["id"]), [])
        with self.assertRaises(NotFoundError):
            self.service.update_task(self.other["id"], task["id"], {"status": "done"})
        with self.assertRaises(NotFoundError):
            self.service.delete_task(self.other["id"], task["id"])

    def test_optimistic_locking_rejects_stale_update(self):
        task = self.service.create_task(self.user["id"], {"title": "Версия"})
        self.service.update_task(self.user["id"], task["id"], {"title": "Версия 2"})
        with self.assertRaisesRegex(ValidationError, "уже изменена"):
            self.service.update_task(
                self.user["id"], task["id"], {"title": "Устаревшая", "version": 1}
            )

    def test_filters_and_input_validation(self):
        self.service.create_task(self.user["id"], {"title": "Срочно", "priority": "high"})
        self.service.create_task(self.user["id"], {"title": "Потом", "priority": "low"})
        self.assertEqual(len(self.service.list_tasks(self.user["id"], priority="high")), 1)
        self.assertEqual(len(self.service.list_tasks(self.user["id"], query="Сроч")), 1)
        with self.assertRaises(ValidationError):
            self.service.create_task(self.user["id"], {"title": ""})
        with self.assertRaises(ValidationError):
            self.service.create_task(self.user["id"], {"title": "X", "due_date": "17.09.2026"})


if __name__ == "__main__":
    unittest.main()
