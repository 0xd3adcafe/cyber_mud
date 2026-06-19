from __future__ import annotations

from commands.registry import CommandContext
from shared.i18n import t
from shared.locale_content import item_label, room_description, room_name
from shared.names import matches_name
from world.state import WorldState
from world.weather import weather_label


def find_item_id(
    state: WorldState,
    item_name: str,
    *,
    room_id: str | None = None,
    inventory: list[str] | None = None,
) -> str | None:
    pools: list[list[str]] = []
    if room_id is not None:
        pools.append(state.items_in_room(room_id))
    if inventory is not None:
        pools.append(inventory)
    for pool in pools:
        for item_id in pool:
            item = state.world.item(item_id)
            if item and matches_name(item_name, item.id, item.name_zh, item.name_en):
                return item_id
    return None


def find_npc_id(state: WorldState, npc_name: str, room_id: str) -> str | None:
    for npc_id in state.npcs_in_room(room_id):
        npc = state.world.npc(npc_id)
        if npc and matches_name(npc_name, npc.id, npc.name_zh, npc.name_en):
            return npc_id
    return None


def faction_label(world, faction_id: str, locale: str) -> str:
    if not faction_id:
        return t(locale, "pda.faction_none")
    return world.factions.get(faction_id, faction_id)


def resolve_faction_id(world, name: str) -> str | None:
    needle = name.strip().lower()
    if not needle:
        return None
    for faction_id, label in world.factions.items():
        if needle == faction_id.lower():
            return faction_id
        if needle in label.lower() or label.lower() in needle:
            return faction_id
    return None


def quest_hint_for_player(ctx: CommandContext) -> str:
    if ctx.player.chased_by_npc:
        from combat.encounter import npc_label

        label = npc_label(ctx.state, ctx.player.chased_by_npc, ctx.player.locale)
        return t(ctx.player.locale, "chase.hint", target=label)
    if ctx.player.active_quest:
        quest = ctx.state.world.quest(ctx.player.active_quest)
        if quest:
            if ctx.player.locale == "zh":
                return quest.hint_zh
            return quest.hint_en or quest.hint_zh
    return ""


def quest_label_for_player(ctx: CommandContext) -> str:
    if not ctx.player.active_quest:
        return ""
    quest = ctx.state.world.quest(ctx.player.active_quest)
    if quest is None:
        return ctx.player.active_quest
    if ctx.player.locale == "zh":
        return quest.name_zh or quest.id
    return quest.name_en or quest.name_zh or quest.id


def current_room(ctx: CommandContext):
    return ctx.state.world.room(ctx.player.room_id)


def mark_visited(ctx: CommandContext) -> None:
    if ctx.player.room_id not in ctx.player.visited_rooms:
        ctx.player.visited_rooms.append(ctx.player.room_id)


def format_look(ctx: CommandContext) -> list[str]:
    mark_visited(ctx)
    room = current_room(ctx)
    if room is None:
        return [t(ctx.player.locale, "look.empty")]

    lines = [
        t(ctx.player.locale, "look.header", name=room_name(room, ctx.player.locale)),
        "",
        room_description(room, ctx.player.locale),
    ]
    if room.district:
        weather_type = ctx.state.weather.get(room.district, "")
        if weather_type:
            lines.append(
                t(
                    ctx.player.locale,
                    "weather.line",
                    weather=weather_label(weather_type, ctx.player.locale),
                )
            )
    if room.exits:
        exits = "、".join(f"{d}→{room.exits[d]}" for d in sorted(room.exits))
        lines.append("")
        lines.append(t(ctx.player.locale, "look.exits", exits=exits))

    item_ids = ctx.state.items_in_room(ctx.player.room_id)
    if item_ids:
        labels = []
        for item_id in item_ids:
            item = ctx.state.world.item(item_id)
            if item:
                labels.append(item.name_zh if ctx.player.locale == "zh" else (item.name_en or item.name_zh))
        if labels:
            lines.append(t(ctx.player.locale, "look.items", items="、".join(labels)))

    npc_labels = []
    for npc_id in ctx.state.npcs_in_room(ctx.player.room_id):
        npc = ctx.state.world.npc(npc_id)
        if npc:
            npc_labels.append(npc.name_zh if ctx.player.locale == "zh" else (npc.name_en or npc.name_zh))
    if npc_labels:
        lines.append(t(ctx.player.locale, "look.npcs", npcs="、".join(npc_labels)))

    return lines