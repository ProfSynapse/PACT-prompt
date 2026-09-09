"""
Location: pact-plugin/tests/test_lint_check_help.py
Summary: Help, bare-refuse, and `--files` plus only help flags for lint-check.sh.
Used by: pytest suite. The --files last-line verdict contract stays in
         test_lint_check_files_mode.py; this file pins the teach prefix.
"""

import subprocess
from pathlib import Path

_SCRIPT = (
    Path(__file__).parent.parent
    / "skills"
    / "pact-coding-standards"
    / "scripts"
    / "lint-check.sh"
)


def _run(*argv):
    return subprocess.run(
        ["bash", str(_SCRIPT), *argv],
        capture_output=True,
        text=True,
    )


class TestLintCheckHelp:
    def test_help_long_exits_zero_with_examples_no_verdict(self):
        proc = _run("--help")
        assert proc.returncode == 0
        text = proc.stdout + proc.stderr
        assert "Examples:" in text
        assert "--files" in text
        assert "IMPORT-HYGIENE:" not in proc.stdout
        assert "IMPORT-HYGIENE:" not in proc.stderr
        assert "Running lint check in:" not in text

    def test_help_short_exits_zero(self):
        proc = _run("-h")
        assert proc.returncode == 0
        assert "Examples:" in (proc.stdout + proc.stderr)
        assert "IMPORT-HYGIENE:" not in proc.stdout

    def test_bare_run_exits_two_with_files_example_no_verdict(self):
        proc = _run()
        assert proc.returncode == 2
        assert "Examples:" in proc.stderr
        assert "--files" in proc.stderr
        assert ".py" in proc.stderr
        # Full example line, content-pinned: the pasteable unit itself, not
        # tokens that also occur in the usage/error lines above it.
        assert f"  {_SCRIPT} --files /abs/path/to/modified.py" in proc.stderr
        assert "IMPORT-HYGIENE:" not in proc.stdout
        assert "IMPORT-HYGIENE:" not in proc.stderr
        assert "Running lint check in:" not in proc.stdout

    def test_empty_directory_arg_refuses_like_bare_run(self):
        proc = _run("")
        assert proc.returncode == 2
        assert "Examples:" in proc.stderr
        assert "--files" in proc.stderr
        assert "IMPORT-HYGIENE:" not in proc.stdout
        assert "Running lint check in:" not in (proc.stdout + proc.stderr)

    def test_files_help_only_is_help_not_skipped(self):
        proc = _run("--files", "--help")
        assert proc.returncode == 0
        assert "Examples:" in (proc.stdout + proc.stderr)
        assert "IMPORT-HYGIENE:" not in proc.stdout

    def test_files_zero_paths_still_skipped(self):
        proc = _run("--files")
        assert proc.returncode == 0
        lines = [line for line in proc.stdout.splitlines() if line]
        assert lines[-1] == "IMPORT-HYGIENE: SKIPPED (no arguments given)"

    def test_files_mixed_with_real_path_and_help_is_files_mode(self):
        # Mixed args: a real .py plus --help. The all-help gate does NOT
        # fire (the .py path is not a help flag), so the run degrades to
        # normal --files mode: --help is reported as a non-.py argument on
        # stderr and the checked file still gets a verdict line.
        target = _SCRIPT.parent / "check_unused_imports.py"
        proc = _run("--files", str(target), "--help")
        assert proc.returncode in (0, 1)
        assert "Examples:" not in (proc.stdout + proc.stderr)
        assert "not a .py path, ignored: --help" in proc.stderr
        lines = [line for line in proc.stdout.splitlines() if line]
        assert lines[-1].startswith("IMPORT-HYGIENE: ")
