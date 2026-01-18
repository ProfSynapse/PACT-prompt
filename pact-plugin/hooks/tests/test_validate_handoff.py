"""Tests for validate_handoff.py hook."""

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import validate_handoff


class TestImportsAndConstants:
    """Smoke tests - verify module loads and key elements exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert validate_handoff is not None

    def test_handoff_elements_defined(self):
        """HANDOFF_ELEMENTS constant should be defined with required keys."""
        assert hasattr(validate_handoff, "HANDOFF_ELEMENTS")
        assert "what_produced" in validate_handoff.HANDOFF_ELEMENTS
        assert "key_decisions" in validate_handoff.HANDOFF_ELEMENTS
        assert "next_steps" in validate_handoff.HANDOFF_ELEMENTS

    def test_phase_completing_agents_defined(self):
        """PHASE_COMPLETING_AGENTS should be defined with expected agents."""
        assert hasattr(validate_handoff, "PHASE_COMPLETING_AGENTS")
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
            assert agent in validate_handoff.PHASE_COMPLETING_AGENTS

    def test_key_functions_exist(self):
        """Key functions should be defined."""
        assert callable(validate_handoff.validate_handoff)
        assert callable(validate_handoff.is_pact_agent)
        assert callable(validate_handoff.is_phase_completing_agent)
        assert callable(validate_handoff.main)


class TestValidateHandoff:
    """Tests for validate_handoff() function."""

    def test_empty_header_fails(self):
        """Empty header (## Summary with no content) should fail validation."""
        transcript = "## Summary\n\n"
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        assert is_valid is False
        assert len(missing) > 0

    def test_header_with_minimal_whitespace_fails(self):
        """Header with only whitespace content should fail."""
        transcript = "## Summary\n   \n   \n"
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        assert is_valid is False

    def test_header_with_insufficient_content_fails(self):
        """Header with less than 20 chars of content should fail."""
        transcript = "## Summary\nShort."
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        # Content "Short." is only 6 chars, so it should check implicit elements
        # Without implicit elements, it should fail
        assert is_valid is False

    def test_header_with_sufficient_content_passes(self):
        """Header with >= 20 chars of content should pass."""
        transcript = "## Summary\nThis is a properly formatted handoff with enough content to pass validation."
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        assert is_valid is True
        assert missing == []

    def test_handoff_header_case_insensitive(self):
        """Handoff header should be case insensitive."""
        transcript = "## HANDOFF\nThis is a properly formatted handoff with enough content to pass validation."
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        assert is_valid is True

    def test_deliverables_header_works(self):
        """Deliverables header should also work."""
        transcript = "## Deliverables\nThis is a properly formatted handoff with enough content to pass validation."
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        assert is_valid is True

    def test_output_header_works(self):
        """Output header should also work."""
        transcript = "## Output\nThis is a properly formatted handoff with enough content to pass validation."
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        assert is_valid is True


class TestImplicitHandoffKeywords:
    """Tests for implicit handoff element detection."""

    def test_all_implicit_elements_present(self):
        """Transcript with all implicit elements should pass."""
        transcript = """
        I created the new authentication module and implemented the login endpoint.
        I decided to use JWT tokens because they work better for our stateless API.
        The next step is for the test engineer to verify the implementation.
        """
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        assert is_valid is True
        assert missing == []

    def test_two_out_of_three_elements_passes(self):
        """Having 2 out of 3 elements should still pass (missing <= 1)."""
        transcript = """
        I created the new authentication module and implemented the login endpoint.
        The next step is for the test engineer to verify the implementation.
        """
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        # Should have "what_produced" and "next_steps" but missing "key_decisions"
        assert is_valid is True
        assert len(missing) <= 1

    def test_one_out_of_three_elements_fails(self):
        """Having only 1 out of 3 elements should fail (missing > 1)."""
        transcript = """
        The weather is nice today. I went for a walk.
        There are many trees in the park. The sky is blue.
        I created something but that's all I can say.
        """
        is_valid, missing = validate_handoff.validate_handoff(transcript)
        # Only "what_produced" might match, missing "key_decisions" and "next_steps"
        assert is_valid is False
        assert len(missing) >= 2

    def test_what_produced_patterns(self):
        """Various what_produced patterns should be detected."""
        patterns_transcripts = [
            "I produced the API documentation.",
            "Created a new component for the dashboard.",
            "Generated the database schema.",
            "The output includes three new files.",
            "Implemented the user service.",
            "Wrote the validation logic.",
            "Built the authentication middleware.",
            "Delivered the frontend components.",
            "Completed the migration script.",
            "Finished the integration work.",
        ]
        for transcript in patterns_transcripts:
            # Add next steps to ensure we have 2/3 elements
            full_transcript = transcript + " Next the tester should verify."
            is_valid, _ = validate_handoff.validate_handoff(full_transcript)
            assert is_valid is True, f"Failed for: {transcript}"

    def test_key_decisions_patterns(self):
        """Various key_decisions patterns should be detected."""
        patterns_transcripts = [
            "I made a decision to use Redis.",
            "Chose PostgreSQL over MySQL.",
            "Selected the observer pattern.",
            "Opted for a microservices approach.",
            "The rationale is performance.",
            "The reason for this is scalability.",
            "I did this because of security.",
            "The trade-off is complexity vs speed.",
            "The approach uses dependency injection.",
            "Decided to go with async processing.",
            "Went with a functional style.",
            "Picked the factory pattern.",
        ]
        for transcript in patterns_transcripts:
            # Add what produced to ensure we have 2/3 elements
            full_transcript = "Created the module. " + transcript
            is_valid, _ = validate_handoff.validate_handoff(full_transcript)
            assert is_valid is True, f"Failed for: {transcript}"

    def test_next_steps_patterns(self):
        """Various next_steps patterns should be detected."""
        patterns_transcripts = [
            "Next, implement the tests.",
            "This needs further review.",
            "Requires database migration.",
            "Depends on the auth service.",
            "You should run the linter.",
            "Must update the documentation.",
            "I recommend adding caching.",
            "Follow-up with integration testing.",
            "Remaining work includes cleanup.",
            "The todo is to add error handling.",
            "Action item: deploy to staging.",
            "The test engineer should verify this.",
            "Next agent needs to review security.",
            "Next phase is testing.",
        ]
        for transcript in patterns_transcripts:
            # Add what produced to ensure we have 2/3 elements
            full_transcript = "Created the module. " + transcript
            is_valid, _ = validate_handoff.validate_handoff(full_transcript)
            assert is_valid is True, f"Failed for: {transcript}"


class TestIsPactAgent:
    """Tests for is_pact_agent() function."""

    def test_pact_dash_prefix(self):
        """Agent IDs starting with pact- should return True."""
        assert validate_handoff.is_pact_agent("pact-backend-coder") is True
        assert validate_handoff.is_pact_agent("pact-test-engineer") is True

    def test_pact_uppercase_dash_prefix(self):
        """Agent IDs starting with PACT- should return True."""
        assert validate_handoff.is_pact_agent("PACT-backend-coder") is True

    def test_pact_underscore_prefix(self):
        """Agent IDs starting with pact_ should return True."""
        assert validate_handoff.is_pact_agent("pact_backend_coder") is True

    def test_pact_uppercase_underscore_prefix(self):
        """Agent IDs starting with PACT_ should return True."""
        assert validate_handoff.is_pact_agent("PACT_backend_coder") is True

    def test_non_pact_agent(self):
        """Non-PACT agent IDs should return False."""
        assert validate_handoff.is_pact_agent("other-agent") is False
        assert validate_handoff.is_pact_agent("my-custom-agent") is False

    def test_empty_agent_id(self):
        """Empty agent ID should return False."""
        assert validate_handoff.is_pact_agent("") is False

    def test_none_agent_id(self):
        """None agent ID should return False."""
        assert validate_handoff.is_pact_agent(None) is False


class TestIsPhaseCompletingAgent:
    """Tests for is_phase_completing_agent() function."""

    def test_phase_completing_agents_return_true(self):
        """All phase-completing agents should return True."""
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
            assert validate_handoff.is_phase_completing_agent(agent) is True

    def test_utility_agents_return_false(self):
        """Utility agents like pact-memory-agent should return False."""
        assert validate_handoff.is_phase_completing_agent("pact-memory-agent") is False

    def test_case_insensitive(self):
        """Agent ID matching should be case insensitive."""
        assert validate_handoff.is_phase_completing_agent("PACT-BACKEND-CODER") is True
        assert validate_handoff.is_phase_completing_agent("Pact-Architect") is True

    def test_empty_agent_id(self):
        """Empty agent ID should return False."""
        assert validate_handoff.is_phase_completing_agent("") is False

    def test_none_agent_id(self):
        """None agent ID should return False."""
        assert validate_handoff.is_phase_completing_agent(None) is False

    def test_non_pact_agent(self):
        """Non-PACT agent should return False."""
        assert validate_handoff.is_phase_completing_agent("other-agent") is False


class TestMain:
    """Tests for main() JSON input/output flow."""

    def test_handles_malformed_json(self):
        """Should exit cleanly on malformed JSON input."""
        with patch.object(sys, "stdin", StringIO("not valid json")), \
             pytest.raises(SystemExit) as exc_info:
            validate_handoff.main()
        assert exc_info.value.code == 0

    def test_handles_empty_input(self):
        """Should exit cleanly on empty input."""
        with patch.object(sys, "stdin", StringIO("")), \
             pytest.raises(SystemExit) as exc_info:
            validate_handoff.main()
        assert exc_info.value.code == 0

    def test_skips_non_pact_agent(self):
        """Should exit silently for non-PACT agents."""
        input_data = json.dumps({
            "agent_id": "other-agent",
            "transcript": "Some transcript content here."
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            validate_handoff.main()
        assert exc_info.value.code == 0

    def test_skips_utility_pact_agents(self):
        """Should skip validation for utility agents like pact-memory-agent."""
        input_data = json.dumps({
            "agent_id": "pact-memory-agent",
            "transcript": "This transcript has no handoff info at all."
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            validate_handoff.main()
        assert exc_info.value.code == 0

    def test_skips_short_transcripts(self):
        """Should skip validation for very short transcripts (< 100 chars)."""
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": "Short."
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            validate_handoff.main()
        assert exc_info.value.code == 0

    def test_outputs_warning_for_invalid_handoff(self, capsys):
        """Should output warning message for invalid handoff."""
        # Transcript with no handoff elements
        transcript = "x" * 150  # Long enough to pass length check but no handoff info
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            validate_handoff.main()

        captured = capsys.readouterr()
        if captured.out:  # Should have output
            output = json.loads(captured.out)
            assert "systemMessage" in output
            assert "pact-backend-coder" in output["systemMessage"]
            assert "missing" in output["systemMessage"].lower()

    def test_no_output_for_valid_handoff(self, capsys):
        """Should not output anything for valid handoff."""
        transcript = """
        ## Summary
        This is a complete handoff with all the necessary information about what was done.
        Created the authentication module. Decided to use JWT. Next: testing phase.
        """ + "x" * 100  # Ensure it's long enough
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            validate_handoff.main()

        captured = capsys.readouterr()
        # Valid handoff should produce no output
        assert captured.out == ""

    def test_handles_missing_transcript_key(self):
        """Should handle input without transcript key gracefully."""
        input_data = json.dumps({
            "agent_id": "pact-backend-coder"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            validate_handoff.main()
        # Should exit cleanly (short transcript check will catch empty string)
        assert exc_info.value.code == 0

    def test_handles_missing_agent_id_key(self):
        """Should handle input without agent_id key gracefully."""
        input_data = json.dumps({
            "transcript": "Some transcript"
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            validate_handoff.main()
        # Should exit cleanly (is_pact_agent handles empty string)
        assert exc_info.value.code == 0

    def test_warning_includes_good_example(self, capsys):
        """Warning message should include a good handoff example."""
        transcript = "y" * 150  # Long enough but no handoff elements
        input_data = json.dumps({
            "agent_id": "pact-backend-coder",
            "transcript": transcript
        })
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            validate_handoff.main()

        captured = capsys.readouterr()
        if captured.out:
            output = json.loads(captured.out)
            message = output.get("systemMessage", "")
            assert "## Summary" in message or "example" in message.lower()
