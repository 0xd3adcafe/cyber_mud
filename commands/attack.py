from combat.actions import resolve_player_attack
from combat.encounter import combat_meta
from commands.registry import CommandContext, ok, player_meta, register


def handle(ctx: CommandContext):
    result = resolve_player_attack(ctx.state, ctx.player, target=ctx.args.strip())
    meta = player_meta(ctx)
    meta.update(combat_meta(ctx.state, ctx.player))
    return ok(
        result.lines,
        meta=meta,
        world_changed=result.world_changed,
        broadcast_key=result.broadcast_key,
        broadcast_kwargs=result.broadcast_kwargs,
    )


register("attack", handle)