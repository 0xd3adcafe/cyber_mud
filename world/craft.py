from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from world.content import Recipe
from world.state import WorldState


def recipe_at_station(player: Player, state: WorldState, recipe: Recipe) -> bool:
    room = state.world.room(player.room_id)
    if room is None or not recipe.station_room_tags:
        return False
    return any(tag in room.tags for tag in recipe.station_room_tags)


def can_craft(player: Player, state: WorldState, recipe: Recipe) -> str | None:
    if not recipe_at_station(player, state, recipe):
        return "craft.no_station"
    if player.gold < recipe.gold_cost:
        return "craft.no_gold"
    for item_id, count in recipe.ingredients.items():
        owned = player.inventory.count(item_id)
        if owned < count:
            return "craft.missing"
    return None


def perform_craft(player: Player, state: WorldState, recipe: Recipe, locale: str) -> list[str]:
    err = can_craft(player, state, recipe)
    if err:
        if err == "craft.no_gold":
            return [t(locale, err, cost=str(recipe.gold_cost))]
        return [t(locale, err)]

    player.gold -= recipe.gold_cost
    for item_id, count in recipe.ingredients.items():
        for _ in range(count):
            player.inventory.remove(item_id)
    for _ in range(recipe.output_count):
        player.inventory.append(recipe.output)

    label = recipe.name_zh if locale == "zh" else (recipe.name_en or recipe.name_zh)
    return [t(locale, "craft.ok", name=label or recipe.id)]


def perform_disassemble(player: Player, state: WorldState, item_id: str, locale: str) -> list[str]:
    recipe = state.world.disassemble_recipe(item_id)
    if recipe is None:
        return [t(locale, "disassemble.unknown", item=item_id)]
    if item_id not in player.inventory:
        return [t(locale, "disassemble.missing", item=item_id)]

    player.inventory.remove(item_id)
    for out_id, count in recipe.outputs.items():
        for _ in range(count):
            player.inventory.append(out_id)
    if recipe.gold_gain > 0:
        player.gold += recipe.gold_gain

    item = state.world.item(item_id)
    label = item.name_zh if item and locale == "zh" else (item.name_en if item else item_id)
    return [t(locale, "disassemble.ok", item=label or item_id, gold=str(recipe.gold_gain))]