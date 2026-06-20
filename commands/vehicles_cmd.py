from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.vehicles_player import active_vehicle_id, add_vehicle, owned_vehicle_ids


def _vehicle_label(vehicle, locale: str) -> str:
    if locale == "en" and vehicle.name_en:
        return vehicle.name_en
    return vehicle.name_zh or vehicle.id


def _resolve_vehicle_id(ctx: CommandContext, name: str):
    needle = name.strip().lower()
    for vid, vehicle in ctx.state.world.vehicles.items():
        labels = {vid.lower(), vehicle.name_zh.lower(), vehicle.name_en.lower()}
        if needle in labels or vid.lower().startswith(needle):
            return vid, vehicle
    return None, None


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    parts = ctx.args.strip().split(maxsplit=1)
    verb = parts[0].lower() if parts else ""
    target = parts[1].strip() if len(parts) > 1 else ""

    if verb == "buy" and target:
        return _buy_vehicle(ctx, target)
    if verb == "select" and target:
        return _select_vehicle(ctx, target)

    lines = [t(locale, "vehicles.header"), ""]
    owned = owned_vehicle_ids(ctx.player)
    if owned:
        active = active_vehicle_id(ctx.player)
        for vid in owned:
            vehicle = ctx.state.world.vehicle(vid)
            if vehicle is None:
                continue
            marker = t(locale, "vehicles.active") if vid == active else ""
            lines.append(
                t(locale, "vehicles.owned_line", name=_vehicle_label(vehicle, locale), marker=marker)
            )
    else:
        lines.append(t(locale, "vehicles.none"))

    room = ctx.state.world.room(ctx.player.room_id)
    if room and "vehicle_dealer" in room.tags:
        lines.append("")
        lines.append(t(locale, "vehicles.dealer_header"))
        for vid, vehicle in ctx.state.world.vehicles.items():
            if vehicle.dealer_room != ctx.player.room_id:
                continue
            owned_mark = t(locale, "vehicles.dealer_owned") if vid in owned else ""
            desc = vehicle.description_zh if locale == "zh" else (vehicle.description_en or vehicle.description_zh)
            lines.append(
                t(
                    locale,
                    "vehicles.dealer_line",
                    name=_vehicle_label(vehicle, locale),
                    cost=str(vehicle.cost),
                    desc=desc or "",
                    owned=owned_mark,
                )
            )
        lines.append("")
        lines.append(t(locale, "vehicles.buy_hint"))

    return ok(lines, meta=player_meta(ctx))


def _buy_vehicle(ctx: CommandContext, target: str):
    locale = ctx.player.locale
    room = ctx.state.world.room(ctx.player.room_id)
    if room is None or "vehicle_dealer" not in room.tags:
        return ok([t(locale, "vehicles.not_dealer")])

    vid, vehicle = _resolve_vehicle_id(ctx, target)
    if vehicle is None or vehicle.dealer_room != ctx.player.room_id:
        return ok([t(locale, "vehicles.unknown", name=target)])

    if vid in owned_vehicle_ids(ctx.player):
        return ok([t(locale, "vehicles.already_owned")])

    if ctx.player.gold < vehicle.cost:
        return ok([t(locale, "vehicles.no_gold", cost=str(vehicle.cost))])

    ctx.player.gold -= vehicle.cost
    add_vehicle(ctx.player, vid)
    return ok(
        [t(locale, "vehicles.buy_ok", name=_vehicle_label(vehicle, locale), cost=str(vehicle.cost))],
        meta=player_meta(ctx),
        world_changed=True,
    )


def _select_vehicle(ctx: CommandContext, target: str):
    locale = ctx.player.locale
    vid, vehicle = _resolve_vehicle_id(ctx, target)
    if vehicle is None:
        return ok([t(locale, "vehicles.unknown", name=target)])
    if vid not in owned_vehicle_ids(ctx.player):
        return ok([t(locale, "vehicles.not_owned", name=_vehicle_label(vehicle, locale))])
    ctx.player.active_vehicle = vid
    ctx.player.vehicle_id = vid
    return ok(
        [t(locale, "vehicles.select_ok", name=_vehicle_label(vehicle, locale))],
        meta=player_meta(ctx),
        world_changed=True,
    )


register("vehicles", handle)
register("vehicle", handle)