ENCODING = "utf-8"
MAX_LINE_BYTES = 4096
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4000
DEFAULT_ADMIN_PORT = 4001

META_PREFIX = "@meta "
PANEL_PREFIX = "@panel "
UI_PREFIX = "@ui "
MOTD_PREFIX = "◈ "
SYS_PREFIX = "▸ "
ERR_PREFIX = "✖ "


def meta_line(key: str, value: str) -> str:
    return f"{META_PREFIX}{key}={value}"


def ui_line(payload: str) -> str:
    return f"{UI_PREFIX}{payload}"