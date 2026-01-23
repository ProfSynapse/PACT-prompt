#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/session_init.py
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
    Create symlinks for plugin resources to ~/.claude/.

    Creates:
    1. ~/.claude/protocols/pact-plugin/ -> plugin/protocols/
       (enables @~/.claude/protocols/pact-plugin/... references in CLAUDE.md)
    2. ~/.claude/agents/pact-*.md -> plugin/agents/pact-*.md
       (enables non-prefixed agent names like "pact-memory-agent")

    Returns:
        Status message or None if successful
    """
    plugin_root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", ""))
    if not plugin_root.exists():
        return None

    claude_dir = Path.home() / ".claude"
    messages = []

    # 1. Symlink protocols/ directory
    protocols_src = plugin_root / "protocols"
    if protocols_src.exists():
        protocols_dst = claude_dir / "protocols" / "pact-plugin"
        protocols_dst.parent.mkdir(parents=True, exist_ok=True)

        try:
            if protocols_dst.is_symlink():
                if protocols_dst.resolve() != protocols_src.resolve():
                    protocols_dst.unlink()
                    protocols_dst.symlink_to(protocols_src)
                    messages.append("protocols updated")
            elif not protocols_dst.exists():
                protocols_dst.symlink_to(protocols_src)
                messages.append("protocols linked")
        except OSError as e:
            messages.append(f"protocols failed: {str(e)[:20]}")

    # 2. Symlink individual agent files (enables non-prefixed agent names)
    agents_src = plugin_root / "agents"
    if agents_src.exists():
        agents_dst = claude_dir / "agents"
        agents_dst.mkdir(parents=True, exist_ok=True)

        agents_updated = 0
        agents_created = 0
        for agent_file in agents_src.glob("pact-*.md"):
            dst_file = agents_dst / agent_file.name
            try:
                if dst_file.is_symlink():
                    if dst_file.resolve() != agent_file.resolve():
                        dst_file.unlink()
                        dst_file.symlink_to(agent_file)
                        agents_updated += 1
                elif not dst_file.exists():
                    dst_file.symlink_to(agent_file)
                    agents_created += 1
                # Skip if real file exists (user override)
            except OSError:
                continue

        if agents_created:
            messages.append(f"{agents_created} agents linked")
        if agents_updated:
            messages.append(f"{agents_updated} agents updated")

    if not messages:
        return "PACT symlinks verified"
    return "PACT: " + ", ".join(messages)




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


def update_claude_md() -> str | None:
    """
    Update ~/.claude/CLAUDE.md with PACT content.

    Automatically merges or updates the PACT Orchestrator prompt in the user's
    CLAUDE.md file. Uses explicit markers to manage the PACT section without
    disturbing other user customizations.

    Strategy:
    1. If file missing -> create with PACT content in markers.
    2. If markers found -> replace content between markers.
    3. If no markers but "PACT Orchestrator" found -> assume manual install, warn.
    4. If no markers and no conflict -> append PACT content with markers.

    Returns:
        Status message or None if no change.
    """
    plugin_root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", ""))
    if not plugin_root.exists():
        return None

    source_file = plugin_root / "CLAUDE.md"
    if not source_file.exists():
        return None

    target_file = Path.home() / ".claude" / "CLAUDE.md"

    START_MARKER = "<!-- PACT_START: Managed by pact-plugin - Do not edit this block -->"
    END_MARKER = "<!-- PACT_END -->"

    try:
        source_content = source_file.read_text(encoding="utf-8")
        wrapped_source = f"{START_MARKER}\n{source_content}\n{END_MARKER}"

        # Case 1: Target doesn't exist
        if not target_file.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(wrapped_source, encoding="utf-8")
            return "Created CLAUDE.md with PACT Orchestrator"

        target_content = target_file.read_text(encoding="utf-8")

        # Case 2: Markers found - update if changed
        if START_MARKER in target_content and END_MARKER in target_content:
            parts = target_content.split(START_MARKER)
            pre = parts[0]
            # Handle case where multiple markers might exist (take first and last valid)
            # but usually just one block.
            rest = parts[1]
            if END_MARKER in rest:
                post = rest.split(END_MARKER, 1)[1]
                new_full_content = f"{pre}{wrapped_source}{post}"

                if new_full_content != target_content:
                    target_file.write_text(new_full_content, encoding="utf-8")
                    return "PACT Orchestrator updated"
                return None

        # Case 3: No markers but content similar to PACT found
        if "PACT Orchestrator" in target_content:
            # Check if it looks roughly like what we expect, or just leave it
            # Returning a message prompts the user to check it
            return "PACT present but unmanaged (add markers to auto-update)"

        # Case 4: No markers, no specific PACT content -> Append
        # Ensure we append on a new line
        if not target_content.endswith("\n"):
            target_content += "\n"
        
        new_content = f"{target_content}\n{wrapped_source}"
        target_file.write_text(new_content, encoding="utf-8")
        return "PACT Orchestrator added to CLAUDE.md"

    except Exception as e:
        return f"PACT update failed: {str(e)[:30]}"


def ensure_project_memory_md() -> str | None:
    """
    Ensure project has a CLAUDE.md with memory sections.

    Creates a minimal project-level CLAUDE.md containing only the memory
    sections (Retrieved Context, Working Memory) if one doesn't exist.
    These sections are project-specific and managed by the pact-memory skill.

    If the project already has a CLAUDE.md, this function does nothing
    (preserves existing project configuration).

    Returns:
        Status message or None if no action taken.
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project_dir:
        return None

    target_file = Path(project_dir) / "CLAUDE.md"

    # Don't overwrite existing project CLAUDE.md
    if target_file.exists():
        return None

    # Create minimal CLAUDE.md with memory sections
    memory_template = """# Project Memory

This file contains project-specific memory managed by the PACT framework.
The global PACT Orchestrator is loaded from `~/.claude/CLAUDE.md`.

## Retrieved Context
<!-- Auto-managed by pact-memory skill. Last 3 retrieved memories shown. -->

## Working Memory
<!-- Auto-managed by pact-memory skill. Last 5 memories shown. Full history searchable via pact-memory skill. -->
"""

    try:
        target_file.write_text(memory_template, encoding="utf-8")
        return "Created project CLAUDE.md with memory sections"
    except Exception as e:
        return f"Project CLAUDE.md failed: {str(e)[:30]}"


