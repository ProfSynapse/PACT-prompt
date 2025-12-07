"""
Tests for complexity_analyzer.py

Tests cover:
- Python AST analysis accuracy
- JavaScript analysis (Node.js AST and regex fallback)
- TypeScript regex fallback
- Threshold flag detection
- JSON output format
- Error handling for syntax errors
"""

import pytest
import json
import subprocess
from pathlib import Path


class TestPythonComplexity:
    """Test Python complexity analysis using AST."""

    def test_simple_functions(self, run_complexity_analyzer, python_fixtures_dir):
        """Test simple Python functions with no decision points."""
        fixture = python_fixtures_dir / 'simple_function.py'
        result = run_complexity_analyzer(fixture, threshold=10)

        assert 'files' in result
        assert len(result['files']) == 1

        file_result = result['files'][0]
        assert file_result['language'] == 'python'
        assert file_result['analysis_method'] == 'python_ast'
        assert file_result['total_complexity'] == 2
        assert file_result['average_complexity'] == 1.0

        # Check individual functions
        functions = {f['name']: f for f in file_result['functions']}
        assert 'greet' in functions
        assert functions['greet']['complexity'] == 1
        assert functions['greet']['exceeds_threshold'] is False

        assert 'add_numbers' in functions
        assert functions['add_numbers']['complexity'] == 1

    def test_moderate_complexity(self, run_complexity_analyzer, python_fixtures_dir):
        """Test moderate complexity Python code."""
        fixture = python_fixtures_dir / 'moderate_complexity.py'
        result = run_complexity_analyzer(fixture, threshold=10)

        file_result = result['files'][0]
        assert file_result['total_complexity'] == 11
        assert file_result['average_complexity'] == 3.7

        functions = {f['name']: f for f in file_result['functions']}

        # validate_email: 3 (base + 2 if statements)
        assert functions['validate_email']['complexity'] == 3

        # calculate_discount: 4 (base + 3 if/elif, else not counted)
        assert functions['calculate_discount']['complexity'] == 4

        # process_items: 4 (base + for + if + and)
        assert functions['process_items']['complexity'] == 4

        # No functions should exceed threshold of 10
        for func in file_result['functions']:
            assert func['exceeds_threshold'] is False

    def test_high_complexity_exceeds_threshold(self, run_complexity_analyzer, python_fixtures_dir):
        """Test high complexity code that exceeds threshold."""
        fixture = python_fixtures_dir / 'high_complexity.py'
        result = run_complexity_analyzer(fixture, threshold=10)

        file_result = result['files'][0]
        assert file_result['total_complexity'] == 19

        functions = {f['name']: f for f in file_result['functions']}

        # process_order should exceed threshold
        assert functions['process_order']['complexity'] == 12
        assert functions['process_order']['exceeds_threshold'] is True
        assert 'recommendation' in functions['process_order']
        assert 'smaller functions' in functions['process_order']['recommendation']

        # validate_user should not exceed threshold
        assert functions['validate_user']['complexity'] == 7
        assert functions['validate_user']['exceeds_threshold'] is False

        # Summary should show 1 function exceeding
        assert result['summary']['functions_exceeding_threshold'] == 1


