from __future__ import annotations

from dataclasses import dataclass

from combat.encounter import (
    ATTACK_CD,
    NPC_ATTACK_CD,
    QUICKHACK_RAM_COST,
    Encounter,
    end_encounter,
    encounter_for_player,
    find_hostile_npc_in_room,
    npc_in_player_room,
    npc_label,
    start_encounter,
)
from entities.player import Player
from shared.i18n import t
from world.state import WorldState


@dataclass
class CombatActionResult:
    lines: list[str]
    world_changed: bool = False
    ended: bool = False
    broadcast_key: str = ""
    broadcast_kwargs: dict[str, str] | None = None


def _player_by_name(state: WorldState, players: list[Player], name: str) -> Player | None:
    for player in players:
        if player.name == name:
            return player
    return None


def resolve_npc_departed(state: WorldState, player: Player, encounter: Encounter) -> CombatActionResult:
    locale = player.locale
    label = npc_label(state, encounter.npc_id, locale)
    line = t(locale, "combat.target_left", target=label)
    end_encounter(state, player, encounter)
    return CombatActionResult(
        [line],
        world_changed=True,
        ended=True,
    )


def resolve_player_attack(state: WorldState, player: Player, *, target: str = "") -> CombatActionResult:
    locale = player.locale
    encounter = encounter_for_player(state, player)

    if encounter is None:
        if not target:
            from shared.i18n import t

            return CombatActionResult([t(locale, "combat.attack_usage")])
        npc = find_hostile_npc_in_room(state, player.room_id, target)
        if npc is None:
            from shared.i18n import t

            return CombatActionResult([t(locale, "combat.no_target")])
        encounter = start_encounter(state, player, npc.id)
        label = npc_label(state, npc.id, locale)
        line = encounter.append_log(locale, "combat.start", target=label)
        lines = [line]
    else:
        if not npc_in_player_room(state, player, encounter):
            return resolve_npc_departed(state, player, encounter)

        if target:
            from shared.i18n import t
            from shared.names import matches_name

            npc = state.world.npc(encounter.npc_id)
            current = npc_label(state, encounter.npc_id, locale)
            if npc is None or not matches_name(target, encounter.npc_id, npc.name_zh, npc.name_en):
                return CombatActionResult([t(locale, "combat.already_fighting", target=current)])

        if encounter.player_cd > 0:
            from combat.encounter import cd_ticks_to_seconds
            from shared.i18n import t

            secs = cd_ticks_to_seconds(state, encounter.player_cd)
            return CombatActionResult(
                [t(locale, "combat.player_cd", cd=str(secs))],
                world_changed=True,
            )

        lines = []

    damage = encounter.calc_player_damage(player, state.world, state=state)
    encounter.npc_hp -= damage
    encounter.player_cd = ATTACK_CD
    label = npc_label(state, encounter.npc_id, locale)
    lines.append(
        encounter.append_log(
            locale,
            "combat.player_hit",
            target=label,
            damage=str(damage),
            hp=str(max(0, encounter.npc_hp)),
        )
    )

    if encounter.npc_hp <= 0:
        return _finish_victory(state, player, encounter, lines)

    return CombatActionResult(lines, world_changed=True)


def resolve_defend(state: WorldState, player: Player) -> CombatActionResult:
    locale = player.locale
    encounter = encounter_for_player(state, player)
    if encounter is None:
        from shared.i18n import t

        return CombatActionResult([t(locale, "combat.not_in_combat")])

    if not npc_in_player_room(state, player, encounter):
        return resolve_npc_departed(state, player, encounter)

    encounter.defending = True
    line = encounter.append_log(locale, "combat.defend")
    return CombatActionResult([line], world_changed=True)


def resolve_flee(state: WorldState, player: Player) -> CombatActionResult:
    locale = player.locale
    encounter = encounter_for_player(state, player)
    if encounter is None:
        from shared.i18n import t

        return CombatActionResult([t(locale, "combat.not_in_combat")])

    if not npc_in_player_room(state, player, encounter):
        return resolve_npc_departed(state, player, encounter)

    label = npc_label(state, encounter.npc_id, locale)
    if encounter.try_flee(player, state):
        line = encounter.append_log(locale, "combat.flee_ok", target=label)
        end_encounter(state, player, encounter)
        player.chased_by_npc = ""
        return CombatActionResult(
            [line],
            world_changed=True,
            ended=True,
            broadcast_key="combat.flee_broadcast",
            broadcast_kwargs={"name": player.name, "target": label},
        )

    line = encounter.append_log(locale, "combat.flee_fail", target=label)
    npc = state.world.npc(encounter.npc_id)
    if npc is not None and npc.aggro > 0 and npc.hostile:
        player.chased_by_npc = encounter.npc_id
        end_encounter(state, player, encounter)
        return CombatActionResult([line], world_changed=True, ended=True)

    return CombatActionResult([line], world_changed=True)


