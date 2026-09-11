#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/unflagged_background_scan.py
Summary: UserPromptSubmit + SessionStart hook — lead-side unflagged-background
         SURFACER. On the lead's turn-start or session start, re-scans the
         team's task list plus the U1 registry for teammates who backgrounded
         harness Bash work, idled, and have no valid intentional_wait past
         the 10-minute idled_at window, then SURFACES an additionalContext
         directing a SendMessage. Writes a once-per-(task_id, registered_at)
         forensic `unflagged_background_wait` journal event via journal-read
         dedup — no filesystem marker.
Used by: hooks.json UserPromptSubmit + SessionStart registration.

WHY A NEW HOOK (not missed_wake_scan): #1301 documents that missed_wake_scan
matches exactly awaiting_lead_completion and stamps that constant. This alarm
records the task's real wait absence class (missing / null / malformed) and
must never reuse missed_wake or awaiting_lead_completion.

WHY LEAD-SIDE: hooks cannot SendMessage. The measured #1625 wake was a lead
SendMessage. Teammate / plain frames no-op.

DEDUP: surface is persistent-while-condition (re-scan live state every fire).
Forensic emit is once-per-(task_id, registered_at) via journal read.

# livelock-safe: additionalContext ONLY on the surface path (a stale
# unflagged-background condition exists); suppressOutput on EVERY other path;
# informational (no loop, never blocks); the journal is read/written ONLY when
# a qualifying task exists.

Input: JSON from stdin (UserPromptSubmit / SessionStart; agent_type is the
       role discriminator).
Output: hookSpecificOutput.additionalContext on the surface path; otherwise
        {"suppressOutput": true}. Exit 0 on every path.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_hooks_dir = Path(__file__).parent
if str(_hooks_dir) not in sys.path:
    sys.path.insert(0, str(_hooks_dir))

import shared.pact_context as pact_context
from shared.background_work import (
    idled_at_stale,
    load_records,
    parse_iso,
    unflagged_fire,
)
from shared.pact_context import is_lead
from shared.session_journal import append_event, get_journal_path, make_event, read_events
from shared.session_state import _sanitize_member_name
from shared.task_utils import get_task_list

_SUPPRESS_OUTPUT = json.dumps({"suppressOutput": True})
_SURFACE_EVENTS = ("UserPromptSubmit", "SessionStart")
_EVENT_TYPE = "unflagged_background_wait"


def find_unflagged_stale(
    tasks: list,
    records: list | None = None,
    now: datetime | None = None,
) -> list[dict]:
    """Tasks that fire the U1 predicate with idled_at older than 10 minutes.

    Each item is {"task": task, "record": record, "wait_class": class}.
    """
    now = now or datetime.now(timezone.utc)
    rows = records if records is not None else load_records(now=now)
    found = []
    if not isinstance(tasks, list):
        return found
    for task in tasks:
        fire, wait_class, record = unflagged_fire(task, records=rows, now=now)
        if not fire or record is None or wait_class is None:
            continue
        if not idled_at_stale(record, now=now):
            continue
        found.append({"task": task, "record": record, "wait_class": wait_class})
    return found


def _fields(item: dict) -> tuple[str, str, str, str, str]:
    task = item.get("task") or {}
    record = item.get("record") or {}
    task_id = str(task.get("id") or "")
    owner = task.get("owner") or record.get("agent_name") or ""
    subject = task.get("subject") or ""
    registered_at = record.get("registered_at") or ""
    wait_class = item.get("wait_class") or ""
    return task_id, owner, subject, registered_at, wait_class


def _emitted_keys() -> set:
    keys = set()
    for ev in read_events(_EVENT_TYPE):
        if not isinstance(ev, dict):
            continue
        task_id = ev.get("task_id")
        registered_at = ev.get("registered_at")
        if task_id and registered_at:
            keys.add((task_id, registered_at))
    return keys


def emit_forensic(stale: list) -> None:
    try:
        if not stale:
            return
        if not get_journal_path():
            return
        emitted = _emitted_keys()
        for item in stale:
            task_id, owner, subject, registered_at, wait_class = _fields(item)
            if not task_id or not owner or not registered_at:
                continue
            if (task_id, registered_at) in emitted:
                continue
            safe_owner = _sanitize_member_name(owner)
            if not safe_owner:
                continue
            safe_subject = _sanitize_member_name(subject) if subject else ""
            fields = {
                "task_id": task_id,
                "agent": safe_owner,
                "registered_at": registered_at,
                "wait_class": wait_class,
            }
            if safe_subject:
                fields["task_subject"] = safe_subject
            append_event(make_event(_EVENT_TYPE, **fields))
            emitted.add((task_id, registered_at))
    except Exception:
        pass


def _age_minutes(ts: str, now: datetime) -> int | None:
    parsed = parse_iso(ts)
    if parsed is None:
        return None
    return max(0, int((now - parsed).total_seconds() // 60))


def build_surface(stale: list, now: datetime | None = None) -> str | None:
    """additionalContext directing SendMessage. Must not mention
    awaiting_lead_completion or a forgotten completion wake."""
    if not stale:
        return None
    now = now or datetime.now(timezone.utc)
    lines = []
    for item in stale:
        task_id, owner, subject, _registered_at, wait_class = _fields(item)
        task_id = _sanitize_member_name(task_id)
        owner = _sanitize_member_name(owner)
        subject = _sanitize_member_name(subject)
        idled_at = (item.get("record") or {}).get("idled_at") or ""
        age = _age_minutes(idled_at, now) if isinstance(idled_at, str) else None
        age_str = f"~{age}min idle" if age is not None else "idle"
        label = f"#{task_id or '?'} ({owner or 'unknown'}"
        label += f": {subject}" if subject else ""
        label += ")"
        lines.append(
            f"- Task {label} — recorded outstanding self-started work, "
            f"intentional_wait {wait_class or 'invalid'}, {age_str}"
        )
    return (
        "PACT unflagged-background alarm: the teammate(s) below backgrounded "
        "harness work and ended the turn without a valid intentional_wait. "
        "Recorded outstanding work is still on disk — this is not a claim the "
        "process is still running. ACTION: SendMessage each named teammate "
        "(the message is the wake; hooks cannot send it). This notice "
        "re-shows every lead turn until the wait is valid or the registry "
        "entry is gone.\n" + "\n".join(lines)
    )


def run_surface(input_data: dict, now: datetime | None = None) -> str | None:
    if not is_lead(input_data):
        return None
    now = now or datetime.now(timezone.utc)
    records = load_records(now=now)
    if not any(idled_at_stale(record, now=now) for record in records):
        return None
    tasks = get_task_list()
    if not tasks:
        return None
    stale = find_unflagged_stale(tasks, records=records, now=now)
    if not stale:
        return None
    emit_forensic(stale)
    return build_surface(stale, now=now)


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
        surface = run_surface(input_data)
        if surface:
            event = input_data.get("hook_event_name")
            if not isinstance(event, str) or event not in _SURFACE_EVENTS:
                event = "UserPromptSubmit"
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "additionalContext": surface,
                }
            }))
        else:
            print(_SUPPRESS_OUTPUT)
        sys.exit(0)
    except SystemExit:
        raise
    except Exception:
        print(_SUPPRESS_OUTPUT)
        sys.exit(0)


if __name__ == "__main__":
    main()
