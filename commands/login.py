from commands.auth_helpers import handle_login
from commands.registry import CommandContext, register


def handle(ctx: CommandContext):
    return handle_login(ctx)


register("login", handle)