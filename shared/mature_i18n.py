from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "locale"


def clear_mature_locale_cache() -> None:
    _load_mature_locale.cache_clear()


@lru_cache(maxsize=4)
def _load_mature_locale(locale: str) -> dict:
    path = DATA_ROOT / f"mature_{locale}.yaml"
    if not path.exists():
        path = DATA_ROOT / "mature_en.yaml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def tm(locale: str, key: str, **kwargs: str) -> str:
    full_key = key if key.startswith("mature.") else f"mature.{key}"
    data = _load_mature_locale(locale)
    parts = full_key.split(".")
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