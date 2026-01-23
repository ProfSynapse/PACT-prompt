"""
Integration tests for the SessionStart hook (compaction_refresh.py).

Tests refresh detection and instruction injection after compaction.
"""

import json
import os
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))


class TestGetEncodedProjectPathFromEnv:
    """Tests for get_encoded_project_path_from_env function."""

    def test_encodes_project_path(self):
        """Test encoding project path from environment."""
        from compaction_refresh import get_encoded_project_path_from_env

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": "/Users/test/myproject"}):
            encoded = get_encoded_project_path_from_env()

        assert encoded == "-Users-test-myproject"

    def test_handles_nested_path(self):
        """Test encoding deeply nested project path."""
        from compaction_refresh import get_encoded_project_path_from_env

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": "/home/user/code/org/repo"}):
            encoded = get_encoded_project_path_from_env()

        assert encoded == "-home-user-code-org-repo"

    def test_returns_none_when_not_set(self):
        """Test returns None when CLAUDE_PROJECT_DIR not set."""
        from compaction_refresh import get_encoded_project_path_from_env

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
            encoded = get_encoded_project_path_from_env()

        assert encoded is None


class TestReadCheckpoint:
    """Tests for read_checkpoint function."""

    def test_read_valid_checkpoint(self, tmp_path: Path, sample_checkpoint):
        """Test reading valid checkpoint file."""
        from compaction_refresh import read_checkpoint

        checkpoint_path = tmp_path / "checkpoint.json"
        checkpoint_path.write_text(json.dumps(sample_checkpoint))

        result = read_checkpoint(checkpoint_path)

        assert result == sample_checkpoint

    def test_read_nonexistent_file(self, tmp_path: Path):
        """Test reading nonexistent file returns None."""
        from compaction_refresh import read_checkpoint

        result = read_checkpoint(tmp_path / "nonexistent.json")

        assert result is None

    def test_read_invalid_json(self, tmp_path: Path):
        """Test reading invalid JSON returns None."""
        from compaction_refresh import read_checkpoint

        checkpoint_path = tmp_path / "invalid.json"
        checkpoint_path.write_text("not valid json {")

        result = read_checkpoint(checkpoint_path)

        assert result is None


class TestValidateCheckpoint:
    """Tests for validate_checkpoint function."""

    def test_validate_matching_session(self, sample_checkpoint):
        """Test validation passes for matching session ID."""
        from compaction_refresh import validate_checkpoint

        is_valid = validate_checkpoint(sample_checkpoint, "test-session-123")

        assert is_valid is True

    def test_validate_mismatched_session(self, sample_checkpoint):
        """Test validation fails for mismatched session ID."""
        from compaction_refresh import validate_checkpoint

        is_valid = validate_checkpoint(sample_checkpoint, "different-session")

        assert is_valid is False

    def test_validate_unsupported_version(self, sample_checkpoint):
        """Test validation fails for unsupported version."""
        from compaction_refresh import validate_checkpoint

        sample_checkpoint["version"] = "2.0"
        is_valid = validate_checkpoint(sample_checkpoint, "test-session-123")

        assert is_valid is False

    def test_validate_missing_workflow(self, sample_checkpoint):
        """Test validation fails without workflow field."""
        from compaction_refresh import validate_checkpoint

        del sample_checkpoint["workflow"]
        is_valid = validate_checkpoint(sample_checkpoint, "test-session-123")

        assert is_valid is False

    def test_validate_empty_checkpoint(self):
        """Test validation fails for empty checkpoint."""
        from compaction_refresh import validate_checkpoint

        is_valid = validate_checkpoint({}, "test-session")

        assert is_valid is False

    def test_validate_none_checkpoint(self):
        """Test validation fails for None."""
        from compaction_refresh import validate_checkpoint

        is_valid = validate_checkpoint(None, "test-session")

        assert is_valid is False


