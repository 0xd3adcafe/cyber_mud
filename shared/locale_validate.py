from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from shared.i18n import DATA_ROOT

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class LocaleIssue:
    severity: str
    message: str


def _flatten_keys(node: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            keys.update(_flatten_keys(value, path))
    elif isinstance(node, str):
        keys.add(prefix)
    elif isinstance(node, list):
        keys.add(prefix)
    return keys


def _load_locale_keys(locale: str) -> set[str]:
    path = DATA_ROOT / f"{locale}.yaml"
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return _flatten_keys(data)


def validate_main_locale_parity() -> list[LocaleIssue]:
    en_keys = _load_locale_keys("en")
    zh_keys = _load_locale_keys("zh")
    issues: list[LocaleIssue] = []
    for key in sorted(en_keys - zh_keys):
        issues.append(LocaleIssue("error", f"zh.yaml missing key: {key}"))
    for key in sorted(zh_keys - en_keys):
        issues.append(LocaleIssue("warn", f"zh.yaml extra key (no en): {key}"))
    return issues