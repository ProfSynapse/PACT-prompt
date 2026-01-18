"""Comprehensive tests for file_size_check.py hook.

Tests the PostToolUse hook that alerts when files exceed line count thresholds,
encouraging SOLID/DRY principles and architectural refactoring.
"""

import json
import os
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import file_size_check


class TestImportsAndConstants:
    """Smoke tests - verify module loads and constants exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert file_size_check is not None

    def test_warning_threshold_default(self):
        """WARNING_THRESHOLD should be 600 lines."""
        assert hasattr(file_size_check, 'WARNING_THRESHOLD')
        assert file_size_check.WARNING_THRESHOLD == 600

    def test_critical_threshold_default(self):
        """CRITICAL_THRESHOLD should be 800 lines."""
        assert hasattr(file_size_check, 'CRITICAL_THRESHOLD')
        assert file_size_check.CRITICAL_THRESHOLD == 800

    def test_checked_extensions_defined(self):
        """CHECKED_EXTENSIONS should contain common source code extensions."""
        assert hasattr(file_size_check, 'CHECKED_EXTENSIONS')
        # Check for essential extensions
        assert ".py" in file_size_check.CHECKED_EXTENSIONS
        assert ".ts" in file_size_check.CHECKED_EXTENSIONS
        assert ".tsx" in file_size_check.CHECKED_EXTENSIONS
        assert ".js" in file_size_check.CHECKED_EXTENSIONS
        assert ".jsx" in file_size_check.CHECKED_EXTENSIONS
        assert ".rb" in file_size_check.CHECKED_EXTENSIONS
        assert ".go" in file_size_check.CHECKED_EXTENSIONS
        assert ".java" in file_size_check.CHECKED_EXTENSIONS
        assert ".rs" in file_size_check.CHECKED_EXTENSIONS

    def test_excluded_paths_defined(self):
        """EXCLUDED_PATHS should contain common build/vendor directories."""
        assert hasattr(file_size_check, 'EXCLUDED_PATHS')
        assert "__pycache__" in file_size_check.EXCLUDED_PATHS
        assert "node_modules" in file_size_check.EXCLUDED_PATHS
        assert ".git/" in file_size_check.EXCLUDED_PATHS
        assert "dist/" in file_size_check.EXCLUDED_PATHS
        assert "vendor/" in file_size_check.EXCLUDED_PATHS

    def test_key_functions_defined(self):
        """Key functions should be defined."""
        assert callable(file_size_check.is_excluded_path)
        assert callable(file_size_check.should_check_file)
        assert callable(file_size_check.count_lines)
        assert callable(file_size_check.format_guidance)
        assert callable(file_size_check.main)


class TestIsExcludedPath:
    """Tests for is_excluded_path() function."""

    def test_pycache_excluded(self):
        """__pycache__ paths should be excluded."""
        assert file_size_check.is_excluded_path("/project/__pycache__/module.cpython-39.pyc") is True
        assert file_size_check.is_excluded_path("src/__pycache__/utils.py") is True

    def test_node_modules_excluded(self):
        """node_modules paths should be excluded."""
        assert file_size_check.is_excluded_path("/project/node_modules/package/index.js") is True
        assert file_size_check.is_excluded_path("node_modules/lodash/lodash.js") is True

    def test_git_directory_excluded(self):
        """Git directory paths should be excluded."""
        assert file_size_check.is_excluded_path("/project/.git/objects/pack/file") is True
        assert file_size_check.is_excluded_path(".git/hooks/pre-commit") is True

    def test_dist_directory_excluded(self):
        """dist/ paths should be excluded."""
        assert file_size_check.is_excluded_path("/project/dist/bundle.js") is True
        assert file_size_check.is_excluded_path("dist/index.js") is True

    def test_build_directory_excluded(self):
        """build/ paths should be excluded."""
        assert file_size_check.is_excluded_path("/project/build/output.js") is True
        assert file_size_check.is_excluded_path("build/app.py") is True

    def test_vendor_directory_excluded(self):
        """vendor/ paths should be excluded."""
        assert file_size_check.is_excluded_path("/project/vendor/package/lib.py") is True
        assert file_size_check.is_excluded_path("vendor/github.com/pkg/main.go") is True

    def test_venv_directories_excluded(self):
        """.venv/ and venv/ paths should be excluded."""
        assert file_size_check.is_excluded_path("/project/.venv/lib/python3.9/site-packages/pkg.py") is True
        assert file_size_check.is_excluded_path("venv/lib/python/utils.py") is True

    def test_source_files_not_excluded(self):
        """Regular source file paths should not be excluded."""
        assert file_size_check.is_excluded_path("/project/src/main.py") is False
        assert file_size_check.is_excluded_path("app/components/Button.tsx") is False
        assert file_size_check.is_excluded_path("/home/user/project/utils.js") is False

    def test_similar_names_not_excluded(self):
        """Paths with similar but different names should not be excluded."""
        # "dist" as part of name, not directory
        assert file_size_check.is_excluded_path("/project/distribution.py") is False
        # "build" as part of name
        assert file_size_check.is_excluded_path("/project/builder.ts") is False


class TestShouldCheckFile:
    """Tests for should_check_file() function."""

    def test_python_files_checked(self):
        """Python files should be checked."""
        assert file_size_check.should_check_file("app.py") is True
        assert file_size_check.should_check_file("/project/src/utils.py") is True

    def test_typescript_files_checked(self):
        """TypeScript files should be checked."""
        assert file_size_check.should_check_file("component.ts") is True
        assert file_size_check.should_check_file("Button.tsx") is True

    def test_javascript_files_checked(self):
        """JavaScript files should be checked."""
        assert file_size_check.should_check_file("app.js") is True
        assert file_size_check.should_check_file("Component.jsx") is True

    def test_other_language_files_checked(self):
        """Other supported language files should be checked."""
        assert file_size_check.should_check_file("main.go") is True
        assert file_size_check.should_check_file("App.java") is True
        assert file_size_check.should_check_file("lib.rs") is True
        assert file_size_check.should_check_file("script.rb") is True
        assert file_size_check.should_check_file("app.swift") is True
        assert file_size_check.should_check_file("Main.kt") is True
        assert file_size_check.should_check_file("App.scala") is True
        assert file_size_check.should_check_file("Component.vue") is True
        assert file_size_check.should_check_file("Widget.svelte") is True
        assert file_size_check.should_check_file("index.php") is True

    def test_c_cpp_files_checked(self):
        """C/C++ files should be checked."""
        assert file_size_check.should_check_file("main.c") is True
        assert file_size_check.should_check_file("app.cpp") is True
        assert file_size_check.should_check_file("header.h") is True
        assert file_size_check.should_check_file("utils.hpp") is True

    def test_csharp_files_checked(self):
        """C# files should be checked."""
        assert file_size_check.should_check_file("Program.cs") is True

    def test_case_insensitive_extensions(self):
        """Extension check should be case-insensitive."""
        assert file_size_check.should_check_file("App.PY") is True
        assert file_size_check.should_check_file("Component.TSX") is True
        assert file_size_check.should_check_file("main.GO") is True

    def test_non_source_files_not_checked(self):
        """Non-source files should not be checked."""
        assert file_size_check.should_check_file("README.md") is False
        assert file_size_check.should_check_file("config.json") is False
        assert file_size_check.should_check_file("package.json") is False
        assert file_size_check.should_check_file("styles.css") is False
        assert file_size_check.should_check_file("image.png") is False
        assert file_size_check.should_check_file("data.yaml") is False
        assert file_size_check.should_check_file(".gitignore") is False
        assert file_size_check.should_check_file("Dockerfile") is False

    def test_files_without_extension(self):
        """Files without extensions should not be checked."""
        assert file_size_check.should_check_file("Makefile") is False
        assert file_size_check.should_check_file("README") is False


