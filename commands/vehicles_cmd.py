from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t


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

    lines = [t(locale, "vehicles.header"), ""]
    if ctx.player.vehicle_id:
        owned = ctx.state.world.vehicle(ctx.player.vehicle_id)
        if owned:
            lines.append(t(locale, "vehicles.owned", name=_vehicle_label(owned, locale)))
    else:
        lines.append(t(locale, "vehicles.none"))

    room = ctx.state.world.room(ctx.player.room_id)
    if room and "vehicle_dealer" in room.tags:
        lines.append("")
        lines.append(t(locale, "vehicles.dealer_header"))
        for vid, vehicle in ctx.state.world.vehicles.items():
            if vehicle.dealer_room != ctx.player.room_id:
                continue
            desc = vehicle.description_zh if locale == "zh" else (vehicle.description_en or vehicle.description_zh)
            lines.append(
                t(locale, "vehicles.dealer_line", name=_vehicle_label(vehicle, locale), cost=str(vehicle.cost), desc=desc or "")
            )
        lines.append("")
        lines.append(t(locale, "vehicles.buy_hint"))

    return ok(lines, meta=player_meta(ctx))


def _buy_vehicle(ctx: CommandContext, target: str):
    locale = ctx.player.locale
    room = ctx.state.world.room(ctx.player.room_id)
    if room is None or "vehicle_dealer" not in room.tags:
        return ok([t(locale, "vehicles.not_dealer")])

    if ctx.player.vehicle_id:
        return ok([t(locale, "vehicles.already_owned")])

    vid, vehicle = _resolve_vehicle_id(ctx, target)
    if vehicle is None or vehicle.dealer_room != ctx.player.room_id:
        return ok([t(locale, "vehicles.unknown", name=target)])

    if ctx.player.gold < vehicle.cost:
        return ok([t(locale, "vehicles.no_gold", cost=str(vehicle.cost))])

    ctx.player.gold -= vehicle.cost
    ctx.player.vehicle_id = vid
    return ok(
        [t(locale, "vehicles.buy_ok", name=_vehicle_label(vehicle, locale), cost=str(vehicle.cost))],
        meta=player_meta(ctx),
        world_changed=True,
    )


register("vehicles", handle)
register("vehicle", handle)