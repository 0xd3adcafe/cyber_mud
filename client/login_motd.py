from __future__ import annotations

from client.output_prefix import spinner_char
from shared.i18n import t, t_list

_FALLBACK_TIP_KEY = "client.motd_fallback"


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


def default_tips(locale: str = "en") -> list[str]:
    tips = [tip.strip() for tip in t_list(locale, "motd.tips") if str(tip).strip()]
    if tips:
        return tips
    return [tip.strip() for tip in t_list(locale, _FALLBACK_TIP_KEY) if str(tip).strip()]


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
    locale: str = "en",
    tips: list[str] | None = None,
    tip_index: int = 0,
    frame: int = 0,
) -> str:
    pool = tips or default_tips(locale)
    title = t(locale, "motd.title")
    if title == "motd.title":
        title = "◈ Night City Neural Link"
    subtitle = t(locale, "motd.subtitle")
    if subtitle == "motd.subtitle":
        subtitle = "NEURAL LINK · cyber_mud"
    if not pool:
        pool = default_tips(locale)
    tip = pool[tip_index % len(pool)]
    return format_login_banner(title, subtitle, tip, frame=frame)