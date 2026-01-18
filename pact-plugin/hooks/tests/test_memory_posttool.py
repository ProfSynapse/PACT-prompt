"""Tests for memory_posttool.py hook."""

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import memory_posttool


class TestImportsAndConstants:
    """Smoke tests - verify module loads and constants exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert memory_posttool is not None

    def test_excluded_paths_defined(self):
        """EXCLUDED_PATHS constant should be defined with expected patterns."""
        assert hasattr(memory_posttool, "EXCLUDED_PATHS")
        assert isinstance(memory_posttool.EXCLUDED_PATHS, list)
        assert len(memory_posttool.EXCLUDED_PATHS) > 0

    def test_excluded_paths_contains_expected_patterns(self):
        """EXCLUDED_PATHS should contain transient/generated file patterns."""
        expected_patterns = [
            "__pycache__",
            "node_modules",
            ".git/",
            "*.log",
            "*.tmp",
            ".pyc",
            "dist/",
            "build/",
        ]
        for pattern in expected_patterns:
            assert pattern in memory_posttool.EXCLUDED_PATHS, f"Missing pattern: {pattern}"

    def test_key_functions_exist(self):
        """Key functions should be defined."""
        assert callable(memory_posttool.is_excluded_path)
        assert callable(memory_posttool.format_prompt)
        assert callable(memory_posttool.main)


class TestIsExcludedPath:
    """Tests for is_excluded_path() function."""

    def test_pycache_excluded(self):
        """Paths containing __pycache__ should be excluded."""
        assert memory_posttool.is_excluded_path("/project/__pycache__/module.pyc") is True
        assert memory_posttool.is_excluded_path("src/__pycache__/test.py") is True

    def test_node_modules_excluded(self):
        """Paths containing node_modules should be excluded."""
        assert memory_posttool.is_excluded_path("/project/node_modules/package/index.js") is True
        assert memory_posttool.is_excluded_path("node_modules/react/lib/react.js") is True

    def test_git_directory_excluded(self):
        """Paths containing .git/ should be excluded."""
        assert memory_posttool.is_excluded_path("/project/.git/config") is True
        assert memory_posttool.is_excluded_path(".git/hooks/pre-commit") is True

    def test_log_pattern_excluded(self):
        """Paths containing *.log pattern substring should be excluded."""
        # Note: is_excluded_path does substring matching, not glob matching
        # So "*.log" pattern matches paths containing "*.log" literally
        assert memory_posttool.is_excluded_path("/var/log/*.log") is True
        assert memory_posttool.is_excluded_path("debug*.log") is True

    def test_tmp_pattern_excluded(self):
        """Paths containing *.tmp pattern substring should be excluded."""
        # Note: is_excluded_path does substring matching, not glob matching
        assert memory_posttool.is_excluded_path("/tmp/*.tmp") is True
        assert memory_posttool.is_excluded_path("cache*.tmp") is True

    def test_log_files_not_excluded_by_extension_alone(self):
        """Regular .log files are NOT excluded (pattern is *.log literal)."""
        # This tests actual behavior - substring match, not glob
        assert memory_posttool.is_excluded_path("/var/log/app.log") is False
        assert memory_posttool.is_excluded_path("debug.log") is False

    def test_tmp_files_not_excluded_by_extension_alone(self):
        """Regular .tmp files are NOT excluded (pattern is *.tmp literal)."""
        # This tests actual behavior - substring match, not glob
        assert memory_posttool.is_excluded_path("/tmp/session.tmp") is False
        assert memory_posttool.is_excluded_path("cache.tmp") is False

    def test_pyc_files_excluded(self):
        """Paths containing .pyc should be excluded."""
        assert memory_posttool.is_excluded_path("/project/module.pyc") is True
        assert memory_posttool.is_excluded_path("test.pyc") is True

    def test_dist_directory_excluded(self):
        """Paths containing dist/ should be excluded."""
        assert memory_posttool.is_excluded_path("/project/dist/bundle.js") is True
        assert memory_posttool.is_excluded_path("dist/main.js") is True

    def test_build_directory_excluded(self):
        """Paths containing build/ should be excluded."""
        assert memory_posttool.is_excluded_path("/project/build/output.js") is True
        assert memory_posttool.is_excluded_path("build/index.html") is True

    def test_normal_source_file_not_excluded(self):
        """Normal source files should not be excluded."""
        assert memory_posttool.is_excluded_path("/project/src/main.py") is False
        assert memory_posttool.is_excluded_path("/project/lib/utils.ts") is False
        assert memory_posttool.is_excluded_path("app/models/user.rb") is False

    def test_documentation_not_excluded(self):
        """Documentation files should not be excluded."""
        assert memory_posttool.is_excluded_path("/project/docs/README.md") is False
        assert memory_posttool.is_excluded_path("CLAUDE.md") is False

    def test_config_files_not_excluded(self):
        """Config files should not be excluded."""
        assert memory_posttool.is_excluded_path("/project/.claude/settings.json") is False
        assert memory_posttool.is_excluded_path("package.json") is False

    def test_empty_path_not_excluded(self):
        """Empty path should not be excluded."""
        assert memory_posttool.is_excluded_path("") is False


class TestFormatPrompt:
    """Tests for format_prompt() function."""

    def test_returns_string(self):
        """format_prompt should return a string."""
        result = memory_posttool.format_prompt()
        assert isinstance(result, str)

    def test_includes_memory_check_prefix(self):
        """Prompt should include memory check prefix."""
        result = memory_posttool.format_prompt()
        assert "Memory check" in result

    def test_includes_completion_guidance(self):
        """Prompt should include guidance about completed work."""
        result = memory_posttool.format_prompt()
        assert "completed" in result.lower() or "finished" in result.lower()

    def test_includes_continue_guidance(self):
        """Prompt should include guidance about continuing work."""
        result = memory_posttool.format_prompt()
        assert "continue" in result.lower() or "mid-task" in result.lower()

    def test_includes_save_bias(self):
        """Prompt should emphasize bias toward saving."""
        result = memory_posttool.format_prompt()
        assert "save" in result.lower()
        assert "doubt" in result.lower() or "bias" in result.lower()


class TestMainToolFiltering:
    """Tests for main() tool name filtering."""

    def test_edit_tool_processed(self, capsys):
        """Edit tool should be processed and produce output."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/src/main.py"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "hookSpecificOutput" in output

    def test_write_tool_processed(self, capsys):
        """Write tool should be processed and produce output."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/project/src/new_file.py"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "hookSpecificOutput" in output

    def test_read_tool_skipped(self, capsys):
        """Read tool should be skipped (no output)."""
        input_data = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/project/src/main.py"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_bash_tool_skipped(self, capsys):
        """Bash tool should be skipped (no output)."""
        input_data = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_glob_tool_skipped(self, capsys):
        """Glob tool should be skipped (no output)."""
        input_data = json.dumps({
            "tool_name": "Glob",
            "tool_input": {"pattern": "*.py"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_grep_tool_skipped(self, capsys):
        """Grep tool should be skipped (no output)."""
        input_data = json.dumps({
            "tool_name": "Grep",
            "tool_input": {"pattern": "TODO"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""


class TestMainExcludedPaths:
    """Tests for main() excluded path handling."""

    def test_pycache_path_skipped(self, capsys):
        """Edits to __pycache__ files should be skipped."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/__pycache__/module.pyc"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_node_modules_path_skipped(self, capsys):
        """Edits to node_modules files should be skipped."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/project/node_modules/pkg/index.js"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_git_path_skipped(self, capsys):
        """Edits to .git/ files should be skipped."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/.git/config"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_tmp_file_skipped(self, capsys):
        """Edits to *.tmp pattern paths should be skipped."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/cache*.tmp"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_dist_path_skipped(self, capsys):
        """Edits to dist/ files should be skipped."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/dist/bundle.js"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_build_path_skipped(self, capsys):
        """Edits to build/ files should be skipped."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/project/build/output.js"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""


class TestMainEdgeCases:
    """Tests for main() edge case handling."""

    def test_missing_file_path_skipped(self, capsys):
        """Edit without file_path should be skipped."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"old_string": "foo", "new_string": "bar"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_empty_file_path_skipped(self, capsys):
        """Edit with empty file_path should be skipped."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": ""},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_missing_tool_name_skipped(self, capsys):
        """Input without tool_name should be skipped."""
        input_data = json.dumps({
            "tool_input": {"file_path": "/project/src/main.py"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_missing_tool_input_skipped(self, capsys):
        """Input without tool_input should be skipped."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == ""


