from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Generic, TypeVar

from commands.registry import CommandContext
from shared.equipment import EQUIP_SLOTS, slot_label
from shared.i18n import t
from shared.locale_content import (
    item_label_with_id,
    net_node_label_with_id,
    npc_label_with_id,
)
from shared.names import matches_name
from world.corpses import _CORPSE_ALIASES, corpse_label, corpses_in_room, find_corpse_id
from world.state import WorldState

T = TypeVar("T")

_ITEM_FROM_RE = re.compile(r"^(.+?)\s+(?:from|從)\s+(.+)$", re.IGNORECASE)
_ITEM_IN_RE = re.compile(r"^(.+?)\s+in\s+(.+)$", re.IGNORECASE)
_ITEM_ON_GROUND_RE = re.compile(r"^(.+?)\s+on\s+(ground|floor|地上)$", re.IGNORECASE)
_INDEX_SUFFIX_RE = re.compile(r"^(.+?)[.#](\d+)$")
_INDEX_PREFIX_RE = re.compile(r"^(?:#)?(\d+)[.\s]+(.+)$")
_INDEX_SPACE_RE = re.compile(r"^(.+?)\s+(\d+)$")

ITEM_SCOPES = frozenset({"ground", "inventory", "equipped", "corpse", "stash"})

_ITEM_SCOPE_ALIASES: dict[str, str] = {
    "ground": "ground",
    "floor": "ground",
    "地上": "ground",
    "inventory": "inventory",
    "inv": "inventory",
    "身上": "inventory",
    "背包": "inventory",
    "equipped": "equipped",
    "equipment": "equipped",
    "gear": "equipped",
    "裝備": "equipped",
    "穿戴": "equipped",
    "stash": "stash",
    "儲物": "stash",
    "儲藏": "stash",
    "corpse": "corpse",
    "屍體": "corpse",
    "body": "corpse",
    "屍体": "corpse",
}


@dataclass(frozen=True)
class ParsedTarget:
    name: str
    index: int | None = None
    scope: str | None = None
    corpse_name: str | None = None


@dataclass(frozen=True)
class ItemRef:
    item_id: str
    scope: str
    slot: str = ""
    corpse_id: str = ""


@dataclass
class TargetResolveResult(Generic[T]):
    value: T | None = None
    lines: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.value is not None

    @property
    def needs_response(self) -> bool:
        return bool(self.lines)


def _resolve_item_scope(word: str) -> str | None:
    key = word.strip()
    if not key:
        return None
    return _ITEM_SCOPE_ALIASES.get(key) or _ITEM_SCOPE_ALIASES.get(key.lower())


def extract_target_index(name_part: str) -> tuple[str, int | None]:
    text = name_part.strip()
    if not text:
        return "", None
    match = _INDEX_SUFFIX_RE.match(text)
    if match:
        return match.group(1).strip(), int(match.group(2))
    match = _INDEX_PREFIX_RE.match(text)
    if match:
        return match.group(2).strip(), int(match.group(1))
    match = _INDEX_SPACE_RE.match(text)
    if match:
        return match.group(1).strip(), int(match.group(2))
    return text, None


def parse_simple_target(text: str) -> ParsedTarget:
    name, index = extract_target_index(text.strip())
    return ParsedTarget(name=name, index=index)


def parse_item_target(text: str) -> ParsedTarget:
    raw = text.strip()
    if not raw:
        return ParsedTarget(name="")

    corpse_name: str | None = None
    scope: str | None = None
    name_part = raw

    from_match = _ITEM_FROM_RE.match(raw)
    if from_match:
        name_part = from_match.group(1).strip()
        from_target = from_match.group(2).strip()
        scope = "corpse"
        if _resolve_item_scope(from_target) != "corpse":
            corpse_name = from_target
    else:
        in_match = _ITEM_IN_RE.match(raw)
        if in_match:
            name_part = in_match.group(1).strip()
            scope = _resolve_item_scope(in_match.group(2).strip())
        else:
            ground_match = _ITEM_ON_GROUND_RE.match(raw)
            if ground_match:
                name_part = ground_match.group(1).strip()
                scope = "ground"
            else:
                parts = raw.split(maxsplit=1)
                if len(parts) == 2:
                    maybe_scope = _resolve_item_scope(parts[0])
                    if maybe_scope:
                        scope = maybe_scope
                        name_part = parts[1].strip()

    name, index = extract_target_index(name_part)
    return ParsedTarget(name=name, index=index, scope=scope, corpse_name=corpse_name)


