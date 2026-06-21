from __future__ import annotations

from commands.registry import CommandContext, ok_panel, player_meta, register
from shared.i18n import t
from shared.ui_json import panel_json
from world.ctos_mesh import format_mesh_map_lines


def _mesh_section_lines(ctx: CommandContext) -> list[str]:
    if not ctx.player.discovered_net_links:
        return [t(ctx.player.locale, "ctos.mesh.empty_panel")]
    mesh_lines = format_mesh_map_lines(ctx.player, ctx.state, ctx.player.locale)
    return mesh_lines[2:]


def _mesh_ui(ctx: CommandContext) -> str:
    return panel_json(
        panel="mesh",
        title=t(ctx.player.locale, "ctos.mesh.header"),
        sections=[{"kind": "text", "lines": _mesh_section_lines(ctx)}],
    )


def handle(ctx: CommandContext):
    # Sidebar renders from @ui JSON; skip duplicate @panel lines (client perf).
    return ok_panel(
        [],
        panel="mesh",
        ui_json=_mesh_ui(ctx),
        meta=player_meta(ctx),
    )


register("mesh", handle)