class TestCountLines:
    """Tests for count_lines() function."""

    def test_count_lines_simple_file(self):
        """Should correctly count lines in a simple file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("line 1\nline 2\nline 3\n")
            f.flush()
            try:
                assert file_size_check.count_lines(f.name) == 3
            finally:
                os.unlink(f.name)

    def test_count_lines_empty_file(self):
        """Should return 0 for empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")
            f.flush()
            try:
                assert file_size_check.count_lines(f.name) == 0
            finally:
                os.unlink(f.name)

    def test_count_lines_single_line_no_newline(self):
        """Should count single line without trailing newline."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("single line without newline")
            f.flush()
            try:
                assert file_size_check.count_lines(f.name) == 1
            finally:
                os.unlink(f.name)

    def test_count_lines_large_file(self):
        """Should correctly count lines in a large file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(1000):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                assert file_size_check.count_lines(f.name) == 1000
            finally:
                os.unlink(f.name)

    def test_count_lines_nonexistent_file(self):
        """Should return 0 for nonexistent file."""
        assert file_size_check.count_lines("/nonexistent/path/file.py") == 0

    def test_count_lines_directory(self):
        """Should return 0 when path is a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assert file_size_check.count_lines(tmpdir) == 0

    def test_count_lines_with_unicode(self):
        """Should handle files with unicode content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write("# Unicode: \u00e9\u00e0\u00fc\u4e2d\u6587\n")
            f.write("# More unicode\n")
            f.flush()
            try:
                assert file_size_check.count_lines(f.name) == 2
            finally:
                os.unlink(f.name)

    def test_count_lines_with_blank_lines(self):
        """Should count blank lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("line 1\n\n\nline 4\n\n")
            f.flush()
            try:
                assert file_size_check.count_lines(f.name) == 5
            finally:
                os.unlink(f.name)


class TestFormatGuidance:
    """Tests for format_guidance() function."""

    def test_warning_threshold_message(self):
        """Should format warning-level guidance for files at warning threshold."""
        guidance = file_size_check.format_guidance("/project/src/large_file.py", 650)
        assert "large_file.py" in guidance
        assert "650 lines" in guidance
        assert "FILE SIZE" in guidance
        assert "SOLID" in guidance
        assert "DRY" in guidance
        assert "pact-architect" in guidance

    def test_critical_threshold_message(self):
        """Should format critical-level guidance for files at critical threshold."""
        guidance = file_size_check.format_guidance("/project/src/huge_file.py", 850)
        assert "huge_file.py" in guidance
        assert "850 lines" in guidance
        assert "CRITICAL" in guidance
        assert "well above" in guidance
        assert "pact-architect" in guidance

    def test_contains_refactoring_suggestions(self):
        """Guidance should contain refactoring suggestions."""
        guidance = file_size_check.format_guidance("/project/file.py", 700)
        assert "Single Responsibility" in guidance
        assert "Modular design" in guidance
        assert "separate modules" in guidance

    def test_extracts_filename_from_path(self):
        """Should extract just the filename from full path."""
        guidance = file_size_check.format_guidance("/very/long/nested/path/to/file.py", 600)
        assert "file.py" in guidance
        # Should not contain full path in the intro
        assert "/very/long/nested/path/to/" not in guidance.split('\n')[0]

    def test_600_line_threshold_mentioned(self):
        """Should reference the 600-line maintainability threshold."""
        guidance = file_size_check.format_guidance("/project/file.py", 650)
        assert "600-line" in guidance or "600 line" in guidance


class TestMainJsonInputOutput:
    """Tests for main() JSON input/output handling."""

    def test_exits_cleanly_on_malformed_json(self):
        """Should exit with code 0 on malformed JSON input."""
        with patch.object(sys, "stdin", StringIO("not valid json")), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_exits_cleanly_on_empty_input(self):
        """Should exit with code 0 on empty input."""
        with patch.object(sys, "stdin", StringIO("")), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_exits_cleanly_on_missing_tool_name(self):
        """Should exit with code 0 when tool_name is missing."""
        input_data = json.dumps({"tool_input": {"file_path": "/test.py"}})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_ignores_non_edit_write_tools(self):
        """Should ignore tools other than Edit and Write."""
        input_data = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/test.py"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_ignores_bash_tool(self):
        """Should ignore Bash tool."""
        input_data = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "echo hello"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_exits_on_missing_file_path(self):
        """Should exit with code 0 when file_path is missing."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"old_string": "foo", "new_string": "bar"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_exits_on_empty_file_path(self):
        """Should exit with code 0 when file_path is empty string."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "", "content": "test"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0


class TestMainExcludedPaths:
    """Tests for main() excluded path handling."""

    def test_skips_node_modules(self):
        """Should skip files in node_modules."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/node_modules/pkg/large.js"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_skips_pycache(self):
        """Should skip files in __pycache__."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/project/__pycache__/module.py"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_skips_venv(self):
        """Should skip files in virtual environments."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/.venv/lib/site-packages/pkg.py"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0


