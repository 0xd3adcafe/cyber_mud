from __future__ import annotations

from commands.registry import CommandContext
from shared.target_resolve import (
    parse_item_target,
    parse_simple_target,
    resolve_item,
    resolve_item_id,
    split_give_args,
)
from tests.conftest import make_player, make_state


def _ctx():
    player = make_player()
    state = make_state()
    return CommandContext(player, state, "")


def test_parse_item_target_index_and_scope():
    assert parse_item_target("knife 2").name == "knife"
    assert parse_item_target("knife 2").index == 2
    assert parse_item_target("inventory knife").scope == "inventory"
    assert parse_item_target("knife.2").index == 2


def test_parse_simple_target():
    assert parse_simple_target("broker 2").name == "broker"
    assert parse_simple_target("broker 2").index == 2


def test_split_give_args():
    assert split_give_args("knife broker") == ("knife", "broker")
    assert split_give_args("knife 2 broker") == ("knife 2", "broker")


def test_resolve_item_ambiguous_on_ground_and_inventory():
    ctx = _ctx()
    ctx.player.inventory = ["knife"]
    result = resolve_item(ctx, "knife", scopes=("ground", "inventory"), verb="look")
    assert result.needs_response
    assert "1." in "\n".join(result.lines)


def test_resolve_item_index_picks_inventory():
    ctx = _ctx()
    ctx.player.inventory = ["knife"]
    result = resolve_item(ctx, "knife 2", scopes=("ground", "inventory"), verb="look")
    assert result.ok
    assert result.value.item_id == "knife"
    assert result.value.scope == "inventory"


def test_resolve_item_id_collapses_same_id():
    ctx = _ctx()
    ctx.player.inventory = ["knife"]
    result = resolve_item_id(ctx, "knife", scopes=("ground", "inventory"), verb="take")
    assert result.ok
    assert result.value == "knife"


def test_resolve_item_scoped_inventory():
    ctx = _ctx()
    ctx.player.inventory = ["knife"]
    result = resolve_item_id(ctx, "inventory knife", scopes=("ground", "inventory"), verb="drop")
    assert result.ok
    assert result.value == "knife"