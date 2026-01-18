#!/usr/bin/env python3
"""
Location: .claude/hooks/session_init.py
Summary: SessionStart hook that initializes PACT environment.
Used by: Claude Code settings.json SessionStart hook

Performs:
1. Detects active plans and notifies user
2. Checks and auto-installs pact-memory dependencies
3. Migrates embeddings if dimension changed
4. Processes any unembedded memories (catch-up)

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
        ('pysqlite3', 'pysqlite3'),  # CRITICAL: enables SQLite extension loading
        ('sqlite-vec', 'sqlite_vec'),
        ('model2vec', 'model2vec'),  # Embedding backend
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


def maybe_migrate_embeddings() -> dict:
    """
    Check if embeddings need migration due to dimension change.

    When switching embedding backends, dimensions may change (e.g., 384->256).
    This function:
    1. Detects dimension mismatch
    2. Drops the old vector table
    3. Re-embeds all existing memories

    Returns:
        dict with status and message
    """
    result = {"status": "ok", "message": None}

    try:
        # Import required modules
        scripts_dir = Path(__file__).parent.parent / "skills" / "pact-memory" / "scripts"
        if not scripts_dir.exists():
            return result

        sys.path.insert(0, str(scripts_dir.parent))
        try:
            import struct
            import pysqlite3 as sqlite3
            import sqlite_vec
            from scripts.database import get_connection
            from scripts.embeddings import get_embedding_service, generate_embedding_text, EMBEDDING_DIM
        except ImportError:
            return result
        finally:
            if str(scripts_dir.parent) in sys.path:
                sys.path.remove(str(scripts_dir.parent))

        # Get expected dimension
        expected_dim = EMBEDDING_DIM

        # Connect to database
        conn = get_connection()
        sqlite_vec.load(conn)

        # Check if vec_memories table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='vec_memories'"
        )
        if cursor.fetchone() is None:
            conn.close()
            return result  # No table, nothing to migrate

        # Check actual dimension by examining an embedding
        try:
            row = conn.execute("SELECT embedding FROM vec_memories LIMIT 1").fetchone()
            if row is None:
                conn.close()
                return result  # Empty table, nothing to migrate

            actual_dim = len(row[0]) // 4  # 4 bytes per float
            if actual_dim == expected_dim:
                conn.close()
                return result  # Dimensions match, no migration needed

        except Exception:
            conn.close()
            return result

        # Dimension mismatch detected - need to migrate
        result["status"] = "migrating"
        result["message"] = f"Migrating embeddings: {actual_dim}-dim -> {expected_dim}-dim"

        # Drop old table
        conn.execute("DROP TABLE IF EXISTS vec_memories")
        conn.commit()

        # Recreate with new dimension
        conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_memories USING vec0(
                memory_id TEXT PRIMARY KEY,
                project_id TEXT PARTITION KEY,
                embedding float[{expected_dim}]
            )
        """)
        conn.commit()

        # Re-embed all memories
        service = get_embedding_service()
        memories = conn.execute("""
            SELECT id, context, goal, lessons_learned, decisions, entities
            FROM memories
        """).fetchall()

        success = 0
        for mem_id, context, goal, lessons, decisions, entities in memories:
            try:
                memory_dict = {
                    'context': context, 'goal': goal, 'lessons_learned': lessons,
                    'decisions': decisions, 'entities': entities,
                }
                embed_text = generate_embedding_text(memory_dict)
                embedding = service.generate(embed_text)

                if embedding:
                    embedding_blob = struct.pack(f'{len(embedding)}f', *embedding)
                    conn.execute(
                        "INSERT OR REPLACE INTO vec_memories(memory_id, embedding) VALUES (?, ?)",
                        (mem_id, embedding_blob)
                    )
                    success += 1
            except Exception:
                continue

        conn.commit()
        conn.close()

        result["status"] = "ok"
        result["message"] = f"Migrated {success}/{len(memories)} embeddings to {expected_dim}-dim"
        return result

    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)[:50]
        return result


# Session-scoped marker to prevent embedding retry loops
def _get_embedding_attempted_path() -> Path:
    """Get path to session-scoped embedding attempt marker file."""
    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
    return Path("/tmp") / f"pact_embedding_attempted_{session_id}"


def maybe_embed_pending() -> dict:
    """
    Check for and process unembedded memories on session start.

    This is a catch-up mechanism for embeddings that failed at save time.

    Features:
    - Session-scoped: Only attempts once per session
    - RAM check: Skips if available RAM is below threshold
    - Fail-fast: Stops on first failure (no retry loops)

    Returns:
        dict with status info (embedded count, skipped reason, etc.)
    """
    result = {"status": "skipped", "message": None}

    # Check if we've already attempted this session
    marker_path = _get_embedding_attempted_path()
    if marker_path.exists():
        result["message"] = "Already attempted this session"
        return result

    # Mark as attempted (do this first to prevent retry on errors)
    try:
        marker_path.touch()
    except OSError:
        result["message"] = "Could not create session marker"
        return result

    try:
        # Import the embedding catch-up function
        scripts_dir = Path(__file__).parent.parent / "skills" / "pact-memory" / "scripts"
        if not scripts_dir.exists():
            result["message"] = "Memory scripts not found"
            return result

        sys.path.insert(0, str(scripts_dir.parent))
        try:
            from scripts.embedding_catchup import embed_pending_memories
        except ImportError as e:
            result["message"] = f"Import failed: {str(e)[:30]}"
            return result
        finally:
            if str(scripts_dir.parent) in sys.path:
                sys.path.remove(str(scripts_dir.parent))

        # Process pending embeddings
        embed_result = embed_pending_memories(min_ram_mb=500.0, limit=20)

        if embed_result.get("skipped_ram"):
            result["status"] = "skipped_ram"
            result["message"] = "Low RAM, skipping"
            return result

        processed = embed_result.get("processed", 0)
        if processed > 0:
            result["status"] = "ok"
            result["message"] = f"Embedded {processed} pending memories"
            return result

        if embed_result.get("failed"):
            result["status"] = "partial"
            result["message"] = embed_result.get("error", "Unknown error")
            return result

        # No pending memories to process
        result["status"] = "ok"
        result["message"] = None
        return result

    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)[:50]
        return result


