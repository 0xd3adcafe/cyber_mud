from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field

from entities.player import Player
from shared.i18n import t
from shared.locale_content import item_label
from world.state import WorldState
from world.world import World

ATTACK_CD = 2
NPC_ATTACK_CD = 2
QUICKHACK_RAM_COST = 2

COMBAT_ALLOWED_COMMANDS = frozenset(
    {"attack", "defend", "flee", "quickhack", "look", "pda", "help", "quit"}
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
    log: list[str] = field(default_factory=list)

    def append_log(self, locale: str, key: str, **kwargs: str) -> str:
        line = t(locale, key, **kwargs)
        self.log.append(line)
        if len(self.log) > 8:
            self.log.pop(0)
        return line

    def player_weapon_damage(self, player: Player, world: World) -> int:
        weapon_id = player.equipment.get("weapon", "")
        if not weapon_id:
            return 0
        item = world.item(weapon_id)
        if item is None:
            return 0
        return item.weapon_damage

    def calc_player_damage(self, player: Player, world: World) -> int:
        return player.body + self.player_weapon_damage(player, world)

    def calc_npc_damage(self, state: WorldState) -> int:
        npc = state.world.npc(self.npc_id)
        if npc is None:
            return 3
        return npc.attack

    def calc_quickhack_damage(self, player: Player) -> int:
        return player.intelligence * 2

    def apply_damage(self, raw_damage: int) -> int:
        if self.defending:
            self.defending = False
            return max(1, raw_damage // 2)
        return raw_damage

    def flee_chance(self, player: Player) -> float:
        return min(0.95, 0.50 + player.reflex * 0.05)

    def try_flee(self, player: Player) -> bool:
        return random.random() < self.flee_chance(player)


def new_encounter_id() -> str:
    return uuid.uuid4().hex[:10]


def encounter_for_player(state: WorldState, player: Player) -> Encounter | None:
    if not player.in_combat or not player.encounter_id:
        return None
    return state.encounters.get(player.encounter_id)


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


def combat_meta(state: WorldState, player: Player) -> dict[str, str]:
    encounter = encounter_for_player(state, player)
    if encounter is None:
        return {}
    label = npc_label(state, encounter.npc_id, player.locale)
    return {
        "combat": "1",
        "combat_log": " | ".join(encounter.log),
        "combat_cd": f"P:{encounter.player_cd} N:{encounter.npc_cd}",
        "combat_target": label,
        "combat_npc_hp": str(encounter.npc_hp),
    }