from __future__ import annotations

from commands.registry import register
from commands.strike_helpers import handle_strike
from combat.styles import STYLE_BACKSTAB


def handle(ctx):
    return handle_strike(ctx, STYLE_BACKSTAB)


register("backstab", handle)