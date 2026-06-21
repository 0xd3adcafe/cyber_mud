from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MATURE_DATA_ROOT = REPO_ROOT / "data" / "mature"


def mature_locale_path(locale: str) -> Path:
    return MATURE_DATA_ROOT / "locale" / f"mature_{locale}.yaml"


def romance_path() -> Path:
    return MATURE_DATA_ROOT / "romance.yaml"


def quests_mature_path() -> Path:
    return MATURE_DATA_ROOT / "quests_mature.yaml"


def braindances_mature_path() -> Path:
    return MATURE_DATA_ROOT / "braindances_mature.yaml"


def mature_content_available() -> bool:
    return all(
        path.is_file()
        for path in (
            mature_locale_path("en"),
            mature_locale_path("zh"),
            romance_path(),
            quests_mature_path(),
            braindances_mature_path(),
        )
    )