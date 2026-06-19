from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "drop.usage")])

    item_id = find_item_id(ctx.state, ctx.args, inventory=ctx.player.inventory)
    if item_id is None:
        return ok([t(ctx.player.locale, "drop.missing")])

    item = ctx.state.world.item(item_id)
    ctx.player.inventory.remove(item_id)
    ctx.state.room_items.setdefault(ctx.player.room_id, []).append(item_id)
    label = item_label(item, ctx.player.locale) if item else item_id
    return ok(
        [t(ctx.player.locale, "drop.ok", label=label)],
        meta=player_meta(ctx),
        world_changed=True,
    )


register("drop", handle)