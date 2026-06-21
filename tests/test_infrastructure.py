from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.infrastructure import room_infra_tags
from world.loader import load_world


def test_room_infra_tags_square():
    room = load_world().room("square")
    tags = room_infra_tags(room)
    assert "surveillance" in tags
    assert "traffic" in tags


def test_look_shows_ctos_infra():
    player = make_player(room_id="square", locale="en")
    state = make_state()
    result = dispatch("look", player, state, [], [])
    text = "\n".join(result.lines)
    assert "ctOS" in text
    assert "surveillance" in text.lower() or "camera" in text.lower()


def test_scan_shows_ctos_infra():
    player = make_player(room_id="docks", locale="en")
    state = make_state()
    result = dispatch("scan", player, state, [], [])
    text = "\n".join(result.lines)
    assert "power_grid" in text or "power" in text.lower()