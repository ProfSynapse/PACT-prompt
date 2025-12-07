"""
Tests for dependency_mapper.py

Tests cover:
- Circular dependency detection
- Orphan module identification
- Dependency graph output (JSON and DOT formats)
- Multi-language support
- Module detail generation
"""

import pytest
import json
import subprocess
from pathlib import Path


class TestCircularDependencies:
    """Test circular dependency detection."""

    def test_detect_circular_python(self, run_dependency_mapper, python_fixtures_dir):
        """Test detection of circular dependencies in Python."""
        result = run_dependency_mapper(python_fixtures_dir, 'python', detect_circular=True)

        # Should detect circular dependency between circular_import_a and circular_import_b
        assert 'circular_dependencies' in result

        circular_deps = result['circular_dependencies']
        assert len(circular_deps) > 0

        # Find the circular dependency involving our test files
        cycle_found = False
        for dep in circular_deps:
            cycle = dep['cycle']
            cycle_files = [Path(f).name for f in cycle]

            if 'circular_import_a.py' in cycle_files and 'circular_import_b.py' in cycle_files:
                cycle_found = True
                assert dep['severity'] in ['high', 'medium']
                break

        assert cycle_found, "Circular dependency between circular_import_a.py and circular_import_b.py not detected"

    def test_no_circular_deps_flag(self, run_dependency_mapper, python_fixtures_dir):
        """Test that circular deps not included when flag not set."""
        result = run_dependency_mapper(python_fixtures_dir, 'python', detect_circular=False)

        # circular_dependencies should not be in output when flag not set
        assert 'circular_dependencies' not in result or len(result.get('circular_dependencies', [])) == 0


class TestOrphanModules:
    """Test orphan module identification."""

    def test_detect_orphan_python(self, run_dependency_mapper, python_fixtures_dir):
        """Test detection of orphan modules in Python."""
        result = run_dependency_mapper(python_fixtures_dir, 'python', detect_circular=False)

        # Should identify standalone_module.py as orphan
        assert 'orphan_modules' in result

        orphans = result['orphan_modules']
        orphan_files = [Path(o).name for o in orphans]

        assert 'standalone_module.py' in orphan_files, \
            "standalone_module.py should be identified as orphan"

    def test_entry_points_not_orphans(self, tmp_path, run_dependency_mapper):
        """Test that entry point files are not flagged as orphans."""
        # Create main.py (entry point) that imports nothing
        main_file = tmp_path / 'main.py'
        main_file.write_text('def main():\n    print("Hello")\n')

        result = run_dependency_mapper(tmp_path, 'python', detect_circular=False)

        orphans = result.get('orphan_modules', [])
        orphan_files = [Path(o).name for o in orphans]

        # main.py should NOT be flagged as orphan (it's an entry point)
        assert 'main.py' not in orphan_files


