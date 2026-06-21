from __future__ import annotations

from entities.player import Player
from shared.equipment import EQUIP_SLOTS
from shared.i18n import t
from shared.locale_content import item_label
from world.life import posture_label

PERSONA_MAX_LEN = 200


def normalize_persona(text: str) -> str:
    cleaned = " ".join(text.split())
    return cleaned[:PERSONA_MAX_LEN]


def _auto_equipment_bits(player: Player, locale: str) -> list[str]:
    bits: list[str] = []
    world_items = None
    for slot in EQUIP_SLOTS:
        item_id = player.equipment.get(slot, "")
        if not item_id:
            continue
        if world_items is None:
            from world.loader import load_world

            world_items = load_world()
        item = world_items.item(item_id)
        if item:
            bits.append(item_label(item, locale))
    return bits


def persona_one_liner(player: Player, locale: str, *, voice: str = "noir") -> str:
    custom = normalize_persona(player.persona)
    if custom:
        if voice == "lewd":
            wrapped = t(locale, "persona.lewd_wrap", persona=custom)
            if wrapped != "persona.lewd_wrap":
                return wrapped
        return custom

    posture = posture_label(player.posture, locale)
    gear = _auto_equipment_bits(player, locale)
    if gear:
        gear_text = ", ".join(gear[:3])
        return t(locale, "persona.auto_summary", posture=posture, gear=gear_text)
    return t(locale, "persona.auto_summary_bare", posture=posture)


def format_look_player(peer: Player, locale: str) -> list[str]:
    lines = [t(locale, "persona.look_player_header", name=peer.name)]
    persona = normalize_persona(peer.persona)
    if persona:
        lines.append(persona)
    else:
        lines.append(t(locale, "persona.look_player_empty"))
    return lines