from commands.registry import CommandContext, player_meta
from shared.completion import complete_input, completion_meta
from shared.locale_content import item_label_with_id, npc_label_with_id
from tests.conftest import make_player, make_state


def test_item_label_with_id_zh():
    player, state = make_player(), make_state()
    item = state.world.item("glowstick")
    assert item is not None
    assert item_label_with_id(item, "zh") == "螢光棒 (Glowstick)"


def test_npc_label_with_id_zh():
    player, state = make_player(), make_state()
    npc = state.world.npc("broker")
    assert npc is not None
    assert npc_label_with_id(npc, "zh") == "情報經紀人 (Info Broker)"


def test_look_shows_english_suffix():
    from commands.registry import dispatch

    player, state = make_player(), make_state()
    result = dispatch("look", player, state, [], [])
    text = "\n".join(result.lines)
    assert "(Glowstick)" in text or "(glowstick)" in text


def test_completion_meta_includes_room_items():
    player, state = make_player(), make_state()
    meta = completion_meta(CommandContext(player, state, ""))
    assert "glowstick" in meta["complete_room_items"]
    assert "north" in meta["complete_exits"]


def test_player_meta_has_completion_fields():
    player, state = make_player(), make_state()
    meta = player_meta(CommandContext(player, state, ""))
    assert "complete_room_items" in meta
    assert "complete_npcs" in meta


def test_complete_input_verb():
    assert complete_input("t", room_items=(), room_npcs=(), room_exits=(), inventory=()) == "take"


def test_complete_input_look_item():
    result = complete_input(
        "look kn",
        room_items=("glowstick", "knife"),
        room_npcs=("broker",),
        room_exits=(),
        inventory=(),
    )
    assert result == "look knife"


def test_complete_input_look_npc():
    result = complete_input(
        "look bro",
        room_items=(),
        room_npcs=("broker",),
        room_exits=(),
        inventory=(),
    )
    assert result == "look broker"


def test_complete_input_take_item():
    result = complete_input(
        "take glo",
        room_items=("glowstick", "knife"),
        room_npcs=(),
        room_exits=(),
        inventory=(),
    )
    assert result == "take glowstick"


def test_complete_input_go_direction():
    result = complete_input(
        "go n",
        room_items=(),
        room_npcs=(),
        room_exits=("north", "south"),
        inventory=(),
    )
    assert result == "go north"


def test_complete_input_local_theme():
    assert complete_input("/th", room_items=(), room_npcs=(), room_exits=(), inventory=()) == "/theme"