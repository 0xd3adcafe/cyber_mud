from __future__ import annotations

from world.loader import clear_world_cache, default_room_items, load_world


def test_default_room_items_returns_independent_copies():
    clear_world_cache()
    first = default_room_items()
    second = default_room_items()
    first["square"].append("phantom_item")
    assert "phantom_item" not in second.get("square", [])


def test_load_world_cache_reuses_instance():
    clear_world_cache()
    assert load_world() is load_world()