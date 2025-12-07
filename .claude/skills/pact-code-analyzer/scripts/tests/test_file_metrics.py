"""
Tests for file_metrics.py

Tests cover:
- PACT 600-line compliance checking
- Comment/code line counting
- Function/class counting
- Multi-language support
- Summary statistics
"""

import pytest
import json
import subprocess
from pathlib import Path


class TestPACTCompliance:
    """Test PACT 600-line limit compliance checking."""

    def test_file_within_limit(self, run_file_metrics, python_fixtures_dir):
        """Test file within PACT 600-line limit."""
        fixture = python_fixtures_dir / 'simple_function.py'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]
        assert file_result['total_lines'] < 600
        assert file_result['exceeds_size_limit'] is False
        assert file_result['size_limit'] == 600
        assert 'acceptable' in file_result['recommendation'].lower()

    def test_file_exceeds_limit(self, run_file_metrics, python_fixtures_dir):
        """Test file exceeding PACT 600-line limit."""
        fixture = python_fixtures_dir / 'large_file.py'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]
        assert file_result['total_lines'] > 600
        assert file_result['exceeds_size_limit'] is True
        assert file_result['size_limit'] == 600
        assert 'splitting' in file_result['recommendation'].lower() or \
               'smaller modules' in file_result['recommendation'].lower()

    def test_summary_files_exceeding(self, run_file_metrics, python_fixtures_dir):
        """Test summary counts files exceeding limit."""
        result = run_file_metrics(directory=python_fixtures_dir)

        summary = result['summary']
        files_exceeding = summary['files_exceeding_limit']

        # Should have at least 1 (large_file.py)
        assert files_exceeding >= 1

        # Verify by checking files array
        actual_exceeding = sum(1 for f in result['files'] if f['exceeds_size_limit'])
        assert files_exceeding == actual_exceeding


class TestLineCountAccuracy:
    """Test accuracy of line counting (code, comments, blank)."""

    def test_python_line_counting(self, run_file_metrics, python_fixtures_dir):
        """Test Python line counting accuracy."""
        fixture = python_fixtures_dir / 'simple_function.py'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]

        # Should have all line types counted
        assert 'total_lines' in file_result
        assert 'code_lines' in file_result
        assert 'comment_lines' in file_result
        assert 'blank_lines' in file_result

        # Total should equal sum of parts
        assert file_result['total_lines'] == (
            file_result['code_lines'] +
            file_result['comment_lines'] +
            file_result['blank_lines']
        )

        # Code lines should be majority for this file
        assert file_result['code_lines'] > 0
        # Comment lines should exist (docstrings)
        assert file_result['comment_lines'] > 0

    def test_comment_detection_python(self, tmp_path, run_file_metrics):
        """Test Python comment detection (# and docstrings)."""
        test_file = tmp_path / 'comments.py'
        test_file.write_text('''"""
Module docstring.
Multi-line.
"""

# Single line comment
def func():
    """Function docstring."""
    return 1  # Inline comment (counted as code)

# Another comment
''')

        result = run_file_metrics(file_path=test_file)
        file_result = result['files'][0]

        # Should detect docstrings and # comments
        assert file_result['comment_lines'] >= 5  # Docstring lines + # comments

    def test_comment_detection_javascript(self, tmp_path, run_file_metrics):
        """Test JavaScript comment detection (// and /* */)."""
        test_file = tmp_path / 'comments.js'
        test_file.write_text('''/**
 * Multi-line comment
 * block.
 */

// Single line comment
function func() {
  return 1; // Inline comment (counted as code)
}

// Another comment
''')

        result = run_file_metrics(file_path=test_file)
        file_result = result['files'][0]

        # Should detect both // and /* */ comments
        assert file_result['comment_lines'] >= 5

    def test_blank_line_counting(self, tmp_path, run_file_metrics):
        """Test blank line counting."""
        test_file = tmp_path / 'blanks.py'
        test_file.write_text('''def func1():
    pass


def func2():
    pass


''')

        result = run_file_metrics(file_path=test_file)
        file_result = result['files'][0]

        # Should count blank lines (4 blank lines in this file)
        assert file_result['blank_lines'] >= 3


