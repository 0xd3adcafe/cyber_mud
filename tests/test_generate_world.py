from __future__ import annotations

import yaml

from tools.generate_world import build_rooms, main, render_yaml, room_id


def test_build_rooms_grid_exits():
    rooms = build_rooms("watson", "watson", rows=2, cols=3)
    assert len(rooms) == 6
    assert rooms[room_id("watson", 0, 0)]["exits"] == {"east": "watson_1_0", "south": "watson_0_1"}
    assert rooms[room_id("watson", 2, 1)]["exits"] == {"west": "watson_1_1", "north": "watson_2_0"}
    assert rooms[room_id("watson", 1, 0)]["exits"] == {
        "south": "watson_1_1",
        "east": "watson_2_0",
        "west": "watson_0_0",
    }


def test_render_yaml_roundtrip():
    rooms = build_rooms("dock", "docks", rows=1, cols=2)
    text = render_yaml(rooms, start_room=room_id("dock", 0, 0))
    data = yaml.safe_load(text)
    assert data["start_room"] == "dock_0_0"
    assert set(data["rooms"]) == {"dock_0_0", "dock_1_0"}


def test_main_stdout(capsys):
    assert main(["testdist", "2", "2"]) == 0
    out = capsys.readouterr().out
    data = yaml.safe_load(out)
    assert data["start_room"] == "testdist_0_0"
    assert len(data["rooms"]) == 4