class TestDependencyGraph:
    """Test dependency graph generation."""

    def test_json_graph_output(self, run_dependency_mapper, python_fixtures_dir):
        """Test JSON format dependency graph."""
        result = run_dependency_mapper(python_fixtures_dir, 'python', detect_circular=False)

        assert 'modules' in result
        modules = result['modules']
        assert isinstance(modules, list)

        # Each module should have expected structure
        for module in modules:
            assert 'path' in module
            assert 'imports' in module
            assert 'imported_by' in module
            assert 'is_orphan' in module

        # Find circular_import_a and verify it imports circular_import_b
        circular_a = next((m for m in modules if 'circular_import_a.py' in m['path']), None)
        if circular_a:
            import_files = [Path(imp).name for imp in circular_a['imports']]
            assert 'circular_import_b.py' in import_files

    def test_dot_graph_output(self, scripts_dir, python_fixtures_dir):
        """Test DOT format dependency graph output."""
        result = subprocess.run(
            ['python3', str(scripts_dir / 'dependency_mapper.py'),
             '--directory', str(python_fixtures_dir),
             '--language', 'python',
             '--output-graph', 'dot'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        dot_output = result.stdout

        # Should have DOT format structure
        assert 'digraph dependencies' in dot_output
        assert 'rankdir=LR' in dot_output
        assert '->' in dot_output  # Dependency arrows

        # Should include our test files
        assert 'circular_import_a.py' in dot_output or 'circular_import_b.py' in dot_output


class TestMultiLanguageSupport:
    """Test dependency mapping for different languages."""

    def test_javascript_dependencies(self, tmp_path, run_dependency_mapper):
        """Test JavaScript dependency detection."""
        # Create simple JS files with dependencies
        file_a = tmp_path / 'moduleA.js'
        file_a.write_text("const b = require('./moduleB');\n")

        file_b = tmp_path / 'moduleB.js'
        file_b.write_text("module.exports = { foo: 'bar' };\n")

        result = run_dependency_mapper(tmp_path, 'javascript', detect_circular=False)

        modules = result['modules']
        module_a = next((m for m in modules if 'moduleA.js' in m['path']), None)

        assert module_a is not None
        assert 'moduleB.js' in ' '.join(module_a['imports'])

    def test_typescript_dependencies(self, tmp_path, run_dependency_mapper):
        """Test TypeScript dependency detection."""
        # Create simple TS files with ES6 imports
        file_a = tmp_path / 'moduleA.ts'
        file_a.write_text("import { helper } from './moduleB';\n")

        file_b = tmp_path / 'moduleB.ts'
        file_b.write_text("export const helper = () => 'help';\n")

        result = run_dependency_mapper(tmp_path, 'typescript', detect_circular=False)

        modules = result['modules']
        module_a = next((m for m in modules if 'moduleA.ts' in m['path']), None)

        assert module_a is not None
        # Should detect import (may need relative path resolution)
        assert len(module_a['imports']) > 0 or 'moduleB.ts' in ' '.join(module_a['imports'])


class TestModuleDetails:
    """Test detailed module information."""

    def test_module_imports_and_imported_by(self, run_dependency_mapper, python_fixtures_dir):
        """Test module imports and imported_by lists."""
        result = run_dependency_mapper(python_fixtures_dir, 'python', detect_circular=False)

        modules = {m['path']: m for m in result['modules']}

        # circular_import_a should import circular_import_b
        circular_a_path = next((k for k in modules.keys() if 'circular_import_a.py' in k), None)
        if circular_a_path:
            circular_a = modules[circular_a_path]
            import_names = [Path(imp).name for imp in circular_a['imports']]
            assert 'circular_import_b.py' in import_names

            # circular_import_b should be imported by circular_import_a
            circular_b_path = next((k for k in modules.keys() if 'circular_import_b.py' in k), None)
            if circular_b_path:
                circular_b = modules[circular_b_path]
                imported_by_names = [Path(imp).name for imp in circular_b['imported_by']]
                assert 'circular_import_a.py' in imported_by_names

    def test_orphan_flag_in_modules(self, run_dependency_mapper, python_fixtures_dir):
        """Test is_orphan flag in module details."""
        result = run_dependency_mapper(python_fixtures_dir, 'python', detect_circular=False)

        modules = {m['path']: m for m in result['modules']}

        # standalone_module.py should be flagged as orphan
        standalone_path = next((k for k in modules.keys() if 'standalone_module.py' in k), None)
        if standalone_path:
            assert modules[standalone_path]['is_orphan'] is True

        # circular_import_a.py should NOT be orphan (imported by circular_import_b)
        circular_a_path = next((k for k in modules.keys() if 'circular_import_a.py' in k), None)
        if circular_a_path:
            assert modules[circular_a_path]['is_orphan'] is False


class TestSummaryStatistics:
    """Test summary statistics generation."""

    def test_summary_structure(self, run_dependency_mapper, python_fixtures_dir):
        """Test summary has required fields."""
        result = run_dependency_mapper(python_fixtures_dir, 'python', detect_circular=True)

        assert 'summary' in result
        summary = result['summary']

        assert 'total_modules' in summary
        assert 'total_dependencies' in summary
        assert 'circular_dependencies' in summary
        assert 'orphan_modules' in summary
        assert 'max_depth' in summary

        # Values should be reasonable
        assert summary['total_modules'] >= 5  # We have at least 5 test fixtures
        assert summary['circular_dependencies'] >= 1  # We have circular deps
        assert summary['orphan_modules'] >= 1  # We have standalone_module

    def test_max_depth_calculation(self, tmp_path, run_dependency_mapper):
        """Test maximum dependency depth calculation."""
        # Create chain: A -> B -> C
        file_a = tmp_path / 'a.py'
        file_a.write_text('from b import func_b\n')

        file_b = tmp_path / 'b.py'
        file_b.write_text('from c import func_c\n')

        file_c = tmp_path / 'c.py'
        file_c.write_text('def func_c(): pass\n')

        result = run_dependency_mapper(tmp_path, 'python', detect_circular=False)

        summary = result['summary']
        # Depth should be at least 2 (A -> B -> C has depth 2)
        assert summary['max_depth'] >= 2


class TestOutputFormat:
    """Test JSON output format and metadata."""

    def test_metadata_structure(self, run_dependency_mapper, python_fixtures_dir):
        """Test metadata in JSON output."""
        result = run_dependency_mapper(python_fixtures_dir, 'python', detect_circular=False)

        assert 'metadata' in result
        metadata = result['metadata']

        assert 'schema_version' in metadata
        assert 'script_version' in metadata
        assert 'timestamp' in metadata
        assert 'execution_duration_ms' in metadata

        # Execution duration should be reasonable
        assert metadata['execution_duration_ms'] >= 0
        assert metadata['execution_duration_ms'] < 10000


class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_nonexistent_directory(self, scripts_dir, tmp_path):
        """Test error handling for nonexistent directory."""
        nonexistent = tmp_path / 'does_not_exist'

        result = subprocess.run(
            ['python3', str(scripts_dir / 'dependency_mapper.py'),
             '--directory', str(nonexistent),
             '--language', 'python'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 1
        error_output = json.loads(result.stderr)
        assert 'error' in error_output

    def test_syntax_error_in_file(self, tmp_path, run_dependency_mapper):
        """Test graceful handling of syntax errors in files."""
        # Create file with syntax error
        bad_file = tmp_path / 'bad.py'
        bad_file.write_text('def broken(\n')

        # Should not crash, should include error/warning
        result = run_dependency_mapper(tmp_path, 'python', detect_circular=False)

        # Should succeed but may have errors list
        assert 'summary' in result
        # May have empty or partial results due to syntax error
        assert 'modules' in result
