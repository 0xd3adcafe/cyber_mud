from client.reconnect import reconnect_status_message, should_resend_auth


def test_should_resend_auth_after_disconnect():
    assert should_resend_auth(needs_reauth=True, authenticated=True, last_auth_line="login V x")
    assert not should_resend_auth(needs_reauth=True, authenticated=True, last_auth_line="")


def test_should_resend_auth_on_login_screen():
    assert should_resend_auth(needs_reauth=False, authenticated=False, last_auth_line="login V x")
    assert not should_resend_auth(needs_reauth=False, authenticated=False, last_auth_line="")


def test_reconnect_status_message():
    assert "第 1 次" in reconnect_status_message(attempt=1, delay=1.0, max_attempts=5)
    assert reconnect_status_message(attempt=5, delay=16.0, max_attempts=5) is not None
    assert reconnect_status_message(attempt=6, delay=30.0, max_attempts=5) == "重連失敗（已達 5 次）。"