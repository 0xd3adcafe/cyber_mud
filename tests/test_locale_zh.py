from __future__ import annotations

from pathlib import Path

from shared.i18n import DATA_ROOT
from shared.locale_validate import validate_main_locale_parity
from shared.mature_paths import mature_locale_path
from shared.zh_traditional_audit import (
    audit_world_zh_fields,
    audit_yaml_strings,
    needs_traditional_fix,
    normalize_tw_text,
)


def test_main_locale_key_parity():
    errors = [issue for issue in validate_main_locale_parity() if issue.severity == "error"]
    assert errors == []


def test_zh_yaml_traditional_audit_clean():
    issues = audit_yaml_strings(DATA_ROOT / "zh.yaml", label="zh")
    errors = [issue for issue in issues if issue.severity == "error"]
    assert errors == []


def test_mature_zh_traditional_audit_clean():
    issues = audit_yaml_strings(mature_locale_path("zh"), label="mature_zh")
    errors = [issue for issue in issues if issue.severity == "error"]
    assert errors == []


def test_world_zh_fields_traditional_audit_clean():
    issues = audit_world_zh_fields(Path(__file__).resolve().parents[1] / "data")
    errors = [issue for issue in issues if issue.severity == "error"]
    assert errors == []


def test_normalize_tw_preserves_game_terms():
    assert normalize_tw_text("背包裡的干擾訊號") == "背包裡的干擾訊號"
    assert needs_traditional_fix("书包藏着庙口传闻") is True
    assert needs_traditional_fix("沙耶香整書包") is False