from __future__ import annotations

from commands.helpers import format_look
from commands.registry import CommandContext, ok, ok_document, player_meta, register
from shared.i18n import t
from shared.locale_content import room_name


def _resolve_dest(ctx: CommandContext, needle: str) -> str | None:
    needle = needle.strip().lower()
    vehicle = ctx.state.world.vehicle(ctx.player.vehicle_id)
    if vehicle is None:
        return None
    if ctx.player.room_id not in vehicle.routes:
        return None
    for room_id in vehicle.routes:
        if room_id.lower() == needle:
            return room_id
        room = ctx.state.world.room(room_id)
        if room and needle in {room.name_zh.lower(), room.name_en.lower()}:
            return room_id
    return None


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    if ctx.player.in_combat:
        return ok([t(locale, "combat.busy")])

    if not ctx.player.vehicle_id:
        return ok([t(locale, "drive.no_vehicle")])

    vehicle = ctx.state.world.vehicle(ctx.player.vehicle_id)
    if vehicle is None:
        return ok([t(locale, "drive.no_vehicle")])

    if ctx.player.room_id not in vehicle.routes:
        return ok([t(locale, "drive.not_road")])

    dest_arg = ctx.args.strip()
    if not dest_arg:
        lines = [t(locale, "drive.header"), ""]
        for room_id in vehicle.routes:
            if room_id == ctx.player.room_id:
                continue
            room = ctx.state.world.room(room_id)
            label = room_name(room, locale) if room else room_id
            lines.append(f"  • {label}")
        lines.append("")
        lines.append(t(locale, "drive.usage"))
        return ok(lines, meta=player_meta(ctx))

    dest_id = _resolve_dest(ctx, dest_arg)
    if dest_id is None or dest_id == ctx.player.room_id:
        return ok([t(locale, "drive.unknown", dest=dest_arg)])

    ctx.player.room_id = dest_id
    dest = ctx.state.world.room(dest_id)
    dest_name = room_name(dest, locale) if dest else dest_id
    vlabel = vehicle.name_zh if locale == "zh" else (vehicle.name_en or vehicle.name_zh)
    lines = [t(locale, "drive.ok", vehicle=vlabel or vehicle.id, dest=dest_name), ""]
    lines.extend(format_look(ctx))
    return ok_document(lines, meta=player_meta(ctx), moved=True, world_changed=True)


register("drive", handle)