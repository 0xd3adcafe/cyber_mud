from __future__ import annotations

import hashlib
import json
import secrets
from base64 import b64decode, b64encode
from dataclasses import dataclass
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from client.themes import settings_path
from shared.i18n import t

PBKDF2_ITERATIONS = 600_000
SALT_BYTES = 16
NONCE_BYTES = 12
STORE_VERSION = 1
PIN_MIN_LEN = 4
PIN_MAX_LEN = 6


@dataclass(frozen=True)
class StoredCredentials:
    username: str
    mode: str
    session_token: str = ""
    password: str = ""


def credentials_path() -> Path:
    return settings_path().parent / "credentials.json"


def validate_pin(pin: str, locale: str = "en") -> str | None:
    if not pin.isdigit():
        return t(locale, "client.credentials.pin_digits")
    if not PIN_MIN_LEN <= len(pin) <= PIN_MAX_LEN:
        return t(
            locale,
            "client.credentials.pin_length",
            min=str(PIN_MIN_LEN),
            max=str(PIN_MAX_LEN),
        )
    return None


def _derive_key(pin: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
        dklen=32,
    )


def _encrypt_payload(pin: str, payload: dict[str, str]) -> dict[str, str | int]:
    salt = secrets.token_bytes(SALT_BYTES)
    key = _derive_key(pin, salt)
    nonce = secrets.token_bytes(NONCE_BYTES)
    plaintext = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    return {
        "version": STORE_VERSION,
        "salt": b64encode(salt).decode("ascii"),
        "nonce": b64encode(nonce).decode("ascii"),
        "ciphertext": b64encode(ciphertext).decode("ascii"),
    }


def _decrypt_payload(pin: str, data: dict) -> dict[str, str] | None:
    try:
        if data.get("version") != STORE_VERSION:
            return None
        salt = b64decode(str(data["salt"]))
        nonce = b64decode(str(data["nonce"]))
        ciphertext = b64decode(str(data["ciphertext"]))
        key = _derive_key(pin, salt)
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
        parsed = json.loads(plaintext.decode("utf-8"))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, InvalidTag):
        return None
    if not isinstance(parsed, dict):
        return None
    username = str(parsed.get("username", "")).strip()
    mode = str(parsed.get("mode", "login"))
    session_token = str(parsed.get("session_token", "")).strip()
    password = str(parsed.get("password", ""))
    if not username or mode not in ("login", "register"):
        return None
    if session_token:
        return {
            "username": username,
            "mode": mode,
            "session_token": session_token,
            "password": "",
        }
    if password:
        return {
            "username": username,
            "mode": mode,
            "session_token": "",
            "password": password,
        }
    return None


def load_store_blob() -> dict | None:
    path = credentials_path()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    if not isinstance(raw, dict):
        return None
    return raw


def has_stored_credentials() -> bool:
    return load_store_blob() is not None


def save_credentials(
    *,
    username: str,
    mode: str,
    pin: str,
    session_token: str = "",
    password: str = "",
) -> str | None:
    pin_err = validate_pin(pin, "en")
    if pin_err:
        return pin_err
    name = username.strip()
    token = session_token.strip()
    if not name:
        return "帳號不可為空。"
    if not token and not password:
        return "缺少可儲存的登入憑證。"
    if mode not in ("login", "register"):
        return "無效的帳號模式。"
    payload: dict[str, str] = {"username": name, "mode": mode}
    if token:
        payload["session_token"] = token
    else:
        payload["password"] = password
    blob = _encrypt_payload(pin, payload)
    path = credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return None


def unlock_credentials(pin: str) -> StoredCredentials | None:
    data = load_store_blob()
    if data is None:
        return None
    payload = _decrypt_payload(pin, data)
    if payload is None:
        return None
    return StoredCredentials(
        username=payload["username"],
        mode=payload["mode"],
        session_token=payload.get("session_token", ""),
        password=payload.get("password", ""),
    )


def clear_credentials() -> None:
    path = credentials_path()
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass