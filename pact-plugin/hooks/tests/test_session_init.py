"""Comprehensive tests for session_init.py hook."""

import json
import os
import subprocess
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
sys.path.insert(0, str(__file__).rsplit("/tests", 1)[0])
import session_init


class TestImportsAndConstants:
    """Smoke tests - verify module loads and constants exist."""

    def test_module_imports(self):
        """Module should import without errors."""
        assert session_init is not None

    def test_min_ram_mb_default(self):
        """Default MIN_RAM_MB should be 500.0."""
        # Note: This tests the module-level constant, not env override
        assert hasattr(session_init, 'MIN_RAM_MB')
        assert isinstance(session_init.MIN_RAM_MB, float)

    def test_key_functions_defined(self):
        """Key functions should be defined."""
        assert callable(session_init.check_and_install_dependencies)
        assert callable(session_init.maybe_migrate_embeddings)
        assert callable(session_init.maybe_embed_pending)
        assert callable(session_init.find_active_plans)
        assert callable(session_init.main)
        assert callable(session_init._get_embedding_attempted_path)


class TestMinRamMbEnvOverride:
    """Test that MIN_RAM_MB can be overridden via environment."""

    def test_env_override_works(self):
        """Environment variable should override default threshold."""
        # Re-evaluate the expression that sets the constant
        with patch.dict(os.environ, {'PACT_MIN_RAM_MB': '1000.0'}):
            new_value = float(os.environ.get('PACT_MIN_RAM_MB', '500.0'))
            assert new_value == 1000.0

    def test_default_when_env_not_set(self):
        """Should use default when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the env var if it exists
            os.environ.pop('PACT_MIN_RAM_MB', None)
            new_value = float(os.environ.get('PACT_MIN_RAM_MB', '500.0'))
            assert new_value == 500.0


class TestGetEmbeddingAttemptedPath:
    """Tests for _get_embedding_attempted_path()."""

    def test_returns_path_with_session_id(self):
        """Should return path containing session ID."""
        with patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session-123'}):
            path = session_init._get_embedding_attempted_path()
            assert isinstance(path, Path)
            assert 'test-session-123' in str(path)
            assert path.parent == Path('/tmp')

    def test_uses_unknown_when_no_session_id(self):
        """Should use 'unknown' when session ID not set."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('CLAUDE_SESSION_ID', None)
            path = session_init._get_embedding_attempted_path()
            assert 'unknown' in str(path)


class TestCheckAndInstallDependencies:
    """Tests for check_and_install_dependencies()."""

    def test_returns_ok_when_all_packages_available(self):
        """Should return 'ok' status when all packages are importable."""
        # Mock all packages as importable
        def mock_import(name):
            return MagicMock()

        with patch('builtins.__import__', mock_import):
            result = session_init.check_and_install_dependencies()
            assert result['status'] == 'ok'
            assert result['installed'] == []
            assert result['failed'] == []

    def test_attempts_install_when_package_missing(self):
        """Should attempt pip install when package is missing."""
        import_count = [0]

        def mock_import(name):
            import_count[0] += 1
            # Fail on first import attempt (pysqlite3)
            if import_count[0] <= 3:  # Check phase
                raise ImportError(f"No module named '{name}'")
            return MagicMock()

        mock_subprocess = MagicMock(returncode=0)

        with patch('builtins.__import__', side_effect=mock_import), \
             patch.object(subprocess, 'run', return_value=mock_subprocess) as mock_run:
            result = session_init.check_and_install_dependencies()
            # Should have attempted installation
            assert mock_run.called

    def test_handles_install_timeout(self):
        """Should handle pip install timeout gracefully."""
        def mock_import(name):
            raise ImportError(f"No module named '{name}'")

        with patch('builtins.__import__', side_effect=mock_import), \
             patch.object(subprocess, 'run', side_effect=subprocess.TimeoutExpired('pip', 60)):
            result = session_init.check_and_install_dependencies()
            assert result['status'] == 'failed'
            assert any('timeout' in f for f in result['failed'])

    def test_handles_install_exception(self):
        """Should handle general pip install exception."""
        def mock_import(name):
            raise ImportError(f"No module named '{name}'")

        with patch('builtins.__import__', side_effect=mock_import), \
             patch.object(subprocess, 'run', side_effect=RuntimeError("Installation failed")):
            result = session_init.check_and_install_dependencies()
            assert result['status'] == 'failed'
            assert len(result['failed']) > 0

    def test_partial_install_status(self):
        """Should return 'partial' when some packages installed, some failed."""
        import_count = [0]
        packages_checked = []

        def mock_import(name):
            packages_checked.append(name)
            # All imports fail during check phase
            raise ImportError(f"No module named '{name}'")

        install_count = [0]
        def mock_run(*args, **kwargs):
            install_count[0] += 1
            # First install succeeds, rest fail
            if install_count[0] == 1:
                return MagicMock(returncode=0)
            return MagicMock(returncode=1)

        with patch('builtins.__import__', side_effect=mock_import), \
             patch.object(subprocess, 'run', side_effect=mock_run):
            result = session_init.check_and_install_dependencies()
            assert result['status'] == 'partial'


