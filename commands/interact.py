from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.target_resolve import resolve_interactable
from world.interactables import interactable_label, perform_interact


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

    obj_result = resolve_interactable(ctx, target, verb="interact")
    if obj_result.needs_response:
        return ok(obj_result.lines)
    if not obj_result.ok:
        return ok([t(locale, "interact.missing", name=target)])
    obj_id = obj_result.value

    obj = ctx.state.world.interactable(obj_id)
    if obj is None:
        return ok([t(locale, "interact.missing", name=target)])

    from commands.lock_helpers import check_entity_lock

    lock_denial = check_entity_lock(ctx, obj, "interact")
    if lock_denial is not None:
        return ok(lock_denial)

    lines = perform_interact(ctx.player, ctx.state, obj, locale)
    return ok(lines, meta=player_meta(ctx), world_changed=True)


register("interact", handle)