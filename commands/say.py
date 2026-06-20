from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t


def handle(ctx: CommandContext):
    message = ctx.args.strip()
    if not message:
        return ok([t(ctx.player.locale, "say.usage")])

    lines: list[str] = []
    if ctx.player.posture == "sleeping":
        from world.life import wake_player

        if wake_player(ctx.player):
            lines.append(t(ctx.player.locale, "life.wake_on_say"))

    lines.append(t(ctx.player.locale, "say.ok", message=message))
    return ok(
        lines,
        meta=player_meta(ctx),
        world_changed=bool(lines) and len(lines) > 1,
        broadcast_key="say.broadcast",
        broadcast_kwargs={"name": ctx.player.name, "message": message},
    )


register("say", handle)