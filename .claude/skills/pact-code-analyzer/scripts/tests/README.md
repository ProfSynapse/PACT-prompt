# Test Suite for pact-code-analyzer

This directory contains comprehensive tests for the pact-code-analyzer skill scripts.

## Overview

The test suite validates all four code analysis scripts:

1. **complexity_analyzer.py** - Cyclomatic complexity calculation
2. **dependency_mapper.py** - Dependency mapping and circular detection
3. **coupling_detector.py** - Module coupling measurement
4. **file_metrics.py** - File statistics and PACT compliance

## Quick Start

### Running Tests

```bash
# Run all tests
cd /path/to/pact-code-analyzer/scripts
pytest tests/

# Run specific test file
pytest tests/test_complexity_analyzer.py

# Run with verbose output
pytest tests/ -v

# Run specific test class
pytest tests/test_complexity_analyzer.py::TestPythonComplexity

# Run specific test function
pytest tests/test_complexity_analyzer.py::TestPythonComplexity::test_simple_functions

# Run with coverage report
pytest tests/ --cov=. --cov-report=html
```

### Prerequisites

```bash
# Install pytest
pip install pytest

# Optional: Install coverage tool
pip install pytest-cov
```

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared pytest fixtures
├── fixtures/                   # Test fixture files
│   ├── python/                 # Python test files
│   ├── javascript/             # JavaScript test files
│   └── typescript/             # TypeScript test files
├── test_complexity_analyzer.py # Complexity analysis tests
├── test_dependency_mapper.py   # Dependency mapping tests
├── test_coupling_detector.py   # Coupling detection tests
├── test_file_metrics.py        # File metrics tests
└── README.md                   # This file
```

## Test Fixtures

### Python Fixtures (`fixtures/python/`)

| Fixture | Purpose | Expected Results |
|---------|---------|------------------|
| `simple_function.py` | Low complexity (1-2) | 2 functions, complexity 1 each |
| `moderate_complexity.py` | Medium complexity (3-5) | 3 functions, avg complexity 4.0 |
| `high_complexity.py` | High complexity (10+) | 2 functions, 1 exceeds threshold |
| `circular_import_a.py` | Circular dependency testing | Imports circular_import_b |
| `circular_import_b.py` | Circular dependency testing | Imports circular_import_a |
| `standalone_module.py` | Orphan module testing | No imports, not imported |
| `large_file.py` | PACT compliance testing | 650+ lines, exceeds limit |

### JavaScript Fixtures (`fixtures/javascript/`)

| Fixture | Purpose | Expected Results |
|---------|---------|------------------|
| `simple_module.js` | Basic JS functions | 2 functions, complexity 1 each |
| `complex_module.js` | Complex JS logic | 3 functions, varying complexity |
| `es6_features.js` | ES6 syntax (arrow, async, class) | Arrow functions, classes detected |

### TypeScript Fixtures (`fixtures/typescript/`)

| Fixture | Purpose | Expected Results |
|---------|---------|------------------|
| `typed_module.ts` | Type annotations | Functions detected despite types |
| `react_component.tsx` | React component | Component and helper functions |

## Test Coverage

### test_complexity_analyzer.py

**Test Classes:**
- `TestPythonComplexity` - Python AST analysis accuracy
- `TestJavaScriptComplexity` - JS analysis (Node.js AST and regex fallback)
- `TestTypeScriptComplexity` - TypeScript regex fallback
- `TestThresholdDetection` - Complexity threshold flags
- `TestOutputFormat` - JSON output structure and metadata
- `TestErrorHandling` - Syntax errors, invalid inputs

**Key Test Cases:**
- Simple functions with no decision points (complexity 1)
- Moderate complexity with if/for/while statements (complexity 3-5)
- High complexity exceeding threshold (complexity 10+)
- JavaScript arrow functions and ES6 features
- TypeScript with type annotations
- Custom threshold detection
- Regex fallback warning when Node.js unavailable
- Error handling for syntax errors and invalid files

**Expected Coverage:**
- AST parsing for Python and JavaScript (when Node.js available)
- Regex fallback for JavaScript/TypeScript
- Decision point counting (if, for, while, and, or, ternary, etc.)
- Threshold violation detection
- JSON output format validation

### test_dependency_mapper.py

**Test Classes:**
- `TestCircularDependencies` - Circular import detection
- `TestOrphanModules` - Orphan module identification
- `TestDependencyGraph` - JSON and DOT graph output
- `TestMultiLanguageSupport` - Python, JS, TS support
- `TestModuleDetails` - Fan-in/fan-out, imported_by lists
- `TestSummaryStatistics` - Aggregate metrics
- `TestOutputFormat` - JSON structure
- `TestErrorHandling` - Invalid inputs

**Key Test Cases:**
- Circular dependency detection between two Python modules
- Orphan module identification (standalone files)
- Entry point exclusion (main.py, index.js not flagged as orphans)
- JSON graph format with imports and imported_by
- DOT graph format for Graphviz visualization
- JavaScript require() and ES6 import detection
- TypeScript import detection
- Maximum dependency depth calculation

**Expected Coverage:**
- Import statement extraction (Python AST, JS/TS regex)
- Dependency graph construction
- Circular dependency DFS algorithm
- Orphan detection (files not imported by others)
- Multi-language support

### test_coupling_detector.py

**Test Classes:**
- `TestFanInFanOut` - Fan-in/fan-out calculation
- `TestCouplingThresholds` - Threshold flags
- `TestRecommendations` - Coupling recommendations
- `TestSummaryStatistics` - Top coupled modules
- `TestOutputFormat` - JSON structure
- `TestErrorHandling` - Invalid inputs
- `TestOrphanModules` - Zero incoming dependencies

**Key Test Cases:**
- Basic coupling metrics (fan-in + fan-out = total coupling)
- Detailed mode with fan_in/fan_out lists
- Circular dependencies reflected in coupling
- Custom threshold detection
- High fan-in recommendation (central module)
- High fan-out recommendation (many dependencies)
- Top 5 coupled modules ranking
- Average coupling calculation

**Expected Coverage:**
- Fan-in calculation (modules importing this module)
- Fan-out calculation (modules this module imports)
- Coupling threshold detection
- Recommendation generation based on coupling type
- Summary statistics

### test_file_metrics.py

**Test Classes:**
- `TestPACTCompliance` - 600-line limit checking
- `TestLineCountAccuracy` - Code/comment/blank counting
- `TestElementCounting` - Function/class/import counting
- `TestMultiLanguageSupport` - Python, JS, TS support
- `TestSummaryStatistics` - Aggregate metrics
- `TestOutputFormat` - JSON structure
- `TestErrorHandling` - Invalid inputs

**Key Test Cases:**
- File within PACT 600-line limit (acceptable)
- File exceeding PACT limit (recommendation to split)
- Line counting accuracy (code + comment + blank = total)
- Python comment detection (# and docstrings)
- JavaScript comment detection (// and /* */)
- Function counting (Python AST, JS regex)
- Class counting (Python AST, JS regex)
- Import statement counting
- Language detection from file extension
- Multi-language directory analysis

**Expected Coverage:**
- Line type classification (code, comment, blank)
- Python docstring detection
- Multi-line comment detection
- Function/class/import counting
- PACT compliance flagging
- Summary aggregation

## Shared Fixtures (conftest.py)

The `conftest.py` file provides shared pytest fixtures used across test modules:

### Directory Fixtures
- `scripts_dir` - Path to scripts directory
- `fixtures_dir` - Path to test fixtures directory
- `python_fixtures_dir` - Path to Python fixtures
- `javascript_fixtures_dir` - Path to JavaScript fixtures
- `typescript_fixtures_dir` - Path to TypeScript fixtures

### Script Runner Fixtures
- `run_complexity_analyzer(file_path, threshold)` - Run complexity_analyzer.py
- `run_dependency_mapper(directory, language, detect_circular)` - Run dependency_mapper.py
- `run_coupling_detector(directory, threshold, show_details)` - Run coupling_detector.py
- `run_file_metrics(file_path, directory, language)` - Run file_metrics.py

## Adding New Tests

### Adding a New Fixture

1. Create the fixture file in the appropriate directory:
   ```bash
   # Python fixture
   touch tests/fixtures/python/new_fixture.py

   # JavaScript fixture
   touch tests/fixtures/javascript/new_fixture.js

   # TypeScript fixture
   touch tests/fixtures/typescript/new_fixture.ts
   ```

2. Add comprehensive docstring with expected results:
   ```python
   """
   Test fixture for [purpose].

   Expected Complexity Analysis Results:
   - function_name: Complexity X (decision points)
   - Total file complexity: Y

   Expected File Metrics:
   - Total lines: ~Z
   - Functions: N
   - Classes: M
   """
   ```

3. Write minimal but representative code that tests the feature

### Adding a New Test Case

1. Identify the appropriate test file (or create a new one)

2. Add test to relevant test class:
   ```python
   class TestFeatureName:
       """Test description."""

       def test_specific_behavior(self, run_script_fixture, fixtures_dir):
           """Test what specific behavior is validated."""
           # Arrange
           fixture = fixtures_dir / 'relevant_fixture.py'

           # Act
           result = run_script_fixture(fixture, threshold=10)

           # Assert
           assert result['expected_field'] == expected_value
   ```

3. Follow naming conventions:
   - Test classes: `TestFeatureName`
   - Test methods: `test_specific_behavior`
   - Use descriptive names that explain what is being tested

### Test Writing Guidelines

1. **Arrange-Act-Assert pattern**: Structure tests clearly
2. **Descriptive names**: Test names should explain what is being tested
3. **One assertion focus**: Each test should validate one behavior
4. **Use fixtures**: Leverage shared fixtures from conftest.py
5. **Document expected results**: Add comments explaining expected values
6. **Handle edge cases**: Test boundary conditions and error scenarios

## Expected Test Results

When all tests pass, you should see output like:

```
============================= test session starts ==============================
collected 85 items

