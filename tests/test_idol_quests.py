from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.quests import accept_quest, quest_is_done


def _setup(state):
    for nid, room in (
        ("kabuki_idol_haejin", "kabuki_lounge"),
        ("kabuki_idol_airi", "kabuki_vip"),
    ):
        state.npc_rooms[nid] = room


def test_idol_blackmail_requires_arcana_unlock():
    player = make_player(locale="en", room_id="kabuki_lounge", content_rating="mature", street_cred=5)
    state = make_state()
    _setup(state)
    result = dispatch("talk kabuki_idol_haejin", player, state, [], [])
    assert not player.active_quest
    player.quest_flags["arcana_unlock_idol_blackmail"] = "1"
    result = dispatch("talk kabuki_idol_haejin", player, state, [], [])
    assert player.active_quest == "idol_blackmail"


def test_idol_fall_dual_ending():
    player = make_player(locale="en", room_id="kabuki_vip", content_rating="mature", street_cred=10)
    player.quest_flags["idol_blackmail"] = "done"
    player.quest_flags["arcana_unlock_idol_blackmail"] = "1"
    state = make_state()
    _setup(state)

    accept_quest(player, state, "idol_fall", "en", giver_npc_id="kabuki_idol_airi")
    player.quest_flags["idol_fall"] = "stage_2"
    dispatch("talk kabuki_idol_airi", player, state, [], [])
    assert player.quest_flags["idol_fall"] == "ready"
    dispatch("talk kabuki_idol_airi", player, state, [], [])
    assert quest_is_done(player, "idol_fall")
    assert player.quest_flags.get("idol_ending") == "airi"