from __future__ import annotations

from commands.registry import dispatch
from entities.player import Player
from shared.locks import evaluate_lock, lock_allows, parse_locks
from tests.conftest import make_player, make_state
from world.world import Room


def test_parse_locks_strips_empty():
    assert parse_locks({"go": " street_cred >= 20 ", "use": ""}) == {"go": "street_cred >= 20"}


def test_evaluate_lock_predicates():
    player = Player(street_cred=25, faction="street")
    player.inventory.append("corpo_token")
    player.quest_flags["vault_ok"] = "1"
    state = make_state()

    assert evaluate_lock("street_cred >= 20", player, state)
    assert not evaluate_lock("street_cred >= 30", player, state)
    assert evaluate_lock("has_item(corpo_token)", player, state)
    assert evaluate_lock("faction(street)", player, state)
    assert evaluate_lock("flag(vault_ok)", player, state)


def test_lock_allows_room_go():
    player = make_player(room_id="crypt", street_cred=5)
    state = make_state()
    dest = state.world.room("data_vault")
    assert dest is not None
    assert not lock_allows(dest, "go", player, state)

    player.street_cred = 20
    assert lock_allows(dest, "go", player, state)


def test_go_denied_without_street_cred():
    player = make_player(room_id="crypt", street_cred=0, locale="en")
    state = make_state()
    result = dispatch("go north", player, state, [], [])
    assert player.room_id == "crypt"
    assert any("clearance" in line.lower() for line in result.lines)


def test_go_allowed_with_street_cred():
    player = make_player(room_id="crypt", street_cred=20, locale="en")
    state = make_state()
    result = dispatch("go north", player, state, [], [])
    assert player.room_id == "data_vault"
    assert result.moved


def test_hack_vault_core_requires_token():
    player = make_player(room_id="data_vault", locale="en")
    player.ram = 4
    state = make_state()
    dispatch("net", player, state, [], [])
    denied = dispatch("hack vault", player, state, [], [])
    assert any("firewall" in line.lower() or "credentials" in line.lower() for line in denied.lines)

    player.inventory.append("corpo_token")
    allowed = dispatch("hack vault", player, state, [], [])
    assert player.ram == 3
    assert any("Vault Core" in line for line in allowed.lines)


def test_entity_without_locks_always_allows():
    player = make_player()
    state = make_state()
    room = Room(id="open")
    assert lock_allows(room, "go", player, state)