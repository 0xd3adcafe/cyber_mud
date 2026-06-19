from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t


def handle(ctx: CommandContext):
    message = ctx.args.strip()
    if not message:
        return ok([t(ctx.player.locale, "say.usage")])

    return ok(
        [t(ctx.player.locale, "say.ok", message=message)],
        meta=player_meta(ctx),
        broadcast_key="say.broadcast",
        broadcast_kwargs={"name": ctx.player.name, "message": message},
    )


register("say", handle)