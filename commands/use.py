from __future__ import annotations

from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label
from world.consumables import (
    apply_consumable,
    apply_status_cure,
    calc_consumable_gains,
    consumable_action_verb,
    format_consumable_effect,
    is_consumable,
)


def _handle_consumable(ctx: CommandContext, *, required_type: str | None = None):
    locale = ctx.player.locale
    if not ctx.args:
        usage_key = "eat.usage" if required_type == "food" else "drink.usage" if required_type == "drink" else "use.usage"
        return ok([t(locale, usage_key)])

    item_id = find_item_id(ctx.state, ctx.args, inventory=ctx.player.inventory)
    if item_id is None:
        return ok([t(locale, "use.missing")])

    item = ctx.state.world.item(item_id)
    if not is_consumable(item):
        return ok([t(locale, "use.not_consumable")])

    assert item is not None
    if required_type and item.consumable != required_type:
        wrong_key = f"use.wrong_type_{required_type}"
        msg = t(locale, wrong_key)
        if msg == wrong_key:
            return ok([t(locale, "use.wrong_type")])
        return ok([msg])

    hp_gain, ram_gain = calc_consumable_gains(ctx.player, item)
    has_cure = bool(item.cures_status and item.cures_status in ctx.player.player_status)
    if hp_gain <= 0 and ram_gain <= 0 and not has_cure:
        return ok([t(locale, "use.no_effect", label=item_label(item, locale))])

    ctx.player.inventory.remove(item_id)
    apply_consumable(ctx.player, item)
    cure_line = apply_status_cure(ctx.player, item, locale)
    verb = consumable_action_verb(item.consumable, locale)
    effect = format_consumable_effect(locale, hp_gain=hp_gain, ram_gain=ram_gain)
    lines = [
        t(
            locale,
            "use.ok",
            verb=verb,
            label=item_label(item, locale),
            effect=effect or t(locale, "consumable.cure_only"),
        )
    ]
    if cure_line:
        lines.append(cure_line)
    return ok(
        lines,
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


def handle_use(ctx: CommandContext):
    return _handle_consumable(ctx)


def handle_eat(ctx: CommandContext):
    return _handle_consumable(ctx, required_type="food")


def handle_drink(ctx: CommandContext):
    return _handle_consumable(ctx, required_type="drink")


register("use", handle_use)
register("eat", handle_eat)
register("drink", handle_drink)