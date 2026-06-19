from __future__ import annotations

from commands.registry import register
from commands.strike_helpers import handle_strike
from combat.styles import STYLE_SLASH


def handle(ctx):
    return handle_strike(ctx, STYLE_SLASH)


register("slash", handle)