def setup_plugin_symlinks() -> str | None:
    """
    Create ~/.claude/protocols/pact-plugin/ symlink to plugin cache.

    This enables CLAUDE.md @references like @~/.claude/protocols/pact-plugin/algedonic.md
    to resolve correctly regardless of where the plugin cache lives.

    Returns:
        Status message or None if successful
    """
    plugin_root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", ""))
    if not plugin_root.exists():
        return None

    claude_dir = Path.home() / ".claude"

    # Only protocols/ needs symlink (CLAUDE.md references these)
    src = plugin_root / "protocols"
    if not src.exists():
        return None

    dst = claude_dir / "protocols" / "pact-plugin"
    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        if dst.is_symlink():
            # Check if symlink target changed (plugin update)
            if dst.resolve() != src.resolve():
                dst.unlink()
                dst.symlink_to(src)
                return "PACT symlinks updated"
            return None  # Already correct
        elif dst.exists():
            return None  # Real directory, don't touch
        else:
            dst.symlink_to(src)
            return "PACT symlinks ready"
    except OSError as e:
        return f"Symlink setup failed: {str(e)[:30]}"


def check_orchestrator_setup() -> str | None:
    """
    Guide user to set up CLAUDE.md if not present or missing PACT content.

    Returns:
        Setup guidance message or None if already configured
    """
    claude_md = Path.home() / ".claude" / "CLAUDE.md"
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")

    if not plugin_root:
        return None

    if not claude_md.exists():
        return f"PACT: Run: cp \"{plugin_root}/CLAUDE.md\" ~/.claude/CLAUDE.md"

    try:
        content = claude_md.read_text(encoding='utf-8')
        if "PACT Orchestrator" not in content:
            return f"PACT: To enable orchestrator, update ~/.claude/CLAUDE.md from {plugin_root}/CLAUDE.md"
    except (IOError, UnicodeDecodeError):
        pass

    return None


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
            in_progress_indicators = [
                "Status: IN_PROGRESS",
                "Status: In Progress",
                "status: in_progress",
                "Status: ACTIVE",
                "Status: Active",
            ]

            has_in_progress_status = any(
                indicator in content for indicator in in_progress_indicators
            )
            has_unchecked_items = "[ ] " in content
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
            continue

    return active_plans


def main():
    """
    Main entry point for the SessionStart hook.

    Performs PACT environment initialization:
    0. Creates plugin symlinks for @reference resolution
    1. Checks for active plans
    2. Guides user if CLAUDE.md setup needed
    3. Auto-installs pact-memory dependencies
    4. Migrates embeddings if dimension changed
    5. Processes any unembedded memories (catch-up)
    """
    try:
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            input_data = {}

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        context_parts = []
        system_messages = []

        # 0. Set up plugin symlinks (enables @~/.claude/protocols/pact-plugin/ references)
        symlink_result = setup_plugin_symlinks()
        if symlink_result and "failed" in symlink_result.lower():
            system_messages.append(symlink_result)
        elif symlink_result:
            context_parts.append(symlink_result)

        # 1. Check for active plans
        active_plans = find_active_plans(project_dir)
        if active_plans:
            plan_list = ", ".join(active_plans[:3])
            if len(active_plans) > 3:
                plan_list += f" (+{len(active_plans) - 3} more)"
            context_parts.append(f"Active plans: {plan_list}")

        # 2. Check if orchestrator setup needed
        orchestrator_msg = check_orchestrator_setup()
        if orchestrator_msg:
            system_messages.append(orchestrator_msg)

        # 3. Check and install dependencies
        deps_result = check_and_install_dependencies()
        if deps_result['installed']:
            context_parts.append(
                f"Installed: {', '.join(deps_result['installed'])}"
            )
        if deps_result['failed']:
            system_messages.append(
                f"Failed to install: {', '.join(deps_result['failed'])}"
            )

        # 4. Migrate embeddings if dimension changed
        migrate_result = maybe_migrate_embeddings()
        if migrate_result.get("message") and "Migrated" in migrate_result["message"]:
            context_parts.append(migrate_result["message"])

        # 5. Process any unembedded memories (catch-up)
        embed_result = maybe_embed_pending()
        if embed_result.get("message"):
            if embed_result["status"] == "ok" and "Embedded" in embed_result["message"]:
                context_parts.append(embed_result["message"])

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
        print(f"Hook warning (session_init): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
