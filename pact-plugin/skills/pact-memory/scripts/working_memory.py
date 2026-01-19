"""
Working Memory Sync Module

Location: pact-plugin/skills/pact-memory/scripts/working_memory.py

Summary: Handles synchronization of memories to the Working Memory section
in CLAUDE.md. Maintains a rolling window of the most recent memories for
quick reference during Claude sessions.

Used by:
- memory_api.py: Calls sync_to_claude_md() after saving memories
- Test files: test_working_memory.py tests all functions in this module
"""

import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Constants for working memory section (saved memories)
WORKING_MEMORY_HEADER = "## Working Memory"
WORKING_MEMORY_COMMENT = "<!-- Auto-managed by pact-memory skill. Last 5 memories shown. Full history searchable via pact-memory skill. -->"
MAX_WORKING_MEMORIES = 5

# Constants for retrieved context section (searched/retrieved memories)
RETRIEVED_CONTEXT_HEADER = "## Retrieved Context"
RETRIEVED_CONTEXT_COMMENT = "<!-- Auto-managed by pact-memory skill. Last 3 retrieved memories shown. -->"
MAX_RETRIEVED_MEMORIES = 3


def _get_claude_md_path() -> Optional[Path]:
    """
    Get the path to CLAUDE.md in the project root.

    Uses CLAUDE_PROJECT_DIR environment variable if set,
    otherwise falls back to current working directory.

    Returns:
        Path to CLAUDE.md if it exists, None otherwise.
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        claude_md = Path(project_dir) / "CLAUDE.md"
    else:
        claude_md = Path.cwd() / "CLAUDE.md"

    if claude_md.exists():
        return claude_md
    return None


def _format_memory_entry(
    memory: Dict[str, Any],
    files: Optional[List[str]] = None,
    memory_id: Optional[str] = None
) -> str:
    """
    Format a memory as a markdown entry for CLAUDE.md.

    Args:
        memory: Memory dictionary with context, goal, decisions, etc.
        files: Optional list of file paths associated with this memory.
        memory_id: Optional memory ID to include for database reference.

    Returns:
        Formatted markdown string for the memory entry.
    """
    # Get date and time for header
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d %H:%M")

    lines = [f"### {date_str}"]

    # Add context if present
    if memory.get("context"):
        lines.append(f"**Context**: {memory['context']}")

    # Add goal if present
    if memory.get("goal"):
        lines.append(f"**Goal**: {memory['goal']}")

    # Add decisions if present
    decisions = memory.get("decisions")
    if decisions:
        if isinstance(decisions, list):
            # Extract decision text from list of dicts or strings
            decision_texts = []
            for d in decisions:
                if isinstance(d, dict):
                    decision_texts.append(d.get("decision", str(d)))
                else:
                    decision_texts.append(str(d))
            if decision_texts:
                lines.append(f"**Decisions**: {', '.join(decision_texts)}")
        elif isinstance(decisions, str):
            lines.append(f"**Decisions**: {decisions}")

    # Add lessons if present
    lessons = memory.get("lessons_learned")
    if lessons:
        if isinstance(lessons, list) and lessons:
            lines.append(f"**Lessons**: {', '.join(str(l) for l in lessons)}")
        elif isinstance(lessons, str):
            lines.append(f"**Lessons**: {lessons}")

    # Add files if present
    if files:
        lines.append(f"**Files**: {', '.join(files)}")

    # Add memory ID if provided
    if memory_id:
        lines.append(f"**Memory ID**: {memory_id}")

    return "\n".join(lines)


def _parse_working_memory_section(
    content: str
) -> Tuple[str, str, str, List[str]]:
    """
    Parse CLAUDE.md content to extract working memory section.

    Args:
        content: Full CLAUDE.md file content.

    Returns:
        Tuple of (before_section, section_header_with_comment, after_section, existing_entries)
        where existing_entries is a list of individual memory entry strings.
    """
    # Pattern to find the Working Memory section
    # Match ## Working Memory followed by optional comment and entries
    section_pattern = re.compile(
        r'^(## Working Memory)\s*\n'
        r'(<!-- [^>]*-->)?\s*\n?',
        re.MULTILINE
    )

    match = section_pattern.search(content)

    if not match:
        # Section doesn't exist
        return content, "", "", []

    section_start = match.start()
    section_header_end = match.end()

    # Find where the next ## section starts (end of working memory section)
    next_section_pattern = re.compile(r'^## (?!Working Memory)', re.MULTILINE)
    next_match = next_section_pattern.search(content, section_header_end)

    if next_match:
        section_end = next_match.start()
    else:
        section_end = len(content)

    before_section = content[:section_start]
    section_content = content[section_header_end:section_end].strip()
    after_section = content[section_end:]

    # Parse existing entries (each starts with ### YYYY-MM-DD)
    entry_pattern = re.compile(r'^### \d{4}-\d{2}-\d{2}', re.MULTILINE)
    entry_starts = [m.start() for m in entry_pattern.finditer(section_content)]

    existing_entries = []
    for i, start in enumerate(entry_starts):
        if i + 1 < len(entry_starts):
            entry = section_content[start:entry_starts[i + 1]].strip()
        else:
            entry = section_content[start:].strip()
        existing_entries.append(entry)

    return before_section, WORKING_MEMORY_HEADER, after_section, existing_entries


def sync_to_claude_md(
    memory: Dict[str, Any],
    files: Optional[List[str]] = None,
    memory_id: Optional[str] = None
) -> bool:
    """
    Sync a memory entry to the Working Memory section of CLAUDE.md.

    Maintains a rolling window of the last 7 memories. New entries are added
    at the top of the section, and entries beyond 7 are removed.

    This function is designed for graceful degradation - if CLAUDE.md doesn't
    exist or the sync fails for any reason, it logs a warning but doesn't
    raise an exception.

    Args:
        memory: Memory dictionary with context, goal, decisions, lessons_learned, etc.
        files: Optional list of file paths associated with this memory.
        memory_id: Optional memory ID to include for database reference.

    Returns:
        True if sync succeeded, False otherwise.
    """
    claude_md_path = _get_claude_md_path()

    if claude_md_path is None:
        logger.debug("CLAUDE.md not found, skipping working memory sync")
        return False

    try:
        # Read current content
        content = claude_md_path.read_text(encoding="utf-8")

        # Parse existing working memory section
        before_section, section_header, after_section, existing_entries = \
            _parse_working_memory_section(content)

        # Format new memory entry
        new_entry = _format_memory_entry(memory, files, memory_id)

        # Build new entries list: new entry first, then existing (up to max - 1)
        all_entries = [new_entry] + existing_entries
        trimmed_entries = all_entries[:MAX_WORKING_MEMORIES]

        # Build new section content
        section_lines = [
            WORKING_MEMORY_HEADER,
            WORKING_MEMORY_COMMENT,
            ""  # Blank line after comment
        ]
        for entry in trimmed_entries:
            section_lines.append(entry)
            section_lines.append("")  # Blank line between entries

        section_text = "\n".join(section_lines)

        # Reconstruct file content
        if section_header:
            # Section existed, replace it
            new_content = before_section + section_text + after_section
        else:
            # Section didn't exist, append at end
            if not content.endswith("\n"):
                content += "\n"
            new_content = content + "\n" + section_text

        # Write back to file
        claude_md_path.write_text(new_content, encoding="utf-8")

        logger.info("Synced memory to CLAUDE.md Working Memory section")
        return True

    except Exception as e:
        logger.warning(f"Failed to sync memory to CLAUDE.md: {e}")
        return False


def _parse_retrieved_context_section(
    content: str
) -> Tuple[str, str, str, List[str]]:
    """
    Parse CLAUDE.md content to extract retrieved context section.

    Args:
        content: Full CLAUDE.md file content.

    Returns:
        Tuple of (before_section, section_header, after_section, existing_entries)
        where existing_entries is a list of individual memory entry strings.
    """
    # Pattern to find the Retrieved Context section
    section_pattern = re.compile(
        r'^(## Retrieved Context)\s*\n'
        r'(<!-- [^>]*-->)?\s*\n?',
        re.MULTILINE
    )

    match = section_pattern.search(content)

    if not match:
        # Section doesn't exist
        return content, "", "", []

    section_start = match.start()
    section_header_end = match.end()

    # Find where the next ## section starts (end of retrieved context section)
    next_section_pattern = re.compile(r'^## (?!Retrieved Context)', re.MULTILINE)
    next_match = next_section_pattern.search(content, section_header_end)

    if next_match:
        section_end = next_match.start()
    else:
        section_end = len(content)

    before_section = content[:section_start]
    section_content = content[section_header_end:section_end].strip()
    after_section = content[section_end:]

    # Parse existing entries (each starts with ### YYYY-MM-DD)
    entry_pattern = re.compile(r'^### \d{4}-\d{2}-\d{2}', re.MULTILINE)
    entry_starts = [m.start() for m in entry_pattern.finditer(section_content)]

    existing_entries = []
    for i, start in enumerate(entry_starts):
        if i + 1 < len(entry_starts):
            entry = section_content[start:entry_starts[i + 1]].strip()
        else:
            entry = section_content[start:].strip()
        existing_entries.append(entry)

    return before_section, RETRIEVED_CONTEXT_HEADER, after_section, existing_entries


def _format_retrieved_entry(
    memory: Dict[str, Any],
    query: str,
    score: Optional[float] = None,
    memory_id: Optional[str] = None
) -> str:
    """
    Format a retrieved memory as a markdown entry for CLAUDE.md.

    Args:
        memory: Memory dictionary with context, goal, decisions, etc.
        query: The search query that retrieved this memory.
        score: Optional similarity score.
        memory_id: Optional memory ID for reference.

    Returns:
        Formatted markdown string for the retrieved entry.
    """
    # Get date and time for header
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d %H:%M")

    lines = [f"### {date_str}"]
    lines.append(f"**Query**: \"{query}\"")

    if score is not None:
        lines.append(f"**Relevance**: {score:.2f}")

    # Add context if present
    if memory.get("context"):
        # Truncate long context for display
        context = memory['context']
        if len(context) > 200:
            context = context[:197] + "..."
        lines.append(f"**Context**: {context}")

    # Add goal if present
    if memory.get("goal"):
        lines.append(f"**Goal**: {memory['goal']}")

    # Add memory ID if provided
    if memory_id:
        lines.append(f"**Memory ID**: {memory_id}")

    return "\n".join(lines)


def sync_retrieved_to_claude_md(
    memories: List[Dict[str, Any]],
    query: str,
    scores: Optional[List[float]] = None,
    memory_ids: Optional[List[str]] = None
) -> bool:
    """
    Sync retrieved memories to the Retrieved Context section of CLAUDE.md.

    Maintains a rolling window of the last 5 retrieved memories. New entries
    are added at the top of the section, and entries beyond 5 are removed.

    Args:
        memories: List of memory dictionaries that were retrieved.
        query: The search query used.
        scores: Optional list of similarity scores (same order as memories).
        memory_ids: Optional list of memory IDs (same order as memories).

    Returns:
        True if sync succeeded, False otherwise.
    """
    if not memories:
        return False

    claude_md_path = _get_claude_md_path()

    if claude_md_path is None:
        logger.debug("CLAUDE.md not found, skipping retrieved context sync")
        return False

    try:
        # Read current content
        content = claude_md_path.read_text(encoding="utf-8")

        # Parse existing retrieved context section
        before_section, section_header, after_section, existing_entries = \
            _parse_retrieved_context_section(content)

        # Format new entries (only the top result to avoid clutter)
        new_entries = []
        top_memory = memories[0]
        score = scores[0] if scores else None
        memory_id = memory_ids[0] if memory_ids else None
        new_entry = _format_retrieved_entry(top_memory, query, score, memory_id)
        new_entries.append(new_entry)

        # Build new entries list: new entry first, then existing (up to max - 1)
        all_entries = new_entries + existing_entries
        trimmed_entries = all_entries[:MAX_RETRIEVED_MEMORIES]

        # Build new section content
        section_lines = [
            RETRIEVED_CONTEXT_HEADER,
            RETRIEVED_CONTEXT_COMMENT,
            ""  # Blank line after comment
        ]
        for entry in trimmed_entries:
            section_lines.append(entry)
            section_lines.append("")  # Blank line between entries

        section_text = "\n".join(section_lines)

        # Reconstruct file content
        if section_header:
            # Section existed, replace it
            # Ensure blank line before next section
            if after_section and not after_section.startswith("\n"):
                new_content = before_section + section_text + "\n" + after_section
            else:
                new_content = before_section + section_text + after_section
        else:
            # Section didn't exist, insert before Working Memory if it exists
            working_memory_match = re.search(
                r'^## Working Memory',
                content,
                re.MULTILINE
            )
            if working_memory_match:
                # Insert before Working Memory with blank line
                insert_pos = working_memory_match.start()
                new_content = content[:insert_pos] + section_text + "\n" + content[insert_pos:]
            else:
                # Append at end
                if not content.endswith("\n"):
                    content += "\n"
                new_content = content + "\n" + section_text

        # Write back to file
        claude_md_path.write_text(new_content, encoding="utf-8")

        logger.info("Synced retrieved memories to CLAUDE.md Retrieved Context section")
        return True

    except Exception as e:
        logger.warning(f"Failed to sync retrieved memories to CLAUDE.md: {e}")
        return False
