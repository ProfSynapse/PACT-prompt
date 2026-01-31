#!/bin/bash
# scripts/verify-completeness-signals.sh
# Verifies that the completeness protocol is canonical and that all command
# files reference it. The canonical signal list lives in
# pact-plugin/protocols/pact-completeness.md (single source of truth).

set -e

echo "=== Completeness Signal Verification ==="
echo ""

COMMANDS_DIR="pact-plugin/commands"
PROTOCOL_FILE="pact-plugin/protocols/pact-completeness.md"

if [ ! -d "$COMMANDS_DIR" ]; then
    echo "ERROR: Commands directory $COMMANDS_DIR not found"
    exit 1
fi

PASS=0
FAIL=0

# Helper: check that a file contains a keyword (case-insensitive grep)
# Args: file, check_name, keyword
check_keyword() {
    local file="$1"
    local name="$2"
    local keyword="$3"

    if [ ! -f "$file" ]; then
        echo "  ✗ $name: FILE NOT FOUND ($file)"
        FAIL=$((FAIL + 1))
        return
    fi

    if grep -qi "$keyword" "$file"; then
        echo "  ✓ $name"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $name: keyword not found: \"$keyword\""
        FAIL=$((FAIL + 1))
    fi
}

# Helper: check that a file contains ALL keywords from a list
# Args: file, check_name, keyword1, keyword2, ...
check_all_keywords() {
    local file="$1"
    local name="$2"
    shift 2
    local keywords=("$@")

    if [ ! -f "$file" ]; then
        echo "  ✗ $name: FILE NOT FOUND ($file)"
        FAIL=$((FAIL + 1))
        return
    fi

    local missing=()
    for kw in "${keywords[@]}"; do
        if ! grep -qi "$kw" "$file"; then
            missing+=("$kw")
        fi
    done

    if [ ${#missing[@]} -eq 0 ]; then
        echo "  ✓ $name: all ${#keywords[@]} keywords present"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $name: missing ${#missing[@]} of ${#keywords[@]} keywords:"
        for m in "${missing[@]}"; do
            echo "      - \"$m\""
        done
        FAIL=$((FAIL + 1))
    fi
}

# ---- Protocol file (canonical source of truth) ----
echo "pact-completeness.md (canonical protocol):"
check_keyword "$PROTOCOL_FILE" "Protocol file exists" \
    "Phase Skip Completeness"
check_all_keywords "$PROTOCOL_FILE" "All 6 canonical signals" \
    "unchecked" \
    "TBD" \
    "forward reference" \
    "unresolved question" \
    "stub" \
    "Phase Requirements"
check_keyword "$PROTOCOL_FILE" "Core principle present" \
    "Existence"
check_keyword "$PROTOCOL_FILE" "Backward compatibility clause" \
    "backward compatibility"
echo ""

# ---- orchestrate.md (links to protocol) ----
echo "orchestrate.md:"
check_keyword "$COMMANDS_DIR/orchestrate.md" "Phase Skip Completeness Check section" \
    "Phase Skip Completeness Check"
check_keyword "$COMMANDS_DIR/orchestrate.md" "Existence != Completeness principle" \
    "Existence"
check_keyword "$COMMANDS_DIR/orchestrate.md" "Links to completeness protocol" \
    "pact-completeness.md"
echo ""

# ---- rePACT.md ----
echo "rePACT.md:"
check_keyword "$COMMANDS_DIR/rePACT.md" "Phase Skip Completeness section" \
    "Phase Skip Completeness"
check_keyword "$COMMANDS_DIR/rePACT.md" "Links to completeness protocol" \
    "pact-completeness.md"
echo ""

# ---- imPACT.md ----
echo "imPACT.md:"
check_keyword "$COMMANDS_DIR/imPACT.md" "Completeness reference" \
    "completeness"
check_keyword "$COMMANDS_DIR/imPACT.md" "Links to completeness protocol" \
    "pact-completeness.md"
echo ""

# ---- comPACT.md ----
echo "comPACT.md:"
check_keyword "$COMMANDS_DIR/comPACT.md" "Completeness reference" \
    "completeness"
check_keyword "$COMMANDS_DIR/comPACT.md" "Links to completeness protocol" \
    "pact-completeness.md"
echo ""

# ---- plan-mode.md ----
echo "plan-mode.md:"
check_keyword "$COMMANDS_DIR/plan-mode.md" "Phase Requirements section template" \
    "Phase Requirements"
check_keyword "$COMMANDS_DIR/plan-mode.md" "Links to completeness protocol" \
    "pact-completeness.md"
check_keyword "$COMMANDS_DIR/plan-mode.md" "TBD convention comment" \
    "TBD"
check_keyword "$COMMANDS_DIR/plan-mode.md" "Unchecked items checking" \
    "unchecked"
echo ""

# ---- Meta-check: file list drift ----
# Ensures this script covers all workflow command files. If a new workflow
# command is added to pact-plugin/commands/, this check will catch it.
echo "Meta: command file coverage:"

# Workflow command files that this script explicitly checks above.
CHECKED_FILES=("orchestrate.md" "rePACT.md" "imPACT.md" "comPACT.md" "plan-mode.md")

# Utility commands that do NOT have phase-skip / completeness logic.
# If a new command is added, decide whether it belongs here or in CHECKED_FILES.
EXCLUDED_FILES=("peer-review.md" "pin-memory.md" "wrap-up.md")

# Build a combined list of known files for quick lookup
declare -A KNOWN_FILES
for f in "${CHECKED_FILES[@]}" "${EXCLUDED_FILES[@]}"; do
    KNOWN_FILES["$f"]=1
done

# Find all .md files in the commands directory and check for uncovered ones
UNCOVERED=()
for filepath in "$COMMANDS_DIR"/*.md; do
    filename="$(basename "$filepath")"
    if [ -z "${KNOWN_FILES[$filename]+x}" ]; then
        UNCOVERED+=("$filename")
    fi
done

if [ ${#UNCOVERED[@]} -eq 0 ]; then
    echo "  ✓ All command files accounted for (${#CHECKED_FILES[@]} checked, ${#EXCLUDED_FILES[@]} excluded)"
    PASS=$((PASS + 1))
else
    echo "  ✗ Uncovered command files found — add to CHECKED_FILES or EXCLUDED_FILES:"
    for f in "${UNCOVERED[@]}"; do
        echo "      - $f"
    done
    FAIL=$((FAIL + 1))
fi
echo ""

# ---- Summary ----
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
