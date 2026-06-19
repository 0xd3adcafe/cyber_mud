from __future__ import annotations

from commands.registry import CommandContext

COMMAND_VERBS: tuple[str, ...] = (
    "appraise",
    "attack",
    "defend",
    "drop",
    "equip",
    "equipment",
    "flee",
    "give",
    "go",
    "help",
    "install",
    "inventory",
    "learn",
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
    "search",
    "status",
    "take",
    "talk",
    "time",
    "unequip",
)

LOCAL_COMMAND_VERBS: tuple[str, ...] = ("prompt", "quit", "reconnect", "theme")

ITEM_TARGET_COMMANDS = frozenset(
    {"take", "drop", "equip", "unequip", "give", "appraise", "install", "mod"}
)
NPC_TARGET_COMMANDS = frozenset({"talk", "attack", "give"})
DIRECTION_COMMANDS = frozenset({"go"})


def room_item_ids(ctx: CommandContext) -> list[str]:
    return list(ctx.state.items_in_room(ctx.player.room_id))


def room_npc_ids(ctx: CommandContext) -> list[str]:
    return list(ctx.state.npcs_in_room(ctx.player.room_id))


def inventory_item_ids(ctx: CommandContext) -> list[str]:
    return list(ctx.player.inventory)


def room_exit_names(ctx: CommandContext) -> list[str]:
    room = ctx.state.world.room(ctx.player.room_id)
    if room is None:
        return []
    return sorted(room.exits.keys())


def completion_meta(ctx: CommandContext) -> dict[str, str]:
    return {
        "complete_room_items": ",".join(room_item_ids(ctx)),
        "complete_inventory": ",".join(inventory_item_ids(ctx)),
        "complete_npcs": ",".join(room_npc_ids(ctx)),
        "complete_exits": ",".join(room_exit_names(ctx)),
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
    room_exits: tuple[str, ...],
    inventory: tuple[str, ...],
) -> tuple[str, ...]:
    if verb in DIRECTION_COMMANDS:
        return room_exits
    if verb in NPC_TARGET_COMMANDS:
        return room_npcs
    if verb in ITEM_TARGET_COMMANDS:
        if verb in {"drop", "equip", "unequip", "give", "appraise", "install", "mod"}:
            return inventory or room_items
        return room_items
    return ()


def complete_input(
    value: str,
    *,
    room_items: tuple[str, ...],
    room_npcs: tuple[str, ...],
    room_exits: tuple[str, ...],
    inventory: tuple[str, ...],
    net_shell: bool = False,
) -> str | None:
    text = value.strip()
    if not text:
        return None

    if text.startswith("/"):
        partial = text[1:].split()[0].lower() if len(text) > 1 else ""
        for verb in LOCAL_COMMAND_VERBS:
            if verb.startswith(partial):
                return f"/{verb}"
        return None

    parts = text.split()
    if len(parts) == 1:
        partial = parts[0].lower()
        verbs = ("exit", "help", "quit") if net_shell else COMMAND_VERBS
        for verb in verbs:
            if verb.startswith(partial):
                return verb
        return None

    verb = parts[0].lower()
    partial = parts[-1].lower()
    prefix = " ".join(parts[:-1])
    pool = target_pool_for_verb(
        verb,
        room_items=room_items,
        room_npcs=room_npcs,
        room_exits=room_exits,
        inventory=inventory,
    )
    return _suggest_with_pool(prefix, partial, pool)


def _suggest_with_pool(prefix: str, partial: str, pool: tuple[str, ...]) -> str | None:
    for candidate in pool:
        if candidate.lower().startswith(partial):
            return f"{prefix} {candidate}"
    return None