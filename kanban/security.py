"""Password, session and request security helpers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import time
from dataclasses import dataclass


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
SESSION_TTL_SECONDS = 12 * 60 * 60
PBKDF2_ITERATIONS = 600_000


def normalize_email(value: str) -> str:
    return value.strip().lower()


def validate_email(value: str) -> bool:
    return len(value) <= 254 and EMAIL_PATTERN.fullmatch(value) is not None


def validate_password(value: str) -> list[str]:
    problems: list[str] = []
    if len(value) < 8:
        problems.append("не менее 8 символов")
    if not any(character.islower() for character in value):
        problems.append("строчная буква")
    if not any(character.isupper() for character in value):
        problems.append("заглавная буква")
    if not any(character.isdigit() for character in value):
        problems.append("цифра")
    return problems


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    scrypt = getattr(hashlib, "scrypt", None)
    if scrypt is not None:
        digest = scrypt(
            password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32
        )
        return "scrypt$16384$8$1${}${}".format(salt.hex(), digest.hex())

    # Some otherwise supported Python builds omit OpenSSL's scrypt binding.
    # Keep the application portable without downgrading to a fast password hash.
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=32
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        parts = encoded.split("$")
        algorithm = parts[0]
        if algorithm == "scrypt" and len(parts) == 6:
            _, n, r, p, salt_hex, digest_hex = parts
            scrypt = getattr(hashlib, "scrypt", None)
            if scrypt is None:
                return False
            actual = scrypt(
                password.encode("utf-8"),
                salt=bytes.fromhex(salt_hex),
                n=int(n),
                r=int(r),
                p=int(p),
                dklen=len(bytes.fromhex(digest_hex)),
            )
        elif algorithm == "pbkdf2_sha256" and len(parts) == 4:
            _, iterations, salt_hex, digest_hex = parts
            actual = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
                dklen=len(bytes.fromhex(digest_hex)),
            )
        else:
            return False
        return hmac.compare_digest(actual.hex(), digest_hex)
    except (AttributeError, TypeError, ValueError):
        return False


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


@dataclass(frozen=True)
class Session:
    user_id: int
    expires_at: int
    nonce: str


class SessionSigner:
    def __init__(self, secret_key: str):
        self._secret = secret_key.encode("utf-8")

    def create(self, user_id: int, now: int | None = None) -> tuple[str, str]:
        issued_at = int(time.time() if now is None else now)
        payload = {
            "uid": user_id,
            "exp": issued_at + SESSION_TTL_SECONDS,
            "nonce": secrets.token_urlsafe(16),
        }
        body = _b64encode(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        signature = _b64encode(
            hmac.new(self._secret, body.encode("ascii"), hashlib.sha256).digest()
        )
        token = f"{body}.{signature}"
        return token, self.csrf_token(payload["nonce"])

    def verify(self, token: str, now: int | None = None) -> Session | None:
        try:
            body, signature = token.split(".", 1)
            expected = _b64encode(
                hmac.new(self._secret, body.encode("ascii"), hashlib.sha256).digest()
            )
            if not hmac.compare_digest(signature, expected):
                return None
            payload = json.loads(_b64decode(body).decode("utf-8"))
            current_time = int(time.time() if now is None else now)
            if int(payload["exp"]) <= current_time:
                return None
            return Session(
                user_id=int(payload["uid"]),
                expires_at=int(payload["exp"]),
                nonce=str(payload["nonce"]),
            )
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return None

    def csrf_token(self, nonce: str) -> str:
        return _b64encode(
            hmac.new(self._secret, f"csrf:{nonce}".encode("utf-8"), hashlib.sha256).digest()
        )

    def valid_csrf(self, session: Session, supplied: str | None) -> bool:
        return bool(supplied) and hmac.compare_digest(
            self.csrf_token(session.nonce), str(supplied)
        )
