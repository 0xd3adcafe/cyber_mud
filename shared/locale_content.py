from __future__ import annotations

from shared.i18n import t


def room_name(room, locale: str) -> str:
    if locale == "en" and getattr(room, "name_en", ""):
        return room.name_en
    return room.name_zh or room.id


def room_description(room, locale: str) -> str:
    if locale == "en" and getattr(room, "description_en", ""):
        return room.description_en
    return room.description_zh or ""


def item_label(item, locale: str) -> str:
    if item is None:
        return "?"
    if locale == "en" and item.name_en:
        return item.name_en
    return item.name_zh or item.id