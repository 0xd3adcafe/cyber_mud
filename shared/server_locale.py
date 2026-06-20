from __future__ import annotations

import os

DEFAULT_SERVER_LOCALE = "en"


def server_locale() -> str:
    value = os.environ.get("CYBER_MUD_SERVER_LOCALE", DEFAULT_SERVER_LOCALE).strip().lower()
    return value if value in {"en", "zh"} else DEFAULT_SERVER_LOCALE