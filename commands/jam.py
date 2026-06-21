from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.target_resolve import resolve_npc
from world.npc_ai import try_jam_npc


def handle(ctx: CommandContext):
    target = ctx.args.strip()
    if not target:
        return ok([t(ctx.player.locale, "ctos.distract.usage")])

    npc_result = resolve_npc(ctx, target, verb="jam")
    if npc_result.needs_response:
        return ok(npc_result.lines)
    if not npc_result.ok:
        return ok([t(ctx.player.locale, "ctos.distract.missing", name=target)])

    lines = try_jam_npc(ctx.player, ctx.state, npc_result.value, ctx.player.locale)
    return ok(lines, meta=player_meta(ctx), world_changed=True)


register("jam", handle)