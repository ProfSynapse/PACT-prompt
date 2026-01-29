#!/bin/bash
# scripts/verify-task-hierarchy.sh
# Verifies that Task Hierarchy sections in command files contain
# the expected lifecycle patterns (TaskCreate, in_progress, completed)

set -e

echo "=== Task Hierarchy Verification ==="
echo ""

COMMANDS_DIR="pact-plugin/commands"

if [ ! -d "$COMMANDS_DIR" ]; then
    echo "ERROR: Commands directory $COMMANDS_DIR not found"
    exit 1
fi

PASS=0
FAIL=0

# Function to check a command file for required patterns
# Args: file, description, pattern1, pattern2, ...
# Optional env var SECTION_HEADING overrides the default "## Task Hierarchy"
verify_patterns() {
    local file="$1"
    local name="$2"
    shift 2
    local patterns=("$@")

    local filepath="$COMMANDS_DIR/$file"
    local heading="${SECTION_HEADING:-## Task Hierarchy}"

    if [ ! -f "$filepath" ]; then
        echo "  ✗ $name: FILE NOT FOUND ($filepath)"
        FAIL=$((FAIL + 1))
        return
    fi

    # Extract section from heading to next ## heading
    local section
    section=$(sed -n "/^${heading}/,/^## /p" "$filepath" | sed '$d')

    if [ -z "$section" ]; then
        echo "  ✗ $name: No '$heading' section found"
        FAIL=$((FAIL + 1))
        return
    fi

    local missing=()
    for pattern in "${patterns[@]}"; do
        if ! echo "$section" | grep -q "$pattern"; then
            missing+=("$pattern")
        fi
    done

    if [ ${#missing[@]} -eq 0 ]; then
        echo "  ✓ $name: all ${#patterns[@]} patterns present"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $name: missing ${#missing[@]} of ${#patterns[@]} patterns:"
        for m in "${missing[@]}"; do
            echo "      - \"$m\""
        done
        FAIL=$((FAIL + 1))
    fi
}

# --- orchestrate.md ---
echo "orchestrate.md:"
verify_patterns "orchestrate.md" "Feature task lifecycle" \
    "TaskCreate: Feature task" \
    "in_progress" \
    "completed"
verify_patterns "orchestrate.md" "Phase task lifecycle" \
    "TaskCreate: Phase tasks" \
    "in_progress" \
    "completed"
verify_patterns "orchestrate.md" "Agent task lifecycle" \
    "agent task" \
    "in_progress" \
    "completed"
verify_patterns "orchestrate.md" "Skipped phase handling" \
    "Skipped phases" \
    "completed" \
    "metadata"
echo ""

# --- comPACT.md ---
echo "comPACT.md:"
verify_patterns "comPACT.md" "Feature task lifecycle" \
    "TaskCreate: Feature task" \
    "in_progress" \
    "completed"
verify_patterns "comPACT.md" "Agent task lifecycle" \
    "Agent task" \
    "in_progress" \
    "completed"
echo ""

# --- peer-review.md ---
echo "peer-review.md:"
verify_patterns "peer-review.md" "Review task lifecycle" \
    "TaskCreate: Review task" \
    "in_progress" \
    "completed"
verify_patterns "peer-review.md" "Reviewer task lifecycle" \
    "TaskCreate: Reviewer" \
    "in_progress" \
    "completed"
echo ""

# --- plan-mode.md ---
echo "plan-mode.md:"
verify_patterns "plan-mode.md" "Planning task lifecycle" \
    "TaskCreate: Planning task" \
    "in_progress" \
    "completed"
verify_patterns "plan-mode.md" "Consultation task lifecycle" \
    "Consultation task" \
    "in_progress" \
    "completed"
echo ""

# --- rePACT.md ---
echo "rePACT.md:"
verify_patterns "rePACT.md" "Sub-feature task lifecycle" \
    "TaskCreate: Sub-feature task" \
    "in_progress" \
    "completed"
echo ""

# --- imPACT.md ---
# imPACT uses different section names than other commands
echo "imPACT.md:"
SECTION_HEADING="## Task Operations" \
verify_patterns "imPACT.md" "Blocker task lifecycle" \
    "TaskCreate" \
    "completed"
SECTION_HEADING="## Phase Re-Entry Task Protocol" \
verify_patterns "imPACT.md" "Phase re-entry lifecycle" \
    "TaskCreate" \
    "in_progress" \
    "completed"
echo ""

# --- Summary ---
echo "=== Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -gt 0 ]; then
    echo "VERIFICATION FAILED"
    exit 1
else
    echo "VERIFICATION PASSED"
    exit 0
fi