class TestMainNonSourceFiles:
    """Tests for main() non-source file handling."""

    def test_skips_markdown_files(self):
        """Should skip markdown files."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/project/README.md", "content": "# Title"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_skips_json_files(self):
        """Should skip JSON files."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/package.json"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_skips_css_files(self):
        """Should skip CSS files."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/project/styles.css", "content": ".class {}"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0


class TestMainNonexistentFile:
    """Tests for main() handling of nonexistent files."""

    def test_skips_nonexistent_file(self):
        """Should skip files that don't exist on disk."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/nonexistent/path/to/file.py"}
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0


class TestMainBelowThreshold:
    """Tests for main() when file is below warning threshold."""

    def test_no_output_below_threshold(self, capsys):
        """Should produce no output for files below warning threshold."""
        # Create a small file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(100):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Edit",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit) as exc_info:
                    file_size_check.main()
                assert exc_info.value.code == 0
                captured = capsys.readouterr()
                assert captured.out == ""
            finally:
                os.unlink(f.name)

    def test_no_output_at_599_lines(self, capsys):
        """Should produce no output for file with 599 lines (just under threshold)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(599):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Write",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit) as exc_info:
                    file_size_check.main()
                assert exc_info.value.code == 0
                captured = capsys.readouterr()
                assert captured.out == ""
            finally:
                os.unlink(f.name)


class TestMainAboveThreshold:
    """Tests for main() when file exceeds warning threshold."""

    def test_outputs_json_at_warning_threshold(self, capsys):
        """Should output JSON guidance at warning threshold (600 lines)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(650):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Edit",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit) as exc_info:
                    file_size_check.main()
                assert exc_info.value.code == 0
                captured = capsys.readouterr()
                output = json.loads(captured.out)
                assert "hookSpecificOutput" in output
                assert "additionalContext" in output["hookSpecificOutput"]
                assert "FILE SIZE" in output["hookSpecificOutput"]["additionalContext"]
            finally:
                os.unlink(f.name)

    def test_outputs_critical_message_at_critical_threshold(self, capsys):
        """Should output critical guidance at critical threshold (800 lines)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(850):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Write",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit) as exc_info:
                    file_size_check.main()
                assert exc_info.value.code == 0
                captured = capsys.readouterr()
                output = json.loads(captured.out)
                assert "CRITICAL" in output["hookSpecificOutput"]["additionalContext"]
            finally:
                os.unlink(f.name)

    def test_output_includes_hook_event_name(self, capsys):
        """Output should include hookEventName = PostToolUse."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(700):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Edit",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit) as exc_info:
                    file_size_check.main()
                assert exc_info.value.code == 0
                captured = capsys.readouterr()
                output = json.loads(captured.out)
                assert output["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
            finally:
                os.unlink(f.name)


class TestMainEditTool:
    """Tests for main() handling Edit tool input."""

    def test_edit_tool_triggers_check(self, capsys):
        """Edit tool should trigger file size check."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(700):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Edit",
                    "tool_input": {
                        "file_path": f.name,
                        "old_string": "old",
                        "new_string": "new"
                    }
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit):
                    file_size_check.main()
                captured = capsys.readouterr()
                assert captured.out != ""
                output = json.loads(captured.out)
                assert "additionalContext" in output["hookSpecificOutput"]
            finally:
                os.unlink(f.name)


class TestMainWriteTool:
    """Tests for main() handling Write tool input."""

    def test_write_tool_triggers_check(self, capsys):
        """Write tool should trigger file size check."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(700):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Write",
                    "tool_input": {
                        "file_path": f.name,
                        "content": "new content"
                    }
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit):
                    file_size_check.main()
                captured = capsys.readouterr()
                assert captured.out != ""
                output = json.loads(captured.out)
                assert "additionalContext" in output["hookSpecificOutput"]
            finally:
                os.unlink(f.name)


