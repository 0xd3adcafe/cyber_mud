from __future__ import annotations

AUTH_MODES = ("login", "register")


def build_auth_command(mode: str, name: str, password: str, *, mature: bool = False) -> str | None:
    name = name.strip()
    password = password  # preserve spaces in password if any
    if not name or not password:
        return None
    if mode not in AUTH_MODES:
        return None
    if mode == "register" and mature:
        return f"register {name} {password} mature"
    return f"{mode} {name} {password}"


def mask_auth_log_line(mode: str, name: str) -> str:
    label = "登入" if mode == "login" else "註冊"
    return f"[dim]▸ {label}：{name}（密碼已隱藏）[/]"