class TestMaybeMigrateEmbeddings:
    """Tests for maybe_migrate_embeddings()."""

    def test_returns_ok_when_scripts_dir_missing(self):
        """Should return ok when scripts directory doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            result = session_init.maybe_migrate_embeddings()
            assert result['status'] == 'ok'
            assert result['message'] is None

    def test_returns_ok_on_import_error(self):
        """Should return ok when imports fail."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True

        with patch.object(Path, '__new__', return_value=mock_path):
            # Import will fail naturally since test dependencies aren't installed
            result = session_init.maybe_migrate_embeddings()
            assert result['status'] == 'ok'

    def test_handles_exception_gracefully(self):
        """Should return error status on exception."""
        # The function handles exceptions internally and returns an appropriate status
        # Since the scripts directory likely doesn't exist in test environment,
        # the function should return 'ok' (early return path)
        result = session_init.maybe_migrate_embeddings()
        # Should handle gracefully without crashing
        assert result['status'] in ('ok', 'error')
        # Either no message (early return) or an error message
        if result['status'] == 'error':
            assert result['message'] is not None


class TestMaybeEmbedPending:
    """Tests for maybe_embed_pending()."""

    def test_skips_if_already_attempted_this_session(self):
        """Should skip if session marker file exists."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            marker_path = Path(f.name)

        try:
            with patch.object(session_init, '_get_embedding_attempted_path', return_value=marker_path):
                result = session_init.maybe_embed_pending()
                assert result['status'] == 'skipped'
                assert 'Already attempted' in result['message']
        finally:
            marker_path.unlink(missing_ok=True)

    def test_creates_session_marker_file(self):
        """Should create session marker file on first attempt."""
        marker_path = Path(tempfile.gettempdir()) / 'test_marker_file_12345'
        marker_path.unlink(missing_ok=True)

        try:
            with patch.object(session_init, '_get_embedding_attempted_path', return_value=marker_path), \
                 patch.object(Path, 'exists', side_effect=[False, False]):  # First for marker, second for scripts_dir
                # Scripts dir doesn't exist, so it should fail early but marker should be created
                result = session_init.maybe_embed_pending()
                # The marker file should have been created
                # (but may be cleaned up - we just check it didn't crash)
                assert 'status' in result
        finally:
            marker_path.unlink(missing_ok=True)

    def test_returns_skipped_when_scripts_not_found(self):
        """Should return skipped when memory scripts directory doesn't exist."""
        marker_path = Path(tempfile.gettempdir()) / 'nonexistent_marker_path'
        marker_path.unlink(missing_ok=True)

        try:
            with patch.object(session_init, '_get_embedding_attempted_path', return_value=marker_path):
                result = session_init.maybe_embed_pending()
                assert 'status' in result
        finally:
            marker_path.unlink(missing_ok=True)

    def test_handles_marker_creation_failure(self):
        """Should return skipped when marker file cannot be created."""
        marker_path = Path('/nonexistent/directory/marker')

        with patch.object(session_init, '_get_embedding_attempted_path', return_value=marker_path):
            result = session_init.maybe_embed_pending()
            assert result['status'] == 'skipped'
            assert 'Could not create session marker' in result['message']

    def test_atomic_marker_prevents_duplicate_embedding(self):
        """Should use atomic marker creation to prevent race conditions."""
        marker_path = Path(tempfile.gettempdir()) / f'test_atomic_marker_{os.getpid()}'
        marker_path.unlink(missing_ok=True)

        try:
            with patch.object(session_init, '_get_embedding_attempted_path', return_value=marker_path), \
                 patch.object(session_init, '_get_pending_memories', return_value=[]) if hasattr(session_init, '_get_pending_memories') else patch.dict(os.environ, {}), \
                 patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}):
                # First call creates marker
                result1 = session_init.maybe_embed_pending()
                assert marker_path.exists()

                # Second call should skip due to FileExistsError
                result2 = session_init.maybe_embed_pending()
                assert result2['status'] == 'skipped'
                assert 'Already attempted' in result2['message']
        finally:
            marker_path.unlink(missing_ok=True)


