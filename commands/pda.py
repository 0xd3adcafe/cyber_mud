from commands.pda_helpers import format_pda
from commands.registry import CommandContext, ok_document, player_meta, register


def handle(ctx: CommandContext):
    return ok_document(format_pda(ctx), meta=player_meta(ctx))


register("pda", handle)
register("status", handle)