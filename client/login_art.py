from __future__ import annotations

import random
from collections.abc import Callable

SceneFn = Callable[[int, int, random.Random, str], list[str]]

_TAGLINES = (
    ">> jack in. leave meat behind.",
    ">> neural link pending…",
    ">> welcome to the sprawl.",
    ">> chrome optional. attitude required.",
    ">> the city never sleeps.",
    ">> flatline is not an option.",
    ">> ghost in the shell, meat in the rain.",
    ">> connect. survive. disconnect.",
)

_MATRIX_CHARS = "ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱｭﾚﾀﾘ0123456789ABCDEF"

_TITLE_GLYPHS: dict[str, list[str]] = {
    "CYBER": [
        " ██████╗██╗   ██╗██████╗ ███████╗██████╗ ",
        "██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗",
        "██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝",
        "██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗",
        "╚██████╗   ██║   ██████╔╝███████╗██║  ██║",
        " ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝",
    ],
    "MUD": [
        "███╗   ███╗██╗   ██╗██████╗ ",
        "████╗ ████║██║   ██║██╔══██╗",
        "██╔████╔██║██║   ██║██║  ██║",
        "██║╚██╔╝██║██║   ██║██║  ██║",
        "██║ ╚═╝ ██║╚██████╔╝██████╔╝",
        "╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ",
    ],
    "NIGHT": [
        "███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗",
        "████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝",
        "██╔██╗ ██║██║██║  ███╗███████║   ██║   ",
        "██║╚██╗██║██║██║   ██║██╔══██║   ██║   ",
        "██║ ╚████║██║╚██████╔╝██║  ██║   ██║   ",
        "╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ",
    ],
}

_THEME_SCENE_BIAS: dict[str, tuple[str, ...]] = {
    "night_city": ("skyline", "neon_gate", "neural_web", "orbital"),
    "blade_runner": ("skyline", "neon_gate", "rain_billboard"),
    "matrix": ("matrix_rain", "neon_gate"),
    "mr_robot": ("terminal_eye", "hex_stream"),
    "hackernet": ("neural_web", "hex_stream", "node_map"),
    "ready_player_one": ("pixel_coin", "neon_gate", "skyline"),
    "tron": ("tron_grid", "circuit_run"),
    "ctos": ("neural_web", "node_map", "hex_stream"),
    "dedsec": ("neon_gate", "skyline", "hex_stream"),
    "profiler": ("node_map", "neural_web", "terminal_eye"),
}


def _make_canvas(width: int, height: int) -> list[list[str]]:
    return [[" "] * width for _ in range(height)]


def _canvas_to_lines(canvas: list[list[str]]) -> list[str]:
    return ["".join(row).rstrip() for row in canvas]


def _pad_lines(lines: list[str], width: int, height: int) -> list[str]:
    if not lines:
        return [" " * width] * height
    out = [line[:width].ljust(width) for line in lines[:height]]
    while len(out) < height:
        out.append(" " * width)
    return out[:height]


def _blit(canvas: list[list[str]], x: int, y: int, sprite: list[str]) -> None:
    height = len(canvas)
    width = len(canvas[0]) if canvas else 0
    for dy, row in enumerate(sprite):
        cy = y + dy
        if cy < 0 or cy >= height:
            continue
        for dx, ch in enumerate(row):
            cx = x + dx
            if 0 <= cx < width and ch != " ":
                canvas[cy][cx] = ch


