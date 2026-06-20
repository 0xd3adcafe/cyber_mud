from __future__ import annotations

from commands.bulk_helpers import is_bulk, resolve_take_targets
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label
from shared.target_resolve import resolve_corpse, resolve_item_id
from world.corpses import corpse_label, split_take_from


def _take_from_corpse(ctx: CommandContext, item_args: str, corpse_name: str):
    locale = ctx.player.locale
    corpse_resolved = resolve_corpse(ctx, corpse_name, verb="take")
    if corpse_resolved.needs_response:
        return ok(corpse_resolved.lines)
    if not corpse_resolved.ok:
        return ok([t(locale, "corpse.corpse_missing")])

    corpse_id = corpse_resolved.value
    corpse = ctx.state.corpses.get(corpse_id)
    if corpse is None:
        return ok([t(locale, "corpse.corpse_missing")])

    corpse_name_label = corpse_label(ctx.state, corpse, locale)

    if is_bulk(item_args):
        targets = []
        for item_id in list(corpse.loot):
            item = ctx.state.world.item(item_id)
            if item and item.takeable:
                targets.append(item_id)
    else:
        item_resolved = resolve_item_id(
            ctx,
            item_args,
            scopes=("corpse",),
            corpse_name=corpse_name,
            verb="take",
        )
        if item_resolved.needs_response:
            return ok(item_resolved.lines)
        targets = [item_resolved.value] if item_resolved.ok else []

    if not targets:
        return ok([t(locale, "corpse.take_missing")])

    lines: list[str] = []
    taken = 0
    for item_id in targets:
        if item_id not in corpse.loot:
            continue
        item = ctx.state.world.item(item_id)
        if item is None or not item.takeable:
            continue
        corpse.loot.remove(item_id)
        ctx.player.inventory.append(item_id)
        lines.append(
            t(
                locale,
                "corpse.take_ok",
                label=item_label(item, locale),
                corpse=corpse_name_label,
            )
        )
        taken += 1

    if not lines:
        return ok([t(locale, "corpse.take_missing")])

    if is_bulk(item_args) and taken > 1:
        lines.insert(0, t(locale, "take.bulk_ok", count=str(taken)))

    from world.quests import advance_quest_on_inventory

    lines.extend(advance_quest_on_inventory(ctx.player, ctx.state, locale))
    return ok(lines, meta=player_meta(ctx), world_changed=True)


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "take.usage")])

    item_args, corpse_name = split_take_from(ctx.args)
    if corpse_name:
        return _take_from_corpse(ctx, item_args, corpse_name)

    resolved = resolve_take_targets(ctx, item_args)
    if resolved.needs_response:
        return ok(resolved.lines)
    targets = resolved.value or []
    if not targets:
        return ok([t(ctx.player.locale, "take.missing")])

    pool = ctx.state.room_items.setdefault(ctx.player.room_id, [])
    lines: list[str] = []
    taken = 0
    for item_id in targets:
        item = ctx.state.world.item(item_id)
        if item is None or not item.takeable or item_id not in pool:
            continue
        pool.remove(item_id)
        ctx.player.inventory.append(item_id)
        lines.append(t(ctx.player.locale, "take.ok", label=item_label(item, ctx.player.locale)))
        taken += 1

    if not lines:
        return ok([t(ctx.player.locale, "take.missing")])

    if is_bulk(item_args) and taken > 1:
        lines.insert(0, t(ctx.player.locale, "take.bulk_ok", count=str(taken)))

    from world.quests import advance_quest_on_inventory

    lines.extend(advance_quest_on_inventory(ctx.player, ctx.state, ctx.player.locale))
    return ok(
        lines,
        meta=player_meta(ctx),
        world_changed=True,
    )


register("take", handle)