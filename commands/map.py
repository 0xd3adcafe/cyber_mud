from __future__ import annotations

from commands.registry import CommandContext, ok_panel, player_meta, register
from shared.i18n import t
from shared.locale_content import room_name
from shared.ui_json import panel_json


def _mark_visited(ctx: CommandContext, room_id: str) -> None:
    if room_id not in ctx.player.visited_rooms:
        ctx.player.visited_rooms.append(room_id)


def format_map(ctx: CommandContext) -> list[str]:
    _mark_visited(ctx, ctx.player.room_id)
    known = set(ctx.player.visited_rooms)
    known.add(ctx.player.room_id)

    rooms = [
        room
        for room in ctx.state.world.rooms.values()
        if room.id in known and (room.grid_x or room.grid_y)
    ]
    if not rooms:
        return [t(ctx.player.locale, "map.empty")]

    min_x = min(r.grid_x for r in rooms)
    max_x = max(r.grid_x for r in rooms)
    min_y = min(r.grid_y for r in rooms)
    max_y = max(r.grid_y for r in rooms)

    by_pos = {(r.grid_x, r.grid_y): r for r in rooms}
    lines = [t(ctx.player.locale, "map.header"), ""]
    for y in range(max_y, min_y - 1, -1):
        row_cells: list[str] = []
        for x in range(min_x, max_x + 1):
            room = by_pos.get((x, y))
            if room is None:
                row_cells.append("  ·  ")
            elif room.id == ctx.player.room_id:
                row_cells.append("[@]")
            else:
                row_cells.append(" ■ ")
        lines.append("".join(row_cells))
    lines.append("")
    lines.append(t(ctx.player.locale, "map.legend"))
    for room in sorted(rooms, key=lambda r: (r.grid_y, r.grid_x)):
        marker = "@" if room.id == ctx.player.room_id else "■"
        lines.append(
            t(
                ctx.player.locale,
                "map.room_line",
                marker=marker,
                name=room_name(room, ctx.player.locale),
            )
        )
    return lines


def _map_ui(ctx: CommandContext) -> str:
    return panel_json(
        panel="map",
        title=t(ctx.player.locale, "map.header"),
        sections=[{"kind": "text", "lines": format_map(ctx)[2:]}],
    )


def handle(ctx: CommandContext):
    # Sidebar renders from @ui JSON; skip duplicate @panel lines (client perf).
    return ok_panel(
        [],
        panel="map",
        ui_json=_map_ui(ctx),
        meta=player_meta(ctx),
    )


register("map", handle)