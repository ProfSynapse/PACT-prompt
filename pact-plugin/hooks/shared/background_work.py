"""
Location: pact-plugin/hooks/shared/background_work.py
Summary: Team-scoped registry of outstanding teammate harness-background
         Bash work, plus the unflagged-background fire predicate.
         Pure helpers and fail-open loaders — no hook I/O, no registration.
Used by: track_files.py (Layer 1 writer), teammate_idle.py (Layer 2
         advisory), missed_wake_scan.py (Layer 3 lead surface).

A teammate who backgrounds Bash and ends the turn with no valid
intentional_wait is recorded here. Detection requires a registry row PLUS
in_progress PLUS validate_wait false — mid-arc in_progress with no row
must not fire.

SCOPE — SHELL-SHAPED WORK ONLY, AND THE LIMIT IS STRUCTURAL RATHER THAN AN
OVERSIGHT. The launch is observed from a PostToolUse `Bash` frame, so the
only background work this registry can ever hold is a shell command. The
platform tracks several other kinds — a monitor, an Agent-tool subagent, an
MCP task, a workflow, a scheduled wakeup — and none of them raises a `Bash`
tool event, so none is recorded and no layer fires for one. A teammate can
therefore hold genuinely outstanding work that this mechanism cannot see.
DO NOT DESCRIBE THIS AS ENFORCING THE WAIT RULE GENERALLY. It enforces it
for shell-shaped launches. The instruction to agents is unconditional —
flag every self-started wait — but what is DETECTED here is a subset, and
conflating the two is what makes an absent advisory read as an all-clear.

Contract: never raise on missing/corrupt files, empty team name, or
malformed records. Read-time 24h TTL drops stale rows. Team path uses
pact_context.get_team_name() after init() — the same identity-aligned
resolver teammate_idle and get_task_list use.

TWO team-scoped state files, and they must stay separate. The registry
(background_work.json) holds outstanding launches. The idle counter
(unflagged_background_idle.json) backs Layer 2's three-consecutive-idles
threshold. DO NOT collapse the counter into the existing idle_counts.json:
that file's writer pops a teammate's key whenever the task is not
`completed`, and Layer 2's whole population is a teammate idling on an
`in_progress` task — the exact branch that pops. Sharing the file resets
the counter every tick and Layer 2 can never reach three.
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

# Layer 3 falls back to registered_at when idled_at is absent, so that a
# missed TeammateIdle cannot disable the lead surface. registered_at is NOT
# evidence of idling — only that time has passed since a launch — so it
# carries the longer window. 30 minutes matches this project's existing
# intentional-wait staleness threshold rather than introducing a second
# number; it is a judgement, not a measurement, and is a named constant so
# a later measurement can move it.
LEAD_UNIDLED_STALE_MINUTES = 30

UNFLAGGED_IDLE_THRESHOLD = 3
DURABLE_COMMAND_TOKENS = frozenset({"dev", "start", "serve", "watch"})
WAIT_CLASS_MISSING = "missing"
WAIT_CLASS_NULL = "null"
WAIT_CLASS_MALFORMED = "malformed"

# F5: `-` is deliberately ABSENT from the LOOKBEHIND class so that the FLAG
# spelling of these tokens matches — `--watch`, `-w --serve`, `foo --dev bar`.
# It remains in the LOOKAHEAD, which is what still excludes `test-start-helper`
# and `run-dev-script`: those have a token followed by `-`, and only the
# lookbehind changed. Both guards had to fail for a hyphenated NAME to start
# matching, and only one of them moved, so this change is one-directional.
_DURABLE_WORD = re.compile(
    r"(?<![A-Za-z0-9_./])("
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
    """Matches dev/start/serve/watch as a standalone word or immediately after
    a hyphen, so `--watch` and `re-start` both hit.

    A hit means "do not record". READ THE FIRST LINE LITERALLY: this is NOT a
    test for a durable process, and calling it one understates its breadth in
    both directions. Both are MEASURED and both are recorded as open findings
    in tests/test_background_work_adversarial.py; neither is fixed here,
    because the one-character change that closes the second opens a new false
    negative, so the predicate needs redesigning rather than patching.

    IT OVER-FIRES ON ORDINARY ONE-SHOT COMMANDS. Three of the four tokens are
    everyday vocabulary in test, build and grep commands, so `pytest -k start`,
    `grep -rn watch hooks/` and `build.py --env dev` are all silently NOT
    recorded, and Layers 1-3 are off for those launches. The word-boundary
    exclusions (`watchdog`, `test_start_helper`, `./scripts/dev-check.sh`,
    `/srv/dev`) prevent ADJACENCY false positives only; the standalone-word
    ones remain and are the common case.

    THE FLAG SPELLING IS NOW CAUGHT — this was the harmful direction and it is
    FIXED. `-` was in the lookbehind exclusion class, so `--watch` never
    matched and `vite --watch` WAS recorded: a process meant to run forever,
    eventually drawing an advisory and a lead-side surface. Dropping `-` from
    the LOOKBEHIND closes it. MEASURED as newly filtered: `--watch`,
    `vite --watch`, `-w --serve`, `foo --dev bar`. Newly recorded: NOTHING —
    the change is one-directional.

    WHY THAT COST NOTHING, because the obvious objection is wrong and was
    believed for hours. It was argued that the same character makes
    `test-start-helper` match `start` and go silently unrecorded. It does not:
    that case is blocked by the LOOKAHEAD `(?![A-Za-z0-9_-])` — `start` is
    followed by `-helper` — and F5 touches only the lookbehind. BOTH guards had
    to fail for that regression and only one moved. `test_start_helper`,
    `run-dev-script`, `pre-serve-hook` and `my-watch-list` are all unchanged.

    THE REAL COST, small and in the silence direction: a token at the END of a
    hyphenated name now matches, so `re-start` and `auto-dev` are no longer
    recorded. A script genuinely named `auto-dev` therefore gets no Layer 1
    row. That is the same hyphen-prefixed class as the flag forms and it is
    accepted deliberately rather than discovered.

    STILL OPEN, and NOT fixed here: the over-firing above. `pytest -k start`
    and `grep -rn watch hooks/` remain silently unrecorded. That needs the
    predicate redesigned rather than patched, and it is recorded as an open
    finding with its measured command set rather than papered over.
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
    """Path of Layer 2's own idle counter. See the module docstring for why
    this is not idle_counts.json."""
    return _team_file(UNFLAGGED_IDLE_FILENAME, team_name)


