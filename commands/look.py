from commands.helpers import format_look, format_look_target
from commands.registry import CommandContext, ok_document, player_meta, register


def handle(ctx: CommandContext):
    if ctx.args.strip():
        lines = format_look_target(ctx, ctx.args)
    else:
        lines = format_look(ctx)
    return ok_document(lines, meta=player_meta(ctx))


register("look", handle)