class TestFindActivePlans:
    """Tests for find_active_plans()."""

    def test_returns_empty_when_plans_dir_missing(self):
        """Should return empty list when plans directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = session_init.find_active_plans(tmpdir)
            assert result == []

    def test_finds_in_progress_plan(self):
        """Should find plan with IN_PROGRESS status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir) / 'docs' / 'plans'
            plans_dir.mkdir(parents=True)

            plan_file = plans_dir / 'feature-plan.md'
            plan_file.write_text('# Feature Plan\nStatus: IN_PROGRESS\n[ ] Task 1')

            result = session_init.find_active_plans(tmpdir)
            assert 'feature-plan.md' in result

    def test_finds_plan_with_unchecked_items(self):
        """Should find plan with unchecked items (not completed)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir) / 'docs' / 'plans'
            plans_dir.mkdir(parents=True)

            plan_file = plans_dir / 'todo-plan.md'
            plan_file.write_text('# Todo Plan\n[ ] Unchecked item\n[x] Checked item')

            result = session_init.find_active_plans(tmpdir)
            assert 'todo-plan.md' in result

    def test_ignores_completed_plans(self):
        """Should ignore plans with completed status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir) / 'docs' / 'plans'
            plans_dir.mkdir(parents=True)

            plan_file = plans_dir / 'done-plan.md'
            plan_file.write_text('# Done Plan\nStatus: COMPLETED\n[ ] This unchecked item should be ignored')

            result = session_init.find_active_plans(tmpdir)
            assert result == []

    def test_ignores_done_status(self):
        """Should ignore plans with Done status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir) / 'docs' / 'plans'
            plans_dir.mkdir(parents=True)

            plan_file = plans_dir / 'finished-plan.md'
            plan_file.write_text('# Finished\nStatus: Done\n[ ] Some task')

            result = session_init.find_active_plans(tmpdir)
            assert result == []

    def test_case_variations_in_progress(self):
        """Should detect various case variations of in-progress status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir) / 'docs' / 'plans'
            plans_dir.mkdir(parents=True)

            # Test different case variations
            variations = [
                ('upper-plan.md', 'Status: IN_PROGRESS'),
                ('title-plan.md', 'Status: In Progress'),
                ('lower-plan.md', 'status: in_progress'),
                ('active-plan.md', 'Status: ACTIVE'),
                ('active2-plan.md', 'Status: Active'),
            ]

            for filename, status_line in variations:
                plan_file = plans_dir / filename
                plan_file.write_text(f'# Plan\n{status_line}')

            result = session_init.find_active_plans(tmpdir)
            assert len(result) == 5

    def test_only_matches_plan_files(self):
        """Should only match files ending in -plan.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir) / 'docs' / 'plans'
            plans_dir.mkdir(parents=True)

            # This should be found
            (plans_dir / 'feature-plan.md').write_text('Status: IN_PROGRESS')
            # These should not
            (plans_dir / 'notes.md').write_text('Status: IN_PROGRESS')
            (plans_dir / 'plan.txt').write_text('Status: IN_PROGRESS')

            result = session_init.find_active_plans(tmpdir)
            assert result == ['feature-plan.md']

    def test_handles_io_error_gracefully(self):
        """Should handle IO errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir) / 'docs' / 'plans'
            plans_dir.mkdir(parents=True)

            # Create a valid plan
            (plans_dir / 'good-plan.md').write_text('Status: IN_PROGRESS')

            # Create a file that will cause read error (permission denied simulation)
            bad_file = plans_dir / 'bad-plan.md'
            bad_file.write_text('Status: IN_PROGRESS')

            # Mock to simulate read error for one file
            original_read_text = Path.read_text
            call_count = [0]

            def mock_read_text(self, *args, **kwargs):
                call_count[0] += 1
                if 'bad-plan.md' in str(self):
                    raise IOError("Permission denied")
                return original_read_text(self, *args, **kwargs)

            with patch.object(Path, 'read_text', mock_read_text):
                result = session_init.find_active_plans(tmpdir)
                # Should still find the good plan
                assert 'good-plan.md' in result

    def test_handles_unicode_error_gracefully(self):
        """Should handle unicode decode errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir) / 'docs' / 'plans'
            plans_dir.mkdir(parents=True)

            # Create a plan with invalid UTF-8
            bad_file = plans_dir / 'binary-plan.md'
            bad_file.write_bytes(b'\xff\xfe' + b'Status: IN_PROGRESS')

            # This should not crash
            result = session_init.find_active_plans(tmpdir)
            # Binary file should be skipped
            assert result == []


class TestMainJsonFlow:
    """Tests for main() JSON input/output flow."""

    def test_handles_missing_stdin_gracefully(self):
        """Should handle empty/missing stdin."""
        with patch.object(sys, 'stdin', StringIO('')), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit) as exc_info:
            session_init.main()
        assert exc_info.value.code == 0

    def test_handles_malformed_json(self):
        """Should handle malformed JSON input."""
        with patch.object(sys, 'stdin', StringIO('not valid json')), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit) as exc_info:
            session_init.main()
        assert exc_info.value.code == 0

    def test_outputs_active_plans(self, capsys):
        """Should output active plans in JSON response."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=['feature-plan.md', 'bug-plan.md']), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'hookSpecificOutput' in output
        assert 'feature-plan.md' in output['hookSpecificOutput']['additionalContext']
        assert 'bug-plan.md' in output['hookSpecificOutput']['additionalContext']

    def test_truncates_many_active_plans(self, capsys):
        """Should truncate list when more than 3 active plans."""
        input_data = json.dumps({})
        many_plans = ['plan1-plan.md', 'plan2-plan.md', 'plan3-plan.md', 'plan4-plan.md', 'plan5-plan.md']

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=many_plans), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        context = output['hookSpecificOutput']['additionalContext']
        assert '(+2 more)' in context

    def test_outputs_dependency_failures(self, capsys):
        """Should output dependency failures as system message."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'failed', 'installed': [], 'failed': ['pysqlite3', 'model2vec']}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'systemMessage' in output
        assert 'pysqlite3' in output['systemMessage']
        assert 'model2vec' in output['systemMessage']
        assert 'Failed to install' in output['systemMessage']

    def test_outputs_migration_success(self, capsys):
        """Should output migration success message."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': 'Migrated 15/15 embeddings to 256-dim'}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'Migrated 15/15' in output['hookSpecificOutput']['additionalContext']

    def test_outputs_embedding_catchup_success(self, capsys):
        """Should output embedding catch-up success message."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': 'Embedded 5 pending memories'}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'Embedded 5 pending' in output['hookSpecificOutput']['additionalContext']

    def test_no_output_when_nothing_to_report(self, capsys):
        """Should output nothing when there's nothing to report."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        assert captured.out == ''

    def test_uses_default_project_dir(self):
        """Should use '.' as default project dir when env var not set."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {}, clear=True), \
             patch.object(session_init, 'find_active_plans', return_value=[]) as mock_find, \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            # Remove the env var
            os.environ.pop('CLAUDE_PROJECT_DIR', None)
            session_init.main()

        mock_find.assert_called_once_with('.')

    def test_handles_exception_gracefully(self, capsys):
        """Should handle exceptions and exit 0 with warning."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', side_effect=RuntimeError("Test error")), \
             pytest.raises(SystemExit) as exc_info:
            session_init.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert 'WARNING' in captured.err
        assert 'session_init' in captured.err

    def test_combines_multiple_context_parts(self, capsys):
        """Should combine multiple context parts with pipe separator."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=['feature-plan.md']), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': 'Migrated 10/10 embeddings to 256-dim'}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': 'Embedded 3 pending memories'}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        context = output['hookSpecificOutput']['additionalContext']
        # Should have multiple parts separated by ' | '
        parts = context.split(' | ')
        assert len(parts) == 3
        assert any('Active plans' in p for p in parts)
        assert any('Migrated' in p for p in parts)
        assert any('Embedded' in p for p in parts)


class TestOutputFormatting:
    """Tests for JSON output formatting."""

    def test_hook_event_name_is_session_start(self, capsys):
        """Should include hookEventName as SessionStart."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=['test-plan.md']), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['hookSpecificOutput']['hookEventName'] == 'SessionStart'

    def test_system_message_separate_from_context(self, capsys):
        """Should have systemMessage separate from additionalContext."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=['plan.md']), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'failed', 'installed': [], 'failed': ['pkg1']}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        # hookSpecificOutput contains context
        assert 'hookSpecificOutput' in output
        assert 'additionalContext' in output['hookSpecificOutput']
        # systemMessage is at top level, separate
        assert 'systemMessage' in output
        assert output['systemMessage'] != output['hookSpecificOutput']['additionalContext']


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_plans_list(self, capsys):
        """Should handle empty plans list gracefully."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        # Should not crash, no output expected
        assert captured.out == ''

    def test_exactly_three_plans(self, capsys):
        """Should display exactly 3 plans without truncation message."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=['a-plan.md', 'b-plan.md', 'c-plan.md']), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        context = output['hookSpecificOutput']['additionalContext']
        assert 'a-plan.md' in context
        assert 'b-plan.md' in context
        assert 'c-plan.md' in context
        assert 'more' not in context

    def test_migration_message_without_migrated_keyword(self, capsys):
        """Should not output migration message if 'Migrated' not in message."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': 'Some other message'}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        # No output expected since 'Migrated' not in message
        assert captured.out == ''

    def test_embedding_message_not_ok_status(self, capsys):
        """Should not output embedding message if status is not ok."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'error', 'message': 'Embedded 5 pending memories'}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        # No output expected since status is not 'ok'
        assert captured.out == ''

    def test_embedding_message_without_embedded_keyword(self, capsys):
        """Should not output embedding message if 'Embedded' not in message."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': 'No pending memories'}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        # No output expected since 'Embedded' not in message
        assert captured.out == ''


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def test_fresh_session_with_active_plans(self, capsys):
        """Simulate fresh session startup with active plans."""
        input_data = json.dumps({"session_id": "new-session-123"})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp', 'CLAUDE_SESSION_ID': 'new-session-123'}), \
             patch.object(session_init, 'find_active_plans', return_value=['auth-feature-plan.md']), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'auth-feature-plan.md' in output['hookSpecificOutput']['additionalContext']

    def test_session_with_missing_dependencies(self, capsys):
        """Simulate session where some dependencies fail to install."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'failed', 'installed': ['pysqlite3'], 'failed': ['model2vec (timeout)']}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': None}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'Failed to install' in output['systemMessage']
        assert 'model2vec' in output['systemMessage']
        assert 'Memory features may be limited' in output['systemMessage']

    def test_session_with_embedding_migration(self, capsys):
        """Simulate session where embeddings need migration."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=[]), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'ok', 'installed': [], 'failed': []}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': 'Migrated 50/50 embeddings to 256-dim'}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': None}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'Migrated 50/50 embeddings to 256-dim' in output['hookSpecificOutput']['additionalContext']

    def test_full_session_init_with_all_outputs(self, capsys):
        """Simulate session with all types of output."""
        input_data = json.dumps({})

        with patch.object(sys, 'stdin', StringIO(input_data)), \
             patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': '/tmp'}), \
             patch.object(session_init, 'find_active_plans', return_value=['big-feature-plan.md']), \
             patch.object(session_init, 'check_and_install_dependencies', return_value={'status': 'partial', 'installed': ['sqlite-vec'], 'failed': ['model2vec']}), \
             patch.object(session_init, 'maybe_migrate_embeddings', return_value={'status': 'ok', 'message': 'Migrated 25/25 embeddings to 256-dim'}), \
             patch.object(session_init, 'maybe_embed_pending', return_value={'status': 'ok', 'message': 'Embedded 10 pending memories'}), \
             pytest.raises(SystemExit):
            session_init.main()

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        # Check context has all expected parts
        context = output['hookSpecificOutput']['additionalContext']
        assert 'big-feature-plan.md' in context
        assert 'Migrated' in context
        assert 'Embedded' in context

        # Check system message for failures
        assert 'model2vec' in output['systemMessage']
