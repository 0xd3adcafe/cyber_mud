from __future__ import annotations

from commands.registry import CommandContext
from shared.equipment import EQUIP_SLOTS, slot_label
from shared.i18n import t
from shared.locale_content import item_label, item_label_with_id, npc_label_with_id, room_description, room_name
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


def find_item_anywhere(ctx: CommandContext, item_name: str) -> str | None:
    item_id = find_item_id(
        ctx.state,
        item_name,
        room_id=ctx.player.room_id,
        inventory=ctx.player.inventory,
    )
    if item_id is not None:
        return item_id
    for equipped_id in ctx.player.equipment.values():
        if not equipped_id:
            continue
        item = ctx.state.world.item(equipped_id)
        if item and matches_name(item_name, item.id, item.name_zh, item.name_en):
            return equipped_id
    return None


def item_description(item, locale: str) -> str:
    if locale == "en" and item.description_en:
        return item.description_en
    return item.description_zh or ""


def npc_description(npc, locale: str) -> str:
    if locale == "en" and npc.description_en:
        return npc.description_en
    return npc.description_zh or ""


def resolve_equipment_slot_name(ctx: CommandContext, name: str) -> str | None:
    needle = name.strip().lower()
    if not needle:
        return None
    aliases = {
        "equipment": "",
        "gear": "",
        "裝備": "",
        "weapon": "weapon",
        "armor": "armor",
        "head": "head",
        "cyber": "cyber",
        "武器": "weapon",
        "護甲": "armor",
        "頭部": "head",
        "義體": "cyber",
        "義體槽": "cyber",
    }
    if needle in aliases:
        slot = aliases[needle]
        return slot or None
    for slot in EQUIP_SLOTS:
        label = slot_label(slot, ctx.player.locale).strip().lower()
        if needle == slot or needle == label:
            return slot
    return None


def item_location_line(ctx: CommandContext, item_id: str) -> str | None:
    locale = ctx.player.locale
    if item_id in ctx.state.items_in_room(ctx.player.room_id):
        return t(locale, "look.location.ground")
    if item_id in ctx.player.inventory:
        return t(locale, "look.location.inventory")
    for slot, equipped_id in ctx.player.equipment.items():
        if equipped_id == item_id:
            return t(locale, "look.location.equipped", slot=slot_label(slot, locale))
    return None


def format_look_item(ctx: CommandContext, item_id: str) -> list[str]:
    item = ctx.state.world.item(item_id)
    if item is None:
        return [t(ctx.player.locale, "look.not_found", target=item_id)]

    locale = ctx.player.locale
    lines = [
        t(locale, "look.target_header", name=item_label_with_id(item, locale)),
        "",
        item_description(item, locale),
    ]
    location = item_location_line(ctx, item_id)
    if location:
        lines.append(location)
    if item.slot:
        lines.append(t(locale, "look.item.slot", slot=slot_label(item.slot, locale)))
    if item.weapon_damage:
        lines.append(t(locale, "look.item.damage", value=str(item.weapon_damage)))
    if item.defense:
        lines.append(t(locale, "look.item.defense", value=str(item.defense)))
    if item.value:
        lines.append(t(locale, "look.item.value", value=str(item.value)))
    take_key = "look.item.takeable" if item.takeable else "look.item.not_takeable"
    lines.append(t(locale, take_key))
    if item.implant_id:
        implant = ctx.state.world.implant(item.implant_id)
        implant_name = item.implant_id
        if implant and (implant.name_zh or implant.name_en):
            implant_name = item_label(implant, locale)
        lines.append(t(locale, "look.item.implant", implant=implant_name))
    mod_labels: list[str] = []
    for mod_id in ctx.player.weapon_mods.get(item_id, []):
        mod = ctx.state.world.mod(mod_id)
        if mod:
            mod_labels.append(item_label(mod, locale))
    if mod_labels:
        lines.append(t(locale, "look.item.mods", mods="、".join(mod_labels)))
    return lines


