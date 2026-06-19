from __future__ import annotations

import json


def panel_json(*, panel: str, title: str, sections: list[dict]) -> str:
    return json.dumps({"panel": panel, "title": title, "sections": sections}, ensure_ascii=False)