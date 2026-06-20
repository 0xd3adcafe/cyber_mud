from __future__ import annotations

from client.output_prefix import spinner_char
from shared.i18n import t, t_list

_FALLBACK_TIPS = (
    "建立連線中…請 register 或 login。",
    "登入後輸入 look 探索，go <方向> 移動。",
    "Tab 補全指令 · F2–F6 開啟側欄。",
    "輸入 help 查看指令 · /theme 切換視覺主題。",
)


def is_motd_separator(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    return all(ch in "═=-─━ " for ch in stripped)


def parse_motd_line(line: str, *, title: str = "") -> str | None:
    text = line.strip()
    if is_motd_separator(text):
        return None
    if title and text == title.strip():
        return None
    return text


def default_tips(locale: str = "zh") -> list[str]:
    tips = [tip.strip() for tip in t_list(locale, "motd.tips") if str(tip).strip()]
    if tips:
        return tips
    return list(_FALLBACK_TIPS)


def merge_tips(base: list[str], extra: list[str]) -> list[str]:
    merged = list(base)
    seen = set(merged)
    for line in extra:
        text = line.strip()
        if not text or text in seen:
            continue
        merged.append(text)
        seen.add(text)
    return merged


def format_login_banner(
    title: str,
    subtitle: str,
    tip: str,
    *,
    frame: int = 0,
) -> str:
    spin = spinner_char(frame)
    return (
        f"[bold]{title}[/]\n"
        f"[dim]{subtitle}[/]\n"
        f"[cyan]{spin}[/] [italic]{tip}[/]"
    )


def banner_text(
    *,
    locale: str = "zh",
    tips: list[str] | None = None,
    tip_index: int = 0,
    frame: int = 0,
) -> str:
    pool = tips or default_tips(locale)
    if not pool:
        pool = list(_FALLBACK_TIPS)
    title = t(locale, "motd.title")
    if title == "motd.title":
        title = "◈ 夜城神經連結"
    subtitle = t(locale, "motd.subtitle")
    if subtitle == "motd.subtitle":
        subtitle = "NEURAL LINK · cyber_mud"
    tip = pool[tip_index % len(pool)]
    return format_login_banner(title, subtitle, tip, frame=frame)