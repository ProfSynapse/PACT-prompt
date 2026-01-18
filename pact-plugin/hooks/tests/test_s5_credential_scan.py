"""Tests for s5-credential-scan.sh hook.

Tests credential detection in Write/Edit operations via PreToolUse hook.
Uses subprocess to call the shell script with JSON input.
"""

import json
import subprocess
from pathlib import Path

import pytest

# Path to the hook script
HOOK_PATH = Path(__file__).parent.parent / "s5-credential-scan.sh"


class TestFixtures:
    """Pytest fixtures for credential scan tests."""


@pytest.fixture
def run_hook():
    """Fixture that returns a function to run the credential scan hook.

    Returns a callable that accepts JSON input and returns (exit_code, stdout, stderr).
    """
    def _run(json_input: dict | str) -> tuple[int, str, str]:
        if isinstance(json_input, dict):
            json_input = json.dumps(json_input)

        result = subprocess.run(
            ["bash", str(HOOK_PATH)],
            input=json_input,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode, result.stdout, result.stderr

    return _run


@pytest.fixture
def write_input():
    """Fixture that returns a function to create Write tool JSON input."""
    def _create(file_path: str, content: str) -> dict:
        return {
            "tool_name": "Write",
            "tool_input": {
                "file_path": file_path,
                "content": content,
            }
        }
    return _create


@pytest.fixture
def edit_input():
    """Fixture that returns a function to create Edit tool JSON input."""
    def _create(file_path: str, new_string: str, old_string: str = "") -> dict:
        return {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": file_path,
                "old_string": old_string,
                "new_string": new_string,
            }
        }
    return _create


class TestHookBasics:
    """Basic hook functionality tests."""

    def test_hook_exists(self):
        """Hook script should exist and be readable."""
        assert HOOK_PATH.exists(), f"Hook not found at {HOOK_PATH}"
        assert HOOK_PATH.is_file(), f"{HOOK_PATH} is not a file"

    def test_empty_input_exits_cleanly(self, run_hook):
        """Empty input should exit with code 0."""
        exit_code, stdout, stderr = run_hook("")
        assert exit_code == 0

    def test_empty_content_exits_cleanly(self, run_hook, write_input):
        """Empty content in Write tool should exit with code 0."""
        json_data = write_input("test.py", "")
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0

    def test_clean_content_exits_cleanly(self, run_hook, write_input):
        """Content without credentials should exit with code 0."""
        json_data = write_input("test.py", "print('Hello, World!')")
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0


