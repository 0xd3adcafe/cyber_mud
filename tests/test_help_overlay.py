from client.help_overlay import format_help_overlay_content, help_overlay_header
from client.meta_handlers import SidebarPanel


def test_help_overlay_header_zh():
    assert "指令說明" in help_overlay_header(locale="zh")
    assert "F3" in help_overlay_header(locale="zh")


def test_help_overlay_header_en():
    assert "Command help" in help_overlay_header(locale="en")
    assert "F3" in help_overlay_header(locale="en")


def test_format_help_overlay_from_ui_list():
    panel = SidebarPanel(
        ui={
            "panel": "help",
            "sections": [
                {
                    "kind": "list",
                    "title": "探索移動",
                    "items": ["look — 察看環境", "go — 移動"],
                }
            ],
        }
    )
    text = format_help_overlay_content(panel)
    assert "探索移動" in text
    assert "look" in text
    assert "察看環境" in text
    assert "go" in text


def test_format_help_overlay_from_categorized_panel_lines():
    panel = SidebarPanel(
        lines=[
            "◈ 可用指令",
            "",
            "── 物品背包 ──",
            "  take — 撿起地上物品",
            "── 戰鬥 ──",
            "  flee — 逃離戰鬥",
        ]
    )
    text = format_help_overlay_content(panel)
    assert "物品背包" in text
    assert "take" in text
    assert "戰鬥" in text
    assert "flee" in text


def test_format_help_overlay_from_panel_lines():
    panel = SidebarPanel(lines=["◈ 可用指令", "", "  take — 撿起地上物品"])
    text = format_help_overlay_content(panel)
    assert "take" in text
    assert "撿起" in text