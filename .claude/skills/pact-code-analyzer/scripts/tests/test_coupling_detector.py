"""
Tests for coupling_detector.py

Tests cover:
- Fan-in/fan-out calculation
- Coupling threshold flags
- Detailed output mode
- Coupling recommendations
- Summary statistics
"""

import pytest
import json
import subprocess
from pathlib import Path


class TestFanInFanOut:
    """Test fan-in and fan-out calculations."""

    def test_basic_coupling_calculation(self, run_coupling_detector, python_fixtures_dir):
        """Test basic coupling metrics calculation."""
        result = run_coupling_detector(python_fixtures_dir, threshold=10, show_details=False)

        assert 'modules' in result
        modules = result['modules']
        assert len(modules) > 0

        # Each module should have coupling metrics
        for module in modules:
            assert 'path' in module
            assert 'outgoing_dependencies' in module
            assert 'incoming_dependencies' in module
            assert 'total_coupling' in module
            assert 'exceeds_threshold' in module

            # Coupling should be sum of incoming and outgoing
            assert module['total_coupling'] == (
                module['incoming_dependencies'] + module['outgoing_dependencies']
            )

    def test_detailed_fan_in_fan_out_lists(self, run_coupling_detector, python_fixtures_dir):
        """Test detailed fan-in/fan-out lists when --show-details flag is set."""
        result = run_coupling_detector(python_fixtures_dir, threshold=10, show_details=True)

        modules = result['modules']

        # With --show-details, should include fan_in and fan_out lists
        for module in modules:
            assert 'fan_in' in module
            assert 'fan_out' in module
            assert isinstance(module['fan_in'], list)
            assert isinstance(module['fan_out'], list)

            # Lists should match counts
            assert len(module['fan_in']) == module['incoming_dependencies']
            assert len(module['fan_out']) == module['outgoing_dependencies']

    def test_details_not_shown_by_default(self, run_coupling_detector, python_fixtures_dir):
        """Test that fan_in/fan_out lists not included without --show-details."""
        result = run_coupling_detector(python_fixtures_dir, threshold=10, show_details=False)

        modules = result['modules']

        # Without --show-details, should not include fan_in/fan_out lists
        for module in modules:
            assert 'fan_in' not in module
            assert 'fan_out' not in module

    def test_circular_dependencies_coupling(self, run_coupling_detector, python_fixtures_dir):
        """Test coupling detection for circular dependencies."""
        result = run_coupling_detector(python_fixtures_dir, threshold=10, show_details=True)

        modules_dict = {m['path']: m for m in result['modules']}

        # Find circular_import_a and circular_import_b
        circular_a_path = next((k for k in modules_dict.keys() if 'circular_import_a.py' in k), None)
        circular_b_path = next((k for k in modules_dict.keys() if 'circular_import_b.py' in k), None)

        if circular_a_path and circular_b_path:
            circular_a = modules_dict[circular_a_path]
            circular_b = modules_dict[circular_b_path]

            # circular_a imports circular_b (outgoing dependency)
            assert circular_a['outgoing_dependencies'] >= 1
            b_name_in_fan_out = any('circular_import_b.py' in dep for dep in circular_a['fan_out'])
            assert b_name_in_fan_out

            # circular_b is imported by circular_a (incoming dependency)
            assert circular_b['incoming_dependencies'] >= 1
            a_name_in_fan_in = any('circular_import_a.py' in dep for dep in circular_b['fan_in'])
            assert a_name_in_fan_in


