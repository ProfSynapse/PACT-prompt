#!/usr/bin/env python3
"""
Location: pact-plugin/hooks/wait_filler_gate.py
Summary: PreToolUse hook (matcher: Bash) that denies bare `true`/`sleep <N>`
    filler commands — the turn-manufacturing no-ops a waiting agent emits
    under the filler-call compulsion.
Used by: pact-plugin/hooks/hooks.json PreToolUse "Bash" matcher entry.

A command is denied iff, after normalization, it IS nothing but a filler
no-op. Normalization, in order:
  1. Strip leading AND trailing whitespace (including ALL trailing
     newlines). A newline remaining after that strip is interior — the
     command is composed — allow.
  2. Strip leading env assignments (`FOO=1 BAR=2 sleep 5` is still filler).
  3. Strip one optional `command `/`builtin ` prefix.
  4. Strip one optional trailing comment (` # ...`).
Then deny on \\A(true|sleep (([0-9]+(\\.[0-9]*)?|\\.[0-9]+)[smhd]?|infinity))\\Z —
anchored \\A...\\Z, never $ (which matches before a single trailing
newline and would re-make the newline forms order-dependent). Any shell
metacharacter or composition fails the anchored pattern and is allowed:
this is an honest-mistake guard, not an adversarial boundary.

Under-block shapes consistent with the grammar, by design: a tab or
multiple spaces between `sleep` and the duration (the pattern's separator
is one literal space), and quoted env values containing spaces
(`FOO="a b" sleep 5` mangles through the env-assignment strip). Both stay
allowed — the persona layer is the standard; this hook is the floor.

Fail direction: OPEN. Any internal error — malformed stdin, a matcher
exception — allows the command (exit 0 + stderr note). A load/match
failure that denied on matcher=Bash would block every Bash call in every
consumer session, and the gated commands are inert no-ops whose occasional
escape costs nothing.

Input: JSON on stdin, {"tool_name": "Bash", "tool_input": {"command": "<cmd>"}}
Output: deny = {"hookSpecificOutput": {...}} + exit 2;
        allow = {"suppressOutput": true} + exit 0. Errors to stderr.
"""

from __future__ import annotations

import json
import re
import sys

_ALLOW_OUTPUT = json.dumps({"suppressOutput": True})

_DENY_REASON = (
    "Passive waiting is the protocol — end the turn with no tool call; "
    "teammate messages arrive as their own turns. A bare true/sleep filler "
    "call manufactures the next turn without producing new information; "
    "compose it with real work or end the turn."
)

_FILLER_PATTERN = re.compile(
    r"\A(true|sleep (([0-9]+(\.[0-9]*)?|\.[0-9]+)[smhd]?|infinity))\Z"
)
_ENV_ASSIGNMENT = re.compile(r"\A[A-Za-z_][A-Za-z0-9_]*=\S*\s+")
_WRAPPER_PREFIX = re.compile(r"\A(?:command|builtin)\s+")
_TRAILING_COMMENT = re.compile(r"\s+#.*\Z")


def _is_filler_command(command: str) -> bool:
    """True iff the command is nothing but a bare `true`/`sleep <N>`.

    Applies the module-docstring normalization chain in order. The chain
    only ever strips benign decoration; anything it cannot reduce to the
    anchored pattern (metacharacters, composition, quoting, wrappers like
    `sudo`/`time`) is allowed.
    """
    normalized = command.strip()
    if "\n" in normalized:
        return False  # interior newline = composed command
    while True:
        stripped = _ENV_ASSIGNMENT.sub("", normalized, count=1)
        if stripped == normalized:
            break
        normalized = stripped
    normalized = _WRAPPER_PREFIX.sub("", normalized, count=1)
    normalized = _TRAILING_COMMENT.sub("", normalized, count=1)
    return _FILLER_PATTERN.match(normalized) is not None


def main() -> None:
    try:
        try:
            input_data = json.load(sys.stdin)
        except ValueError as error:
            print(
                f"wait_filler_gate: malformed stdin JSON — allowing "
                f"(fail-open): {error}",
                file=sys.stderr,
            )
            sys.exit(0)

        if not isinstance(input_data, dict) or input_data.get("tool_name") != "Bash":
            print(_ALLOW_OUTPUT)
            sys.exit(0)

        tool_input = input_data.get("tool_input")
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        if not isinstance(command, str) or not _is_filler_command(command):
            print(_ALLOW_OUTPUT)
            sys.exit(0)

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": _DENY_REASON,
            }
        }))
        sys.exit(2)

    except Exception as error:  # noqa: BLE001 — fail-open catch-all
        print(
            f"wait_filler_gate: internal error — allowing (fail-open): {error}",
            file=sys.stderr,
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
