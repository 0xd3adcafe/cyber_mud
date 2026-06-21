from __future__ import annotations

import time

LOCKOUT_MAX_FAILURES = 10
LOCKOUT_SECONDS = 900


def is_account_locked(*, locked_until: float, now: float | None = None) -> bool:
    if locked_until <= 0:
        return False
    current = time.time() if now is None else now
    return current < locked_until


def lockout_remaining_seconds(*, locked_until: float, now: float | None = None) -> int:
    if locked_until <= 0:
        return 0
    current = time.time() if now is None else now
    return max(0, int(locked_until - current))


def record_auth_failure(*, failed_attempts: int, locked_until: float, now: float | None = None) -> tuple[int, float, bool]:
    """Return updated (failed_attempts, locked_until, newly_locked)."""
    current = time.time() if now is None else now
    if is_account_locked(locked_until=locked_until, now=current):
        return failed_attempts, locked_until, False
    attempts = failed_attempts + 1
    if attempts >= LOCKOUT_MAX_FAILURES:
        return 0, current + LOCKOUT_SECONDS, True
    return attempts, locked_until, False


def clear_lockout_state() -> tuple[int, float]:
    return 0, 0.0