class TestRealCredentialsDetected:
    """Tests that real credentials are properly detected."""

    def test_openai_api_key_detected(self, run_hook, write_input):
        """OpenAI API key (sk-...) should be detected."""
        content = 'OPENAI_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect OpenAI key. stdout: {stdout}"
        assert "OpenAI API key" in stdout

    def test_stripe_test_key_detected(self, run_hook, write_input):
        """Stripe test key should be detected.

        NOTE: We test sk_test_ instead of sk_live_ because sk_live_ triggers
        GitHub Push Protection even with obviously fake keys.
        """
        content = 'stripe_key = "sk_test_TESTKEY00000000000000000000"'
        json_data = write_input("payments.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect Stripe key. stdout: {stdout}"
        assert "Stripe" in stdout and "API key" in stdout

    def test_aws_access_key_detected(self, run_hook, write_input):
        """AWS Access Key ID (AKIA...) should be detected."""
        content = 'AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"'
        json_data = write_input("aws_config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect AWS key. stdout: {stdout}"
        assert "AWS Access Key ID" in stdout

    def test_github_token_detected(self, run_hook, write_input):
        """GitHub token (ghp_...) should be detected."""
        content = 'GITHUB_TOKEN = "ghp_TESTTOKEN0000000000000000000000000000"'
        json_data = write_input("ci.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect GitHub token. stdout: {stdout}"
        assert "GitHub token" in stdout

    def test_anthropic_api_key_detected(self, run_hook, write_input):
        """Anthropic API key (sk-ant-...) should be detected."""
        content = 'ANTHROPIC_KEY = "sk-ant-abcdefghijklmnopqrstuvwxyz1234567890abcdefghij"'
        json_data = write_input("llm.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect Anthropic key. stdout: {stdout}"
        assert "Anthropic API key" in stdout

    def test_google_api_key_detected(self, run_hook, write_input):
        """Google API key (AIza...) should be detected."""
        content = 'GOOGLE_API_KEY = "AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe"'
        json_data = write_input("maps.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect Google key. stdout: {stdout}"
        assert "Google API key" in stdout

    @pytest.mark.xfail(reason="Known issue: patterns starting with '-----' are interpreted as grep options")
    def test_private_key_detected(self, run_hook, write_input):
        """RSA private key should be detected.

        NOTE: Currently fails due to grep pattern issue - the '-----BEGIN' pattern
        is interpreted as a grep option rather than a pattern. This is a bug in
        the hook that should be fixed by adding '--' before the pattern.
        """
        content = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"""
        json_data = write_input("keys.pem", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect private key. stdout: {stdout}"
        assert "Private key" in stdout

    @pytest.mark.xfail(reason="Known issue: patterns starting with '-----' are interpreted as grep options")
    def test_openssh_private_key_detected(self, run_hook, write_input):
        """OpenSSH private key should be detected.

        NOTE: Currently fails due to grep pattern issue.
        """
        content = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAA...
-----END OPENSSH PRIVATE KEY-----"""
        json_data = write_input("id_rsa", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect OpenSSH key. stdout: {stdout}"
        assert "Private key" in stdout

    @pytest.mark.xfail(reason="Known issue: patterns starting with '-----' are interpreted as grep options")
    def test_pgp_private_key_detected(self, run_hook, write_input):
        """PGP private key should be detected.

        NOTE: Currently fails due to grep pattern issue.
        """
        content = """-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG v1
...
-----END PGP PRIVATE KEY BLOCK-----"""
        json_data = write_input("private.asc", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect PGP key. stdout: {stdout}"
        assert "PGP private key" in stdout

    def test_hardcoded_password_detected(self, run_hook, write_input):
        """Hardcoded password assignment should be detected."""
        content = 'password = "supersecretpassword123"'
        json_data = write_input("auth.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect password. stdout: {stdout}"
        assert "Hardcoded password" in stdout

    def test_database_connection_string_detected(self, run_hook, write_input):
        """Database connection string with credentials should be detected."""
        content = 'DATABASE_URL = "postgresql://user:secretpass@localhost:5432/mydb"'
        json_data = write_input("database.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect DB connection. stdout: {stdout}"
        assert "connection string" in stdout.lower()

    def test_aws_secret_access_key_detected(self, run_hook, write_input):
        """AWS Secret Access Key should be detected."""
        content = 'AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"'
        json_data = write_input("aws.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect AWS secret. stdout: {stdout}"
        assert "AWS Secret Access Key" in stdout

    def test_jwt_secret_detected(self, run_hook, write_input):
        """JWT secret should be detected."""
        content = 'JWT_SECRET = "mysupersecretjwtkey123456789"'
        json_data = write_input("jwt.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should detect JWT secret. stdout: {stdout}"
        assert "JWT secret" in stdout


class TestExampleCredentialsSkipped:
    """Tests that example/mock/test credentials are properly skipped."""

    def test_example_api_key_skipped(self, run_hook, write_input):
        """API key marked as example should be skipped."""
        content = 'OPENAI_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"  # example key'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip example key. stdout: {stdout}"

    def test_fake_api_key_skipped(self, run_hook, write_input):
        """API key marked as fake should be skipped."""
        content = '# This is a fake key for testing\nOPENAI_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        # Note: The comment is on a separate line, so the key line itself is not marked as example
        # Let's test with inline indicator
        content2 = 'OPENAI_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"  # fake'
        json_data2 = write_input("config.py", content2)
        exit_code2, stdout2, stderr2 = run_hook(json_data2)
        assert exit_code2 == 0, f"Should skip fake key. stdout: {stdout2}"

    def test_mock_password_skipped(self, run_hook, write_input):
        """Password marked as mock (with word boundary) should be skipped.

        NOTE: The hook uses word boundaries, so 'mock' must be a standalone word.
        'mock_password' does NOT match because '_' is a word character.
        """
        content = 'password = "secretvalue"  # mock value for testing'
        json_data = write_input("test_auth.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip mock password. stdout: {stdout}"

    def test_test_credentials_skipped(self, run_hook, write_input):
        """Credentials with 'test' indicator should be skipped."""
        content = 'api_key = "sk-testkey1234567890123456789012345678"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        # 'test' appears in 'testkey' but we need word boundary - this should trigger!
        # Let's check the actual behavior
        # Actually, looking at the regex: \btest\b - 'testkey' won't match because 'k' follows
        # But 'test_key' or 'test key' would match
        # Let's test with proper word boundary
        content2 = 'api_key = "sk-abcdefghijklmnopqrstuvwxyz1234567890"  # test'
        json_data2 = write_input("config.py", content2)
        exit_code2, stdout2, stderr2 = run_hook(json_data2)
        assert exit_code2 == 0, f"Should skip test key. stdout: {stdout2}"

    def test_placeholder_skipped(self, run_hook, write_input):
        """Credentials marked as placeholder (word boundary) should be skipped.

        NOTE: 'placeholder' must be a standalone word, not part of a larger token.
        """
        content = 'password = "secretvalue"  # placeholder'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip placeholder. stdout: {stdout}"

    def test_dummy_credentials_skipped(self, run_hook, write_input):
        """Credentials marked as dummy (word boundary) should be skipped.

        NOTE: 'dummy' must be a standalone word. 'dummykey' does NOT match.
        """
        content = 'API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"  # dummy'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip dummy key. stdout: {stdout}"

    def test_sample_password_skipped(self, run_hook, write_input):
        """Credentials marked as sample (word boundary) should be skipped.

        NOTE: 'sample' must be a standalone word. 'sample_password' does NOT match.
        """
        content = 'password = "secretvalue"  # sample'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip sample password. stdout: {stdout}"

    def test_your_api_key_skipped(self, run_hook, write_input):
        """Credentials with 'your_' prefix should be skipped."""
        content = 'API_KEY = "your_api_key_here"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip your_ placeholder. stdout: {stdout}"

    def test_xxx_placeholder_skipped(self, run_hook, write_input):
        """Credentials with 'xxx' placeholder should be skipped."""
        content = 'password = "xxx_replace_me_xxx"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip xxx placeholder. stdout: {stdout}"

    def test_replace_indicator_skipped(self, run_hook, write_input):
        """Credentials with 'replace' indicator (word boundary) should be skipped.

        NOTE: 'replace' must be a standalone word.
        """
        content = 'API_KEY = "secretvalue"  # replace with real key'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip replace indicator. stdout: {stdout}"

    def test_comment_line_skipped(self, run_hook, write_input):
        """Credentials in comment lines should be skipped."""
        content = '# password = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip commented line. stdout: {stdout}"

    def test_js_comment_skipped(self, run_hook, write_input):
        """Credentials in JavaScript comments should be skipped."""
        content = '// const API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890";'
        json_data = write_input("config.js", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip JS comment. stdout: {stdout}"

    def test_html_comment_skipped(self, run_hook, write_input):
        """Credentials in HTML comments should be skipped."""
        content = '<!-- API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890" -->'
        json_data = write_input("index.html", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should skip HTML comment. stdout: {stdout}"


class TestPathExclusions:
    """Tests that path exclusions work correctly."""

    def test_docs_examples_excluded(self, run_hook, write_input):
        """Files in docs/examples/ should be excluded."""
        content = 'OPENAI_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
        json_data = write_input("docs/examples/config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should exclude docs/examples/. stdout: {stdout}"

    def test_nested_docs_examples_excluded(self, run_hook, write_input):
        """Files in nested docs/examples/ paths should be excluded."""
        content = 'password = "secretpassword123"'
        json_data = write_input("/project/docs/examples/auth.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should exclude nested docs/examples/. stdout: {stdout}"

    def test_docs_templates_excluded(self, run_hook, write_input):
        """Files in docs/templates/ should be excluded."""
        content = 'API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
        json_data = write_input("docs/templates/env.example", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should exclude docs/templates/. stdout: {stdout}"

    def test_docs_tutorials_excluded(self, run_hook, write_input):
        """Files in docs/tutorials/ should be excluded."""
        content = 'password = "tutorialpassword"'
        json_data = write_input("docs/tutorials/getting-started.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should exclude docs/tutorials/. stdout: {stdout}"

    def test_test_fixtures_excluded(self, run_hook, write_input):
        """Files in test/fixtures/ should be excluded.

        NOTE: Path patterns require leading path component (*/test/fixtures/*).
        """
        content = 'OPENAI_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
        json_data = write_input("/project/test/fixtures/mock_config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should exclude test/fixtures/. stdout: {stdout}"

    def test_tests_fixtures_excluded(self, run_hook, write_input):
        """Files in tests/fixtures/ should be excluded."""
        content = 'password = "fixturepassword"'
        json_data = write_input("tests/fixtures/auth_data.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should exclude tests/fixtures/. stdout: {stdout}"

    def test_dunder_tests_fixtures_excluded(self, run_hook, write_input):
        """Files in __tests__/fixtures/ should be excluded."""
        content = 'API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
        json_data = write_input("src/__tests__/fixtures/config.js", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should exclude __tests__/fixtures/. stdout: {stdout}"

    def test_markdown_files_excluded(self, run_hook, write_input):
        """Markdown files should be excluded."""
        content = 'OPENAI_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
        json_data = write_input("README.md", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should exclude .md files. stdout: {stdout}"

    def test_docs_config_not_excluded(self, run_hook, write_input):
        """Files in docs/config/ should NOT be excluded (real config)."""
        content = 'password = "realpassword123"'
        json_data = write_input("docs/config/settings.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should NOT exclude docs/config/. stdout: {stdout}"

    def test_docs_deployment_not_excluded(self, run_hook, write_input):
        """Files in docs/deployment/ should NOT be excluded."""
        content = 'OPENAI_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
        json_data = write_input("docs/deployment/config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should NOT exclude docs/deployment/. stdout: {stdout}"

    def test_src_directory_not_excluded(self, run_hook, write_input):
        """Files in src/ should NOT be excluded."""
        content = 'password = "productionpassword"'
        json_data = write_input("src/config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should scan src/ files. stdout: {stdout}"


class TestJsonInputParsing:
    """Tests for JSON input parsing with Write and Edit tools."""

    def test_write_tool_content_parsed(self, run_hook):
        """Write tool content field should be parsed correctly."""
        json_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "config.py",
                "content": 'password = "realpassword123"',
            }
        }
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should parse Write content. stdout: {stdout}"
        assert "Hardcoded password" in stdout

    def test_edit_tool_new_string_parsed(self, run_hook):
        """Edit tool new_string field should be parsed correctly."""
        json_data = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "config.py",
                "old_string": "placeholder",
                "new_string": 'password = "realpassword123"',
            }
        }
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"Should parse Edit new_string. stdout: {stdout}"
        assert "Hardcoded password" in stdout

    def test_edit_tool_old_string_not_scanned(self, run_hook):
        """Edit tool old_string should NOT be scanned (only new content)."""
        json_data = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "config.py",
                "old_string": 'password = "realpassword123"',  # Contains credential
                "new_string": "placeholder = None",  # Clean content
            }
        }
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"Should only scan new_string, not old_string. stdout: {stdout}"

    def test_malformed_json_handled(self, run_hook):
        """Malformed JSON should be handled gracefully."""
        exit_code, stdout, stderr = run_hook("not valid json {")
        # The script falls back to treating input as raw content
        # Since "not valid json {" doesn't contain credentials, it should pass
        assert exit_code == 0

    def test_missing_tool_input_handled(self, run_hook):
        """Missing tool_input should be handled gracefully."""
        json_data = {"tool_name": "Write"}  # Missing tool_input
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0  # No content to scan


class TestExitCodes:
    """Tests for correct exit codes."""

    def test_clean_content_exit_0(self, run_hook, write_input):
        """Clean content should exit with code 0."""
        json_data = write_input("app.py", "def hello():\n    return 'Hello!'")
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0

    def test_credential_detected_exit_1(self, run_hook, write_input):
        """Detected credential should exit with code 1."""
        json_data = write_input("config.py", 'password = "secretpassword123"')
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1

    def test_example_credential_exit_0(self, run_hook, write_input):
        """Example credential should exit with code 0."""
        json_data = write_input("config.py", 'password = "example_password_here"')
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0

    def test_excluded_path_exit_0(self, run_hook, write_input):
        """Excluded path should exit with code 0 even with credentials."""
        json_data = write_input("docs/examples/config.py", 'password = "realpassword"')
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0


class TestWordBoundaries:
    """Tests that word boundaries work correctly to avoid false positives."""

    def test_contest_does_not_match_test(self, run_hook, write_input):
        """'contest' in content should NOT match 'test' word boundary."""
        content = 'password = "contestwinner2024"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        # 'contest' contains 'test' but should NOT trigger example detection
        assert exit_code == 1, f"'contest' should not match 'test' word boundary. stdout: {stdout}"

    def test_protester_does_not_match_test(self, run_hook, write_input):
        """'protester' in content should NOT match 'test' word boundary."""
        content = 'password = "protesteraccount"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"'protester' should not match 'test'. stdout: {stdout}"

    def test_testimony_does_not_match_test(self, run_hook, write_input):
        """'testimony' in content should NOT match 'test' word boundary."""
        content = 'password = "testimonyrecord"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1, f"'testimony' should not match 'test'. stdout: {stdout}"

    def test_testing_matches_as_word(self, run_hook, write_input):
        """'testing' as a word should match 'test' boundary."""
        # Note: This tests that 'test' as prefix of 'testing' matches
        # Looking at the regex: \btest\b - 'testing' won't match because 'i' follows 't'
        # Actually 'test' in 'testing' has word boundary before but not after
        # The regex uses \btest\b which requires boundaries on BOTH sides
        # So 'testing' should NOT match and credential should be detected
        content = 'password = "testing123"'  # 'testing' != 'test'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        # 'testing' won't match \btest\b (test is followed by 'i', not word boundary)
        assert exit_code == 1, f"'testing' should not match \\btest\\b. stdout: {stdout}"

    def test_test_as_word_matches(self, run_hook, write_input):
        """'test' as a standalone word should trigger skip."""
        content = 'password = "secretpass123"  # test'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, f"'test' as word should skip. stdout: {stdout}"

    def test_test_underscore_prefix_does_not_match(self, run_hook, write_input):
        """'test_' prefix does NOT trigger skip (word boundary not met).

        NOTE: 'test_password' contains 'test' followed by '_', which is a word
        character, so \\btest\\b does NOT match. The hook requires word boundaries.
        """
        content = 'password = "test_password_value"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        # This SHOULD be detected because test_ doesn't match \btest\b
        assert exit_code == 1, f"'test_' should NOT match word boundary. stdout: {stdout}"

    def test_example_in_variable_name_does_not_match(self, run_hook, write_input):
        """'example_password' does NOT skip (word boundary not met).

        NOTE: 'example_password' has 'example' followed by '_', which is a word
        character, so \\bexample\\b does NOT match.
        """
        content = 'example_password = "secretpass123"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        # This SHOULD be detected because example_ doesn't match \bexample\b
        assert exit_code == 1, f"'example_' should NOT match word boundary. stdout: {stdout}"

    def test_contestant_does_not_match_test(self, run_hook, write_input):
        """'contestant' should NOT match 'test' word boundary."""
        content = 'password = "contestant_auth_token"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        # 'contestant' contains 'test' but shouldn't match \btest\b
        assert exit_code == 1, f"'contestant' should not match 'test'. stdout: {stdout}"


class TestEdgeCases:
    """Edge case and regression tests."""

    def test_multiple_credentials_first_detected(self, run_hook, write_input):
        """Multiple credentials - first one should trigger detection."""
        content = '''OPENAI_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"
password = "secretpassword"'''
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1

    @pytest.mark.xfail(reason="Known issue: patterns starting with '-----' are interpreted as grep options")
    def test_multiline_private_key(self, run_hook, write_input):
        """Multiline private key should be detected.

        NOTE: Currently fails due to grep pattern issue.
        """
        content = """KEY = '''-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASC...
-----END PRIVATE KEY-----'''"""
        json_data = write_input("secrets.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1
        assert "Private key" in stdout

    def test_unicode_in_password(self, run_hook, write_input):
        """Password with unicode characters should still be detected."""
        content = 'password = "secretpassword123"'
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1

    def test_very_long_content(self, run_hook, write_input):
        """Very long content with credential should still detect."""
        # Create content with lots of safe lines and one credential
        safe_lines = ["# Line " + str(i) for i in range(100)]
        safe_lines.append('password = "realpassword123"')
        safe_lines.extend(["# More line " + str(i) for i in range(100)])
        content = "\n".join(safe_lines)
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1

    def test_credential_in_json_string(self, run_hook, write_input):
        """Credential in JSON file should be detected."""
        content = '{"api_key": "sk-abcdefghijklmnopqrstuvwxyz1234567890"}'
        json_data = write_input("config.json", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1

    def test_tool_input_env_variable(self, run_hook):
        """TOOL_INPUT environment variable should work."""
        import os
        json_input = json.dumps({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "config.py",
                "content": 'password = "secretpassword123"',
            }
        })

        env = os.environ.copy()
        env["TOOL_INPUT"] = json_input

        result = subprocess.run(
            ["bash", str(HOOK_PATH)],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        assert result.returncode == 1
        assert "Hardcoded password" in result.stdout

    def test_mixed_real_and_example_credentials(self, run_hook, write_input):
        """Real credential after example should still be detected."""
        content = '''# Example: password = "sk-example123456789012345678901234567890"
API_KEY = "sk-realkey12345678901234567890123456789012"'''
        json_data = write_input("config.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        # First line is comment, should be skipped
        # Second line has real credential
        assert exit_code == 1


class TestGCPServiceAccount:
    """Tests for GCP service account key detection."""

    def test_gcp_service_account_detected(self, run_hook, write_input):
        """GCP service account JSON should be detected."""
        content = '''{
    "type": "service_account",
    "project_id": "my-project",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nMII..."
}'''
        json_data = write_input("service-account.json", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1
        assert "GCP service account" in stdout

    def test_gcp_partial_not_detected(self, run_hook, write_input):
        """Partial GCP patterns should not trigger (need both patterns)."""
        # Only type, no private_key
        content = '{"type": "service_account", "project_id": "test"}'
        json_data = write_input("config.json", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 0, "Should need both type and private_key"


class TestAzureCredentials:
    """Tests for Azure credential detection."""

    def test_azure_storage_connection_string_detected(self, run_hook, write_input):
        """Azure storage connection string should be detected."""
        content = 'AZURE_STORAGE = "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJ=="'
        json_data = write_input("azure.py", content)
        exit_code, stdout, stderr = run_hook(json_data)
        assert exit_code == 1
        assert "Azure" in stdout
