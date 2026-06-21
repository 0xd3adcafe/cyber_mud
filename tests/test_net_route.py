from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.ctos_mesh import discover_mesh_in_room


def test_route_via_mesh_after_probe():
    player = make_player(room_id="watson_1_0", locale="en", ram=8, street_cred=10)
    state = make_state()
    dispatch("net", player, state, [], [])
    dispatch("probe", player, state, [], [])
    discover_mesh_in_room(player, state, "watson_1_0")
    result = dispatch("route docks_grid_node", player, state, [], [])
    text = "\n".join(result.lines)
    assert "Docks" in text or "碼頭" in text or "proxy" in text.lower() or "mesh" in text.lower()
    assert player.net_route_node == "docks_grid_node"