def _center_blit(canvas: list[list[str]], sprite: list[str], y: int) -> None:
    if not canvas:
        return
    width = len(canvas[0])
    sprite_w = max(len(line) for line in sprite) if sprite else 0
    x = max(0, (width - sprite_w) // 2)
    _blit(canvas, x, y, sprite)


def _gradient_row(width: int, left: str, mid: str, right: str) -> str:
    if width <= 2:
        return mid * width
    third = max(1, width // 3)
    center = width - third * 2
    return left * third + mid * center + right * third


def _scene_skyline(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    ground = height - 1
    x = 0
    while x < width:
        building_w = rng.randint(3, max(4, width // 10))
        building_h = rng.randint(max(3, height // 5), max(4, height * 2 // 3))
        top = ground - building_h
        for row in range(top, ground + 1):
            ch = "█" if row < ground else "▄"
            line = ch * building_w
            _blit(canvas, x, row, [line])
        for _ in range(rng.randint(1, building_w)):
            wx = x + rng.randint(0, max(0, building_w - 1))
            wy = rng.randint(top + 1, ground - 1)
            if 0 <= wy < height and 0 <= wx < width:
                canvas[wy][wx] = rng.choice("░▒▓◈")
        x += building_w + rng.randint(0, 2)
    glow_y = max(0, ground - height * 2 // 3)
    for col in range(width):
        canvas[glow_y][col] = rng.choice("·:═─")
    _center_blit(canvas, _TITLE_GLYPHS["NIGHT"][: min(6, height // 2)], max(0, height // 8))
    tag = rng.choice(_TAGLINES)
    _center_blit(canvas, [tag[:width]], height - 2)
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_neon_gate(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    frame_top = "▄" + "▀" * max(0, width - 2) + "▄"
    frame_mid = "█" + " " * max(0, width - 2) + "█"
    frame_bot = "▀" + "▄" * max(0, width - 2) + "▀"
    _blit(canvas, 0, 0, [frame_top])
    for row in range(1, height - 1):
        _blit(canvas, 0, row, [frame_mid])
    _blit(canvas, 0, height - 1, [frame_bot])
    inner_h = max(6, height - 4)
    title = _TITLE_GLYPHS["CYBER"][: min(6, inner_h // 2)]
    subtitle = _TITLE_GLYPHS["MUD"][: min(6, inner_h // 2)]
    y = max(1, (height - len(title) - len(subtitle) - 2) // 2)
    _center_blit(canvas, title, y)
    _center_blit(canvas, subtitle, y + len(title) + 1)
    pulse_y = height - 2
    pulse = _gradient_row(width - 4, "░", "▒", "░")
    _blit(canvas, 2, pulse_y, [pulse])
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_matrix_rain(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    for col in range(width):
        start = rng.randint(-height, 0)
        length = rng.randint(max(3, height // 4), height)
        for row in range(height):
            idx = row - start
            if 0 <= idx < length:
                canvas[row][col] = rng.choice(_MATRIX_CHARS)
            if idx == length - 1:
                canvas[row][col] = rng.choice("ABCDEF0123456789")
    banner = rng.choice(("FOLLOW THE WHITE RABBIT", "WAKE UP", "THE MATRIX HAS YOU"))
    _center_blit(canvas, [banner[:width]], max(0, height // 2 - 1))
    _center_blit(canvas, ["◈ NIGHT CITY ◈"], max(0, height // 2 + 1))
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_tron_grid(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    horizon = height // 2
    for row in range(horizon, height):
        t = (row - horizon) / max(1, height - horizon - 1)
        spread = int(t * width * 0.45)
        center = width // 2
        left = max(0, center - spread)
        right = min(width - 1, center + spread)
        for col in range(left, right + 1):
            canvas[row][col] = "─" if col not in (left, right) else "┼"
    for col in range(0, width, max(4, width // 16)):
        for row in range(horizon):
            canvas[row][col] = "│"
    cycle_y = horizon + rng.randint(1, max(1, height - horizon - 2))
    _blit(canvas, 2, cycle_y, ["▄▄▄████▄▄▄"])
    _center_blit(canvas, ["╔═ TRON GRID ═╗"], 1)
    _center_blit(canvas, _TITLE_GLYPHS["CYBER"][:4], max(2, horizon // 4))
    tag = rng.choice(_TAGLINES)
    _center_blit(canvas, [tag[:width]], height - 2)
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_neural_web(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    node_count = max(5, min(12, (width * height) // 80))
    nodes: list[tuple[int, int]] = []
    for _ in range(node_count):
        nodes.append((rng.randint(2, width - 3), rng.randint(2, height - 3)))
    for x1, y1 in nodes:
        for x2, y2 in nodes:
            if (x1, y1) == (x2, y2):
                continue
            if rng.random() < 0.12:
                _draw_line(canvas, x1, y1, x2, y2, rng.choice("─│╱╲"))
    for x, y in nodes:
        canvas[y][x] = rng.choice("◈●○◎")
    _center_blit(canvas, ["░▒▓ NEURAL WEB ▓▒░"], 1)
    _center_blit(canvas, _TITLE_GLYPHS["MUD"][:4], max(2, height // 2 - 2))
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _draw_line(canvas: list[list[str]], x0: int, y0: int, x1: int, y1: int, ch: str) -> None:
    dx = 1 if x1 >= x0 else -1
    dy = 1 if y1 >= y0 else -1
    x, y = x0, y0
    height = len(canvas)
    width = len(canvas[0])
    while True:
        if 0 <= y < height and 0 <= x < width and canvas[y][x] == " ":
            canvas[y][x] = ch
        if x == x1 and y == y1:
            break
        if x != x1:
            x += dx
        elif y != y1:
            y += dy


def _scene_rain_billboard(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    for _ in range(width * height // 6):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        canvas[y][x] = rng.choice("│╱╲·")
    box_w = min(width - 4, 48)
    box_h = min(height - 4, 10)
    bx = (width - box_w) // 2
    by = (height - box_h) // 2
    _blit(canvas, bx, by, ["╔" + "═" * (box_w - 2) + "╗"])
    for row in range(1, box_h - 1):
        _blit(canvas, bx, by + row, ["║" + " " * (box_w - 2) + "║"])
    _blit(canvas, bx, by + box_h - 1, ["╚" + "═" * (box_w - 2) + "╝"])
    _center_blit(canvas, ["◈ NIGHT CITY ◈"], by + 2)
    _center_blit(canvas, [rng.choice(_TAGLINES)[: box_w - 4]], by + 4)
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_terminal_eye(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    eye = [
        "    ╭──────────╮    ",
        "  ╱   ░░░░░░░░   ╲  ",
        " │    ▓▓▓▓▓▓▓▓    │ ",
        " │     ██████     │ ",
        " │      ◈◈◈      │ ",
        " │     ██████     │ ",
        "  ╲   ░░░░░░░░   ╱  ",
        "    ╰──────────╯    ",
    ]
    _center_blit(canvas, eye, max(1, height // 2 - len(eye) // 2))
    _center_blit(canvas, ["[ fsociety ]"], 1)
    _center_blit(canvas, [rng.choice(_TAGLINES)[:width]], height - 2)
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_hex_stream(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    for row in range(height):
        chunks = []
        pos = 0
        while pos < width:
            if rng.random() < 0.15 and pos + 8 < width:
                chunks.append(rng.choice(("0x", ">>", "//", "@@")))
                pos += 2
            else:
                chunks.append(rng.choice("0123456789ABCDEFabcdef"))
                pos += 1
        line = "".join(chunks)[:width]
        _blit(canvas, 0, row, [line])
    _center_blit(canvas, ["┌─ INTRUSION DETECTED ─┐"], max(1, height // 4))
    _center_blit(canvas, _TITLE_GLYPHS["CYBER"][:4], max(2, height // 2 - 2))
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_node_map(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    hubs = [(width // 4, height // 2), (width * 3 // 4, height // 2), (width // 2, height // 4)]
    for hx, hy in hubs:
        label = f"[{rng.randint(10, 99):02x}]"
        _blit(canvas, hx - len(label) // 2, hy, [label])
        canvas[hy][hx] = "◈"
    for hx, hy in hubs:
        _draw_line(canvas, hx, hy, width // 2, height * 3 // 4, "═")
    _center_blit(canvas, ["HACKERNET // NODE MAP"], 1)
    _center_blit(canvas, [rng.choice(_TAGLINES)[:width]], height - 2)
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_pixel_coin(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    coin = [
        "  ████████████  ",
        " ██████████████ ",
        " ████░░░░░░████ ",
        " ███░▓▓▓▓▓░████ ",
        " ███░▓◈◈◈▓░████ ",
        " ███░▓▓▓▓▓░████ ",
        " ████░░░░░░████ ",
        " ██████████████ ",
        "  ████████████  ",
    ]
    _center_blit(canvas, coin, max(1, height // 2 - len(coin) // 2))
    _center_blit(canvas, ["▶ READY PLAYER ◀"], 1)
    _center_blit(canvas, ["HIGH SCORE: NIGHT CITY"], height - 2)
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_circuit_run(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    for row in range(0, height, 2):
        line = []
        x = 0
        while x < width:
            seg = rng.choice(("───", "─┴─", "─┬─", "═══"))
            line.append(seg)
            x += len(seg)
        _blit(canvas, 0, row, ["".join(line)[:width]])
    _center_blit(canvas, ["╱╲ CIRCUIT RUN ╱╲"], 1)
    _center_blit(canvas, _TITLE_GLYPHS["MUD"][:4], max(2, height // 3))
    return _pad_lines(_canvas_to_lines(canvas), width, height)


def _scene_orbital(width: int, height: int, rng: random.Random, _theme: str) -> list[str]:
    canvas = _make_canvas(width, height)
    cx, cy = width // 2, height // 2
    radius = min(width, height) // 3
    for angle_step in range(radius * 4):
        t = angle_step / (radius * 4)
        rx = int(cx + radius * 1.4 * (t - 0.5))
        ry = int(cy + radius * 0.35 * (0.5 - abs(t - 0.5) * 2))
        if 0 <= ry < height and 0 <= rx < width:
            canvas[ry][rx] = rng.choice("·°○●◈")
    _center_blit(canvas, ["◈ ORBITAL VIEW ◈"], max(0, cy - radius - 2))
    _center_blit(canvas, [rng.choice(_TAGLINES)[:width]], min(height - 2, cy + radius + 1))
    return _pad_lines(_canvas_to_lines(canvas), width, height)


_SCENES: dict[str, SceneFn] = {
    "skyline": _scene_skyline,
    "neon_gate": _scene_neon_gate,
    "matrix_rain": _scene_matrix_rain,
    "tron_grid": _scene_tron_grid,
    "neural_web": _scene_neural_web,
    "rain_billboard": _scene_rain_billboard,
    "terminal_eye": _scene_terminal_eye,
    "hex_stream": _scene_hex_stream,
    "node_map": _scene_node_map,
    "pixel_coin": _scene_pixel_coin,
    "circuit_run": _scene_circuit_run,
    "orbital": _scene_orbital,
}


def _scene_names_for_theme(theme_id: str) -> tuple[str, ...]:
    bias = _THEME_SCENE_BIAS.get(theme_id)
    if bias:
        return bias
    return tuple(_SCENES.keys())


def _pick_scene(theme_id: str, rng: random.Random) -> SceneFn:
    name = rng.choice(_scene_names_for_theme(theme_id))
    return _SCENES[name]


def scene_for_carousel(theme_id: str, index: int) -> SceneFn:
    names = _scene_names_for_theme(theme_id)
    return _SCENES[names[index % len(names)]]


def render_login_art(
    max_lines: int,
    *,
    max_width: int = 80,
    theme_id: str = "night_city",
    rng: random.Random | None = None,
    scene_index: int | None = None,
) -> str:
    """Procedurally compose login art that fills the upper terminal half."""
    width = max(40, max_width)
    height = max(6, max_lines)
    if height < 3:
        return "◈ cyber_mud".center(width)[:width]

    picker = rng or random.Random()
    if scene_index is not None:
        scene = scene_for_carousel(theme_id, scene_index)
    else:
        scene = _pick_scene(theme_id, picker)
    lines = scene(width, height, picker, theme_id)
    return "\n".join(_pad_lines(lines, width, height))