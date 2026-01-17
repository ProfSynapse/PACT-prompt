#!/bin/bash
# S5 Credential Scan - Detect credentials in Write operations
# VSM Layer: S5 (Policy)
#
# Location: pact-plugin/hooks/s5-credential-scan.sh
# Purpose: PreToolUse hook that detects credentials before file writes
# Used by: hooks.json PreToolUse Write matcher

# Read file content from tool input
# Claude passes tool arguments in TOOL_INPUT environment variable
if [ -n "$TOOL_INPUT" ]; then
    content="$TOOL_INPUT"
else
    content=$(cat)
fi

# Exit early if no content
if [ -z "$content" ]; then
    exit 0
fi

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
if echo "$content" | grep -qE '\bsk-[a-zA-Z0-9]{20,}\b'; then
    alert_credential "OpenAI API key (sk-...)"
fi

# Stripe live keys (pk_live_, sk_live_)
if echo "$content" | grep -qE '\b(pk|sk)_live_[a-zA-Z0-9]{20,}\b'; then
    alert_credential "Stripe live API key"
fi

# AWS Access Key ID (AKIA...)
if echo "$content" | grep -qE '\bAKIA[A-Z0-9]{16}\b'; then
    alert_credential "AWS Access Key ID (AKIA...)"
fi

# Google API keys (AIza...)
if echo "$content" | grep -qE '\bAIza[a-zA-Z0-9_-]{35}\b'; then
    alert_credential "Google API key (AIza...)"
fi

# GitHub tokens (ghp_, gho_, ghu_, ghs_, ghr_)
if echo "$content" | grep -qE '\bgh[pousr]_[a-zA-Z0-9]{36,}\b'; then
    alert_credential "GitHub token"
fi

# Anthropic API keys (sk-ant-)
if echo "$content" | grep -qE '\bsk-ant-[a-zA-Z0-9_-]{40,}\b'; then
    alert_credential "Anthropic API key"
fi

# === PRIVATE KEYS ===

# RSA/DSA/EC/OPENSSH private keys
if echo "$content" | grep -qE -- '-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----'; then
    alert_credential "Private key"
fi

# PGP private key block
if echo "$content" | grep -qE -- '-----BEGIN PGP PRIVATE KEY BLOCK-----'; then
    alert_credential "PGP private key"
fi

# === HARDCODED PASSWORDS ===

# Common password assignment patterns
# password = "...", password: "...", passwd = "..."
if echo "$content" | grep -qiE '(password|passwd|pwd)\s*[:=]\s*["\x27][^"\x27]{4,}["\x27]'; then
    alert_credential "Hardcoded password"
fi

# Secret/API key assignments
if echo "$content" | grep -qiE '(api[_-]?key|api[_-]?secret|secret[_-]?key)\s*[:=]\s*["\x27][a-zA-Z0-9_-]{8,}["\x27]'; then
    alert_credential "Hardcoded API key/secret"
fi

# === CONNECTION STRINGS WITH CREDENTIALS ===

# Database connection strings with embedded passwords
# postgresql://user:password@host, mysql://user:password@host, mongodb://user:password@host
if echo "$content" | grep -qE '(postgresql|mysql|mongodb|redis|amqp)://[^:]+:[^@]+@[^/]+'; then
    alert_credential "Database connection string with embedded credentials"
fi

# === AWS CREDENTIALS ===

# AWS Secret Access Key (case-insensitive key name, 40-char value)
if echo "$content" | grep -qiE 'aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\x27]?[a-zA-Z0-9/+=]{40}["\x27]?'; then
    alert_credential "AWS Secret Access Key"
fi

# === AZURE/GCP CREDENTIALS ===

# Azure connection strings
if echo "$content" | grep -qE 'DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[a-zA-Z0-9+/=]{40,}'; then
    alert_credential "Azure Storage connection string"
fi

# GCP service account key files (JSON with private_key)
if echo "$content" | grep -qE '"type"\s*:\s*"service_account"' && echo "$content" | grep -qE '"private_key"\s*:'; then
    alert_credential "GCP service account key"
fi

# === JWT SECRETS ===

# JWT secret assignments
if echo "$content" | grep -qiE 'jwt[_-]?(secret|key)\s*[:=]\s*["\x27][^"\x27]{16,}["\x27]'; then
    alert_credential "JWT secret"
fi

# Content passed all checks
exit 0
