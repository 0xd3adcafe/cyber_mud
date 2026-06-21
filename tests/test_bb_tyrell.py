from __future__ import annotations

from tests.conftest import make_player, make_state
from world.quests import quest_available


def test_tyrell_bb_npcs_and_net_node():
    state = make_state()
    for nid in ("tyrell_liaison_vera", "tyrell_gene_thief_seojin", "tyrell_corp_attendant_meera"):
        assert state.world.npc(nid) is not None
    assert state.world.net_node("corpo_ghost_control") is not None


def test_tyrell_shadow_requires_arcana():
    player = make_player(street_cred=10)
    state = make_state()
    quest = state.world.quest("tyrell_shadow")
    assert quest is not None
    assert not quest_available(player, quest)
    player.quest_flags["arcana_unlock_tyrell_shadow"] = "1"
    assert quest_available(player, quest)