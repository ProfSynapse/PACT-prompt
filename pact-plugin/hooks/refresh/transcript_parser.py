"""
Location: pact-plugin/hooks/refresh/transcript_parser.py
Summary: JSONL transcript parsing and turn extraction.
Used by: refresh/__init__.py for extracting workflow state.

Parses Claude Code JSONL transcript files into Turn objects for
analysis. Handles streaming from end of file for efficiency and
gracefully skips malformed lines.
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ToolCall:
    """Represents a tool call within a turn."""

    name: str
    input_data: dict[str, Any] = field(default_factory=dict)
    tool_use_id: str = ""


@dataclass
class Turn:
    """
    Represents a single turn in the conversation transcript.

    Attributes:
        turn_type: "user", "assistant", "progress", or "summary"
        content: Text content of the message (may be empty for tool-only turns)
        timestamp: ISO timestamp string if available
        tool_calls: List of tool calls made in this turn
        raw_data: Original parsed JSON for advanced analysis
        line_number: Line number in the transcript file
    """

    turn_type: str
    content: str = ""
    timestamp: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict)
    line_number: int = 0

    @property
    def is_user(self) -> bool:
        """Check if this is a user turn."""
        return self.turn_type == "user"

    @property
    def is_assistant(self) -> bool:
        """Check if this is an assistant turn."""
        return self.turn_type == "assistant"

    @property
    def has_tool_calls(self) -> bool:
        """Check if this turn contains tool calls."""
        return len(self.tool_calls) > 0

    def get_tool_call(self, name: str) -> ToolCall | None:
        """Get a tool call by name, or None if not found."""
        for tc in self.tool_calls:
            if tc.name == name:
                return tc
        return None

    def has_task_to_pact_agent(self) -> bool:
        """Check if this turn has a Task call to a PACT agent."""
        for tc in self.tool_calls:
            if tc.name == "Task":
                subagent = tc.input_data.get("subagent_type", "")
                if "pact-" in subagent:
                    return True
        return False


def parse_line(line: str, line_number: int) -> Turn | None:
    """
    Parse a single JSONL line into a Turn object.

    Args:
        line: Raw JSON line from transcript
        line_number: Line number for debugging

    Returns:
        Turn object or None if line is invalid/empty
    """
    line = line.strip()
    if not line:
        return None

    try:
        data = json.loads(line)
    except json.JSONDecodeError as e:
        print(f"Warning: Malformed JSON at line {line_number}: {e}", file=sys.stderr)
        return None

    turn_type = data.get("type", "")
    if not turn_type:
        return None

    # Extract content - handle both string and list formats
    message = data.get("message", {})
    content_raw = message.get("content", "")

    content = ""
    tool_calls = []

    if isinstance(content_raw, str):
        content = content_raw
    elif isinstance(content_raw, list):
        # Content is a list of content blocks
        text_parts = []
        for block in content_raw:
            if isinstance(block, dict):
                block_type = block.get("type", "")
                if block_type == "text":
                    text_parts.append(block.get("text", ""))
                elif block_type == "tool_use":
                    tool_calls.append(
                        ToolCall(
                            name=block.get("name", ""),
                            input_data=block.get("input", {}),
                            tool_use_id=block.get("id", ""),
                        )
                    )
            elif isinstance(block, str):
                text_parts.append(block)
        content = "\n".join(text_parts)

    timestamp = data.get("timestamp", "")

    return Turn(
        turn_type=turn_type,
        content=content,
        timestamp=timestamp,
        tool_calls=tool_calls,
        raw_data=data,
        line_number=line_number,
    )


# Size threshold for switching to efficient tail-reading (10 MB)
LARGE_FILE_THRESHOLD_BYTES = 10 * 1024 * 1024


def read_last_n_lines(path: Path, n: int) -> list[str]:
    """
    Read the last N lines from a file efficiently.

    For small files (< 10MB), reads all and slices.
    For large files, uses efficient reverse-seek approach to avoid
    loading entire file into memory. (Fix 6: optimized for large files)

    Args:
        path: Path to the file
        n: Maximum number of lines to return

    Returns:
        List of lines (most recent last)
    """
    try:
        file_size = path.stat().st_size

        # For small files, simple approach is efficient enough
        if file_size < LARGE_FILE_THRESHOLD_BYTES:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) <= n:
                    return lines
                return lines[-n:]

        # For large files, read from end in chunks to find last N lines
        # This avoids loading entire file into memory
        chunk_size = 8192
        lines: list[str] = []
        with open(path, "rb") as f:
            # Start from end of file
            f.seek(0, 2)  # Seek to end
            remaining = f.tell()
            buffer = b""

            while remaining > 0 and len(lines) < n:
                # Read a chunk from the end
                read_size = min(chunk_size, remaining)
                remaining -= read_size
                f.seek(remaining)
                chunk = f.read(read_size)
                buffer = chunk + buffer

                # Split into lines and accumulate
                # Keep partial line at start of buffer for next iteration
                buffer_lines = buffer.split(b"\n")
                if remaining > 0:
                    # First element might be partial, keep in buffer
                    buffer = buffer_lines[0]
                    new_lines = buffer_lines[1:]
                else:
                    # At start of file, include everything
                    new_lines = buffer_lines
                    buffer = b""

                # Prepend new lines (they're earlier in file)
                lines = [line.decode("utf-8", errors="replace") + "\n" for line in new_lines if line] + lines

            # Return only the last n lines
            if len(lines) > n:
                lines = lines[-n:]
            return lines

    except IOError as e:
        print(f"Warning: Could not read transcript: {e}", file=sys.stderr)
        return []


def parse_transcript(path: Path, max_lines: int = 500) -> list[Turn]:
    """
    Parse a JSONL transcript file into Turn objects.

    Reads the last `max_lines` lines from the file and parses each
    into a Turn object. Invalid lines are skipped with a warning.

    Args:
        path: Path to the JSONL transcript file
        max_lines: Maximum number of lines to read (default 500)

    Returns:
        List of Turn objects in chronological order (oldest first)
    """
    if not path.exists():
        print(f"Warning: Transcript not found: {path}", file=sys.stderr)
        return []

    lines = read_last_n_lines(path, max_lines)
    turns = []

    # Calculate starting line number (for debugging)
    # If we read fewer lines than max, we got the whole file
    start_line = 1
    try:
        with open(path, "r", encoding="utf-8") as f:
            total_lines = sum(1 for _ in f)
            if total_lines > max_lines:
                start_line = total_lines - max_lines + 1
    except IOError:
        pass

    for i, line in enumerate(lines):
        line_number = start_line + i
        turn = parse_line(line, line_number)
        if turn:
            turns.append(turn)

    return turns


def find_turns_by_type(turns: list[Turn], turn_type: str) -> list[Turn]:
    """
    Filter turns by type.

    Args:
        turns: List of turns to filter
        turn_type: Type to filter for ("user", "assistant", etc.)

    Returns:
        Filtered list of turns
    """
    return [t for t in turns if t.turn_type == turn_type]


def find_turns_with_content(turns: list[Turn], pattern: str) -> list[Turn]:
    """
    Find turns whose content contains the given pattern.

    Args:
        turns: List of turns to search
        pattern: Substring to search for (case-insensitive)

    Returns:
        List of matching turns
    """
    pattern_lower = pattern.lower()
    return [t for t in turns if pattern_lower in t.content.lower()]


def find_last_user_message(turns: list[Turn]) -> Turn | None:
    """
    Find the most recent user message.

    Args:
        turns: List of turns (chronological order)

    Returns:
        Most recent user Turn or None
    """
    for turn in reversed(turns):
        if turn.is_user:
            return turn
    return None


def find_task_calls_to_agent(turns: list[Turn], agent_pattern: str) -> list[tuple[Turn, ToolCall]]:
    """
    Find all Task tool calls to agents matching the pattern.

    Args:
        turns: List of turns to search
        agent_pattern: Pattern to match in subagent_type (e.g., "pact-")

    Returns:
        List of (Turn, ToolCall) tuples for matching Task calls
    """
    results = []
    for turn in turns:
        for tc in turn.tool_calls:
            if tc.name == "Task":
                subagent = tc.input_data.get("subagent_type", "")
                if agent_pattern in subagent:
                    results.append((turn, tc))
    return results


def find_trigger_turn_index(turns: list[Turn], trigger_line_number: int) -> int:
    """
    Find the index of a turn by its line number.

    Shared utility to avoid duplicate trigger-index lookup loops across modules
    (Fix 4: extracted from workflow_detector.py, step_extractor.py, checkpoint_builder.py).

    Args:
        turns: List of turns to search
        trigger_line_number: Line number of the trigger turn

    Returns:
        Index of the turn with matching line number, or 0 if not found
    """
    for i, turn in enumerate(turns):
        if turn.line_number == trigger_line_number:
            return i
    return 0
