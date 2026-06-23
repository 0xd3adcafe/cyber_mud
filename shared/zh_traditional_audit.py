from __future__ import annotations

import difflib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# Taiwan game copy: keep these forms even when OpenCC prefers alternatives.
_TW_GAME_TERM_FIXES: tuple[tuple[str, str], ...] = (
    ("揹包", "背包"),
    ("幹擾", "干擾"),
    ("干扰", "干擾"),
    ("臺詞", "台詞"),
    ("櫃臺", "櫃台"),
)


@dataclass(frozen=True)
class ZhAuditIssue:
    severity: str
    path: str
    message: str


def _has_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


@lru_cache(maxsize=1)
def _opencc_s2tw():
    from opencc import OpenCC

    return OpenCC("s2tw")


def normalize_tw_text(text: str) -> str:
    """Convert simplified forms to Taiwan Traditional; preserve game-term preferences."""
    if not _has_cjk(text):
        return text
    converted = _opencc_s2tw().convert(text)
    for src, dst in _TW_GAME_TERM_FIXES:
        converted = converted.replace(src, dst)
    return converted


# Simplified-only characters (GB2312 forms absent from standard TW usage).
_SIMPLIFIED_ONLY_CHARS = frozenset(
    "这们说过发现应经进择认设显连统误删创检验执运闭击输滤复贴编览载传败"
    "标类状数价邮账录专报图链签单钮块扩样话弹处妆辉环笔锁买闪齐哔语庙"
    "压装决东钥余烬绕电义丰饶喂养跃汇骇听动宠兽静嚣寻腾壳旧谨稀灵选谎"
    "贯湿诱妈结场划磨骑喘鸡丝顶脏饥剥拽帘书"
)

_SIMPLIFIED_PARTICLE_PATTERNS: tuple[str, ...] = (
    "藏着",
    "贴着",
    "晕着",
    "挂着",
    "绕着",
    "听着",
    "看着",
    "等着",
    "睡着",
    "笑着",
)

_SIMPLIFIED_PHRASE_PATTERNS: tuple[str, ...] = (
    "书包",
    "划过",
    "湿吻",
    "喉结",
    "场关",
    "干到",
    "舞台妆",
    "环形灯",
    "样本箱",
    "压低声音",
    "装受害者",
    "聊天是公开",
    "折叠床",
    "小声点",
    "轻声数拍",
    "房租日神圣",
    "家里的事",
    "东边求运",
    "动能",
    "义体",
    "喂养",
    "账目会平",
    "已经湿透",
    "骑我大腿",
    "场后用手指",
    "上湿了一道",
    "坐上你的鸡巴",
)


def needs_traditional_fix(text: str) -> bool:
    if not _has_cjk(text):
        return False
    if any(pattern in text for pattern in _SIMPLIFIED_PARTICLE_PATTERNS):
        return True
    if any(pattern in text for pattern in _SIMPLIFIED_PHRASE_PATTERNS):
        return True
    converter = _opencc_s2tw()
    converted = converter.convert(text)
    if converted == text:
        return False
    matcher = difflib.SequenceMatcher(None, text, converted)
    for op, i1, i2, _j1, _j2 in matcher.get_opcodes():
        if op in {"replace", "delete"}:
            chunk = text[i1:i2]
            if any(ch in _SIMPLIFIED_ONLY_CHARS for ch in chunk):
                return True
    return False


def untranslated_english_hits(text: str) -> list[str]:
    """Flag English prose left in zh mirrors (commands/placeholders are OK)."""
    markers = (
        " lands, ",
        "whispered:",
        "growled:",
        "Fade to black",
        "Fade implied",
        "Stage four",
        "Stage three",
        "quiet heat",
        "filthy heat",
        "Breath and shadow",
        "Pulse loud",
        "Bodies slam",
        "Measured glance",
        "Low voice",
        "Hungry look",
        "Closer—stage",
        "Do not stop",
        "makes me wet",
        "I felt it",
        "Time folds",
    )
    return [marker for marker in markers if marker in text]


def _walk_yaml_strings(
    node: Any,
    prefix: str,
    sink: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            _walk_yaml_strings(value, child, sink)
    elif isinstance(node, str):
        sink.append((prefix, node))
    return sink


def audit_yaml_strings(path: Path, *, label: str | None = None) -> list[ZhAuditIssue]:
    tag = label or str(path)
    if not path.exists():
        return [ZhAuditIssue("error", tag, f"missing locale file: {path}")]

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    issues: list[ZhAuditIssue] = []
    for key_path, text in _walk_yaml_strings(data, "", []):
        if needs_traditional_fix(text):
            issues.append(
                ZhAuditIssue(
                    "error",
                    f"{tag}:{key_path}",
                    "simplified or non-TW form in zh string",
                )
            )
        for marker in untranslated_english_hits(text):
            issues.append(
                ZhAuditIssue(
                    "error",
                    f"{tag}:{key_path}",
                    f"untranslated English marker {marker!r}",
                )
            )
    return issues


def audit_world_zh_fields(data_dir: Path | None = None) -> list[ZhAuditIssue]:
    root = data_dir or (REPO_ROOT / "data")
    issues: list[ZhAuditIssue] = []
    for path in sorted(root.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for key_path, text in _walk_world_zh_strings(data, path.stem, []):
            if needs_traditional_fix(text):
                issues.append(
                    ZhAuditIssue(
                        "error",
                        f"{path.name}:{key_path}",
                        "simplified or non-TW form in *_zh field",
                    )
                )
    return issues


def _walk_world_zh_strings(
    node: Any,
    prefix: str,
    sink: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            if key.endswith("_zh") and isinstance(value, str):
                sink.append((child, value))
            else:
                _walk_world_zh_strings(value, child, sink)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            _walk_world_zh_strings(item, f"{prefix}[{index}]", sink)
    return sink