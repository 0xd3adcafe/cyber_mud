from __future__ import annotations

from commands.registry import CommandContext
from shared.i18n import t
from world.infrastructure import room_infra_tags
from world.modifiers import period_for_room, weather_for_room
from world.world import Room

CTOS_HACK_TYPES: dict[str, dict] = {
    "blackout": {
        "tags": frozenset({"power_grid"}),
        "ram": 2,
        "cred_cost": 0,
        "footprint": 8,
    },
    "jam_signals": {
        "tags": frozenset({"traffic", "surveillance"}),
        "ram": 1,
        "cred_cost": 1,
        "footprint": 5,
    },
    "overload": {
        "tags": frozenset({"steam", "power_grid"}),
        "ram": 2,
        "cred_cost": 2,
        "footprint": 12,
    },
}


def _room_has_tag(room: Room | None, required: frozenset[str]) -> bool:
    if room is None:
        return False
    present = set(room_infra_tags(room))
    return bool(present & required)


def infra_hack_ram_cost(base: int, state, room_id: str) -> int:
    cost = base
    period = period_for_room(state)
    if period in {"night", "dusk"}:
        cost += 1
    if weather_for_room(state, room_id) == "acid_rain":
        cost += 1
    room = state.world.room(room_id)
    if room and room.district == "corpo":
        cost += 1
    return cost


def try_infra_hack(ctx: CommandContext, hack_id: str) -> list[str] | None:
    spec = CTOS_HACK_TYPES.get(hack_id)
    if spec is None:
        return None

    locale = ctx.player.locale
    room = ctx.state.world.room(ctx.player.room_id)
    if not _room_has_tag(room, spec["tags"]):
        return [t(locale, "ctos.hack.no_infra", hack=hack_id)]

    cred_cost = int(spec["cred_cost"])
    if ctx.player.street_cred < cred_cost:
        return [t(locale, "ctos.hack.need_cred", cost=str(cred_cost))]

    ram_cost = infra_hack_ram_cost(int(spec["ram"]), ctx.state, ctx.player.room_id)
    if ctx.player.ram < ram_cost:
        return [t(locale, "ctos.hack.need_ram", cost=str(ram_cost))]

    ctx.player.ram -= ram_cost
    if cred_cost:
        ctx.player.street_cred -= cred_cost

    from world.ctos_events import begin_district_event_from_hack
    from world.footprint import add_footprint

    lines = [t(locale, f"ctos.hack.{hack_id}.ok", room=ctx.player.room_id)]
    if room and room.district:
        begin_district_event_from_hack(ctx.state, hack_id, room.district)
    lines.extend(add_footprint(ctx.player, int(spec["footprint"]), ctx.state, locale, reason="hack"))
    from world.life import gain_fatigue

    gain_fatigue(ctx.player, "netrun")
    from world.quests import advance_quest_on_infra_hack

    lines.extend(advance_quest_on_infra_hack(ctx.player, ctx.state, hack_id, locale))
    return lines