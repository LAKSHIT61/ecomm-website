import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone

from ..config import settings


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64url(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str) -> str:
    """Hash a password using scrypt with a random salt."""
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=64)
    return "scrypt$16384$8$1${}${}".format(_b64url(salt), _b64url(digest))


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, n, r, p, salt_b64, digest_b64 = encoded.split("$", 5)
        if scheme != "scrypt":
            return False
        salt = _unb64url(salt_b64)
        expected = _unb64url(digest_b64)
        actual = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p), dklen=len(expected)
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    payload = {"sub": str(user_id), "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp())}
    header_part = _b64url(json.dumps(header, separators=(",", ":")).encode())
    payload_part = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_part}.{payload_part}".encode()
    signature = hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest()
    return f"{header_part}.{payload_part}.{_b64url(signature)}"


def decode_access_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3 or settings.jwt_algorithm != "HS256":
        raise ValueError("Invalid token")
    signing_input = f"{parts[0]}.{parts[1]}".encode()
    expected = hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _unb64url(parts[2])):
        raise ValueError("Invalid token signature")
    payload = json.loads(_unb64url(parts[1]).decode())
    if int(payload.get("exp", 0)) <= int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Token expired")
    return payload
