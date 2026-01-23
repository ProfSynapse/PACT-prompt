#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/precompact_refresh.py
Summary: PreCompact hook that extracts workflow state from transcript before compaction.
Used by: Claude Code hooks.json PreCompact hook

This hook fires just before context compaction occurs. It parses the conversation
transcript to extract the current workflow state (if any) and writes a checkpoint
file. The checkpoint is then read by compaction_refresh.py on SessionStart to
inject refresh instructions into the resumed session.

Input: JSON from stdin with:
  - transcript_path: Path to the JSONL conversation transcript

Output: JSON with hookSpecificOutput.additionalContext (status message)

Checkpoint location: ~/.claude/pact-refresh/{encoded-path}.json
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Add hooks directory to path for refresh package imports
_hooks_dir = Path(__file__).parent
if str(_hooks_dir) not in sys.path:
    sys.path.insert(0, str(_hooks_dir))

from refresh.constants import CHECKPOINT_MAX_AGE_DAYS
from refresh.checkpoint_builder import (
    get_checkpoint_path,
    get_encoded_project_path,
    build_no_workflow_checkpoint,
)


def write_checkpoint_atomic(checkpoint_path: Path, data: dict) -> bool:
    """
    Write checkpoint data atomically using temp file + rename.

    Args:
        checkpoint_path: Destination path for checkpoint
        data: Checkpoint data to write

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temp file in same directory, then rename
        fd, temp_path = tempfile.mkstemp(
            suffix=".tmp",
            prefix="checkpoint_",
            dir=checkpoint_path.parent
        )
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            # Atomic rename
            os.rename(temp_path, checkpoint_path)
            return True
        except Exception:
            # Clean up temp file on failure
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise
    except Exception:
        return False


def cleanup_old_checkpoints(checkpoint_dir: Path) -> int:
    """
    Item 11: Remove checkpoint files older than CHECKPOINT_MAX_AGE_DAYS.

    Called when writing a new checkpoint to prevent accumulation of stale files.

    Args:
        checkpoint_dir: Directory containing checkpoint files

    Returns:
        Number of files cleaned up
    """
    if not checkpoint_dir.exists():
        return 0

    max_age_seconds = CHECKPOINT_MAX_AGE_DAYS * 24 * 60 * 60
    cutoff_time = time.time() - max_age_seconds
    cleaned = 0

    try:
        for checkpoint_file in checkpoint_dir.glob("*.json"):
            try:
                mtime = os.path.getmtime(checkpoint_file)
                if mtime < cutoff_time:
                    checkpoint_file.unlink()
                    cleaned += 1
            except OSError:
                # File may have been deleted by another process
                pass
    except Exception:
        # Don't fail the hook due to cleanup issues
        pass

    return cleaned


def main():
    """
    Main entry point for the PreCompact hook.

    Reads transcript path from input, extracts workflow state, and writes checkpoint.
    Always exits 0 to never block compaction.
    """
    try:
        # Parse input
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            input_data = {}

        transcript_path = input_data.get("transcript_path", "")
        session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")

        # Extract encoded project path
        encoded_path = get_encoded_project_path(transcript_path)
        if encoded_path == "unknown-project":
            # Cannot determine project, skip checkpoint
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreCompact",
                    "additionalContext": "Skipped: could not extract project path"
                }
            }))
            sys.exit(0)

        # Try to extract workflow state using the refresh package
        # (Fix 5: sys.path already configured at module level)
        checkpoint = None
        try:
            from refresh import extract_workflow_state
            # extract_workflow_state returns checkpoint dict directly (or None)
            checkpoint = extract_workflow_state(transcript_path)
            if checkpoint is not None:
                # Update session_id to current session (may differ from extraction)
                checkpoint["session_id"] = session_id
        except ImportError as e:
            # Refresh package not yet available (Agent A still building it)
            print(f"PreCompact: refresh package not available ({e})", file=sys.stderr)
            # Still write a checkpoint with no workflow state
            pass
        except Exception as e:
            # Parsing failed, log and continue
            print(f"PreCompact: transcript parsing failed ({e})", file=sys.stderr)
            pass

        # Build fallback checkpoint if extraction failed or returned None
        if checkpoint is None:
            checkpoint = build_no_workflow_checkpoint(
                transcript_path=transcript_path,
                lines_scanned=0,
                reason="No active workflow detected"
            )
            checkpoint["session_id"] = session_id

        # Write checkpoint atomically
        checkpoint_path = get_checkpoint_path(encoded_path)

        # Item 11: Clean up old checkpoints before writing new one
        cleanup_old_checkpoints(checkpoint_path.parent)

        success = write_checkpoint_atomic(checkpoint_path, checkpoint)

        if success:
            workflow_name = checkpoint.get("workflow", {}).get("name", "none")
            confidence = checkpoint.get("extraction", {}).get("confidence", 0)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreCompact",
                    "additionalContext": f"Checkpoint saved: workflow={workflow_name}, confidence={confidence:.1f}"
                }
            }
        else:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreCompact",
                    "additionalContext": "Warning: checkpoint write failed"
                }
            }

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        # Never fail the hook - log and exit cleanly
        print(f"PreCompact hook warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
