from __future__ import annotations

from commands.pda_helpers import build_pda_ui, format_pda
from commands.registry import CommandContext, ok_panel, player_meta, register
from commands.stats import format_stats_lines
from commands.talents_cmd import format_talents_catalog_lines
from shared.i18n import t

_PDA_VIEWS: dict[str, object] = {
    "stats": format_stats_lines,
    "stat": format_stats_lines,
    "talents": format_talents_catalog_lines,
    "talent": format_talents_catalog_lines,
    "perks": format_talents_catalog_lines,
    "perk": format_talents_catalog_lines,
}


def handle(ctx: CommandContext):
    view = ctx.args.strip().lower()
    if view in _PDA_VIEWS:
        formatter = _PDA_VIEWS[view]
        return ok_panel(
            formatter(ctx),
            panel="pda",
            meta=player_meta(ctx),
        )
    if view:
        return ok_panel(
            [t(ctx.player.locale, "pda.usage")],
            panel="pda",
            meta=player_meta(ctx),
        )
    return ok_panel(
        format_pda(ctx),
        panel="pda",
        ui_json=build_pda_ui(ctx),
        meta=player_meta(ctx),
    )


register("pda", handle)
register("status", handle)