#!/bin/bash
# S5 Credential Scan - Detect credentials in Write/Edit operations
# VSM Layer: S5 (Policy)
#
# Location: pact-plugin/hooks/s5-credential-scan.sh
# Purpose: PreToolUse hook that detects credentials before file writes/edits
# Used by: hooks.json PreToolUse Write and Edit matchers
#
# False Positive Mitigation:
# - Excludes docs/, test fixtures, and .md files
# - Skips credentials in comments or near example/mock indicators

# Read JSON input from stdin
# Format (Write): {"tool_name": "Write", "tool_input": {"file_path": "...", "content": "..."}}
# Format (Edit):  {"tool_name": "Edit", "tool_input": {"file_path": "...", "new_string": "..."}}
if [ -n "$TOOL_INPUT" ]; then
    json_input="$TOOL_INPUT"
else
    json_input=$(cat)
fi

# Exit early if no input
if [ -z "$json_input" ]; then
    exit 0
fi

# Extract file_path and content from JSON
# Use python3 for reliable JSON parsing (available on macOS/Linux)
file_path=$(echo "$json_input" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('tool_input', {}).get('file_path', ''))" 2>/dev/null)
content=$(echo "$json_input" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('tool_input', {}).get('content', '') or data.get('tool_input', {}).get('new_string', ''))" 2>/dev/null)

# Fallback: if JSON parsing failed, treat entire input as content (backward compatibility)
if [ -z "$content" ] && [ -n "$json_input" ]; then
    content="$json_input"
    file_path=""
fi

# Exit early if no content
if [ -z "$content" ]; then
    exit 0
fi

# === PATH EXCLUSIONS (False Positive Mitigation) ===
# Skip scanning for documentation, test fixtures, and markdown files

