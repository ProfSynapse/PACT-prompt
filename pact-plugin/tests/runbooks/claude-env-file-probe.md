# Runbook: CLAUDE_ENV_FILE dogfood live-probe (Phase A gate, claude-project-dir-once)

**Purpose:** the ONE documented live-probe smoke note for the
`CLAUDE_ENV_FILE` distribution channel that `hooks/session_init.py` Phase A
relies on. The unit/integration layers ship in the PR
(`tests/test_session_init_env_file.py`); what they cannot prove is the
platform half of the contract — that a SessionStart hook's appended
`export VAR=value` line actually lands in a subsequent Bash-tool environment.
This runbook is that measurement, plus the two premises the design keys on
(hook cwd, version floor).

**Status: RUN 2026-09-09, Claude Code 2.1.266, macOS (Darwin).** Results in §3.

## §1 — Method (throwaway; never the shipped hooks.json)

Scratch config only — the probe registers a one-line SessionStart hook in a
disposable `CLAUDE_CONFIG_DIR`, never in any real config:

1. `mkdir -p /tmp/pact-env-file-probe/{config,project}`; scratch
   `config/settings.json` registers a matcher-less SessionStart hook running
   `/tmp/pact-env-file-probe/hook.sh`.
2. `hook.sh` logs `pwd`, `$CLAUDE_PROJECT_DIR`, `$CLAUDE_ENV_FILE` to a probe
   log, then appends `export PACT_PROBE_VAR=probe-ok` to `"$CLAUDE_ENV_FILE"`
   (guarded on non-empty, per the hooks doc's own example shape).
3. Headless leg: from the probe project dir,
   `CLAUDE_CONFIG_DIR=/tmp/pact-env-file-probe/config claude -p --dangerously-skip-permissions "<prompt that runs exactly: echo PROBE_VALUE=${PACT_PROBE_VAR:-UNSET}>"`.
4. Control leg: same prompt against a hook-less scratch config — must print
   `PROBE_VALUE=UNSET`, separating the env-file channel from ambient shell
   inheritance.

## §2 — Acceptance criteria

1. **Channel works:** headless spawned-Bash prints `PROBE_VALUE=probe-ok`;
   control prints `PROBE_VALUE=UNSET`.
2. **Hook-cwd premise:** `os.getcwd()` semantics inside a SessionStart hook
   match the platform's `CLAUDE_PROJECT_DIR` (soundness of the record-side
   cwd-fallback leg).
3. **Version floor:** changelog evidence for when `CLAUDE_ENV_FILE` became
   reliable; the shipped hook must no-op cleanly when the var is unset.

## §3 — Results (2026-09-09, v2.1.266)

1. **PASS.** Headless leg printed `PROBE_VALUE=probe-ok`; hook-less control
   printed `PROBE_VALUE=UNSET`. The env-file append reaches the spawned
   Bash-tool environment. `$CLAUDE_ENV_FILE` pointed at
   `<config>/session-env/<session-uuid>/sessionstart-hook-0.sh`.
2. **PASS, with a macOS nuance.** Hook process received
   `CLAUDE_PROJECT_DIR=/private/tmp/pact-env-file-probe/project`; the shell's
   logical `pwd` printed `/tmp/...` (macOS `/tmp` symlink), but Python's
   `os.getcwd()` returns the PHYSICAL path (`/private/tmp/...`) — matching the
   platform value. The premise holds for the Python implementation; a
   shell-level string comparison would false-negative through symlinked roots.
3. **Floor: introduction not changelogged.** Earliest `CLAUDE_ENV_FILE`
   changelog entries are fixes (2.1.108, 2.1.111, 2.1.136 — the last covers
   staleness after `/resume` or `/clear`). Installed 2.1.266 postdates all of
   them. The implementation's unset-var no-op covers older versions by
   failing open.

**Unverified modes (explicitly not claimed):** in-process teammate Bash and
tmux teammate Bash propagation were not launchable from the teammate session
that ran this probe. The measured leg is the headless spawned-Bash path; the
interactive spawned-Bash path shares the Bash tool's env construction but was
not separately driven. The session-record rung (Phase B) covers sessions
where the channel is absent.

**Cleanup:** `/tmp/pact-env-file-probe/` is throwaway; no shipped file
references it. Re-run by repeating §1 on any newer platform version.
