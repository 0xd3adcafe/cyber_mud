from commands.registry import CommandContext, ok_document, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label


def format_inventory(ctx: CommandContext) -> list[str]:
    lines = [t(ctx.player.locale, "inventory.header"), ""]
    if not ctx.player.inventory:
        lines.append(t(ctx.player.locale, "inventory.empty"))
        return lines
    for item_id in ctx.player.inventory:
        item = ctx.state.world.item(item_id)
        lines.append(f"  • {item_label(item, ctx.player.locale)}")
    return lines


def handle(ctx: CommandContext):
    return ok_document(format_inventory(ctx), meta=player_meta(ctx))


register("inventory", handle)