from __future__ import annotations

import secrets
import time
from dataclasses import dataclass

TOKEN_TTL_SECONDS = 7 * 24 * 3600


@dataclass
class _SessionRecord:
    player_name: str
    expires_at: float


_TOKENS: dict[str, _SessionRecord] = {}


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def _purge_expired(*, now: float | None = None) -> None:
    current = time.monotonic() if now is None else now
    expired = [token for token, record in _TOKENS.items() if record.expires_at <= current]
    for token in expired:
        _TOKENS.pop(token, None)


def revoke_tokens_for(player_name: str) -> None:
    target = _normalize_name(player_name)
    stale = [token for token, record in _TOKENS.items() if record.player_name == target]
    for token in stale:
        _TOKENS.pop(token, None)


def issue_session_token(player_name: str, *, now: float | None = None) -> str:
    current = time.monotonic() if now is None else now
    _purge_expired(now=current)
    revoke_tokens_for(player_name)
    token = secrets.token_urlsafe(32)
    _TOKENS[token] = _SessionRecord(
        player_name=_normalize_name(player_name),
        expires_at=current + TOKEN_TTL_SECONDS,
    )
    return token


def validate_session_token(token: str, *, now: float | None = None) -> str | None:
    text = token.strip()
    if not text:
        return None
    current = time.monotonic() if now is None else now
    _purge_expired(now=current)
    record = _TOKENS.get(text)
    if record is None or record.expires_at <= current:
        _TOKENS.pop(text, None)
        return None
    return record.player_name


def rotate_session_token(token: str, *, now: float | None = None) -> str | None:
    player_name = validate_session_token(token, now=now)
    if player_name is None:
        return None
    _TOKENS.pop(token.strip(), None)
    return issue_session_token(player_name, now=now)


def clear_all_session_tokens() -> None:
    _TOKENS.clear()