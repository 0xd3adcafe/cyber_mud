from __future__ import annotations

import re

NAME_MIN_LEN = 2
NAME_MAX_LEN = 24
PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 128
MAX_LINE_BYTES = 4096

_INVALID_NAME_RE = re.compile(r"[/\\]|\.\.")


def validate_character_name(name: str) -> str | None:
    if not name or len(name) < NAME_MIN_LEN:
        return "auth.name_short"
    if len(name) > NAME_MAX_LEN:
        return "auth.name_long"
    if _INVALID_NAME_RE.search(name) or any(ord(ch) < 32 for ch in name):
        return "auth.name_invalid"
    return None


def validate_password(password: str) -> str | None:
    if not password:
        return "auth.password_empty"
    if len(password) < PASSWORD_MIN_LEN:
        return "auth.password_short"
    if len(password) > PASSWORD_MAX_LEN:
        return "auth.password_long"
    return None