def split_give_args(args: str) -> tuple[str, str]:
    parts = args.split()
    if len(parts) < 2:
        return "", ""
    if len(parts) >= 3 and parts[1].isdigit():
        return f"{parts[0]} {parts[1]}", " ".join(parts[2:])
    return parts[0], " ".join(parts[1:])


def split_mod_args(args: str) -> tuple[str, str | None]:
    parts = args.split()
    if not parts:
        return "", None
    if len(parts) == 1:
        return parts[0], None
    if len(parts) == 2 and parts[1].isdigit():
        return f"{parts[0]} {parts[1]}", None
    if len(parts) >= 3 and parts[1].isdigit():
        return f"{parts[0]} {parts[1]}", " ".join(parts[2:])
    return parts[0], " ".join(parts[1:])


def _matching_item_refs_in_pool(
    state: WorldState,
    item_name: str,
    pool: list[str],
    *,
    scope: str,
    slot: str = "",
    corpse_id: str = "",
) -> list[ItemRef]:
    matches: list[ItemRef] = []
    for item_id in pool:
        item = state.world.item(item_id)
        if item and matches_name(item_name, item.id, item.name_zh, item.name_en):
            matches.append(ItemRef(item_id, scope, slot=slot, corpse_id=corpse_id))
    return matches


def collect_matching_item_refs(
    ctx: CommandContext,
    item_name: str,
    *,
    scopes: tuple[str, ...] | None = None,
    corpse_name: str | None = None,
) -> list[ItemRef]:
    if not item_name.strip():
        return []

    state = ctx.state
    player = ctx.player
    search_scopes = list(scopes) if scopes else ["ground", "inventory", "equipped", "corpse", "stash"]
    matches: list[ItemRef] = []

    for current_scope in search_scopes:
        if current_scope == "ground":
            matches.extend(
                _matching_item_refs_in_pool(
                    state,
                    item_name,
                    state.items_in_room(player.room_id),
                    scope="ground",
                )
            )
        elif current_scope == "inventory":
            matches.extend(
                _matching_item_refs_in_pool(state, item_name, player.inventory, scope="inventory")
            )
        elif current_scope == "equipped":
            for slot in EQUIP_SLOTS:
                item_id = player.equipment.get(slot, "")
                if not item_id:
                    continue
                item = state.world.item(item_id)
                if item and matches_name(item_name, item.id, item.name_zh, item.name_en):
                    matches.append(ItemRef(item_id, "equipped", slot=slot))
        elif current_scope == "corpse":
            if corpse_name:
                corpse_id = find_corpse_id(state, corpse_name, player.room_id)
                corpse = state.corpses.get(corpse_id) if corpse_id else None
                if corpse is not None:
                    matches.extend(
                        _matching_item_refs_in_pool(
                            state,
                            item_name,
                            corpse.loot,
                            scope="corpse",
                            corpse_id=corpse.id,
                        )
                    )
            else:
                for corpse in corpses_in_room(state, player.room_id):
                    matches.extend(
                        _matching_item_refs_in_pool(
                            state,
                            item_name,
                            corpse.loot,
                            scope="corpse",
                            corpse_id=corpse.id,
                        )
                    )
        elif current_scope == "stash":
            matches.extend(
                _matching_item_refs_in_pool(state, item_name, player.home_stash, scope="stash")
            )
    return matches


