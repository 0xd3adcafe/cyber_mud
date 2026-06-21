from __future__ import annotations

from commands.registry import CommandContext
from shared.i18n import t
from shared.locks import lock_allows


def check_entity_lock(ctx: CommandContext, entity, action: str) -> list[str] | None:
    if entity is None or lock_allows(entity, action, ctx.player, ctx.state):
        return None
    locale = ctx.player.locale
    key = f"lock.denied_{action}"
    msg = t(locale, key)
    if msg == key:
        lines = [t(locale, "lock.denied")]
    else:
        lines = [msg]
    from world.footprint import add_footprint

    lines.extend(add_footprint(ctx.player, 4, ctx.state, locale, reason="lock"))
    return lines