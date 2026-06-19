from __future__ import annotations

import random

_ART_POOL = (
    r"""
 ███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗     ██████╗██╗████████╗██╗   ██╗
 ████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝    ██╔════╝██║╚══██╔══╝╚██╗ ██╔╝
 ██╔██╗ ██║██║██║  ███╗███████║   ██║       ██║     ██║   ██║    ╚████╔╝
 ██║╚██╗██║██║██║   ██║██╔══██║   ██║       ██║     ██║   ██║     ╚██╔╝
 ██║ ╚████║██║╚██████╔╝██║  ██║   ██║       ╚██████╗██║   ██║      ██║
 ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝        ╚═════╝╚═╝   ╚═╝      ╚═╝
""".strip("\n"),
    r"""
    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
    █  ◈ N E U R A L   L I N K   //  N I G H T   C I T Y  ◈                  █
    █  ═══════════════════════════════════════════════════════════════════   █
    █  >> jack in. leave meat behind.                                        █
    ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
""".strip("\n"),
    r"""
      ╔═══════════════════════════════════════╗
      ║  ┌─┐┬┌─┐┬ ┬┌─┐┬  ┬┌─┐  ┬  ┬┌─┐┬┬─┐┬ ┬   ║
      ║  │ │├┤ │││├┤ │  │││  │  │├─┤│├┬┘└┬┘   ║
      ║  └─┘┴ └─┘└┴┘└─┘┴─┘┴ ┴  ┴─┘┴┴ ┴┴└─ ┴    ║
      ║       [ CYBER_MUD // EDGERUNNER ]       ║
      ╚═══════════════════════════════════════╝
""".strip("\n"),
    r"""
    ░▒▓█ NEURAL INTERFACE █▓▒░
         ╱╲    ╱╲    ╱╲
        ╱  ╲  ╱  ╲  ╱  ╲
       ╱ ◈  ╲╱ ◈  ╲╱ ◈  ╲
      ═══════════════════════
       N I G H T   C I T Y
      ═══════════════════════
""".strip("\n"),
    r"""
     █▀▀ █ █▀▀ █▀▀ ▀█▀ █   █▀█ █▀▀
     █▄▄ █ █▀  ██▄  █  █▄▄ █▄█ █▄█
           ◈ cyber_mud ◈
""".strip("\n"),
)


def render_login_art(max_lines: int, *, rng: random.Random | None = None) -> str:
    """Pick random ASCII art and fit to exactly max_lines (half terminal height)."""
    if max_lines < 3:
        return "◈ cyber_mud"

    source = random.choice(_ART_POOL) if rng is None else rng.choice(_ART_POOL)
    core = source.splitlines()
    if len(core) > max_lines:
        start = (len(core) - max_lines) // 2
        core = core[start : start + max_lines]
    out = [""] * max_lines
    offset = (max_lines - len(core)) // 2
    for index, line in enumerate(core):
        out[offset + index] = line
    return "\n".join(out)