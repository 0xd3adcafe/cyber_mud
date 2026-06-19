from commands.helpers import current_room, format_look, player_meta
from commands.registry import CommandContext, ok, ok_document, register
from shared.i18n import t


def handle(ctx: CommandContext):
    direction = ctx.args.strip().lower()
    if not direction:
        return ok([t(ctx.player.locale, "game.no_exit")])

    room = current_room(ctx)
    if room is None or direction not in room.exits:
        return ok([t(ctx.player.locale, "game.no_exit")])

    ctx.player.room_id = room.exits[direction]
    lines = [t(ctx.player.locale, "go.ok", direction=direction), ""]
    lines.extend(format_look(ctx))
    return ok_document(lines, meta=player_meta(ctx), moved=True)


register("go", handle)