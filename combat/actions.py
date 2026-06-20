from __future__ import annotations

from dataclasses import dataclass

from combat.encounter import (
    ATTACK_CD,
    NPC_ATTACK_CD,
    QUICKHACK_RAM_COST,
    Encounter,
    end_encounter,
    encounter_for_player,
    npc_in_player_room,
    npc_label,
)

from entities.player import Player
from shared.i18n import t
from shared.locale_content import room_name
from world.corpses import corpse_label, spawn_corpse, spawn_player_corpse
from world.state import WorldState


@dataclass
class CombatActionResult:
    lines: list[str]
    world_changed: bool = False
    ended: bool = False
    moved: bool = False
    broadcast_key: str = ""
    broadcast_mature_key: str = ""
    broadcast_kwargs: dict[str, str] | None = None
    broadcast_room_id: str = ""


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


def resolve_defend(state: WorldState, player: Player) -> CombatActionResult:
    locale = player.locale
    encounter = encounter_for_player(state, player)
    if encounter is None:
        from shared.i18n import t

        return CombatActionResult([t(locale, "combat.not_in_combat")])

    if not npc_in_player_room(state, player, encounter):
        return resolve_npc_departed(state, player, encounter)

    from combat.defend_style import defend_combat_key, defend_combat_kwargs

    encounter.defending = True
    line = encounter.append_log(
        locale,
        defend_combat_key(player, state.world),
        **defend_combat_kwargs(player, state.world, locale),
    )
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
    if npc is not None and npc.hostile and npc.aggro > 0:
        from world.factions import npc_aggro_modifier
        from world.modifiers import district_aggro_bonus

        effective_aggro = (
            npc.aggro
            + npc_aggro_modifier(player, state.world.room(player.room_id))
            + int(district_aggro_bonus(state, player.room_id) * 10)
        )
        if effective_aggro > 0:
            player.chased_by_npc = encounter.npc_id
        end_encounter(state, player, encounter)
        return CombatActionResult([line], world_changed=True, ended=True)

    return CombatActionResult([line], world_changed=True)


def resolve_quickhack(state: WorldState, player: Player, quickhack_id: str = "") -> CombatActionResult:
    locale = player.locale
    encounter = encounter_for_player(state, player)
    if encounter is None:
        return CombatActionResult([t(locale, "combat.not_in_combat")])

    if not npc_in_player_room(state, player, encounter):
        return resolve_npc_departed(state, player, encounter)

    from combat.encounter import cd_ticks_to_seconds

    qh_id = _resolve_quickhack_id(state, player, quickhack_id)
    if qh_id is None:
        return CombatActionResult([t(locale, "quickhack.unknown", name=quickhack_id or "")])

    quickhack = state.world.quickhack(qh_id)
    if quickhack is None:
        return CombatActionResult([t(locale, "quickhack.unknown", name=quickhack_id)])

    ram_cost = quickhack.ram_cost
    if player.ram < ram_cost:
        return CombatActionResult([t(locale, "combat.no_ram", cost=str(ram_cost))])

    if encounter.player_cd > 0:
        secs = cd_ticks_to_seconds(state, encounter.player_cd)
        return CombatActionResult(
            [t(locale, "combat.player_cd", cd=str(secs))],
            world_changed=True,
        )

    player.ram -= ram_cost
    damage = encounter.calc_quickhack_damage(player, state=state, damage_mult=quickhack.damage_mult)
    encounter.npc_hp -= damage
    encounter.player_cd = ATTACK_CD
    if quickhack.status_effect and quickhack.status_duration > 0:
        encounter.npc_status.apply(quickhack.status_effect, quickhack.status_duration)

    label = npc_label(state, encounter.npc_id, locale)
    qh_label = quickhack.name_zh if locale == "zh" else (quickhack.name_en or quickhack.name_zh)
    lines = [
        encounter.append_log(
            locale,
            "combat.quickhack_named",
            hack=qh_label or qh_id,
            target=label,
            damage=str(damage),
            hp=str(max(0, encounter.npc_hp)),
        )
    ]
    if quickhack.status_effect:
        lines.append(
            t(locale, "combat.status_applied", effect=t(locale, f"status.{quickhack.status_effect}"))
        )

    from world.trauma import apply_player_overheat

    apply_player_overheat(player, duration=3)
    lines.append(t(locale, "combat.overheat_self"))
    from world.reactions import reputation_from_quickhack, shift_reputation

    lines.extend(shift_reputation(player, reputation_from_quickhack(), locale))
    from world.proficiencies import award_proficiency_xp

    lines.extend(
        award_proficiency_xp(
            player,
            "quickhacking",
            12,
            locale,
            proficiencies=state.world.proficiencies,
        )
    )

    if encounter.npc_hp <= 0:
        return _finish_victory(state, player, encounter, lines)

    return CombatActionResult(lines, world_changed=True)


def _resolve_quickhack_id(state: WorldState, player: Player, name: str) -> str | None:
    from combat.encounter import available_quickhacks

    allowed = available_quickhacks(state.world, player)
    if not allowed:
        return None
    needle = name.strip().lower()
    if not needle:
        return allowed[0]
    for qid in allowed:
        qh = state.world.quickhack(qid)
        if qh is None:
            continue
        labels = {qid.lower(), qh.name_zh.lower(), qh.name_en.lower()}
        if needle in labels:
            return qid
    return None


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
    from world.trauma import maybe_bleed_on_hit, maybe_poison_on_hit

    maybe_bleed_on_hit(player, damage)
    npc = state.world.npc(encounter.npc_id)
    maybe_poison_on_hit(
        player,
        encounter.npc_id,
        damage,
        npc_faction=npc.faction if npc else "",
    )

    if player.hp <= 0:
        lines.append(encounter.append_log(locale, "combat.player_down"))
        return _finish_defeat(
            state,
            player,
            encounter,
            lines,
            npc_label=label,
        )

    return CombatActionResult(lines, world_changed=True)


