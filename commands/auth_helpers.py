from __future__ import annotations

from commands.registry import CommandContext, ok
from entities.player import Player
from persistence.account_lockout import (
    clear_lockout_state,
    is_account_locked,
    lockout_remaining_seconds,
    record_auth_failure,
)
from persistence.passwords import hash_password, needs_rehash, verify_password
from persistence.save import load_player, player_exists, save_name_allowed, save_player
from server.audit_log import log_security_event
from server.session_tokens import issue_session_token, rotate_session_token, validate_session_token
from shared.i18n import t
from shared.security import validate_character_name, validate_password
from world.mature import set_content_rating

AUTH_COMMANDS = frozenset({"login", "register", "resume", "help", "quit"})

STARTING_GOLD = 100


def parse_auth_credentials(args: str) -> tuple[str, str] | None:
    text = args.strip()
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None
    return parts[0], parts[1]


def parse_two_secret_fields(args: str) -> tuple[str, str] | None:
    text = args.strip()
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None
    return parts[0], parts[1]


def parse_register_credentials(args: str) -> tuple[str, str, bool] | None:
    text = args.strip()
    if not text:
        return None
    mature = False
    lowered = text.lower()
    if lowered.endswith(" mature"):
        text = text[: -len(" mature")].rstrip()
        mature = True
    creds = parse_auth_credentials(text)
    if creds is None:
        return None
    name, password = creds
    return name, password, mature


def auth_success_meta(player_name: str) -> dict[str, str]:
    token = issue_session_token(player_name)
    return {"session_token": token}


def find_online_player(ctx: CommandContext, name: str):
    target = name.lower()
    for player in ctx.all_players:
        if player.named and player.name.lower() == target:
            return player
    return None


def reset_player_to_guest(player, start_room: str) -> None:
    locale = player.locale
    fresh = Player(room_id=start_room, locale=locale)
    player.name = fresh.name
    player.room_id = fresh.room_id
    player.locale = fresh.locale
    player.named = False
    player.hp = fresh.hp
    player.max_hp = fresh.max_hp
    player.gold = fresh.gold
    player.body = fresh.body
    player.reflex = fresh.reflex
    player.tech = fresh.tech
    player.cool = fresh.cool
    player.intelligence = fresh.intelligence
    player.humanity = fresh.humanity
    player.reputation = fresh.reputation
    player.faction = fresh.faction
    player.ram = fresh.ram
    player.max_ram = fresh.max_ram
    player.inventory = list(fresh.inventory)
    player.equipment = dict(fresh.equipment)
    player.implants = list(fresh.implants)
    player.cyberware = dict(fresh.cyberware)
    player.home_room_id = fresh.home_room_id
    player.home_stash = list(fresh.home_stash)
    player.vehicle_id = fresh.vehicle_id
    player.vehicles = list(fresh.vehicles)
    player.active_vehicle = fresh.active_vehicle
    player.wanted_level = fresh.wanted_level
    player.interact_flags = dict(fresh.interact_flags)
    player.braindance_flags = dict(fresh.braindance_flags)
    player.visited_rooms = list(fresh.visited_rooms)
    player.prompt_mud = fresh.prompt_mud
    player.skills = list(fresh.skills)
    player.proficiency_levels = dict(fresh.proficiency_levels)
    player.proficiency_xp = dict(fresh.proficiency_xp)
    player.password_hash = fresh.password_hash
    player.auth_failed_attempts = fresh.auth_failed_attempts
    player.auth_locked_until = fresh.auth_locked_until
    player.in_combat = False
    player.encounter_id = ""
    player.active_quest = fresh.active_quest
    player.quest_flags = dict(fresh.quest_flags)
    player.quest_hint = fresh.quest_hint
    player.net_shell = False
    player.weapon_mods = dict(fresh.weapon_mods)
    player.chased_by_npc = fresh.chased_by_npc
    player.content_rating = fresh.content_rating
    player.romance_flags = dict(fresh.romance_flags)
    player.player_status = dict(fresh.player_status)
    player.posture = fresh.posture
    player.fatigue = fresh.fatigue
    player.life_anchor = fresh.life_anchor


