"""
Fuzz tests for the patterns module using Hypothesis.

Tests regex patterns for robustness against pathological inputs,
ReDoS vulnerabilities, and unicode handling.
"""

import re
import time
from pathlib import Path

import pytest

# Try to import hypothesis, skip tests if not available
try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Create dummy module/decorators for when hypothesis isn't installed
    # These allow the module to load even without hypothesis
    class DummyStrategies:
        """Dummy strategies module for when hypothesis isn't installed."""
        @staticmethod
        def text(*args, **kwargs):
            return None
        @staticmethod
        def sampled_from(*args, **kwargs):
            return None
        @staticmethod
        def integers(*args, **kwargs):
            return None
        @staticmethod
        def booleans():
            return None
        @staticmethod
        def lists(*args, **kwargs):
            return None
        @staticmethod
        def characters(*args, **kwargs):
            return None
        @staticmethod
        def one_of(*args, **kwargs):
            return None
        @staticmethod
        def just(*args, **kwargs):
            return None

    st = DummyStrategies()

    def given(*args, **kwargs):
        """Dummy given decorator."""
        def decorator(func):
            return func
        return decorator

    def settings(*args, **kwargs):
        """Dummy settings decorator."""
        def decorator(func):
            return func
        return decorator

    def assume(condition):
        """Dummy assume function."""
        pass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))

from refresh.patterns import (
    TRIGGER_PATTERNS,
    TERMINATION_SIGNALS,
    CONTEXT_EXTRACTORS,
    PENDING_ACTION_PATTERNS,
    PACT_AGENT_PATTERN,
    TASK_TOOL_PATTERN,
    SUBAGENT_TYPE_PATTERN,
    is_termination_signal,
    extract_context_value,
)


# Skip all tests in this module if hypothesis is not available
pytestmark = pytest.mark.skipif(
    not HYPOTHESIS_AVAILABLE,
    reason="hypothesis library not installed"
)


class TestTriggerPatternsFuzz:
    """Fuzz tests for workflow trigger patterns."""

    @given(st.text(min_size=0, max_size=10000))
    @settings(max_examples=200, deadline=1000)
    def test_trigger_patterns_no_crash(self, content: str):
        """Test trigger patterns don't crash on arbitrary input."""
        for name, pattern in TRIGGER_PATTERNS.items():
            # Should not raise any exception
            result = pattern.search(content)
            # Result should be None or a Match object
            assert result is None or hasattr(result, 'group')

    @given(st.text(min_size=0, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',))))
    @settings(max_examples=100, deadline=500)
    def test_trigger_patterns_unicode_handling(self, content: str):
        """Test trigger patterns handle unicode correctly."""
        for name, pattern in TRIGGER_PATTERNS.items():
            result = pattern.search(content)
            assert result is None or hasattr(result, 'group')

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=100, deadline=2000)
    def test_trigger_patterns_no_redos(self, content: str):
        """Test trigger patterns don't exhibit ReDoS behavior."""
        start_time = time.time()

        for name, pattern in TRIGGER_PATTERNS.items():
            pattern.search(content)

        elapsed = time.time() - start_time
        # Should complete in reasonable time (< 1 second for all patterns)
        assert elapsed < 1.0, f"Patterns took too long: {elapsed}s"


class TestTerminationSignalsFuzz:
    """Fuzz tests for termination signal patterns."""

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=200, deadline=1000)
    def test_termination_signals_no_crash(self, content: str):
        """Test termination signal detection doesn't crash on arbitrary input."""
        workflows = ["peer-review", "orchestrate", "plan-mode", "comPACT", "rePACT"]

        for workflow in workflows:
            # Should not raise any exception
            result = is_termination_signal(content, workflow)
            assert isinstance(result, bool)

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=100, deadline=2000)
    def test_termination_signals_no_redos(self, content: str):
        """Test termination signal patterns don't exhibit ReDoS behavior."""
        start_time = time.time()

        for workflow, signals in TERMINATION_SIGNALS.items():
            for signal_pattern in signals:
                re.search(signal_pattern, content, re.IGNORECASE)

        elapsed = time.time() - start_time
        assert elapsed < 1.0, f"Termination signals took too long: {elapsed}s"

    @given(st.sampled_from(["peer-review", "orchestrate", "plan-mode", "comPACT", "rePACT"]),
           st.text(min_size=0, max_size=1000))
    @settings(max_examples=200, deadline=500)
    def test_is_termination_signal_deterministic(self, workflow: str, content: str):
        """Test is_termination_signal returns consistent results."""
        result1 = is_termination_signal(content, workflow)
        result2 = is_termination_signal(content, workflow)
        assert result1 == result2


