"""HTTP layer for the FlowBoard web application."""

from __future__ import annotations

import json
import mimetypes
import re
import time
from collections import defaultdict, deque
from email.utils import formatdate
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from .config import Config, ROOT_DIR
from .database import Database
from .security import Session, SessionSigner
from .service import BoardService, NotFoundError, ValidationError


MAX_BODY_BYTES = 32 * 1024
TASK_PATH = re.compile(r"^/api/tasks/(\d+)$")
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; "
        "script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    ),
    "Referrer-Policy": "same-origin",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


class RequestError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class SlidingWindowLimiter:
    def __init__(self, attempts: int = 8, window_seconds: int = 60):
        self.attempts = attempts
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        events = self._events[key]
        while events and current - events[0] > self.window_seconds:
            events.popleft()
        if len(events) >= self.attempts:
            return False
        events.append(current)
        return True


def create_server(config: Config, port: int | None = None) -> ThreadingHTTPServer:
    database = Database(config.database_path)
    database.migrate()
    database.seed_demo(config.demo_email, config.demo_password, config.demo_name)
    service = BoardService(database)
    signer = SessionSigner(config.secret_key)
    limiter = SlidingWindowLimiter()
    public_dir = ROOT_DIR / "public"

    class FlowBoardHandler(BaseHTTPRequestHandler):
        server_version = "FlowBoard/1.0"
        sys_version = ""

        def do_GET(self) -> None:  # noqa: N802 - standard library hook
            self._dispatch()

        def do_POST(self) -> None:  # noqa: N802 - standard library hook
            self._dispatch()

        def do_PUT(self) -> None:  # noqa: N802 - standard library hook
            self._dispatch()

        def do_DELETE(self) -> None:  # noqa: N802 - standard library hook
            self._dispatch()

        def do_OPTIONS(self) -> None:  # noqa: N802 - standard library hook
            self._send_json(HTTPStatus.METHOD_NOT_ALLOWED, {"error": "CORS не разрешён"})

        def _dispatch(self) -> None:
            try:
                path = urlparse(self.path).path
                if path.startswith("/api/"):
                    self._handle_api(path)
                elif self.command == "GET":
                    self._serve_static(path)
                else:
                    raise RequestError(HTTPStatus.METHOD_NOT_ALLOWED, "Метод не поддерживается")
            except RequestError as error:
                self._send_json(error.status, {"error": error.message})
            except ValidationError as error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
            except NotFoundError as error:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": str(error)})
            except _ResponseSent:
                return
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as error:
                self.log_error("Unhandled request error: %s", type(error).__name__)
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": "Внутренняя ошибка сервера"},
                )

        def _handle_api(self, path: str) -> None:
            method = self.command
            if path == "/api/health" and method == "GET":
                self._send_json(
                    HTTPStatus.OK,
                    {"status": "ok", "database": database.integrity_check()},
                )
                return
            if path == "/api/register" and method == "POST":
                payload = self._read_json()
                key = f"register:{self.client_address[0]}"
                if not limiter.allow(key):
                    raise RequestError(HTTPStatus.TOO_MANY_REQUESTS, "Слишком много попыток. Попробуйте позже")
                user = service.register(
                    str(payload.get("email", "")),
                    str(payload.get("password", "")),
                    str(payload.get("display_name", "")),
                )
                self._send_authenticated(HTTPStatus.CREATED, user)
                return
            if path == "/api/login" and method == "POST":
                payload = self._read_json()
                email = str(payload.get("email", "")).strip().lower()
                key = f"login:{self.client_address[0]}:{email[:100]}"
                if not limiter.allow(key):
                    raise RequestError(HTTPStatus.TOO_MANY_REQUESTS, "Слишком много попыток. Попробуйте позже")
                user = service.authenticate(email, str(payload.get("password", "")))
                if not user:
                    raise RequestError(HTTPStatus.UNAUTHORIZED, "Неверный email или пароль")
                self._send_authenticated(HTTPStatus.OK, user)
                return

            session, user = self._require_user()
            if path == "/api/session" and method == "GET":
                self._send_json(
                    HTTPStatus.OK,
                    {"authenticated": True, "user": user, "csrf_token": signer.csrf_token(session.nonce)},
                )
                return
            if method in {"POST", "PUT", "DELETE"}:
                supplied_csrf = self.headers.get("X-CSRF-Token")
                if not signer.valid_csrf(session, supplied_csrf):
                    raise RequestError(HTTPStatus.FORBIDDEN, "Проверка CSRF не пройдена")
            if path == "/api/logout" and method == "POST":
                self._send_empty(HTTPStatus.NO_CONTENT, cookie=self._expired_cookie())
                return
            if path == "/api/tasks" and method == "GET":
                query = parse_qs(urlparse(self.path).query)
                tasks = service.list_tasks(
                    int(user["id"]),
                    query=query.get("query", [""])[0],
                    status=query.get("status", [""])[0],
                    priority=query.get("priority", [""])[0],
                )
                self._send_json(HTTPStatus.OK, {"tasks": tasks})
                return
            if path == "/api/tasks" and method == "POST":
                task = service.create_task(int(user["id"]), self._read_json())
                self._send_json(HTTPStatus.CREATED, {"task": task})
                return
            match = TASK_PATH.match(path)
            if match and method == "PUT":
                task = service.update_task(
                    int(user["id"]), int(match.group(1)), self._read_json()
                )
                self._send_json(HTTPStatus.OK, {"task": task})
                return
            if match and method == "DELETE":
                service.delete_task(int(user["id"]), int(match.group(1)))
                self._send_empty(HTTPStatus.NO_CONTENT)
                return
            if path == "/api/stats" and method == "GET":
                self._send_json(HTTPStatus.OK, {"stats": service.stats(int(user["id"]))})
                return
            if path == "/api/activity" and method == "GET":
                self._send_json(
                    HTTPStatus.OK,
                    {"activity": service.activity(int(user["id"]))},
                )
                return
            raise RequestError(HTTPStatus.NOT_FOUND, "Маршрут не найден")

        def _require_user(self) -> tuple[Session, dict[str, Any]]:
            token = self._session_cookie()
            session = signer.verify(token) if token else None
            if not session:
                if urlparse(self.path).path == "/api/session" and self.command == "GET":
                    self._send_json(HTTPStatus.OK, {"authenticated": False})
                    raise _ResponseSent
                raise RequestError(HTTPStatus.UNAUTHORIZED, "Необходима авторизация")
            user = service.get_user(session.user_id)
            if not user:
                raise RequestError(HTTPStatus.UNAUTHORIZED, "Сессия больше недействительна")
            return session, user

        def _send_authenticated(self, status: int, user: dict[str, Any]) -> None:
            token, csrf_token = signer.create(int(user["id"]))
            self._send_json(
                status,
                {"authenticated": True, "user": user, "csrf_token": csrf_token},
                cookie=self._session_cookie_header(token),
            )

        def _read_json(self) -> dict[str, Any]:
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
            if content_type != "application/json":
                raise RequestError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Ожидается application/json")
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as error:
                raise RequestError(HTTPStatus.BAD_REQUEST, "Неверная длина запроса") from error
            if length <= 0:
                return {}
            if length > MAX_BODY_BYTES:
                raise RequestError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Тело запроса слишком большое")
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise RequestError(HTTPStatus.BAD_REQUEST, "Неверный JSON") from error
            if not isinstance(payload, dict):
                raise RequestError(HTTPStatus.BAD_REQUEST, "JSON должен быть объектом")
            return payload

        def _serve_static(self, path: str) -> None:
            requested = "index.html" if path in {"", "/"} else unquote(path.lstrip("/"))
            target = (public_dir / requested).resolve()
            if public_dir.resolve() not in target.parents and target != public_dir.resolve():
                raise RequestError(HTTPStatus.NOT_FOUND, "Файл не найден")
            if not target.is_file():
                target = public_dir / "index.html"
            content = target.read_bytes()
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            for name, value in SECURITY_HEADERS.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(content)

        def _send_json(
            self,
            status: int,
            payload: dict[str, Any],
            cookie: str | None = None,
        ) -> None:
            body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.send_response(int(status))
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            if cookie:
                self.send_header("Set-Cookie", cookie)
            for name, value in SECURITY_HEADERS.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body)

        def _send_empty(self, status: int, cookie: str | None = None) -> None:
            self.send_response(int(status))
            self.send_header("Content-Length", "0")
            self.send_header("Cache-Control", "no-store")
            if cookie:
                self.send_header("Set-Cookie", cookie)
            for name, value in SECURITY_HEADERS.items():
                self.send_header(name, value)
            self.end_headers()

        def _session_cookie(self) -> str | None:
            raw_cookie = self.headers.get("Cookie")
            if not raw_cookie:
                return None
            cookie = SimpleCookie()
            try:
                cookie.load(raw_cookie)
            except Exception:
                return None
            morsel = cookie.get("flowboard_session")
            return morsel.value if morsel else None

        @staticmethod
        def _session_cookie_header(token: str) -> str:
            secure = "; Secure" if config.cookie_secure else ""
            return (
                f"flowboard_session={token}; Path=/; HttpOnly; SameSite=Lax; "
                f"Max-Age=43200{secure}"
            )

        @staticmethod
        def _expired_cookie() -> str:
            secure = "; Secure" if config.cookie_secure else ""
            expired = formatdate(0, usegmt=True)
            return (
                f"flowboard_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0; "
                f"Expires={expired}{secure}"
            )

        def log_message(self, message: str, *args: Any) -> None:
            safe_path = urlparse(self.path).path
            print(f'{self.address_string()} [{self.log_date_time_string()}] "{self.command} {safe_path}" {args[1] if len(args) > 1 else ""}')

    class _FlowBoardServer(ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    actual_port = config.port if port is None else port
    return _FlowBoardServer((config.host, actual_port), FlowBoardHandler)


class _ResponseSent(Exception):
    """Stop dispatch after a complete anonymous-session response."""