def apply_loaded_player(session_player, loaded) -> None:
    session_player.name = loaded.name
    session_player.room_id = loaded.room_id
    session_player.locale = loaded.locale
    session_player.named = True
    session_player.hp = loaded.hp
    session_player.max_hp = loaded.max_hp
    session_player.gold = loaded.gold
    session_player.inventory = list(loaded.inventory)
    session_player.equipment = dict(loaded.equipment)
    session_player.body = loaded.body
    session_player.reflex = loaded.reflex
    session_player.tech = loaded.tech
    session_player.cool = loaded.cool
    session_player.intelligence = loaded.intelligence
    session_player.humanity = loaded.humanity
    session_player.reputation = loaded.reputation
    session_player.street_cred = loaded.street_cred
    session_player.level = loaded.level
    session_player.xp = loaded.xp
    session_player.attribute_points = loaded.attribute_points
    session_player.perk_points = loaded.perk_points
    session_player.perks = list(loaded.perks)
    session_player.ram = loaded.ram
    session_player.max_ram = loaded.max_ram
    session_player.implants = list(loaded.implants)
    session_player.cyberware = dict(loaded.cyberware)
    session_player.home_room_id = loaded.home_room_id
    session_player.home_stash = list(loaded.home_stash)
    session_player.vehicle_id = loaded.vehicle_id
    session_player.vehicles = list(loaded.vehicles)
    session_player.active_vehicle = loaded.active_vehicle
    session_player.wanted_level = loaded.wanted_level
    session_player.interact_flags = dict(loaded.interact_flags)
    session_player.braindance_flags = dict(loaded.braindance_flags)
    session_player.visited_rooms = list(loaded.visited_rooms)
    session_player.prompt_mud = loaded.prompt_mud
    session_player.skills = list(loaded.skills)
    session_player.proficiency_levels = dict(loaded.proficiency_levels)
    session_player.proficiency_xp = dict(loaded.proficiency_xp)
    session_player.password_hash = loaded.password_hash
    session_player.auth_failed_attempts = loaded.auth_failed_attempts
    session_player.auth_locked_until = loaded.auth_locked_until
    session_player.faction = loaded.faction
    session_player.active_quest = loaded.active_quest
    session_player.quest_flags = dict(loaded.quest_flags)
    session_player.net_shell = loaded.net_shell
    session_player.weapon_mods = {k: list(v) for k, v in loaded.weapon_mods.items()}
    session_player.chased_by_npc = loaded.chased_by_npc
    session_player.in_combat = loaded.in_combat
    session_player.encounter_id = loaded.encounter_id
    session_player.content_rating = loaded.content_rating
    session_player.romance_flags = dict(loaded.romance_flags)
    session_player.player_status = dict(loaded.player_status)
    session_player.posture = loaded.posture
    session_player.fatigue = loaded.fatigue
    session_player.life_anchor = loaded.life_anchor


def _persist_lockout_state(loaded: Player) -> None:
    save_player(loaded)


