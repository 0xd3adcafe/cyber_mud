from __future__ import annotations

from combat.actions import CombatActionResult, _finish_victory
from combat.encounter import (
    Encounter,
    encounter_for_player,
    find_hostile_npc_in_room,
    npc_in_player_room,
    npc_label,
    start_encounter,
)
from combat.styles import (
    ALL_STYLES,
    STYLES,
    STYLE_BACKSTAB,
    default_style_for_weapon,
    roll_backstab,
    style_error_key,
    calc_strike_damage,
)
from combat.encounter import cd_ticks_to_seconds
from combat.actions import resolve_npc_departed
from entities.player import Player
from shared.i18n import t
from world.state import WorldState


def parse_attack_args(args: str) -> tuple[str, str]:
    text = args.strip()
    if not text:
        return "", ""
    parts = text.split(maxsplit=1)
    if parts[0].lower() in ALL_STYLES:
        return parts[0].lower(), parts[1] if len(parts) > 1 else ""
    return "", text


def resolve_player_strike(
    state: WorldState,
    player: Player,
    *,
    style: str = "",
    target: str = "",
) -> CombatActionResult:
    locale = player.locale
    style_id = style or default_style_for_weapon(player, state.world)
    if style_id not in STYLES:
        return CombatActionResult([t(locale, "combat.unknown_style")])

    err_key = style_error_key(style_id, player, state.world)
    if err_key:
        return CombatActionResult([t(locale, err_key)])

    encounter = encounter_for_player(state, player)
    style_def = STYLES[style_id]

    if encounter is None:
        if not target:
            return CombatActionResult([t(locale, "combat.attack_usage")])
        npc = find_hostile_npc_in_room(state, player.room_id, target)
        if npc is None:
            return CombatActionResult([t(locale, "combat.no_target")])
        encounter = start_encounter(state, player, npc.id)
        label = npc_label(state, npc.id, locale)
        line = encounter.append_log(locale, style_def.start_key, target=label)
        lines = [line]
    else:
        if not npc_in_player_room(state, player, encounter):
            return resolve_npc_departed(state, player, encounter)

        if target:
            from shared.names import matches_name

            npc = state.world.npc(encounter.npc_id)
            current = npc_label(state, encounter.npc_id, locale)
            if npc is None or not matches_name(target, encounter.npc_id, npc.name_zh, npc.name_en):
                return CombatActionResult([t(locale, "combat.already_fighting", target=current)])

        if encounter.player_cd > 0:
            secs = cd_ticks_to_seconds(state, encounter.player_cd)
            return CombatActionResult(
                [t(locale, "combat.player_cd", cd=str(secs))],
                world_changed=True,
            )

        lines = []

    from combat.passives import bonus_attack_damage
    from world.modifiers import apply_damage_modifier

    def room_mod(raw: int) -> int:
        if player.room_id:
            return apply_damage_modifier(state, player.room_id, raw)
        return raw

    weapon_damage = 0
    if not style_def.unarmed_only:
        weapon_damage = encounter.player_weapon_damage(player, state.world)

    backstab_hit = True
    if style_id == STYLE_BACKSTAB:
        backstab_hit = roll_backstab(player)

    from world.proficiencies import (
        award_proficiency_xp,
        proficiency_damage_bonus,
        proficiency_for_strike,
    )

    prof_id = proficiency_for_strike(player, state.world, style_id=style_id)
    damage = calc_strike_damage(
        style_id=style_id,
        player=player,
        world=state.world,
        weapon_damage=weapon_damage,
        bonus_damage=bonus_attack_damage(player, state),
        backstab_hit=backstab_hit,
        room_modifier=room_mod,
        proficiency_bonus=proficiency_damage_bonus(player, prof_id),
    )

    encounter.npc_hp -= damage
    encounter.player_cd = style_def.cd_ticks
    from world.life import gain_fatigue

    gain_fatigue(player, "combat")
    label = npc_label(state, encounter.npc_id, locale)

    if style_id == STYLE_BACKSTAB and not backstab_hit:
        lines.append(
            encounter.append_log(
                locale,
                "combat.backstab_fail",
                target=label,
                damage=str(damage),
                hp=str(max(0, encounter.npc_hp)),
            )
        )
    else:
        lines.append(
            encounter.append_log(
                locale,
                style_def.hit_key,
                target=label,
                damage=str(damage),
                hp=str(max(0, encounter.npc_hp)),
            )
        )
        npc = state.world.npc(encounter.npc_id)
        from combat.gore import maybe_gore_crit

        gore_line = maybe_gore_crit(
            player,
            locale,
            target=label,
            damage=damage,
            npc_max_hp=npc.max_hp if npc else 30,
        )
        if gore_line:
            lines.append(gore_line)

    if prof_id:
        xp_gain = max(5, min(20, damage // 2))
        lines.extend(
            award_proficiency_xp(
                player,
                prof_id,
                xp_gain,
                locale,
                proficiencies=state.world.proficiencies,
            )
        )

    if encounter.npc_hp <= 0:
        return _finish_victory(state, player, encounter, lines)

    return CombatActionResult(lines, world_changed=True)


def resolve_player_attack(state: WorldState, player: Player, *, target: str = "") -> CombatActionResult:
    style, parsed_target = parse_attack_args(target)
    return resolve_player_strike(state, player, style=style, target=parsed_target)