def format_look_npc(ctx: CommandContext, npc_id: str) -> list[str]:
    npc = ctx.state.world.npc(npc_id)
    if npc is None:
        return [t(ctx.player.locale, "look.not_found", target=npc_id)]

    locale = ctx.player.locale
    label = npc_label_with_id(npc, locale)
    lines = [t(locale, "look.target_header", name=label), "", npc_description(npc, locale)]

    from combat.encounter import encounter_for_player

    max_hp = npc.max_hp or npc.hp
    hp = npc.hp
    encounter = encounter_for_player(ctx.state, ctx.player)
    in_fight = encounter is not None and encounter.npc_id == npc_id
    if in_fight and encounter is not None:
        hp = encounter.npc_hp
        lines.append(t(locale, "look.npc.in_combat"))
    lines.append(t(locale, "look.npc.hp", hp=str(hp), max_hp=str(max_hp)))
    if npc.attack:
        lines.append(t(locale, "look.npc.attack", value=str(npc.attack)))
    mood_key = "look.npc.hostile" if npc.hostile else "look.npc.peaceful"
    lines.append(t(locale, mood_key))
    if npc.quest_id:
        quest = ctx.state.world.quest(npc.quest_id)
        if quest:
            quest_name = quest.name_zh if locale == "zh" else (quest.name_en or quest.name_zh)
            lines.append(t(locale, "look.npc.quest", quest=quest_name or npc.quest_id))
    return lines


def format_look_equipment_slot(ctx: CommandContext, slot: str) -> list[str]:
    item_id = ctx.player.equipment.get(slot, "")
    if not item_id:
        return [t(ctx.player.locale, "look.slot_missing", slot=slot_label(slot, ctx.player.locale))]
    return format_look_item(ctx, item_id)


def format_look_equipment(ctx: CommandContext) -> list[str]:
    locale = ctx.player.locale
    lines = [t(locale, "look.equipment.header"), ""]
    any_item = False
    for slot in EQUIP_SLOTS:
        item_id = ctx.player.equipment.get(slot, "")
        slot_name = slot_label(slot, locale)
        if not item_id:
            lines.append(t(locale, "look.equipment.empty_slot", slot=slot_name))
            continue
        any_item = True
        item = ctx.state.world.item(item_id)
        label = item_label(item, locale) if item else item_id
        lines.append(t(locale, "look.equipment.slot_line", slot=slot_name, item=label))
        if item:
            desc = item_description(item, locale)
            if desc:
                lines.append(f"  {desc}")
            stats: list[str] = []
            if item.weapon_damage:
                stats.append(t(locale, "look.item.damage", value=str(item.weapon_damage)))
            if item.defense:
                stats.append(t(locale, "look.item.defense", value=str(item.defense)))
            if stats:
                lines.append("  " + "  ".join(stats))
    if not any_item:
        lines.append(t(locale, "look.equipment.all_empty"))
    return lines


def format_look_target(ctx: CommandContext, target: str) -> list[str]:
    text = target.strip()
    if not text:
        return format_look(ctx)

    slot = resolve_equipment_slot_name(ctx, text)
    if text.strip().lower() in ("equipment", "gear", "裝備"):
        return format_look_equipment(ctx)
    if slot:
        return format_look_equipment_slot(ctx, slot)

    npc_id = find_npc_id(ctx.state, text, ctx.player.room_id)
    if npc_id:
        return format_look_npc(ctx, npc_id)

    item_id = find_item_anywhere(ctx, text)
    if item_id:
        return format_look_item(ctx, item_id)

    return [t(ctx.player.locale, "look.not_found", target=text)]


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
                labels.append(item_label_with_id(item, ctx.player.locale))
        if labels:
            lines.append(t(ctx.player.locale, "look.items", items="、".join(labels)))

    npc_labels = []
    for npc_id in ctx.state.npcs_in_room(ctx.player.room_id):
        npc = ctx.state.world.npc(npc_id)
        if npc:
            npc_labels.append(npc_label_with_id(npc, ctx.player.locale))
    if npc_labels:
        lines.append(t(ctx.player.locale, "look.npcs", npcs="、".join(npc_labels)))

    return lines