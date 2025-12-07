#!/usr/bin/env python3
"""
Shared utilities for PACT code analyzer scripts.

Provides common functionality for security validation, timeout handling,
and error management used across all analyzer scripts.

Location: skills/pact-code-analyzer/scripts/utils.py
Used by: complexity_analyzer.py, coupling_detector.py, dependency_mapper.py, file_metrics.py
Dependencies: Python 3.11+ standard library only
"""

import signal
from pathlib import Path
from typing import Optional

# Constants
MAX_FILE_SIZE = 1024 * 1024  # 1MB
TIMEOUT_SECONDS = 60


class TimeoutError(Exception):
    """Raised when script execution exceeds timeout."""
    pass


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass


def timeout_handler(signum, frame):
    """Handle timeout signal."""
    raise TimeoutError("Script execution exceeded timeout")


def validate_file_path(file_path: str, allowed_root: Optional[str] = None) -> Path:
    """
    Validate file path is within allowed directory and meets security requirements.

    Args:
        file_path: Path to validate
        allowed_root: Root directory to restrict access to (defaults to CWD)

    Returns:
        Validated Path object

    Raises:
        SecurityError: If path fails validation
        FileNotFoundError: If file doesn't exist
    """
    if allowed_root is None:
        allowed_root = Path.cwd()
    else:
        allowed_root = Path(allowed_root).resolve()

    path = Path(file_path).resolve()

    # Check if path is within allowed root
    try:
        path.relative_to(allowed_root)
    except ValueError:
        raise SecurityError(f"Path {file_path} is outside allowed directory {allowed_root}")

    # Reject symbolic links
    if path.is_symlink():
        raise SecurityError(f"Symbolic links not allowed: {file_path}")

    # Check file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check file size (only for files, not directories)
    if path.is_file() and path.stat().st_size > MAX_FILE_SIZE:
        raise SecurityError(f"File too large (max {MAX_FILE_SIZE} bytes): {file_path}")

    return path