def _account_locked_response(ctx: CommandContext, loaded: Player):
    remaining = lockout_remaining_seconds(locked_until=loaded.auth_locked_until)
    minutes = max(1, (remaining + 59) // 60)
    log_security_event(
        "auth_account_locked",
        player=loaded.name,
        remaining_seconds=remaining,
    )
    return ok(
        [t(ctx.player.locale, "auth.account_locked", minutes=str(minutes))],
        auth_failure=True,
    )


def handle_register(ctx: CommandContext):
    if ctx.player.named:
        return ok([t(ctx.player.locale, "auth.already_logged_in")])

    parsed = parse_register_credentials(ctx.args)
    if parsed is None:
        return ok([t(ctx.player.locale, "auth.register_usage")])

    name, password, mature_opt_in = parsed
    if err := validate_character_name(name):
        return ok([t(ctx.player.locale, err)])
    if not save_name_allowed(name):
        return ok([t(ctx.player.locale, "auth.name_invalid")])
    if err := validate_password(password):
        return ok([t(ctx.player.locale, err)])
    if find_online_player(ctx, name):
        return ok([t(ctx.player.locale, "auth.name_online", name=name)])

    if player_exists(name):
        return ok([t(ctx.player.locale, "auth.name_taken", name=name)])

    ctx.player.name = name
    ctx.player.named = True
    ctx.player.password_hash = hash_password(password)
    ctx.player.room_id = ctx.state.world.start_room
    ctx.player.gold = STARTING_GOLD
    if mature_opt_in:
        set_content_rating(ctx.player, True)
    save_player(ctx.player)
    log_security_event("auth_register_success", player=name)
    lines = [t(ctx.player.locale, "auth.register_ok", name=name)]
    if mature_opt_in:
        lines.append(t(ctx.player.locale, "auth.register_mature_on"))
    return ok(lines, auth_event=True, meta=auth_success_meta(name))


def handle_login(ctx: CommandContext):
    if ctx.player.named:
        return ok([t(ctx.player.locale, "auth.already_logged_in")])

    creds = parse_auth_credentials(ctx.args)
    if creds is None:
        return ok([t(ctx.player.locale, "auth.login_usage")])

    name, password = creds
    if find_online_player(ctx, name):
        return ok([t(ctx.player.locale, "auth.name_online", name=name)])

    loaded = load_player(name)
    if loaded is None:
        log_security_event("auth_login_failure", player=name, reason="unknown_account")
        return ok([t(ctx.player.locale, "auth.invalid_credentials")], auth_failure=True)

    if is_account_locked(locked_until=loaded.auth_locked_until):
        return _account_locked_response(ctx, loaded)

    if not verify_password(password, loaded.password_hash):
        attempts, locked_until, newly_locked = record_auth_failure(
            failed_attempts=loaded.auth_failed_attempts,
            locked_until=loaded.auth_locked_until,
        )
        loaded.auth_failed_attempts = attempts
        loaded.auth_locked_until = locked_until
        _persist_lockout_state(loaded)
        log_security_event(
            "auth_login_failure",
            player=name,
            reason="bad_password",
            newly_locked=newly_locked,
        )
        if newly_locked:
            return _account_locked_response(ctx, loaded)
        return ok([t(ctx.player.locale, "auth.invalid_credentials")], auth_failure=True)

    loaded.auth_failed_attempts, loaded.auth_locked_until = clear_lockout_state()
    apply_loaded_player(ctx.player, loaded)
    if needs_rehash(loaded.password_hash):
        ctx.player.password_hash = hash_password(password)
    save_player(ctx.player)
    log_security_event("auth_login_success", player=name)
    return ok(
        [t(ctx.player.locale, "auth.login_ok", name=name)],
        auth_event=True,
        meta=auth_success_meta(name),
    )


def handle_resume(ctx: CommandContext):
    if ctx.player.named:
        return ok([t(ctx.player.locale, "auth.already_logged_in")])

    token = ctx.args.strip()
    if not token:
        return ok([t(ctx.player.locale, "auth.resume_usage")])

    player_key = validate_session_token(token)
    if player_key is None:
        log_security_event("auth_resume_failure", reason="invalid_token")
        return ok([t(ctx.player.locale, "auth.invalid_session")], auth_failure=True)

    loaded = load_player(player_key)
    if loaded is None:
        log_security_event("auth_resume_failure", player=player_key, reason="missing_save")
        return ok([t(ctx.player.locale, "auth.invalid_session")], auth_failure=True)

    if is_account_locked(locked_until=loaded.auth_locked_until):
        return _account_locked_response(ctx, loaded)

    if find_online_player(ctx, loaded.name):
        return ok([t(ctx.player.locale, "auth.name_online", name=loaded.name)])

    new_token = rotate_session_token(token)
    if new_token is None:
        log_security_event("auth_resume_failure", player=loaded.name, reason="rotate_failed")
        return ok([t(ctx.player.locale, "auth.invalid_session")], auth_failure=True)

    apply_loaded_player(ctx.player, loaded)
    log_security_event("auth_resume_success", player=loaded.name)
    return ok(
        [t(ctx.player.locale, "auth.resume_ok", name=loaded.name)],
        auth_event=True,
        meta={"session_token": new_token},
    )