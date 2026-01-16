"""
PACT Memory API

Location: pact-plugin/skills/pact-memory/scripts/memory_api.py

High-level API for the PACT Memory skill providing a clean interface
for saving, searching, and managing memories.

This is the primary entry point for agents and hooks to interact
with the memory system.

Used by:
- SKILL.md: Documents API usage for skill invocation
- Hooks: memory_prompt.py and session_init.py
- Agents: Direct memory operations during PACT phases
"""

import logging
import os
import re
import struct
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Use the same sqlite3 module as database.py for type consistency
try:
    import pysqlite3 as sqlite3
except ImportError:
    import sqlite3

from .database import (
    db_connection,
    create_memory,
    get_memory,
    update_memory,
    delete_memory,
    list_memories,
    ensure_initialized,
    get_db_path,
    generate_id,
    SQLITE_EXTENSIONS_ENABLED
)
from .embeddings import (
    generate_embedding,
    generate_embedding_text,
    check_embedding_availability
)
from .graph import (
    track_file,
    link_memory_to_paths,
    get_files_for_memory,
    get_memories_for_files
)
from .models import MemoryObject, memory_from_db_row
from .search import (
    graph_enhanced_search,
    semantic_search,
    search_by_file,
    get_search_capabilities
)

# Configure logging
logger = logging.getLogger(__name__)

# Constants for working memory section
WORKING_MEMORY_HEADER = "## Working Memory"
WORKING_MEMORY_COMMENT = "<!-- Auto-managed by pact-memory skill. Last 5 memories shown. Full history searchable via pact-memory skill. -->"
MAX_WORKING_MEMORIES = 5


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


def _format_memory_entry(memory: Dict[str, Any], files: Optional[List[str]] = None, memory_id: Optional[str] = None) -> str:
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


def _parse_working_memory_section(content: str) -> tuple[str, str, str, List[str]]:
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


