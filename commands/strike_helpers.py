from __future__ import annotations

from combat.encounter import combat_meta
from combat.strike import resolve_player_strike
from commands.registry import CommandContext, ok, player_meta


def handle_strike(ctx: CommandContext, style: str):
    result = resolve_player_strike(ctx.state, ctx.player, style=style, target=ctx.args.strip())
    meta = player_meta(ctx)
    meta.update(combat_meta(ctx.state, ctx.player))
    return ok(
        result.lines,
        meta=meta,
        moved=result.moved,
        world_changed=result.world_changed,
        broadcast_key=result.broadcast_key,
        broadcast_mature_key=result.broadcast_mature_key,
        broadcast_kwargs=result.broadcast_kwargs,
        broadcast_room_id=result.broadcast_room_id,
    )