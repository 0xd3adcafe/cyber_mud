from commands.auth_helpers import handle_register
from commands.registry import CommandContext, register


def handle(ctx: CommandContext):
    return handle_register(ctx)


register("register", handle)