class TestMainJsonHandling:
    """Tests for main() JSON input/output handling."""

    def test_handles_malformed_json(self):
        """Should exit cleanly on malformed JSON input."""
        with patch.object(sys, "stdin", StringIO("not valid json")), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()
        assert exc_info.value.code == 0

    def test_handles_empty_input(self):
        """Should exit cleanly on empty input."""
        with patch.object(sys, "stdin", StringIO("")), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()
        assert exc_info.value.code == 0

    def test_handles_empty_json_object(self):
        """Should exit cleanly on empty JSON object."""
        with patch.object(sys, "stdin", StringIO("{}")), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()
        assert exc_info.value.code == 0

    def test_output_format_correct(self, capsys):
        """Output should be correctly formatted JSON with expected structure."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/src/main.py"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_posttool.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        # Verify structure
        assert "hookSpecificOutput" in output
        assert "hookEventName" in output["hookSpecificOutput"]
        assert "additionalContext" in output["hookSpecificOutput"]

        # Verify values
        assert output["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        assert isinstance(output["hookSpecificOutput"]["additionalContext"], str)

    def test_additional_context_contains_prompt(self, capsys):
        """additionalContext should contain the formatted prompt."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/project/src/new.py"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_posttool.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        context = output["hookSpecificOutput"]["additionalContext"]
        assert "Memory check" in context
        assert "save" in context.lower()


