"""
PACT Memory Database Layer

SQLite database implementation for the PACT Memory skill.
Provides schema initialization, connection management, and CRUD operations
for rich memory objects.

Storage Location: ~/.claude/pact-memory/memory.db
Uses WAL mode for corruption prevention and concurrent access safety.
"""

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .config import DB_PATH, PACT_MEMORY_DIR

# Configure logging
logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """Get the database file path, creating parent directories if needed."""
    PACT_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Create and return a database connection.

    Args:
        db_path: Optional custom database path. Uses default if not provided.

    Returns:
        SQLite connection configured with WAL mode and foreign keys.
    """
    path = db_path or get_db_path()

    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Enable WAL mode for corruption prevention and better concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")

    return conn


@contextmanager
def db_connection(db_path: Optional[Path] = None):
    """
    Context manager for database connections.

    Handles connection lifecycle and ensures proper cleanup.

    Usage:
        with db_connection() as conn:
            cursor = conn.execute("SELECT * FROM memories")
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_schema(conn: sqlite3.Connection) -> None:
    """
    Initialize the database schema.

    Creates all required tables, indexes, and attempts to create
    the vector table for semantic search.

    Args:
        conn: Active database connection.
    """
    # Core memory table (rich objects)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            context TEXT,
            goal TEXT,
            active_tasks TEXT,
            lessons_learned TEXT,
            decisions TEXT,
            entities TEXT,
            project_id TEXT,
            session_id TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Files table (for graph network)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            path TEXT NOT NULL,
            project_id TEXT,
            last_modified TEXT,
            UNIQUE(path, project_id)
        )
    """)

    # Memory to File relationships (graph edges)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory_files (
            memory_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
            file_id TEXT REFERENCES files(id),
            relationship TEXT DEFAULT 'modified',
            PRIMARY KEY (memory_id, file_id)
        )
    """)

    # File to File relationships (imports, tests, etc.)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS file_relations (
            source_file TEXT REFERENCES files(id),
            target_file TEXT REFERENCES files(id),
            relationship TEXT,
            PRIMARY KEY (source_file, target_file, relationship)
        )
    """)

    # Create indexes for efficient queries
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_files_project ON files(project_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_files_file ON memory_files(file_id)")

    # Attempt to create vector table for semantic search
    _init_vector_table(conn)

    conn.commit()
    logger.info("Database schema initialized successfully")


def _init_vector_table(conn: sqlite3.Connection) -> bool:
    """
    Attempt to create the vector table for semantic search.

    Requires sqlite-vec extension. Gracefully fails if not installed.

    Args:
        conn: Active database connection.

    Returns:
        True if vector table was created, False otherwise.
    """
    try:
        # Try to load sqlite-vec extension
        conn.enable_load_extension(True)
        try:
            import sqlite_vec
            sqlite_vec.load(conn)
        except ImportError:
            logger.warning(
                "sqlite-vec not installed. Vector search will be unavailable. "
                "Install with: pip install sqlite-vec"
            )
            return False

        # Create vector table
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_memories USING vec0(
                memory_id TEXT PRIMARY KEY,
                project_id TEXT PARTITION KEY,
                embedding float[384]
            )
        """)
        logger.info("Vector table created successfully")
        return True

    except Exception as e:
        logger.warning(f"Could not create vector table: {e}. Semantic search will be unavailable.")
        return False


def ensure_initialized(conn: sqlite3.Connection) -> None:
    """
    Ensure the database is initialized.

    Checks if tables exist and initializes schema if not.

    Args:
        conn: Active database connection.
    """
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='memories'"
    )
    if cursor.fetchone() is None:
        init_schema(conn)


# =============================================================================
# JSON Field Helpers
# =============================================================================

JSON_FIELDS = {"active_tasks", "lessons_learned", "decisions", "entities"}