class TestContextExtractorsFuzz:
    """Fuzz tests for context extraction patterns."""

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=200, deadline=1000)
    def test_context_extractors_no_crash(self, content: str):
        """Test context extractors don't crash on arbitrary input."""
        for key, pattern in CONTEXT_EXTRACTORS.items():
            result = pattern.search(content)
            assert result is None or hasattr(result, 'group')

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=100, deadline=2000)
    def test_context_extractors_no_redos(self, content: str):
        """Test context extractor patterns don't exhibit ReDoS behavior."""
        start_time = time.time()

        for key, pattern in CONTEXT_EXTRACTORS.items():
            pattern.search(content)

        elapsed = time.time() - start_time
        assert elapsed < 1.0, f"Context extractors took too long: {elapsed}s"

    @given(st.sampled_from(["pr_number", "branch_name", "task_summary"]),
           st.text(min_size=0, max_size=1000))
    @settings(max_examples=200, deadline=500)
    def test_extract_context_value_no_crash(self, key: str, content: str):
        """Test extract_context_value doesn't crash."""
        result = extract_context_value(content, key)
        assert result is None or isinstance(result, str)

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=100, deadline=500)
    def test_extract_context_value_unknown_key(self, content: str):
        """Test extract_context_value handles unknown keys gracefully."""
        result = extract_context_value(content, "nonexistent_key_xyz")
        assert result is None


class TestPendingActionPatternsFuzz:
    """Fuzz tests for pending action patterns."""

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=200, deadline=1000)
    def test_pending_action_patterns_no_crash(self, content: str):
        """Test pending action patterns don't crash on arbitrary input."""
        for name, pattern in PENDING_ACTION_PATTERNS.items():
            result = pattern.search(content)
            assert result is None or hasattr(result, 'group')

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=100, deadline=2000)
    def test_pending_action_patterns_no_redos(self, content: str):
        """Test pending action patterns don't exhibit ReDoS behavior."""
        start_time = time.time()

        for name, pattern in PENDING_ACTION_PATTERNS.items():
            pattern.search(content)

        elapsed = time.time() - start_time
        assert elapsed < 1.0, f"Pending action patterns took too long: {elapsed}s"


class TestAgentPatternsFuzz:
    """Fuzz tests for agent-related patterns."""

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=200, deadline=1000)
    def test_pact_agent_pattern_no_crash(self, content: str):
        """Test PACT agent pattern doesn't crash."""
        result = PACT_AGENT_PATTERN.search(content)
        assert result is None or hasattr(result, 'group')

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=200, deadline=1000)
    def test_task_tool_pattern_no_crash(self, content: str):
        """Test Task tool pattern doesn't crash."""
        result = TASK_TOOL_PATTERN.search(content)
        assert result is None or hasattr(result, 'group')

    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=200, deadline=1000)
    def test_subagent_type_pattern_no_crash(self, content: str):
        """Test subagent type pattern doesn't crash."""
        result = SUBAGENT_TYPE_PATTERN.search(content)
        assert result is None or hasattr(result, 'group')