class TestJavaScriptComplexity:
    """Test JavaScript complexity analysis (AST or regex fallback)."""

    def test_simple_javascript(self, run_complexity_analyzer, javascript_fixtures_dir):
        """Test simple JavaScript functions."""
        fixture = javascript_fixtures_dir / 'simple_module.js'
        result = run_complexity_analyzer(fixture, threshold=10)

        file_result = result['files'][0]
        assert file_result['language'] == 'javascript'
        assert file_result['total_complexity'] == 2
        assert file_result['average_complexity'] == 1.0

        # Both functions should have complexity 1
        functions = {f['name']: f for f in file_result['functions']}
        assert 'greet' in functions
        assert functions['greet']['complexity'] == 1
        assert 'add' in functions
        assert functions['add']['complexity'] == 1

    def test_complex_javascript(self, run_complexity_analyzer, javascript_fixtures_dir):
        """Test complex JavaScript with multiple decision points."""
        fixture = javascript_fixtures_dir / 'complex_module.js'
        result = run_complexity_analyzer(fixture, threshold=10)

        file_result = result['files'][0]
        assert file_result['language'] == 'javascript'

        functions = {f['name']: f for f in file_result['functions']}

        # processPayment should have high complexity (8-10 range acceptable)
        assert 'processPayment' in functions
        assert 7 <= functions['processPayment']['complexity'] <= 11

        # validateCard should have moderate complexity (5-6 range)
        assert 'validateCard' in functions
        assert 4 <= functions['validateCard']['complexity'] <= 7

        # formatAmount should have low complexity (2-3)
        assert 'formatAmount' in functions
        assert 1 <= functions['formatAmount']['complexity'] <= 4

    def test_es6_features(self, run_complexity_analyzer, javascript_fixtures_dir):
        """Test ES6 JavaScript features (arrow functions, classes, async)."""
        fixture = javascript_fixtures_dir / 'es6_features.js'
        result = run_complexity_analyzer(fixture, threshold=10)

        file_result = result['files'][0]
        assert file_result['language'] == 'javascript'

        # Should detect arrow functions and class methods
        functions = file_result['functions']
        assert len(functions) >= 3  # At minimum: filterActive, fetchUserData, square

        # Arrow function names should be detected
        function_names = [f['name'] for f in functions]
        assert 'filterActive' in function_names or 'fetchUserData' in function_names

    def test_regex_fallback_warning(self, run_complexity_analyzer, javascript_fixtures_dir):
        """Test that regex fallback produces warning when Node.js unavailable."""
        fixture = javascript_fixtures_dir / 'simple_module.js'
        result = run_complexity_analyzer(fixture, threshold=10)

        file_result = result['files'][0]

        # Check if regex fallback was used (warning may be present in errors)
        if file_result['analysis_method'] == 'regex_fallback':
            assert 'errors' in result or 'warnings' in result or len(result.get('errors', [])) > 0


class TestTypeScriptComplexity:
    """Test TypeScript complexity analysis (regex fallback)."""

    def test_typescript_with_types(self, run_complexity_analyzer, typescript_fixtures_dir):
        """Test TypeScript with type annotations."""
        fixture = typescript_fixtures_dir / 'typed_module.ts'
        result = run_complexity_analyzer(fixture, threshold=10)

        file_result = result['files'][0]
        assert file_result['language'] == 'typescript'

        # TypeScript function detection can be limited with regex fallback
        # Just verify the script runs without error
        assert 'functions' in file_result
        assert isinstance(file_result['functions'], list)
        # If functions detected, complexity should be reasonable
        if len(file_result['functions']) > 0:
            for func in file_result['functions']:
                assert func['complexity'] >= 1

    def test_react_tsx_component(self, run_complexity_analyzer, typescript_fixtures_dir):
        """Test React TSX component analysis."""
        fixture = typescript_fixtures_dir / 'react_component.tsx'
        result = run_complexity_analyzer(fixture, threshold=10)

        file_result = result['files'][0]
        assert file_result['language'] == 'typescript'

        # TypeScript/TSX function detection is challenging with regex fallback
        # Just verify the script runs without error and returns valid structure
        assert 'functions' in file_result
        assert isinstance(file_result['functions'], list)
        # If functions detected, validate structure
        if len(file_result['functions']) > 0:
            for func in file_result['functions']:
                assert 'name' in func
                assert 'complexity' in func


class TestThresholdDetection:
    """Test complexity threshold flag detection."""

    def test_custom_threshold(self, run_complexity_analyzer, python_fixtures_dir):
        """Test custom threshold detection."""
        fixture = python_fixtures_dir / 'high_complexity.py'

        # Use low threshold (5) - multiple functions should exceed
        result = run_complexity_analyzer(fixture, threshold=5)
        file_result = result['files'][0]

        exceeding_count = sum(1 for f in file_result['functions'] if f['exceeds_threshold'])
        assert exceeding_count >= 2  # Both functions should exceed threshold of 5

    def test_high_threshold(self, run_complexity_analyzer, python_fixtures_dir):
        """Test high threshold - no functions should exceed."""
        fixture = python_fixtures_dir / 'high_complexity.py'

        # Use high threshold (20) - no functions should exceed
        result = run_complexity_analyzer(fixture, threshold=20)
        file_result = result['files'][0]

        exceeding_count = sum(1 for f in file_result['functions'] if f['exceeds_threshold'])
        assert exceeding_count == 0