tests/test_complexity_analyzer.py ..................                      [ 21%]
tests/test_coupling_detector.py .....................                    [ 45%]
tests/test_dependency_mapper.py .....................                    [ 70%]
tests/test_file_metrics.py .............................                 [100%]

============================== 85 passed in 5.23s ==============================
```

## Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError: No module named 'pytest'**
```bash
# Solution: Install pytest
pip install pytest
```

**Issue: Tests fail with "File not found" errors**
```bash
# Solution: Ensure you're running from the scripts directory
cd /path/to/pact-code-analyzer/scripts
pytest tests/
```

**Issue: JavaScript tests fail or skip**
```bash
# Cause: Node.js not installed or npm dependencies missing
# Solution: Install Node.js and run:
cd scripts
npm install

# Alternatively, tests will use regex fallback (with warnings)
```

**Issue: Circular import fixture tests fail**
```bash
# Cause: Python may prevent actual circular import execution
# Solution: Tests validate detection, not execution of circular imports
# The fixtures are analyzed statically, not imported
```

### Debugging Tests

Run specific test with verbose output:
```bash
pytest tests/test_complexity_analyzer.py::TestPythonComplexity::test_simple_functions -v -s
```

Print script output during tests:
```bash
pytest tests/ -v -s --capture=no
```

## Maintenance

### When to Update Tests

1. **Script changes**: When modifying script behavior, update corresponding tests
2. **Bug fixes**: Add regression tests for fixed bugs
3. **New features**: Add tests for new functionality
4. **Fixture updates**: If fixture expected results change, update docstrings

### Test Quality Standards

- Maintain >80% code coverage for all scripts
- All tests must pass before committing changes
- Add tests for new features before implementation (TDD)
- Document expected results in fixture docstrings
- Keep fixtures minimal but representative

## Contributing

When adding tests:

1. Follow existing test structure and naming conventions
2. Add comprehensive docstrings to fixtures
3. Use shared fixtures from conftest.py
4. Ensure tests are isolated (no dependencies between tests)
5. Update this README if adding new test categories
6. Run full test suite before submitting changes

## License

These tests are part of the PACT Framework and follow the same MIT license as the main project.
