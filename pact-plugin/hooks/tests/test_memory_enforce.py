"""Tests for memory_enforce.py hook."""

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import memory_enforce


class TestImportsAndConstants:
    """Smoke tests - verify module loads and constants exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert memory_enforce is not None

    def test_pact_work_agents_defined(self):
        """PACT_WORK_AGENTS list should be defined with expected agents."""
        assert hasattr(memory_enforce, "PACT_WORK_AGENTS")
        expected_agents = [
            "pact-preparer",
            "pact-architect",
            "pact-backend-coder",
            "pact-frontend-coder",
            "pact-database-engineer",
            "pact-test-engineer",
            "pact-n8n",
        ]
        for agent in expected_agents:
            assert agent in memory_enforce.PACT_WORK_AGENTS

    def test_pact_memory_agent_excluded(self):
        """pact-memory-agent should NOT be in PACT_WORK_AGENTS to prevent recursion."""
        assert "pact-memory-agent" not in memory_enforce.PACT_WORK_AGENTS

    def test_work_patterns_defined(self):
        """WORK_PATTERNS list should be defined and non-empty."""
        assert hasattr(memory_enforce, "WORK_PATTERNS")
        assert len(memory_enforce.WORK_PATTERNS) > 0

    def test_decision_patterns_defined(self):
        """DECISION_PATTERNS list should be defined and non-empty."""
        assert hasattr(memory_enforce, "DECISION_PATTERNS")
        assert len(memory_enforce.DECISION_PATTERNS) > 0

    def test_key_functions_exist(self):
        """Key functions should be defined."""
        assert callable(memory_enforce.is_pact_work_agent)
        assert callable(memory_enforce.did_meaningful_work)
        assert callable(memory_enforce.format_enforcement_message)
        assert callable(memory_enforce.main)


class TestIsPactWorkAgent:
    """Tests for is_pact_work_agent() function."""

    def test_pact_work_agents_return_true(self):
        """All PACT work agents should return True."""
        agents = [
            "pact-preparer",
            "pact-architect",
            "pact-backend-coder",
            "pact-frontend-coder",
            "pact-database-engineer",
            "pact-test-engineer",
            "pact-n8n",
        ]
        for agent in agents:
            assert memory_enforce.is_pact_work_agent(agent) is True

    def test_case_insensitive(self):
        """Agent ID matching should be case insensitive."""
        assert memory_enforce.is_pact_work_agent("PACT-BACKEND-CODER") is True
        assert memory_enforce.is_pact_work_agent("Pact-Architect") is True
        assert memory_enforce.is_pact_work_agent("PACT-TEST-ENGINEER") is True

    def test_pact_memory_agent_returns_false(self):
        """pact-memory-agent should return False to prevent recursion."""
        assert memory_enforce.is_pact_work_agent("pact-memory-agent") is False
        assert memory_enforce.is_pact_work_agent("PACT-MEMORY-AGENT") is False

    def test_non_pact_agent_returns_false(self):
        """Non-PACT agents should return False."""
        assert memory_enforce.is_pact_work_agent("other-agent") is False
        assert memory_enforce.is_pact_work_agent("my-custom-agent") is False

    def test_empty_agent_id_returns_false(self):
        """Empty agent ID should return False."""
        assert memory_enforce.is_pact_work_agent("") is False

    def test_none_agent_id_returns_false(self):
        """None agent ID should return False."""
        assert memory_enforce.is_pact_work_agent(None) is False

    def test_partial_match_works(self):
        """Agent ID containing PACT agent name should match."""
        # The function uses 'any(agent in agent_lower for agent in PACT_WORK_AGENTS)'
        # so partial matches should work
        assert memory_enforce.is_pact_work_agent("my-pact-backend-coder-instance") is True


class TestDidMeaningfulWork:
    """Tests for did_meaningful_work() function."""

    def test_empty_transcript_returns_false(self):
        """Empty transcript should return False with empty reasons."""
        did_work, reasons = memory_enforce.did_meaningful_work("")
        assert did_work is False
        assert reasons == []

    def test_none_transcript_returns_false(self):
        """None transcript should return False with empty reasons."""
        did_work, reasons = memory_enforce.did_meaningful_work(None)
        assert did_work is False
        assert reasons == []

    def test_short_transcript_returns_false(self):
        """Transcript shorter than 200 characters should return False."""
        short_transcript = "a" * 199
        did_work, reasons = memory_enforce.did_meaningful_work(short_transcript)
        assert did_work is False
        assert reasons == []

    def test_exactly_200_chars_is_not_enough(self):
        """Transcript of exactly 200 characters should return False (< 200 threshold)."""
        transcript = "a" * 200
        did_work, reasons = memory_enforce.did_meaningful_work(transcript)
        assert did_work is False

    def test_work_patterns_file_operations(self):
        """File operation patterns should be detected."""
        patterns = [
            "created config.py for database settings",
            "wrote handler.ts to process requests",
            "edited schema.json with new fields",
            "modified auth.js for better security",
            "updated server.go with new endpoints",
            "implemented user.rb model class",
        ]
        for pattern in patterns:
            # Pad to meet minimum length
            transcript = pattern + " " * 200
            did_work, reasons = memory_enforce.did_meaningful_work(transcript)
            assert did_work is True, f"Failed for: {pattern}"
            assert "work completed" in reasons

    def test_work_patterns_architecture(self):
        """Architecture-related patterns should be detected."""
        patterns = [
            "designed the new authentication flow",
            "architected the microservices layer",
            "defined the api contract for users",
            "specified the interface requirements",
            "created a diagram for the data flow",
        ]
        for pattern in patterns:
            transcript = pattern + " " * 200
            did_work, reasons = memory_enforce.did_meaningful_work(transcript)
            assert did_work is True, f"Failed for: {pattern}"

    def test_work_patterns_code_work(self):
        """Code work patterns should be detected."""
        patterns = [
            "added a new function for validation",
            "implemented the user class model",
            "refactored the authentication method",
            "fixed the login endpoint bug",
            "created new service for notifications",
        ]
        for pattern in patterns:
            transcript = pattern + " " * 200
            did_work, reasons = memory_enforce.did_meaningful_work(transcript)
            assert did_work is True, f"Failed for: {pattern}"

    def test_work_patterns_research(self):
        """Research work patterns should be detected."""
        patterns = [
            "researched the best practices for caching",
            "gathered requirements from the spec",
            "documented the api in docs/preparation",
            "analyzed the performance metrics",
            "evaluated different database options",
            "created docs/architecture for the system",
        ]
        for pattern in patterns:
            transcript = pattern + " " * 200
            did_work, reasons = memory_enforce.did_meaningful_work(transcript)
            assert did_work is True, f"Failed for: {pattern}"

    def test_decision_patterns(self):
        """Decision patterns should be detected with 'decisions made' reason."""
        patterns = [
            "decided to use postgres for the database",
            "chose to use typescript for the frontend",
            "selected for the redis caching solution",
            "opted for serverless architecture",
            "trade-off between speed and memory",
            "because of security requirements we changed approach",
            "the rationale for this is performance",
            "reason for using this approach is simplicity",
        ]
        for pattern in patterns:
            transcript = pattern + " " * 200
            did_work, reasons = memory_enforce.did_meaningful_work(transcript)
            assert did_work is True, f"Failed for: {pattern}"
            assert "decisions made" in reasons

    def test_file_path_patterns(self):
        """File path patterns should be detected with 'file operations' reason."""
        patterns = [
            "updated .claude/settings.json",
            "modified docs/readme.md",
            "changes to src/main.py",
            "updated lib/utils.js",
            "new test file in tests/",
            "modified the spec for parsing",
        ]
        for pattern in patterns:
            transcript = pattern + " " * 200
            did_work, reasons = memory_enforce.did_meaningful_work(transcript)
            assert did_work is True, f"Failed for: {pattern}"
            assert "file operations" in reasons

    def test_multiple_reasons_detected(self):
        """Multiple work indicators should result in multiple reasons."""
        transcript = """
        I implemented the new user.py module for authentication.
        I decided to use JWT tokens because they are stateless.
        Made changes to the .claude/config.json file.
        """ + " " * 200
        did_work, reasons = memory_enforce.did_meaningful_work(transcript)
        assert did_work is True
        # Should detect work completed, decisions made, and file operations
        assert len(reasons) >= 2

    def test_case_insensitive_matching(self):
        """Pattern matching should be case insensitive."""
        transcript = "IMPLEMENTED THE USER CLASS AND DECIDED TO USE JWT" + " " * 200
        did_work, reasons = memory_enforce.did_meaningful_work(transcript)
        assert did_work is True

    def test_no_meaningful_work(self):
        """Transcript without work patterns should return False."""
        transcript = "Hello world. This is a casual conversation about nothing in particular. Just chatting about the weather and other mundane topics." + " " * 200
        did_work, reasons = memory_enforce.did_meaningful_work(transcript)
        assert did_work is False
        assert reasons == []


class TestFormatEnforcementMessage:
    """Tests for format_enforcement_message() function."""

    def test_includes_agent_id(self):
        """Message should include the agent ID."""
        message = memory_enforce.format_enforcement_message("pact-backend-coder", ["work completed"])
        assert "pact-backend-coder" in message

    def test_includes_reasons(self):
        """Message should include the reasons."""
        message = memory_enforce.format_enforcement_message("pact-backend-coder", ["work completed", "decisions made"])
        assert "work completed" in message
        assert "decisions made" in message

    def test_empty_reasons_uses_default(self):
        """Empty reasons should use 'work completed' as default."""
        message = memory_enforce.format_enforcement_message("pact-backend-coder", [])
        assert "work completed" in message

    def test_includes_mandatory_header(self):
        """Message should include MANDATORY header."""
        message = memory_enforce.format_enforcement_message("pact-backend-coder", [])
        assert "MANDATORY" in message

    def test_includes_pact_memory_agent_reference(self):
        """Message should reference pact-memory-agent for delegation."""
        message = memory_enforce.format_enforcement_message("pact-backend-coder", [])
        assert "pact-memory-agent" in message

    def test_includes_task_invocation_example(self):
        """Message should include Task invocation example."""
        message = memory_enforce.format_enforcement_message("pact-backend-coder", [])
        assert "Task(" in message
        assert "subagent_type" in message
        assert "run_in_background" in message

    def test_includes_urgency_language(self):
        """Message should include urgent language."""
        message = memory_enforce.format_enforcement_message("pact-backend-coder", [])
        assert "NOW" in message or "MUST" in message


class TestMainJsonFlow:
    """Tests for main() JSON input/output flow."""

    def test_handles_malformed_json(self):
        """Should exit cleanly on malformed JSON input."""
        with patch.object(sys, "stdin", StringIO("not valid json")), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        assert exc_info.value.code == 0

    def test_handles_empty_input(self):
        """Should exit cleanly on empty input."""
        with patch.object(sys, "stdin", StringIO("")), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        assert exc_info.value.code == 0

    def test_skips_non_pact_agent(self):
        """Should exit silently for non-PACT agents."""
        input_data = json.dumps({
            "agent_id": "other-agent",
            "transcript": "Some transcript content here." * 50
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        assert exc_info.value.code == 0

    def test_skips_pact_memory_agent(self):
        """Should skip pact-memory-agent to prevent recursion."""
        input_data = json.dumps({
            "agent_id": "pact-memory-agent",
            "transcript": "Saved memory about implemented feature." * 50
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        assert exc_info.value.code == 0

    def test_skips_when_stop_hook_active(self):
        """Should exit when stop_hook_active is True to prevent loops."""
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": "Implemented the user authentication feature." * 50,
            "stop_hook_active": True
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        assert exc_info.value.code == 0

    def test_skips_short_transcript(self, capsys):
        """Should not output anything for short transcripts."""
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": "Short."
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_outputs_json_for_meaningful_work(self, capsys):
        """Should output JSON with additionalContext when meaningful work detected."""
        transcript = "Implemented the user authentication feature using JWT tokens. Decided to use bcrypt for password hashing." + " " * 200
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "hookSpecificOutput" in output
        assert output["hookSpecificOutput"]["hookEventName"] == "SubagentStop"
        assert "additionalContext" in output["hookSpecificOutput"]
        assert "MANDATORY" in output["hookSpecificOutput"]["additionalContext"]
        assert "pact-backend-coder" in output["hookSpecificOutput"]["additionalContext"]

    def test_no_output_when_no_meaningful_work(self, capsys):
        """Should not output anything when no meaningful work detected."""
        # Long but meaningless transcript
        transcript = "Hello world. " * 100
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_handles_missing_agent_id(self):
        """Should handle input without agent_id gracefully."""
        input_data = json.dumps({
            "transcript": "Some transcript"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        assert exc_info.value.code == 0

    def test_handles_missing_transcript(self):
        """Should handle input without transcript gracefully."""
        input_data = json.dumps({
            "agent_id": "pact-backend-coder"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        assert exc_info.value.code == 0

    def test_handles_exception_gracefully(self, capsys):
        """Should exit 0 and log warning on unexpected errors."""
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": "a" * 300
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(memory_enforce, "did_meaningful_work", side_effect=RuntimeError("test error")), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.err


class TestStopHookRecursionPrevention:
    """Tests specifically for stop hook recursion prevention."""

    def test_stop_hook_active_true_skips_processing(self):
        """When stop_hook_active is True, should skip all processing."""
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": "Implemented the feature. Decided to use pattern X." * 50,
            "stop_hook_active": True
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        assert exc_info.value.code == 0

    def test_stop_hook_active_false_allows_processing(self, capsys):
        """When stop_hook_active is False, should process normally."""
        transcript = "Implemented the user feature and decided to use JWT." + " " * 200
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript,
            "stop_hook_active": False
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""

    def test_stop_hook_active_missing_allows_processing(self, capsys):
        """When stop_hook_active is not present, should process normally."""
        transcript = "Implemented the user feature and decided to use JWT." + " " * 200
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""

    def test_pact_memory_agent_always_skipped(self, capsys):
        """pact-memory-agent should always be skipped regardless of content."""
        transcript = "Saved memory. Created file. Implemented feature. Decided to use X." * 20
        input_data = json.dumps({
            "agent_id": "pact-memory-agent",
            "transcript": transcript,
            "stop_hook_active": False
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out == ""


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_transcript_exactly_at_threshold(self):
        """Transcript at exactly 200 chars should not trigger (< 200 check)."""
        transcript = "a" * 200
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        assert exc_info.value.code == 0

    def test_transcript_just_above_threshold(self, capsys):
        """Transcript at 201 chars with work patterns should trigger."""
        # Need work patterns plus length > 200
        transcript = "implemented the function and decided to use pattern" + " " * 150
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""

    def test_unicode_in_transcript(self, capsys):
        """Should handle unicode characters in transcript."""
        transcript = "Implemented the feature with emoji support. Decided to use UTF-8." + " " * 200
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""

    def test_newlines_in_transcript(self, capsys):
        """Should handle newlines in transcript."""
        transcript = """
        Line 1: Implemented the feature.
        Line 2: Decided to use the factory pattern.
        Line 3: Created the user.py module.
        """ + " " * 200
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""

    def test_special_characters_in_agent_id(self):
        """Should handle special characters in agent ID."""
        input_data = json.dumps({
            "agent_id": "pact-backend-coder-v2.0",
            "transcript": "Implemented feature" * 50
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_enforce.main()
        # Should process since it contains "pact-backend-coder"
        assert exc_info.value.code == 0


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def test_backend_coder_completion(self, capsys):
        """Backend coder completing implementation should trigger enforcement."""
        transcript = """
        I have completed the user authentication endpoint.
        Created auth/handler.py with the login and register functions.
        Decided to use bcrypt for password hashing because of security.
        Implemented JWT token generation with 24h expiry.
        The rationale for this approach is stateless authentication.
        """ + " " * 100
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "MANDATORY" in output["hookSpecificOutput"]["additionalContext"]

    def test_architect_design_completion(self, capsys):
        """Architect completing design should trigger enforcement."""
        transcript = """
        Designed the microservices architecture for the payment system.
        Created a diagram showing the service interactions.
        Defined the api contract between services.
        Chose gRPC for internal communication because of performance.
        """ + " " * 100
        input_data = json.dumps({
            "agent_id": "pact-architect",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""

    def test_test_engineer_completion(self, capsys):
        """Test engineer completing tests should trigger enforcement."""
        transcript = """
        Implemented comprehensive test suite for the auth module.
        Created test/auth_test.py with unit and integration tests.
        Documented the test scenarios in docs/testing.md.
        """ + " " * 100
        input_data = json.dumps({
            "agent_id": "pact-test-engineer",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""

    def test_preparer_research_completion(self, capsys):
        """Preparer completing research should trigger enforcement."""
        transcript = """
        Researched best practices for API versioning.
        Gathered requirements from the product spec.
        Documented findings in docs/preparation/api-research.md.
        Evaluated different versioning strategies.
        """ + " " * 100
        input_data = json.dumps({
            "agent_id": "pact-preparer",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out != ""

    def test_casual_agent_conversation_no_trigger(self, capsys):
        """Agent conversation without work patterns should not trigger."""
        transcript = """
        The user asked about the project structure.
        I explained how the directories are organized.
        No changes were made during this session.
        Just a discussion about code organization principles.
        """ + " " * 150
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_enforce.main()

        captured = capsys.readouterr()
        assert captured.out == ""
