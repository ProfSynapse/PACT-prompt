#!/bin/bash
# S5 Security Policy - Block dangerous Bash commands
# VSM Layer: S5 (Policy)
#
# Location: pact-plugin/hooks/s5-security-policy.sh
# Purpose: PreToolUse hook that blocks dangerous/destructive Bash commands
# Used by: hooks.json PreToolUse Bash matcher
#
# Known Limitations:
# - Pattern matching is static and cannot detect:
#   - Commands constructed via variable interpolation (e.g., cmd="git push"; $cmd --force)
#   - Commands split across lines in heredocs
#   - Commands executed through eval or indirect invocation
# - This provides defense-in-depth, not absolute prevention
# - Users with malicious intent can bypass these checks

# Read the command from tool input (passed via environment or stdin)
# Claude passes tool arguments in TOOL_INPUT environment variable
if [ -n "$TOOL_INPUT" ]; then
    command_text="$TOOL_INPUT"
else
    # Read stdin with timeout (5 seconds max) to prevent hanging
    command_text=$(timeout 5 cat 2>/dev/null || echo "")
fi

# Exit early if no command
if [ -z "$command_text" ]; then
    exit 0
fi

# Function to block with message
block_command() {
    local reason="$1"
    echo ""
    echo "=== S5 POLICY VIOLATION ==="
    echo ""
    echo "BLOCKED: $reason"
    echo ""
    echo "This command was blocked by S5 security policy."
    echo "If you believe this is a false positive, consult with the user."
    echo ""
    exit 1
}

# Normalize command for pattern matching (lowercase)
cmd_lower=$(echo "$command_text" | tr '[:upper:]' '[:lower:]')

# === DESTRUCTIVE FILE SYSTEM COMMANDS ===

# Block rm -rf on root or critical system directories
if echo "$command_text" | grep -qE 'rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|(-[a-zA-Z]*f[a-zA-Z]*r))\s+(/|/\*|/bin|/boot|/dev|/etc|/home|/lib|/opt|/root|/sbin|/sys|/tmp|/usr|/var)\b'; then
    block_command "Destructive rm command targeting system directories"
fi

# Block rm -rf with --no-preserve-root
if echo "$command_text" | grep -qE 'rm\s+.*--no-preserve-root'; then
    block_command "rm with --no-preserve-root is forbidden"
fi

# === DISK/DEVICE COMMANDS ===

# Block dd to system devices
# Covers: SATA/SCSI (sd*), IDE (hd*), NVMe, virtio (vd*), Xen (xvd*), SD/eMMC (mmcblk*), device mapper (dm-*), loop devices
if echo "$command_text" | grep -qE 'dd\s+.*of=\s*/dev/(sd[a-z]|hd[a-z]|nvme[0-9]*n[0-9]*|vd[a-z]|xvd[a-z]|mmcblk[0-9]*|dm-[0-9]+|loop[0-9]*)\b'; then
    block_command "dd to system device is forbidden"
fi

# Block mkfs commands (filesystem creation)
if echo "$command_text" | grep -qE '\bmkfs(\.[a-z0-9]+)?\s+'; then
    block_command "mkfs commands are forbidden - can destroy filesystems"
fi

# === FORK BOMB ===

# Block fork bomb pattern
if echo "$command_text" | grep -qE ':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:'; then
    block_command "Fork bomb detected"
fi

# === GIT FORCE PUSH TO PROTECTED BRANCHES ===

# Block force push to main/master
# Pattern 1: --force flag anywhere in push command targeting main/master
# Handles: git push --force origin main, git push origin main --force, git push origin --force main
if echo "$command_text" | grep -qE 'git\s+push\s+.*--force' && echo "$command_text" | grep -qE 'git\s+push\s+.*(main|master)\b'; then
    block_command "Force push to main/master is forbidden"
fi

# Pattern 2: -f short flag anywhere in push command targeting main/master
# Handles: git push -f origin main, git push origin main -f, git push origin -f main
if echo "$command_text" | grep -qE 'git\s+push\s+.*\s-f(\s|$)' && echo "$command_text" | grep -qE 'git\s+push\s+.*(main|master)\b'; then
    block_command "Force push to main/master is forbidden"
fi

# Block git push --force-with-lease to main/master (still dangerous)
# Handles: git push --force-with-lease origin main, git push origin main --force-with-lease
if echo "$command_text" | grep -qE 'git\s+push\s+.*--force-with-lease' && echo "$command_text" | grep -qE 'git\s+push\s+.*(main|master)\b'; then
    block_command "Force push (with-lease) to main/master is forbidden"
fi

# === DATABASE DESTRUCTIVE COMMANDS ===

# Block DROP DATABASE (case insensitive)
if echo "$cmd_lower" | grep -qE '\bdrop\s+database\b'; then
    block_command "DROP DATABASE command detected - potential data loss"
fi

# Block TRUNCATE TABLE without explicit confirmation pattern
if echo "$cmd_lower" | grep -qE '\btruncate\s+(table\s+)?[a-z_]+\b'; then
    block_command "TRUNCATE command detected - potential data loss"
fi

# === CHMOD/CHOWN RECURSIVE ON ROOT ===

# Block chmod -R on root
if echo "$command_text" | grep -qE 'chmod\s+(-[a-zA-Z]*R[a-zA-Z]*)\s+[0-9]+\s+/\s*$'; then
    block_command "Recursive chmod on root is forbidden"
fi

# Block chown -R on root
if echo "$command_text" | grep -qE 'chown\s+(-[a-zA-Z]*R[a-zA-Z]*)\s+\S+\s+/\s*$'; then
    block_command "Recursive chown on root is forbidden"
fi

# === WGET/CURL PIPED TO SHELL ===

# Block curl/wget piped directly to shell (common malware vector)
if echo "$command_text" | grep -qE '(curl|wget)\s+.*\|\s*(bash|sh|zsh)\b'; then
    block_command "Piping remote content directly to shell is risky"
fi

# Command passed all checks
exit 0
