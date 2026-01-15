#!/usr/bin/env python3
"""
Location: .claude/hooks/session_init.py
Summary: SessionStart hook that initializes PACT environment.
Used by: Claude Code settings.json SessionStart hook

Performs:
1. Detects active plans and notifies user
2. Checks and auto-installs pact-memory dependencies
3. Downloads embedding model if needed

Input: JSON from stdin with session context
Output: JSON with `hookSpecificOutput.additionalContext` for status
"""

import json
import sys
import os
import subprocess
from pathlib import Path


def check_and_install_dependencies() -> dict:
    """
    Check for pact-memory dependencies and auto-install if missing.

    Returns:
        dict with status, installed, and failed packages
    """
    packages = [
        ('sqlite-vec', 'sqlite_vec'),
        ('sqlite-lembed', 'sqlite_lembed'),
        ('sentence-transformers', 'sentence_transformers'),  # Fallback embeddings
    ]

    missing = []
    installed = []
    failed = []

    # Check what's missing
    for pip_name, import_name in packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)

    if not missing:
        return {'status': 'ok', 'installed': [], 'failed': []}

    # Attempt installation
    for pkg in missing:
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-q', pkg],
                capture_output=True,
                timeout=60
            )
            if result.returncode == 0:
                installed.append(pkg)
            else:
                failed.append(pkg)
        except subprocess.TimeoutExpired:
            failed.append(f"{pkg} (timeout)")
        except Exception as e:
            failed.append(f"{pkg} ({str(e)[:20]})")

    status = 'ok' if not failed else ('partial' if installed else 'failed')
    return {'status': status, 'installed': installed, 'failed': failed}


def check_and_download_model() -> dict:
    """
    Check for embedding model and download if missing.

    Returns:
        dict with status and message
    """
    model_dir = Path.home() / ".claude" / "pact-memory" / "models"
    model_path = model_dir / "all-MiniLM-L6-v2-Q8_0.gguf"
    model_url = (
        "https://huggingface.co/second-state/All-MiniLM-L6-v2-Embedding-GGUF/"
        "resolve/main/all-MiniLM-L6-v2-Q8_0.gguf"
    )

    if model_path.exists():
        return {'status': 'ok', 'message': 'Model present'}

    # Check if sqlite-lembed is available (needed for model)
    try:
        import sqlite_lembed
    except ImportError:
        return {'status': 'skip', 'message': 'sqlite-lembed not available'}

    # Download model using subprocess curl (more reliable SSL handling)
    try:
        model_dir.mkdir(parents=True, exist_ok=True)
        temp_path = model_path.with_suffix('.tmp')

        result = subprocess.run(
            ['curl', '-fsSL', '-o', str(temp_path), model_url],
            capture_output=True,
            timeout=120  # 2 min for 24MB download
        )

        if result.returncode == 0 and temp_path.exists():
            temp_path.rename(model_path)
            return {'status': 'ok', 'message': 'Model downloaded (24MB)'}
        else:
            return {'status': 'failed', 'message': 'curl download failed'}
    except subprocess.TimeoutExpired:
        return {'status': 'failed', 'message': 'Download timeout (>2min)'}
    except Exception as e:
        return {'status': 'failed', 'message': f'Download failed: {str(e)[:30]}'}


def find_active_plans(project_dir: str) -> list:
    """
    Find plans with IN_PROGRESS status or uncompleted items.

    Args:
        project_dir: The project root directory path

    Returns:
        List of plan filenames that appear to be in progress
    """
    plans_dir = Path(project_dir) / "docs" / "plans"
    active_plans = []

    if not plans_dir.is_dir():
        return active_plans

    for plan_file in plans_dir.glob("*-plan.md"):
        try:
            content = plan_file.read_text(encoding='utf-8')
            # Check for various in-progress indicators
            in_progress_indicators = [
                "Status: IN_PROGRESS",
                "Status: In Progress",
                "status: in_progress",
                "Status: ACTIVE",
                "Status: Active",
            ]

            # Check for explicit status markers
            has_in_progress_status = any(
                indicator in content for indicator in in_progress_indicators
            )

            # Check for unchecked items (uncompleted tasks)
            has_unchecked_items = "[ ] " in content

            # Check for explicit completion status (to avoid false positives)
            is_completed = any(
                status in content for status in [
                    "Status: COMPLETED",
                    "Status: Completed",
                    "Status: DONE",
                    "Status: Done",
                ]
            )

            if has_in_progress_status or (has_unchecked_items and not is_completed):
                active_plans.append(plan_file.name)

        except (IOError, UnicodeDecodeError):
            # Skip files we can't read
            continue

    return active_plans


def main():
    """
    Main entry point for the SessionStart hook.

    Performs PACT environment initialization:
    1. Checks for active plans
    2. Auto-installs pact-memory dependencies
    3. Downloads embedding model if needed
    """
    try:
        # Read input from stdin (may be empty for SessionStart)
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            input_data = {}

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        context_parts = []
        system_messages = []

        # 1. Check for active plans
        active_plans = find_active_plans(project_dir)
        if active_plans:
            plan_list = ", ".join(active_plans[:3])
            if len(active_plans) > 3:
                plan_list += f" (+{len(active_plans) - 3} more)"
            context_parts.append(f"Active plans: {plan_list}")

        # 2. Check and install dependencies
        deps_result = check_and_install_dependencies()
        if deps_result['installed']:
            context_parts.append(
                f"Installed: {', '.join(deps_result['installed'])}"
            )
        if deps_result['failed']:
            system_messages.append(
                f"Failed to install: {', '.join(deps_result['failed'])}"
            )

        # 3. Check and download model
        model_result = check_and_download_model()
        if model_result['status'] == 'ok' and 'downloaded' in model_result['message'].lower():
            context_parts.append(model_result['message'])
        elif model_result['status'] == 'failed':
            system_messages.append(f"Model: {model_result['message']}")

        # Build output
        output = {}

        if context_parts or system_messages:
            output["hookSpecificOutput"] = {
                "hookEventName": "SessionStart",
                "additionalContext": " | ".join(context_parts) if context_parts else "Success"
            }

        if system_messages:
            output["systemMessage"] = " | ".join(system_messages)

        if output:
            print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        # Don't block session start on errors - just warn
        print(f"Hook warning (session_init): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