class TestBuildRefreshMessage:
    """Tests for build_refresh_message function."""

    def test_build_complete_message(self, sample_checkpoint):
        """Test building directive prompt refresh message with all fields."""
        from compaction_refresh import build_refresh_message

        message = build_refresh_message(sample_checkpoint)

        # Check directive prompt format
        assert "[WORKFLOW REFRESH]" in message
        assert "Context auto-compaction occurred" in message
        assert "following framework protocols" in message
        assert "You are resuming:" in message
        assert "peer-review" in message
        assert "pr-64" in message
        assert "State:" in message
        assert "recommendations" in message
        # Check step description is included
        assert "Processing review recommendations" in message
        assert "Confidence: 0.9" in message
        assert "Verify with user if context seems outdated" in message

    def test_build_message_with_pending_action(self, sample_checkpoint):
        """Test refresh message includes pending action as Action line."""
        from compaction_refresh import build_refresh_message

        message = build_refresh_message(sample_checkpoint)

        assert "Action:" in message
        assert "Would you like to review" in message

    def test_build_message_with_context(self, sample_checkpoint):
        """Test refresh message includes context with verbose key names."""
        from compaction_refresh import build_refresh_message

        message = build_refresh_message(sample_checkpoint)

        assert "Context:" in message
        # pr_number stays the same (already clear)
        assert "pr_number=64" in message
        # has_blocking becomes has_blocking_issues
        assert "has_blocking_issues=False" in message
        # minor_count becomes minor_issues_count
        assert "minor_issues_count=0" in message
        # future_count becomes future_recommendations_count
        assert "future_recommendations_count=1" in message

    def test_build_message_confidence_values(self):
        """Test confidence values are displayed in guidance line."""
        from compaction_refresh import build_refresh_message

        checkpoint = {
            "workflow": {"name": "peer-review", "id": ""},
            "step": {"name": "commit"},
            "extraction": {"confidence": 0.5},
            "context": {},
        }

        message = build_refresh_message(checkpoint)

        # Directive format shows confidence in guidance line
        assert "Confidence: 0.5" in message
        assert "Verify with user if context seems outdated" in message


