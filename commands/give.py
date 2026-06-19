from __future__ import annotations

from commands.auth_helpers import find_online_player
from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label


def handle(ctx: CommandContext):
    parts = ctx.args.split()
    if len(parts) < 2:
        return ok([t(ctx.player.locale, "give.usage")])

    item_name, target_name = parts[0], parts[1]
    item_id = find_item_id(ctx.state, item_name, inventory=ctx.player.inventory)
    if item_id is None:
        return ok([t(ctx.player.locale, "give.missing_item")])

    target = find_online_player(ctx, target_name)
    if target is None or target.room_id != ctx.player.room_id:
        return ok([t(ctx.player.locale, "give.missing_player", name=target_name)])

    for slot, equipped_id in list(ctx.player.equipment.items()):
        if equipped_id == item_id:
            del ctx.player.equipment[slot]

    ctx.player.inventory.remove(item_id)
    target.inventory.append(item_id)
    item = ctx.state.world.item(item_id)
    label = item_label(item, ctx.player.locale)
    return ok(
        [t(ctx.player.locale, "give.ok", label=label, name=target.name)],
        meta=player_meta(ctx),
        world_changed=True,
        broadcast_key="give.broadcast",
        broadcast_kwargs={"name": ctx.player.name, "target": target.name, "label": label},
    )


register("give", handle)