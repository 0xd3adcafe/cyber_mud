from __future__ import annotations

from entities.player import Player
from persistence.save import player_from_dict


def test_new_player_defaults_to_en():
    player = Player()
    assert player.locale == "en"


def test_save_load_defaults_missing_locale_to_en():
    player = player_from_dict({"name": "V", "room_id": "square"})
    assert player.locale == "en"