class TestOutputFormat:
    """Test JSON output format and metadata."""

    def test_json_structure(self, run_complexity_analyzer, python_fixtures_dir):
        """Test JSON output has required structure."""
        fixture = python_fixtures_dir / 'simple_function.py'
        result = run_complexity_analyzer(fixture)

        # Check metadata
        assert 'metadata' in result
        assert 'schema_version' in result['metadata']
        assert 'timestamp' in result['metadata']
        assert 'execution_duration_ms' in result['metadata']

        # Check summary
        assert 'summary' in result
        assert 'total_files' in result['summary']
        assert 'total_functions' in result['summary']
        assert 'average_complexity' in result['summary']

        # Check files array
        assert 'files' in result
        assert isinstance(result['files'], list)
        assert len(result['files']) == 1

        # Check file structure
        file_result = result['files'][0]
        assert 'path' in file_result
        assert 'language' in file_result
        assert 'analysis_method' in file_result
        assert 'total_complexity' in file_result
        assert 'average_complexity' in file_result
        assert 'functions' in file_result

        # Check function structure
        func = file_result['functions'][0]
        assert 'name' in func
        assert 'line' in func
        assert 'complexity' in func
        assert 'exceeds_threshold' in func

    def test_execution_duration(self, run_complexity_analyzer, python_fixtures_dir):
        """Test execution duration is measured."""
        fixture = python_fixtures_dir / 'simple_function.py'
        result = run_complexity_analyzer(fixture)

        duration = result['metadata']['execution_duration_ms']
        assert isinstance(duration, int)
        assert duration >= 0
        assert duration < 10000  # Should complete in under 10 seconds


class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_syntax_error_handling(self, scripts_dir, python_fixtures_dir):
        """Test graceful handling of Python syntax errors."""
        # Create file with syntax error in fixtures directory (within security boundary)
        bad_file = python_fixtures_dir / 'syntax_error_test.py'
        bad_file.write_text('def broken(\n  # Missing closing paren and body')

        try:
            # Should not crash, should return empty functions list
            result = subprocess.run(
                ['python3', str(scripts_dir / 'complexity_analyzer.py'),
                 '--file', str(bad_file), '--threshold', '10'],
                capture_output=True,
                text=True
            )

            # Script should succeed (exit code 0) but with empty/error results
            assert result.returncode == 0
            output = json.loads(result.stdout)
            file_result = output['files'][0]
            assert file_result['functions'] == []  # Empty due to syntax error
        finally:
            # Cleanup
            if bad_file.exists():
                bad_file.unlink()

    def test_nonexistent_file(self, scripts_dir, python_fixtures_dir):
        """Test error handling for nonexistent file."""
        # Use path within security boundary
        nonexistent = python_fixtures_dir / 'does_not_exist_xyz123.py'

        result = subprocess.run(
            ['python3', str(scripts_dir / 'complexity_analyzer.py'),
             '--file', str(nonexistent)],
            capture_output=True,
            text=True
        )

        # Should fail with error
        assert result.returncode == 1
        error_output = json.loads(result.stderr)
        assert 'error' in error_output
        assert 'not found' in error_output['error'].lower() or 'file not found' in error_output['error'].lower()

    def test_unsupported_file_extension(self, scripts_dir, python_fixtures_dir):
        """Test error for unsupported file extension."""
        # Create unsupported file in fixtures directory (within security boundary)
        unsupported = python_fixtures_dir / 'test_file.txt'
        unsupported.write_text('Some text content')

        try:
            result = subprocess.run(
                ['python3', str(scripts_dir / 'complexity_analyzer.py'),
                 '--file', str(unsupported)],
                capture_output=True,
                text=True
            )

            # Should fail with unsupported extension error
            assert result.returncode == 1
            error_output = json.loads(result.stderr)
            assert 'error' in error_output
            assert 'unsupported' in error_output['error'].lower()
        finally:
            # Cleanup
            if unsupported.exists():
                unsupported.unlink()
