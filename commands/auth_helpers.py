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
    session_player.password_hash = loaded.password_hash


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