def main():
    """
    Main entry point for the SessionStart hook.

    Performs PACT environment initialization:
    0. Creates plugin symlinks for @reference resolution
    1. Checks for active plans
    2. Updates ~/.claude/CLAUDE.md (merges/installs PACT Orchestrator)
    3. Ensures project CLAUDE.md exists with memory sections
    4. Auto-installs pact-memory dependencies
    5. Migrates embeddings if dimension changed
    6. Processes any unembedded memories (catch-up)
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

        # 2. Updates ~/.claude/CLAUDE.md (merges/installs PACT Orchestrator)
        claude_md_msg = update_claude_md()
        if claude_md_msg:
            if "failed" in claude_md_msg.lower() or "unmanaged" in claude_md_msg.lower():
                system_messages.append(claude_md_msg)
            else:
                context_parts.append(claude_md_msg)

        # 3. Ensure project has CLAUDE.md with memory sections
        project_md_msg = ensure_project_memory_md()
        if project_md_msg:
            if "failed" in project_md_msg.lower():
                system_messages.append(project_md_msg)
            else:
                context_parts.append(project_md_msg)

        # 4. Check and install dependencies
        deps_result = check_and_install_dependencies()
        if deps_result['installed']:
            context_parts.append(
                f"Installed: {', '.join(deps_result['installed'])}"
            )
        if deps_result['failed']:
            system_messages.append(
                f"Failed to install: {', '.join(deps_result['failed'])}"
            )

        # 5. Migrate embeddings if dimension changed
        migrate_result = maybe_migrate_embeddings()
        if migrate_result.get("message") and "Migrated" in migrate_result["message"]:
            context_parts.append(migrate_result["message"])

        # 6. Process any unembedded memories (catch-up)
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