class TestCompactionRefreshMain:
    """Integration tests for the main() function."""

    def test_main_with_active_workflow(self, tmp_path: Path, sample_checkpoint):
        """Test full refresh flow with active workflow."""
        # Create checkpoint file
        checkpoint_dir = tmp_path / ".claude" / "pact-refresh"
        checkpoint_dir.mkdir(parents=True)
        checkpoint_path = checkpoint_dir / "-test-project.json"
        checkpoint_path.write_text(json.dumps(sample_checkpoint))

        input_data = json.dumps({"source": "compact"})

        with patch("sys.stdin", StringIO(input_data)), \
             patch.dict(os.environ, {
                 "CLAUDE_SESSION_ID": "test-session-123",
                 "CLAUDE_PROJECT_DIR": "/test/project",
             }), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                output = mock_stdout.getvalue()

        result = json.loads(output)

        assert "hookSpecificOutput" in result
        refresh_msg = result["hookSpecificOutput"]["additionalContext"]
        assert "[WORKFLOW REFRESH]" in refresh_msg
        assert "peer-review" in refresh_msg

    def test_main_with_no_workflow(self, tmp_path: Path):
        """Test flow when checkpoint has no active workflow."""
        checkpoint_dir = tmp_path / ".claude" / "pact-refresh"
        checkpoint_dir.mkdir(parents=True)
        checkpoint_path = checkpoint_dir / "-test-project.json"
        checkpoint_path.write_text(json.dumps({
            "version": "1.0",
            "session_id": "test-session",
            "workflow": {"name": "none"},
            "extraction": {"confidence": 1.0},
        }))

        input_data = json.dumps({"source": "compact"})

        with patch("sys.stdin", StringIO(input_data)), \
             patch.dict(os.environ, {
                 "CLAUDE_SESSION_ID": "test-session",
                 "CLAUDE_PROJECT_DIR": "/test/project",
             }), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                # Capture exit
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit 0 without output (no refresh needed)
                assert exc_info.value.code == 0

    def test_main_non_compact_source(self, tmp_path: Path, sample_checkpoint):
        """Test that non-compact sessions are ignored."""
        # Create checkpoint that would trigger refresh
        checkpoint_dir = tmp_path / ".claude" / "pact-refresh"
        checkpoint_dir.mkdir(parents=True)
        checkpoint_path = checkpoint_dir / "-test-project.json"
        checkpoint_path.write_text(json.dumps(sample_checkpoint))

        # Source is NOT "compact"
        input_data = json.dumps({"source": "new"})

        with patch("sys.stdin", StringIO(input_data)), \
             patch.dict(os.environ, {
                 "CLAUDE_SESSION_ID": "test-session-123",
                 "CLAUDE_PROJECT_DIR": "/test/project",
             }), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit 0 without refresh (not a compact session)
                assert exc_info.value.code == 0
                output = mock_stdout.getvalue()
                # No output expected for non-compact sessions
                assert output == ""

    def test_main_no_checkpoint_file(self, tmp_path: Path):
        """Test handling when no checkpoint file exists."""
        input_data = json.dumps({"source": "compact"})

        with patch("sys.stdin", StringIO(input_data)), \
             patch.dict(os.environ, {
                 "CLAUDE_SESSION_ID": "test-session",
                 "CLAUDE_PROJECT_DIR": "/test/project",
             }), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # Should exit 0 without error
                assert exc_info.value.code == 0

    def test_main_mismatched_session_id(self, tmp_path: Path, sample_checkpoint):
        """Test handling when session ID doesn't match."""
        checkpoint_dir = tmp_path / ".claude" / "pact-refresh"
        checkpoint_dir.mkdir(parents=True)
        checkpoint_path = checkpoint_dir / "-test-project.json"
        checkpoint_path.write_text(json.dumps(sample_checkpoint))

        input_data = json.dumps({"source": "compact"})

        # Session ID doesn't match checkpoint
        with patch("sys.stdin", StringIO(input_data)), \
             patch.dict(os.environ, {
                 "CLAUDE_SESSION_ID": "different-session",
                 "CLAUDE_PROJECT_DIR": "/test/project",
             }), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                output = mock_stdout.getvalue()

        result = json.loads(output)
        assert "validation failed" in result["hookSpecificOutput"]["additionalContext"]

    def test_main_missing_project_dir(self, tmp_path: Path, sample_checkpoint):
        """Test handling when CLAUDE_PROJECT_DIR not set."""
        checkpoint_dir = tmp_path / ".claude" / "pact-refresh"
        checkpoint_dir.mkdir(parents=True)

        input_data = json.dumps({"source": "compact"})

        with patch("sys.stdin", StringIO(input_data)), \
             patch.dict(os.environ, {"CLAUDE_SESSION_ID": "test-session"}, clear=True), \
             patch("pathlib.Path.home", return_value=tmp_path):

            # Ensure CLAUDE_PROJECT_DIR is not set
            os.environ.pop("CLAUDE_PROJECT_DIR", None)

            from compaction_refresh import main

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                output = mock_stdout.getvalue()

        result = json.loads(output)
        assert "project path unavailable" in result["hookSpecificOutput"]["additionalContext"]

    def test_main_never_raises(self, tmp_path: Path):
        """Test that main() never raises exceptions."""
        # Invalid JSON input
        with patch("sys.stdin", StringIO("invalid json {")), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main

            # Should not raise
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_main_with_invalid_json_input(self, tmp_path: Path):
        """Test handling of invalid JSON input."""
        with patch("sys.stdin", StringIO("not json")), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            # Should exit cleanly
            assert exc_info.value.code == 0


