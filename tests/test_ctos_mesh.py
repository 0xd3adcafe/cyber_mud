from commands.map import format_map
from commands.net_shell import dispatch_net
from commands.registry import CommandContext
from tests.conftest import make_player, make_state


def test_probe_discovers_mesh_links():
    player = make_player(room_id="watson_1_0", locale="en", net_shell=True, street_cred=10)
    state = make_state()
    ctx = CommandContext(player=player, state=state, args="", peers=[])
    result = dispatch_net("probe", ctx)
    text = "\n".join(result.lines)
    assert "Docks" in text or "docks" in text.lower()
    assert player.discovered_net_links


def test_map_shows_discovered_mesh():
    player = make_player(
        room_id="square",
        locale="en",
        visited_rooms=["square"],
        discovered_net_links=["docks_grid_node<->watson_grid_node"],
    )
    state = make_state()
    ctx = CommandContext(player=player, state=state, args="", peers=[])
    lines = format_map(ctx)
    text = "\n".join(lines)
    assert "mesh" in text.lower() or "ctOS" in text


def test_cross_district_link_locked_without_cred():
    player = make_player(room_id="watson_1_0", locale="en", net_shell=True, street_cred=0)
    state = make_state()
    ctx = CommandContext(player=player, state=state, args="", peers=[])
    dispatch_net("probe", ctx)
    assert not any("corpo" in link for link in player.discovered_net_links)