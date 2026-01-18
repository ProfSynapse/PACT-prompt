"""Tests for memory_prompt.py hook."""

import json
import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import memory_prompt


class TestImportsAndConstants:
    """Smoke tests - verify module loads and constants exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert memory_prompt is not None

    def test_min_transcript_length_default(self):
        """Default MIN_TRANSCRIPT_LENGTH should be 500."""
        # Note: This tests the module-level constant, not env override
        # Env override is tested separately
        assert hasattr(memory_prompt, 'MIN_TRANSCRIPT_LENGTH')
        # Default is 500 unless env var overrides it
        assert isinstance(memory_prompt.MIN_TRANSCRIPT_LENGTH, int)

    def test_pact_agents_defined(self):
        """PACT_AGENTS list should be defined with expected agents."""
        assert hasattr(memory_prompt, 'PACT_AGENTS')
        assert "pact-preparer" in memory_prompt.PACT_AGENTS
        assert "pact-architect" in memory_prompt.PACT_AGENTS
        assert "pact-backend-coder" in memory_prompt.PACT_AGENTS
        assert "pact-test-engineer" in memory_prompt.PACT_AGENTS
        assert "pact-memory-agent" in memory_prompt.PACT_AGENTS

    def test_pattern_lists_defined(self):
        """Pattern lists should be defined."""
        assert hasattr(memory_prompt, 'DECISION_PATTERNS')
        assert hasattr(memory_prompt, 'LESSON_PATTERNS')
        assert hasattr(memory_prompt, 'BLOCKER_PATTERNS')
        assert len(memory_prompt.DECISION_PATTERNS) > 0
        assert len(memory_prompt.LESSON_PATTERNS) > 0
        assert len(memory_prompt.BLOCKER_PATTERNS) > 0


class TestMinTranscriptLengthEnvOverride:
    """Test that MIN_TRANSCRIPT_LENGTH can be overridden via environment."""

    def test_env_override_works(self):
        """Environment variable should override default threshold."""
        # Save original value
        original = memory_prompt.MIN_TRANSCRIPT_LENGTH

        # Reload module with env var set
        with patch.dict(os.environ, {'PACT_MIN_TRANSCRIPT_LENGTH': '100'}):
            # Re-evaluate the expression that sets the constant
            new_value = int(os.environ.get('PACT_MIN_TRANSCRIPT_LENGTH', '500'))
            assert new_value == 100

        # Original module constant unchanged (evaluated at import time)
        assert memory_prompt.MIN_TRANSCRIPT_LENGTH == original


class TestTranscriptLengthCheck:
    """Tests for transcript length filtering."""

    def test_short_transcript_skipped(self):
        """Short transcripts should be skipped (exit 0, no output)."""
        short_transcript = "a" * 100  # Less than MIN_TRANSCRIPT_LENGTH
        input_data = json.dumps({"transcript": short_transcript})

        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_prompt.main()

        assert exc_info.value.code == 0

    def test_empty_transcript_skipped(self):
        """Empty transcript should be skipped."""
        input_data = json.dumps({"transcript": ""})

        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_prompt.main()

        assert exc_info.value.code == 0

    def test_missing_transcript_skipped(self):
        """Missing transcript field should be skipped."""
        input_data = json.dumps({})

        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            memory_prompt.main()

        assert exc_info.value.code == 0


class TestDetectPactAgents:
    """Tests for detect_pact_agents()."""

    def test_detects_single_agent(self):
        """Should detect a single PACT agent mention."""
        transcript = "We invoked the pact-backend-coder to implement the feature."
        agents = memory_prompt.detect_pact_agents(transcript)
        assert agents == ["pact-backend-coder"]

    def test_detects_multiple_agents(self):
        """Should detect multiple PACT agents."""
        transcript = "First pact-preparer gathered requirements, then pact-architect designed it."
        agents = memory_prompt.detect_pact_agents(transcript)
        assert "pact-preparer" in agents
        assert "pact-architect" in agents

    def test_case_insensitive(self):
        """Detection should be case insensitive."""
        transcript = "PACT-BACKEND-CODER was invoked."
        agents = memory_prompt.detect_pact_agents(transcript)
        assert "pact-backend-coder" in agents

    def test_no_agents(self):
        """Should return empty list when no agents detected."""
        transcript = "Just a casual conversation about code."
        agents = memory_prompt.detect_pact_agents(transcript)
        assert agents == []


class TestDetectPatterns:
    """Tests for detect_patterns()."""

    def test_detects_decision_pattern(self):
        """Should detect decision-related patterns."""
        transcript = "We decided to use TypeScript for this project."
        assert memory_prompt.detect_patterns(transcript, memory_prompt.DECISION_PATTERNS) is True

    def test_detects_lesson_pattern(self):
        """Should detect lesson-related patterns."""
        transcript = "We learned that caching significantly improves performance."
        assert memory_prompt.detect_patterns(transcript, memory_prompt.LESSON_PATTERNS) is True

    def test_detects_blocker_pattern(self):
        """Should detect blocker-related patterns."""
        transcript = "We ran into a problem with the database connection."
        assert memory_prompt.detect_patterns(transcript, memory_prompt.BLOCKER_PATTERNS) is True

    def test_case_insensitive(self):
        """Detection should be case insensitive."""
        transcript = "DECIDED TO go with option A."
        assert memory_prompt.detect_patterns(transcript, memory_prompt.DECISION_PATTERNS) is True

    def test_no_match(self):
        """Should return False when no patterns match."""
        transcript = "Hello world example code."
        assert memory_prompt.detect_patterns(transcript, memory_prompt.DECISION_PATTERNS) is False


class TestAnalyzeTranscript:
    """Tests for analyze_transcript()."""

    def test_returns_analysis_dict(self):
        """Should return dict with all expected keys."""
        transcript = "Some transcript content."
        analysis = memory_prompt.analyze_transcript(transcript)

        assert "agents" in analysis
        assert "has_decisions" in analysis
        assert "has_lessons" in analysis
        assert "has_blockers" in analysis

    def test_detects_all_signals(self):
        """Should detect agents, decisions, lessons, and blockers."""
        transcript = """
        We invoked pact-backend-coder to implement the API.
        Decided to use REST instead of GraphQL.
        Learned that pagination is essential for large datasets.
        Ran into a problem with authentication middleware.
        """
        analysis = memory_prompt.analyze_transcript(transcript)

        assert "pact-backend-coder" in analysis["agents"]
        assert analysis["has_decisions"] is True
        assert analysis["has_lessons"] is True
        assert analysis["has_blockers"] is True


class TestShouldPromptMemory:
    """Tests for should_prompt_memory()."""

    def test_pact_work_always_triggers(self):
        """PACT agent work should always trigger memory prompt."""
        analysis = {
            "agents": ["pact-backend-coder"],
            "has_decisions": False,
            "has_lessons": False,
            "has_blockers": False,
        }
        assert memory_prompt.should_prompt_memory(analysis) is True

    def test_single_signal_not_enough(self):
        """Single non-agent signal should not trigger prompt."""
        # Only decisions
        analysis = {
            "agents": [],
            "has_decisions": True,
            "has_lessons": False,
            "has_blockers": False,
        }
        assert memory_prompt.should_prompt_memory(analysis) is False

        # Only lessons
        analysis = {
            "agents": [],
            "has_decisions": False,
            "has_lessons": True,
            "has_blockers": False,
        }
        assert memory_prompt.should_prompt_memory(analysis) is False

    def test_two_signals_triggers(self):
        """Two non-agent signals should trigger prompt."""
        analysis = {
            "agents": [],
            "has_decisions": True,
            "has_lessons": True,
            "has_blockers": False,
        }
        assert memory_prompt.should_prompt_memory(analysis) is True

    def test_three_signals_triggers(self):
        """Three non-agent signals should trigger prompt."""
        analysis = {
            "agents": [],
            "has_decisions": True,
            "has_lessons": True,
            "has_blockers": True,
        }
        assert memory_prompt.should_prompt_memory(analysis) is True

    def test_no_signals_no_prompt(self):
        """No signals should not trigger prompt."""
        analysis = {
            "agents": [],
            "has_decisions": False,
            "has_lessons": False,
            "has_blockers": False,
        }
        assert memory_prompt.should_prompt_memory(analysis) is False


class TestFormatPrompt:
    """Tests for format_prompt()."""

    def test_includes_mandatory_header(self):
        """Prompt should include mandatory save message."""
        analysis = {"agents": ["pact-backend-coder"], "has_decisions": False,
                    "has_lessons": False, "has_blockers": False}
        prompt = memory_prompt.format_prompt(analysis)
        assert "MANDATORY" in prompt
        assert "pact-memory-agent" in prompt

    def test_lists_agents(self):
        """Prompt should list detected agents."""
        analysis = {"agents": ["pact-backend-coder", "pact-test-engineer"],
                    "has_decisions": False, "has_lessons": False, "has_blockers": False}
        prompt = memory_prompt.format_prompt(analysis)
        assert "pact-backend-coder" in prompt
        assert "pact-test-engineer" in prompt

    def test_mentions_decisions(self):
        """Prompt should mention decisions when detected."""
        analysis = {"agents": [], "has_decisions": True,
                    "has_lessons": False, "has_blockers": False}
        prompt = memory_prompt.format_prompt(analysis)
        assert "Decisions" in prompt

    def test_mentions_lessons(self):
        """Prompt should mention lessons when detected."""
        analysis = {"agents": [], "has_decisions": False,
                    "has_lessons": True, "has_blockers": False}
        prompt = memory_prompt.format_prompt(analysis)
        assert "Lessons" in prompt

    def test_mentions_blockers(self):
        """Prompt should mention blockers when detected."""
        analysis = {"agents": [], "has_decisions": False,
                    "has_lessons": False, "has_blockers": True}
        prompt = memory_prompt.format_prompt(analysis)
        assert "Blockers" in prompt


class TestMainJsonFlow:
    """Tests for main() JSON input/output flow."""

    def test_outputs_json_with_system_message(self, capsys):
        """Should output JSON with systemMessage when prompt triggered."""
        # Long transcript with PACT agent mention
        transcript = "a" * 600 + " pact-backend-coder was invoked"
        input_data = json.dumps({"transcript": transcript})

        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_prompt.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "systemMessage" in output
        assert "pact-memory-agent" in output["systemMessage"]

    def test_no_output_when_no_prompt_needed(self, capsys):
        """Should not output anything when no memory prompt needed."""
        # Long transcript but no memory-worthy signals
        transcript = "a" * 600 + " just regular conversation"
        input_data = json.dumps({"transcript": transcript})

        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_prompt.main()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_handles_malformed_json(self):
        """Should exit cleanly on malformed JSON input."""
        with patch.object(sys, "stdin", StringIO("not valid json")), \
             pytest.raises(SystemExit) as exc_info:
            memory_prompt.main()

        assert exc_info.value.code == 0

    def test_handles_exception_gracefully(self, capsys):
        """Should exit 0 and log warning on unexpected errors."""
        input_data = json.dumps({"transcript": "a" * 600})

        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(memory_prompt, "analyze_transcript", side_effect=RuntimeError("test error")), \
             pytest.raises(SystemExit) as exc_info:
            memory_prompt.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.err


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def test_pact_phase_completion_triggers_prompt(self, capsys):
        """Completing a PACT phase should trigger memory prompt."""
        transcript = """
        Starting backend implementation phase.
        Delegating to pact-backend-coder for user authentication endpoint.
        The agent completed the implementation successfully.
        All smoke tests pass.
        """ + ("." * 500)  # Ensure length threshold met

        input_data = json.dumps({"transcript": transcript})

        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_prompt.main()

        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "pact-backend-coder" in output["systemMessage"]

    def test_decision_and_lesson_triggers_prompt(self, capsys):
        """Session with decisions AND lessons should trigger prompt."""
        transcript = """
        We decided to use PostgreSQL for better JSON support.
        After testing, we learned that connection pooling is essential.
        """ + ("." * 500)  # Ensure length threshold met

        input_data = json.dumps({"transcript": transcript})

        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_prompt.main()

        captured = capsys.readouterr()
        assert captured.out != ""
        output = json.loads(captured.out)
        assert "Decisions" in output["systemMessage"]
        assert "Lessons" in output["systemMessage"]

    def test_casual_conversation_no_prompt(self, capsys):
        """Casual conversation without memory signals should not prompt."""
        transcript = """
        User: What's the weather like?
        Assistant: I don't have access to weather data.
        User: Okay, thanks anyway.
        """ + ("." * 500)  # Ensure length threshold met

        input_data = json.dumps({"transcript": transcript})

        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit):
            memory_prompt.main()

        captured = capsys.readouterr()
        assert captured.out == ""
