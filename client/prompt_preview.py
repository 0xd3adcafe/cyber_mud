from __future__ import annotations

from dataclasses import dataclass

from client.meta_handlers import ClientViewState
from shared.i18n import t
from shared.prompt_tokens import CP2077_TEMPLATES, DEFAULT_PROMPT, PROMPT_TOKENS


@dataclass(frozen=True)
class PromptEditContext:
    template: str
    kind: str


def detect_prompt_edit(text: str) -> PromptEditContext | None:
    stripped = text.strip()
    body = stripped[1:].strip() if stripped.startswith("/") else stripped
    lower = body.lower()
    if lower.startswith("prompt set "):
        template = body[11:]
        if not template.strip():
            return None
        return PromptEditContext(template=template, kind="set")
    if lower.startswith("prompt template "):
        name = body[16:].strip().split(maxsplit=1)[0] if body[16:].strip() else ""
        if not name:
            return None
        template = CP2077_TEMPLATES.get(name.lower())
        if template is None:
            return None
        return PromptEditContext(template=template, kind="template")
    return None


def expand_prompt_from_view(template: str, view: ClientViewState) -> str:
    locale = view.locale or "zh"
    faction = view.faction or t(locale, "prompt.faction_none")
    replacements = {
        "%n": view.player_name or "旅人",
        "%r": view.room or "—",
        "%h": view.hp or "—",
        "%t": view.time or "—",
        "%w": view.weather or "—",
        "%g": view.gold or "0",
        "%p": view.period or "—",
        "%f": faction,
        "%m": view.ram or "—",
        "%l": view.level or "1",
        "%c": view.street_cred or "0",
        "%v": view.wanted or "0",
        "%x": view.xp or "0/—",
    }
    result = template
    for token, value in replacements.items():
        result = result.replace(token, value)
    return result


def current_prompt_template(view: ClientViewState, *, local_override: str = "") -> str:
    if local_override.strip():
        return local_override
    if view.prompt_template.strip():
        return view.prompt_template
    return DEFAULT_PROMPT


def format_prompt_preview(template: str, expanded: str) -> str:
    return f"[dim]預覽[/] [bold cyan]{expanded}[/]  [dim]· {template}[/]"


def format_prompt_show_lines(view: ClientViewState, *, local_override: str = "") -> list[str]:
    locale = view.locale or "zh"
    template = current_prompt_template(view, local_override=local_override)
    expanded = expand_prompt_from_view(template, view)
    lines = [
        t(locale, "prompt.show_header"),
        t(locale, "prompt.template", template=template),
        t(locale, "prompt.expanded", expanded=expanded),
        "",
        t(locale, "prompt.tokens_header"),
    ]
    for token, desc_key in PROMPT_TOKENS.items():
        lines.append(
            t(
                locale,
                "prompt.token_line",
                token=token,
                desc=t(locale, desc_key),
            )
        )
    return lines