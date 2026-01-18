"""Tests for track_files.py hook.

Tests file tracking functionality for PostToolUse hook (Edit, Write tools).
Uses tmp_path fixture to avoid writing to real tracking directory.
"""

import json
import os
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import track_files


class TestImportsAndConstants:
    """Smoke tests - verify module loads and constants exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert track_files is not None

    def test_tracking_dir_constant_defined(self):
        """TRACKING_DIR constant should be defined as a Path."""
        assert hasattr(track_files, 'TRACKING_DIR')
        assert isinstance(track_files.TRACKING_DIR, Path)

    def test_tracking_dir_path_structure(self):
        """TRACKING_DIR should be under ~/.claude/pact-memory/session-tracking."""
        expected_suffix = Path(".claude") / "pact-memory" / "session-tracking"
        assert str(track_files.TRACKING_DIR).endswith(str(expected_suffix))


class TestEnsureTrackingDir:
    """Tests for ensure_tracking_dir() function."""

    def test_creates_directory_if_not_exists(self, tmp_path):
        """Should create tracking directory if it doesn't exist."""
        test_dir = tmp_path / "tracking"
        assert not test_dir.exists()

        with patch.object(track_files, 'TRACKING_DIR', test_dir):
            track_files.ensure_tracking_dir()

        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_handles_existing_directory(self, tmp_path):
        """Should not fail if directory already exists."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        with patch.object(track_files, 'TRACKING_DIR', test_dir):
            # Should not raise
            track_files.ensure_tracking_dir()

        assert test_dir.exists()

    def test_creates_parent_directories(self, tmp_path):
        """Should create parent directories as needed."""
        test_dir = tmp_path / "deep" / "nested" / "tracking"
        assert not test_dir.exists()

        with patch.object(track_files, 'TRACKING_DIR', test_dir):
            track_files.ensure_tracking_dir()

        assert test_dir.exists()
        assert test_dir.is_dir()


class TestGetSessionTrackingFile:
    """Tests for get_session_tracking_file() function."""

    def test_returns_path_with_session_id(self, tmp_path):
        """Should return path containing the session ID."""
        test_dir = tmp_path / "tracking"

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session-123'}):
            result = track_files.get_session_tracking_file()

        assert result == test_dir / "test-session-123.json"

    def test_uses_unknown_when_no_session_id(self, tmp_path):
        """Should use 'unknown' when CLAUDE_SESSION_ID is not set."""
        test_dir = tmp_path / "tracking"

        # Remove CLAUDE_SESSION_ID if present
        env = os.environ.copy()
        env.pop('CLAUDE_SESSION_ID', None)

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, env, clear=True):
            result = track_files.get_session_tracking_file()

        assert result == test_dir / "unknown.json"

    def test_returns_path_object(self, tmp_path):
        """Should return a Path object."""
        test_dir = tmp_path / "tracking"

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'any-session'}):
            result = track_files.get_session_tracking_file()

        assert isinstance(result, Path)


class TestLoadTrackedFiles:
    """Tests for load_tracked_files() function."""

    def test_loads_existing_file(self, tmp_path):
        """Should load and parse existing tracking file."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        existing_data = {
            "files": [
                {"path": "/test/file.py", "tool": "Edit", "first_seen": "2024-01-01T00:00:00+00:00"}
            ],
            "session_id": "test-session"
        }
        tracking_file = test_dir / "test-session.json"
        tracking_file.write_text(json.dumps(existing_data))

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            result = track_files.load_tracked_files()

        assert result == existing_data
        assert len(result["files"]) == 1
        assert result["files"][0]["path"] == "/test/file.py"

    def test_returns_empty_structure_when_file_missing(self, tmp_path):
        """Should return empty structure when tracking file doesn't exist."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'nonexistent-session'}):
            result = track_files.load_tracked_files()

        assert result == {"files": [], "session_id": "nonexistent-session"}

    def test_returns_empty_structure_on_json_error(self, tmp_path):
        """Should return empty structure when JSON is malformed."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        tracking_file = test_dir / "test-session.json"
        tracking_file.write_text("not valid json {{{")

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            result = track_files.load_tracked_files()

        assert result == {"files": [], "session_id": "test-session"}

    def test_returns_empty_structure_on_io_error(self, tmp_path):
        """Should return empty structure on IO error."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch('builtins.open', side_effect=IOError("Read error")):
            # First need to create the file so exists() returns True
            tracking_file = test_dir / "test-session.json"
            tracking_file.write_text("{}")

        # Now test with patched open that raises IOError
        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            # The file exists, so we need to simulate IOError during read
            original_open = open

            def mock_open_with_error(*args, **kwargs):
                if 'test-session.json' in str(args[0]):
                    raise IOError("Read error")
                return original_open(*args, **kwargs)

            with patch('builtins.open', mock_open_with_error):
                result = track_files.load_tracked_files()

        assert result == {"files": [], "session_id": "test-session"}


class TestSaveTrackedFiles:
    """Tests for save_tracked_files() function."""

    def test_saves_data_to_file(self, tmp_path):
        """Should save data to tracking file."""
        test_dir = tmp_path / "tracking"

        data = {
            "files": [
                {"path": "/test/file.py", "tool": "Write"}
            ],
            "session_id": "test-session"
        }

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            track_files.save_tracked_files(data)

        tracking_file = test_dir / "test-session.json"
        assert tracking_file.exists()

        saved_data = json.loads(tracking_file.read_text())
        assert saved_data == data

    def test_creates_directory_if_needed(self, tmp_path):
        """Should create tracking directory if it doesn't exist."""
        test_dir = tmp_path / "new" / "tracking"
        assert not test_dir.exists()

        data = {"files": [], "session_id": "test"}

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test'}):
            track_files.save_tracked_files(data)

        assert test_dir.exists()

    def test_formats_json_with_indent(self, tmp_path):
        """Should format JSON with indentation for readability."""
        test_dir = tmp_path / "tracking"

        data = {"files": [{"path": "/a"}], "session_id": "test"}

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test'}):
            track_files.save_tracked_files(data)

        tracking_file = test_dir / "test.json"
        content = tracking_file.read_text()

        # Should be indented (not all on one line)
        assert "\n" in content
        assert "  " in content  # 2-space indent

    def test_handles_io_error_gracefully(self, tmp_path, capsys):
        """Should log warning on IO error, not raise."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        data = {"files": [], "session_id": "test"}

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test'}), \
             patch('builtins.open', side_effect=IOError("Write failed")):
            # Should not raise
            track_files.save_tracked_files(data)

        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "could not save" in captured.err.lower()


class TestExtractFilePath:
    """Tests for extract_file_path() function."""

    def test_extracts_file_path_from_tool_input(self):
        """Should extract file_path from tool input dict."""
        tool_input = {"file_path": "/path/to/file.py", "content": "..."}
        result = track_files.extract_file_path(tool_input)
        assert result == "/path/to/file.py"

    def test_returns_empty_string_when_missing(self):
        """Should return empty string when file_path is not in input."""
        tool_input = {"content": "some content"}
        result = track_files.extract_file_path(tool_input)
        assert result == ""

    def test_handles_empty_dict(self):
        """Should handle empty dict gracefully."""
        result = track_files.extract_file_path({})
        assert result == ""

    def test_handles_empty_file_path(self):
        """Should return empty string for empty file_path value."""
        tool_input = {"file_path": ""}
        result = track_files.extract_file_path(tool_input)
        assert result == ""


class TestTrackFile:
    """Tests for track_file() function."""

    def test_tracks_new_file(self, tmp_path):
        """Should add new file to tracking list."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            track_files.track_file("/path/to/new-file.py", "Write")

        tracking_file = test_dir / "test-session.json"
        data = json.loads(tracking_file.read_text())

        assert len(data["files"]) == 1
        assert data["files"][0]["path"] == "/path/to/new-file.py"
        assert data["files"][0]["tool"] == "Write"
        assert "first_seen" in data["files"][0]
        assert "last_modified" in data["files"][0]

    def test_updates_existing_file(self, tmp_path):
        """Should update timestamp when file is already tracked."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        # Create initial tracking data
        initial_data = {
            "files": [{
                "path": "/path/to/file.py",
                "tool": "Write",
                "first_seen": "2024-01-01T00:00:00+00:00",
                "last_modified": "2024-01-01T00:00:00+00:00"
            }],
            "session_id": "test-session"
        }
        tracking_file = test_dir / "test-session.json"
        tracking_file.write_text(json.dumps(initial_data))

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            track_files.track_file("/path/to/file.py", "Edit")

        data = json.loads(tracking_file.read_text())

        # Should still have only one file
        assert len(data["files"]) == 1
        # first_seen should be preserved
        assert data["files"][0]["first_seen"] == "2024-01-01T00:00:00+00:00"
        # last_modified should be updated
        assert data["files"][0]["last_modified"] != "2024-01-01T00:00:00+00:00"
        # tool should be updated to latest
        assert data["files"][0]["tool"] == "Edit"

    def test_ignores_empty_file_path(self, tmp_path):
        """Should do nothing when file_path is empty."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            track_files.track_file("", "Write")

        tracking_file = test_dir / "test-session.json"
        # File should not be created
        assert not tracking_file.exists()

    def test_tracks_multiple_files(self, tmp_path):
        """Should track multiple different files."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            track_files.track_file("/path/to/file1.py", "Write")
            track_files.track_file("/path/to/file2.py", "Edit")
            track_files.track_file("/path/to/file3.py", "Write")

        tracking_file = test_dir / "test-session.json"
        data = json.loads(tracking_file.read_text())

        assert len(data["files"]) == 3
        paths = [f["path"] for f in data["files"]]
        assert "/path/to/file1.py" in paths
        assert "/path/to/file2.py" in paths
        assert "/path/to/file3.py" in paths

    def test_timestamps_are_iso_format(self, tmp_path):
        """Should store timestamps in ISO format with timezone."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            track_files.track_file("/path/to/file.py", "Write")

        tracking_file = test_dir / "test-session.json"
        data = json.loads(tracking_file.read_text())

        first_seen = data["files"][0]["first_seen"]
        last_modified = data["files"][0]["last_modified"]

        # Should be parseable as ISO datetime
        datetime.fromisoformat(first_seen)
        datetime.fromisoformat(last_modified)

        # Should include timezone (ends with +00:00 or Z)
        assert "+00:00" in first_seen or first_seen.endswith("Z")


