from __future__ import annotations

from shared.i18n import t
from shared.locale_content import item_label

# CP2077 服裝部位 + 武器槽（顯示順序）
WEAPON_EQUIP_SLOTS = ("weapon_primary", "weapon_secondary")
WEAPON_ITEM_SLOT = "weapon"

EQUIP_SLOTS = (
    *WEAPON_EQUIP_SLOTS,
    "head",
    "inner_torso",
    "outer_torso",
    "legs",
    "feet",
    "cyber",
)

SLOT_LEGACY_ALIASES: dict[str, str] = {
    "armor": "outer_torso",
    "weapon": "weapon_primary",
}

WEAPON_MODES = frozenset({"primary", "secondary", "two_handed", "dual_wield"})

# CP2077 武器種類（遠程）
RANGED_WEAPON_TYPES = frozenset(
    {
        "handgun",
        "revolver",
        "smg",
        "assault_rifle",
        "shotgun",
        "sniper_rifle",
        "precision_rifle",
        "heavy_machine_gun",
        "gun",
    }
)

BLADE_WEAPON_TYPES = frozenset({"blade", "katana", "mantis_blades"})
BLUNT_WEAPON_TYPES = frozenset({"blunt", "gorilla_arms"})

WEAPON_CLASSES = frozenset({"power", "tech", "smart", "melee"})

TWO_HANDED_WEAPON_TYPES = frozenset(
    {
        "assault_rifle",
        "shotgun",
        "sniper_rifle",
        "precision_rifle",
        "heavy_machine_gun",
        "katana",
    }
)
SECONDARY_WEAPON_TYPES = frozenset({"handgun", "revolver", "gun"})
PRIMARY_WEAPON_TYPES = frozenset({"smg"})

BODY_ARMOR_SLOTS = ("inner_torso", "outer_torso")


def resolve_slot_id(slot: str) -> str:
    return SLOT_LEGACY_ALIASES.get(slot, slot)


def is_weapon_item(item) -> bool:
    return item is not None and item.slot == WEAPON_ITEM_SLOT


def effective_weapon_mode(item) -> str:
    if item is None:
        return ""
    mode = getattr(item, "weapon_mode", "") or ""
    if mode in WEAPON_MODES:
        return mode
    wtype = item.weapon_type or ""
    if wtype in TWO_HANDED_WEAPON_TYPES:
        return "two_handed"
    if wtype in SECONDARY_WEAPON_TYPES:
        return "secondary"
    if wtype in PRIMARY_WEAPON_TYPES:
        return "primary"
    if wtype in BLADE_WEAPON_TYPES or wtype in BLUNT_WEAPON_TYPES:
        return "dual_wield"
    if wtype in RANGED_WEAPON_TYPES:
        return "primary"
    return "dual_wield"


def weapon_mode_label(mode: str, locale: str) -> str:
    if not mode:
        return ""
    key = f"weapon_mode.{mode}"
    label = t(locale, key)
    return label if label != key else mode


def primary_weapon_id(equipment: dict[str, str]) -> str:
    return equipment.get("weapon_primary", "") or ""


def secondary_weapon_id(equipment: dict[str, str]) -> str:
    return equipment.get("weapon_secondary", "") or ""


def has_two_handed_primary(player, world) -> bool:
    item_id = primary_weapon_id(player.equipment)
    if not item_id:
        return False
    item = world.item(item_id)
    return effective_weapon_mode(item) == "two_handed"


def resolve_weapon_equip_slot(item, player) -> str:
    mode = effective_weapon_mode(item)
    if mode in {"two_handed", "primary"}:
        return "weapon_primary"
    if mode == "secondary":
        return "weapon_secondary"
    if not secondary_weapon_id(player.equipment):
        return "weapon_secondary"
    if not primary_weapon_id(player.equipment):
        return "weapon_primary"
    return "weapon_secondary"


def wield_state(player, world) -> str:
    primary_id = primary_weapon_id(player.equipment)
    secondary_id = secondary_weapon_id(player.equipment)
    primary = world.item(primary_id) if primary_id else None
    secondary = world.item(secondary_id) if secondary_id else None

    if primary and secondary and effective_weapon_mode(primary) != "two_handed":
        return "dual_wield"
    if primary and effective_weapon_mode(primary) == "two_handed":
        return "two_handed"
    if primary:
        return "primary"
    if secondary:
        return "secondary"
    return "unarmed"