def _record_expired(record: dict, now: datetime) -> bool:
    registered = parse_iso(record.get("registered_at"))
    if registered is None:
        return True
    return (now - registered).total_seconds() >= RECORD_TTL_SECONDS


def _clean_task_ids(raw: Any) -> list[str] | None:
    """Normalize the task_ids field, or None when it is unusable.

    A bare string is REJECTED rather than coerced into a one-element list.
    Records are ephemeral team state with a 24h TTL and are never read
    across a version boundary, so a scalar here is a malformed write rather
    than an older schema, and dropping it is safer than reinterpreting it.
    """
    if not isinstance(raw, list):
        return None
    out: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item:
            return None
        out.append(item)
    return out or None


def _sanitize_record(raw: Any) -> dict | None:
    if not isinstance(raw, dict):
        return None
    agent_name = raw.get("agent_name")
    session_id = raw.get("session_id")
    task_ids = _clean_task_ids(raw.get("task_ids"))
    registered_at = raw.get("registered_at")
    if not isinstance(agent_name, str) or not agent_name:
        return None
    if not isinstance(session_id, str) or not session_id:
        return None
    if task_ids is None:
        return None
    if parse_iso(registered_at) is None:
        return None
    out = {
        "agent_name": agent_name,
        "session_id": session_id,
        "task_ids": task_ids,
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


def _load_records(
    team_name: str | None = None,
    now: datetime | None = None,
) -> list[dict]:
    """Load outstanding (non-expired) records. Fail-open to [].

    Expiry here is the 24h TTL alone. See `unflagged_fire` for why no
    task-status predicate belongs here.
    """
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


def record_task_ids(record: Any) -> list[str]:
    """The task ids a record covers. [] for anything malformed."""
    if not isinstance(record, dict):
        return []
    ids = record.get("task_ids")
    return list(ids) if isinstance(ids, list) else []


def matching_outstanding(
    task: Any,
    records: list[dict] | None = None,
    now: datetime | None = None,
    team_name: str | None = None,
) -> dict | None:
    """First outstanding record listing this task among its task_ids."""
    if not isinstance(task, dict):
        return None
    task_id = task.get("id")
    if task_id is None:
        return None
    task_id = str(task_id)
    rows = records if records is not None else _load_records(team_name, now=now)
    for record in rows:
        if task_id in record_task_ids(record):
            return record
    return None


def any_listed_task_flagged(
    record: Any,
    tasks: Any = None,
) -> bool:
    """True iff SOME in_progress task listed on the record carries a valid wait.

    This is the R5 fire predicate's silencing half, and it generalises in
    the SAFE direction deliberately: a teammate holding two tasks who
    flagged the wait on EITHER has flagged it, so the advisory stays
    silent. Under the old exactly-one-task rule that teammate got no record
    at all, so this strictly adds coverage without adding a
    false-positive route.

    `tasks` is the team's task list. When it is None the caller has no
    task set to check and only the task in hand can be judged, so this
    returns False and the caller's own classify_wait decides.
    """
    if not isinstance(tasks, list):
        return False
    listed = set(record_task_ids(record))
    if not listed:
        return False
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if task.get("status") != "in_progress":
            continue
        if str(task.get("id")) not in listed:
            continue
        if classify_wait(task) is None:
            return True
    return False


def load_records_for_discharge(
    team_name: str | None = None,
    now: datetime | None = None,
) -> list[dict]:
    """The UNGATED read. TTL only — no expiry gate, no suppression gate.

    THE NAME IS THE ENFORCEMENT. The raw loader is private (`_load_records`)
    so that a future consumer cannot reach an ungated read by accident; to get
    one it has to type the word `discharge`, which is a decision rather than a
    default. The previous arrangement — a public raw loader plus a docstring
    asking callers to remember two gates — did not hold for the second
    consumer, and would not have held for a third.

    ONLY the discharge path may use this. It must see FLAGGED records,
    because a flagged record is precisely what it exists to retire; a gated
    read would hide every record it is looking for and kill the mechanism
    while every gate test still passed. Tests asserting raw on-disk state are
    the other legitimate caller.

    Anything that SURFACES a record to a human or an agent must call
    `outstanding_unflagged` instead.
    """
    return _load_records(team_name, now=now)


def task_is_live(task: Any) -> bool:
    """True iff this task is still `in_progress`. The liveness SSOT.

    Named rather than inlined so the per-task consumer (`unflagged_fire`) and
    the per-record consumer (`has_live_listed_task`) share ONE implementation.
    Two copies of the same predicate is how they drift apart.
    """
    return isinstance(task, dict) and task.get("status") == "in_progress"


def has_live_listed_task(record: Any, tasks: Any) -> bool:
    """True iff some task this record covers is still live."""
    if not isinstance(tasks, list):
        return False
    listed = set(record_task_ids(record))
    return any(task_is_live(t) and str(t.get("id")) in listed for t in tasks)


def outstanding_unflagged(
    tasks: Any,
    team_name: str | None = None,
    now: datetime | None = None,
    records: list[dict] | None = None,
) -> list[dict]:
    """THE ONLY SANCTIONED READ PATH FOR SURFACING A RECORD TO A HUMAN OR AGENT.

    Applies BOTH gates, so a caller cannot surface a record by forgetting one:
      - TASK-STATUS: at least one listed task is still `in_progress`.
      - FLAGGED-WAIT: no listed `in_progress` task carries a valid wait.
    (The 24h TTL is applied upstream by `load_records`.)

    WHY THIS EXISTS AS A NAMED SELECTOR RATHER THAN A CONVENTION. Layer 2
    reached records through `unflagged_fire`, which applies both gates; Layer 3
    went straight to `load_records`, which applies neither. MEASURED on one
    40-minute-old record: the lead-side path surfaced it while the teammate-side
    path refused it, both because the task was `completed` AND because a valid
    wait was flagged. The lead-facing text asserts "outstanding launches and no
    flagged wait" — on the ungated path nothing evaluated the second clause, so
    the surface claimed a property the code never checked. A docstring asking
    the next consumer to remember two gates is exactly what produced that; a
    selector makes the next consumer INHERIT them.

    THE TWO GATES ARE DIFFERENT KINDS OF PREDICATE, and that is why only one
    of them could ever have moved into the loader:

      GATE A — task status — is EXPIRY. A record none of whose listed tasks
      is still `in_progress` is dead PERMANENTLY. That is a property of the
      record alone given the task store, so no consumer should be able to opt
      out of it, and it does not interact with the discharge: a discharged
      record is removed, a record on a dead task is removed, no conflict.

      GATE B — flagged wait — is SUPPRESSION. The record is still LIVE and
      still meaningful; we are declining to surface it RIGHT NOW because the
      teammate has flagged. That is a property of the MOMENT, not of the
      record. Move it into any read the discharge uses and
      `discharge_acknowledged` never sees a flagged record to retire — the
      mechanism dies silently, green, because every gate test still passes.

    So expiry filters the READ and suppression filters the SURFACE. Do not
    "simplify" them together: they differ in lifetime, not just in placement.
    """
    rows = records if records is not None else _load_records(team_name, now=now)
    if not isinstance(tasks, list):
        # No task set means neither gate can be evaluated. Surface NOTHING
        # rather than fall back to the ungated list — this function's whole
        # purpose is that an unevaluable gate never reads as a passed gate.
        return []
    out = []
    for record in rows:
        # GATE A — EXPIRY. No live task means the record is dead permanently.
        if not has_live_listed_task(record, tasks):
            continue
        # GATE B — SUPPRESSION. The record is LIVE; we decline to surface it
        # right now because the teammate has flagged. See the note above on
        # why this one cannot move into a read the discharge uses.
        if any_listed_task_flagged(record, tasks):
            continue
        out.append(record)
    return out


def wait_covers_record(task: Any, record: Any) -> bool:
    """True iff this task's VALID wait acknowledges this record's launch.

    THE ACKNOWLEDGMENT SIGNAL IS THE FLAG, NOT THE JOB'S COMPLETION. The
    advisory exists to catch a teammate who backgrounded work and never said
    so. Once it has flagged a wait covering that launch, it has demonstrably
    associated the two, and the record has done its job — whether or not the
    job itself has finished. Nothing needs to observe the shell.

    `since >= registered_at` IS LOAD-BEARING AND MUST NOT BE SIMPLIFIED AWAY.
    It is what makes this precise rather than a blanket amnesty: a wait
    flagged for job 1 does NOT acquit a job 2 launched afterwards, because
    job 2's `registered_at` is later than that wait's `since`.

    Pure: reads a task dict and a record dict, writes nothing.
    """
    if not isinstance(task, dict) or not isinstance(record, dict):
        return False
    if classify_wait(task) is not None:
        return False  # no valid wait to acknowledge anything
    metadata = task.get("metadata")
    wait = metadata.get("intentional_wait") if isinstance(metadata, dict) else None
    since = parse_iso(wait.get("since")) if isinstance(wait, dict) else None
    registered = parse_iso(record.get("registered_at"))
    if since is None or registered is None:
        return False
    return since >= registered


def discharge_acknowledged(
    task: Any,
    team_name: str | None = None,
    now: datetime | None = None,
) -> int:
    """Drop every record this task's valid wait acknowledges. Returns the count.

    RESIDUAL, AND IT IS NOT EMPTY. Discharge needs a TeammateIdle between the
    flag and the clear, because this runs on that event. A teammate that
    flags and clears inside ONE turn, never idling, keeps its record and can
    still draw a stale advisory later. That population correlates with
    UNNECESSARY flagging rather than with diligence — flagging exists because
    you are about to end a turn, and ending a turn is an idle — but it is
    real and is pinned by a test rather than claimed away.
    """
    if not isinstance(task, dict):
        return 0
    task_id = task.get("id")
    if task_id is None:
        return 0
    task_id = str(task_id)
    dropped = 0

    def _apply(records: list[dict]) -> tuple[list[dict], bool]:
        nonlocal dropped
        kept = []
        for record in records:
            if task_id in record_task_ids(record) and wait_covers_record(task, record):
                dropped += 1
                continue
            kept.append(record)
        return kept, dropped > 0

    _atomic_update_records(_apply, team_name=team_name, now=now)
    return dropped


def unflagged_fire(
    task: Any,
    records: list[dict] | None = None,
    now: datetime | None = None,
    team_name: str | None = None,
    tasks: list | None = None,
) -> tuple[bool, str | None, dict | None]:
    """Fire when in_progress + outstanding record + no listed task flagged.

    Returns (fire, wait_class, record). wait_class is set only on fire.
    Pass `tasks` (the team task list) so the R5 silencing check can see the
    record's other tasks; without it only `task` is judged.
    """
    if not isinstance(task, dict):
        return False, None, None
    # THIS GATE COVERS THIS FUNCTION'S CALLERS ONLY — Layer 2. IT IS NOT A
    # PROPERTY OF THE MODULE.
    #
    # An earlier version of this comment claimed "every consumer reaches a
    # record through this function" and named `load_records` as a REJECTED
    # place for the predicate on that basis. MEASURED FALSE: Layer 3's
    # lead-side selector read `load_records` directly and applied neither the
    # status gate nor the flagged-wait gate, so it surfaced records this line
    # refuses. The comment did not merely fail to prevent that — it argued
    # against the check the other consumer needed, and warned the next reader
    # off "cleaning up the duplication". A false scope claim in a comment is
    # worse than no comment, because it stops the reader looking.
    #
    # The gates now live in `outstanding_unflagged` for any read path that
    # surfaces a record. This line stays because Layer 2 is per-task and
    # reaches records through here.
    #
    # It also does NOT resolve the sticky-row defect, which is a different
    # case: a job finishing WITHIN one still-`in_progress` task leaves the
    # record live and the task status unchanged, so no status check of any
    # kind reaches it. That is what the acknowledgment discharge is for.
    if not task_is_live(task):
        return False, None, None
    record = matching_outstanding(task, records=records, now=now, team_name=team_name)
    if record is None:
        return False, None, None
    if any_listed_task_flagged(record, tasks):
        return False, None, record
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
            if task_id in record_task_ids(record) and not record.get("idled_at"):
                record = dict(record)
                record["idled_at"] = stamp
                changed = True
            out.append(record)
        return out, changed

    ok = _atomic_update_records(_apply, team_name=team_name, now=now)
    return bool(ok and changed)


def effective_since(record: Any) -> tuple[datetime | None, int]:
    """The clock Layer 3 measures against, and the window that applies to it.

    Returns (since, threshold_minutes). `idled_at` is preferred; when it is
    absent we fall back to `registered_at` with the longer window, so that a
    missed TeammateIdle cannot disable the lead surface. Before this
    fallback existed, `stamp_idled_at`'s single production call site was the
    only writer of `idled_at`, which made Layer 3 a consumer of Layer 2
    rather than a backstop for it.
    """
    if not isinstance(record, dict):
        return None, LEAD_STALE_MINUTES
    idled = parse_iso(record.get("idled_at"))
    if idled is not None:
        return idled, LEAD_STALE_MINUTES
    return parse_iso(record.get("registered_at")), LEAD_UNIDLED_STALE_MINUTES


def lead_stale(
    record: dict,
    now: datetime | None = None,
) -> bool:
    """True iff the record is older than the window its own clock carries."""
    since, threshold_minutes = effective_since(record)
    if since is None:
        return False
    now = now or utc_now()
    return (now - since).total_seconds() >= threshold_minutes * 60


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
    # TypeError / ValueError are here to keep the module's stated contract —
    # "never raise on missing/corrupt files, empty team name, or MALFORMED
    # RECORDS". A counter entry whose `count` is a non-int is a malformed
    # record, and a mutator coercing it raises ValueError from inside this
    # call. MEASURED before this was added: a `{"count": "not-an-int"}` entry
    # raised straight out of here, so the docstring was false.
    # The caller's own coercion is total as well (see teammate_idle), so this
    # is the contract backstop rather than the primary defence — a mutator
    # should not depend on it to be careless.
    except (OSError, TypeError, ValueError):
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


# --------------------------------------------------------------------------
# Layer 1 — the write path.
#
# This lives here rather than in the host hook deliberately. track_files.py
# hosts the call because it is already registered on PostToolUse
# `Edit|Write|Bash`, so folding into it costs no new subprocess — but the
# host is meant to gain a gate and a call, nothing more. Identity resolution
# inside the host would be a second resolver sitting in a file whose job is
# file tracking, which is exactly the coupling the fold was supposed to
# avoid.
# --------------------------------------------------------------------------


def _truthy_background(value: Any) -> bool:
    return value is True or value == "true" or value == 1


def is_harness_background_bash(input_data: Any) -> bool:
    """True iff this frame is a Bash launch with run_in_background set."""
    if not isinstance(input_data, dict):
        return False
    if input_data.get("tool_name") != "Bash":
        return False
    tool_input = input_data.get("tool_input")
    if not isinstance(tool_input, dict):
        return False
    return _truthy_background(tool_input.get("run_in_background"))


def command_from_frame(input_data: Any) -> str:
    tool_input = input_data.get("tool_input") if isinstance(input_data, dict) else None
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command")
    return command if isinstance(command, str) else ""


# Platform-supplied agent types that are NOT this plugin's agents. Hard-coded
# because they come from the harness rather than from a file we can enumerate.
# This list going stale is a real exposure — see the residual note on
# `agent_type_names_a_member`.
_PLATFORM_AGENT_TYPES = frozenset(
    {"general-purpose", "Explore", "Plan", "statusline-setup"}
)


def _known_agent_types() -> frozenset:
    """Agent-type stems this plugin ships, DERIVED AT RUNTIME from agents/.

    Derived rather than listed so that adding an agent file cannot silently
    open a collision with a teammate name. A hard-coded copy would go stale
    the day someone adds one, and the failure would be a mis-bind rather than
    an error.
    """
    try:
        agents_dir = Path(__file__).resolve().parents[2] / "agents"
        return frozenset(p.stem for p in agents_dir.glob("*.md"))
    except (OSError, IndexError):
        return frozenset()


def agent_type_names_a_member(agent_type: Any, team_name: str) -> bool:
    """True iff the frame's `agent_type` is an IDENTITY rather than a TYPE.

    MEASURED 2026-09-11 on a live in-process Agent-Teams teammate PostToolUse
    Bash frame: `agent_type` carried the teammate's own NAME, not the
    `pact-`-prefixed agentType its team config records. `agent_name` was
    absent and `agent_id` carried no `@`, so no other route resolves. See
    `tests/fixtures/role_frames.py` ::
    captured_posttooluse_teammate_inprocess_bash_background.

    The test is MEMBERSHIP in the team config the platform wrote at spawn —
    a lookup in authoritative local state, not string surgery. Step 4 already
    strips this field today; this validates the value before trusting it.

    RESIDUAL, STATED RATHER THAN CLAIMED AWAY. `classify_session_role` treats
    any `agent_type` outside `LEAD_AGENT_TYPES` as a teammate, so a generic
    Agent-tool subagent reaches this code. The deny set below reduces the
    collision to perverse naming — a member would have to be NAMED after a
    real agent type — but an UNKNOWN FUTURE PLATFORM TYPE colliding with a
    member name remains possible, and that case fails toward MIS-BIND rather
    than silence, which is the worse direction: a launch would be attributed
    to a teammate who did not make it. This is an accepted exposure, not an
    eliminated one.

    TMUX IS UNTESTED, NOT COVERED. Under tmux the frame reportedly carries the
    real type, so this returns False and the caller falls through to the
    registry, which works there because the in-process self-guard does not
    fire. That rests on one captured PreToolUse frame and NO Bash PostToolUse
    frame. It was UNEXERCISED during development because the development
    machine had no tmux teams — which bounds the VERIFICATION, not the
    behaviour. This plugin ships to consumers who may run tmux teams, so do
    not read "no teams to test against" as "a path nobody takes".
    """
    if not isinstance(agent_type, str) or not agent_type:
        return False
    if agent_type in _PLATFORM_AGENT_TYPES:
        return False
    if agent_type in _known_agent_types():
        return False
    from .pact_context import _iter_members

    return any(
        isinstance(m, dict) and m.get("name") == agent_type
        for m in _iter_members(team_name)
    )


def bind_launcher_identity(
    input_data: Any, team_name: str
) -> tuple[str, str, list[str]] | None:
    """Return (agent_name, session_id, task_ids) or None when identity is absent.

    Steps 1-3.5 of resolve_agent_name only. `agent_type` is deliberately NOT
    type-stripped as the owner.

    THE FIELD IS POLYMORPHIC BY ROLE, NOT RANDOMLY UNRELIABLE, and the
    distinction decides when the membership match can be trusted. MEASURED:
    on TEAMMATE frames it carried the member's NAME every time — three
    teammates, two independent instruments, two operators — and on LEAD
    frames it carries the agent-type spelling (`PACT:pact-orchestrator` in
    the team whose file-edits rows were the original evidence). So it is
    consistently a name for teammates and consistently a type for the lead.
    Reading it as "sometimes one, sometimes the other, per frame" would be
    wrong and would undersell a mechanism that is deterministic per role.
    Stripping it unconditionally would therefore attribute a launch to
    whatever string happens to be there, which is why the value is VALIDATED
    against the team config instead of trusted for its shape.

    A hex agent_id is an in-process discriminator, not a teammate name.
    Refusing to guess means the registry stays silent rather than wrong.

    STEP 1 IS INERT IN EVERY TOPOLOGY MEASURED SO FAR AND STAYS ANYWAY.
    `agent_name` is absent from the in-process frame's 15 keys, and the SSOT
    records it absent under tmux too, so it may be dead everywhere — nobody
    has established that. The branch costs one dict lookup on a fail-open
    ordering, so keeping it is a cheap option on a future harness that does
    carry the field, not dead weight. Do not delete it as unreachable
    without measuring the topology you are deleting it for.

    ALL matching in_progress tasks are returned, not one. Requiring exactly
    one silently recorded nothing for a teammate holding two — and holding two
    is behaviour the pact-teachback skill explicitly permits, so the mechanism
    switched itself off for teammates following the framework's own
    instruction. Zero matches stays a no-write: a teammate with no in_progress
    task is not inside a dispatch, so there is no task context for an advisory
    to reference.
    """
    # Function-level: the whole module is imported only once a Bash frame
    # arrives, and these three are needed only once identity is being bound.
    from .pact_context import resolve_agent_name
    from .session_registry import resolve as registry_resolve
    from .task_utils import iter_team_task_jsons

    if not isinstance(input_data, dict) or not team_name:
        return None
    session_id = input_data.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return None

    named_by_name = isinstance(input_data.get("agent_name"), str) and bool(
        input_data.get("agent_name")
    )
    agent_id = input_data.get("agent_id")
    named_by_id_split = isinstance(agent_id, str) and "@" in agent_id
    # The measured in-process route: neither field above is present on a Bash
    # PostToolUse frame, and `agent_type` carries the name instead.
    named_by_membership = agent_type_names_a_member(
        input_data.get("agent_type"), team_name
    )
    registry_name = None
    # THIS EARLY RETURN IS THE COLLAPSE PROTECTION. With no name on the frame,
    # no `@`-bearing id, and no validated membership match, the only remaining
    # route would be an UNVALIDATED type-strip of `agent_type` — which would
    # attribute a launch to whatever string that field happens to hold and
    # collapse same-type siblings onto one name. Refusing here is what makes
    # the registry silent rather than wrong, and silence is the acceptable
    # direction: a mis-bind names a teammate who did not launch the work.
    #
    # A second guard further down used to restate this. It was DEAD — reaching
    # it with all three flags false implies `registry_name is not None`,
    # because that exact combination already returned here, so its conjunction
    # was unsatisfiable. Deleting it proved zero kills across the full suite.
    # Do not reintroduce one: a redundant predicate implies this line does not
    # already hold the property, which invites the next reader to delete the
    # wrong one of the two.
    if not named_by_name and not named_by_id_split and not named_by_membership:
        resolved = registry_resolve(session_id)
        if resolved and "@" in resolved:
            registry_name = resolved.split("@")[0]
        else:
            return None

    # THE VALUE THAT PASSED VALIDATION IS THE VALUE THAT GETS RECORDED.
    # `agent_type_names_a_member` validates the RAW `agent_type`; routing that
    # case back through `resolve_agent_name` would re-derive a DIFFERENT
    # string, because its Step 4 strips a `pact-` prefix. MEASURED before this
    # was fixed: a member named `pact-reviewer` validated, then bound to its
    # sibling `reviewer` and to that sibling's task — a launch attributed to a
    # teammate who did not make it, which is the unacceptable direction.
    #
    # THE RAW VALUE IS USED ON THE MEMBERSHIP ROUTE AND NOWHERE ELSE. On the
    # registry route and the `agent_name` / `@`-bearing `agent_id` routes the
    # resolved value is the correct one and `agent_type` may hold a genuine
    # type there, so letting the raw value reach those branches would move the
    # mis-bind rather than close it.
    #
    # Precedence is preserved: Steps 1 and 2 still win over the validated
    # Step-4 route, which is why they are tested before it rather than after.
    # The final branch needs no `named_by_membership` test — reaching it means
    # `registry_name` is None and neither earlier flag is set, and that
    # combination already returned at the early return above unless membership
    # matched.
    if registry_name:
        agent_name = registry_name
    elif named_by_name or named_by_id_split:
        agent_name = resolve_agent_name(input_data, team_name=team_name)
    else:
        agent_name = input_data.get("agent_type")
    if not agent_name:
        return None

    task_ids = []
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
        task_ids.append(str(task_id))
    if not task_ids:
        return None
    return agent_name, session_id, task_ids


def record_background_launch(input_data: Any) -> bool:
    """Write one registry row when the frame is a recordable teammate launch.

    Fail-open on every path — the host calls this for its side effect only and
    must not be disturbed by anything that happens here.
    """
    from .pact_context import classify_session_role

    if not is_harness_background_bash(input_data):
        return False
    if classify_session_role(input_data) != "teammate":
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
    agent_name, session_id, task_ids = bound
    return append_record(
        {
            "agent_name": agent_name,
            "session_id": session_id,
            "task_ids": task_ids,
            "command": command,
            "registered_at": iso_now(),
        },
        team_name=team_name,
    )
