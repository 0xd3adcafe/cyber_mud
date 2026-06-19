from __future__ import annotations


def should_resend_auth(*, needs_reauth: bool, authenticated: bool, last_auth_line: str) -> bool:
    if not last_auth_line.strip():
        return False
    return needs_reauth or not authenticated


def reconnect_status_message(*, attempt: int, delay: float, max_attempts: int) -> str | None:
    if attempt >= max_attempts:
        return "重連失敗（已達 5 次）。"
    return f"{delay:.0f}s 後重連（第 {attempt} 次）…"