def _corpse_matches_name(state: WorldState, corpse, needle: str, locale: str) -> bool:
    if matches_name(needle, *_CORPSE_ALIASES):
        return True
    if corpse.player_name and matches_name(needle, corpse.player_name):
        return True
    npc = state.world.npc(corpse.npc_id)
    if npc and matches_name(needle, corpse.npc_id, npc.name_zh, npc.name_en):
        return True
    if matches_name(needle, corpse_label(state, corpse, locale)):
        return True
    alt = "en" if locale == "zh" else "zh"
    if matches_name(needle, corpse_label(state, corpse, alt)):
        return True
    return False


def collect_matching_corpse_ids(ctx: CommandContext, name: str) -> list[str]:
    needle = name.strip()
    if not needle:
        return []
    matches: list[str] = []
    locale = ctx.player.locale
    for corpse in corpses_in_room(ctx.state, ctx.player.room_id):
        if _corpse_matches_name(ctx.state, corpse, needle, locale):
            matches.append(corpse.id)
    return matches


def collect_matching_npc_ids(
    ctx: CommandContext,
    name: str,
    *,
    hostile_only: bool = False,
) -> list[str]:
    if not name.strip():
        return []
    matches: list[str] = []
    for npc_id in ctx.state.npcs_in_room(ctx.player.room_id):
        npc = ctx.state.world.npc(npc_id)
        if npc is None:
            continue
        if hostile_only and not npc.hostile:
            continue
        if matches_name(name, npc.id, npc.name_zh, npc.name_en):
            matches.append(npc_id)
    return matches


def collect_matching_net_node_ids(ctx: CommandContext, name: str) -> list[str]:
    if not name.strip():
        return []
    matches: list[str] = []
    for node in ctx.state.world.net_nodes_in_room(ctx.player.room_id):
        if matches_name(name, node.id, node.name_zh, node.name_en):
            matches.append(node.id)
    return matches


def collect_matching_interactable_ids(ctx: CommandContext, name: str) -> list[str]:
    if not name.strip():
        return []
    matches: list[str] = []
    for obj in ctx.state.world.interactables_in_room(ctx.player.room_id):
        if matches_name(name, obj.id, obj.name_zh, obj.name_en):
            matches.append(obj.id)
    return matches


def collect_matching_shop_item_ids(ctx: CommandContext, name: str, shop) -> list[str]:
    if not name.strip():
        return []
    matches: list[str] = []
    for item_id in shop.sells:
        item = ctx.state.world.item(item_id)
        if item and matches_name(name, item.id, item.name_zh, item.name_en):
            matches.append(item_id)
    return matches


def collect_matching_recipe_ids(ctx: CommandContext, name: str) -> list[str]:
    if not name.strip():
        return []
    matches: list[str] = []
    for rid, recipe in ctx.state.world.recipes.items():
        if matches_name(name, rid, recipe.name_zh, recipe.name_en):
            matches.append(rid)
    return matches


def collect_matching_braindance_ids(ctx: CommandContext, name: str) -> list[str]:
    if not name.strip():
        return []
    matches: list[str] = []
    for bid, bd in ctx.state.world.braindances.items():
        if matches_name(name, bid, bd.name_zh, bd.name_en):
            matches.append(bid)
    return matches


def item_location_line_for_ref(ctx: CommandContext, ref: ItemRef) -> str | None:
    locale = ctx.player.locale
    if ref.scope == "ground":
        return t(locale, "look.location.ground")
    if ref.scope == "inventory":
        return t(locale, "look.location.inventory")
    if ref.scope == "equipped":
        return t(locale, "look.location.equipped", slot=slot_label(ref.slot, locale))
    if ref.scope == "corpse":
        corpse = ctx.state.corpses.get(ref.corpse_id)
        if corpse is not None:
            return t(locale, "look.location.corpse", corpse=corpse_label(ctx.state, corpse, locale))
        return t(locale, "look.location.corpse", corpse=ref.corpse_id)
    if ref.scope == "stash":
        return t(locale, "look.location.stash")
    return None


