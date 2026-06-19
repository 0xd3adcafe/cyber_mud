import random

from client.auth_ui import build_auth_command, mask_auth_log_line
from client.login_art import render_login_art


def test_render_login_art_exact_height():
    art = render_login_art(12)
    assert len(art.split("\n")) == 12


def test_render_login_art_random_variety():
    rng = random.Random(0)
    samples = {render_login_art(8, rng=rng) for _ in range(30)}
    assert len(samples) >= 2


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