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
        return [t(locale, "lock.denied")]
    return [msg]