def format_ambiguous(
    locale: str,
    name: str,
    entries: list[tuple[str, str]],
    *,
    verb: str = "look",
) -> list[str]:
    lines = [t(locale, "target.ambiguous.header", name=name), ""]
    for index, (label, location) in enumerate(entries, 1):
        lines.append(
            t(locale, "target.ambiguous.line", index=str(index), label=label, location=location)
        )
    lines.extend(["", t(locale, "target.ambiguous.hint", verb=verb, name=name)])
    return lines


def _pick_indexed(
    locale: str,
    name: str,
    matches: list[T],
    index: int | None,
    *,
    verb: str,
    label_for: Callable[[T], str],
    location_for: Callable[[T], str] | None = None,
) -> TargetResolveResult[T]:
    if not matches:
        return TargetResolveResult()
    if index is not None:
        if index < 1 or index > len(matches):
            return TargetResolveResult(
                lines=[
                    t(
                        locale,
                        "target.index_out_of_range",
                        index=str(index),
                        name=name,
                        count=str(len(matches)),
                    )
                ]
            )
        return TargetResolveResult(value=matches[index - 1])
    if len(matches) > 1:
        entries: list[tuple[str, str]] = []
        for match in matches:
            label = label_for(match)
            location = location_for(match) if location_for else ""
            entries.append((label, location))
        return TargetResolveResult(lines=format_ambiguous(locale, name, entries, verb=verb))
    return TargetResolveResult(value=matches[0])


def resolve_item(
    ctx: CommandContext,
    target: str,
    *,
    scopes: tuple[str, ...],
    corpse_name: str | None = None,
    verb: str = "look",
    collapse_same_id: bool = False,
) -> TargetResolveResult[ItemRef]:
    parsed = parse_item_target(target)
    if not parsed.name:
        return TargetResolveResult()

    if parsed.scope and parsed.scope not in scopes:
        return TargetResolveResult()

    effective_corpse = corpse_name or parsed.corpse_name
    effective_scope = parsed.scope
    if effective_corpse and "corpse" in scopes:
        effective_scope = "corpse"

    search_scopes = (effective_scope,) if effective_scope else scopes
    matches = collect_matching_item_refs(
        ctx,
        parsed.name,
        scopes=search_scopes,
        corpse_name=effective_corpse,
    )
    if collapse_same_id and matches and len({ref.item_id for ref in matches}) == 1:
        matches = [matches[0]]
    locale = ctx.player.locale
    return _pick_indexed(
        locale,
        parsed.name,
        matches,
        parsed.index,
        verb=verb,
        label_for=lambda ref: item_label_with_id(ctx.state.world.item(ref.item_id), locale)
        if ctx.state.world.item(ref.item_id)
        else ref.item_id,
        location_for=lambda ref: item_location_line_for_ref(ctx, ref) or "",
    )


def resolve_item_id(
    ctx: CommandContext,
    target: str,
    *,
    scopes: tuple[str, ...],
    corpse_name: str | None = None,
    verb: str = "look",
    collapse_same_id: bool = True,
) -> TargetResolveResult[str]:
    result = resolve_item(
        ctx,
        target,
        scopes=scopes,
        corpse_name=corpse_name,
        verb=verb,
        collapse_same_id=collapse_same_id,
    )
    if result.value is None:
        return TargetResolveResult(lines=result.lines)
    return TargetResolveResult(value=result.value.item_id)


def resolve_npc(
    ctx: CommandContext,
    target: str,
    *,
    hostile_only: bool = False,
    verb: str = "talk",
) -> TargetResolveResult[str]:
    parsed = parse_simple_target(target)
    if not parsed.name:
        return TargetResolveResult()
    matches = collect_matching_npc_ids(ctx, parsed.name, hostile_only=hostile_only)
    locale = ctx.player.locale
    return _pick_indexed(
        locale,
        parsed.name,
        matches,
        parsed.index,
        verb=verb,
        label_for=lambda npc_id: npc_label_with_id(ctx.state.world.npc(npc_id), locale),
    )


