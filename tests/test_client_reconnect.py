from client.auth_ui import build_resume_command
from client.reconnect import reconnect_status_message, should_resend_auth


def test_should_resend_auth_when_needs_reauth():
    assert should_resend_auth(needs_reauth=True, authenticated=True, last_auth_line="login a b")


def test_should_resend_auth_when_not_authenticated():
    assert should_resend_auth(needs_reauth=False, authenticated=False, last_auth_line="login a b")


def test_should_not_resend_without_last_line():
    assert not should_resend_auth(needs_reauth=True, authenticated=True, last_auth_line="")


def test_should_resend_resume_token_line():
    assert should_resend_auth(
        needs_reauth=True,
        authenticated=True,
        last_auth_line="resume abc.def.ghi",
    )


def test_build_resume_command():
    assert build_resume_command("abc.def") == "resume abc.def"
    assert build_resume_command("  ") is None


def test_reconnect_status_message():
    assert "第 1 次" in reconnect_status_message(attempt=1, delay=1.0, max_attempts=5)
    assert reconnect_status_message(attempt=5, delay=16.0, max_attempts=5) is not None
    assert reconnect_status_message(attempt=6, delay=30.0, max_attempts=5) == "重連失敗（已達 5 次）。"