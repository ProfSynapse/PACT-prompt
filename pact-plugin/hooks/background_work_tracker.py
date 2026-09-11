#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/background_work_tracker.py
Summary: PostToolUse hook (matcher: Bash) — records teammate harness-background
         Bash launches into the team-scoped U1 registry.
Used by: hooks.json PostToolUse Bash matcher.

#1625 Layer-2 floor. Writes only in teammate processes (not lead / plain).
Does not write the canonical session journal.

Identity bind (U2): resolve_agent_name steps 1–3.5 only (agent_name, agent_id,
session_id registry). Do NOT type-strip agent_type as the owner — two
same-agentType siblings would collapse. Attach the unique in_progress task
via iter_team_task_jsons on the aligned team. Ambiguous or missing identity
fail-opens with no write.

Stdin keys encoded from in-repo contracts, not a live Bash+run_in_background
capture (this environment cannot fire Claude Code teammate PostToolUse):
  - tool_name / tool_input.command — wait_filler_gate.py Input contract
  - tool_input.run_in_background — 1620 runbook + pact-qa-engineer.md
  - agent_type / session_id — HOOK_STDIN_DISCRIMINATORS PostToolUse row
Harness task id in tool_response is NOT encoded: no committed Bash-background
tool_response exists. Completion clear relies on U1 24h TTL at read time.

# livelock-safe: suppressOutput on every path; exit 0; informational write
# only; never deny.

Input: PostToolUse JSON (tool_name, tool_input, agent_type, session_id).
Output: {"suppressOutput": true}. Exit 0 on every path.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_hooks_dir = Path(__file__).parent
if str(_hooks_dir) not in sys.path:
    sys.path.insert(0, str(_hooks_dir))

import shared.pact_context as pact_context
from shared.background_work import append_record, iso_now, is_durable_command
from shared.pact_context import (
    classify_session_role,
    get_team_name,
    resolve_agent_name,
)
from shared.session_registry import resolve as registry_resolve
from shared.task_utils import iter_team_task_jsons

_SUPPRESS_OUTPUT = json.dumps({"suppressOutput": True})


def _truthy_background(value) -> bool:
    return value is True or value == "true" or value == 1


def is_harness_background_bash(input_data: dict) -> bool:
    """True iff this frame is a Bash launch with run_in_background set."""
    if not isinstance(input_data, dict):
        return False
    if input_data.get("tool_name") != "Bash":
        return False
    tool_input = input_data.get("tool_input")
    if not isinstance(tool_input, dict):
        return False
    return _truthy_background(tool_input.get("run_in_background"))


def command_from_frame(input_data: dict) -> str:
    tool_input = input_data.get("tool_input") if isinstance(input_data, dict) else None
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command")
    return command if isinstance(command, str) else ""


def bind_launcher_identity(input_data: dict, team_name: str) -> tuple[str, str, str] | None:
    """Return (agent_name, session_id, task_id) or None when identity is not unique.

    Steps 1–3.5 of resolve_agent_name only. If the resolved name equals the
    agent_type type-strip AND no earlier step supplied a name, treat as
    collapsed and refuse the write.
    """
    if not isinstance(input_data, dict) or not team_name:
        return None
    session_id = input_data.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return None

    named_by_field = bool(input_data.get("agent_name") or input_data.get("agent_id"))
    named_by_registry = False
    if not named_by_field:
        resolved = registry_resolve(session_id)
        named_by_registry = bool(resolved and "@" in resolved)

    agent_name = resolve_agent_name(input_data, team_name=team_name)
    if not agent_name:
        return None

    agent_type = input_data.get("agent_type")
    type_strip = ""
    if isinstance(agent_type, str) and agent_type:
        type_strip = (
            agent_type[len("pact-"):] if agent_type.startswith("pact-") else agent_type
        )
    if agent_name == type_strip and not named_by_field and not named_by_registry:
        return None

    matches = []
    for task in iter_team_task_jsons(team_name):
        if not isinstance(task, dict):
            continue
        if task.get("status") != "in_progress":
            continue
        if task.get("owner") != agent_name:
            continue
        task_id = task.get("id")
        if task_id is None:
            continue
        matches.append(str(task_id))
    if len(matches) != 1:
        return None
    return agent_name, session_id, matches[0]


def record_background_launch(input_data: dict) -> bool:
    """Write one registry row when the frame is a recordable teammate launch."""
    if classify_session_role(input_data) != "teammate":
        return False
    if not is_harness_background_bash(input_data):
        return False
    command = command_from_frame(input_data)
    if is_durable_command(command):
        return False
    team_name = get_team_name()
    if not team_name:
        return False
    bound = bind_launcher_identity(input_data, team_name)
    if bound is None:
        return False
    agent_name, session_id, task_id = bound
    return append_record(
        {
            "agent_name": agent_name,
            "session_id": session_id,
            "task_id": task_id,
            "command": command,
            "registered_at": iso_now(),
        },
        team_name=team_name,
    )


def main() -> None:
    try:
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            print(_SUPPRESS_OUTPUT)
            sys.exit(0)
        if not isinstance(input_data, dict):
            print(_SUPPRESS_OUTPUT)
            sys.exit(0)
        pact_context.init(input_data)
        record_background_launch(input_data)
        print(_SUPPRESS_OUTPUT)
        sys.exit(0)
    except SystemExit:
        raise
    except Exception:
        print(_SUPPRESS_OUTPUT)
        sys.exit(0)


if __name__ == "__main__":
    main()
