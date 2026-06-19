from __future__ import annotations

from entities.item import Item
from entities.player import Player
from shared.i18n import t

CONSUMABLE_TYPES = frozenset({"food", "drink", "medicine"})


def is_consumable(item: Item | None) -> bool:
    return item is not None and item.consumable in CONSUMABLE_TYPES


def calc_consumable_gains(player: Player, item: Item) -> tuple[int, int]:
    hp_gain = 0
    ram_gain = 0
    if item.hp_restore > 0 and player.hp < player.max_hp:
        hp_gain = min(item.hp_restore, player.max_hp - player.hp)
    if item.ram_restore > 0 and player.ram < player.max_ram:
        ram_gain = min(item.ram_restore, player.max_ram - player.ram)
    return hp_gain, ram_gain


def apply_consumable(player: Player, item: Item) -> tuple[int, int]:
    hp_gain, ram_gain = calc_consumable_gains(player, item)
    if hp_gain > 0:
        player.hp += hp_gain
    if ram_gain > 0:
        player.ram += ram_gain
    return hp_gain, ram_gain


def consumable_action_verb(consumable_type: str, locale: str) -> str:
    key = f"consumable.verb.{consumable_type}"
    label = t(locale, key)
    return label if label != key else consumable_type


def format_consumable_effect(locale: str, *, hp_gain: int, ram_gain: int) -> str:
    parts: list[str] = []
    if hp_gain > 0:
        parts.append(t(locale, "consumable.effect_hp", hp=str(hp_gain)))
    if ram_gain > 0:
        parts.append(t(locale, "consumable.effect_ram", ram=str(ram_gain)))
    return "、".join(parts)