class TestElementCounting:
    """Test function and class counting."""

    def test_python_function_counting(self, run_file_metrics, python_fixtures_dir):
        """Test Python function counting."""
        fixture = python_fixtures_dir / 'moderate_complexity.py'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]

        # Should count functions
        assert 'functions' in file_result
        assert file_result['functions'] == 3  # validate_email, calculate_discount, process_items

    def test_python_class_counting(self, tmp_path, run_file_metrics):
        """Test Python class counting."""
        test_file = tmp_path / 'classes.py'
        test_file.write_text('''class ClassA:
    def method1(self):
        pass

class ClassB:
    def method2(self):
        pass
''')

        result = run_file_metrics(file_path=test_file)
        file_result = result['files'][0]

        # Should count classes
        assert file_result['classes'] == 2
        # Should count methods as functions
        assert file_result['functions'] == 2

    def test_javascript_function_counting(self, run_file_metrics, javascript_fixtures_dir):
        """Test JavaScript function counting."""
        fixture = javascript_fixtures_dir / 'simple_module.js'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]

        # Should count both regular and arrow functions
        assert file_result['functions'] >= 2  # greet and add

    def test_javascript_class_counting(self, run_file_metrics, javascript_fixtures_dir):
        """Test JavaScript class counting."""
        fixture = javascript_fixtures_dir / 'es6_features.js'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]

        # Should detect class
        assert file_result['classes'] >= 1  # UserManager class

    def test_import_counting_python(self, run_file_metrics, python_fixtures_dir):
        """Test Python import statement counting."""
        fixture = python_fixtures_dir / 'moderate_complexity.py'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]

        # Should count import statements
        assert 'imports' in file_result
        assert file_result['imports'] >= 1  # import re

    def test_import_counting_javascript(self, tmp_path, run_file_metrics):
        """Test JavaScript import statement counting."""
        test_file = tmp_path / 'imports.js'
        test_file.write_text('''import { foo } from 'bar';
import baz from 'qux';
const lib = require('library');
''')

        result = run_file_metrics(file_path=test_file)
        file_result = result['files'][0]

        # Should count import and require statements
        assert file_result['imports'] >= 3


class TestMultiLanguageSupport:
    """Test file metrics for different languages."""

    def test_python_detection(self, run_file_metrics, python_fixtures_dir):
        """Test Python language detection."""
        fixture = python_fixtures_dir / 'simple_function.py'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]
        assert file_result['language'] == 'python'

    def test_javascript_detection(self, run_file_metrics, javascript_fixtures_dir):
        """Test JavaScript language detection."""
        fixture = javascript_fixtures_dir / 'simple_module.js'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]
        assert file_result['language'] == 'javascript'

    def test_typescript_detection(self, run_file_metrics, typescript_fixtures_dir):
        """Test TypeScript language detection."""
        fixture = typescript_fixtures_dir / 'typed_module.ts'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]
        assert file_result['language'] == 'typescript'

    def test_directory_multi_language(self, tmp_path, run_file_metrics):
        """Test directory analysis with multiple languages."""
        # Create files in different languages
        (tmp_path / 'file.py').write_text('def func(): pass\n')
        (tmp_path / 'file.js').write_text('function func() {}\n')
        (tmp_path / 'file.ts').write_text('function func(): void {}\n')

        result = run_file_metrics(directory=tmp_path)

        languages = {f['language'] for f in result['files']}
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'typescript' in languages

    def test_language_filter(self, tmp_path, run_file_metrics):
        """Test language filter option."""
        # Create files in different languages
        (tmp_path / 'file.py').write_text('def func(): pass\n')
        (tmp_path / 'file.js').write_text('function func() {}\n')

        # Filter for Python only
        result = run_file_metrics(directory=tmp_path, language='python')

        # Should only have Python files
        assert len(result['files']) == 1
        assert result['files'][0]['language'] == 'python'


