from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "take.usage")])

    item_id = find_item_id(ctx.state, ctx.args, room_id=ctx.player.room_id)
    if item_id is None:
        return ok([t(ctx.player.locale, "take.missing")])

    item = ctx.state.world.item(item_id)
    if item is None or not item.takeable:
        return ok([t(ctx.player.locale, "take.not_takeable")])

    pool = ctx.state.room_items.setdefault(ctx.player.room_id, [])
    if item_id not in pool:
        return ok([t(ctx.player.locale, "take.missing")])

    pool.remove(item_id)
    ctx.player.inventory.append(item_id)
    label = item_label(item, ctx.player.locale)
    return ok(
        [t(ctx.player.locale, "take.ok", label=label)],
        meta=player_meta(ctx),
        world_changed=True,
    )


register("take", handle)