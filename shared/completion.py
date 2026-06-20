from __future__ import annotations

from commands.registry import CommandContext

COMMAND_VERBS: tuple[str, ...] = (
    "appraise",
    "braindance",
    "bd",
    "buy",
    "attack",
    "shoot",
    "slash",
    "bash",
    "punch",
    "backstab",
    "defend",
    "drive",
    "drop",
    "equip",
    "equipment",
    "flee",
    "give",
    "go",
    "gigs",
    "home",
    "gig",
    "help",
    "install",
    "inventory",
    "learn",
    "rent",
    "stats",
    "stash",
    "transit",
    "talents",
    "talent",
    "perks",
    "perk",
    "improve",
    "look",
    "map",
    "mod",
    "net",
    "netrun",
    "pda",
    "pledge",
    "prompt",
    "quickhack",
    "quit",
    "recall",
    "register",
    "say",
    "scan",
    "sell",
    "shop",
    "search",
    "status",
    "take",
    "talk",
    "time",
    "unequip",
    "uninstall",
    "vehicles",
    "vehicle",
    "cyberware",
    "chrome",
    "craft",
    "disassemble",
    "interact",
)

LOCAL_COMMAND_VERBS: tuple[str, ...] = ("clear", "log", "prompt", "quit", "reconnect", "theme")

ITEM_TARGET_COMMANDS = frozenset(
    {"take", "drop", "equip", "unequip", "give", "appraise", "buy", "sell", "install", "mod"}
)
NPC_TARGET_COMMANDS = frozenset({"talk", "attack", "give"})
LOOK_TARGET_COMMANDS = frozenset({"look"})
INTERACT_TARGET_COMMANDS = frozenset({"interact"})
CRAFT_TARGET_COMMANDS = frozenset({"craft", "disassemble", "braindance", "bd"})
DIRECTION_COMMANDS = frozenset({"go"})
LOOK_SLOT_HINTS = (
    "equipment",
    "weapon",
    "weapon_primary",
    "weapon_secondary",
    "主要武器",
    "次要武器",
    "head",
    "inner_torso",
    "outer_torso",
    "legs",
    "feet",
    "cyber",
    "armor",
    "護甲",
    "內層",
    "外套",
    "下身",
    "足部",
)
CORPSE_HINTS = ("corpse", "屍體", "body")


def room_item_ids(ctx: CommandContext) -> list[str]:
    return list(ctx.state.items_in_room(ctx.player.room_id))


def room_npc_ids(ctx: CommandContext) -> list[str]:
    return list(ctx.state.npcs_in_room(ctx.player.room_id))


def room_corpse_ids(ctx: CommandContext) -> list[str]:
    from world.corpses import corpses_in_room

    ids: list[str] = []
    for corpse in corpses_in_room(ctx.state, ctx.player.room_id):
        if corpse.player_name:
            ids.append(corpse.player_name)
        elif corpse.npc_id:
            ids.append(corpse.npc_id)
    return ids


def inventory_item_ids(ctx: CommandContext) -> list[str]:
    return list(ctx.player.inventory)


def equipped_item_ids(ctx: CommandContext) -> list[str]:
    return [item_id for item_id in ctx.player.equipment.values() if item_id]


def room_net_node_ids(ctx: CommandContext) -> list[str]:
    return [node.id for node in ctx.state.world.net_nodes_in_room(ctx.player.room_id)]


def room_exit_names(ctx: CommandContext) -> list[str]:
    room = ctx.state.world.room(ctx.player.room_id)
    if room is None:
        return []
    return sorted(room.exits.keys())


def room_interactable_ids(ctx: CommandContext) -> list[str]:
    return [obj.id for obj in ctx.state.world.interactables_in_room(ctx.player.room_id)]


def recipe_ids(ctx: CommandContext) -> list[str]:
    return sorted(ctx.state.world.recipes.keys())


def braindance_ids(ctx: CommandContext) -> list[str]:
    return sorted(ctx.state.world.braindances.keys())


def shop_item_ids(ctx: CommandContext) -> list[str]:
    from world.trade import active_shop

    shop = active_shop(ctx)
    if shop is None:
        return []
    return sorted(shop.sells.keys())


def completion_meta(ctx: CommandContext) -> dict[str, str]:
    return {
        "complete_room_items": ",".join(room_item_ids(ctx)),
        "complete_inventory": ",".join(inventory_item_ids(ctx)),
        "complete_equipped": ",".join(equipped_item_ids(ctx)),
        "complete_shop_items": ",".join(shop_item_ids(ctx)),
        "complete_npcs": ",".join(room_npc_ids(ctx)),
        "complete_corpses": ",".join(room_corpse_ids(ctx)),
        "complete_exits": ",".join(room_exit_names(ctx)),
        "complete_net_nodes": ",".join(room_net_node_ids(ctx)),
        "complete_interactables": ",".join(room_interactable_ids(ctx)),
        "complete_recipes": ",".join(recipe_ids(ctx)),
        "complete_braindances": ",".join(braindance_ids(ctx)),
    }