def sync_to_claude_md(memory: Dict[str, Any], files: Optional[List[str]] = None, memory_id: Optional[str] = None) -> bool:
    """
    Sync a memory entry to the Working Memory section of CLAUDE.md.

    Maintains a rolling window of the last 5 memories. New entries are added
    at the top of the section, and entries beyond 5 are removed.

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

        logger.info(f"Synced memory to CLAUDE.md Working Memory section")
        return True

    except Exception as e:
        logger.warning(f"Failed to sync memory to CLAUDE.md: {e}")
        return False


class PACTMemory:
    """
    High-level interface for PACT Memory operations.

    Provides a clean API for saving, searching, and managing memories
    with automatic project/session detection and file tracking.

    Usage:
        memory = PACTMemory()

        # Save a memory
        memory_id = memory.save({
            "context": "Working on authentication",
            "goal": "Add JWT refresh tokens",
            "lessons_learned": ["Redis INCR is atomic"],
            "decisions": [{"decision": "Use Redis", "rationale": "Fast TTL"}]
        })

        # Search memories
        results = memory.search("authentication tokens")

        # List recent memories
        recent = memory.list(limit=10)
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        db_path: Optional[Path] = None
    ):
        """
        Initialize the PACTMemory API.

        Args:
            project_id: Project identifier. Auto-detected from CLAUDE_PROJECT_DIR if not provided.
            session_id: Session identifier. Auto-detected from CLAUDE_SESSION_ID if not provided.
            db_path: Custom database path. Uses default if not provided.
        """
        self._project_id = project_id or self._detect_project_id()
        self._session_id = session_id or self._detect_session_id()
        self._db_path = db_path

        # Session file tracking (populated by hooks)
        self._session_files: List[str] = []

        logger.debug(
            f"PACTMemory initialized: project={self._project_id}, session={self._session_id}"
        )

    @staticmethod
    def _detect_project_id() -> Optional[str]:
        """Detect project ID from environment."""
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
        if project_dir:
            # Use the directory name as project ID
            return Path(project_dir).name
        return None

    @staticmethod
    def _detect_session_id() -> Optional[str]:
        """Detect session ID from environment."""
        return os.environ.get("CLAUDE_SESSION_ID")

    @property
    def project_id(self) -> Optional[str]:
        """Get the current project ID."""
        return self._project_id

    @property
    def session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self._session_id

    def track_file(self, path: str) -> None:
        """
        Track a file modified in this session.

        Called by file tracking hooks to accumulate files
        that will be linked to saved memories.

        Args:
            path: File path that was modified.
        """
        if path not in self._session_files:
            self._session_files.append(path)
            logger.debug(f"Tracking file: {path}")

    def get_tracked_files(self) -> List[str]:
        """Get list of files tracked in this session."""
        return self._session_files.copy()

    def clear_tracked_files(self) -> None:
        """Clear the list of tracked files."""
        self._session_files.clear()

    def save(
        self,
        memory: Dict[str, Any],
        files: Optional[List[str]] = None,
        include_tracked: bool = True
    ) -> str:
        """
        Save a memory to the database.

        Automatically:
        - Adds project_id and session_id if not provided
        - Links tracked files from the session
        - Generates and stores embedding for semantic search

        Args:
            memory: Memory dictionary with fields like context, goal,
                    lessons_learned, decisions, entities, active_tasks.
            files: Optional explicit file list to link.
            include_tracked: Include automatically tracked session files.

        Returns:
            The ID of the saved memory.
        """
        # Add project/session context if not provided
        if "project_id" not in memory or memory["project_id"] is None:
            memory["project_id"] = self._project_id
        if "session_id" not in memory or memory["session_id"] is None:
            memory["session_id"] = self._session_id

        with db_connection(self._db_path) as conn:
            ensure_initialized(conn)

            # Create the memory record
            memory_id = create_memory(conn, memory)

            # Collect files to link
            files_to_link = []
            if files:
                files_to_link.extend(files)
            if include_tracked and self._session_files:
                files_to_link.extend(self._session_files)

            # Link files to memory
            if files_to_link:
                link_memory_to_paths(
                    conn, memory_id, files_to_link,
                    self._project_id, "modified"
                )

            # Store embedding for semantic search
            self._store_embedding(conn, memory_id, memory)

            logger.info(f"Saved memory {memory_id} with {len(files_to_link)} files")

        # Sync to CLAUDE.md working memory (outside db connection context)
        # This is non-critical - failures are logged but don't fail the save
        try:
            sync_to_claude_md(memory, files_to_link if files_to_link else None, memory_id)
        except Exception as e:
            logger.warning(f"Failed to sync to CLAUDE.md: {e}")

        return memory_id

    def _store_embedding(
        self,
        conn: sqlite3.Connection,
        memory_id: str,
        memory: Dict[str, Any]
    ) -> bool:
        """
        Generate and store embedding for a memory.

        Requires SQLITE_EXTENSIONS_ENABLED (pysqlite3-binary) and sqlite-vec.
        If extensions are unavailable, skips embedding storage silently -
        search will fall back to keyword-only mode.

        Args:
            conn: Active database connection.
            memory_id: Memory ID to associate embedding with.
            memory: Memory data for embedding generation.

        Returns:
            True if embedding was stored, False otherwise.
        """
        # Check if SQLite extension loading is available
        if not SQLITE_EXTENSIONS_ENABLED:
            logger.debug(
                "Skipping embedding storage - SQLite extensions unavailable. "
                "Search will use keyword mode."
            )
            return False

        # Generate text for embedding
        text = generate_embedding_text(memory)
        if not text:
            return False

        # Generate embedding
        embedding = generate_embedding(text)
        if embedding is None:
            logger.debug("Embedding generation unavailable, skipping")
            return False

        try:
            # Enable extension loading (safe because SQLITE_EXTENSIONS_ENABLED is True)
            conn.enable_load_extension(True)
            try:
                import sqlite_vec
                sqlite_vec.load(conn)
            except ImportError:
                logger.debug("sqlite-vec not installed, skipping embedding storage")
                return False

            # Convert to blob
            embedding_blob = struct.pack(f'{len(embedding)}f', *embedding)

            # Insert into vector table
            conn.execute(
                """
                INSERT OR REPLACE INTO vec_memories (memory_id, project_id, embedding)
                VALUES (?, ?, ?)
                """,
                (memory_id, memory.get("project_id"), embedding_blob)
            )
            conn.commit()

            logger.debug(f"Stored embedding for memory {memory_id}")
            return True

        except Exception as e:
            logger.debug(f"Failed to store embedding: {e}")
            return False

    def search(
        self,
        query: str,
        current_file: Optional[str] = None,
        limit: int = 5
    ) -> List[MemoryObject]:
        """
        Search memories using semantic similarity and graph relationships.

        Args:
            query: Search query text.
            current_file: Optional current file for context boosting.
            limit: Maximum number of results.

        Returns:
            List of matching MemoryObject instances.
        """
        return graph_enhanced_search(
            query,
            current_file=current_file,
            project_id=self._project_id,
            limit=limit
        )

    def search_by_file(
        self,
        file_path: str,
        limit: int = 10
    ) -> List[MemoryObject]:
        """
        Find memories related to a specific file.

        Args:
            file_path: File path to search for.
            limit: Maximum number of results.

        Returns:
            List of related MemoryObject instances.
        """
        return search_by_file(file_path, self._project_id, limit)

    def get(self, memory_id: str) -> Optional[MemoryObject]:
        """
        Get a specific memory by ID.

        Args:
            memory_id: The memory ID.

        Returns:
            MemoryObject if found, None otherwise.
        """
        with db_connection(self._db_path) as conn:
            ensure_initialized(conn)

            memory_dict = get_memory(conn, memory_id)
            if memory_dict is None:
                return None

            # Get associated files
            files_data = get_files_for_memory(conn, memory_id)
            file_paths = [f["path"] for f in files_data]

            return memory_from_db_row(memory_dict, file_paths)

    def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing memory.

        Args:
            memory_id: The memory ID.
            updates: Dictionary of fields to update.

        Returns:
            True if updated, False if memory not found.
        """
        with db_connection(self._db_path) as conn:
            ensure_initialized(conn)

            success = update_memory(conn, memory_id, updates)

            if success:
                # Update embedding if content changed
                content_fields = {"context", "goal", "lessons_learned", "decisions", "entities"}
                if any(field in updates for field in content_fields):
                    memory_dict = get_memory(conn, memory_id)
                    if memory_dict:
                        self._store_embedding(conn, memory_id, memory_dict)

            return success

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: The memory ID.

        Returns:
            True if deleted, False if not found.
        """
        with db_connection(self._db_path) as conn:
            ensure_initialized(conn)

            # Also remove from vector table
            try:
                conn.execute(
                    "DELETE FROM vec_memories WHERE memory_id = ?",
                    (memory_id,)
                )
            except Exception:
                pass  # Vector table might not exist

            return delete_memory(conn, memory_id)

    def list(
        self,
        limit: int = 20,
        session_only: bool = False
    ) -> List[MemoryObject]:
        """
        List recent memories.

        Args:
            limit: Maximum number of results.
            session_only: Only return memories from current session.

        Returns:
            List of MemoryObject instances ordered by creation time.
        """
        with db_connection(self._db_path) as conn:
            ensure_initialized(conn)

            session_id = self._session_id if session_only else None

            memories_data = list_memories(
                conn,
                project_id=self._project_id,
                session_id=session_id,
                limit=limit
            )

            memories = []
            for memory_dict in memories_data:
                files_data = get_files_for_memory(conn, memory_dict["id"])
                file_paths = [f["path"] for f in files_data]
                memories.append(memory_from_db_row(memory_dict, file_paths))

            return memories

    def get_status(self) -> Dict[str, Any]:
        """
        Get status information about the memory system.

        Returns:
            Dictionary with database stats and capabilities.
        """
        from .database import get_memory_count
        from .graph import get_graph_stats

        with db_connection(self._db_path) as conn:
            ensure_initialized(conn)

            memory_count = get_memory_count(conn, self._project_id)
            graph_stats = get_graph_stats(conn, self._project_id)

        capabilities = get_search_capabilities()

        return {
            "project_id": self._project_id,
            "session_id": self._session_id,
            "memory_count": memory_count,
            "tracked_files_count": len(self._session_files),
            "graph_stats": graph_stats,
            "capabilities": capabilities,
            "db_path": str(get_db_path())
        }


# Module-level singleton for convenience
_lock = threading.Lock()
_instance: Optional[PACTMemory] = None


def get_memory_instance(
    project_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> PACTMemory:
    """
    Get the PACTMemory singleton instance.

    Args:
        project_id: Optional project ID override.
        session_id: Optional session ID override.

    Returns:
        PACTMemory instance.
    """
    global _instance
    with _lock:
        if _instance is None:
            _instance = PACTMemory(project_id, session_id)
    return _instance


def reset_memory_instance() -> None:
    """Reset the singleton instance (useful for testing)."""
    global _instance
    with _lock:
        _instance = None


# Convenience functions for simple usage
def save_memory(memory: Dict[str, Any], **kwargs) -> str:
    """Save a memory using the default instance."""
    return get_memory_instance().save(memory, **kwargs)


def search_memory(query: str, **kwargs) -> List[MemoryObject]:
    """Search memories using the default instance."""
    return get_memory_instance().search(query, **kwargs)


def list_memories_simple(limit: int = 20) -> List[MemoryObject]:
    """List recent memories using the default instance."""
    return get_memory_instance().list(limit=limit)
