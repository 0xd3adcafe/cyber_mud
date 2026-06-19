import random

from client.auth_ui import build_auth_command, mask_auth_log_line
from client.login_art import render_login_art


def test_render_login_art_exact_height():
    art = render_login_art(12)
    assert len(art.split("\n")) == 12


def test_render_login_art_fills_width_and_height():
    width = 80
    height = 16
    art = render_login_art(height, max_width=width, rng=random.Random(42))
    lines = art.split("\n")
    assert len(lines) == height
    assert all(len(line) == width for line in lines)
    assert any("█" in line or "◈" in line or "N" in line for line in lines)


def test_render_login_art_theme_bias():
    matrix_art = render_login_art(14, max_width=70, theme_id="matrix", rng=random.Random(1))
    tron_art = render_login_art(14, max_width=70, theme_id="tron", rng=random.Random(1))
    assert matrix_art != tron_art


def test_render_login_art_random_variety():
    rng = random.Random(0)
    samples = {render_login_art(12, max_width=60, rng=rng) for _ in range(40)}
    assert len(samples) >= 8


def test_build_auth_command():
    assert build_auth_command("login", "V", "secret") == "login V secret"
    assert build_auth_command("register", "V", "secret") == "register V secret"
    assert build_auth_command("login", "", "x") is None
    assert build_auth_command("hack", "V", "x") is None


def test_mask_auth_log_hides_password():
    line = mask_auth_log_line("login", "Runner")
    assert "Runner" in line
    assert "secret" not in line
    assert "隱藏" in line