def resolve_quickhack(state: WorldState, player: Player) -> CombatActionResult:
    locale = player.locale
    encounter = encounter_for_player(state, player)
    if encounter is None:
        from shared.i18n import t

        return CombatActionResult([t(locale, "combat.not_in_combat")])

    if not npc_in_player_room(state, player, encounter):
        return resolve_npc_departed(state, player, encounter)

    if player.ram < QUICKHACK_RAM_COST:
        from shared.i18n import t

        return CombatActionResult([t(locale, "combat.no_ram", cost=str(QUICKHACK_RAM_COST))])

    if encounter.player_cd > 0:
        from combat.encounter import cd_ticks_to_seconds
        from shared.i18n import t

        secs = cd_ticks_to_seconds(state, encounter.player_cd)
        return CombatActionResult(
            [t(locale, "combat.player_cd", cd=str(secs))],
            world_changed=True,
        )

    player.ram -= QUICKHACK_RAM_COST
    damage = encounter.calc_quickhack_damage(player, state=state)
    encounter.npc_hp -= damage
    encounter.player_cd = ATTACK_CD
    label = npc_label(state, encounter.npc_id, locale)
    lines = [
        encounter.append_log(
            locale,
            "combat.quickhack",
            target=label,
            damage=str(damage),
            hp=str(max(0, encounter.npc_hp)),
        )
    ]

    if encounter.npc_hp <= 0:
        return _finish_victory(state, player, encounter, lines)

    return CombatActionResult(lines, world_changed=True)


def resolve_npc_attack(state: WorldState, player: Player, encounter: Encounter) -> CombatActionResult:
    locale = player.locale
    raw = encounter.calc_npc_damage(state)
    damage = encounter.apply_damage(raw)
    player.hp = max(0, player.hp - damage)
    label = npc_label(state, encounter.npc_id, locale)
    lines = [
        encounter.append_log(
            locale,
            "combat.npc_hit",
            target=label,
            damage=str(damage),
            hp=str(player.hp),
        )
    ]
    encounter.npc_cd = NPC_ATTACK_CD

    if player.hp <= 0:
        lines.append(encounter.append_log(locale, "combat.player_down"))
        end_encounter(state, player, encounter)
        return CombatActionResult(
            lines,
            world_changed=True,
            ended=True,
            broadcast_key="combat.defeat_broadcast",
            broadcast_kwargs={"name": player.name, "target": label},
        )

    return CombatActionResult(lines, world_changed=True)


def _finish_victory(
    state: WorldState,
    player: Player,
    encounter: Encounter,
    lines: list[str],
) -> CombatActionResult:
    locale = player.locale
    label = npc_label(state, encounter.npc_id, locale)
    lines.append(encounter.append_log(locale, "combat.victory", target=label))
    end_encounter(state, player, encounter)
    player.chased_by_npc = ""
    return CombatActionResult(
        lines,
        world_changed=True,
        ended=True,
        broadcast_key="combat.victory_broadcast",
        broadcast_kwargs={"name": player.name, "target": label},
    )


def tick_encounter(
    state: WorldState,
    encounter: Encounter,
    players: list[Player],
) -> CombatActionResult | None:
    player = _player_by_name(state, players, encounter.player_name)
    if player is None or not player.in_combat:
        state.encounters.pop(encounter.id, None)
        return None

    if not npc_in_player_room(state, player, encounter):
        return resolve_npc_departed(state, player, encounter)

    if encounter.player_cd > 0:
        encounter.player_cd -= 1
    if encounter.npc_cd > 0:
        encounter.npc_cd -= 1

    if encounter.npc_cd == 0 and encounter.npc_hp > 0 and player.hp > 0:
        result = resolve_npc_attack(state, player, encounter)
        return CombatActionResult(
            result.lines,
            world_changed=True,
            ended=result.ended,
            broadcast_key=result.broadcast_key,
            broadcast_kwargs=result.broadcast_kwargs,
        )

    return None