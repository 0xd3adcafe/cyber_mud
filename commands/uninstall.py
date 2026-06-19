from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.cyberware_slots import resolve_cyber_slot, slot_label
from shared.i18n import t
from commands.install import implant_label
from world.cyberware import uninstall_implant

UNINSTALL_COST = 50


def _at_ripperdoc(ctx: CommandContext) -> bool:
    room = ctx.state.world.room(ctx.player.room_id)
    return room is not None and "ripperdoc" in room.tags


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    if not _at_ripperdoc(ctx):
        return ok([t(locale, "uninstall.need_ripperdoc")])

    slot_arg = ctx.args.strip().lower()
    if not slot_arg:
        return ok([t(locale, "uninstall.usage")])

    slot = resolve_cyber_slot(slot_arg)
    if slot not in ctx.player.cyberware:
        return ok([t(locale, "uninstall.empty", slot=slot_label(slot, locale))])

    if ctx.player.gold < UNINSTALL_COST:
        return ok([t(locale, "uninstall.no_gold", cost=str(UNINSTALL_COST))])

    implant = uninstall_implant(ctx.player, ctx.state.world, slot)
    if implant is None:
        return ok([t(locale, "uninstall.empty", slot=slot_label(slot, locale))])

    ctx.player.gold -= UNINSTALL_COST
    label = implant_label(implant, locale)
    return ok(
        [t(locale, "uninstall.ok", label=label, slot=slot_label(slot, locale), cost=str(UNINSTALL_COST))],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("uninstall", handle)