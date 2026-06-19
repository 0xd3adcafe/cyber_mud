from __future__ import annotations

from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.i18n import t
from shared.locale_content import item_label


def apply_implant(player, implant) -> None:
    player.body += implant.body
    player.reflex += implant.reflex
    player.tech += implant.tech
    player.cool += implant.cool
    player.intelligence += implant.intelligence
    player.humanity = max(0, player.humanity - implant.humanity_cost)


def implant_label(implant, locale: str) -> str:
    if implant is None:
        return "?"
    if locale == "en" and implant.name_en:
        return implant.name_en
    return implant.name_zh or implant.id


def handle(ctx: CommandContext):
    if not ctx.args:
        return ok([t(ctx.player.locale, "install.usage")])

    item_id = find_item_id(ctx.state, ctx.args, inventory=ctx.player.inventory)
    if item_id is None:
        return ok([t(ctx.player.locale, "install.missing")])

    item = ctx.state.world.item(item_id)
    if item is None or not item.implant_id:
        return ok([t(ctx.player.locale, "install.not_implant")])

    implant = ctx.state.world.implant(item.implant_id)
    if implant is None:
        return ok([t(ctx.player.locale, "install.unknown_implant")])

    if item.implant_id in ctx.player.implants:
        return ok([t(ctx.player.locale, "install.already")])

    ctx.player.inventory.remove(item_id)
    ctx.player.implants.append(item.implant_id)
    apply_implant(ctx.player, implant)
    label = implant_label(implant, ctx.player.locale)
    return ok(
        [
            t(
                ctx.player.locale,
                "install.ok",
                label=label,
                humanity=str(ctx.player.humanity),
                body=str(ctx.player.body),
            )
        ],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("install", handle)