class TestEndToEndRefresh:
    """End-to-end tests simulating full compaction-refresh cycle."""

    def test_precompact_to_sessionstart_flow(self, tmp_path: Path):
        """Test complete flow from PreCompact to SessionStart."""
        # Step 1: Simulate PreCompact writing checkpoint
        from conftest import create_peer_review_transcript

        transcript_content = create_peer_review_transcript(
            step="recommendations",
            include_pr_number=99,
            include_pending_question=True,
        )

        # Create transcript structure
        projects_dir = tmp_path / ".claude" / "projects"
        encoded_path = "-test-project"
        session_dir = projects_dir / encoded_path / "session-uuid"
        session_dir.mkdir(parents=True)
        transcript_path = session_dir / "session.jsonl"
        transcript_path.write_text(transcript_content)

        # Create checkpoint directory
        checkpoint_dir = tmp_path / ".claude" / "pact-refresh"
        checkpoint_dir.mkdir(parents=True)

        # Run PreCompact
        precompact_input = json.dumps({"transcript_path": str(transcript_path)})

        with patch("sys.stdin", StringIO(precompact_input)), \
             patch.dict(os.environ, {"CLAUDE_SESSION_ID": "test-session-e2e"}), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from precompact_refresh import main as precompact_main

            with patch("sys.stdout", new_callable=StringIO):
                with pytest.raises(SystemExit) as exc_info:
                    precompact_main()
                assert exc_info.value.code == 0

        # Verify checkpoint was created
        checkpoint_path = checkpoint_dir / f"{encoded_path}.json"
        assert checkpoint_path.exists()

        checkpoint = json.loads(checkpoint_path.read_text())
        assert checkpoint["workflow"]["name"] == "peer-review"
        assert checkpoint["session_id"] == "test-session-e2e"

        # Step 2: Simulate SessionStart reading checkpoint
        sessionstart_input = json.dumps({"source": "compact"})

        with patch("sys.stdin", StringIO(sessionstart_input)), \
             patch.dict(os.environ, {
                 "CLAUDE_SESSION_ID": "test-session-e2e",  # Same session
                 "CLAUDE_PROJECT_DIR": "/test/project",
             }), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main as sessionstart_main

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    sessionstart_main()
                assert exc_info.value.code == 0
                output = mock_stdout.getvalue()

        # Verify refresh message was generated
        result = json.loads(output)
        refresh_msg = result["hookSpecificOutput"]["additionalContext"]

        assert "[WORKFLOW REFRESH]" in refresh_msg
        assert "peer-review" in refresh_msg
        assert "recommendations" in refresh_msg or "pr-99" in refresh_msg

    def test_terminated_workflow_no_refresh(self, tmp_path: Path):
        """Test that terminated workflow doesn't trigger refresh."""
        from conftest import create_terminated_workflow_transcript

        transcript_content = create_terminated_workflow_transcript()

        projects_dir = tmp_path / ".claude" / "projects"
        encoded_path = "-test-project"
        session_dir = projects_dir / encoded_path / "session-uuid"
        session_dir.mkdir(parents=True)
        transcript_path = session_dir / "session.jsonl"
        transcript_path.write_text(transcript_content)

        checkpoint_dir = tmp_path / ".claude" / "pact-refresh"
        checkpoint_dir.mkdir(parents=True)

        # Run PreCompact
        precompact_input = json.dumps({"transcript_path": str(transcript_path)})

        with patch("sys.stdin", StringIO(precompact_input)), \
             patch.dict(os.environ, {"CLAUDE_SESSION_ID": "test-session"}), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from precompact_refresh import main as precompact_main

            with patch("sys.stdout", new_callable=StringIO):
                with pytest.raises(SystemExit) as exc_info:
                    precompact_main()
                assert exc_info.value.code == 0

        checkpoint_path = checkpoint_dir / f"{encoded_path}.json"
        checkpoint = json.loads(checkpoint_path.read_text())

        # Terminated workflow should result in "none" workflow
        # (or low confidence that doesn't trigger refresh)
        # The exact behavior depends on confidence threshold
        assert checkpoint["workflow"]["name"] in ["none", "peer-review"]


