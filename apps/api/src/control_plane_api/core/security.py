import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any


class TokenError(ValueError):
    """Raised when a bearer token is invalid."""


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str, *, iterations: int = 210_000) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt, expected_hex = password_hash.split("$", 3)
        iterations = int(iterations_text)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return hmac.compare_digest(digest.hex(), expected_hex)


def create_access_token(
    *,
    subject: str,
    secret_key: str,
    expires_delta: timedelta,
    claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        **(claims or {}),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str, *, secret_key: str) -> dict[str, Any]:
    if not secret_key:
        raise TokenError("AUTH_SECRET_KEY is not configured")

    parts = token.split(".")
    if len(parts) != 3:
        raise TokenError("Invalid token format")

    signing_input = ".".join(parts[:2])
    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()

    try:
        actual_signature = _b64url_decode(parts[2])
    except Exception as exc:
        raise TokenError("Invalid token signature encoding") from exc

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise TokenError("Invalid token signature")

    try:
        payload = json.loads(_b64url_decode(parts[1]))
    except Exception as exc:
        raise TokenError("Invalid token payload") from exc

    expires_at = payload.get("exp")
    if not isinstance(expires_at, int):
        raise TokenError("Token missing expiration")

    if datetime.now(UTC).timestamp() >= expires_at:
        raise TokenError("Token expired")

    return payload
