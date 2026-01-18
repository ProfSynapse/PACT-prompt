"""Common fixtures for pact-plugin hooks tests.

This module provides reusable pytest fixtures for testing hook scripts.
Fixtures are automatically discovered by pytest and available to all test files.
"""

import json
import subprocess
import sys
from io import StringIO
from pathlib import Path
from typing import Callable
from unittest.mock import patch

import pytest


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def hooks_dir() -> Path:
    """Return the path to the hooks directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def tests_dir() -> Path:
    """Return the path to the tests directory."""
    return Path(__file__).parent


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================

@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory structure.

    Returns a clean temporary directory that can be used as CLAUDE_PROJECT_DIR.
    """
    return tmp_path


@pytest.fixture
def project_with_docs(tmp_path: Path) -> Path:
    """Create a project directory with standard PACT docs structure.

    Creates:
    - docs/preparation/
    - docs/architecture/
    - docs/decision-logs/
    - docs/review/
    """
    for subdir in ["preparation", "architecture", "decision-logs", "review"]:
        (tmp_path / "docs" / subdir).mkdir(parents=True)
    return tmp_path


@pytest.fixture
def project_with_populated_docs(project_with_docs: Path) -> Path:
    """Create a project directory with populated docs directories.

    Creates the same structure as project_with_docs but with files in each.
    """
    (project_with_docs / "docs" / "preparation" / "requirements.md").write_text("# Requirements")
    (project_with_docs / "docs" / "architecture" / "design.md").write_text("# Design")
    (project_with_docs / "docs" / "decision-logs" / "feature.md").write_text("# Decisions")
    (project_with_docs / "docs" / "review" / "test-report.md").write_text("# Tests")
    return project_with_docs


# ============================================================================
# JSON Input Fixtures
# ============================================================================

@pytest.fixture
def make_json_input() -> Callable[..., str]:
    """Factory fixture to create JSON input strings.

    Usage:
        json_str = make_json_input(transcript="...", agent_id="...")
    """
    def _make(**kwargs) -> str:
        return json.dumps(kwargs)
    return _make


@pytest.fixture
def stdin_json() -> Callable[[dict], None]:
    """Factory fixture to patch stdin with JSON data.

    Returns a context manager that patches sys.stdin.

    Usage:
        with stdin_json({"transcript": "..."}):
            module.main()
    """
    def _patch(data: dict):
        return patch.object(sys, "stdin", StringIO(json.dumps(data)))
    return _patch


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def mock_project_dir(tmp_path: Path):
    """Context manager to mock CLAUDE_PROJECT_DIR environment variable.

    Usage:
        with mock_project_dir:
            # CLAUDE_PROJECT_DIR is set to tmp_path
    """
    import os
    return patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)})


# ============================================================================
# Shell Script Runner Fixtures
# ============================================================================

@pytest.fixture
def run_shell_hook(hooks_dir: Path) -> Callable[[str, dict | str], tuple[int, str, str]]:
    """Factory fixture to run shell hook scripts.

    Args:
        script_name: Name of the shell script (e.g., "s5-credential-scan.sh")
        json_input: JSON input as dict or string

    Returns:
        Tuple of (exit_code, stdout, stderr)

    Usage:
        exit_code, stdout, stderr = run_shell_hook("s5-credential-scan.sh", {...})
    """
    def _run(script_name: str, json_input: dict | str) -> tuple[int, str, str]:
        script_path = hooks_dir / script_name
        if isinstance(json_input, dict):
            json_input = json.dumps(json_input)

        result = subprocess.run(
            ["bash", str(script_path)],
            input=json_input,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode, result.stdout, result.stderr

    return _run


# ============================================================================
# Transcript Fixtures
# ============================================================================

@pytest.fixture
def long_transcript() -> str:
    """Return a transcript that meets minimum length requirements (> 200 chars)."""
    return "This is a sample transcript that contains enough content to meet minimum length thresholds. " * 5


@pytest.fixture
def code_phase_transcript() -> str:
    """Return a transcript indicating CODE phase activity."""
    return "Invoking pact-backend-coder for API implementation. Created user.py module." + " " * 200


@pytest.fixture
def test_phase_transcript() -> str:
    """Return a transcript indicating TEST phase activity."""
    return "Invoking pact-test-engineer for verification. Writing unit tests for auth module." + " " * 200


@pytest.fixture
def prepare_phase_transcript() -> str:
    """Return a transcript indicating PREPARE phase activity."""
    return "Invoking pact-preparer for requirements gathering. Researching API patterns." + " " * 200


@pytest.fixture
def architect_phase_transcript() -> str:
    """Return a transcript indicating ARCHITECT phase activity."""
    return "Invoking pact-architect for system design. Designing the authentication flow." + " " * 200


# ============================================================================
# PACT Agent Fixtures
# ============================================================================

@pytest.fixture
def pact_work_agents() -> list[str]:
    """Return list of all PACT work agents (excludes pact-memory-agent)."""
    return [
        "pact-preparer",
        "pact-architect",
        "pact-backend-coder",
        "pact-frontend-coder",
        "pact-database-engineer",
        "pact-test-engineer",
        "pact-n8n",
    ]


@pytest.fixture
def pact_code_agents() -> list[str]:
    """Return list of CODE phase agents."""
    return [
        "pact-backend-coder",
        "pact-frontend-coder",
        "pact-database-engineer",
    ]
