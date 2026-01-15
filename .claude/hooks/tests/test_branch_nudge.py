"""Minimal tests for branch_nudge.py hook."""

import json
import subprocess
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import branch_nudge


class TestImportsAndConstants:
    """Smoke tests - verify module loads and constants exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert branch_nudge is not None

    def test_constants_defined(self):
        """Key constants should be defined."""
        assert branch_nudge.PROTECTED_BRANCHES == {"main", "master"}
        assert branch_nudge.PUSH_REMINDER_THRESHOLD == 10
        assert branch_nudge.HOOK_VERSION == "1.0.0"


class TestIsGitRepo:
    """Tests for is_git_repo()."""

    def test_returns_true_in_git_repo(self):
        """Should return True when git rev-parse succeeds."""
        mock_result = MagicMock(returncode=0)
        with patch.object(subprocess, "run", return_value=mock_result):
            assert branch_nudge.is_git_repo() is True

    def test_returns_false_outside_git_repo(self):
        """Should return False when git rev-parse fails."""
        mock_result = MagicMock(returncode=1)
        with patch.object(subprocess, "run", return_value=mock_result):
            assert branch_nudge.is_git_repo() is False

    def test_returns_false_on_timeout(self):
        """Should return False on timeout."""
        with patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 5)):
            assert branch_nudge.is_git_repo() is False


class TestGetCurrentBranch:
    """Tests for get_current_branch()."""

    def test_returns_branch_name(self):
        """Should return branch name from git output."""
        mock_result = MagicMock(stdout="feature-branch\n", returncode=0)
        with patch.object(subprocess, "run", return_value=mock_result):
            assert branch_nudge.get_current_branch() == "feature-branch"

    def test_returns_empty_on_error(self):
        """Should return empty string on subprocess error."""
        with patch.object(subprocess, "run", side_effect=subprocess.CalledProcessError(1, "git")):
            assert branch_nudge.get_current_branch() == ""


class TestBuildNudgeMessage:
    """Tests for build_nudge_message()."""

    def test_returns_empty_when_not_git_repo(self):
        """Should return empty string when not in git repo."""
        with patch.object(branch_nudge, "is_git_repo", return_value=False):
            assert branch_nudge.build_nudge_message() == ""

    def test_warns_on_protected_branch(self):
        """Should warn when on main branch."""
        with patch.object(branch_nudge, "is_git_repo", return_value=True), \
             patch.object(branch_nudge, "get_current_branch", return_value="main"), \
             patch.object(branch_nudge, "increment_edit_count", return_value=1), \
             patch.object(branch_nudge, "should_remind_push", return_value=False):
            message = branch_nudge.build_nudge_message()
            assert "main" in message
            assert "feature branch" in message

    def test_no_warning_on_feature_branch(self):
        """Should not warn when on feature branch with low edit count."""
        with patch.object(branch_nudge, "is_git_repo", return_value=True), \
             patch.object(branch_nudge, "get_current_branch", return_value="feature-x"), \
             patch.object(branch_nudge, "increment_edit_count", return_value=1), \
             patch.object(branch_nudge, "should_remind_push", return_value=False):
            assert branch_nudge.build_nudge_message() == ""


class TestMain:
    """Tests for main() JSON input/output flow."""

    def test_ignores_non_edit_tools(self):
        """Should exit silently for non-Edit/Write tools."""
        input_data = json.dumps({"tool_name": "Read"})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            branch_nudge.main()
        assert exc_info.value.code == 0

    def test_processes_edit_tool(self, capsys):
        """Should process Edit tool and output nudge message."""
        input_data = json.dumps({"tool_name": "Edit"})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(branch_nudge, "build_nudge_message", return_value="Test nudge"), \
             pytest.raises(SystemExit):
            branch_nudge.main()
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["systemMessage"] == "Test nudge"

    def test_handles_malformed_json(self):
        """Should exit cleanly on malformed JSON input."""
        with patch.object(sys, "stdin", StringIO("not valid json")), \
             pytest.raises(SystemExit) as exc_info:
            branch_nudge.main()
        assert exc_info.value.code == 0

    def test_handles_empty_nudge(self, capsys):
        """Should not output anything when no nudge needed."""
        input_data = json.dumps({"tool_name": "Write"})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(branch_nudge, "build_nudge_message", return_value=""), \
             pytest.raises(SystemExit):
            branch_nudge.main()
        captured = capsys.readouterr()
        assert captured.out == ""
