from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from world.mature import is_mature
from world.mature_social import mature_room, mature_say_broadcast_keys, mature_say_self_line


def handle(ctx: CommandContext):
    message = ctx.args.strip()
    if not message:
        return ok([t(ctx.player.locale, "say.usage")])

    lines: list[str] = []
    if ctx.player.posture == "sleeping":
        from world.life import wake_player

        if wake_player(ctx.player):
            lines.append(t(ctx.player.locale, "life.wake_on_say"))

    locale = ctx.player.locale
    room = ctx.state.world.room(ctx.player.room_id)
    if mature_room(room) and is_mature(ctx.player):
        self_line = mature_say_self_line(locale, room.id, message) or t(locale, "say.ok", message=message)
        lines.append(self_line)
        broadcast_key, broadcast_fallback = mature_say_broadcast_keys(room.id)
        return ok(
            lines,
            meta=player_meta(ctx),
            world_changed=bool(lines) and len(lines) > 1,
            broadcast_key="say.broadcast",
            broadcast_mature_key=broadcast_key,
            broadcast_mature_fallback_key=broadcast_fallback,
            broadcast_kwargs={"name": ctx.player.name, "message": message},
        )

    lines.append(t(locale, "say.ok", message=message))
    return ok(
        lines,
        meta=player_meta(ctx),
        world_changed=bool(lines) and len(lines) > 1,
        broadcast_key="say.broadcast",
        broadcast_kwargs={"name": ctx.player.name, "message": message},
    )


register("say", handle)