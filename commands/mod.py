from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.equipment import WEAPON_EQUIP_SLOTS, active_weapon_id
from shared.i18n import t
from shared.locale_content import item_label
from shared.target_resolve import resolve_item_id, split_mod_args


_MOD_WEAPON_SLOT_ALIASES: dict[str, str] = {
    "primary": "weapon_primary",
    "secondary": "weapon_secondary",
    "weapon_primary": "weapon_primary",
    "weapon_secondary": "weapon_secondary",
    "主武器": "weapon_primary",
    "副武器": "weapon_secondary",
}


def _weapon_id_from_slot_alias(player, weapon_name: str) -> str | None:
    key = weapon_name.strip()
    slot = _MOD_WEAPON_SLOT_ALIASES.get(key) or _MOD_WEAPON_SLOT_ALIASES.get(key.lower())
    if not slot or slot not in WEAPON_EQUIP_SLOTS:
        return None
    return player.equipment.get(slot, "") or None


def _mod_for_chip(world, chip_item_id: str):
    for mod_id, mod in world.mods.items():
        if mod.chip_item == chip_item_id:
            return mod_id, mod
    return None, None


def handle(ctx: CommandContext):
    chip_name, weapon_name = split_mod_args(ctx.args.strip())
    if not chip_name:
        return ok([t(ctx.player.locale, "mod.usage")])

    chip_result = resolve_item_id(ctx, chip_name, scopes=("inventory",), verb="mod")
    if chip_result.needs_response:
        return ok(chip_result.lines)
    if not chip_result.ok:
        return ok([t(ctx.player.locale, "mod.missing_chip")])
    chip_id = chip_result.value

    mod_id, mod = _mod_for_chip(ctx.state.world, chip_id)
    if mod is None:
        return ok([t(ctx.player.locale, "mod.unknown_chip")])

    if weapon_name:
        weapon_id = _weapon_id_from_slot_alias(ctx.player, weapon_name)
        if weapon_id is None and weapon_name.strip().lower() in _MOD_WEAPON_SLOT_ALIASES:
            return ok([t(ctx.player.locale, "mod.missing_weapon", name=weapon_name)])
        if weapon_id is None:
            weapon_result = resolve_item_id(
                ctx,
                weapon_name,
                scopes=("equipped",),
                verb="mod",
                collapse_same_id=False,
            )
            if weapon_result.needs_response:
                return ok(weapon_result.lines)
            if not weapon_result.ok:
                return ok([t(ctx.player.locale, "mod.missing_weapon", name=weapon_name)])
            weapon_id = weapon_result.value
    else:
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