class TestCouplingThresholds:
    """Test coupling threshold detection and flags."""

    def test_threshold_flag_detection(self, tmp_path, run_coupling_detector):
        """Test that modules exceeding threshold are flagged."""
        # Create a hub module that imports many others
        hub = tmp_path / 'hub.py'
        imports = '\n'.join([f'from module_{i} import func' for i in range(15)])
        hub.write_text(imports + '\n')

        # Create imported modules
        for i in range(15):
            module = tmp_path / f'module_{i}.py'
            module.write_text(f'def func(): pass\n')

        result = run_coupling_detector(tmp_path, threshold=10, show_details=False)

        modules_dict = {m['path']: m for m in result['modules']}
        hub_path = next((k for k in modules_dict.keys() if 'hub.py' in k), None)

        if hub_path:
            hub_module = modules_dict[hub_path]
            # Hub should have high outgoing dependencies (15)
            assert hub_module['outgoing_dependencies'] >= 15
            # Should exceed threshold of 10
            assert hub_module['exceeds_threshold'] is True

    def test_custom_threshold(self, run_coupling_detector, python_fixtures_dir):
        """Test custom threshold setting."""
        # Use low threshold (2)
        result = run_coupling_detector(python_fixtures_dir, threshold=2, show_details=False)

        # More modules should exceed low threshold
        exceeding_count = sum(1 for m in result['modules'] if m['exceeds_threshold'])
        assert exceeding_count >= 1  # At least circular imports should exceed

        # Summary should reflect this
        assert result['summary']['coupling_threshold'] == 2


class TestRecommendations:
    """Test coupling recommendations."""

    def test_high_fan_in_recommendation(self, tmp_path, run_coupling_detector):
        """Test recommendation for high fan-in (central module)."""
        # Create a central module imported by many others
        central = tmp_path / 'central.py'
        central.write_text('def shared_function(): pass\n')

        # Create multiple modules that import central
        for i in range(12):
            importer = tmp_path / f'importer_{i}.py'
            importer.write_text('from central import shared_function\n')

        result = run_coupling_detector(tmp_path, threshold=10, show_details=False)

        modules_dict = {m['path']: m for m in result['modules']}
        central_path = next((k for k in modules_dict.keys() if 'central.py' in k), None)

        if central_path:
            central_module = modules_dict[central_path]
            # Should have high fan-in
            assert central_module['incoming_dependencies'] >= 12
            assert central_module['exceeds_threshold'] is True

            # Should have recommendation about high fan-in
            assert 'recommendation' in central_module
            assert 'fan-in' in central_module['recommendation'].lower()
            assert 'stable' in central_module['recommendation'].lower() or \
                   'well-tested' in central_module['recommendation'].lower()

    def test_high_fan_out_recommendation(self, tmp_path, run_coupling_detector):
        """Test recommendation for high fan-out (depends on many modules)."""
        # Create a module that imports many others
        dependent = tmp_path / 'dependent.py'
        imports = '\n'.join([f'from module_{i} import func' for i in range(15)])
        dependent.write_text(imports + '\n')

        # Create imported modules
        for i in range(15):
            module = tmp_path / f'module_{i}.py'
            module.write_text(f'def func(): pass\n')

        result = run_coupling_detector(tmp_path, threshold=10, show_details=False)

        modules_dict = {m['path']: m for m in result['modules']}
        dependent_path = next((k for k in modules_dict.keys() if 'dependent.py' in k), None)

        if dependent_path:
            dependent_module = modules_dict[dependent_path]
            # Should have high fan-out
            assert dependent_module['outgoing_dependencies'] >= 15
            assert dependent_module['exceeds_threshold'] is True

            # Should have recommendation about high fan-out
            assert 'recommendation' in dependent_module
            assert 'fan-out' in dependent_module['recommendation'].lower()
            assert 'dependency injection' in dependent_module['recommendation'].lower() or \
                   'events' in dependent_module['recommendation'].lower() or \
                   'facades' in dependent_module['recommendation'].lower()


