from __future__ import annotations

import json
import sys
import time
from typing import Any


def log_security_event(event: str, **fields: Any) -> None:
    payload = {
        "ts": time.time(),
        "event": event,
        **fields,
    }
    line = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    sys.stderr.write(f"[audit] {line}\n")
    sys.stderr.flush()