class TestMainJsonFlow:
    """Tests for main() JSON input/output handling."""

    def test_processes_write_tool(self, tmp_path):
        """Should track file from Write tool input."""
        test_dir = tmp_path / "tracking"

        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/path/to/written-file.py",
                "content": "print('hello')"
            }
        })

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            track_files.main()

        assert exc_info.value.code == 0

        tracking_file = test_dir / "test-session.json"
        data = json.loads(tracking_file.read_text())
        assert len(data["files"]) == 1
        assert data["files"][0]["path"] == "/path/to/written-file.py"
        assert data["files"][0]["tool"] == "Write"

    def test_processes_edit_tool(self, tmp_path):
        """Should track file from Edit tool input."""
        test_dir = tmp_path / "tracking"

        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "/path/to/edited-file.py",
                "old_string": "old",
                "new_string": "new"
            }
        })

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            track_files.main()

        assert exc_info.value.code == 0

        tracking_file = test_dir / "test-session.json"
        data = json.loads(tracking_file.read_text())
        assert len(data["files"]) == 1
        assert data["files"][0]["path"] == "/path/to/edited-file.py"
        assert data["files"][0]["tool"] == "Edit"

    def test_ignores_non_edit_write_tools(self, tmp_path):
        """Should ignore tools other than Edit and Write."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        input_data = json.dumps({
            "tool_name": "Read",
            "tool_input": {
                "file_path": "/path/to/read-file.py"
            }
        })

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            track_files.main()

        assert exc_info.value.code == 0

        # Should not create tracking file for Read tool
        tracking_file = test_dir / "test-session.json"
        assert not tracking_file.exists()

    def test_handles_malformed_json(self):
        """Should exit cleanly on malformed JSON input."""
        with patch.object(sys, "stdin", StringIO("not valid json {")), \
             pytest.raises(SystemExit) as exc_info:
            track_files.main()

        assert exc_info.value.code == 0

    def test_handles_missing_tool_name(self, tmp_path):
        """Should exit cleanly when tool_name is missing."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        input_data = json.dumps({
            "tool_input": {"file_path": "/path/to/file.py"}
        })

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            track_files.main()

        assert exc_info.value.code == 0

    def test_handles_missing_tool_input(self, tmp_path):
        """Should exit cleanly when tool_input is missing."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        input_data = json.dumps({
            "tool_name": "Write"
        })

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            track_files.main()

        assert exc_info.value.code == 0

    def test_handles_missing_file_path(self, tmp_path):
        """Should exit cleanly when file_path is missing from tool_input."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"content": "some content"}
        })

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            track_files.main()

        assert exc_info.value.code == 0

        # No file should be tracked
        tracking_file = test_dir / "test-session.json"
        assert not tracking_file.exists()

    def test_handles_exception_gracefully(self, capsys):
        """Should exit 0 and log warning on unexpected errors."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/path/to/file.py"}
        })

        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(track_files, "track_file", side_effect=RuntimeError("test error")), \
             pytest.raises(SystemExit) as exc_info:
            track_files.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "track_files" in captured.err


class TestEdgeCases:
    """Edge case and boundary condition tests."""

    def test_missing_session_id_uses_unknown(self, tmp_path):
        """Should use 'unknown' as session ID when env var is missing."""
        test_dir = tmp_path / "tracking"

        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/path/to/file.py", "content": "..."}
        })

        # Clear CLAUDE_SESSION_ID
        env = {k: v for k, v in os.environ.items() if k != 'CLAUDE_SESSION_ID'}

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, env, clear=True), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            track_files.main()

        tracking_file = test_dir / "unknown.json"
        assert tracking_file.exists()

    def test_file_already_tracked_updates_only_timestamp(self, tmp_path):
        """When file is already tracked, only timestamp and tool should update."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        # Initial tracking data with extra metadata
        initial_data = {
            "files": [{
                "path": "/path/to/file.py",
                "tool": "Write",
                "first_seen": "2024-01-01T10:00:00+00:00",
                "last_modified": "2024-01-01T10:00:00+00:00",
            }],
            "session_id": "test-session"
        }
        tracking_file = test_dir / "test-session.json"
        tracking_file.write_text(json.dumps(initial_data))

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            track_files.track_file("/path/to/file.py", "Edit")

        data = json.loads(tracking_file.read_text())

        # first_seen preserved
        assert data["files"][0]["first_seen"] == "2024-01-01T10:00:00+00:00"
        # last_modified updated
        assert data["files"][0]["last_modified"] != "2024-01-01T10:00:00+00:00"
        # tool updated
        assert data["files"][0]["tool"] == "Edit"

    def test_empty_json_object(self, tmp_path):
        """Should handle empty JSON object gracefully."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        input_data = json.dumps({})

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            track_files.main()

        assert exc_info.value.code == 0

    def test_special_characters_in_file_path(self, tmp_path):
        """Should handle special characters in file paths."""
        test_dir = tmp_path / "tracking"

        special_path = "/path/with spaces/and-dashes/file_name.py"
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": special_path, "content": "..."}
        })

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            track_files.main()

        tracking_file = test_dir / "test-session.json"
        data = json.loads(tracking_file.read_text())
        assert data["files"][0]["path"] == special_path

    def test_unicode_in_file_path(self, tmp_path):
        """Should handle unicode characters in file paths."""
        test_dir = tmp_path / "tracking"

        unicode_path = "/path/to/archivo_espanol_conena.py"
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": unicode_path, "old_string": "a", "new_string": "b"}
        })

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}), \
             patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            track_files.main()

        tracking_file = test_dir / "test-session.json"
        data = json.loads(tracking_file.read_text())
        assert data["files"][0]["path"] == unicode_path


class TestIntegrationScenarios:
    """Integration tests for realistic usage scenarios."""

    def test_typical_edit_session(self, tmp_path):
        """Simulate a typical editing session with multiple file changes."""
        test_dir = tmp_path / "tracking"

        files_to_edit = [
            ("/project/src/main.py", "Write"),
            ("/project/src/utils.py", "Write"),
            ("/project/src/main.py", "Edit"),  # Re-edit
            ("/project/tests/test_main.py", "Write"),
            ("/project/src/utils.py", "Edit"),  # Re-edit
        ]

        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'dev-session'}):
            for file_path, tool in files_to_edit:
                input_data = json.dumps({
                    "tool_name": tool,
                    "tool_input": {"file_path": file_path, "content": "..."}
                })
                with patch.object(sys, "stdin", StringIO(input_data)), \
                     pytest.raises(SystemExit):
                    track_files.main()

        tracking_file = test_dir / "dev-session.json"
        data = json.loads(tracking_file.read_text())

        # Should have 3 unique files
        assert len(data["files"]) == 3

        paths = [f["path"] for f in data["files"]]
        assert "/project/src/main.py" in paths
        assert "/project/src/utils.py" in paths
        assert "/project/tests/test_main.py" in paths

        # Re-edited files should have Edit as last tool
        for f in data["files"]:
            if f["path"] == "/project/src/main.py":
                assert f["tool"] == "Edit"
            elif f["path"] == "/project/src/utils.py":
                assert f["tool"] == "Edit"
            elif f["path"] == "/project/tests/test_main.py":
                assert f["tool"] == "Write"

    def test_handles_concurrent_sessions(self, tmp_path):
        """Different session IDs should have separate tracking files."""
        test_dir = tmp_path / "tracking"

        # Session 1
        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'session-1'}):
            track_files.track_file("/session1/file.py", "Write")

        # Session 2
        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'session-2'}):
            track_files.track_file("/session2/file.py", "Write")

        # Verify separate files
        session1_file = test_dir / "session-1.json"
        session2_file = test_dir / "session-2.json"

        assert session1_file.exists()
        assert session2_file.exists()

        data1 = json.loads(session1_file.read_text())
        data2 = json.loads(session2_file.read_text())

        assert data1["session_id"] == "session-1"
        assert data1["files"][0]["path"] == "/session1/file.py"

        assert data2["session_id"] == "session-2"
        assert data2["files"][0]["path"] == "/session2/file.py"

    def test_preserves_existing_session_data(self, tmp_path):
        """New file tracking should preserve existing session data."""
        test_dir = tmp_path / "tracking"
        test_dir.mkdir(parents=True)

        # Initial session data
        initial_data = {
            "files": [
                {
                    "path": "/existing/file1.py",
                    "tool": "Write",
                    "first_seen": "2024-01-01T00:00:00+00:00",
                    "last_modified": "2024-01-01T00:00:00+00:00"
                },
                {
                    "path": "/existing/file2.py",
                    "tool": "Edit",
                    "first_seen": "2024-01-01T01:00:00+00:00",
                    "last_modified": "2024-01-01T01:00:00+00:00"
                }
            ],
            "session_id": "test-session"
        }
        tracking_file = test_dir / "test-session.json"
        tracking_file.write_text(json.dumps(initial_data))

        # Add new file
        with patch.object(track_files, 'TRACKING_DIR', test_dir), \
             patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session'}):
            track_files.track_file("/new/file3.py", "Write")

        data = json.loads(tracking_file.read_text())

        # Should have all 3 files
        assert len(data["files"]) == 3

        # Existing files should be preserved
        paths = [f["path"] for f in data["files"]]
        assert "/existing/file1.py" in paths
        assert "/existing/file2.py" in paths
        assert "/new/file3.py" in paths
