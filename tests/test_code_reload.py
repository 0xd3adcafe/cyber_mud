from commands.registry import _REGISTRY, dispatch
from server.code_reload import iter_code_files, reload_application_code, snapshot_code_mtimes
from tests.conftest import make_player, make_state


def test_iter_code_files_includes_commands():
    paths = {path.as_posix() for path in iter_code_files()}
    assert any(path.endswith("commands/look.py") for path in paths)


def test_snapshot_code_mtimes_matches_files():
    mtimes = snapshot_code_mtimes()
    assert mtimes
    assert all(path.exists() for path in mtimes)


def test_reload_application_code_restores_registry():
    player, state = make_player(), make_state()
    before = len(_REGISTRY)
    failures = reload_application_code()
    assert len(_REGISTRY) == before
    assert failures == []
    result = dispatch("look", player, state, [], [])
    assert any("霓虹廣場" in line for line in result.lines)