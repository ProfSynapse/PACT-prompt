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
from datetime import datetime, timezone
from pathlib import Path


def get_encoded_project_path(transcript_path: str) -> str | None:
    """
    Extract the encoded project path from the transcript path.

    The transcript path follows this structure:
    ~/.claude/projects/{encoded-path}/{session-uuid}/session.jsonl

    Args:
        transcript_path: Full path to the transcript file

    Returns:
        The encoded project path segment, or None if extraction fails
    """
    try:
        parts = transcript_path.split("/")
        projects_idx = parts.index("projects")
        return parts[projects_idx + 1]
    except (ValueError, IndexError):
        return None


def get_checkpoint_path(encoded_path: str) -> Path:
    """
    Get the full checkpoint file path for a project.

    Args:
        encoded_path: The encoded project path segment

    Returns:
        Path to the checkpoint file
    """
    return Path.home() / ".claude" / "pact-refresh" / f"{encoded_path}.json"


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


def build_checkpoint(
    workflow_state: dict | None,
    session_id: str,
    transcript_path: str,
    lines_scanned: int = 0
) -> dict:
    """
    Build checkpoint data structure.

    Args:
        workflow_state: Extracted workflow state from refresh package, or None
        session_id: Current session ID
        transcript_path: Path to transcript that was parsed
        lines_scanned: Number of transcript lines scanned

    Returns:
        Checkpoint dictionary ready for JSON serialization
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if workflow_state is None:
        # No active workflow detected
        return {
            "version": "1.0",
            "session_id": session_id,
            "workflow": {
                "name": "none"
            },
            "extraction": {
                "confidence": 1.0,
                "notes": "No active workflow detected",
                "transcript_lines_scanned": lines_scanned
            },
            "created_at": now
        }

    # Build full checkpoint from extracted state
    checkpoint = {
        "version": "1.0",
        "session_id": session_id,
        "workflow": workflow_state.get("workflow", {"name": "none"}),
        "created_at": now
    }

    # Add step if present
    if "step" in workflow_state:
        checkpoint["step"] = workflow_state["step"]

    # Add pending_action if present
    if "pending_action" in workflow_state:
        checkpoint["pending_action"] = workflow_state["pending_action"]

    # Add context if present
    if "context" in workflow_state:
        checkpoint["context"] = workflow_state["context"]

    # Add extraction metadata
    checkpoint["extraction"] = workflow_state.get("extraction", {
        "confidence": 0.5,
        "notes": "State extracted from transcript",
        "transcript_lines_scanned": lines_scanned
    })

    return checkpoint


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
        if not encoded_path:
            # Cannot determine project, skip checkpoint
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreCompact",
                    "additionalContext": "Skipped: could not extract project path"
                }
            }))
            sys.exit(0)

        # Try to extract workflow state using the refresh package
        checkpoint = None
        try:
            # The refresh package is built by Agent A in parallel
            # Import path: hooks/refresh/
            hooks_dir = Path(__file__).parent
            sys.path.insert(0, str(hooks_dir))
            try:
                from refresh import extract_workflow_state
                # extract_workflow_state returns checkpoint dict directly (or None)
                checkpoint = extract_workflow_state(transcript_path)
                if checkpoint is not None:
                    # Update session_id to current session (may differ from extraction)
                    checkpoint["session_id"] = session_id
            finally:
                if str(hooks_dir) in sys.path:
                    sys.path.remove(str(hooks_dir))
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
            checkpoint = build_checkpoint(
                workflow_state=None,
                session_id=session_id,
                transcript_path=transcript_path,
                lines_scanned=0
            )

        # Write checkpoint atomically
        checkpoint_path = get_checkpoint_path(encoded_path)
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
