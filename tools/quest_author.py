#!/usr/bin/env python3
"""NPC quest authoring CLI — validate, outline, and scaffold multi-NPC quest scripts."""

from __future__ import annotations

import argparse
import sys

from world.loader import load_world
from world.quest_author import (
    format_npc_quest_report,
    format_quest_list_line,
    format_quest_outline,
    scaffold_quest_yaml,
    validate_quests,
)


def _parse_stage(value: str) -> tuple[str, str]:
    kind, sep, target = value.partition(":")
    if not sep or not kind.strip() or not target.strip():
        raise argparse.ArgumentTypeError(
            f"stage 格式應為 type:target（如 talk_npc:broker），收到：{value!r}"
        )
    return kind.strip(), target.strip()


def cmd_list(world) -> int:
    print(f"任務清單（{len(world.quests)}）")
    for quest in sorted(world.quests.values(), key=lambda q: q.id):
        print(format_quest_list_line(quest, world))
    return 0


def cmd_show(world, quest_id: str) -> int:
    quest = world.quest(quest_id)
    if quest is None:
        print(f"ERR: 任務不存在：{quest_id}")
        return 1
    print(format_quest_outline(quest, world))
    return 0


def cmd_validate(world) -> int:
    issues = validate_quests(world)
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warn"]
    for issue in warnings:
        print(f"WARN [{issue.quest_id}] {issue.message}")
    for issue in errors:
        print(f"ERR  [{issue.quest_id}] {issue.message}")
    if errors:
        print(f"FAIL: {len(errors)} 個錯誤、{len(warnings)} 個警告")
        return 1
    print(f"OK: {len(world.quests)} 個任務通過驗證（{len(warnings)} 個警告）")
    return 0


def cmd_npc(world, npc_id: str) -> int:
    print(format_npc_quest_report(world, npc_id))
    return 0 if world.npc(npc_id) is not None else 1


def cmd_scaffold(args: argparse.Namespace) -> int:
    text = scaffold_quest_yaml(
        args.quest_id,
        giver=args.giver,
        complete=args.complete,
        stages=args.stage,
        name_zh=args.name_zh,
        name_en=args.name_en,
        street_cred_req=args.street_cred_req,
        reward_gold=args.reward_gold,
        reward_xp=args.reward_xp,
        reward_street_cred=args.reward_street_cred,
    )
    sys.stdout.write(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NPC 任務編排工具")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="列出所有任務摘要")
    show = sub.add_parser("show", help="顯示任務劇本大綱")
    show.add_argument("quest_id")

    sub.add_parser("validate", help="驗證任務資料與世界引用")

    npc = sub.add_parser("npc", help="顯示 NPC 參與的任務角色")
    npc.add_argument("npc_id")

    scaffold = sub.add_parser("scaffold", help="輸出多階段任務 YAML 範本")
    scaffold.add_argument("quest_id")
    scaffold.add_argument("--giver", required=True, help="發佈 NPC id")
    scaffold.add_argument("--complete", required=True, help="交件 NPC id")
    scaffold.add_argument(
        "--stage",
        action="append",
        default=[],
        type=_parse_stage,
        help="階段：talk_npc:broker / visit_room:docks / interact:obj_id",
    )
    scaffold.add_argument("--name-zh", default="TODO 任務名稱")
    scaffold.add_argument("--name-en", default="TODO Quest Name")
    scaffold.add_argument("--street-cred-req", type=int, default=0)
    scaffold.add_argument("--reward-gold", type=int, default=0)
    scaffold.add_argument("--reward-xp", type=int, default=0)
    scaffold.add_argument("--reward-street-cred", type=int, default=0)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scaffold":
        if not args.stage:
            print("ERR: scaffold 至少需要一個 --stage")
            return 1
        return cmd_scaffold(args)

    world = load_world()
    if args.command == "list":
        return cmd_list(world)
    if args.command == "show":
        return cmd_show(world, args.quest_id)
    if args.command == "validate":
        return cmd_validate(world)
    if args.command == "npc":
        return cmd_npc(world, args.npc_id)
    parser.error(f"unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())