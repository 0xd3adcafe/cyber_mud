from __future__ import annotations

from commands.auth_helpers import find_online_player
from commands.helpers import find_item_id, find_npc_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label
from world.mature import is_mature
from world.mature_give import romance_gift_line


def _remove_item(ctx: CommandContext, item_id: str) -> None:
    for slot, equipped_id in list(ctx.player.equipment.items()):
        if equipped_id == item_id:
            del ctx.player.equipment[slot]
    if item_id in ctx.player.inventory:
        ctx.player.inventory.remove(item_id)


def handle(ctx: CommandContext):
    parts = ctx.args.split()
    if len(parts) < 2:
        return ok([t(ctx.player.locale, "give.usage")])

    item_name, target_name = parts[0], parts[1]
    item_id = find_item_id(ctx.state, item_name, inventory=ctx.player.inventory)
    if item_id is None:
        return ok([t(ctx.player.locale, "give.missing_item")])

    item = ctx.state.world.item(item_id)
    label = item_label(item, ctx.player.locale)

    target = find_online_player(ctx, target_name)
    if target is not None and target.room_id == ctx.player.room_id:
        _remove_item(ctx, item_id)
        target.inventory.append(item_id)
        return ok(
            [t(ctx.player.locale, "give.ok", label=label, name=target.name)],
            meta=player_meta(ctx),
            world_changed=True,
            broadcast_key="give.broadcast",
            broadcast_kwargs={"name": ctx.player.name, "target": target.name, "label": label},
        )

    npc_id = find_npc_id(ctx.state, target_name, ctx.player.room_id)
    if npc_id is None:
        return ok([t(ctx.player.locale, "give.missing_target", name=target_name)])

    npc = ctx.state.world.npc(npc_id)
    if npc is None:
        return ok([t(ctx.player.locale, "give.missing_target", name=target_name)])

    name = npc.name_zh if ctx.player.locale == "zh" else (npc.name_en or npc.name_zh)
    gift_line = romance_gift_line(ctx.player, npc_id, item_id, ctx.player.locale)
    if gift_line:
        _remove_item(ctx, item_id)
        broadcast_mature = "give.broadcast" if is_mature(ctx.player) else ""
        return ok(
            [t(ctx.player.locale, "give.npc_ok", label=label, name=name), gift_line],
            meta=player_meta(ctx),
            world_changed=True,
            broadcast_key="give.broadcast",
            broadcast_mature_key=broadcast_mature,
            broadcast_kwargs={"name": ctx.player.name, "target": name, "label": label},
        )

    from world.quests import advance_quest_on_give

    quest_lines = advance_quest_on_give(ctx.player, ctx.state, npc_id, item_id, ctx.player.locale)
    if not quest_lines:
        return ok([t(ctx.player.locale, "give.npc_refused", name=name)])

    _remove_item(ctx, item_id)
    return ok(
        [t(ctx.player.locale, "give.npc_ok", label=label, name=name), *quest_lines],
        meta=player_meta(ctx),
        world_changed=True,
        broadcast_key="give.broadcast",
        broadcast_kwargs={"name": ctx.player.name, "target": name, "label": label},
    )


register("give", handle)