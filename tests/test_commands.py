from commands.registry import dispatch
from entities.player import Player
from world.loader import load_world
from world.state import WorldState


def _ctx(room_id: str = "square"):
    world = load_world()
    state = WorldState(world=world, room_items={"square": ["glowstick"]})
    player = Player(room_id=room_id, locale="zh", named=True, name="V")
    return player, state


def test_look_square():
    player, state = _ctx()
    result = dispatch("look", player, state, [], [])
    assert any("霓虹廣場" in line for line in result.lines)


def test_go_north():
    player, state = _ctx()
    result = dispatch("go north", player, state, [], [])
    assert player.room_id == "alley"
    assert result.moved


def test_alias_l():
    player, state = _ctx()
    result = dispatch("l", player, state, [], [])
    assert any("霓虹廣場" in line for line in result.lines)