class TestMainExceptionHandling:
    """Tests for main() exception handling."""

    def test_handles_read_error_gracefully(self, capsys):
        """Should handle file read errors gracefully."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/test/file.py"}
        })

        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(file_size_check, "count_lines", side_effect=RuntimeError("Test error")), \
             patch.object(os.path, "isfile", return_value=True), \
             patch.object(file_size_check, "should_check_file", return_value=True), \
             patch.object(file_size_check, "is_excluded_path", return_value=False), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.err

    def test_exception_does_not_block_operation(self, capsys):
        """Exceptions should not block the Edit/Write operation (exit 0)."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/test/file.py"}
        })

        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(file_size_check, "is_excluded_path", side_effect=Exception("Unexpected")), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()

        assert exc_info.value.code == 0


class TestMainToolInputVariants:
    """Tests for various tool_input structures."""

    def test_handles_missing_tool_input(self):
        """Should handle missing tool_input field."""
        input_data = json.dumps({"tool_name": "Edit"})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_handles_null_tool_input(self):
        """Should handle null tool_input field."""
        input_data = json.dumps({"tool_name": "Write", "tool_input": None})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0

    def test_handles_tool_input_as_string(self):
        """Should handle tool_input as string instead of dict."""
        input_data = json.dumps({"tool_name": "Edit", "tool_input": "not a dict"})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            file_size_check.main()
        assert exc_info.value.code == 0


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def test_full_workflow_large_python_file(self, capsys):
        """Full workflow: large Python file triggers guidance."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write a realistic-looking large Python file
            f.write('"""Module docstring."""\n\n')
            f.write('import os\nimport sys\n\n')
            for i in range(700):
                f.write(f'def function_{i}():\n')
                f.write(f'    """Function {i} docstring."""\n')
                f.write(f'    pass\n\n')
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Edit",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit):
                    file_size_check.main()

                captured = capsys.readouterr()
                output = json.loads(captured.out)
                context = output["hookSpecificOutput"]["additionalContext"]
                # Should mention the filename
                assert os.path.basename(f.name) in context
                # Should mention SOLID/DRY
                assert "SOLID" in context
                assert "pact-architect" in context
            finally:
                os.unlink(f.name)

    def test_full_workflow_typescript_file(self, capsys):
        """Full workflow: large TypeScript file triggers guidance."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False) as f:
            f.write('// React component\n')
            f.write('import React from "react";\n\n')
            for i in range(650):
                f.write(f'// Component definition {i}\n')
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Write",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit):
                    file_size_check.main()

                captured = capsys.readouterr()
                output = json.loads(captured.out)
                assert "hookSpecificOutput" in output
            finally:
                os.unlink(f.name)

    def test_small_file_no_warning(self, capsys):
        """Small files should not trigger any warning."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('"""Small module."""\n\n')
            f.write('def hello():\n')
            f.write('    return "Hello, World!"\n')
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Edit",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit) as exc_info:
                    file_size_check.main()

                assert exc_info.value.code == 0
                captured = capsys.readouterr()
                assert captured.out == ""
            finally:
                os.unlink(f.name)

    def test_excluded_large_file_no_warning(self, capsys):
        """Large files in excluded paths should not trigger warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a node_modules subdirectory
            node_modules = os.path.join(tmpdir, "node_modules", "pkg")
            os.makedirs(node_modules)
            large_file = os.path.join(node_modules, "large.js")

            with open(large_file, 'w') as f:
                for i in range(1000):
                    f.write(f'// Line {i}\n')

            input_data = json.dumps({
                "tool_name": "Edit",
                "tool_input": {"file_path": large_file}
            })
            with patch.object(sys, "stdin", StringIO(input_data)), \
                 pytest.raises(SystemExit) as exc_info:
                file_size_check.main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert captured.out == ""


