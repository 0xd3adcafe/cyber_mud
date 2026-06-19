from combat.encounter import combat_meta
from combat.strike import resolve_player_attack
from commands.registry import CommandContext, ok, player_meta, register


def handle(ctx: CommandContext):
    result = resolve_player_attack(ctx.state, ctx.player, target=ctx.args)
    meta = player_meta(ctx)
    meta.update(combat_meta(ctx.state, ctx.player))
    return ok(
        result.lines,
        meta=meta,
        moved=result.moved,
        world_changed=result.world_changed,
        broadcast_key=result.broadcast_key,
        broadcast_kwargs=result.broadcast_kwargs,
        broadcast_room_id=result.broadcast_room_id,
    )


register("attack", handle)