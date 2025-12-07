"""
Shared pytest fixtures for pact-code-analyzer tests.

Provides common test utilities and fixtures used across multiple test modules.
"""

import pytest
import json
import subprocess
from pathlib import Path


@pytest.fixture
def scripts_dir():
    """Return path to scripts directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture
def python_fixtures_dir(fixtures_dir):
    """Return path to Python test fixtures."""
    return fixtures_dir / 'python'


@pytest.fixture
def javascript_fixtures_dir(fixtures_dir):
    """Return path to JavaScript test fixtures."""
    return fixtures_dir / 'javascript'


@pytest.fixture
def typescript_fixtures_dir(fixtures_dir):
    """Return path to TypeScript test fixtures."""
    return fixtures_dir / 'typescript'


def run_script(script_path: Path, args: list) -> dict:
    """
    Run a Python script and return JSON output.

    Args:
        script_path: Path to the Python script
        args: Command-line arguments as list

    Returns:
        Parsed JSON output from script

    Raises:
        subprocess.CalledProcessError: If script exits with non-zero status
        json.JSONDecodeError: If output is not valid JSON
    """
    result = subprocess.run(
        ['python3', str(script_path)] + args,
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)


@pytest.fixture
def run_complexity_analyzer(scripts_dir):
    """Fixture that returns a function to run complexity_analyzer.py."""
    def _run(file_path: Path, threshold: int = 10):
        return run_script(
            scripts_dir / 'complexity_analyzer.py',
            ['--file', str(file_path), '--threshold', str(threshold)]
        )
    return _run


@pytest.fixture
def run_dependency_mapper(scripts_dir):
    """Fixture that returns a function to run dependency_mapper.py."""
    def _run(directory: Path, language: str, detect_circular: bool = False):
        args = ['--directory', str(directory), '--language', language]
        if detect_circular:
            args.append('--detect-circular')
        return run_script(
            scripts_dir / 'dependency_mapper.py',
            args
        )
    return _run


@pytest.fixture
def run_coupling_detector(scripts_dir):
    """Fixture that returns a function to run coupling_detector.py."""
    def _run(directory: Path, threshold: int = 10, show_details: bool = False):
        args = ['--directory', str(directory), '--threshold', str(threshold)]
        if show_details:
            args.append('--show-details')
        return run_script(
            scripts_dir / 'coupling_detector.py',
            args
        )
    return _run


@pytest.fixture
def run_file_metrics(scripts_dir):
    """Fixture that returns a function to run file_metrics.py."""
    def _run(file_path: Path = None, directory: Path = None, language: str = None):
        args = []
        if file_path:
            args.extend(['--file', str(file_path)])
        elif directory:
            args.extend(['--directory', str(directory)])
        if language:
            args.extend(['--language', language])
        return run_script(
            scripts_dir / 'file_metrics.py',
            args
        )
    return _run
