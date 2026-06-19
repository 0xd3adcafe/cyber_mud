from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "locale"


@lru_cache(maxsize=4)
def _load_locale(locale: str) -> dict:
    path = DATA_ROOT / f"{locale}.yaml"
    if not path.exists():
        path = DATA_ROOT / "zh.yaml"
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def t(locale: str, key: str, **kwargs: str) -> str:
    data = _load_locale(locale)
    parts = key.split(".")
    node = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return key
        node = node[part]
    if not isinstance(node, str):
        return key
    try:
        return node.format(**kwargs)
    except KeyError:
        return node


def t_list(locale: str, key: str) -> list[str]:
    data = _load_locale(locale)
    parts = key.split(".")
    node = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return []
        node = node[part]
    return list(node) if isinstance(node, list) else []