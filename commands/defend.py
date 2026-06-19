from combat.actions import resolve_defend
from combat.encounter import combat_meta
from commands.registry import CommandContext, ok, player_meta, register


def handle(ctx: CommandContext):
    result = resolve_defend(ctx.state, ctx.player)
    meta = player_meta(ctx)
    meta.update(combat_meta(ctx.state, ctx.player))
    return ok(result.lines, meta=meta, world_changed=result.world_changed)


register("defend", handle)