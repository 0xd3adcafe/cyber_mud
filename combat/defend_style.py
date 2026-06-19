from __future__ import annotations

from entities.player import Player
from shared.equipment import BODY_ARMOR_SLOTS, active_weapon
from shared.locale_content import item_label
from world.world import World


def _equipped_item(player: Player, world: World, slot: str):
    item_id = player.equipment.get(slot, "")
    if not item_id:
        return None
    return world.item(item_id)


def defend_style(player: Player, world: World) -> str:
    has_armor = any(_equipped_item(player, world, slot) is not None for slot in BODY_ARMOR_SLOTS)
    has_head = _equipped_item(player, world, "head") is not None
    has_weapon = active_weapon(player, world) is not None
    if has_armor and has_head:
        return "armor_head"
    if has_armor:
        return "armor"
    if has_head:
        return "head"
    if has_weapon:
        return "weapon"
    return "bare"


def defend_combat_key(player: Player, world: World) -> str:
    return f"combat.defend_{defend_style(player, world)}"


def defend_help_key(player: Player, world: World) -> str:
    return f"help_cmds.defend_{defend_style(player, world)}"


def defend_combat_kwargs(player: Player, world: World, locale: str) -> dict[str, str]:
    if defend_style(player, world) != "weapon":
        return {}
    weapon = active_weapon(player, world)
    if weapon is None:
        return {}
    return {"weapon": item_label(weapon, locale)}