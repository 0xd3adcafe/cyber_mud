from __future__ import annotations

import hashlib

from commands.registry import CommandContext, ok
from persistence.save import load_player, player_exists, save_player
from shared.i18n import t

AUTH_COMMANDS = frozenset({"login", "register", "help", "quit"})


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def find_online_player(ctx: CommandContext, name: str):
    target = name.lower()
    for player in ctx.all_players:
        if player.named and player.name.lower() == target:
            return player
    return None


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
    session_player.ram = loaded.ram
    session_player.max_ram = loaded.max_ram
    session_player.implants = list(loaded.implants)
    session_player.visited_rooms = list(loaded.visited_rooms)
    session_player.prompt_mud = loaded.prompt_mud
    session_player.skills = list(loaded.skills)
    session_player.password_hash = loaded.password_hash
    session_player.faction = loaded.faction
    session_player.active_quest = loaded.active_quest
    session_player.quest_flags = dict(loaded.quest_flags)
    session_player.net_shell = loaded.net_shell
    session_player.weapon_mods = {k: list(v) for k, v in loaded.weapon_mods.items()}
    session_player.chased_by_npc = loaded.chased_by_npc
    session_player.in_combat = loaded.in_combat
    session_player.encounter_id = loaded.encounter_id


def handle_register(ctx: CommandContext):
    if ctx.player.named:
        return ok([t(ctx.player.locale, "auth.already_logged_in")])

    parts = ctx.args.split()
    if len(parts) < 2:
        return ok([t(ctx.player.locale, "auth.register_usage")])

    name, password = parts[0], parts[1]
    if len(name) < 2:
        return ok([t(ctx.player.locale, "auth.name_short")])
    if find_online_player(ctx, name):
        return ok([t(ctx.player.locale, "auth.name_online", name=name)])

    if player_exists(name):
        return ok([t(ctx.player.locale, "auth.name_taken", name=name)])

    ctx.player.name = name
    ctx.player.named = True
    ctx.player.password_hash = hash_password(password)
    ctx.player.room_id = ctx.state.world.start_room
    save_player(ctx.player)
    return ok([t(ctx.player.locale, "auth.register_ok", name=name)], auth_event=True)


def handle_login(ctx: CommandContext):
    if ctx.player.named:
        return ok([t(ctx.player.locale, "auth.already_logged_in")])

    parts = ctx.args.split()
    if len(parts) < 2:
        return ok([t(ctx.player.locale, "auth.login_usage")])

    name, password = parts[0], parts[1]
    if find_online_player(ctx, name):
        return ok([t(ctx.player.locale, "auth.name_online", name=name)])

    loaded = load_player(name)
    if loaded is None:
        return ok([t(ctx.player.locale, "auth.no_such_player", name=name)])
    if not verify_password(password, loaded.password_hash):
        return ok([t(ctx.player.locale, "auth.bad_password")])

    apply_loaded_player(ctx.player, loaded)
    return ok([t(ctx.player.locale, "auth.login_ok", name=name)], auth_event=True)