#!/usr/bin/env python3
"""
Location: .claude/hooks/validate_handoff.py
Summary: SubagentStop hook that validates PACT agent handoff format.
Used by: Claude Code settings.json SubagentStop hook

Checks that PACT agents complete with proper handoff information
containing: what was produced, key decisions, next agent needs.

Input: JSON from stdin with `transcript` and `agent_id`
Output: JSON with `systemMessage` if handoff format is incomplete
"""

import json
import sys
import re


# Required handoff elements with their patterns and descriptions
HANDOFF_ELEMENTS = {
    "what_produced": {
        "patterns": [
            r"(?:produced|created|generated|output|implemented|wrote|built|delivered)",
            r"(?:file|document|component|module|function|class|api|endpoint|schema)",
            r"(?:completed|finished|done with)",
        ],
        "description": "what was produced",
    },
    "key_decisions": {
        "patterns": [
            r"(?:decision|chose|selected|opted|rationale|reason|because)",
            r"(?:trade-?off|alternative|approach|strategy|pattern)",
            r"(?:decided to|went with|picked)",
        ],
        "description": "key decisions",
    },
    "next_steps": {
        "patterns": [
            r"(?:next|needs|requires|depends|should|must|recommend)",
            r"(?:follow-?up|remaining|todo|to-?do|action item)",
            r"(?:test engineer|tester|reviewer|next agent|next phase)",
        ],
        "description": "next steps/needs",
    },
}


def validate_handoff(transcript: str) -> tuple:
    """
    Check if transcript contains proper handoff elements.

    Args:
        transcript: The agent's complete output/transcript

    Returns:
        Tuple of (is_valid, missing_elements)
    """
    missing = []

    # First, check for explicit handoff section (indicates structured handoff)
    has_handoff_section = bool(re.search(
        r"(?:##?\s*)?(?:handoff|hand-off|hand off|summary|output|deliverables)[\s:]*\n",
        transcript,
        re.IGNORECASE
    ))

    # If there's an explicit handoff section, be more lenient
    if has_handoff_section:
        return True, []

    # Otherwise, check for implicit handoff elements
    transcript_lower = transcript.lower()

    for element_key, element_info in HANDOFF_ELEMENTS.items():
        found = False
        for pattern in element_info["patterns"]:
            if re.search(pattern, transcript_lower):
                found = True
                break

        if not found:
            missing.append(element_info["description"])

    # Consider valid if at least 2 out of 3 elements are present
    # (some agents may not have explicit decisions if straightforward)
    is_valid = len(missing) <= 1

    return is_valid, missing


def is_pact_agent(agent_id: str) -> bool:
    """
    Check if the agent is a PACT framework agent.

    Args:
        agent_id: The identifier of the agent

    Returns:
        True if this is a PACT agent that should be validated
    """
    if not agent_id:
        return False

    pact_prefixes = ["pact-", "PACT-", "pact_", "PACT_"]
    return any(agent_id.startswith(prefix) for prefix in pact_prefixes)


# Phase-completing agents that produce deliverables requiring handoff validation
# Utility agents (e.g., pact-memory-agent) are excluded as they don't complete phases
PHASE_COMPLETING_AGENTS = [
    "pact-preparer",
    "pact-architect",
    "pact-backend-coder",
    "pact-frontend-coder",
    "pact-database-engineer",
    "pact-test-engineer",
    "pact-n8n",
]


def is_phase_completing_agent(agent_id: str) -> bool:
    """
    Check if this agent completes a PACT phase (vs utility/helper agents).

    Only phase-completing agents need handoff validation. Utility agents
    like pact-memory-agent don't produce deliverables requiring handoff.

    Args:
        agent_id: The identifier of the agent

    Returns:
        True if this agent completes a phase and needs handoff validation
    """
    if not agent_id:
        return False

    return agent_id.lower() in PHASE_COMPLETING_AGENTS


def main():
    """
    Main entry point for the SubagentStop hook.

    Reads agent transcript from stdin, validates handoff format for PACT agents,
    and outputs a warning message if the handoff is incomplete.
    """
    try:
        # Read input from stdin
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            # No input or invalid JSON - can't validate
            sys.exit(0)

        transcript = input_data.get("transcript", "")
        agent_id = input_data.get("agent_id", "")

        # Only validate PACT agents
        if not is_pact_agent(agent_id):
            sys.exit(0)

        # Only validate phase-completing agents (skip utility agents like pact-memory-agent)
        if not is_phase_completing_agent(agent_id):
            sys.exit(0)

        # Skip validation if transcript is very short (likely an error case)
        if len(transcript) < 100:
            sys.exit(0)

        is_valid, missing = validate_handoff(transcript)

        if not is_valid and missing:
            # Provide specific, actionable guidance
            missing_str = ', '.join(missing)
            output = {
                "systemMessage": (
                    f"PACT Handoff: '{agent_id}' missing {missing_str}. "
                    "Good handoff example: '## Summary\\n- Created X\\n- Decided Y because Z\\n- Next: test engineer should verify...'"
                )
            }
            print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        # Don't block on errors - just warn
        print(f"Hook warning (validate_handoff): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