class TestMainErrorHandling:
    """Tests for main() error handling."""

    def test_handles_exception_gracefully(self, capsys):
        """Should exit 0 and log warning on unexpected errors."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/src/main.py"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(memory_posttool, "is_excluded_path", side_effect=RuntimeError("test error")), \
             pytest.raises(SystemExit) as exc_info:
            memory_posttool.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.err

    def test_error_message_includes_hook_name(self, capsys):
        """Error message should include hook identifier."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/src/main.py"},
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(memory_posttool, "format_prompt", side_effect=Exception("boom")), \
             pytest.raises(SystemExit):
            memory_posttool.main()

        captured = capsys.readouterr()
        assert "memory_posttool" in captured.err


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def test_typical_edit_workflow(self, capsys):
        """Typical edit operation should produce memory prompt."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/Users/dev/project/src/api/handlers.py",
                "old_string": "def get_user():",
                "new_string": "def get_user(user_id: str):"
            },
            "tool_output": {"success": True}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_posttool.main()

        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "Memory check" in output["hookSpecificOutput"]["additionalContext"]

    def test_typical_write_workflow(self, capsys):
        """Typical write operation should produce memory prompt."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/Users/dev/project/src/models/user.py",
                "content": "class User:\n    pass"
            },
            "tool_output": {"success": True}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_posttool.main()

        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "Memory check" in output["hookSpecificOutput"]["additionalContext"]

    def test_claude_md_edit_produces_prompt(self, capsys):
        """Edits to CLAUDE.md should produce memory prompt (not excluded)."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/Users/dev/project/CLAUDE.md",
                "old_string": "## Context",
                "new_string": "## Project Context"
            },
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_posttool.main()

        captured = capsys.readouterr()
        assert captured.out != ""

    def test_test_file_edit_produces_prompt(self, capsys):
        """Edits to test files should produce memory prompt."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/project/tests/test_user.py",
                "old_string": "def test_user():",
                "new_string": "def test_user_creation():"
            },
            "tool_output": {}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_posttool.main()

        captured = capsys.readouterr()
        assert captured.out != ""
