from __future__ import annotations

from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.cyberware_slots import slot_label
from shared.i18n import t
from world.cyberware import can_install, install_implant


def implant_label(implant, locale: str) -> str:
    if implant is None:
        return "?"
    if locale == "en" and implant.name_en:
        return implant.name_en
    return implant.name_zh or implant.id


def _at_ripperdoc(ctx: CommandContext) -> bool:
    room = ctx.state.world.room(ctx.player.room_id)
    if room is None:
        return False
    return "ripperdoc" in room.tags


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

    if implant.ripperdoc_only and not _at_ripperdoc(ctx):
        return ok([t(ctx.player.locale, "install.need_ripperdoc")])

    error = can_install(ctx.player, implant)
    if error:
        if error == "install.slot_taken":
            slot_name = slot_label(implant.slot, ctx.player.locale)
            return ok([t(ctx.player.locale, error, slot=slot_name)])
        return ok([t(ctx.player.locale, error)])

    ctx.player.inventory.remove(item_id)
    install_implant(ctx.player, implant)
    label = implant_label(implant, ctx.player.locale)
    slot_name = slot_label(implant.slot, ctx.player.locale)
    return ok(
        [
            t(
                ctx.player.locale,
                "install.ok",
                label=label,
                slot=slot_name,
                humanity=str(ctx.player.humanity),
                body=str(ctx.player.body),
            )
        ],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("install", handle)