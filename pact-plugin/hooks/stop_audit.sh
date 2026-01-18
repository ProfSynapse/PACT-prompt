#!/bin/bash
# PreToolUse hook: Lists uncommitted changes and nudges Claude

# Exit early if not in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    exit 0
fi

changes=$(git status --porcelain 2>/dev/null)

if [ -z "$changes" ]; then
    exit 0
fi

echo "=== PACT Audit ==="
echo ""
echo "Files changed this session:"
echo "$changes" | while IFS= read -r line; do
    file="${line:3}"
    echo "  • $file"
done
echo ""
echo "Consider:"
echo "  • Any cleanup or docs updates needed?"
echo "  • Ready to commit?"
echo ""
