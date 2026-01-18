"""Comprehensive tests for phase_completion.py hook.

Tests phase detection, decision log reminders, and test phase reminders
for the Stop hook that verifies CODE phase completion documentation.
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import phase_completion


# ============================================================================
# TestImportsAndConstants - Smoke tests for module structure
# ============================================================================

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

    def test_code_phase_indicators_underscore_variants(self):
        """CODE_PHASE_INDICATORS should include underscore variants."""
        assert "pact_backend_coder" in phase_completion.CODE_PHASE_INDICATORS
        assert "pact_frontend_coder" in phase_completion.CODE_PHASE_INDICATORS
        assert "pact_database_engineer" in phase_completion.CODE_PHASE_INDICATORS

    def test_decision_log_mentions_defined(self):
        """DECISION_LOG_MENTIONS should contain expected values."""
        assert "decision-log" in phase_completion.DECISION_LOG_MENTIONS
        assert "decision log" in phase_completion.DECISION_LOG_MENTIONS
        assert "docs/decision-logs" in phase_completion.DECISION_LOG_MENTIONS

    def test_decision_log_mentions_all_variants(self):
        """DECISION_LOG_MENTIONS should include all common variants."""
        expected = ["decision-log", "decision log", "decision_log", "decisionlog", "docs/decision-logs", "decision-logs/"]
        for variant in expected:
            assert variant in phase_completion.DECISION_LOG_MENTIONS, f"Missing: {variant}"

    def test_key_functions_exist(self):
        """Key functions should be defined and callable."""
        assert callable(phase_completion.check_for_code_phase_activity)
        assert callable(phase_completion.check_decision_log_mentioned)
        assert callable(phase_completion.phase_docs_exist)
        assert callable(phase_completion.check_for_test_reminders)
        assert callable(phase_completion.main)


# ============================================================================
# TestCheckForCodePhaseActivity - CODE phase detection tests
# ============================================================================

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

    def test_detects_underscore_variant_backend(self):
        """Should detect pact_backend_coder (underscore) in transcript."""
        transcript = "Calling pact_backend_coder for implementation"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_detects_underscore_variant_frontend(self):
        """Should detect pact_frontend_coder (underscore) in transcript."""
        transcript = "Calling pact_frontend_coder for UI"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_detects_underscore_variant_database(self):
        """Should detect pact_database_engineer (underscore) in transcript."""
        transcript = "Calling pact_database_engineer for schema"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_case_insensitive(self):
        """Detection should be case insensitive."""
        transcript = "Using PACT-BACKEND-CODER for implementation"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_case_insensitive_mixed_case(self):
        """Detection should handle mixed case."""
        transcript = "Using Pact-Frontend-Coder for UI work"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_returns_false_for_test_engineer(self):
        """Should return False for pact-test-engineer (not CODE phase)."""
        transcript = "Running pact-test-engineer for testing"
        assert phase_completion.check_for_code_phase_activity(transcript) is False

    def test_returns_false_for_architect(self):
        """Should return False for pact-architect (not CODE phase)."""
        transcript = "Invoking pact-architect for design"
        assert phase_completion.check_for_code_phase_activity(transcript) is False

    def test_returns_false_for_preparer(self):
        """Should return False for pact-preparer (not CODE phase)."""
        transcript = "Using pact-preparer for research"
        assert phase_completion.check_for_code_phase_activity(transcript) is False

    def test_returns_false_for_empty_transcript(self):
        """Should return False for empty transcript."""
        assert phase_completion.check_for_code_phase_activity("") is False

    def test_returns_false_for_whitespace_only(self):
        """Should return False for whitespace-only transcript."""
        assert phase_completion.check_for_code_phase_activity("   \n\t  ") is False

    def test_detects_in_multiline_transcript(self):
        """Should detect CODE phase in multiline transcript."""
        transcript = """
        Starting work on feature.
        Invoking pact-backend-coder for implementation.
        Completed the API endpoint.
        """
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_detects_multiple_coders_in_transcript(self):
        """Should detect when multiple CODE agents are mentioned."""
        transcript = "Used pact-backend-coder and pact-frontend-coder together"
        assert phase_completion.check_for_code_phase_activity(transcript) is True


# ============================================================================
# TestPreparePhaseDetection - PREPARE phase detection tests
# ============================================================================

class TestPreparePhaseDetection:
    """Tests for PREPARE phase detection and prompts."""

    def test_prepare_phase_docs_path(self):
        """Should use docs/preparation for PREPARE phase."""
        # This tests the phase_docs_exist function's path mapping
        # by verifying the prepare phase maps to docs/preparation
        assert phase_completion.phase_docs_exist("/nonexistent", "prepare") is False

    def test_prepare_docs_exist_when_present(self, tmp_path):
        """Should detect existing preparation docs."""
        preparation = tmp_path / "docs" / "preparation"
        preparation.mkdir(parents=True)
        (preparation / "requirements.md").write_text("# Requirements")

        assert phase_completion.phase_docs_exist(str(tmp_path), "prepare") is True

    def test_prepare_docs_missing_when_dir_empty(self, tmp_path):
        """Should return False when preparation dir exists but is empty."""
        preparation = tmp_path / "docs" / "preparation"
        preparation.mkdir(parents=True)

        assert phase_completion.phase_docs_exist(str(tmp_path), "prepare") is False


# ============================================================================
# TestArchitectPhaseDetection - ARCHITECT phase detection tests
# ============================================================================

class TestArchitectPhaseDetection:
    """Tests for ARCHITECT phase detection and prompts."""

    def test_architect_phase_docs_path(self):
        """Should use docs/architecture for ARCHITECT phase."""
        assert phase_completion.phase_docs_exist("/nonexistent", "architect") is False

    def test_architect_docs_exist_when_present(self, tmp_path):
        """Should detect existing architecture docs."""
        architecture = tmp_path / "docs" / "architecture"
        architecture.mkdir(parents=True)
        (architecture / "design.md").write_text("# Design")

        assert phase_completion.phase_docs_exist(str(tmp_path), "architect") is True

    def test_architect_docs_missing_when_dir_empty(self, tmp_path):
        """Should return False when architecture dir exists but is empty."""
        architecture = tmp_path / "docs" / "architecture"
        architecture.mkdir(parents=True)

        assert phase_completion.phase_docs_exist(str(tmp_path), "architect") is False


# ============================================================================
# TestCodePhaseDetection - CODE phase detection and prompts
# ============================================================================

class TestCodePhaseDetection:
    """Tests for CODE phase detection and prompts."""

    def test_code_phase_docs_path(self):
        """Should use docs/decision-logs for CODE phase."""
        assert phase_completion.phase_docs_exist("/nonexistent", "code") is False

    def test_code_docs_exist_when_present(self, tmp_path):
        """Should detect existing decision logs."""
        decision_logs = tmp_path / "docs" / "decision-logs"
        decision_logs.mkdir(parents=True)
        (decision_logs / "feature.md").write_text("# Decision Log")

        assert phase_completion.phase_docs_exist(str(tmp_path), "code") is True

    def test_code_docs_missing_when_dir_empty(self, tmp_path):
        """Should return False when decision-logs dir exists but is empty."""
        decision_logs = tmp_path / "docs" / "decision-logs"
        decision_logs.mkdir(parents=True)

        assert phase_completion.phase_docs_exist(str(tmp_path), "code") is False


# ============================================================================
# TestCheckDecisionLogMentioned - Decision log mention detection
# ============================================================================

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

    def test_detects_decision_log_underscore(self):
        """Should detect 'decision_log' mention."""
        transcript = "Created decision_log.md file"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_detects_decisionlog_no_separator(self):
        """Should detect 'decisionlog' mention (no separator)."""
        transcript = "Updated the decisionlog"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_detects_decision_logs_path(self):
        """Should detect docs/decision-logs path."""
        transcript = "Saving to docs/decision-logs/user-auth.md"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_detects_decision_logs_directory(self):
        """Should detect decision-logs/ directory reference."""
        transcript = "Created file in decision-logs/ directory"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_case_insensitive(self):
        """Detection should be case insensitive."""
        transcript = "DECISION-LOG created"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_case_insensitive_mixed(self):
        """Detection should handle mixed case."""
        transcript = "Decision Log documented"
        assert phase_completion.check_decision_log_mentioned(transcript) is True

    def test_returns_false_when_not_mentioned(self):
        """Should return False when decision log not mentioned."""
        transcript = "Implemented the user authentication feature"
        assert phase_completion.check_decision_log_mentioned(transcript) is False

    def test_returns_false_for_empty_transcript(self):
        """Should return False for empty transcript."""
        assert phase_completion.check_decision_log_mentioned("") is False

    def test_returns_false_for_whitespace_only(self):
        """Should return False for whitespace-only transcript."""
        assert phase_completion.check_decision_log_mentioned("   \n\t  ") is False

    def test_detects_in_multiline_transcript(self):
        """Should detect decision log mention in multiline transcript."""
        transcript = """
        Completed the implementation.
        Created decision-log for architectural choices.
        Moving to testing phase.
        """
        assert phase_completion.check_decision_log_mentioned(transcript) is True


# ============================================================================
# TestPhaseDocsExist - Phase documentation existence checks
# ============================================================================

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

    def test_returns_false_for_empty_phase(self, tmp_path):
        """Should return False for empty phase name."""
        assert phase_completion.phase_docs_exist(str(tmp_path), "") is False

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

    def test_handles_multiple_files_in_directory(self, tmp_path):
        """Should return True when directory has multiple files."""
        decision_logs = tmp_path / "docs" / "decision-logs"
        decision_logs.mkdir(parents=True)
        (decision_logs / "feature1.md").write_text("# Feature 1")
        (decision_logs / "feature2.md").write_text("# Feature 2")

        assert phase_completion.phase_docs_exist(str(tmp_path), "code") is True

    def test_handles_subdirectories(self, tmp_path):
        """Should return True when directory has subdirectories with files."""
        decision_logs = tmp_path / "docs" / "decision-logs"
        subdir = decision_logs / "feature"
        subdir.mkdir(parents=True)
        # The subdirectory itself counts as an item
        assert phase_completion.phase_docs_exist(str(tmp_path), "code") is True


# ============================================================================
# TestCheckForTestReminders - Test phase reminder detection
# ============================================================================

class TestCheckForTestReminders:
    """Tests for check_for_test_reminders()."""

    def test_detects_test_engineer(self):
        """Should detect pact-test-engineer mention."""
        transcript = "Invoking pact-test-engineer for verification"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_detects_test_engineer_phrase(self):
        """Should detect 'test engineer' phrase."""
        transcript = "The test engineer will verify the implementation"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_detects_testing_discussion(self):
        """Should detect general testing discussion."""
        transcript = "Testing the implementation now"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_detects_unit_test_mention(self):
        """Should detect unit test mention."""
        transcript = "Writing unit test for the service"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_detects_integration_test_mention(self):
        """Should detect integration test mention."""
        transcript = "Creating integration test for the API"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_detects_test_coverage_mention(self):
        """Should detect test coverage mention."""
        transcript = "Checking test coverage for the module"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_case_insensitive(self):
        """Detection should be case insensitive."""
        transcript = "UNIT TEST created"
        assert phase_completion.check_for_test_reminders(transcript) is True

    def test_returns_false_when_no_testing(self):
        """Should return False when testing not mentioned."""
        transcript = "Implemented the feature and committed changes"
        assert phase_completion.check_for_test_reminders(transcript) is False

    def test_returns_false_for_empty_transcript(self):
        """Should return False for empty transcript."""
        assert phase_completion.check_for_test_reminders("") is False

    def test_detects_in_multiline_transcript(self):
        """Should detect testing mention in multiline transcript."""
        transcript = """
        Completed the implementation.
        Now running the unit test suite.
        All tests passing.
        """
        assert phase_completion.check_for_test_reminders(transcript) is True


# ============================================================================
# TestEdgeCases - Boundary conditions and special cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_partial_phase_name_not_matched(self):
        """Partial phase names should not falsely match."""
        transcript = "Using backend-coder without pact prefix"
        assert phase_completion.check_for_code_phase_activity(transcript) is False

    def test_similar_words_not_matched(self):
        """Similar words should not falsely match decision log patterns."""
        transcript = "Making decisions about logging infrastructure"
        # "decision" alone shouldn't match decision-log patterns
        # Actually checking the implementation - it checks for specific patterns
        assert phase_completion.check_decision_log_mentioned(transcript) is False

    def test_transcript_with_special_characters(self):
        """Should handle transcripts with special characters."""
        transcript = "Invoking pact-backend-coder! @#$% special chars"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_transcript_with_unicode(self):
        """Should handle transcripts with unicode characters."""
        transcript = "Invoking pact-backend-coder for implementation"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_very_long_transcript(self):
        """Should handle very long transcripts efficiently."""
        long_prefix = "Some text. " * 1000
        transcript = long_prefix + "Invoking pact-backend-coder for implementation"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_newlines_and_tabs_in_transcript(self):
        """Should handle transcripts with various whitespace."""
        transcript = "Line1\n\tInvoking pact-backend-coder\n\nLine3"
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_multiple_phases_in_transcript(self):
        """Should detect CODE phase even when multiple phases mentioned."""
        transcript = """
        First, pact-preparer gathered requirements.
        Then pact-architect designed the system.
        Finally, pact-backend-coder implemented it.
        """
        assert phase_completion.check_for_code_phase_activity(transcript) is True

    def test_empty_project_dir(self, tmp_path):
        """Should handle empty project directory."""
        assert phase_completion.phase_docs_exist(str(tmp_path), "code") is False
        assert phase_completion.phase_docs_exist(str(tmp_path), "prepare") is False
        assert phase_completion.phase_docs_exist(str(tmp_path), "architect") is False
        assert phase_completion.phase_docs_exist(str(tmp_path), "test") is False


# ============================================================================
# TestMainJsonFlow - Main function JSON input/output tests
# ============================================================================

class TestMainJsonFlow:
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

    def test_exits_cleanly_on_empty_input(self):
        """Should exit cleanly on empty input."""
        with patch.object(sys, "stdin", StringIO("")), \
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

    def test_no_output_for_prepare_phase(self, capsys):
        """Should not output CODE reminders for PREPARE phase."""
        input_data = json.dumps({
            "transcript": "Running pact-preparer for research"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_no_output_for_architect_phase(self, capsys):
        """Should not output CODE reminders for ARCHITECT phase."""
        input_data = json.dumps({
            "transcript": "Running pact-architect for design"
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


# ============================================================================
# TestMissingTranscriptHandling - Handling of missing/null transcript
# ============================================================================

class TestMissingTranscriptHandling:
    """Tests for handling missing or null transcript values."""

    def test_null_transcript_in_json(self):
        """Should handle null transcript in JSON."""
        input_data = json.dumps({"transcript": None})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            phase_completion.main()
        assert exc_info.value.code == 0

    def test_numeric_transcript_in_json(self):
        """Should handle numeric transcript gracefully."""
        input_data = json.dumps({"transcript": 12345})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            phase_completion.main()
        # Should not crash - either exits 0 or handles gracefully
        assert exc_info.value.code == 0

    def test_list_transcript_in_json(self):
        """Should handle list transcript gracefully."""
        input_data = json.dumps({"transcript": ["line1", "line2"]})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            phase_completion.main()
        assert exc_info.value.code == 0


# ============================================================================
# TestIntegrationScenarios - Realistic integration tests
# ============================================================================

class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def test_full_code_phase_workflow_without_docs(self, capsys, tmp_path):
        """Full CODE phase without existing docs should show both reminders."""
        input_data = json.dumps({
            "transcript": """
            Invoking pact-backend-coder for user authentication.
            Implemented JWT token validation.
            Created user.py with login endpoint.
            """
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "Decision logs" in output["systemMessage"]
        assert "TEST Phase" in output["systemMessage"]

    def test_code_phase_with_decision_log_mention_no_testing(self, capsys, tmp_path):
        """CODE phase with decision log mentioned but no testing should show test reminder."""
        input_data = json.dumps({
            "transcript": """
            Invoking pact-backend-coder for implementation.
            Created decision-log at docs/decision-logs/auth.md.
            Completed the authentication module.
            """
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        if captured.out:
            output = json.loads(captured.out)
            # Should have test reminder but not decision log reminder
            assert "TEST Phase" in output.get("systemMessage", "")
            assert "Decision logs should be created" not in output.get("systemMessage", "")

    def test_code_phase_with_testing_mention_no_decision_log(self, capsys, tmp_path):
        """CODE phase with testing mentioned but no decision log should show decision log reminder."""
        input_data = json.dumps({
            "transcript": """
            Invoking pact-backend-coder for implementation.
            Also discussing testing strategy for the module.
            Will run unit test after completion.
            """
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        # Should have decision log reminder but not test reminder
        assert "Decision logs" in output["systemMessage"]
        assert "TEST Phase Reminder" not in output["systemMessage"]

    def test_code_phase_all_addressed(self, capsys, tmp_path):
        """CODE phase with both decision log and testing addressed should show no reminders."""
        input_data = json.dumps({
            "transcript": """
            Invoking pact-backend-coder for implementation.
            Created decision-log documenting the approach.
            Running unit test to verify functionality.
            """
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        # No output when both are addressed
        assert captured.out == ""

    def test_multiple_code_agents_in_session(self, capsys, tmp_path):
        """Multiple CODE agents in one session should still trigger reminders."""
        input_data = json.dumps({
            "transcript": """
            First, invoking pact-backend-coder for API.
            Then, invoking pact-frontend-coder for UI.
            Finally, pact-database-engineer for schema.
            """
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "Decision logs" in output["systemMessage"]

    def test_established_project_no_reminders(self, capsys, tmp_path):
        """Established project with existing docs should show no reminders."""
        # Create existing docs
        decision_logs = tmp_path / "docs" / "decision-logs"
        decision_logs.mkdir(parents=True)
        (decision_logs / "existing.md").write_text("# Existing Log")

        review = tmp_path / "docs" / "review"
        review.mkdir(parents=True)
        (review / "existing.md").write_text("# Existing Review")

        input_data = json.dumps({
            "transcript": "Invoking pact-backend-coder for new feature"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": str(tmp_path)}), \
             pytest.raises(SystemExit):
            phase_completion.main()

        captured = capsys.readouterr()
        assert captured.out == ""