def _finish_defeat(
    state: WorldState,
    player: Player,
    encounter: Encounter,
    lines: list[str],
    *,
    npc_label: str,
) -> CombatActionResult:
    locale = player.locale
    death_room = player.room_id
    corpse = spawn_player_corpse(state, player, death_room)
    if corpse is not None:
        corpse_name = corpse_label(state, corpse, locale)
        lines.append(t(locale, "corpse.created", label=corpse_name))
    end_encounter(state, player, encounter)
    player.chased_by_npc = ""
    respawn_id = state.world.respawn_room
    respawn = state.world.room(respawn_id)
    moved = False
    if respawn is not None:
        player.room_id = respawn_id
        player.hp = player.max_hp
        moved = True
        lines.append(t(locale, "combat.respawn", room=room_name(respawn, locale)))
    else:
        player.hp = max(1, player.max_hp // 4)
    from world.mature import is_mature
    from world.mature_social import random_mature_combat_broadcast

    mature_broadcast = random_mature_combat_broadcast("defeat") if is_mature(player) else ""
    return CombatActionResult(
        lines,
        world_changed=True,
        ended=True,
        moved=moved,
        broadcast_key="combat.defeat_broadcast",
        broadcast_mature_key=mature_broadcast,
        broadcast_kwargs={"name": player.name, "target": npc_label},
        broadcast_room_id=death_room,
    )


def _finish_victory(
    state: WorldState,
    player: Player,
    encounter: Encounter,
    lines: list[str],
) -> CombatActionResult:
    locale = player.locale
    label = npc_label(state, encounter.npc_id, locale)
    lines.append(encounter.append_log(locale, "combat.victory", target=label))
    from combat.gore import maybe_gore_kill

    gore_line = maybe_gore_kill(player, locale, target=label)
    if gore_line:
        lines.append(gore_line)
    room_id = state.npc_room(encounter.npc_id) or player.room_id
    corpse = spawn_corpse(state, encounter.npc_id, room_id)
    if corpse is not None:
        corpse_name = corpse_label(state, corpse, locale)
        lines.append(t(locale, "corpse.created", label=corpse_name))
    end_encounter(state, player, encounter)
    player.chased_by_npc = ""
    npc = state.world.npc(encounter.npc_id)
    from world.progression import award_xp, npc_xp_reward

    lines.extend(award_xp(player, npc_xp_reward(npc), locale, state=state))
    from world.proficiencies import award_proficiency_xp

    lines.extend(
        award_proficiency_xp(
            player,
            "cold_blood",
            15,
            locale,
            proficiencies=state.world.proficiencies,
        )
    )
    from world.street_cred import STREET_CRED_PER_NPC, award_street_cred

    lines.extend(award_street_cred(player, STREET_CRED_PER_NPC, locale))
    from world.wanted import add_wanted

    lines.extend(add_wanted(player, 1, locale))
    from world.quests import advance_quest_on_defeat
    from world.reactions import reputation_from_combat_victory, shift_reputation

    lines.extend(advance_quest_on_defeat(player, state, encounter.npc_id, locale))
    lines.extend(shift_reputation(player, reputation_from_combat_victory(npc), locale))
    from world.mature import is_mature
    from world.mature_social import random_mature_combat_broadcast

    mature_broadcast = random_mature_combat_broadcast("victory") if is_mature(player) else ""
    return CombatActionResult(
        lines,
        world_changed=True,
        ended=True,
        broadcast_key="combat.victory_broadcast",
        broadcast_mature_key=mature_broadcast,
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

    burn_lines = _tick_npc_status(state, player, encounter)
    if burn_lines:
        if encounter.npc_hp <= 0:
            return _finish_victory(state, player, encounter, burn_lines)
        return CombatActionResult(burn_lines, world_changed=True)

    if encounter.npc_cd == 0 and encounter.npc_hp > 0 and player.hp > 0:
        from world.status_effects import npc_skip_attack

        if npc_skip_attack(encounter.npc_status):
            label = npc_label(state, encounter.npc_id, player.locale)
            line = encounter.append_log(player.locale, "combat.shock_skip", target=label)
            encounter.npc_cd = NPC_ATTACK_CD
            return CombatActionResult([line], world_changed=True)
        result = resolve_npc_attack(state, player, encounter)
        return CombatActionResult(
            result.lines,
            world_changed=result.world_changed,
            ended=result.ended,
            moved=result.moved,
            broadcast_key=result.broadcast_key,
            broadcast_kwargs=result.broadcast_kwargs,
            broadcast_room_id=result.broadcast_room_id,
        )

    return None


def _tick_npc_status(state: WorldState, player: Player, encounter: Encounter) -> list[str]:
    from world.status_effects import EFFECT_BURN, burn_tick_damage

    lines: list[str] = []
    locale = player.locale
    if encounter.npc_status.has(EFFECT_BURN):
        damage = burn_tick_damage(player.intelligence)
        encounter.npc_hp -= damage
        label = npc_label(state, encounter.npc_id, locale)
        lines.append(
            encounter.append_log(
                locale,
                "combat.burn_tick",
                target=label,
                damage=str(damage),
                hp=str(max(0, encounter.npc_hp)),
            )
        )
    encounter.npc_status.tick()
    return lines

