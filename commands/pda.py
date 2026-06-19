from __future__ import annotations

from commands.pda_helpers import build_pda_ui, format_pda
from commands.registry import CommandContext, ok_panel, player_meta, register


def handle(ctx: CommandContext):
    return ok_panel(
        format_pda(ctx),
        panel="pda",
        ui_json=build_pda_ui(ctx),
        meta=player_meta(ctx),
    )


register("pda", handle)
register("status", handle)