def wield_state_label(player, world, locale: str) -> str:
    return weapon_mode_label(wield_state(player, world), locale)


def active_weapon_id(equipment: dict[str, str]) -> str:
    return primary_weapon_id(equipment) or secondary_weapon_id(equipment)


def active_weapon(player, world):
    weapon_id = active_weapon_id(player.equipment)
    if not weapon_id:
        return None
    return world.item(weapon_id)


def weapon_equip_error_key(item, player, world, locale: str) -> str | None:
    if not is_weapon_item(item):
        return None
    mode = effective_weapon_mode(item)
    target = resolve_weapon_equip_slot(item, player)
    if mode in {"secondary", "dual_wield"} and target == "weapon_secondary" and has_two_handed_primary(player, world):
        return "equip.two_handed_blocks"
    return None


def apply_weapon_equip(player, item, target_slot: str) -> list[str]:
    """Return inventory items displaced by two-handed equip."""
    displaced: list[str] = []
    if not is_weapon_item(item):
        return displaced
    if effective_weapon_mode(item) == "two_handed" and target_slot == "weapon_primary":
        secondary_id = secondary_weapon_id(player.equipment)
        if secondary_id:
            displaced.append(secondary_id)
            del player.equipment["weapon_secondary"]
    return displaced


def normalize_equipment(equipment: dict[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for slot, item_id in equipment.items():
        if not item_id:
            continue
        resolved = resolve_slot_id(str(slot))
        if resolved in EQUIP_SLOTS:
            normalized[resolved] = str(item_id)
    return normalized


def is_equippable_slot(slot: str) -> bool:
    resolved = resolve_slot_id(slot)
    return resolved in EQUIP_SLOTS or resolved == WEAPON_ITEM_SLOT


def slot_label(slot: str, locale: str) -> str:
    resolved = resolve_slot_id(slot)
    label = t(locale, f"equipment.slot.{resolved}")
    return label if label != f"equipment.slot.{resolved}" else resolved


def weapon_type_label(weapon_type: str, locale: str) -> str:
    if not weapon_type:
        return ""
    key = f"weapon_type.{weapon_type}"
    label = t(locale, key)
    return label if label != key else weapon_type


def weapon_class_label(weapon_class: str, locale: str) -> str:
    if not weapon_class:
        return ""
    key = f"weapon_class.{weapon_class}"
    label = t(locale, key)
    return label if label != key else weapon_class


def is_ranged_weapon_type(weapon_type: str) -> bool:
    return weapon_type in RANGED_WEAPON_TYPES


def is_blade_weapon_type(weapon_type: str) -> bool:
    return weapon_type in BLADE_WEAPON_TYPES


def is_blunt_weapon_type(weapon_type: str) -> bool:
    return weapon_type in BLUNT_WEAPON_TYPES


def format_npc_equipment_lines(npc, world, locale: str) -> list[str]:
    lines: list[str] = []
    for slot in EQUIP_SLOTS:
        item_id = npc.equipment.get(slot, "")
        if not item_id:
            continue
        item = world.item(item_id)
        label = item_label(item, locale)
        lines.append(t(locale, "look.equipment.slot_line", slot=slot_label(slot, locale), item=label))
    return lines


def format_equipment_lines(player, world, locale: str) -> list[str]:
    lines = [t(locale, "equipment.header"), ""]
    for slot in EQUIP_SLOTS:
        item_id = player.equipment.get(slot, "")
        if item_id:
            item = world.item(item_id)
            label = item_label(item, locale)
            lines.append(t(locale, "equipment.slot_line", slot=slot_label(slot, locale), item=label))
        else:
            lines.append(t(locale, "equipment.empty_slot", slot=slot_label(slot, locale)))
    state = wield_state(player, world)
    if state != "unarmed":
        lines.append("")
        lines.append(t(locale, "equipment.wield_state", state=wield_state_label(player, world, locale)))
    return lines