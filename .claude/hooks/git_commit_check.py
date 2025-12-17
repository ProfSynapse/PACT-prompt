#!/usr/bin/env python3
import sys
import json
import subprocess
import re

def get_staged_files():
    """Returns a list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().splitlines()
    except subprocess.CalledProcessError:
        return []

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        tool_input = input_data.get("tool_input", {})
        command = tool_input.get("command", "")

        # Check if the command is a git commit
        # Matches: git commit, git commit -m "...", etc.
        if not re.search(r'\bgit\s+commit\b', command):
            sys.exit(0) # Not a commit command, allow it

        staged_files = get_staged_files()
        
        # If no files are staged, let git handle the error
        if not staged_files:
            sys.exit(0)

        has_code_changes = any(f.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.java', '.c', '.cpp', '.h', '.rs', '.go')) for f in staged_files)
        has_doc_changes = any(f.startswith('docs/') or f == 'CLAUDE.md' or f.endswith('.md') for f in staged_files)

        # Rule: If code changes, docs must change (or be present in the commit)
        if has_code_changes and not has_doc_changes:
            print("Error: PACT Protocol Violation", file=sys.stderr)
            print("------------------------------", file=sys.stderr)
            print("You are attempting to commit code changes without updating documentation.", file=sys.stderr)
            print("Please update 'docs/CHANGELOG.md', 'CLAUDE.md', or files in 'docs/' to reflect your changes.", file=sys.stderr)
            print("Run '/PACT:wrap-up' or manually update the docs before committing.", file=sys.stderr)
            sys.exit(2) # Block the tool execution

        sys.exit(0) # Allow the commit

    except Exception as e:
        # If something goes wrong in the hook, log it but don't block unless necessary
        print(f"Hook Error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
