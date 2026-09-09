"""Phase A env-file export pins for session_init's CLAUDE_ENV_FILE channel.

Pins the contract of ``session_init._persist_project_dir_env`` and its call
site in ``main()``:

- export written when BOTH $CLAUDE_ENV_FILE and $CLAUDE_PROJECT_DIR are present
- no-op when CLAUDE_ENV_FILE is unset (older platform versions fail open)
- no append when CLAUDE_PROJECT_DIR is unset (the structural guard: an
  env-absent frame's cwd-fallback value is never exported)
- producer-side shlex.quote for paths with spaces / ``$`` (the env file is
  sourced by a shell)
- re-fire dedupe: an identical export line is never appended twice
  (resume/compact/clear re-fires stay idempotent)
- exported == recorded invariant: the value appended to the env file is the
  same resolve-once value passed to build_context_cache (env verbatim when
  present; absolute cwd on the env-absent leg, never the retired "." default)

The main()-driven rows use the same injection-orthogonal stub set as
test_config_injection_both_modes.py — the env-file write happens at main()
top, before any stubbed collaborator runs.
"""
import io
import json
import os
import shlex
from pathlib import Path
from unittest.mock import patch

import pytest

import session_init

_PROJECT_DIR = "/Users/example/Sites/test-project"


def _run_main(monkeypatch, tmp_path, frame=None):
    """Drive real session_init.main() with heavy collaborators stubbed.
    Returns (stdout additionalContext, recorded project_dir captured from the
    build_context_cache call)."""
    recorded = {}

    def _capture_context_cache(*args, **kwargs):
        # build_context_cache(team_name, session_id, project_dir, plugin_root, ...)
        recorded["project_dir"] = args[2] if len(args) > 2 else kwargs.get("project_dir")
        return (Path("/tmp/ctx.json"), {})

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    stdin_data = json.dumps({"source": "startup", "session_id": "33334444-0000-0000-0000-000000000000", **(frame or {})})
    with patch("session_init.setup_plugin_symlinks", return_value=None), \
         patch("session_init.ensure_project_memory_md", return_value=None), \
         patch("session_init.check_pinned_staleness", return_value=None), \
         patch("session_init.get_task_list", return_value=None), \
         patch("session_init.restore_last_session", return_value=None), \
         patch("session_init.build_context_cache", side_effect=_capture_context_cache), \
         patch("session_init.persist_context", return_value=None), \
         patch("session_init.append_event"), \
         patch("session_init.update_session_info", return_value=None), \
         patch("session_init.check_resume_state", return_value=None), \
         patch("session_init._registry_resolve", return_value=None), \
         patch("session_init.get_peer_context", return_value=None), \
         patch("sys.stdin", io.StringIO(stdin_data)), \
         patch("sys.stdout", new_callable=io.StringIO):
        with pytest.raises(SystemExit) as exc:
            session_init.main()
    assert exc.value.code == 0
    return recorded.get("project_dir")


class TestEnvFileExport:
    """main()-driven contract rows (call-site gate + helper)."""

    def test_export_written_when_both_present(self, monkeypatch, tmp_path):
        env_file = tmp_path / "session-env.sh"  # deliberately not pre-created
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", _PROJECT_DIR)
        monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))
        recorded = _run_main(monkeypatch, tmp_path)
        assert env_file.read_text(encoding="utf-8") == (
            f"export CLAUDE_PROJECT_DIR={shlex.quote(_PROJECT_DIR)}\n"
        )
        assert recorded == _PROJECT_DIR

    def test_noop_when_env_file_unset(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", _PROJECT_DIR)
        monkeypatch.delenv("CLAUDE_ENV_FILE", raising=False)
        # No env-file channel -> clean no-op, exit 0, record side unaffected.
        recorded = _run_main(monkeypatch, tmp_path)
        assert recorded == _PROJECT_DIR

    def test_no_append_when_project_dir_unset(self, monkeypatch, tmp_path):
        env_file = tmp_path / "session-env.sh"
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))
        recorded = _run_main(monkeypatch, tmp_path)
        # Structural guard: env-absent frame never reaches the append...
        assert not env_file.exists() or "CLAUDE_PROJECT_DIR" not in env_file.read_text(encoding="utf-8")
        # ...and the record side gets the absolute cwd, never the retired "." default.
        assert recorded == os.getcwd()
        assert Path(recorded).is_absolute()

    def test_spacey_dollar_path_is_quoted(self, monkeypatch, tmp_path):
        spacey = "/Users/example/My Proj$ect/work"
        env_file = tmp_path / "session-env.sh"
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", spacey)
        monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))
        recorded = _run_main(monkeypatch, tmp_path)
        assert env_file.read_text(encoding="utf-8") == (
            f"export CLAUDE_PROJECT_DIR={shlex.quote(spacey)}\n"
        )
        assert recorded == spacey  # verbatim, not resolved


class TestPersistProjectDirEnvHelper:
    """Helper-level guards, exercised directly (no main() drive)."""

    def test_refire_dedupe_appends_nothing_twice(self, monkeypatch, tmp_path):
        env_file = tmp_path / "session-env.sh"
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", _PROJECT_DIR)
        monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))
        session_init._persist_project_dir_env(_PROJECT_DIR)
        session_init._persist_project_dir_env(_PROJECT_DIR)
        lines = env_file.read_text(encoding="utf-8").splitlines()
        assert lines == [f"export CLAUDE_PROJECT_DIR={shlex.quote(_PROJECT_DIR)}"]

    def test_non_absolute_value_skipped(self, monkeypatch, tmp_path):
        env_file = tmp_path / "session-env.sh"
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", _PROJECT_DIR)
        monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))
        session_init._persist_project_dir_env("relative/dir")
        assert not env_file.exists()

    def test_env_var_unset_skips_even_with_arg(self, monkeypatch, tmp_path):
        env_file = tmp_path / "session-env.sh"
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))
        session_init._persist_project_dir_env(_PROJECT_DIR)
        assert not env_file.exists()

    def test_env_file_unset_skips(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", _PROJECT_DIR)
        monkeypatch.delenv("CLAUDE_ENV_FILE", raising=False)
        session_init._persist_project_dir_env(_PROJECT_DIR)  # must not raise
