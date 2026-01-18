"""Minimal tests for phase_completion.py hook."""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import phase_completion


class TestImportsAndConstants:
    """Smoke tests - verify module loads and constants exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert phase_completion is not None

    def test_code_phase_indicators_defined(self):
        """CODE_PHASE_INDICATORS should contain expected values."""
        assert "pact-backend-coder" in phase_completion.CODE_PHASE_INDICATORS
        assert "pact-frontend-coder" in phase_completion.CODE_PHASE_INDICATORS
        assert "pact-database-engineer" in phase_completion.CODE_PHASE_INDICATORS

    def test_decision_log_mentions_defined(self):
        """DECISION_LOG_MENTIONS should contain expected values."""
        assert "decision-log" in phase_completion.DECISION_LOG_MENTIONS
        assert "decision log" in phase_completion.DECISION_LOG_MENTIONS
        assert "docs/decision-logs" in phase_completion.DECISION_LOG_MENTIONS


class TestCheckForCodePhaseActivity:
    """Tests for check_for_code_phase_activity()."""

    def test_detects_backend_coder(self):
        """Should detect pact-backend-coder in transcript."""
        transcript = "Invoking pact-backend-coder for API implementation"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_detects_frontend_coder(self):
        """Should detect pact-frontend-coder in transcript."""
        transcript = "Delegating to pact-frontend-coder for UI work"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_detects_database_engineer(self):
        """Should detect pact-database-engineer in transcript."""
        transcript = "Using pact-database-engineer for schema migration"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_case_insensitive(self):
        """Detection should be case insensitive."""
        transcript = "Using PACT-BACKEND-CODER for implementation"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_returns_false_for_other_phases(self):
        """Should return False when no CODE phase indicators present."""
        transcript = "Running pact-test-engineer for testing"
        assert phase_completion.check_for_code_phase_activity(transcript) is False

    def test_returns_false_for_empty_transcript(self):
        """Should return False for empty transcript."""
        assert phase_completion.check_for_code_phase_activity("") is False


class TestCheckDecisionLogMentioned:
    """Tests for check_decision_log_mentioned()."""

    def test_detects_decision_log_hyphenated(self):
        """Should detect 'decision-log' mention."""
        transcript = "Created a decision-log for the feature"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_detects_decision_log_space(self):
        """Should detect 'decision log' mention."""
        transcript = "Writing the decision log now"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_detects_decision_logs_path(self):
        """Should detect docs/decision-logs path."""
        transcript = "Saving to docs/decision-logs/user-auth.md"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_case_insensitive(self):
        """Detection should be case insensitive."""
        transcript = "DECISION-LOG created"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_returns_false_when_not_mentioned(self):
        """Should return False when decision log not mentioned."""
        transcript = "Implemented the user authentication feature"
        assert phase_completion.check_decision_log_mentioned(transcript) is False

    def test_returns_false_for_empty_transcript(self):
        """Should return False for empty transcript."""
        assert phase_completion.check_decision_log_mentioned("") is False


class TestPhaseDocsExist:
    """Tests for phase_docs_exist()."""

    def test_returns_true_when_code_docs_exist(self, tmp_path):
        """Should return True when decision-logs directory has files."""
        decision_logs = tmp_path / "docs" / "decision-logs"
        decision_logs.mkdir(parents=True)
        (decision_logs / "feature.md").write_text("# Decision Log")

        assert phase_completion.phase_docs_exist(str(tmp_path), "code") is True

    def test_returns_false_when_directory_empty(self, tmp_path):
        """Should return False when docs directory exists but is empty."""
        decision_logs = tmp_path / "docs" / "decision-logs"
        decision_logs.mkdir(parents=True)

        assert phase_completion.phase_docs_exist(str(tmp_path), "code") is False

    def test_returns_false_when_directory_missing(self, tmp_path):
        """Should return False when docs directory doesn't exist."""
        assert phase_completion.phase_docs_exist(str(tmp_path), "code") is False

    def test_returns_false_for_unknown_phase(self, tmp_path):
        """Should return False for unknown phase name."""
        assert phase_completion.phase_docs_exist(str(tmp_path), "unknown") is False

    def test_returns_true_for_prepare_phase(self, tmp_path):
        """Should check docs/preparation for prepare phase."""
        preparation = tmp_path / "docs" / "preparation"
        preparation.mkdir(parents=True)
        (preparation / "requirements.md").write_text("# Requirements")

        assert phase_completion.phase_docs_exist(str(tmp_path), "prepare") is True

    def test_returns_true_for_architect_phase(self, tmp_path):
        """Should check docs/architecture for architect phase."""
        architecture = tmp_path / "docs" / "architecture"
        architecture.mkdir(parents=True)
        (architecture / "design.md").write_text("# Design")

        assert phase_completion.phase_docs_exist(str(tmp_path), "architect") is True

    def test_returns_true_for_test_phase(self, tmp_path):
        """Should check docs/review for test phase."""
        review = tmp_path / "docs" / "review"
        review.mkdir(parents=True)
        (review / "test-report.md").write_text("# Test Report")

        assert phase_completion.phase_docs_exist(str(tmp_path), "test") is True


