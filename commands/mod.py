from __future__ import annotations

from commands.helpers import find_item_id
from commands.registry import CommandContext, ok, player_meta, register
from shared.equipment import active_weapon_id
from shared.i18n import t
from shared.locale_content import item_label


def _mod_for_chip(world, chip_item_id: str):
    for mod_id, mod in world.mods.items():
        if mod.chip_item == chip_item_id:
            return mod_id, mod
    return None, None


def handle(ctx: CommandContext):
    chip_name = ctx.args.strip()
    if not chip_name:
        return ok([t(ctx.player.locale, "mod.usage")])

    chip_id = find_item_id(ctx.state, chip_name, inventory=ctx.player.inventory)
    if chip_id is None:
        return ok([t(ctx.player.locale, "mod.missing_chip")])

    mod_id, mod = _mod_for_chip(ctx.state.world, chip_id)
    if mod is None:
        return ok([t(ctx.player.locale, "mod.unknown_chip")])

    weapon_id = active_weapon_id(ctx.player.equipment)
    if not weapon_id:
        return ok([t(ctx.player.locale, "mod.no_weapon")])

    installed = ctx.player.weapon_mods.setdefault(weapon_id, [])
    if mod_id in installed:
        label = mod.name_zh if ctx.player.locale == "zh" else (mod.name_en or mod.name_zh)
        return ok([t(ctx.player.locale, "mod.already", mod=label)])

    ctx.player.inventory.remove(chip_id)
    installed.append(mod_id)

    weapon = ctx.state.world.item(weapon_id)
    mod_label = mod.name_zh if ctx.player.locale == "zh" else (mod.name_en or mod.name_zh)
    weapon_label = item_label(weapon, ctx.player.locale)
    return ok(
        [t(ctx.player.locale, "mod.ok", mod=mod_label, weapon=weapon_label)],
        meta=player_meta(ctx),
        world_changed=True,
        refresh_sidebar=True,
    )


register("mod", handle)