from __future__ import annotations

import re

from client.mature_format import is_mature_marker_line
from shared.protocol import ERR_PREFIX, MOTD_PREFIX, SYS_PREFIX

LOG_KINDS = frozenset(
    {
        "motd",
        "sys",
        "err",
        "echo",
        "combat",
        "quest",
        "social",
        "progression",
        "ambient",
        "env_move",
        "env",
        "mature",
        "text",
    }
)

_HEADER_MARK = "◈"
_SCAN_MARKERS = ("掃描", "Scan")
_ENTITY_PREFIXES = (
    "出口：",
    "Exits:",
    "地上：",
    "On the ground:",
    "物品：",
    "Items:",
    "這裡有：",
    "Here:",
    "人物：",
    "People:",
    "屍體：",
    "Corpses:",
    "玩家：",
    "Player:",
    "天氣：",
    "Weather:",
    "隱藏",
    "Hidden clue",
)

_COMBAT_MARKERS = (
    " damage (",
    " 傷害（",
    " strikes back",
    " 反擊",
    "Quickhack",
    "快速破解",
    "→",
    "engage ",
    "發起攻擊",
    "cooldown",
    "冷卻",
    "escape combat",
    "脫離了戰鬥",
    "left the area—combat",
    "離開了戰場",
    "You drop ",
    "你擊倒了",
    "go down",
    "你倒下了",
    "fled from combat",
    "從與",
    "的戰鬥中逃脫",
    "was dropped by",
    "was dropped",
    "擊倒了",
    "draw a bead",
    "舉槍瞄準",
    "slash at",
    "揮刀撲向",
    "square up",
    "拳擊架勢",
    "slip behind",
    "潛向",
    "brace for impact",
    "舉盾防禦",
    "burns for",
    "灼燒中",
    "shorts out",
    "義體短路",
    "overheat debuff",
    "過熱",
)

_QUEST_MARKERS = (
    "Objective complete",
    "目標達成",
    "Gig progress",
    "委託進度",
    "Gig complete",
    "委託完成",
    "Return to",
    "回去找",
    "Obtain ",
    "取得 ",
    "Defeat ",
    "擊倒 ",
    "Go to ",
    "前往 ",
)

_PROGRESSION_MARKERS = (
    "XP.",
    "經驗",
    "Level up",
    "升級",
    "Street cred",
    "街頭聲望",
    "Proficiency",
    "熟練度",
    "perk point",
    "天賦點",
    "attribute point",
    "屬性點",
    "Street rep shifts",
    "街頭聲望變動",
    "聲望變動",
)

_SOCIAL_MARKERS = (
    " says:",
    "說：",
    "You say:",
    "你說",
    " enters.",
    " leaves.",
    " says:",
    "進入了。",
    "離開了。",
    "You say:",
    "你說：",
)

_AMBIENT_MARKERS = (
    "NCPD drones",
    "NCPD 無人機",
    "Acid rain hisses",
    "酸雨在路面",
    "Smuggler cranes",
    "走私起重機",
    "Corporate PA",
    "企業廣播",
    "Neon bass",
    "霓虹低音",
    "sample drone",
    "樣本無人機",
    "Incense smoke",
    "線香煙",
    "Water drips",
    "積水滴滴",
    "Distant gunfire",
    "遠處槍聲",
    "Night City never sleeps",
    "夜之城從不睡眠",
    "Blood loss:",
    "失血：",
    "Toxin damage",
    "毒素傷害",
)

_MOVE_RE = re.compile(r"^(You go |你前往 )")


def _strip_rich(text: str) -> str:
    return re.sub(r"\[/?[^\]]+\]", "", text).strip()


_EXPLICIT_KINDS = frozenset({"echo", "err", "sys"})


def classify_log_line(line: str, *, kind: str | None = None) -> str:
    if kind in _EXPLICIT_KINDS:
        return kind

    plain = _strip_rich(line)
    if not plain:
        return "text"

    lower = plain.lower()

    if plain.startswith(MOTD_PREFIX) or plain.startswith(_HEADER_MARK):
        if any(marker in plain for marker in _SCAN_MARKERS):
            return "env"
        for marker in _QUEST_MARKERS:
            if marker in plain:
                return "quest"
        for marker in _PROGRESSION_MARKERS:
            if marker in plain or marker.lower() in lower:
                return "progression"
        if "Growth" in plain or "成長" in plain or "Talents" in plain or "天賦" in plain:
            return "progression"
        return "env"
    if plain.startswith(SYS_PREFIX):
        return "sys"
    if plain.startswith(ERR_PREFIX):
        return "err"

    if _MOVE_RE.match(plain):
        return "env_move"

    if is_mature_marker_line(plain):
        return "mature"

    for marker in _PROGRESSION_MARKERS:
        if marker.lower() in lower or marker in plain:
            return "progression"

    for marker in _QUEST_MARKERS:
        if marker in plain:
            return "quest"

    for marker in _AMBIENT_MARKERS:
        if marker in plain:
            return "ambient"

    for marker in _SOCIAL_MARKERS:
        if marker in plain:
            return "social"

    for marker in _COMBAT_MARKERS:
        if marker in plain:
            return "combat"

    if plain.startswith(_HEADER_MARK) or any(marker in plain for marker in _SCAN_MARKERS):
        return "env"
    if any(plain.startswith(prefix) for prefix in _ENTITY_PREFIXES):
        return "env"
    if "Client commands:" in plain or "本機指令" in plain:
        return "sys"

    return "text"