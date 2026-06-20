from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.interactables import find_interactable_id, interactable_label, perform_interact


def handle(ctx: CommandContext):
    target = ctx.args.strip()
    locale = ctx.player.locale
    if not target:
        objs = ctx.state.world.interactables_in_room(ctx.player.room_id)
        if not objs:
            return ok([t(locale, "interact.none")])
        lines = [t(locale, "interact.header"), ""]
        for obj in objs:
            lines.append(f"  • {interactable_label(obj, locale)}")
        lines.append("")
        lines.append(t(locale, "interact.usage"))
        return ok(lines, meta=player_meta(ctx))

    obj_id = find_interactable_id(ctx.state, ctx.player.room_id, target)
    if obj_id is None:
        return ok([t(locale, "interact.missing", name=target)])

    obj = ctx.state.world.interactable(obj_id)
    if obj is None:
        return ok([t(locale, "interact.missing", name=target)])

    lines = perform_interact(ctx.player, ctx.state, obj, locale)
    return ok(lines, meta=player_meta(ctx), world_changed=True)


register("interact", handle)