class TestPathologicalInputs:
    """Tests for known pathological regex inputs."""

    def test_repeated_characters(self):
        """Test patterns handle extremely repeated characters."""
        # Common ReDoS triggers
        pathological_inputs = [
            "a" * 10000,
            "." * 10000,
            "*" * 10000,
            " " * 10000,
            "\n" * 10000,
            "\\n" * 5000,
            "PR #" + "9" * 10000,
            "/PACT:" + "x" * 10000,
        ]

        for content in pathological_inputs:
            start_time = time.time()

            # Test all patterns
            for name, pattern in TRIGGER_PATTERNS.items():
                pattern.search(content)

            for key, pattern in CONTEXT_EXTRACTORS.items():
                pattern.search(content)

            for name, pattern in PENDING_ACTION_PATTERNS.items():
                pattern.search(content)

            PACT_AGENT_PATTERN.search(content)
            TASK_TOOL_PATTERN.search(content)
            SUBAGENT_TYPE_PATTERN.search(content)

            elapsed = time.time() - start_time
            assert elapsed < 1.0, f"Pathological input took too long: {elapsed}s on input length {len(content)}"

    def test_nested_patterns(self):
        """Test patterns handle nested/recursive-like structures."""
        nested_inputs = [
            "(((" * 1000 + ")))" * 1000,
            "[[[[" * 500 + "]]]]" * 500,
            "{{{" * 1000 + "}}}" * 1000,
            "<<<" * 1000 + ">>>" * 1000,
        ]

        for content in nested_inputs:
            start_time = time.time()

            for name, pattern in TRIGGER_PATTERNS.items():
                pattern.search(content)

            elapsed = time.time() - start_time
            assert elapsed < 1.0, f"Nested pattern took too long: {elapsed}s"

    def test_alternating_patterns(self):
        """Test patterns handle alternating character sequences."""
        alternating_inputs = [
            "ab" * 5000,
            "PR PR PR " * 1000,
            "/PACT:x /PACT:y " * 500,
            "merged closed merged closed " * 500,
        ]

        for content in alternating_inputs:
            start_time = time.time()

            for workflow in ["peer-review", "orchestrate"]:
                is_termination_signal(content, workflow)

            elapsed = time.time() - start_time
            assert elapsed < 1.0, f"Alternating pattern took too long: {elapsed}s"


class TestUnicodeEdgeCases:
    """Tests for unicode edge cases."""

    def test_unicode_categories(self):
        """Test patterns handle various unicode categories."""
        unicode_inputs = [
            # CJK characters
            "" * 1000,
            # Arabic
            "" * 1000,
            # Emoji
            "" * 500,
            # Mixed scripts
            "Hello " + "world",
            # Zero-width characters
            "\u200b" * 1000,  # Zero-width space
            "\u200d" * 1000,  # Zero-width joiner
            # RTL markers
            "\u200f" * 1000,  # Right-to-left mark
            # Combining characters
            "e\u0301" * 1000,  # e + combining acute accent
        ]

        for content in unicode_inputs:
            # Should not crash
            for name, pattern in TRIGGER_PATTERNS.items():
                result = pattern.search(content)
                assert result is None or hasattr(result, 'group')

    def test_mixed_unicode_with_patterns(self):
        """Test patterns work when unicode is mixed with expected content."""
        # These should still match even with unicode around them
        assert TRIGGER_PATTERNS["peer-review"].search("/PACT:peer-review ") is not None
        assert TRIGGER_PATTERNS["orchestrate"].search("/PACT:orchestrate") is not None

        # These shouldn't crash
        assert CONTEXT_EXTRACTORS["pr_number"].search("PR #123 ") is not None
        assert is_termination_signal("PR merged ", "peer-review") is True

    @given(st.text(min_size=10, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),  # Letters, digits, spaces
        whitelist_characters='/PACT:-_#'
    )))
    @settings(max_examples=100, deadline=500)
    def test_realistic_mixed_content(self, content: str):
        """Test patterns with realistic mixed alphanumeric content."""
        for name, pattern in TRIGGER_PATTERNS.items():
            result = pattern.search(content)
            assert result is None or hasattr(result, 'group')
