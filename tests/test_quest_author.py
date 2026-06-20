from __future__ import annotations

import yaml

from world.content import Quest, QuestStage, load_quests
from world.loader import load_world
from world.quest_author import (
    format_quest_outline,
    npc_quest_roles,
    scaffold_quest_yaml,
    validate_quest,
    validate_quests,
)


def test_validate_real_quests_pass():
    world = load_world()
    errors = [issue for issue in validate_quests(world) if issue.severity == "error"]
    assert not errors


def test_validate_missing_stage_target():
    world = load_world()
    quest = Quest(
        id="bad_quest",
        name_zh="壞任務",
        npc_id="broker",
        complete_npc_id="broker",
        stages=[QuestStage(objective_type="visit_room", objective_target="missing_room")],
    )
    issues = validate_quest(world, quest)
    assert any(issue.severity == "error" and "missing_room" in issue.message for issue in issues)


def test_format_quest_outline_dock_watch():
    world = load_world()
    quest = world.quest("dock_watch")
    assert quest is not None
    text = format_quest_outline(quest, world)
    assert "碼頭監視" in text
    assert "visit_room" in text
    assert "dock_crane" in text
    assert "broker" in text


def test_npc_quest_roles_includes_broker():
    world = load_world()
    roles = npc_quest_roles(world)
    assert "broker" in roles
    quest_ids = {entry.quest_id for entry in roles["broker"]}
    assert "broker_rumor" in quest_ids
    assert "dock_watch" in quest_ids


def test_scaffold_yaml_structure():
    text = scaffold_quest_yaml(
        "test_scaffold",
        giver="broker",
        complete="broker",
        stages=[("visit_room", "docks"), ("talk_npc", "broker")],
        name_zh="測試",
        reward_gold=10,
    )
    raw = yaml.safe_load(text)
    data = raw["test_scaffold"]
    assert data["npc_id"] == "broker"
    assert data["complete_npc_id"] == "broker"
    assert len(data["stages"]) == 2
    assert data["stages"][0]["objective_target"] == "docks"