class TestCheckForTestReminders:
    """Tests for check_for_test_reminders()."""

    def test_detects_test_engineer(self):
        """Should detect pact-test-engineer mention."""
        transcript = "Invoking pact-test-engineer for verification"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_detects_testing_discussion(self):
        """Should detect general testing discussion."""
        transcript = "Testing the implementation now"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_detects_unit_test_mention(self):
        """Should detect unit test mention."""
        transcript = "Writing unit test for the service"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_returns_false_when_no_testing(self):
        """Should return False when testing not mentioned."""
        transcript = "Implemented the feature and committed changes"
        assert phase_completion.check_for_test_reminders(transcript) is False


class TestMain:
    """Tests for main() JSON input/output flow."""

    def test_exits_cleanly_on_empty_transcript(self):
        """Should exit with code 0 when transcript is empty."""
        input_data = json.dumps({"transcript": ""})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            phase_completion.main()
        assert exc_info.value.code == 0

    def test_exits_cleanly_on_missing_transcript(self):
        """Should exit with code 0 when transcript key is missing."""
        input_data = json.dumps({})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            phase_completion.main()
        assert exc_info.value.code == 0

    def test_exits_cleanly_on_malformed_json(self):
        """Should exit cleanly on malformed JSON input."""
        with patch.object(sys, "stdin", StringIO("not valid json")), \
             pytest.raises(SystemExit) as exc_info:
            phase_completion.main()
        assert exc_info.value.code == 0

    def test_outputs_reminder_when_code_phase_without_decision_log(self, capsys, tmp_path):
        """Should output reminder when CODE phase detected without decision log."""
        input_data = json.dumps({
            "transcript": "Invoking pact-backend-coder for implementation"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "systemMessage" in output
        assert "Decision logs" in output["systemMessage"]
        assert "docs/decision-logs" in output["systemMessage"]

    def test_outputs_test_reminder_when_testing_not_discussed(self, capsys, tmp_path):
        """Should output test reminder when CODE phase without testing discussion."""
        input_data = json.dumps({
            "transcript": "Invoking pact-backend-coder for implementation"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "TEST Phase Reminder" in output["systemMessage"]
        assert "pact-test-engineer" in output["systemMessage"]

    def test_suppresses_reminder_when_decision_log_mentioned(self, capsys, tmp_path):
        """Should not output decision log reminder when mentioned in transcript."""
        input_data = json.dumps({
            "transcript": "Invoking pact-backend-coder. Created decision-log for feature."
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        # May still have test reminder, but not decision log reminder
        if captured.out:
            output = json.loads(captured.out)
            assert "Decision logs should be created" not in output.get("systemMessage", "")

    def test_suppresses_reminder_when_docs_exist(self, capsys, tmp_path):
        """Should not output reminders when phase docs already exist."""
        # Create existing docs
        decision_logs = tmp_path / "docs" / "decision-logs"
        decision_logs.mkdir(parents=True)
        (decision_logs / "existing.md").write_text("# Existing Log")

        review = tmp_path / "docs" / "review"
        review.mkdir(parents=True)
        (review / "existing.md").write_text("# Existing Review")

        input_data = json.dumps({
            "transcript": "Invoking pact-backend-coder for implementation"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        # No output when docs already exist
        assert captured.out == ""

    def test_no_output_for_non_code_phase(self, capsys):
        """Should not output reminders for non-CODE phase activity."""
        input_data = json.dumps({
            "transcript": "Running pact-test-engineer for verification"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_handles_exception_gracefully(self, capsys):
        """Should exit cleanly and warn on unexpected errors."""
        input_data = json.dumps({
            "transcript": "Some transcript content"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(phase_completion, "check_for_code_phase_activity",
                         side_effect=Exception("Test error")), \
             pytest.raises(SystemExit) as exc_info:
            phase_completion.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "phase_completion" in captured.err