should_skip_path() {
    local path="$1"

    # Skip if no path provided
    [ -z "$path" ] && return 1

    # Skip docs/ directory
    if [[ "$path" == */docs/* ]] || [[ "$path" == docs/* ]]; then
        return 0
    fi

    # Skip test fixture directories
    if [[ "$path" == */test/fixtures/* ]] || [[ "$path" == */tests/fixtures/* ]] || [[ "$path" == */__tests__/fixtures/* ]]; then
        return 0
    fi

    # Skip markdown files
    if [[ "$path" == *.md ]]; then
        return 0
    fi

    return 1
}

# Check path exclusions
if should_skip_path "$file_path"; then
    exit 0
fi

# === EXAMPLE/MOCK CREDENTIAL DETECTION (False Positive Mitigation) ===
# Check if a line appears to be an example or is in a comment

is_example_or_comment() {
    local line="$1"

    # Check if line is a comment (common comment prefixes)
    # Trim leading whitespace for comment detection
    local trimmed
    trimmed=$(echo "$line" | sed 's/^[[:space:]]*//')

    # Shell/Python/YAML comments
    if [[ "$trimmed" == \#* ]]; then
        return 0
    fi

    # JavaScript/TypeScript/C/Java comments
    if [[ "$trimmed" == //* ]] || [[ "$trimmed" == \** ]]; then
        return 0
    fi

    # HTML/XML comments
    if [[ "$trimmed" == \<\!--* ]]; then
        return 0
    fi

    # Check for example/mock/placeholder indicators (case-insensitive)
    local lower_line
    lower_line=$(echo "$line" | tr '[:upper:]' '[:lower:]')

    if [[ "$lower_line" == *"example"* ]] || \
       [[ "$lower_line" == *"fake"* ]] || \
       [[ "$lower_line" == *"mock"* ]] || \
       [[ "$lower_line" == *"test"* ]] || \
       [[ "$lower_line" == *"placeholder"* ]] || \
       [[ "$lower_line" == *"dummy"* ]] || \
       [[ "$lower_line" == *"sample"* ]] || \
       [[ "$lower_line" == *"your-"* ]] || \
       [[ "$lower_line" == *"your_"* ]] || \
       [[ "$lower_line" == *"xxx"* ]] || \
       [[ "$lower_line" == *"replace"* ]]; then
        return 0
    fi

    return 1
}

# Check content for a pattern, excluding examples and comments
# Returns 0 (true) if a REAL credential is found, 1 otherwise
check_credential_pattern() {
    local pattern="$1"
    local case_flag="${2:--E}"  # Default to -E (extended regex), can pass -iE for case-insensitive

    # Get all matching lines
    local matches
    matches=$(echo "$content" | grep $case_flag "$pattern" 2>/dev/null)

    # If no matches, return false (no credential found)
    [ -z "$matches" ] && return 1

    # Check each matching line - if ANY is not an example/comment, it's a real credential
    while IFS= read -r line; do
        if ! is_example_or_comment "$line"; then
            return 0  # Found a real credential
        fi
    done <<< "$matches"

    return 1  # All matches were examples or comments
}

# Function to alert on credential detection
alert_credential() {
    local credential_type="$1"
    echo ""
    echo "=== S5 CREDENTIAL DETECTED ==="
    echo ""
    echo "WARNING: $credential_type found in file content"
    echo ""
    echo "Writing credentials to files violates S5 security policy."
    echo "Use environment variables or secret management instead."
    echo ""
    echo "If this is a false positive (e.g., documentation example),"
    echo "consult with the user before proceeding."
    echo ""
    exit 1
}

# === API KEY PATTERNS ===

# OpenAI API keys (sk-...)
if check_credential_pattern '\bsk-[a-zA-Z0-9]{20,}\b'; then
    alert_credential "OpenAI API key (sk-...)"
fi

# Stripe live keys (pk_live_, sk_live_)
if check_credential_pattern '\b(pk|sk)_live_[a-zA-Z0-9]{20,}\b'; then
    alert_credential "Stripe live API key"
fi

# AWS Access Key ID (AKIA...)
if check_credential_pattern '\bAKIA[A-Z0-9]{16}\b'; then
    alert_credential "AWS Access Key ID (AKIA...)"
fi

# Google API keys (AIza...)
if check_credential_pattern '\bAIza[a-zA-Z0-9_-]{35}\b'; then
    alert_credential "Google API key (AIza...)"
fi

# GitHub tokens (ghp_, gho_, ghu_, ghs_, ghr_)
if check_credential_pattern '\bgh[pousr]_[a-zA-Z0-9]{36,}\b'; then
    alert_credential "GitHub token"
fi

# Anthropic API keys (sk-ant-)
if check_credential_pattern '\bsk-ant-[a-zA-Z0-9_-]{40,}\b'; then
    alert_credential "Anthropic API key"
fi

# === PRIVATE KEYS ===

# RSA/DSA/EC/OPENSSH private keys
if check_credential_pattern '-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----'; then
    alert_credential "Private key"
fi

# PGP private key block
if check_credential_pattern '-----BEGIN PGP PRIVATE KEY BLOCK-----'; then
    alert_credential "PGP private key"
fi

# === HARDCODED PASSWORDS ===

# Common password assignment patterns
# password = "...", password: "...", passwd = "..."
if check_credential_pattern '(password|passwd|pwd)\s*[:=]\s*["\x27][^"\x27]{4,}["\x27]' '-iE'; then
    alert_credential "Hardcoded password"
fi

# Secret/API key assignments
if check_credential_pattern '(api[_-]?key|api[_-]?secret|secret[_-]?key)\s*[:=]\s*["\x27][a-zA-Z0-9_-]{8,}["\x27]' '-iE'; then
    alert_credential "Hardcoded API key/secret"
fi

# === CONNECTION STRINGS WITH CREDENTIALS ===

# Database connection strings with embedded passwords
# postgresql://user:password@host, mysql://user:password@host, mongodb://user:password@host
if check_credential_pattern '(postgresql|mysql|mongodb|redis|amqp)://[^:]+:[^@]+@[^/]+'; then
    alert_credential "Database connection string with embedded credentials"
fi

# === AWS CREDENTIALS ===

# AWS Secret Access Key (case-insensitive key name, 40-char value)
if check_credential_pattern 'aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\x27]?[a-zA-Z0-9/+=]{40}["\x27]?' '-iE'; then
    alert_credential "AWS Secret Access Key"
fi

# === AZURE/GCP CREDENTIALS ===

# Azure connection strings
if check_credential_pattern 'DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[a-zA-Z0-9+/=]{40,}'; then
    alert_credential "Azure Storage connection string"
fi

# GCP service account key files (JSON with private_key)
# Note: GCP check uses two patterns - both must match, context checked on private_key line
if echo "$content" | grep -qE '"type"\s*:\s*"service_account"' && check_credential_pattern '"private_key"\s*:'; then
    alert_credential "GCP service account key"
fi

# === JWT SECRETS ===

# JWT secret assignments
if check_credential_pattern 'jwt[_-]?(secret|key)\s*[:=]\s*["\x27][^"\x27]{16,}["\x27]' '-iE'; then
    alert_credential "JWT secret"
fi

# Content passed all checks
exit 0