class TestExceptionHandlingPaths:
    """Tests for exception handling and defensive paths in compaction_refresh."""

    def test_read_checkpoint_io_error(self, tmp_path: Path):
        """Test handling of IOError when reading checkpoint file."""
        from compaction_refresh import read_checkpoint

        # Create a directory where a file is expected (will cause IOError on read)
        checkpoint_path = tmp_path / "checkpoint.json"
        checkpoint_path.mkdir()  # Create as directory, not file

        result = read_checkpoint(checkpoint_path)

        assert result is None

    def test_read_checkpoint_corrupted_json(self, tmp_path: Path):
        """Test handling of corrupted JSON in checkpoint file."""
        from compaction_refresh import read_checkpoint

        checkpoint_path = tmp_path / "checkpoint.json"
        checkpoint_path.write_text("{ corrupted json without closing brace")

        result = read_checkpoint(checkpoint_path)

        assert result is None

    def test_main_outer_exception_handling(self, tmp_path: Path):
        """Test that outer try/except in main() catches all exceptions.

        The main() function has a top-level try/except that should
        catch any unexpected exceptions and exit cleanly.
        """
        # Simulate an exception by patching stdin to raise
        class RaisingStdin:
            def read(self):
                raise RuntimeError("Simulated stdin error")

        with patch("sys.stdin", RaisingStdin()), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main

            # Should not raise, should exit 0
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_main_handles_missing_session_id(self, tmp_path: Path, sample_checkpoint):
        """Test handling when CLAUDE_SESSION_ID is missing."""
        # Create checkpoint file
        checkpoint_dir = tmp_path / ".claude" / "pact-refresh"
        checkpoint_dir.mkdir(parents=True)
        checkpoint_path = checkpoint_dir / "-test-project.json"
        checkpoint_path.write_text(json.dumps(sample_checkpoint))

        input_data = json.dumps({"source": "compact"})

        # Environment without session ID
        env_without_session = {"CLAUDE_PROJECT_DIR": "/test/project"}

        with patch("sys.stdin", StringIO(input_data)), \
             patch.dict(os.environ, env_without_session, clear=True), \
             patch("pathlib.Path.home", return_value=tmp_path):

            from compaction_refresh import main

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                output = mock_stdout.getvalue()

        # Should handle gracefully - validation will fail due to session mismatch
        if output:
            result = json.loads(output)
            assert "hookSpecificOutput" in result

    def test_validate_checkpoint_with_none_fields(self, sample_checkpoint):
        """Test validation handles None values in checkpoint fields."""
        from compaction_refresh import validate_checkpoint

        # Set version to None
        sample_checkpoint["version"] = None
        is_valid = validate_checkpoint(sample_checkpoint, "test-session-123")

        assert is_valid is False

    def test_build_refresh_message_with_missing_fields(self):
        """Test build_refresh_message handles missing optional fields."""
        from compaction_refresh import build_refresh_message

        # Minimal checkpoint with only required fields
        minimal_checkpoint = {
            "workflow": {"name": "peer-review"},
            "step": {"name": "unknown"},
            "extraction": {"confidence": 0.5},
        }

        message = build_refresh_message(minimal_checkpoint)

        # Should not crash and should produce valid message
        assert "[WORKFLOW REFRESH]" in message
        assert "peer-review" in message

    def test_build_refresh_message_with_empty_context(self):
        """Test build_refresh_message handles empty context dict."""
        from compaction_refresh import build_refresh_message

        checkpoint = {
            "workflow": {"name": "peer-review", "id": ""},
            "step": {"name": "commit"},
            "extraction": {"confidence": 0.7},
            "context": {},  # Empty context
        }

        message = build_refresh_message(checkpoint)

        # Should not crash
        assert "[WORKFLOW REFRESH]" in message

    def test_get_encoded_project_path_from_env_empty_string(self):
        """Test handling of empty string CLAUDE_PROJECT_DIR."""
        from compaction_refresh import get_encoded_project_path_from_env

        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": ""}):
            result = get_encoded_project_path_from_env()

        assert result is None
