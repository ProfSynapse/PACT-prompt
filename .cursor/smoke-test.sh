#!/usr/bin/env bash
# Live end-to-end smoke test: load the PACT plugin into a real Claude Code
# session and confirm the orchestrator persona is active and the plugin's
# structure validates.
#
# Two phases:
#   1. Offline: `claude plugin validate` on the plugin + marketplace (no auth).
#   2. Live:    a single headless `-p` turn with the plugin loaded and the
#               orchestrator persona selected. Requires ANTHROPIC_API_KEY.
#
# The live phase is skipped (not failed) when ANTHROPIC_API_KEY is absent, so
# the offline phase still runs in environments without the secret.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/pact-plugin"

# Resolve the claude CLI (user-local npm prefix from install.sh, or PATH).
export PATH="$HOME/.npm-global/bin:$PATH"
if ! command -v claude >/dev/null 2>&1; then
  echo "FAIL: claude CLI not found. Run .cursor/install.sh first." >&2
  exit 1
fi
echo "claude version: $(claude --version)"

echo
echo "== Phase 1: offline plugin + marketplace validation =="
claude plugin validate "$PLUGIN_DIR"
claude plugin validate "$REPO_ROOT"

echo
echo "== Phase 2: live headless session =="
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "SKIP: ANTHROPIC_API_KEY not set — offline validation passed; skipping live model call."
  exit 0
fi

# Prerequisites the plugin documents for agent operation.
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
export CLAUDE_CODE_ENABLE_TODO_TOOLS=1

MARKER="PACT_SMOKE_OK"
PROMPT="You are running as the PACT orchestrator persona loaded from a plugin. \
Do NOT spawn any agents, do NOT use any tools, and do NOT start an orchestration. \
Reply with exactly one line: the token ${MARKER} followed by a comma-separated \
list of the PACT specialist agent roles you coordinate."

set +e
OUT="$(claude \
  --plugin-dir "$PLUGIN_DIR" \
  --agent PACT:pact-orchestrator \
  --permission-mode bypassPermissions \
  --model sonnet \
  --output-format text \
  -p "$PROMPT" 2>&1)"
RC=$?
set -e

echo "---- model output ----"
echo "$OUT"
echo "----------------------"

if [ $RC -ne 0 ]; then
  echo "FAIL: claude exited with code $RC" >&2
  exit 1
fi

if echo "$OUT" | grep -q "$MARKER"; then
  echo "PASS: plugin loaded, orchestrator persona active, model round-trip succeeded."
  exit 0
fi

echo "FAIL: expected marker '$MARKER' not found in model output." >&2
exit 1
