#!/bin/bash
# scripts/verify-completeness-signals.sh
# Verifies that incompleteness signal lists stay consistent across all
# command files that reference them. The canonical list lives in
# orchestrate.md's "Phase Skip Completeness Check" section.

set -e

echo "=== Completeness Signal Verification ==="
echo ""

COMMANDS_DIR="pact-plugin/commands"

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

    local filepath="$COMMANDS_DIR/$file"

    if [ ! -f "$filepath" ]; then
        echo "  ✗ $name: FILE NOT FOUND ($filepath)"
        FAIL=$((FAIL + 1))
        return
    fi

    if grep -qi "$keyword" "$filepath"; then
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

    local filepath="$COMMANDS_DIR/$file"

    if [ ! -f "$filepath" ]; then
        echo "  ✗ $name: FILE NOT FOUND ($filepath)"
        FAIL=$((FAIL + 1))
        return
    fi

    local missing=()
    for kw in "${keywords[@]}"; do
        if ! grep -qi "$kw" "$filepath"; then
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

# ---- orchestrate.md (canonical signal list) ----
echo "orchestrate.md (canonical):"
check_all_keywords "orchestrate.md" "Canonical signal list" \
    "unchecked" \
    "TBD" \
    "forward reference" \
    "unresolved question" \
    "stub" \
    "Phase Requirements"
check_keyword "orchestrate.md" "Phase Skip Completeness Check section" \
    "Phase Skip Completeness Check"
check_keyword "orchestrate.md" "Existence != Completeness principle" \
    "Existence"
echo ""

# ---- rePACT.md ----
echo "rePACT.md:"
check_all_keywords "rePACT.md" "Core signal keywords" \
    "unchecked" \
    "TBD" \
    "forward reference" \
    "unresolved" \
    "Phase Requirements"
check_keyword "rePACT.md" "Existence != Completeness principle" \
    "Existence"
echo ""

# ---- imPACT.md ----
echo "imPACT.md:"
check_all_keywords "imPACT.md" "Core signal keywords" \
    "unchecked" \
    "TBD" \
    "handled during" \
    "stub" \
    "unresolved" \
    "Phase Requirements"
check_keyword "imPACT.md" "Completeness signals section" \
    "Completeness signals"
echo ""

# ---- comPACT.md ----
echo "comPACT.md:"
check_all_keywords "comPACT.md" "Inline signal references" \
    "unchecked" \
    "TBD" \
    "handled during"
echo ""

# ---- plan-mode.md ----
echo "plan-mode.md:"
check_keyword "plan-mode.md" "Phase Requirements section template" \
    "Phase Requirements"
check_keyword "plan-mode.md" "TBD convention comment" \
    "TBD"
check_keyword "plan-mode.md" "Forward reference checking" \
    "forward reference"
check_keyword "plan-mode.md" "Unchecked items checking" \
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
