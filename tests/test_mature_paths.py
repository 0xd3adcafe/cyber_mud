from __future__ import annotations

from shared.mature_paths import MATURE_DATA_ROOT, mature_content_available, mature_locale_path, romance_path


def test_mature_paths_layout():
    assert mature_locale_path("en").name == "mature_en.yaml"
    assert mature_locale_path("en").parent == MATURE_DATA_ROOT / "locale"
    assert romance_path().name == "romance.yaml"


def test_mature_pack_available_in_dev_tree():
    assert mature_content_available()