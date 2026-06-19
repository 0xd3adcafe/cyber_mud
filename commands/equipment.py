from __future__ import annotations

from commands.registry import CommandContext, ok_panel, player_meta, register
from shared.equipment import format_equipment_lines
from shared.i18n import t
from shared.ui_json import panel_json


def _equipment_ui(ctx: CommandContext) -> str:
    sections = []
    for slot in ("weapon", "armor", "head", "cyber"):
        item_id = ctx.player.equipment.get(slot, "")
        item = ctx.state.world.item(item_id) if item_id else None
        from shared.locale_content import item_label

        value = item_label(item, ctx.player.locale) if item else t(ctx.player.locale, "equipment.none")
        sections.append(
            {
                "kind": "row",
                "label": t(ctx.player.locale, f"equipment.slot.{slot}"),
                "value": value,
            }
        )
    return panel_json(
        panel="equipment",
        title=t(ctx.player.locale, "equipment.header"),
        sections=sections,
    )


def handle(ctx: CommandContext):
    return ok_panel(
        format_equipment_lines(ctx.player, ctx.state.world, ctx.player.locale),
        panel="equipment",
        ui_json=_equipment_ui(ctx),
        meta=player_meta(ctx),
    )


register("equipment", handle)