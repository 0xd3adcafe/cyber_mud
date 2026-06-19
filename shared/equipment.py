from __future__ import annotations

from shared.i18n import t
from shared.locale_content import item_label

EQUIP_SLOTS = ("weapon", "armor", "head", "cyber")


def slot_label(slot: str, locale: str) -> str:
    label = t(locale, f"equipment.slot.{slot}")
    return label if label != f"equipment.slot.{slot}" else slot


def format_equipment_lines(player, world, locale: str) -> list[str]:
    lines = [t(locale, "equipment.header"), ""]
    for slot in EQUIP_SLOTS:
        item_id = player.equipment.get(slot, "")
        if item_id:
            item = world.item(item_id)
            label = item_label(item, locale)
            lines.append(t(locale, "equipment.slot_line", slot=slot_label(slot, locale), item=label))
        else:
            lines.append(t(locale, "equipment.empty_slot", slot=slot_label(slot, locale)))
    return lines