from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t

_VALID = frozenset({"en", "zh"})


def handle(ctx: CommandContext):
    args = ctx.args.strip().lower()
    if not args:
        return ok([t(ctx.player.locale, "lang.current", code=ctx.player.locale)])
    if args not in _VALID:
        return ok([t(ctx.player.locale, "lang.invalid", code=args)])
    ctx.player.locale = args
    return ok(
        [t(args, "lang.ok", code=args)],
        meta={**player_meta(ctx), "locale": args},
        refresh_sidebar=True,
    )


register("lang", handle)