from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t


def handle(ctx: CommandContext):
    clock = ctx.state.clock
    config = ctx.state.time_config
    lines = [
        t(
            ctx.player.locale,
            "time.now",
            clock=clock.format_clock(ctx.player.locale),
            period=clock.format_period(ctx.player.locale, config),
        )
    ]
    return ok(lines, meta=player_meta(ctx))


register("time", handle)