def _serialize_json_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize JSON fields in a memory dict for database storage.

    Args:
        data: Memory dictionary with potential list/dict values.

    Returns:
        Dictionary with JSON fields serialized to strings.
    """
    result = data.copy()
    for field in JSON_FIELDS:
        if field in result and result[field] is not None:
            if isinstance(result[field], (list, dict)):
                result[field] = json.dumps(result[field])
    return result


def _deserialize_json_fields(row: Union[sqlite3.Row, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deserialize JSON fields from database row to Python objects.

    Args:
        row: Database row or dictionary with serialized JSON fields.

    Returns:
        Dictionary with JSON fields deserialized to Python objects.
    """
    if isinstance(row, sqlite3.Row):
        result = dict(row)
    else:
        result = row.copy()

    for field in JSON_FIELDS:
        if field in result and result[field] is not None:
            if isinstance(result[field], str):
                try:
                    result[field] = json.loads(result[field])
                except json.JSONDecodeError:
                    # Keep as string if not valid JSON
                    pass
    return result


# =============================================================================
# Memory CRUD Operations
# =============================================================================

def generate_id() -> str:
    """Generate a unique ID for a new memory."""
    import secrets
    return secrets.token_hex(16)


def create_memory(
    conn: sqlite3.Connection,
    memory: Dict[str, Any]
) -> str:
    """
    Create a new memory record.

    Args:
        conn: Active database connection.
        memory: Memory dictionary with fields:
            - context: Optional[str] - Working context
            - goal: Optional[str] - Goal description
            - active_tasks: Optional[List[dict]] - Task list
            - lessons_learned: Optional[List[str]] - Lessons
            - decisions: Optional[List[dict]] - Decisions
            - entities: Optional[List[dict]] - Entities
            - project_id: Optional[str] - Project identifier
            - session_id: Optional[str] - Session identifier

    Returns:
        The ID of the created memory.
    """
    ensure_initialized(conn)

    # Generate ID if not provided
    memory_id = memory.get("id") or generate_id()

    # Prepare data with JSON serialization
    data = _serialize_json_fields(memory)

    # Set timestamps
    now = datetime.now(timezone.utc).isoformat()

    conn.execute("""
        INSERT INTO memories (
            id, context, goal, active_tasks, lessons_learned,
            decisions, entities, project_id, session_id,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        memory_id,
        data.get("context"),
        data.get("goal"),
        data.get("active_tasks"),
        data.get("lessons_learned"),
        data.get("decisions"),
        data.get("entities"),
        data.get("project_id"),
        data.get("session_id"),
        now,
        now
    ))

    conn.commit()
    logger.debug(f"Created memory with ID: {memory_id}")
    return memory_id


def get_memory(
    conn: sqlite3.Connection,
    memory_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a memory by ID.

    Args:
        conn: Active database connection.
        memory_id: The unique memory identifier.

    Returns:
        Memory dictionary if found, None otherwise.
    """
    ensure_initialized(conn)

    cursor = conn.execute(
        "SELECT * FROM memories WHERE id = ?",
        (memory_id,)
    )
    row = cursor.fetchone()

    if row is None:
        return None

    return _deserialize_json_fields(row)


def update_memory(
    conn: sqlite3.Connection,
    memory_id: str,
    updates: Dict[str, Any]
) -> bool:
    """
    Update an existing memory record.

    Args:
        conn: Active database connection.
        memory_id: The unique memory identifier.
        updates: Dictionary of fields to update.

    Returns:
        True if the memory was updated, False if not found.
    """
    ensure_initialized(conn)

    # Check if memory exists
    if get_memory(conn, memory_id) is None:
        return False

    # Prepare updates with JSON serialization
    data = _serialize_json_fields(updates)

    # Build dynamic UPDATE statement
    # Exclude id and created_at from updates
    data.pop("id", None)
    data.pop("created_at", None)

    # Always update updated_at
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    if not data:
        return True  # Nothing to update

    set_clauses = [f"{key} = ?" for key in data.keys()]
    values = list(data.values()) + [memory_id]

    conn.execute(
        f"UPDATE memories SET {', '.join(set_clauses)} WHERE id = ?",
        values
    )
    conn.commit()

    logger.debug(f"Updated memory {memory_id}")
    return True


def delete_memory(
    conn: sqlite3.Connection,
    memory_id: str
) -> bool:
    """
    Delete a memory record.

    Also removes associated memory_files entries due to CASCADE.

    Args:
        conn: Active database connection.
        memory_id: The unique memory identifier.

    Returns:
        True if the memory was deleted, False if not found.
    """
    ensure_initialized(conn)

    cursor = conn.execute(
        "DELETE FROM memories WHERE id = ?",
        (memory_id,)
    )
    conn.commit()

    deleted = cursor.rowcount > 0
    if deleted:
        logger.debug(f"Deleted memory {memory_id}")
    return deleted


def list_memories(
    conn: sqlite3.Connection,
    project_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    List memories with optional filtering.

    Args:
        conn: Active database connection.
        project_id: Optional project filter.
        session_id: Optional session filter.
        limit: Maximum number of results (default 20).
        offset: Number of results to skip (default 0).

    Returns:
        List of memory dictionaries, ordered by created_at DESC.
    """
    ensure_initialized(conn)

    query = "SELECT * FROM memories"
    params: List[Any] = []
    conditions = []

    if project_id is not None:
        conditions.append("project_id = ?")
        params.append(project_id)

    if session_id is not None:
        conditions.append("session_id = ?")
        params.append(session_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor = conn.execute(query, params)
    rows = cursor.fetchall()

    return [_deserialize_json_fields(row) for row in rows]


def search_memories_by_text(
    conn: sqlite3.Connection,
    search_term: str,
    project_id: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search memories by text content (basic substring search).

    Searches across context, goal, lessons_learned, and decisions fields.
    For semantic search, use the search module with embeddings.

    Args:
        conn: Active database connection.
        search_term: Text to search for.
        project_id: Optional project filter.
        limit: Maximum number of results.

    Returns:
        List of matching memory dictionaries.
    """
    ensure_initialized(conn)

    search_pattern = f"%{search_term}%"

    query = """
        SELECT * FROM memories
        WHERE (
            context LIKE ?
            OR goal LIKE ?
            OR lessons_learned LIKE ?
            OR decisions LIKE ?
        )
    """
    params = [search_pattern, search_pattern, search_pattern, search_pattern]

    if project_id is not None:
        query += " AND project_id = ?"
        params.append(project_id)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor = conn.execute(query, params)
    rows = cursor.fetchall()

    return [_deserialize_json_fields(row) for row in rows]


# =============================================================================
# Database Maintenance
# =============================================================================

def get_memory_count(
    conn: sqlite3.Connection,
    project_id: Optional[str] = None
) -> int:
    """
    Get the total count of memories.

    Args:
        conn: Active database connection.
        project_id: Optional project filter.

    Returns:
        Number of memories matching the criteria.
    """
    ensure_initialized(conn)

    if project_id is not None:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM memories WHERE project_id = ?",
            (project_id,)
        )
    else:
        cursor = conn.execute("SELECT COUNT(*) FROM memories")

    return cursor.fetchone()[0]


def vacuum_database(conn: sqlite3.Connection) -> None:
    """
    Optimize the database by running VACUUM.

    Reclaims space and defragments the database file.

    Args:
        conn: Active database connection.
    """
    conn.execute("VACUUM")
    logger.info("Database vacuumed successfully")


def check_integrity(conn: sqlite3.Connection) -> bool:
    """
    Check database integrity.

    Args:
        conn: Active database connection.

    Returns:
        True if database passes integrity check.
    """
    cursor = conn.execute("PRAGMA integrity_check")
    result = cursor.fetchone()[0]

    is_ok = result == "ok"
    if not is_ok:
        logger.error(f"Database integrity check failed: {result}")
    return is_ok


# =============================================================================
# Convenience Functions
# =============================================================================

def initialize_database(db_path: Optional[Path] = None) -> None:
    """
    Initialize the database with schema.

    Creates the database file and all required tables.

    Args:
        db_path: Optional custom database path.
    """
    with db_connection(db_path) as conn:
        init_schema(conn)


def quick_save(
    context: Optional[str] = None,
    goal: Optional[str] = None,
    lessons_learned: Optional[List[str]] = None,
    decisions: Optional[List[Dict[str, Any]]] = None,
    project_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """
    Quickly save a memory with minimal setup.

    Convenience function for simple memory creation.

    Args:
        context: Working context description.
        goal: Goal description.
        lessons_learned: List of lessons.
        decisions: List of decision dicts.
        project_id: Project identifier.
        session_id: Session identifier.

    Returns:
        The ID of the created memory.
    """
    memory = {
        "context": context,
        "goal": goal,
        "lessons_learned": lessons_learned or [],
        "decisions": decisions or [],
        "project_id": project_id,
        "session_id": session_id
    }

    with db_connection() as conn:
        return create_memory(conn, memory)
