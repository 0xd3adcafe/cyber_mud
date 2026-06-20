from __future__ import annotations

from commands.registry import CommandContext
from shared.equipment import (
    EQUIP_SLOTS,
    format_npc_equipment_lines,
    slot_label,
    effective_weapon_mode,
    weapon_class_label,
    weapon_mode_label,
    weapon_type_label,
)
from shared.i18n import t
from shared.locale_content import (
    format_room_exits,
    item_label,
    item_label_with_id,
    net_node_label_with_id,
    npc_label_with_id,
    room_description,
    room_name,
)
from shared.names import matches_name
from shared.target_resolve import (
    ItemRef,
    item_location_line_for_ref,
    resolve_corpse,
    resolve_item,
    resolve_net_node,
    resolve_npc,
)
from world.corpses import corpse_label, corpses_in_room, decay_time_label, find_corpse_id
from world.state import WorldState
from world.weather import weather_label


def resolve_look_item(ctx: CommandContext, target: str) -> list[str] | None:
    result = resolve_item(
        ctx,
        target,
        scopes=("ground", "inventory", "equipped", "corpse", "stash"),
        verb="look",
    )
    if result.needs_response:
        return result.lines
    if not result.ok:
        return None
    return format_look_item(ctx, result.value)


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


def find_net_node_id(state: WorldState, node_name: str, room_id: str) -> str | None:
    for node in state.world.net_nodes_in_room(room_id):
        if matches_name(node_name, node.id, node.name_zh, node.name_en):
            return node.id
    return None


def find_npc_id(state: WorldState, npc_name: str, room_id: str) -> str | None:
    for npc_id in state.npcs_in_room(room_id):
        npc = state.world.npc(npc_id)
        if npc and matches_name(npc_name, npc.id, npc.name_zh, npc.name_en):
            return npc_id
    return None


def find_item_in_corpse(state: WorldState, item_name: str, corpse_id: str) -> str | None:
    corpse = state.corpses.get(corpse_id)
    if corpse is None:
        return None
    for item_id in corpse.loot:
        item = state.world.item(item_id)
        if item and matches_name(item_name, item.id, item.name_zh, item.name_en):
            return item_id
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
        "weapon": "weapon_primary",
        "weapon_primary": "weapon_primary",
        "weapon_secondary": "weapon_secondary",
        "armor": "outer_torso",
        "head": "head",
        "cyber": "cyber",
        "inner_torso": "inner_torso",
        "outer_torso": "outer_torso",
        "legs": "legs",
        "feet": "feet",
        "武器": "weapon_primary",
        "主要武器": "weapon_primary",
        "次要武器": "weapon_secondary",
        "護甲": "outer_torso",
        "頭部": "head",
        "內層": "inner_torso",
        "內層上身": "inner_torso",
        "外套": "outer_torso",
        "外套上身": "outer_torso",
        "下身": "legs",
        "腿部": "legs",
        "足部": "feet",
        "鞋子": "feet",
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
    for corpse in corpses_in_room(ctx.state, ctx.player.room_id):
        if item_id in corpse.loot:
            return t(locale, "look.location.corpse", corpse=corpse_label(ctx.state, corpse, locale))
    if item_id in ctx.player.home_stash:
        return t(locale, "look.location.stash")
    return None


def format_look_item(ctx: CommandContext, ref: ItemRef | str) -> list[str]:
    item_ref = ref if isinstance(ref, ItemRef) else ItemRef(str(ref), "")
    item_id = item_ref.item_id
    item = ctx.state.world.item(item_id)
    if item is None:
        return [t(ctx.player.locale, "look.not_found", target=item_id)]

    locale = ctx.player.locale
    lines = [
        t(locale, "look.target_header", name=item_label_with_id(item, locale)),
        "",
        item_description(item, locale),
    ]
    location = (
        item_location_line_for_ref(ctx, item_ref)
        if item_ref.scope
        else item_location_line(ctx, item_id)
    )
    if location:
        lines.append(location)
    if item.slot:
        lines.append(t(locale, "look.item.slot", slot=slot_label(item.slot, locale)))
    if item.weapon_type:
        lines.append(t(locale, "look.item.weapon_type", type=weapon_type_label(item.weapon_type, locale)))
    if item.weapon_class:
        lines.append(
            t(locale, "look.item.weapon_class", weapon_class=weapon_class_label(item.weapon_class, locale))
        )
    if item.slot == "weapon":
        mode = effective_weapon_mode(item)
        if mode:
            lines.append(t(locale, "look.item.weapon_mode", mode=weapon_mode_label(mode, locale)))
    if item.weapon_damage:
        lines.append(t(locale, "look.item.damage", value=str(item.weapon_damage)))
    if item.defense:
        lines.append(t(locale, "look.item.defense", value=str(item.defense)))
    if item.value:
        lines.append(t(locale, "look.item.value", value=str(item.value)))
    if item.consumable:
        lines.append(
            t(
                locale,
                "look.item.consumable",
                kind=t(locale, f"consumable.kind.{item.consumable}"),
            )
        )
        if item.hp_restore:
            lines.append(t(locale, "look.item.hp_restore", value=str(item.hp_restore)))
        if item.ram_restore:
            lines.append(t(locale, "look.item.ram_restore", value=str(item.ram_restore)))
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


