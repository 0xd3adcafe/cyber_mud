from commands.registry import CommandContext, CommandResult, player_meta, register
from shared.i18n import t


def handle(ctx: CommandContext) -> CommandResult:
    return CommandResult(
        lines=[t(ctx.player.locale, "game.quit")],
        meta=player_meta(ctx),
        quit_game=True,
    )


register("quit", handle)