def parse_csv_meta(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def target_pool_for_verb(
    verb: str,
    *,
    room_items: tuple[str, ...],
    room_npcs: tuple[str, ...],
    room_corpses: tuple[str, ...] = (),
    room_exits: tuple[str, ...],
    inventory: tuple[str, ...],
    equipped: tuple[str, ...] = (),
    shop_items: tuple[str, ...] = (),
    net_nodes: tuple[str, ...] = (),
    interactables: tuple[str, ...] = (),
    recipes: tuple[str, ...] = (),
    braindances: tuple[str, ...] = (),
) -> tuple[str, ...]:
    if verb == "hack":
        return net_nodes
    if verb in INTERACT_TARGET_COMMANDS:
        return interactables
    if verb in CRAFT_TARGET_COMMANDS:
        if verb in {"craft"}:
            return recipes
        if verb in {"braindance", "bd"}:
            return braindances
        return inventory
    if verb in DIRECTION_COMMANDS:
        return room_exits
    if verb in LOOK_TARGET_COMMANDS:
        merged_items = tuple(dict.fromkeys((*room_items, *inventory, *equipped)))
        return tuple(dict.fromkeys((*LOOK_SLOT_HINTS, *CORPSE_HINTS, *merged_items, *room_npcs, *room_corpses)))
    if verb in NPC_TARGET_COMMANDS:
        return room_npcs
    if verb == "buy":
        return shop_items
    if verb in ITEM_TARGET_COMMANDS:
        if verb in {"sell", "appraise", "install", "mod"}:
            return tuple(dict.fromkeys((*inventory, *equipped)))
        if verb in {"drop", "equip", "unequip", "give"}:
            return inventory or room_items
        return room_items
    return ()


def _command_verbs(net_shell: bool) -> tuple[str, ...]:
    if net_shell:
        return ("hack", "probe", "status", "look", "scan", "talk", "say", "exit", "help", "quit")
    return COMMAND_VERBS


def _matching_candidates(prefix: str, partial: str, pool: tuple[str, ...]) -> list[str]:
    matches = [candidate for candidate in pool if candidate.lower().startswith(partial)]
    if prefix:
        return [f"{prefix} {candidate}" for candidate in matches]
    return matches


def complete_input_candidates(
    value: str,
    *,
    room_items: tuple[str, ...],
    room_npcs: tuple[str, ...],
    room_corpses: tuple[str, ...] = (),
    room_exits: tuple[str, ...],
    inventory: tuple[str, ...],
    equipped: tuple[str, ...] = (),
    shop_items: tuple[str, ...] = (),
    net_nodes: tuple[str, ...] = (),
    interactables: tuple[str, ...] = (),
    recipes: tuple[str, ...] = (),
    braindances: tuple[str, ...] = (),
    net_shell: bool = False,
) -> list[str]:
    text = value.strip()
    if not text:
        return []

    if text.startswith("/"):
        partial = text[1:].split()[0].lower() if len(text) > 1 else ""
        return [f"/{verb}" for verb in LOCAL_COMMAND_VERBS if verb.startswith(partial)]

    parts = text.split()
    if len(parts) == 1:
        partial = parts[0].lower()
        return [verb for verb in _command_verbs(net_shell) if verb.startswith(partial)]

    verb = parts[0].lower()
    partial = parts[-1].lower()
    prefix = " ".join(parts[:-1])

    if verb == "take" and len(parts) >= 3 and parts[-2].lower() == "from":
        return _matching_candidates(prefix, partial, (*CORPSE_HINTS, *room_corpses))

    pool = target_pool_for_verb(
        verb,
        room_items=room_items,
        room_npcs=room_npcs,
        room_corpses=room_corpses,
        room_exits=room_exits,
        inventory=inventory,
        equipped=equipped,
        shop_items=shop_items,
        net_nodes=net_nodes if net_shell else (),
        interactables=interactables,
        recipes=recipes,
        braindances=braindances,
    )
    return _matching_candidates(prefix, partial, pool)


def complete_input(
    value: str,
    *,
    room_items: tuple[str, ...],
    room_npcs: tuple[str, ...],
    room_corpses: tuple[str, ...] = (),
    room_exits: tuple[str, ...],
    inventory: tuple[str, ...],
    equipped: tuple[str, ...] = (),
    shop_items: tuple[str, ...] = (),
    net_nodes: tuple[str, ...] = (),
    interactables: tuple[str, ...] = (),
    recipes: tuple[str, ...] = (),
    braindances: tuple[str, ...] = (),
    net_shell: bool = False,
) -> str | None:
    candidates = complete_input_candidates(
        value,
        room_items=room_items,
        room_npcs=room_npcs,
        room_corpses=room_corpses,
        room_exits=room_exits,
        inventory=inventory,
        equipped=equipped,
        shop_items=shop_items,
        net_nodes=net_nodes,
        interactables=interactables,
        recipes=recipes,
        braindances=braindances,
        net_shell=net_shell,
    )
    return candidates[0] if candidates else None


def complete_input_cycle(
    value: str,
    cycle_index: int,
    *,
    room_items: tuple[str, ...],
    room_npcs: tuple[str, ...],
    room_corpses: tuple[str, ...] = (),
    room_exits: tuple[str, ...],
    inventory: tuple[str, ...],
    equipped: tuple[str, ...] = (),
    shop_items: tuple[str, ...] = (),
    net_nodes: tuple[str, ...] = (),
    interactables: tuple[str, ...] = (),
    recipes: tuple[str, ...] = (),
    braindances: tuple[str, ...] = (),
    net_shell: bool = False,
) -> tuple[str | None, int]:
    candidates = complete_input_candidates(
        value,
        room_items=room_items,
        room_npcs=room_npcs,
        room_corpses=room_corpses,
        room_exits=room_exits,
        inventory=inventory,
        equipped=equipped,
        shop_items=shop_items,
        net_nodes=net_nodes,
        interactables=interactables,
        recipes=recipes,
        braindances=braindances,
        net_shell=net_shell,
    )
    if not candidates:
        return None, 0
    idx = cycle_index % len(candidates)
    next_index = (cycle_index + 1) % len(candidates) if len(candidates) > 1 else 0
    return candidates[idx], next_index