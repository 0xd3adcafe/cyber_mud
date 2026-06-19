from __future__ import annotations

from shared.i18n import t

# CP2077 義體槽位
CYBERWARE_SLOTS: tuple[str, ...] = (
    "cyberdeck",
    "frontal",
    "ocular",
    "cardiovascular",
    "nervous",
    "integumentary",
    "skeleton",
    "arms",
    "legs",
)

SLOT_LEGACY_ALIASES: dict[str, str] = {
    "cyber": "arms",
}


def resolve_cyber_slot(slot: str) -> str:
    return SLOT_LEGACY_ALIASES.get(slot, slot)


def slot_label(slot: str, locale: str) -> str:
    key = f"cyberware.slot.{resolve_cyber_slot(slot)}"
    label = t(locale, key)
    return label if label != key else slot