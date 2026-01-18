"""Comprehensive tests for git_commit_check.py hook."""

import json
import subprocess
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import git_commit_check


class TestImportsAndFunctions:
    """Smoke tests - verify module loads and key functions exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert git_commit_check is not None

    def test_key_functions_defined(self):
        """Key functions should be defined."""
        assert callable(git_commit_check.get_staged_files)
        assert callable(git_commit_check.get_staged_file_content)
        assert callable(git_commit_check.check_security)
        assert callable(git_commit_check.check_frontend_credentials)
        assert callable(git_commit_check.check_direct_api_calls)
        assert callable(git_commit_check.check_env_file_in_gitignore)
        assert callable(git_commit_check.is_example_password)
        assert callable(git_commit_check.check_hardcoded_secrets)
        assert callable(git_commit_check.main)


class TestIsExamplePassword:
    """Tests for is_example_password() function."""

    def test_detects_example_indicator(self):
        """Should detect 'example' as an indicator."""
        assert git_commit_check.is_example_password('password = "example_secret"') is True

    def test_detects_fake_indicator(self):
        """Should detect 'fake' as an indicator."""
        assert git_commit_check.is_example_password('password = "fake_password"') is True

    def test_detects_mock_indicator(self):
        """Should detect 'mock' as an indicator."""
        assert git_commit_check.is_example_password('password = "mock-token-123"') is True

    def test_detects_test_indicator(self):
        """Should detect 'test' as an indicator."""
        assert git_commit_check.is_example_password('api_key = "test_api_key"') is True

    def test_detects_placeholder_indicator(self):
        """Should detect 'placeholder' as an indicator."""
        assert git_commit_check.is_example_password('secret = "placeholder_value"') is True

    def test_detects_dummy_indicator(self):
        """Should detect 'dummy' as an indicator."""
        assert git_commit_check.is_example_password('token = "dummy-token"') is True

    def test_detects_sample_indicator(self):
        """Should detect 'sample' as an indicator."""
        assert git_commit_check.is_example_password('key = "sample_key_123"') is True

    def test_detects_changeme_indicator(self):
        """Should detect 'changeme' as an indicator."""
        assert git_commit_check.is_example_password('password = "changeme"') is True

    def test_detects_your_prefix(self):
        """Should detect 'your-' prefix pattern."""
        assert git_commit_check.is_example_password('password = "your-password-here"') is True
        assert git_commit_check.is_example_password('secret = "your_secret_key"') is True

    def test_detects_xxx_placeholder(self):
        """Should detect 'xxx' placeholder."""
        assert git_commit_check.is_example_password('password = "xxx"') is True

    def test_detects_replace_indicator(self):
        """Should detect 'replace' as an indicator."""
        assert git_commit_check.is_example_password('# Replace with your real key') is True

    def test_detects_template_indicator(self):
        """Should detect 'template' as an indicator."""
        assert git_commit_check.is_example_password('password = "template_password"') is True

    def test_no_false_positive_on_contest(self):
        """Should NOT flag 'contest' as containing 'test'."""
        assert git_commit_check.is_example_password('password = "contest_winner_2024"') is False

    def test_no_false_positive_on_latest(self):
        """Should NOT flag 'latest' as containing 'test'."""
        assert git_commit_check.is_example_password('version = "latest"') is False

    def test_no_false_positive_on_fastest(self):
        """Should NOT flag 'fastest' as containing 'test'."""
        assert git_commit_check.is_example_password('algorithm = "fastest_sort"') is False

    def test_no_false_positive_on_detest(self):
        """Should NOT flag 'detest' as containing 'test'."""
        assert git_commit_check.is_example_password('mood = "detest"') is False

    def test_no_false_positive_on_attest(self):
        """Should NOT flag 'attest' as containing 'test'."""
        assert git_commit_check.is_example_password('action = "attest"') is False

    def test_no_false_positive_on_real_password(self):
        """Should NOT flag real-looking passwords."""
        assert git_commit_check.is_example_password('password = "Xk9#mP2$vL8@nQ4!"') is False

    def test_no_false_positive_on_production_key(self):
        """Should NOT flag production-style keys.

        NOTE: We use a realistic key format that doesn't contain indicator words
        like 'test', 'live', 'example', etc. The actual Stripe sk_live_ format
        cannot be used because it triggers GitHub Push Protection.
        """
        assert git_commit_check.is_example_password('api_key = "rk_prod_4Xm9Pz7KjL2nQwYs"') is False


class TestGetStagedFiles:
    """Tests for get_staged_files()."""

    def test_returns_staged_file_list(self):
        """Should return list of staged files."""
        mock_result = MagicMock(stdout="file1.py\nfile2.js\n", returncode=0)
        with patch.object(subprocess, "run", return_value=mock_result):
            result = git_commit_check.get_staged_files()
            assert result == ["file1.py", "file2.js"]

    def test_returns_empty_list_on_error(self):
        """Should return empty list on subprocess error."""
        with patch.object(subprocess, "run", side_effect=subprocess.CalledProcessError(1, "git")):
            assert git_commit_check.get_staged_files() == []

    def test_returns_empty_list_when_nothing_staged(self):
        """Should return empty list when no files staged."""
        mock_result = MagicMock(stdout="", returncode=0)
        with patch.object(subprocess, "run", return_value=mock_result):
            result = git_commit_check.get_staged_files()
            assert result == []

    def test_returns_empty_list_on_timeout(self):
        """Should return empty list on subprocess timeout."""
        with patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 30)):
            assert git_commit_check.get_staged_files() == []


class TestGetStagedFileContent:
    """Tests for get_staged_file_content()."""

    def test_returns_file_content(self):
        """Should return content of staged file."""
        mock_result = MagicMock(stdout="file content here", returncode=0)
        with patch.object(subprocess, "run", return_value=mock_result):
            assert git_commit_check.get_staged_file_content("test.py") == "file content here"

    def test_returns_empty_string_on_error(self):
        """Should return empty string on subprocess error."""
        with patch.object(subprocess, "run", side_effect=subprocess.CalledProcessError(1, "git")):
            assert git_commit_check.get_staged_file_content("test.py") == ""

    def test_returns_empty_string_on_timeout(self):
        """Should return empty string on subprocess timeout."""
        with patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 30)):
            assert git_commit_check.get_staged_file_content("test.py") == ""


class TestCheckSecurity:
    """Tests for check_security()."""

    def test_detects_env_file(self):
        """Should detect .env file in staged files."""
        errors = git_commit_check.check_security([".env"])
        assert len(errors) == 1
        assert "environment file" in errors[0].lower()

    def test_detects_nested_env_file(self):
        """Should detect nested .env file."""
        errors = git_commit_check.check_security(["config/.env"])
        assert len(errors) == 1
        assert ".env" in errors[0]

    def test_detects_env_variants(self):
        """Should detect .env variant files."""
        errors = git_commit_check.check_security([".env.local"])
        assert len(errors) == 1

    def test_allows_non_env_files(self):
        """Should allow non-.env files."""
        errors = git_commit_check.check_security(["config.py", "app.js"])
        assert errors == []

    def test_detects_password_logging_js(self):
        """Should detect password being logged in JavaScript."""
        with patch.object(
            git_commit_check, "get_staged_file_content",
            return_value='console.log(password)'
        ):
            errors = git_commit_check.check_security(["app.js"])
            assert len(errors) == 1
            assert "secret exposure" in errors[0].lower()

    def test_detects_env_logging_python(self):
        """Should detect environment variable logging in Python."""
        with patch.object(
            git_commit_check, "get_staged_file_content",
            return_value='print(os.environ.get("DATABASE_URL"))'
        ):
            errors = git_commit_check.check_security(["app.py"])
            assert len(errors) >= 1
            assert any("secret exposure" in e.lower() for e in errors)


class TestCheckHardcodedSecrets:
    """Tests for check_hardcoded_secrets()."""

    def test_detects_openai_key(self):
        """Should detect OpenAI API key."""
        content = 'api_key = "sk-abc123def456ghi789jkl012mno345"'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_hardcoded_secrets(["app.py"])
            assert len(errors) == 1
            assert "OpenAI" in errors[0]

    def test_detects_stripe_test_key(self):
        """Should detect Stripe test key.

        NOTE: We test sk_test_ instead of sk_live_ because sk_live_ triggers
        GitHub Push Protection even with obviously fake keys.
        """
        content = 'key = "sk_test_TESTKEY00000000000000000000000"'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_hardcoded_secrets(["payment.py"])
            assert len(errors) == 1
            assert "Stripe" in errors[0] and "key" in errors[0].lower()

    def test_detects_github_pat(self):
        """Should detect GitHub personal access token."""
        content = 'token = "ghp_TESTTOKEN0000000000000000000000000000"'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_hardcoded_secrets(["deploy.py"])
            assert len(errors) == 1
            assert "GitHub" in errors[0]

    def test_detects_slack_token(self):
        """Should detect Slack token."""
        content = 'slack_token = "xoxb-abc123-def456-ghi789"'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_hardcoded_secrets(["notifier.py"])
            assert len(errors) == 1
            assert "Slack" in errors[0]

    def test_skips_example_password(self):
        """Should skip passwords that look like examples."""
        content = 'password = "your-password-here"'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_hardcoded_secrets(["config.py"])
            assert errors == []

    def test_skips_changeme_password(self):
        """Should skip 'changeme' placeholder passwords."""
        content = 'password = "changeme"'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_hardcoded_secrets(["config.py"])
            assert errors == []

    def test_skips_test_prefix_password(self):
        """Should skip test passwords."""
        content = 'password = "test_password_123"'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_hardcoded_secrets(["config.py"])
            assert errors == []

    def test_detects_real_password(self):
        """Should detect real-looking hardcoded password."""
        content = 'password = "Xk9mP2vL8nQ4wR6t"'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_hardcoded_secrets(["config.py"])
            assert len(errors) == 1
            assert "Hardcoded password" in errors[0]

    def test_ignores_non_code_files(self):
        """Should ignore non-code files."""
        content = 'password = "real_secret_123"'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_hardcoded_secrets(["data.json", "readme.md"])
            assert errors == []


class TestCheckFrontendCredentials:
    """Tests for check_frontend_credentials()."""

    def test_detects_vite_api_key(self):
        """Should detect VITE_ credential in frontend code."""
        content = 'const key = import.meta.env.VITE_API_KEY'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_frontend_credentials(["src/App.tsx"])
            assert len(errors) >= 1
            assert any("Frontend credential exposure" in e for e in errors)

    def test_detects_react_app_secret(self):
        """Should detect REACT_APP_ credential."""
        content = 'const secret = process.env.REACT_APP_SECRET_KEY'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_frontend_credentials(["src/api.jsx"])
            assert len(errors) >= 1
            assert any("REACT_APP" in e for e in errors)

    def test_detects_next_public_token(self):
        """Should detect NEXT_PUBLIC_ credential."""
        content = 'const token = process.env.NEXT_PUBLIC_AUTH_TOKEN'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_frontend_credentials(["pages/index.tsx"])
            assert len(errors) >= 1
            assert any("NEXT_PUBLIC" in e for e in errors)

    def test_allows_safe_frontend_env(self):
        """Should allow non-credential frontend env vars."""
        content = 'const apiUrl = process.env.NEXT_PUBLIC_API_URL'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            errors = git_commit_check.check_frontend_credentials(["pages/index.tsx"])
            assert errors == []


class TestCheckDirectApiCalls:
    """Tests for check_direct_api_calls()."""

    def test_warns_on_direct_stripe_call(self):
        """Should warn on direct Stripe API call from frontend."""
        content = 'fetch("https://api.stripe.com/v1/charges")'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            warnings = git_commit_check.check_direct_api_calls(["src/payment.jsx"])
            assert len(warnings) == 1
            assert "SACROSANCT Warning" in warnings[0]
            assert "backend proxy" in warnings[0].lower()

    def test_warns_on_direct_openai_call(self):
        """Should warn on direct OpenAI API call from frontend."""
        content = 'fetch("https://api.openai.com/v1/completions")'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            warnings = git_commit_check.check_direct_api_calls(["src/chat.tsx"])
            assert len(warnings) == 1
            assert "SACROSANCT Warning" in warnings[0]
            assert "backend proxy" in warnings[0].lower()

    def test_no_warning_for_backend_files(self):
        """Should not warn for backend files."""
        content = 'fetch("https://api.openai.com/v1/completions")'
        with patch.object(git_commit_check, "get_staged_file_content", return_value=content):
            warnings = git_commit_check.check_direct_api_calls(["server/api/openai.ts"])
            assert warnings == []


class TestCheckEnvFileInGitignore:
    """Tests for check_env_file_in_gitignore()."""

    def test_returns_true_when_protected(self):
        """Should return True when .env is in .gitignore."""
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=".env\n.env.*\n"):
            is_protected, error = git_commit_check.check_env_file_in_gitignore()
            assert is_protected is True
            assert error is None

    def test_returns_error_when_no_gitignore(self):
        """Should return error when no .gitignore exists."""
        with patch("pathlib.Path.exists", return_value=False):
            is_protected, error = git_commit_check.check_env_file_in_gitignore()
            assert is_protected is False
            assert "No .gitignore file found" in error

    def test_returns_violation_when_env_not_protected(self):
        """Should return violation when .env not in .gitignore."""
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value="node_modules/\n*.log\n"):
            is_protected, error = git_commit_check.check_env_file_in_gitignore()
            assert is_protected is False
            assert "VIOLATION" in error


class TestMain:
    """Tests for main() JSON input/output flow."""

    def test_allows_non_commit_commands(self):
        """Should allow non-commit git commands."""
        input_data = json.dumps({"tool_input": {"command": "git status"}})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             pytest.raises(SystemExit) as exc_info:
            git_commit_check.main()
        assert exc_info.value.code == 0

    def test_allows_commit_when_no_staged_files(self):
        """Should allow commit when no files are staged."""
        input_data = json.dumps({"tool_input": {"command": "git commit -m 'test'"}})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(git_commit_check, "get_staged_files", return_value=[]), \
             pytest.raises(SystemExit) as exc_info:
            git_commit_check.main()
        assert exc_info.value.code == 0

    def test_blocks_on_security_violation(self, capsys):
        """Should exit with code 2 on security violation."""
        input_data = json.dumps({"tool_input": {"command": "git commit -m 'test'"}})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(git_commit_check, "get_staged_files", return_value=[".env"]), \
             pytest.raises(SystemExit) as exc_info:
            git_commit_check.main()
        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert "PACT Security Violation" in captured.err

    def test_allows_clean_commit(self, capsys):
        """Should allow commit when no violations."""
        input_data = json.dumps({"tool_input": {"command": "git commit -m 'test'"}})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(git_commit_check, "get_staged_files", return_value=["clean.py"]), \
             patch.object(git_commit_check, "get_staged_file_content", return_value="# Clean code"), \
             patch.object(git_commit_check, "check_env_file_in_gitignore", return_value=(True, None)), \
             pytest.raises(SystemExit) as exc_info:
            git_commit_check.main()
        assert exc_info.value.code == 0

    def test_handles_malformed_json(self):
        """Should exit cleanly on malformed JSON input."""
        with patch.object(sys, "stdin", StringIO("not valid json")), \
             pytest.raises(SystemExit) as exc_info:
            git_commit_check.main()
        assert exc_info.value.code == 0

    def test_handles_exception_gracefully(self, capsys):
        """Should handle exceptions and allow commit to proceed."""
        input_data = json.dumps({"tool_input": {"command": "git commit -m 'test'"}})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(git_commit_check, "get_staged_files", side_effect=RuntimeError("Test error")), \
             pytest.raises(SystemExit) as exc_info:
            git_commit_check.main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "ERROR" in captured.err

    def test_prints_warnings_to_stderr(self, capsys):
        """Should print warnings to stderr but still allow commit."""
        input_data = json.dumps({"tool_input": {"command": "git commit -m 'test'"}})
        with patch.object(sys, "stdin", StringIO(input_data)), \
             patch.object(git_commit_check, "get_staged_files", return_value=["src/api.jsx"]), \
             patch.object(git_commit_check, "get_staged_file_content", return_value='fetch("https://api.stripe.com/v1/charges")'), \
             patch.object(git_commit_check, "check_env_file_in_gitignore", return_value=(True, None)), \
             pytest.raises(SystemExit) as exc_info:
            git_commit_check.main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "PACT Security Warnings" in captured.err
