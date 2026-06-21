from __future__ import annotations

from commands.auth_helpers import handle_resume
from commands.registry import CommandContext, register


def handle(ctx: CommandContext):
    return handle_resume(ctx)


register("resume", handle)