class TestSummaryStatistics:
    """Test summary statistics generation."""

    def test_summary_structure(self, run_file_metrics, python_fixtures_dir):
        """Test summary has required fields."""
        result = run_file_metrics(directory=python_fixtures_dir)

        assert 'summary' in result
        summary = result['summary']

        assert 'total_files' in summary
        assert 'total_lines' in summary
        assert 'total_code_lines' in summary
        assert 'total_comment_lines' in summary
        assert 'total_blank_lines' in summary
        assert 'total_functions' in summary
        assert 'total_classes' in summary
        assert 'average_file_size' in summary
        assert 'files_exceeding_limit' in summary

    def test_summary_totals(self, run_file_metrics, python_fixtures_dir):
        """Test summary totals match file data."""
        result = run_file_metrics(directory=python_fixtures_dir)

        summary = result['summary']
        files = result['files']

        # Total files should match
        assert summary['total_files'] == len(files)

        # Totals should be sums of individual files
        assert summary['total_lines'] == sum(f['total_lines'] for f in files)
        assert summary['total_code_lines'] == sum(f['code_lines'] for f in files)
        assert summary['total_comment_lines'] == sum(f['comment_lines'] for f in files)
        assert summary['total_blank_lines'] == sum(f['blank_lines'] for f in files)
        assert summary['total_functions'] == sum(f['functions'] for f in files)
        assert summary['total_classes'] == sum(f['classes'] for f in files)

    def test_average_file_size(self, run_file_metrics, python_fixtures_dir):
        """Test average file size calculation."""
        result = run_file_metrics(directory=python_fixtures_dir)

        summary = result['summary']
        files = result['files']

        # Calculate expected average
        expected_avg = sum(f['total_lines'] for f in files) / len(files)

        # Should match (allowing for rounding)
        assert abs(summary['average_file_size'] - expected_avg) < 0.5


class TestOutputFormat:
    """Test JSON output format and metadata."""

    def test_metadata_structure(self, run_file_metrics, python_fixtures_dir):
        """Test metadata in JSON output."""
        result = run_file_metrics(directory=python_fixtures_dir)

        assert 'metadata' in result
        metadata = result['metadata']

        assert 'schema_version' in metadata
        assert 'script_version' in metadata
        assert 'timestamp' in metadata
        assert 'execution_duration_ms' in metadata

        # Execution duration should be reasonable
        assert metadata['execution_duration_ms'] >= 0
        assert metadata['execution_duration_ms'] < 10000

    def test_file_result_structure(self, run_file_metrics, python_fixtures_dir):
        """Test file result has all required fields."""
        fixture = python_fixtures_dir / 'simple_function.py'
        result = run_file_metrics(file_path=fixture)

        file_result = result['files'][0]

        required_fields = [
            'path', 'language', 'total_lines', 'code_lines',
            'comment_lines', 'blank_lines', 'functions', 'classes',
            'imports', 'exceeds_size_limit', 'size_limit', 'recommendation'
        ]

        for field in required_fields:
            assert field in file_result, f"Missing required field: {field}"


class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_nonexistent_file(self, scripts_dir, tmp_path):
        """Test error handling for nonexistent file."""
        nonexistent = tmp_path / 'does_not_exist.py'

        result = subprocess.run(
            ['python3', str(scripts_dir / 'file_metrics.py'),
             '--file', str(nonexistent)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 1
        error_output = json.loads(result.stderr)
        assert 'error' in error_output

    def test_unsupported_file_extension(self, scripts_dir, tmp_path):
        """Test error for unsupported file extension."""
        unsupported = tmp_path / 'file.txt'
        unsupported.write_text('Some text')

        result = subprocess.run(
            ['python3', str(scripts_dir / 'file_metrics.py'),
             '--file', str(unsupported)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 1
        error_output = json.loads(result.stderr)
        assert 'error' in error_output
        assert 'unsupported' in error_output['error'].lower()

    def test_syntax_error_handling(self, tmp_path, run_file_metrics):
        """Test graceful handling of syntax errors."""
        bad_file = tmp_path / 'syntax_error.py'
        bad_file.write_text('def broken(\n')

        result = run_file_metrics(file_path=bad_file)

        # Should still return results (with 0 functions/classes due to parse error)
        file_result = result['files'][0]
        assert file_result['functions'] == 0
        assert file_result['classes'] == 0
        # But line counting should still work
        assert file_result['total_lines'] > 0

    def test_empty_directory(self, tmp_path, run_file_metrics):
        """Test handling of empty directory."""
        empty_dir = tmp_path / 'empty'
        empty_dir.mkdir()

        result = run_file_metrics(directory=empty_dir)

        # Should succeed with empty results
        assert result['summary']['total_files'] == 0
        assert result['files'] == []
