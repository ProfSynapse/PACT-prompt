#!/bin/bash
# scripts/verify-protocol-extracts.sh
# Verifies that protocol extract files match their SSOT sections verbatim

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

# Function to verify verbatim match
# Args: extract_file, description, line_ranges (space-separated sed ranges)
verify() {
    local file="$1"
    local name="$2"
    shift 2
    local ranges="$@"

    if [ ! -f "$PROTOCOLS_DIR/$file" ]; then
        echo "✗ $name: FILE NOT FOUND ($PROTOCOLS_DIR/$file)"
        FAIL=$((FAIL + 1))
        return
    fi

    # Extract SSOT content using sed ranges to a temp file
    local tmpfile=$(mktemp)
    trap "rm -f $tmpfile" RETURN

    for range in $ranges; do
        sed -n "${range}p" "$SOURCE" >> "$tmpfile"
    done

    # Compare with extract file
    if diff -q "$PROTOCOLS_DIR/$file" "$tmpfile" > /dev/null 2>&1; then
        echo "✓ $name: MATCH"
        PASS=$((PASS + 1))
    else
        echo "✗ $name: DIFFERS"
        echo "  Diff output:"
        diff "$PROTOCOLS_DIR/$file" "$tmpfile" 2>&1 | head -20 | sed 's/^/    /'
        FAIL=$((FAIL + 1))
    fi
}

# Single-range extracts
verify "pact-s5-policy.md" "S5 Policy (lines 13-147)" "13,147"
verify "pact-s4-checkpoints.md" "S4 Checkpoints (lines 148-219)" "148,219"
verify "pact-s4-environment.md" "S4 Environment (lines 220-293)" "220,293"
verify "pact-s4-tension.md" "S4 Tension (lines 294-358)" "294,358"
verify "pact-s1-autonomy.md" "S1 Autonomy (lines 481-555)" "481,555"
verify "pact-variety.md" "Variety (lines 599-660)" "599,660"

# Combined-range extracts
verify "pact-s2-coordination.md" "S2 Coordination (lines 359-480 + 799-813)" "359,480" "799,813"
verify "pact-workflows.md" "Workflows (lines 661-787)" "661,787"
verify "pact-phase-transitions.md" "Phase Transitions (lines 788-798 + 814-891)" "788,798" "814,891"
verify "pact-documentation.md" "Documentation (lines 892-916)" "892,916"

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