def format_look_corpse(ctx: CommandContext, corpse_id: str) -> list[str]:
    corpse = ctx.state.corpses.get(corpse_id)
    if corpse is None:
        return [t(ctx.player.locale, "look.not_found", target=corpse_id)]

    locale = ctx.player.locale
    label = corpse_label(ctx.state, corpse, locale)
    lines = [t(locale, "look.target_header", name=label), ""]
    if corpse.player_name:
        lines.append(t(locale, "corpse.player_desc", name=corpse.player_name))
        lines.append("")
    else:
        npc = ctx.state.world.npc(corpse.npc_id)
        if npc:
            lines.append(npc_description(npc, locale))
            lines.append("")
    from combat.gore import maybe_gore_corpse

    lines.extend(maybe_gore_corpse(ctx.player, locale, corpse, ctx.state))
    if corpse.loot:
        item_labels = []
        for item_id in corpse.loot:
            item = ctx.state.world.item(item_id)
            if item:
                item_labels.append(item_label_with_id(item, locale))
        if item_labels:
            lines.append(t(locale, "corpse.look_items", items="、".join(item_labels)))
    else:
        lines.append(t(locale, "corpse.look_empty"))
    decay = decay_time_label(ctx.state, corpse, locale)
    if decay:
        lines.append(t(locale, "corpse.look_decay", time=decay))
    return lines


def format_look_net_node(ctx: CommandContext, node_id: str) -> list[str]:
    node = ctx.state.world.net_node(node_id)
    if node is None:
        return [t(ctx.player.locale, "look.not_found", target=node_id)]

    locale = ctx.player.locale
    label = net_node_label_with_id(node, locale)
    lines = [t(locale, "look.target_header", name=label), ""]
    status_key = "look.net_node.hackable" if node.hackable else "look.net_node.sealed"
    lines.append(t(locale, status_key))
    if ctx.player.net_shell:
        lines.append(t(locale, "look.net_node.hint"))
    return lines


def format_look_npc(ctx: CommandContext, npc_id: str) -> list[str]:
    npc = ctx.state.world.npc(npc_id)
    if npc is None:
        return [t(ctx.player.locale, "look.not_found", target=npc_id)]

    locale = ctx.player.locale
    label = npc_label_with_id(npc, locale)
    lines = [t(locale, "look.target_header", name=label), "", npc_description(npc, locale)]
    from world.mature_flavor import mature_npc_detail

    if detail := mature_npc_detail(npc_id, ctx.player):
        lines.append(detail)

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
    equip_lines = format_npc_equipment_lines(npc, ctx.state.world, locale)
    if equip_lines:
        lines.append(t(locale, "look.npc.equipment_header"))
        lines.extend(equip_lines)
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
    return format_look_item(ctx, ItemRef(item_id, "equipped", slot=slot))


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

    if text.lower() in {"me", "self", "自己"}:
        from world.life import format_self_life

        return format_self_life(ctx.player, ctx.player.locale)

    slot = resolve_equipment_slot_name(ctx, text)
    if text.strip().lower() in ("equipment", "gear", "裝備"):
        return format_look_equipment(ctx)
    if slot:
        return format_look_equipment_slot(ctx, slot)

    corpse_result = resolve_corpse(ctx, text, verb="look")
    if corpse_result.needs_response:
        return corpse_result.lines
    if corpse_result.ok:
        return format_look_corpse(ctx, corpse_result.value)

    npc_result = resolve_npc(ctx, text, verb="look")
    if npc_result.needs_response:
        return npc_result.lines
    if npc_result.ok:
        return format_look_npc(ctx, npc_result.value)

    node_result = resolve_net_node(ctx, text, verb="look")
    if node_result.needs_response:
        return node_result.lines
    if node_result.ok:
        return format_look_net_node(ctx, node_result.value)

    item_lines = resolve_look_item(ctx, text)
    if item_lines is not None:
        return item_lines

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
            from world.quests import quest_hint_for_quest

            return quest_hint_for_quest(ctx.player, ctx.state, quest, ctx.player.locale)
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
    from world.districts import atmosphere_line, grid_flavor_line

    atmosphere = atmosphere_line(room, ctx.player.locale)
    if atmosphere:
        lines.append(atmosphere)
    grid_flavor = grid_flavor_line(room, ctx.player.locale)
    if grid_flavor:
        lines.append(grid_flavor)
    from world.mature_flavor import mature_room_flavor

    mature_flavor = mature_room_flavor(room, ctx.player)
    if mature_flavor:
        lines.append(mature_flavor)
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
        lines.append("")
        lines.append(
            t(
                ctx.player.locale,
                "look.exits",
                exits=format_room_exits(room, ctx.state.world, ctx.player.locale),
            )
        )

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

    if ctx.player.net_shell:
        net_labels = [
            net_node_label_with_id(node, ctx.player.locale)
            for node in ctx.state.world.net_nodes_in_room(ctx.player.room_id)
        ]
        if net_labels:
            lines.append(t(ctx.player.locale, "look.net_nodes", nodes="、".join(net_labels)))

    corpse_labels = [corpse_label(ctx.state, corpse, ctx.player.locale) for corpse in corpses_in_room(ctx.state, ctx.player.room_id)]
    if corpse_labels:
        lines.append(t(ctx.player.locale, "corpse.room_line", corpses="、".join(corpse_labels)))

    from world.interactables import interactable_label

    interact_labels = [
        interactable_label(obj, ctx.player.locale)
        for obj in ctx.state.world.interactables_in_room(ctx.player.room_id)
    ]
    if interact_labels:
        lines.append(t(ctx.player.locale, "look.interactables", objects="、".join(interact_labels)))

    from world.life import peer_posture_line

    peer_labels = [peer_posture_line(peer, ctx.player.locale) for peer in ctx.peers if peer.named]
    if peer_labels:
        lines.append(t(ctx.player.locale, "look.players", players="、".join(peer_labels)))

    return lines