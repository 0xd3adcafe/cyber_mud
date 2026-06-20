from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field

from entities.player import Player
from shared.i18n import t
from shared.locale_content import item_label
from world.state import WorldState
from world.status_effects import StatusEffectState
from world.world import World

COMBAT_TICK_SECONDS = 3
ATTACK_CD = 1
NPC_ATTACK_CD = 2
QUICKHACK_RAM_COST = 2

COMBAT_ALLOWED_COMMANDS = frozenset(
    {
        "attack",
        "shoot",
        "slash",
        "bash",
        "punch",
        "backstab",
        "defend",
        "flee",
        "quickhack",
        "look",
        "use",
        "eat",
        "drink",
        "pda",
        "help",
        "quit",
    }
)


@dataclass
class Encounter:
    id: str
    player_name: str
    npc_id: str
    npc_hp: int
    player_cd: int = 0
    npc_cd: int = 0
    defending: bool = False
    npc_status: StatusEffectState = field(default_factory=StatusEffectState)
    log: list[str] = field(default_factory=list)

    def append_log(self, locale: str, key: str, **kwargs: str) -> str:
        line = t(locale, key, **kwargs)
        self.log.append(line)
        if len(self.log) > 8:
            self.log.pop(0)
        return line

    def player_weapon_damage(self, player: Player, world: World) -> int:
        from shared.equipment import active_weapon_id

        weapon_id = active_weapon_id(player.equipment)
        if not weapon_id:
            return 0
        item = world.item(weapon_id)
        if item is None:
            return 0
        damage = item.weapon_damage
        for mod_id in player.weapon_mods.get(weapon_id, []):
            mod = world.mod(mod_id)
            if mod:
                damage += mod.weapon_damage
        return damage

    def calc_player_damage(self, player: Player, world: World, *, state: WorldState | None = None) -> int:
        from combat.passives import bonus_attack_damage
        from world.cyberpsychosis import player_damage_multiplier
        from world.modifiers import apply_damage_modifier

        from world.wanted import wanted_damage_penalty

        raw = int(
            (player.body + self.player_weapon_damage(player, world) + bonus_attack_damage(player, state))
            * player_damage_multiplier(player)
            * wanted_damage_penalty(player)
        )
        if state is not None and player.room_id:
            return apply_damage_modifier(state, player.room_id, raw)
        return raw

    def calc_npc_damage(self, state: WorldState) -> int:
        from world.status_effects import npc_damage_multiplier

        npc = state.world.npc(self.npc_id)
        if npc is None:
            raw = 3
        else:
            raw = npc.attack
        return max(1, int(raw * npc_damage_multiplier(self.npc_status)))

    def calc_quickhack_damage(
        self,
        player: Player,
        *,
        state: WorldState | None = None,
        damage_mult: float = 1.0,
    ) -> int:
        from combat.passives import quickhack_damage_multiplier
        from world.cyberpsychosis import player_damage_multiplier
        from world.modifiers import apply_damage_modifier

        if damage_mult <= 0:
            return 0
        from world.wanted import wanted_damage_penalty

        raw = int(
            player.intelligence
            * 2
            * quickhack_damage_multiplier(player, state)
            * damage_mult
            * player_damage_multiplier(player)
            * wanted_damage_penalty(player)
        )
        if state is not None and player.room_id:
            return apply_damage_modifier(state, player.room_id, raw)
        return raw

    def apply_damage(self, raw_damage: int) -> int:
        if self.defending:
            self.defending = False
            return max(1, raw_damage // 2)
        return raw_damage

    def flee_chance(self, player: Player) -> float:
        return min(0.95, 0.50 + player.reflex * 0.05)

    def try_flee(self, player: Player, state: WorldState | None = None) -> bool:
        from world.modifiers import modified_flee_chance

        base = self.flee_chance(player)
        if state is not None and player.room_id:
            base = modified_flee_chance(base, state, player.room_id)
        return random.random() < base


def new_encounter_id() -> str:
    return uuid.uuid4().hex[:10]


def encounter_for_player(state: WorldState, player: Player) -> Encounter | None:
    if not player.in_combat or not player.encounter_id:
        return None
    return state.encounters.get(player.encounter_id)


def npc_in_player_room(state: WorldState, player: Player, encounter: Encounter) -> bool:
    return state.npc_room(encounter.npc_id) == player.room_id


def npc_label(state: WorldState, npc_id: str, locale: str) -> str:
    npc = state.world.npc(npc_id)
    if npc is None:
        return npc_id
    if locale == "en" and npc.name_en:
        return npc.name_en
    return npc.name_zh or npc.id


def find_hostile_npc_in_room(state: WorldState, room_id: str, target: str):
    from shared.names import matches_name

    for npc_id, npc in state.world.npcs.items():
        if not npc.hostile or state.npc_room(npc_id) != room_id:
            continue
        if matches_name(target, npc.id, npc.name_zh, npc.name_en):
            return npc
    return None


def start_encounter(state: WorldState, player: Player, npc_id: str) -> Encounter:
    npc = state.world.npc(npc_id)
    if npc is None:
        raise ValueError(npc_id)
    encounter = Encounter(
        id=new_encounter_id(),
        player_name=player.name,
        npc_id=npc_id,
        npc_hp=npc.hp,
        npc_cd=NPC_ATTACK_CD,
    )
    state.encounters[encounter.id] = encounter
    player.in_combat = True
    player.encounter_id = encounter.id
    return encounter


def end_encounter(state: WorldState, player: Player, encounter: Encounter) -> None:
    state.encounters.pop(encounter.id, None)
    player.in_combat = False
    player.encounter_id = ""
    encounter.log.clear()
    encounter.npc_status.clear()


def cd_ticks_to_seconds(_state: WorldState, ticks: int) -> int:
    return max(0, ticks) * COMBAT_TICK_SECONDS


def combat_meta(state: WorldState, player: Player) -> dict[str, str]:
    encounter = encounter_for_player(state, player)
    if encounter is None:
        return {}
    label = npc_label(state, encounter.npc_id, player.locale)
    player_secs = cd_ticks_to_seconds(state, encounter.player_cd)
    npc_secs = cd_ticks_to_seconds(state, encounter.npc_cd)
    return {
        "combat": "1",
        "combat_log": " | ".join(encounter.log),
        "combat_cd": f"P:{player_secs} N:{npc_secs}",
        "combat_target": label,
        "combat_npc_hp": str(encounter.npc_hp),
    }


def available_quickhacks(world: World, player: Player) -> list[str]:
    ids: list[str] = []
    for qid, qh in world.quickhacks.items():
        if qh.skill_req and qh.skill_req not in player.skills:
            continue
        ids.append(qid)
    return ids