def resolve_corpse(ctx: CommandContext, target: str, *, verb: str = "look") -> TargetResolveResult[str]:
    parsed = parse_simple_target(target)
    if not parsed.name:
        return TargetResolveResult()
    matches = collect_matching_corpse_ids(ctx, parsed.name)
    locale = ctx.player.locale
    return _pick_indexed(
        locale,
        parsed.name,
        matches,
        parsed.index,
        verb=verb,
        label_for=lambda corpse_id: corpse_label(
            ctx.state, ctx.state.corpses[corpse_id], locale
        )
        if corpse_id in ctx.state.corpses
        else corpse_id,
    )


def resolve_net_node(ctx: CommandContext, target: str, *, verb: str = "hack") -> TargetResolveResult[str]:
    parsed = parse_simple_target(target)
    if not parsed.name:
        return TargetResolveResult()
    matches = collect_matching_net_node_ids(ctx, parsed.name)
    locale = ctx.player.locale
    return _pick_indexed(
        locale,
        parsed.name,
        matches,
        parsed.index,
        verb=verb,
        label_for=lambda node_id: net_node_label_with_id(
            ctx.state.world.net_node(node_id), locale
        ),
    )


def resolve_interactable(ctx: CommandContext, target: str, *, verb: str = "interact") -> TargetResolveResult[str]:
    parsed = parse_simple_target(target)
    if not parsed.name:
        return TargetResolveResult()
    matches = collect_matching_interactable_ids(ctx, parsed.name)
    locale = ctx.player.locale

    def _label(obj_id: str) -> str:
        from world.interactables import interactable_label

        obj = ctx.state.world.interactable(obj_id)
        return interactable_label(obj, locale) if obj else obj_id

    return _pick_indexed(
        locale,
        parsed.name,
        matches,
        parsed.index,
        verb=verb,
        label_for=_label,
    )


def resolve_shop_item(ctx: CommandContext, target: str, shop, *, verb: str = "buy") -> TargetResolveResult[str]:
    parsed = parse_simple_target(target)
    if not parsed.name:
        return TargetResolveResult()
    matches = collect_matching_shop_item_ids(ctx, parsed.name, shop)
    locale = ctx.player.locale
    return _pick_indexed(
        locale,
        parsed.name,
        matches,
        parsed.index,
        verb=verb,
        label_for=lambda item_id: item_label_with_id(ctx.state.world.item(item_id), locale)
        if ctx.state.world.item(item_id)
        else item_id,
    )


def resolve_recipe(ctx: CommandContext, target: str, *, verb: str = "craft") -> TargetResolveResult[str]:
    parsed = parse_simple_target(target)
    if not parsed.name:
        return TargetResolveResult()
    matches = collect_matching_recipe_ids(ctx, parsed.name)
    locale = ctx.player.locale
    return _pick_indexed(
        locale,
        parsed.name,
        matches,
        parsed.index,
        verb=verb,
        label_for=lambda rid: rid,
    )


def resolve_braindance(ctx: CommandContext, target: str, *, verb: str = "braindance") -> TargetResolveResult[str]:
    parsed = parse_simple_target(target)
    if not parsed.name:
        return TargetResolveResult()
    matches = collect_matching_braindance_ids(ctx, parsed.name)
    locale = ctx.player.locale
    return _pick_indexed(
        locale,
        parsed.name,
        matches,
        parsed.index,
        verb=verb,
        label_for=lambda bid: bid,
    )


def resolve_npc_in_room(
    state: WorldState,
    room_id: str,
    locale: str,
    target: str,
    *,
    hostile_only: bool = False,
    verb: str = "attack",
) -> TargetResolveResult[str]:
    class _RoomCtx:
        def __init__(self) -> None:
            self.state = state
            self.player = type("P", (), {"room_id": room_id, "locale": locale})()

    return resolve_npc(_RoomCtx(), target, hostile_only=hostile_only, verb=verb)