from __future__ import annotations

from entities.implant import Implant
from entities.player import Player
from shared.cyberware_slots import resolve_cyber_slot
from world.world import World


def implanted_ids(player: Player) -> list[str]:
    return list(player.cyberware.values())


def has_implant(player: Player, implant_id: str) -> bool:
    return implant_id in player.cyberware.values()


def implant_in_slot(player: Player, slot: str) -> str | None:
    resolved = resolve_cyber_slot(slot)
    return player.cyberware.get(resolved)


def apply_implant_stats(player: Player, implant: Implant) -> None:
    player.body += implant.body
    player.reflex += implant.reflex
    player.tech += implant.tech
    player.cool += implant.cool
    player.intelligence += implant.intelligence
    player.max_hp += implant.max_hp
    player.hp += implant.max_hp
    player.max_ram += implant.ram_bonus
    player.ram += implant.ram_bonus
    player.humanity = max(0, player.humanity - implant.humanity_cost)


def remove_implant_stats(player: Player, implant: Implant) -> None:
    player.body = max(0, player.body - implant.body)
    player.reflex = max(0, player.reflex - implant.reflex)
    player.tech = max(0, player.tech - implant.tech)
    player.cool = max(0, player.cool - implant.cool)
    player.intelligence = max(0, player.intelligence - implant.intelligence)
    player.max_hp = max(1, player.max_hp - implant.max_hp)
    player.hp = min(player.hp, player.max_hp)
    player.max_ram = max(0, player.max_ram - implant.ram_bonus)
    player.ram = min(player.ram, player.max_ram)


def can_install(player: Player, implant: Implant) -> str | None:
    slot = resolve_cyber_slot(implant.slot)
    if implant.id in player.cyberware.values():
        return "install.already"
    if slot in player.cyberware:
        return "install.slot_taken"
    return None


def install_implant(player: Player, implant: Implant) -> None:
    slot = resolve_cyber_slot(implant.slot)
    player.cyberware[slot] = implant.id
    apply_implant_stats(player, implant)


def uninstall_implant(player: Player, world: World, slot: str) -> Implant | None:
    resolved = resolve_cyber_slot(slot)
    implant_id = player.cyberware.pop(resolved, None)
    if not implant_id:
        return None
    implant = world.implant(implant_id)
    if implant is not None:
        remove_implant_stats(player, implant)
    return implant


def migrate_legacy_implants(player: Player, world: World) -> None:
    if player.cyberware:
        return
    for implant_id in list(player.implants):
        implant = world.implant(implant_id)
        if implant is None:
            continue
        slot = resolve_cyber_slot(implant.slot)
        if slot in player.cyberware:
            continue
        player.cyberware[slot] = implant_id
    player.implants = implanted_ids(player)