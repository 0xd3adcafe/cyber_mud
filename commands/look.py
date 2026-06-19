from commands.helpers import format_look
from commands.registry import CommandContext, ok_document, player_meta, register


def handle(ctx: CommandContext):
    return ok_document(format_look(ctx), meta=player_meta(ctx))


register("look", handle)