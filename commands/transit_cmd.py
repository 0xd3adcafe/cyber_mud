from __future__ import annotations

from commands.helpers import format_look
from commands.registry import CommandContext, ok, ok_document, player_meta, register
from shared.i18n import t
from shared.locale_content import room_name


def _route_label(route, locale: str) -> str:
    if locale == "en" and route.name_en:
        return route.name_en
    return route.name_zh or route.to_room


def _resolve_dest(ctx: CommandContext, needle: str) -> str | None:
    needle = needle.strip().lower()
    if not needle:
        return None
    for route in ctx.state.world.transit_from(ctx.player.room_id):
        dest = ctx.state.world.room(route.to_room)
        if route.to_room.lower() == needle:
            return route.to_room
        if dest:
            names = {route.to_room.lower(), dest.name_zh.lower(), dest.name_en.lower()}
            if needle in names:
                return route.to_room
    return None


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    if ctx.player.in_combat:
        return ok([t(locale, "combat.busy")])

    room = ctx.state.world.room(ctx.player.room_id)
    if room is None or "transit" not in room.tags and "metro" not in room.tags:
        return ok([t(locale, "transit.not_here")])

    dest_arg = ctx.args.strip()
    routes = ctx.state.world.transit_from(ctx.player.room_id)
    if not dest_arg:
        lines = [t(locale, "transit.header"), ""]
        for route in routes:
            if route.requires_home:
                home = ctx.state.world.home(route.requires_home)
                if home is None or ctx.player.home_room_id != home.room_id:
                    continue
            dest = ctx.state.world.room(route.to_room)
            dest_name = room_name(dest, locale) if dest else route.to_room
            lines.append(
                t(
                    locale,
                    "transit.line",
                    line=_route_label(route, locale),
                    dest=dest_name,
                    fare=str(route.fare),
                )
            )
        lines.append("")
        lines.append(t(locale, "transit.usage"))
        return ok(lines, meta=player_meta(ctx))

    dest_id = _resolve_dest(ctx, dest_arg)
    if dest_id is None:
        return ok([t(locale, "transit.unknown", dest=dest_arg)])

    route = next((r for r in routes if r.to_room == dest_id), None)
    if route is None:
        return ok([t(locale, "transit.unknown", dest=dest_arg)])

    if route.requires_home:
        home = ctx.state.world.home(route.requires_home)
        if home is None or ctx.player.home_room_id != home.room_id:
            return ok([t(locale, "transit.need_home")])

    if ctx.player.gold < route.fare:
        return ok([t(locale, "transit.no_gold", fare=str(route.fare))])

    ctx.player.gold -= route.fare
    ctx.player.room_id = dest_id
    dest = ctx.state.world.room(dest_id)
    dest_name = room_name(dest, locale) if dest else dest_id
    lines = [t(locale, "transit.ok", dest=dest_name, fare=str(route.fare)), ""]
    lines.extend(format_look(ctx))
    return ok_document(lines, meta=player_meta(ctx), moved=True, world_changed=True)


register("transit", handle)