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

def get_staged_file_content(filename):
    """Returns the content of a staged file."""
    try:
        result = subprocess.run(
            ["git", "show", f":{filename}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""

def check_security(staged_files):
    errors = []
    
    # 1. Check for .env files
    for f in staged_files:
        if f.endswith('.env') or '/.env' in f:
            errors.append(f"SECURITY: Attempting to commit environment file: {f}")

    # 2. Check for sensitive logs
    risky_patterns = [
        r'console\.log\s*\(.*process\.env',
        r'print\s*\(.*os\.environ',
        r'console\.log\s*\(.*password',
        r'print\s*\(.*password',
        r'console\.log\s*\(.*secret',
        r'print\s*\(.*secret',
        r'console\.log\s*\(.*key',
        r'print\s*\(.*key',
        r'console\.log\s*\(.*token',
        r'print\s*\(.*token',
    ]
    
    for f in staged_files:
        if f.endswith(('.js', '.ts', '.jsx', '.tsx', '.py')):
            content = get_staged_file_content(f)
            for pattern in risky_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    errors.append(f"SECURITY: Potential secret exposure in log in {f}: matches pattern '{pattern}'")
    
    return errors

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

        # --- Security Check ---
        security_errors = check_security(staged_files)
        if security_errors:
            print("Error: PACT Security Violation", file=sys.stderr)
            print("------------------------------", file=sys.stderr)
            for err in security_errors:
                print(f"• {err}", file=sys.stderr)
            print("------------------------------", file=sys.stderr)
            print("Please remove sensitive files or logs before committing.", file=sys.stderr)
            sys.exit(2) # Block the tool execution

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
