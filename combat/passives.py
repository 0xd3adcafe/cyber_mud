from __future__ import annotations

from entities.player import Player
from world.cyberware import has_implant
from world.state import WorldState


def _active_chains(player: Player, state: WorldState):
    for chain in state.world.passive_chains.values():
        if chain.requires_implants and not all(has_implant(player, iid) for iid in chain.requires_implants):
            continue
        if chain.requires_skills and not all(skill in player.skills for skill in chain.requires_skills):
            continue
        if chain.requires_perks and not all(perk in player.perks for perk in chain.requires_perks):
            continue
        if player.street_cred < chain.min_street_cred:
            continue
        yield chain


def bonus_attack_damage(player: Player, state: WorldState | None = None) -> int:
    bonus = 0
    if has_implant(player, "cyber_arm_v1"):
        bonus += 1
    if has_implant(player, "mantis_blades"):
        bonus += 2
    if "blade_flow" in player.skills:
        bonus += 1
    if state is not None:
        for chain in _active_chains(player, state):
            bonus += chain.bonus_attack
    return bonus


def quickhack_damage_multiplier(player: Player, state: WorldState | None = None) -> float:
    mult = 1.0
    if "breach_protocol" in player.skills:
        mult *= 1.10
    if state is not None:
        for chain in _active_chains(player, state):
            if chain.quickhack_mult > 1.0:
                mult *= chain.quickhack_mult
    return mult


def xp_bonus_percent(player: Player, state: WorldState) -> int:
    total = 0
    for chain in _active_chains(player, state):
        total += chain.bonus_xp_percent
    return total