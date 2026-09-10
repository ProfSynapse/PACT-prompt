# Runbook: Teammate Background-Task Wake-Channel Probe (#1620)

**Purpose:** the measurement record behind the teammate wait-discipline layers
pinned in `skills/pact-agent-teams/SKILL.md` ("Wait Discipline for
Self-Started Work") and the pin tests in
`tests/test_wait_discipline_layers_pinned.py`. Layer 3's prescription — route
long watches through the team-lead rather than a self-backgrounded task —
stands on this ledger. A pytest cannot pin the underlying behavior (it spans
live sessions and the platform's notification machinery, not repo code), so
this runbook plus the ledger is the durable, re-runnable artifact.

---

## §1 — Measurement protocol (per trial)

1. The teammate launches exactly ONE harness-backgrounded command —
   `sleep N; echo PROBE_DONE` via the `run_in_background` parameter, NEVER
   shell `&` — and states the returned task ID in its launch message (the ID
   proves harness-level tracking).
2. The teammate SETs
   `intentional_wait{reason=probe_background_wake, expected_resolver=harness-task-notification, since=<utc>}`
   and ends its turn with no further calls.
3. Wake = the teammate sends `PROBE: woke at <utc>` unprompted after
   completion. No reply within completion + 3 min scores the push question
   negative (a push channel delivers promptly); the lead clears the flag and
   records the trial. The observation window itself stays open to
   completion + 10 min regardless: it must exceed both the 3-min negative
   threshold and the +6..8 min silent-window observations of §2 — the queued
   drains there landed 8m20s–9m31s after completion, so a window ending at
   either bound would misread §3's late-drain shape as no wake at all. Any
   wake arriving inside the window is recorded with its timestamp, trigger,
   and clock source, and discriminated per §3.

**Record per trial:** agent type, sleep duration, task ID, wake y/n, latency
if woken, clock source.

**Round-2 cleanliness condition:** the lead stays fully silent for the whole
window — no lead-backgrounded commands and no lead `SendMessage` after the
launch. Round 1 did not control this, which is what its false negatives (and
false retraction) turned on.

**Clock discipline:** compute every latency from platform envelope timestamps
(or the task's own output-file stamp / printed completion timestamp), never
from the teammate's `date -u` — see the clock-skew caveat in §4.

---

## §2 — Trial ledger (7 measurement events, 2026-09-09/10)

Round 1 (lead active during window):

| # | Agent type | Duration | Task ID | Wake? | Latency (platform clocks) | Notes |
|---|-----------|----------|---------|-------|---------------------------|-------|
| 1 | pact-architect | 45 s | — | ❌ (none observed) | — | original probe; flag `since` clock uncertain; participant corroborated: "nothing re-invoked me until your message arrived" |
| 2 | pact-backend-coder | 60 s | `blzlwlsgp` | ✅ late | ~4.5 min (sleep ended ~00:34:40Z, wake 00:39:13Z) | first read negative; teammate later reported the notification DID arrive, "queued behind your message" (the lead's flag-clear `SendMessage`) |
| 3 | pact-test-engineer | 60 s | `bqo37owot` | ✅ late | ~4.3 min (wake 00:39:13Z) | same shape as trial 2 |

Round 2 (lead fully silent — clean probe):

| # | Agent type | Duration | Task ID | Wake? | Latency (platform clocks) | Notes |
|---|-----------|----------|---------|-------|---------------------------|-------|
| 4 | pact-backend-coder | 45 s | `bw6ijyqzl` | ✅ late | 9m31s (task output stamp 00:43:41Z → re-invocation 00:53:12Z) | none at +8 min with lead dark; the queued gap terminated exactly when the lead's flag-clear `SendMessage` turned the session |
| 5 | pact-test-engineer | 120 s | `bxl4hrkwp` | ✅ late | 8m20s (output-file mtime 00:44:59Z → re-invocation 00:53:19Z) | none at +6 min with lead dark; the two round-2 wakes landed 7 s apart (00:53:12 / 00:53:19) tracking the lead's two flag-clear messages, NOT the two completion times (00:43:41 vs 00:44:59) — per-notification delivery at the next message-driven turn |

Post-campaign timing confirmations (rows 6–7; no new trials — precision
follow-ups on trials 4 and 5 using task-output stamps immune to teammate
clock skew):

| # | Subject | Finding |
|---|---------|---------|
| 6 | trial 4 follow-up (`bw6ijyqzl`) | task printed its own completion stamp 00:43:41Z; notification re-invoked the session at 00:53:12Z — queued for the entire silent window, delivered only inside a message-driven wake |
| 7 | trial 5 follow-up (`bxl4hrkwp`) | completed 00:44:59Z (output-file mtime); re-invoked 00:53:19Z — same shape; discrimination note: wake spacing tracks lead messages, not completions |

Lead-side contrast (same sessions): the LEAD session provably wakes on
harness-backgrounded task completion — measured 3x (two external-reviewer
watchers + one timer), each re-invoking with output and no external stimulus.
The lead's channel is push; the teammate's is not.

---

## §3 — The retracted verdict (kept on record)

After trials 1–3 the ledger was recorded as **"3/3 negative — teammate wake
does not exist"**. That verdict was **retracted**: both round-1 teammates
subsequently reported the completion notification DID arrive and re-invoke
them — late, and only in conjunction with the lead's flag-clear
`SendMessage`s (both wakes at the same instant, 00:39:13Z, despite different
completion times — the fingerprint of queued-drain behind a message-driven
wake, not slow independent delivery). Round 2 then isolated the variable:
with the lead dark, NO wake occurred at all within the window (+6 to +8 min),
and the queued notifications delivered only when the lead's messages later
turned both sessions.

Any future reader re-running this measurement should expect the same
two-step shape: a silent window that reads as "no wake", followed by a late
wake that reads as "slow push". The discriminator is whether the wake's
timestamp tracks the completion time or the lead's message time — and
whether ANY wake occurs with the lead silent.

---

## §4 — Clock-skew caveat (load-bearing for latency numbers)

Teammate `date -u` values disagreed with platform envelope timestamps by
~20–40 min, differently per teammate (trial 2's own-clock math said ~46 min
where platform envelopes said ~4.5 min; trial 3's said ~27 min vs ~4.3 min).
Latency figures computed from teammate clocks are unreliable; the
platform-envelope / task-output-stamp math above is the defensible number.
Always record the clock source per trial.

---

## §5 — Final model (what the layers teach)

Teammate background-task notification is **wake-on-read, not push**:
completion ENQUEUES the notification, but delivery to an idle teammate
session is DEFERRED — it surfaces only when another stimulus (typically the
lead's `SendMessage`) wakes that session. A teammate watcher therefore cannot
self-terminate a wait, and routing long watches through the lead is not a
workaround — the lead's channel is the only push channel in the system. If a
future platform measurement shows teammate notifications push-delivered,
re-run §1 (both rounds, including the lead-silent condition) and demote the
layer-3 routing to a preference; the unconditional `intentional_wait` flag
(layer 2) is what made every trial in this ledger auditable and stays either
way.
