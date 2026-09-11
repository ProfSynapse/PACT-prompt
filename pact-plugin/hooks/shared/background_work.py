"""
Location: pact-plugin/hooks/shared/background_work.py
Summary: Team-scoped registry of outstanding teammate harness-background
         Bash work, plus the unflagged-background fire predicate.
         Pure helpers and fail-open loaders — no hook I/O.
Used by: background_work_tracker.py (writer), teammate_idle.py (advisory),
         unflagged_background_scan.py (lead surface).

#1625: a teammate who backgrounds Bash and ends the turn with no valid
intentional_wait is recorded here. Detection requires a registry row PLUS
in_progress PLUS validate_wait false — mid-arc in_progress with no row
must not fire.

Contract: never raise on missing/corrupt files, empty team name, or
malformed records. Read-time 24h TTL drops stale rows from outstanding
state. Team path uses pact_context.get_team_name() after init() — the
same identity-aligned resolver teammate_idle and get_task_list use.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .intentional_wait import canonical_since, validate_wait
from .pact_context import get_team_name
from .paths import get_claude_config_dir

try:
    import fcntl
    HAS_FLOCK = True
except ImportError:
    HAS_FLOCK = False

REGISTRY_FILENAME = "background_work.json"
UNFLAGGED_IDLE_FILENAME = "unflagged_background_idle.json"
RECORD_TTL_SECONDS = 24 * 3600
LEAD_STALE_MINUTES = 10
UNFLAGGED_IDLE_THRESHOLD = 3
DURABLE_COMMAND_TOKENS = frozenset({"dev", "start", "serve", "watch"})
WAIT_CLASS_MISSING = "missing"
WAIT_CLASS_NULL = "null"
WAIT_CLASS_MALFORMED = "malformed"

_DURABLE_WORD = re.compile(
    r"(?<![A-Za-z0-9_./-])("
    + "|".join(re.escape(tok) for tok in sorted(DURABLE_COMMAND_TOKENS))
    + r")(?![A-Za-z0-9_-])",
    re.IGNORECASE,
)


def parse_iso(ts: Any) -> datetime | None:
    """Parse a tz-aware ISO-8601 timestamp, or None if unusable."""
    if not isinstance(ts, str) or not ts:
        return None
    try:
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now(now: datetime | None = None) -> str:
    if now is None:
        return canonical_since()
    return now.isoformat(timespec="seconds")


def classify_wait(task: Any) -> str | None:
    """Return the wait-absence class, or None if validate_wait succeeds.

    Classes: missing (no intentional_wait key), null (value is None),
    malformed (present but not well-formed). Never raises on plain dicts.
    """
    if not isinstance(task, dict):
        return WAIT_CLASS_MISSING
    metadata = task.get("metadata")
    if not isinstance(metadata, dict):
        return WAIT_CLASS_MISSING
    if "intentional_wait" not in metadata:
        return WAIT_CLASS_MISSING
    wait = metadata.get("intentional_wait")
    if wait is None:
        return WAIT_CLASS_NULL
    if validate_wait(wait):
        return None
    return WAIT_CLASS_MALFORMED


def is_durable_command(command: Any) -> bool:
    """True iff the command looks like a durable process (dev/start/serve/watch).

    Word-boundary match so `watchdog` and `test_start_helper` do not hit.
    Conservative: a hit means "do not record" (R3).
    """
    if not isinstance(command, str) or not command.strip():
        return False
    return _DURABLE_WORD.search(command) is not None


def _team_file(filename: str, team_name: str | None = None) -> Path | None:
    name = team_name if team_name is not None else get_team_name()
    if not isinstance(name, str) or not name:
        return None
    return get_claude_config_dir() / "teams" / name / filename


def registry_path(team_name: str | None = None) -> Path | None:
    """Team-scoped registry path, or None when the team name is unusable."""
    return _team_file(REGISTRY_FILENAME, team_name)


def unflagged_idle_path(team_name: str | None = None) -> Path | None:
    return _team_file(UNFLAGGED_IDLE_FILENAME, team_name)


def _record_expired(record: dict, now: datetime) -> bool:
    registered = parse_iso(record.get("registered_at"))
    if registered is None:
        return True
    return (now - registered).total_seconds() >= RECORD_TTL_SECONDS


def _sanitize_record(raw: Any) -> dict | None:
    if not isinstance(raw, dict):
        return None
    agent_name = raw.get("agent_name")
    session_id = raw.get("session_id")
    task_id = raw.get("task_id")
    registered_at = raw.get("registered_at")
    if not isinstance(agent_name, str) or not agent_name:
        return None
    if not isinstance(session_id, str) or not session_id:
        return None
    if not isinstance(task_id, str) or not task_id:
        return None
    if parse_iso(registered_at) is None:
        return None
    out = {
        "agent_name": agent_name,
        "session_id": session_id,
        "task_id": task_id,
        "registered_at": registered_at,
    }
    harness = raw.get("harness_task_id")
    if isinstance(harness, str) and harness:
        out["harness_task_id"] = harness
    command = raw.get("command")
    if isinstance(command, str) and command:
        out["command"] = command[:240]
    idled_at = raw.get("idled_at")
    if parse_iso(idled_at) is not None:
        out["idled_at"] = idled_at
    return out


def _parse_records_text(text: str, now: datetime) -> list[dict]:
    try:
        raw = json.loads(text) if text.strip() else {}
    except (json.JSONDecodeError, TypeError, ValueError):
        return []
    items = raw.get("records") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return []
    out: list[dict] = []
    for item in items:
        record = _sanitize_record(item)
        if record is None or _record_expired(record, now):
            continue
        out.append(record)
    return out


def load_records(
    team_name: str | None = None,
    now: datetime | None = None,
) -> list[dict]:
    """Load outstanding (non-expired) records. Fail-open to []."""
    path = registry_path(team_name)
    if path is None:
        return []
    now = now or utc_now()
    try:
        text = _read_text_shared(path)
    except FileNotFoundError:
        return []
    except (OSError, TypeError, ValueError):
        return []
    return _parse_records_text(text, now)


def _read_text_shared(path: Path) -> str:
    """Read text under a shared flock when available.

    Writers take LOCK_EX, truncate-in-place, and flush before unlock so a
    LOCK_SH reader cannot observe the empty or partial mid-write file.
    """
    if HAS_FLOCK:
        with open(path, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                return f.read()
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    return path.read_text(encoding="utf-8")


def _rewrite_locked(f, text: str) -> None:
    """Truncate-in-place and flush while the caller still holds LOCK_EX."""
    f.seek(0)
    f.truncate()
    f.write(text)
    f.flush()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if HAS_FLOCK:
        with open(path, "a+", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                _rewrite_locked(f, text)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    else:
        path.write_text(text, encoding="utf-8")


def _write_records(path: Path, records: list[dict]) -> None:
    _write_text(path, json.dumps({"records": records}))


def _atomic_update_records(
    mutator,
    team_name: str | None = None,
    now: datetime | None = None,
) -> bool:
    """Read-modify-write the registry under one lock. Fail-open."""
    path = registry_path(team_name)
    if path is None:
        return False
    now = now or utc_now()
    path.parent.mkdir(parents=True, exist_ok=True)

    def _apply(text: str) -> tuple[str, bool]:
        current = _parse_records_text(text, now)
        updated, changed = mutator(current)
        if not changed:
            return text, False
        clean = [r for r in (_sanitize_record(x) for x in updated) if r is not None]
        return json.dumps({"records": clean}), True

    try:
        if HAS_FLOCK:
            with open(path, "a+", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    f.seek(0)
                    new_text, changed = _apply(f.read())
                    if changed:
                        _rewrite_locked(f, new_text)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            return True
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            text = ""
        new_text, changed = _apply(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
        return True
    except OSError:
        return False


def save_records(
    records: list[dict],
    team_name: str | None = None,
) -> bool:
    """Replace the registry. Fail-open: return False on any error."""
    path = registry_path(team_name)
    if path is None:
        return False
    clean = [r for r in (_sanitize_record(x) for x in records) if r is not None]
    try:
        _write_records(path, clean)
        return True
    except OSError:
        return False


def append_record(record: dict, team_name: str | None = None) -> bool:
    """Append one sanitized record. Fail-open."""
    clean = _sanitize_record(record)
    if clean is None:
        return False

    def _append(current: list[dict]) -> tuple[list[dict], bool]:
        current.append(clean)
        return current, True

    return _atomic_update_records(_append, team_name=team_name)


def matching_outstanding(
    task: Any,
    records: list[dict] | None = None,
    now: datetime | None = None,
    team_name: str | None = None,
) -> dict | None:
    """First outstanding record whose task_id matches the task."""
    if not isinstance(task, dict):
        return None
    task_id = task.get("id")
    if task_id is None:
        return None
    task_id = str(task_id)
    rows = records if records is not None else load_records(team_name, now=now)
    for record in rows:
        if record.get("task_id") == task_id:
            return record
    return None


def unflagged_fire(
    task: Any,
    records: list[dict] | None = None,
    now: datetime | None = None,
    team_name: str | None = None,
) -> tuple[bool, str | None, dict | None]:
    """Fire when in_progress + outstanding record + no valid wait.

    Returns (fire, wait_class, record). wait_class is set only on fire.
    """
    if not isinstance(task, dict):
        return False, None, None
    if task.get("status") != "in_progress":
        return False, None, None
    record = matching_outstanding(task, records=records, now=now, team_name=team_name)
    if record is None:
        return False, None, None
    wait_class = classify_wait(task)
    if wait_class is None:
        return False, None, record
    return True, wait_class, record


def stamp_idled_at(
    task_id: str,
    now: datetime | None = None,
    team_name: str | None = None,
) -> bool:
    """Set idled_at on the first matching record that lacks it."""
    if not isinstance(task_id, str) or not task_id:
        return False
    stamp = iso_now(now)
    changed = False

    def _apply(records: list[dict]) -> tuple[list[dict], bool]:
        nonlocal changed
        out = []
        for record in records:
            if record.get("task_id") == task_id and not record.get("idled_at"):
                record = dict(record)
                record["idled_at"] = stamp
                changed = True
            out.append(record)
        return out, changed

    ok = _atomic_update_records(_apply, team_name=team_name, now=now)
    return bool(ok and changed)


def idled_at_stale(
    record: dict,
    now: datetime | None = None,
    threshold_minutes: int = LEAD_STALE_MINUTES,
) -> bool:
    """True iff record.idled_at is present and older than the lead window."""
    idled = parse_iso(record.get("idled_at") if isinstance(record, dict) else None)
    if idled is None:
        return False
    now = now or utc_now()
    return (now - idled).total_seconds() >= threshold_minutes * 60


def _parse_idle_counts_text(text: str) -> dict:
    try:
        data = json.loads(text) if text.strip() else {}
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def load_unflagged_idle_counts(team_name: str | None = None) -> dict:
    path = unflagged_idle_path(team_name)
    if path is None:
        return {}
    try:
        text = _read_text_shared(path)
    except FileNotFoundError:
        return {}
    except (OSError, TypeError, ValueError):
        return {}
    return _parse_idle_counts_text(text)


def update_unflagged_idle_counts(mutator, team_name: str | None = None) -> dict:
    """Atomic RMW of unflagged_background_idle.json. Fail-open to {}."""
    path = unflagged_idle_path(team_name)
    if path is None:
        return {}
    path.parent.mkdir(parents=True, exist_ok=True)

    def _apply(text: str) -> tuple[str, dict, bool]:
        counts = _parse_idle_counts_text(text)
        before = json.dumps(counts)
        updated = mutator(counts)
        if not isinstance(updated, dict):
            updated = {}
        new_text = json.dumps(updated)
        return new_text, updated, new_text != before

    try:
        if HAS_FLOCK:
            with open(path, "a+", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    f.seek(0)
                    new_text, updated, changed = _apply(f.read())
                    if changed:
                        _rewrite_locked(f, new_text)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            return updated
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            text = ""
        new_text, updated, changed = _apply(text)
        if changed:
            path.write_text(new_text, encoding="utf-8")
        return updated
    except OSError:
        return {}


def save_unflagged_idle_counts(counts: dict, team_name: str | None = None) -> bool:
    path = unflagged_idle_path(team_name)
    if path is None:
        return False
    try:
        _write_text(path, json.dumps(counts if isinstance(counts, dict) else {}))
        return True
    except OSError:
        return False
