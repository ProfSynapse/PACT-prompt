# Runbook: Unflagged Background Wait Probe (#1625)

**Purpose:** live-process confirmation that the mechanical floor under Wait
Discipline Layer 2 fires in a real Agent-Teams session. Pytest covers the
registry predicate, TeammateIdle N=3 advisory, and lead `SendMessage`
directive. It cannot pin the wake channel (#1620): teammate background
notifications are wake-on-read. This runbook is the L3 probe for
`unflagged_background_scan` (and the tracker write that feeds it).

Record both topologies (in-process and tmux). A green pytest suite does
not close the wake-delivery question.

---

## §1 — Measurement protocol (per trial)

1. Spawn a specialist teammate with an `in_progress` task.
2. The teammate launches exactly ONE harness-backgrounded command —
   `sleep 8; echo PROBE_DONE` via the `run_in_background` parameter, NEVER
   shell `&` — and does **not** SET `intentional_wait`.
3. The teammate sends a one-line interim report and ends the turn.
4. Confirm on disk:
   - `{CLAUDE_CONFIG_DIR}/teams/{team}/background_work.json` has one row
     bound to that teammate and task id.
   - The task file still has `intentional_wait: null` (or the key absent).
5. Allow TeammateIdle to fire three times (or wait for the platform idle
   cadence). Expect a `systemMessage` naming SET `intentional_wait` or
   transfer-the-watch. The advisory must not carry the zombie
   "no response needed" preamble.
6. Wait until `idled_at` is older than 10 minutes (or back-date `idled_at`
   on the registry row for a compressed trial).
7. On the lead, start a new turn (`UserPromptSubmit` or a fresh
   `SessionStart`). Expect `additionalContext` from
   `unflagged_background_scan` that names the teammate and directs
   `SendMessage`. It must not mention `awaiting_lead_completion` or a
   forgotten completion wake.
8. Lead `SendMessage`s the teammate. Expect the teammate to wake
   (wake-on-read). Record whether the wake arrived only after that
   message.

**Do not claim pytest can pin step 8.**

---

## §2 — Trial ledger

| # | Topology | Tracker row? | Idle advisory at N=3? | Lead surface? | Wake after SendMessage? | Notes |
|---|----------|--------------|-----------------------|---------------|-------------------------|-------|
|   | in-process |  |  |  |  |  |
|   | tmux |  |  |  |  |  |

---

## §3 — Negative controls

- Mid-arc teammate (`in_progress`, null wait, **no** registry row): no
  unflagged advisory, no lead surface.
- Durable launch (`npm run dev` with `run_in_background`): no registry row.
- Valid `intentional_wait` after a recorded launch: both alarms clear.
- A different task idling on `awaiting_lead_completion` still belongs to
  `missed_wake_scan` only.

---

## §4 — Capture note

A live PostToolUse `Bash` + `run_in_background` stdin frame was **not**
captured in the implementation environment (no Claude Code teammate
process). Encoded keys are the in-repo contracts named on
`synthesized_teammate_bash_background` in `tests/fixtures/role_frames.py`.
If a live capture shows the teammate writer and lead reader resolving
different team directories, or cannot uniquely name one of two
same-`agentType` siblings, stop and report — do not guess.