class TestSummaryStatistics:
    """Test summary statistics generation."""

    def test_summary_structure(self, run_coupling_detector, python_fixtures_dir):
        """Test summary has required fields."""
        result = run_coupling_detector(python_fixtures_dir, threshold=10, show_details=False)

        assert 'summary' in result
        summary = result['summary']

        assert 'total_modules' in summary
        assert 'average_coupling' in summary
        assert 'tightly_coupled_modules' in summary
        assert 'coupling_threshold' in summary
        assert 'top_coupled_modules' in summary

        # Values should be reasonable
        assert summary['total_modules'] >= 5  # We have multiple fixtures
        assert summary['average_coupling'] >= 0
        assert summary['coupling_threshold'] == 10

    def test_top_coupled_modules(self, run_coupling_detector, python_fixtures_dir):
        """Test top coupled modules list in summary."""
        result = run_coupling_detector(python_fixtures_dir, threshold=10, show_details=False)

        summary = result['summary']
        top_coupled = summary['top_coupled_modules']

        assert isinstance(top_coupled, list)
        assert len(top_coupled) <= 5  # Should limit to top 5

        # Each entry should have path and coupling
        for module in top_coupled:
            assert 'path' in module
            assert 'coupling' in module

        # Should be sorted by coupling (descending)
        if len(top_coupled) > 1:
            for i in range(len(top_coupled) - 1):
                assert top_coupled[i]['coupling'] >= top_coupled[i + 1]['coupling']

    def test_average_coupling_calculation(self, tmp_path, run_coupling_detector):
        """Test average coupling calculation."""
        # Create simple scenario with known coupling
        file_a = tmp_path / 'a.py'
        file_a.write_text('from b import func\n')

        file_b = tmp_path / 'b.py'
        file_b.write_text('def func(): pass\n')

        result = run_coupling_detector(tmp_path, threshold=10, show_details=False)

        summary = result['summary']
        modules = result['modules']

        # Calculate average manually
        total_coupling = sum(m['total_coupling'] for m in modules)
        expected_avg = total_coupling / len(modules)

        assert abs(summary['average_coupling'] - expected_avg) < 0.1  # Allow small rounding


class TestOutputFormat:
    """Test JSON output format and metadata."""

    def test_metadata_structure(self, run_coupling_detector, python_fixtures_dir):
        """Test metadata in JSON output."""
        result = run_coupling_detector(python_fixtures_dir, threshold=10, show_details=False)

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

    def test_empty_directory(self, tmp_path, run_coupling_detector):
        """Test handling of directory with no Python files."""
        # Create empty directory
        empty_dir = tmp_path / 'empty'
        empty_dir.mkdir()

        result = run_coupling_detector(empty_dir, threshold=10, show_details=False)

        # Should succeed with empty results
        assert result['summary']['total_modules'] == 0
        assert result['modules'] == []
        assert 'warning' in result or result['summary']['total_modules'] == 0

    def test_nonexistent_directory(self, scripts_dir, tmp_path):
        """Test error handling for nonexistent directory."""
        nonexistent = tmp_path / 'does_not_exist'

        result = subprocess.run(
            ['python3', str(scripts_dir / 'coupling_detector.py'),
             '--directory', str(nonexistent),
             '--threshold', '10'],
            capture_output=True,
            text=True
        )

        assert result.returncode == 1
        error_output = json.loads(result.stderr)
        assert 'error' in error_output


class TestOrphanModules:
    """Test handling of orphan modules in coupling analysis."""

    def test_orphan_module_zero_incoming(self, run_coupling_detector, python_fixtures_dir):
        """Test that orphan modules have zero incoming dependencies."""
        result = run_coupling_detector(python_fixtures_dir, threshold=10, show_details=False)

        modules_dict = {m['path']: m for m in result['modules']}
        standalone_path = next((k for k in modules_dict.keys() if 'standalone_module.py' in k), None)

        if standalone_path:
            standalone_module = modules_dict[standalone_path]
            # Orphan should have zero incoming dependencies
            assert standalone_module['incoming_dependencies'] == 0
            # May have outgoing dependencies (imports stdlib)
            # Total coupling should equal outgoing only
            assert standalone_module['total_coupling'] == standalone_module['outgoing_dependencies']
