from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.life import (
    POSTURE_LYING,
    POSTURE_SITTING,
    POSTURE_SLEEPING,
    POSTURE_STANDING,
    life_blocked,
    set_posture,
    sleep_refusal,
    wake_player,
)


def _blocked(ctx: CommandContext):
    msg = life_blocked(ctx.player, ctx.player.locale)
    if msg:
        return ok([msg], meta=player_meta(ctx))
    return None


def _set(ctx: CommandContext, posture: str, *, key: str, anchor: str = ""):
    blocked = _blocked(ctx)
    if blocked:
        return blocked
    set_posture(ctx.player, posture, anchor=anchor)
    return ok([t(ctx.player.locale, key)], meta=player_meta(ctx), world_changed=True)


def handle_sit(ctx: CommandContext):
    if ctx.player.posture == POSTURE_SITTING:
        return ok([t(ctx.player.locale, "life.already", posture="sitting")], meta=player_meta(ctx))
    return _set(ctx, POSTURE_SITTING, key="life.sit_ok")


def handle_stand(ctx: CommandContext):
    if ctx.player.posture == POSTURE_STANDING:
        return ok([t(ctx.player.locale, "life.already_standing")], meta=player_meta(ctx))
    wake_player(ctx.player)
    return ok([t(ctx.player.locale, "life.stand_ok")], meta=player_meta(ctx), world_changed=True)


def handle_lie(ctx: CommandContext):
    if ctx.player.posture == POSTURE_LYING:
        return ok([t(ctx.player.locale, "life.already", posture="lying")], meta=player_meta(ctx))
    return _set(ctx, POSTURE_LYING, key="life.lie_ok")


def handle_rest(ctx: CommandContext):
    blocked = _blocked(ctx)
    if blocked:
        return blocked
    if ctx.player.posture == POSTURE_STANDING:
        set_posture(ctx.player, POSTURE_SITTING)
        key = "life.rest_sit"
    elif ctx.player.posture == POSTURE_SITTING:
        key = "life.rest_ok"
    else:
        key = "life.rest_deep"
    return ok([t(ctx.player.locale, key)], meta=player_meta(ctx), world_changed=True)


def handle_sleep(ctx: CommandContext):
    blocked = _blocked(ctx)
    if blocked:
        return blocked
    refusal = sleep_refusal(ctx.player, ctx.state, ctx.player.locale)
    if refusal:
        return ok([refusal], meta=player_meta(ctx))
    set_posture(ctx.player, POSTURE_SLEEPING)
    return ok([t(ctx.player.locale, "life.sleep_ok")], meta=player_meta(ctx), world_changed=True)


def handle_wake(ctx: CommandContext):
    if ctx.player.posture not in {POSTURE_LYING, POSTURE_SLEEPING, POSTURE_SITTING}:
        return ok([t(ctx.player.locale, "life.not_resting")], meta=player_meta(ctx))
    wake_player(ctx.player)
    return ok([t(ctx.player.locale, "life.wake_ok")], meta=player_meta(ctx), world_changed=True)


register("sit", handle_sit)
register("stand", handle_stand)
register("lie", handle_lie)
register("rest", handle_rest)
register("sleep", handle_sleep)
register("wake", handle_wake)