import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from kanban.config import Config
from kanban.web import create_server


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        config = Config(
            host="127.0.0.1",
            port=0,
            database_path=Path(cls.temp_dir.name) / "api.db",
            secret_key="api-test-secret",
        )
        cls.server = create_server(config, port=0)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.temp_dir.cleanup()

    def setUp(self):
        self.cookie = ""
        self.csrf = ""

    def request(self, method, path, payload=None, csrf=True):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        headers = {"Accept": "application/json"}
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.cookie:
            headers["Cookie"] = self.cookie
        if csrf and self.csrf:
            headers["X-CSRF-Token"] = self.csrf
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw_body = response.read()
        data = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        set_cookie = response.getheader("Set-Cookie")
        if set_cookie:
            self.cookie = set_cookie.split(";", 1)[0]
        connection.close()
        return response.status, data

    def login(self):
        status, data = self.request(
            "POST", "/api/login", {"email": "demo@example.com", "password": "Demo123!"}
        )
        self.assertEqual(status, 200)
        self.csrf = data["csrf_token"]
        return data

    def test_health_and_anonymous_session(self):
        status, health = self.request("GET", "/api/health")
        self.assertEqual((status, health["database"]), (200, "ok"))
        status, session = self.request("GET", "/api/session")
        self.assertEqual(status, 200)
        self.assertFalse(session["authenticated"])

    def test_login_rejects_bad_password(self):
        status, data = self.request(
            "POST", "/api/login", {"email": "demo@example.com", "password": "BadPassword1"}
        )
        self.assertEqual(status, 401)
        self.assertIn("Неверный", data["error"])

    def test_protected_route_requires_session(self):
        status, _ = self.request("GET", "/api/tasks")
        self.assertEqual(status, 401)

    def test_csrf_is_required_for_mutation(self):
        self.login()
        status, _ = self.request("POST", "/api/tasks", {"title": "No CSRF"}, csrf=False)
        self.assertEqual(status, 403)

    def test_task_crud_through_api(self):
        self.login()
        status, created = self.request(
            "POST", "/api/tasks", {"title": "Unique API task 1947", "priority": "high"}
        )
        self.assertEqual(status, 201)
        task = created["task"]
        status, changed = self.request(
            "PUT",
            f"/api/tasks/{task['id']}",
            {"status": "done", "version": task["version"]},
        )
        self.assertEqual(status, 200)
        self.assertEqual(changed["task"]["status"], "done")
        status, data = self.request("GET", "/api/tasks?query=1947")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["tasks"]), 1)
        status, _ = self.request("DELETE", f"/api/tasks/{task['id']}", {})
        self.assertEqual(status, 204)

    def test_registration_starts_authenticated_session(self):
        status, data = self.request(
            "POST",
            "/api/register",
            {"email": "new@example.com", "password": "NewPass123", "display_name": "Новый"},
        )
        self.assertEqual(status, 201)
        self.assertTrue(data["authenticated"])
        self.assertTrue(self.cookie)


if __name__ == "__main__":
    unittest.main()
