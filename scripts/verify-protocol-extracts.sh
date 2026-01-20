#!/bin/bash
# scripts/verify-protocol-extracts.sh
# Verifies that protocol extract files have the expected line counts
# based on the VSM-aligned protocol refactor plan.

set -e

echo "=== Protocol Extract Verification ==="
echo ""

SOURCE="pact-plugin/protocols/pact-protocols.md"
PROTOCOLS_DIR="pact-plugin/protocols"

if [ ! -f "$SOURCE" ]; then
    echo "ERROR: Source file $SOURCE not found"
    exit 1
fi

PASS=0
FAIL=0

verify() {
    local expected=$1
    local file=$2
    local name=$3

    if [ ! -f "$PROTOCOLS_DIR/$file" ]; then
        echo "✗ $name: FILE NOT FOUND ($PROTOCOLS_DIR/$file)"
        FAIL=$((FAIL + 1))
        return
    fi

    local actual=$(wc -l < "$PROTOCOLS_DIR/$file" | tr -d ' ')

    if [ "$actual" -eq "$expected" ]; then
        echo "✓ $name: $actual lines (expected $expected)"
        PASS=$((PASS + 1))
    else
        echo "✗ $name: $actual lines (expected $expected)"
        FAIL=$((FAIL + 1))
    fi
}

# Single-range extracts
verify 135 "pact-s5-policy.md" "S5 Policy (lines 13-147)"
verify 72 "pact-s4-checkpoints.md" "S4 Checkpoints (lines 148-219)"
verify 74 "pact-s4-environment.md" "S4 Environment (lines 220-293)"
verify 65 "pact-s4-tension.md" "S4 Tension (lines 294-358)"
verify 75 "pact-s1-autonomy.md" "S1 Autonomy (lines 481-555)"
verify 62 "pact-variety.md" "Variety (lines 599-660)"

# Combined-range extracts
verify 137 "pact-s2-coordination.md" "S2 Coordination (lines 359-480 + 799-813)"
verify 127 "pact-workflows.md" "Workflows (lines 661-787)"
verify 89 "pact-phase-transitions.md" "Phase Transitions (lines 788-798 + 814-891)"
verify 25 "pact-documentation.md" "Documentation (lines 892-916)"

echo ""
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
