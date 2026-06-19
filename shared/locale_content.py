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


def command_name_suffix(name_en: str, entity_id: str) -> str:
    return name_en.strip() if name_en and name_en.strip() else entity_id


def label_with_command_suffix(label: str, suffix: str) -> str:
    if not suffix or suffix.lower() == label.lower():
        return label
    return f"{label} ({suffix})"


def _label_with_suffix(label: str, suffix: str) -> str:
    return label_with_command_suffix(label, suffix)


def item_label_with_id(item, locale: str) -> str:
    if item is None:
        return "?"
    label = item_label(item, locale)
    return _label_with_suffix(label, command_name_suffix(item.name_en, item.id))


def net_node_label(node, locale: str) -> str:
    if node is None:
        return "?"
    if locale == "en" and node.name_en:
        return node.name_en
    return node.name_zh or node.id


def net_node_label_with_id(node, locale: str) -> str:
    if node is None:
        return "?"
    label = net_node_label(node, locale)
    return _label_with_suffix(label, command_name_suffix(node.name_en, node.id))


def npc_label_with_id(npc, locale: str) -> str:
    if npc is None:
        return "?"
    if locale == "en" and npc.name_en:
        label = npc.name_en
    else:
        label = npc.name_zh or npc.id
    return _label_with_suffix(label, command_name_suffix(npc.name_en, npc.id))


def direction_label(direction: str, locale: str) -> str:
    key = f"direction.{direction}"
    translated = t(locale, key)
    if translated == key:
        translated = direction
    return _label_with_suffix(translated, direction)


def format_room_exits(room, _world, locale: str) -> str:
    segments = [direction_label(direction, locale) for direction in sorted(room.exits)]
    return "、".join(segments)