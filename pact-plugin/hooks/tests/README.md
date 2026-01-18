# PACT Plugin Hooks Tests

This directory contains tests for the PACT plugin hook scripts.

## Test Structure

Tests are organized by hook module, with each test file following a consistent structure:

```
tests/
├── conftest.py              # Shared fixtures for all tests
├── pytest.ini               # Pytest configuration
├── README.md                # This file
├── test_phase_completion.py # Tests for phase_completion.py
├── test_memory_enforce.py   # Tests for memory_enforce.py
├── test_s5_credential_scan.py # Tests for s5-credential-scan.sh
└── ...                      # Other hook tests
```

### Test Class Organization

Each test file follows a consistent class structure:

| Class Pattern | Purpose |
|---------------|---------|
| `TestImportsAndConstants` | Smoke tests - module loads, constants exist |
| `Test{FunctionName}` | Unit tests for specific functions |
| `TestMainJsonFlow` | Tests for main() JSON I/O |
| `TestEdgeCases` | Boundary conditions, special inputs |
| `TestIntegrationScenarios` | Realistic end-to-end scenarios |

## Running Tests

### Basic Test Run

```bash
cd pact-plugin/hooks
python -m pytest tests/ -v
```

### With Coverage Report

```bash
# Install pytest-cov if needed
pip install pytest-cov

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing

# Generate HTML coverage report
python -m pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test File

```bash
python -m pytest tests/test_phase_completion.py -v
```

### Run Specific Test Class

```bash
python -m pytest tests/test_phase_completion.py::TestCheckForCodePhaseActivity -v
```

### Run Specific Test

```bash
python -m pytest tests/test_phase_completion.py::TestCheckForCodePhaseActivity::test_detects_backend_coder -v
```

## Test Patterns and Conventions

### Why `sk_test_` Instead of `sk_live_` for Stripe Tests

In credential scan tests, we use `sk_test_` prefixed keys instead of `sk_live_`:

```python
# Good - uses sk_test_
content = 'stripe_key = "sk_test_TESTKEY00000000000000000000"'

# Avoid - triggers GitHub Push Protection even with fake keys
content = 'stripe_key = "sk_live_<REDACTED>"'  # Pattern blocked by GitHub
```

**Reason**: GitHub Push Protection scans all commits for credential patterns. Even obviously fake `sk_live_` keys trigger alerts and block pushes. Using `sk_test_` patterns still tests the credential detection logic while avoiding false positives from GitHub's scanning.

### Adding New Credential Patterns for Testing

When testing credential detection:

1. **Use test/example prefixes when possible**
   ```python
   # Preferred patterns for test keys
   "sk_test_..."      # Stripe test keys
   "AKIAIOSFODNN7EXAMPLE"  # AWS example key (from AWS docs)
   "ghp_TESTTOKEN..."  # GitHub test token
   ```

2. **Mark obviously fake values**
   ```python
   # Include indicator words in the value or comment
   content = 'api_key = "sk-abcdefghij..."  # example key'
   content = 'password = "test_password_placeholder"'
   ```

3. **Use safe path exclusions**
   ```python
   # Test in excluded paths when testing that exclusions work
   json_data = write_input("docs/examples/config.py", content)
   ```

4. **Never use real credentials**, even partially. The credential scan should detect them, but Git history is permanent.

### Testing Shell Scripts vs Python Modules

**Python modules** are tested by importing and calling functions directly:

```python
import phase_completion

def test_function():
    result = phase_completion.check_for_code_phase_activity("...")
    assert result is True
```

**Shell scripts** are tested via subprocess:

```python
def test_shell_hook(run_hook, write_input):
    json_data = write_input("config.py", "password = 'secret'")
    exit_code, stdout, stderr = run_hook(json_data)
    assert exit_code == 1
```

### Common Fixtures

The `conftest.py` provides shared fixtures:

| Fixture | Purpose |
|---------|---------|
| `tmp_path` | pytest built-in - temporary directory |
| `project_dir` | Clean temp directory for project root |
| `project_with_docs` | Project with standard PACT docs structure |
| `project_with_populated_docs` | Project with files in all docs directories |
| `make_json_input` | Factory to create JSON input strings |
| `run_shell_hook` | Factory to run shell hook scripts |
| `long_transcript` | Transcript meeting minimum length requirements |
| `code_phase_transcript` | Transcript with CODE phase indicators |
| `pact_work_agents` | List of all PACT work agent names |

### Test Naming Conventions

- Test functions start with `test_`
- Use descriptive names that explain what's being tested
- Format: `test_{what}_{condition}` or `test_{action}_{expected_result}`

Examples:
```python
def test_detects_backend_coder():          # Tests detection
def test_returns_false_for_empty_input():  # Tests edge case
def test_exits_cleanly_on_malformed_json(): # Tests error handling
```

## Troubleshooting

### Import Errors

If you see import errors, ensure you're running from the correct directory:

```bash
# Run from hooks directory
cd pact-plugin/hooks
python -m pytest tests/ -v
```

### Path Issues

Tests use `sys.path.insert()` to find the hook modules:

```python
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
```

This adds the parent `hooks/` directory to the Python path.

### Shell Script Tests Failing

Ensure shell scripts are executable:

```bash
chmod +x pact-plugin/hooks/*.sh
```

### Coverage Reports

If coverage seems low, ensure you're measuring the right directory:

```bash
# Measure coverage for the hooks directory (parent of tests)
python -m pytest tests/ --cov=.. --cov-report=term-missing
```

## Adding New Tests

1. Create a new test file following the naming convention: `test_{hook_name}.py`
2. Import the module under test with the path adjustment
3. Follow the class organization pattern
4. Use fixtures from `conftest.py` where applicable
5. Run tests to verify they pass