class TestEdgeCases:
    """Edge case tests."""

    def test_exactly_600_lines(self, capsys):
        """File with exactly 600 lines should trigger warning."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(600):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Edit",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit):
                    file_size_check.main()
                captured = capsys.readouterr()
                output = json.loads(captured.out)
                assert "additionalContext" in output["hookSpecificOutput"]
            finally:
                os.unlink(f.name)

    def test_exactly_800_lines(self, capsys):
        """File with exactly 800 lines should trigger critical warning."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(800):
                f.write(f"# Line {i}\n")
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Edit",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit):
                    file_size_check.main()
                captured = capsys.readouterr()
                output = json.loads(captured.out)
                assert "CRITICAL" in output["hookSpecificOutput"]["additionalContext"]
            finally:
                os.unlink(f.name)

    def test_file_with_special_characters_in_path(self, capsys):
        """Should handle file paths with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            special_dir = os.path.join(tmpdir, "my project (v2)")
            os.makedirs(special_dir)
            file_path = os.path.join(special_dir, "file.py")

            with open(file_path, 'w') as f:
                for i in range(700):
                    f.write(f"# Line {i}\n")

            input_data = json.dumps({
                "tool_name": "Edit",
                "tool_input": {"file_path": file_path}
            })
            with patch.object(sys, "stdin", StringIO(input_data)), \
                 pytest.raises(SystemExit):
                file_size_check.main()
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert "file.py" in output["hookSpecificOutput"]["additionalContext"]

    def test_very_long_lines(self, capsys):
        """Should count lines correctly even with very long lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            for i in range(650):
                f.write("x" * 10000 + "\n")  # Very long lines
            f.flush()
            try:
                input_data = json.dumps({
                    "tool_name": "Edit",
                    "tool_input": {"file_path": f.name}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit):
                    file_size_check.main()
                captured = capsys.readouterr()
                output = json.loads(captured.out)
                assert "650 lines" in output["hookSpecificOutput"]["additionalContext"]
            finally:
                os.unlink(f.name)
