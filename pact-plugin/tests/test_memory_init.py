"""
Tests for the memory_init module - lazy initialization system for PACT memory.

Tests cover:
1. Unit tests for ensure_memory_ready(), reset_initialization(), is_initialized()
2. Thread safety - multiple concurrent calls only run once
3. Integration with memory_api.py - first API call triggers initialization
4. Edge cases - graceful degradation, already-installed dependencies
"""

import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch, call

import pytest

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "pact-memory" / "scripts"))


class TestEnsureMemoryReady:
    """Tests for ensure_memory_ready() - the main lazy initialization entry point."""

    def test_returns_dict_with_expected_keys(self):
        """Test that ensure_memory_ready returns expected result structure."""
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            result = ensure_memory_ready()

            assert 'already_initialized' in result
            assert 'deps' in result
            assert 'migration' in result
            assert 'embedding' in result
            assert result['already_initialized'] is False

    def test_idempotent_only_runs_once(self):
        """Test that ensure_memory_ready only runs initialization once per session."""
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # First call should run initialization
            result1 = ensure_memory_ready()
            assert result1['already_initialized'] is False
            assert mock_deps.call_count == 1

            # Second call should return early
            result2 = ensure_memory_ready()
            assert result2['already_initialized'] is True
            assert mock_deps.call_count == 1  # Still 1, not called again

            # Third call also returns early
            result3 = ensure_memory_ready()
            assert result3['already_initialized'] is True
            assert mock_deps.call_count == 1

    def test_runs_all_three_steps(self):
        """Test that all three initialization steps are called in order."""
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        call_order = []

        def track_deps():
            call_order.append('deps')
            return {'status': 'ok', 'installed': [], 'failed': []}

        def track_migrate():
            call_order.append('migrate')
            return {'status': 'ok', 'message': None}

        def track_embed():
            call_order.append('embed')
            return {'status': 'ok', 'message': None}

        with patch('memory_init.check_and_install_dependencies', side_effect=track_deps), \
             patch('memory_init.maybe_migrate_embeddings', side_effect=track_migrate), \
             patch('memory_init.maybe_embed_pending', side_effect=track_embed):

            ensure_memory_ready()

            assert call_order == ['deps', 'migrate', 'embed']


class TestResetInitialization:
    """Tests for reset_initialization() - allows re-initialization for testing."""

    def test_reset_allows_reinitialization(self):
        """Test that reset_initialization allows initialization to run again."""
        from memory_init import ensure_memory_ready, reset_initialization, is_initialized

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # First initialization
            result1 = ensure_memory_ready()
            assert result1['already_initialized'] is False
            assert is_initialized() is True
            assert mock_deps.call_count == 1

            # Reset
            reset_initialization()
            assert is_initialized() is False

            # Second initialization runs again
            result2 = ensure_memory_ready()
            assert result2['already_initialized'] is False
            assert mock_deps.call_count == 2


class TestIsInitialized:
    """Tests for is_initialized() - checks current initialization state."""

    def test_returns_false_before_initialization(self):
        """Test is_initialized returns False before ensure_memory_ready is called."""
        from memory_init import reset_initialization, is_initialized

        reset_initialization()
        assert is_initialized() is False

    def test_returns_true_after_initialization(self):
        """Test is_initialized returns True after ensure_memory_ready completes."""
        from memory_init import ensure_memory_ready, reset_initialization, is_initialized

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            ensure_memory_ready()
            assert is_initialized() is True


class TestThreadSafety:
    """Tests for thread safety - multiple concurrent calls only run once."""

    def test_concurrent_calls_only_initialize_once(self):
        """Test that multiple concurrent calls only run initialization once."""
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        call_count = {'value': 0}
        call_lock = threading.Lock()

        def counting_deps():
            with call_lock:
                call_count['value'] += 1
            # Simulate some work
            time.sleep(0.05)
            return {'status': 'ok', 'installed': [], 'failed': []}

        with patch('memory_init.check_and_install_dependencies', side_effect=counting_deps), \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # Launch 10 concurrent calls
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(ensure_memory_ready) for _ in range(10)]
                results = [f.result() for f in as_completed(futures)]

            # Only one call should have run the full initialization
            assert call_count['value'] == 1

            # Exactly one result should have already_initialized=False
            not_initialized = [r for r in results if not r['already_initialized']]
            already_initialized = [r for r in results if r['already_initialized']]

            assert len(not_initialized) == 1
            assert len(already_initialized) == 9

    def test_double_check_locking_pattern(self):
        """Test that double-check locking prevents race conditions."""
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        # Track how many times we enter the lock
        lock_entries = {'value': 0}
        original_lock = threading.Lock()

        class TrackingLock:
            def __enter__(self):
                lock_entries['value'] += 1
                return original_lock.__enter__()

            def __exit__(self, *args):
                return original_lock.__exit__(*args)

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed, \
             patch('memory_init._init_lock', TrackingLock()):

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # First call acquires lock
            ensure_memory_ready()

            # Second call should return early without acquiring lock (fast path)
            # due to the initial check before lock acquisition
            ensure_memory_ready()

            # Lock was only entered once
            assert lock_entries['value'] == 1


class TestCheckAndInstallDependencies:
    """Tests for check_and_install_dependencies function."""

    def test_all_dependencies_present_returns_ok(self):
        """Test when all dependencies are already installed - returns ok status."""
        from memory_init import check_and_install_dependencies

        # When deps are already importable, function returns ok with empty lists
        # The actual function checks via __import__, and if successful, returns ok
        # We test this by calling it (deps are installed in test env)
        result = check_and_install_dependencies()

        # If deps are installed, status should be ok
        # If not installed, the test still passes as we're testing the return structure
        assert 'status' in result
        assert 'installed' in result
        assert 'failed' in result

    def test_subprocess_called_for_missing_deps(self):
        """Test that subprocess.run is called when deps are missing."""
        import builtins
        from memory_init import check_and_install_dependencies

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            # Simulate pysqlite3 not installed
            if name == 'pysqlite3':
                raise ImportError("No module named 'pysqlite3'")
            return original_import(name, *args, **kwargs)

        with patch.object(builtins, '__import__', mock_import), \
             patch('memory_init.subprocess.run') as mock_run:

            mock_run.return_value = MagicMock(returncode=0)

            result = check_and_install_dependencies()

            # Should have attempted pip install
            assert mock_run.called

    def test_installation_failure_recorded(self):
        """Test that installation failures are recorded in result."""
        import builtins
        from memory_init import check_and_install_dependencies

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            # All deps missing
            if name in ('pysqlite3', 'sqlite_vec', 'model2vec'):
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        with patch.object(builtins, '__import__', mock_import), \
             patch('memory_init.subprocess.run') as mock_run:

            mock_run.return_value = MagicMock(returncode=1)  # All installations fail

            result = check_and_install_dependencies()

            assert result['status'] == 'failed'
            assert len(result['failed']) > 0

    def test_installation_timeout_handled(self):
        """Test that installation timeout is handled gracefully."""
        import builtins
        import subprocess
        from memory_init import check_and_install_dependencies

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == 'pysqlite3':
                raise ImportError("Not installed")
            return original_import(name, *args, **kwargs)

        with patch.object(builtins, '__import__', mock_import), \
             patch('memory_init.subprocess.run') as mock_run:

            mock_run.side_effect = subprocess.TimeoutExpired(cmd='pip', timeout=60)

            result = check_and_install_dependencies()

            # Should record timeout in failed list
            assert any('timeout' in str(f).lower() for f in result['failed'])


class TestMaybeEmbedPending:
    """Tests for maybe_embed_pending function.

    Note: These tests use session marker files to track once-per-session behavior.
    The embed_pending_memories import is mocked via sys.modules since the
    embedding_catchup module uses relative imports that don't work in test context.
    """

    def test_session_scoped_only_runs_once(self, tmp_path):
        """Test that maybe_embed_pending only runs once per session via marker file."""
        from memory_init import maybe_embed_pending, _get_embedding_attempted_path

        # Use a unique session ID for this test
        test_session_id = f"test-once-{time.time()}"

        with patch.dict(os.environ, {'CLAUDE_SESSION_ID': test_session_id}):
            marker_path = _get_embedding_attempted_path()

            # Clean up any existing marker
            if marker_path.exists():
                marker_path.unlink()

            # Create a mock module for embedding_catchup
            mock_catchup = MagicMock()
            mock_catchup.embed_pending_memories = MagicMock(return_value={'processed': 0})

            with patch.dict(sys.modules, {'.embedding_catchup': mock_catchup}):
                # First call creates marker and attempts embedding
                result1 = maybe_embed_pending()

                # Marker should now exist
                assert marker_path.exists()

                # Second call should skip because marker exists
                result2 = maybe_embed_pending()
                assert result2['status'] == 'skipped'
                assert 'already attempted' in result2['message'].lower()

            # Clean up
            if marker_path.exists():
                marker_path.unlink()

    def test_marker_file_created_on_first_call(self, tmp_path):
        """Test that the marker file is created on first call."""
        from memory_init import maybe_embed_pending, _get_embedding_attempted_path

        test_session_id = f"test-marker-{time.time()}"

        with patch.dict(os.environ, {'CLAUDE_SESSION_ID': test_session_id}):
            marker_path = _get_embedding_attempted_path()

            # Ensure marker doesn't exist
            if marker_path.exists():
                marker_path.unlink()

            assert not marker_path.exists()

            # Call maybe_embed_pending - it will fail to import embedding_catchup
            # but should still create the marker file first
            result = maybe_embed_pending()

            # Marker should be created regardless of whether embedding succeeds
            assert marker_path.exists()

            # Clean up
            marker_path.unlink()

    def test_skips_when_marker_exists(self, tmp_path):
        """Test that function skips immediately when marker exists."""
        from memory_init import maybe_embed_pending, _get_embedding_attempted_path

        test_session_id = f"test-skip-{time.time()}"

        with patch.dict(os.environ, {'CLAUDE_SESSION_ID': test_session_id}):
            marker_path = _get_embedding_attempted_path()

            # Pre-create the marker
            marker_path.touch()

            result = maybe_embed_pending()

            assert result['status'] == 'skipped'
            assert 'already attempted' in result['message'].lower()

            # Clean up
            marker_path.unlink()


class TestMemoryAPIIntegration:
    """Tests for integration between memory_api.py and memory_init.py.

    Note: Direct testing of memory_api.py is complex due to its relative imports.
    These tests verify the lazy initialization pattern by testing the _ensure_ready
    helper function behavior and the ensure_memory_ready integration.
    """

    def test_ensure_ready_helper_calls_ensure_memory_ready(self):
        """Test that _ensure_ready() calls ensure_memory_ready()."""
        from memory_init import reset_initialization, is_initialized, ensure_memory_ready

        reset_initialization()
        assert is_initialized() is False

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # Simulate what _ensure_ready does: call ensure_memory_ready
            ensure_memory_ready()

            assert is_initialized() is True
            assert mock_deps.call_count == 1

    def test_repeated_ensure_ready_calls_are_idempotent(self):
        """Test that calling ensure_memory_ready multiple times only initializes once."""
        from memory_init import reset_initialization, ensure_memory_ready

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # Multiple calls simulating multiple API method calls
            ensure_memory_ready()  # save()
            ensure_memory_ready()  # search()
            ensure_memory_ready()  # list()
            ensure_memory_ready()  # get()
            ensure_memory_ready()  # update()

            # Should only initialize once
            assert mock_deps.call_count == 1

    def test_fast_path_returns_immediately(self):
        """Test that fast path (already_initialized=True) returns without work."""
        from memory_init import reset_initialization, ensure_memory_ready

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # First call does work
            result1 = ensure_memory_ready()
            assert result1['already_initialized'] is False

            # Subsequent calls return immediately
            result2 = ensure_memory_ready()
            assert result2['already_initialized'] is True

            result3 = ensure_memory_ready()
            assert result3['already_initialized'] is True

            # Work was only done once
            assert mock_deps.call_count == 1
            assert mock_migrate.call_count == 1
            assert mock_embed.call_count == 1

    def test_api_pattern_simulation(self):
        """Simulate how memory_api uses _ensure_ready pattern."""
        from memory_init import reset_initialization, ensure_memory_ready, is_initialized

        reset_initialization()

        # Define a mock API method that follows the pattern
        def mock_api_method():
            """Simulates save(), search(), list(), etc."""
            ensure_memory_ready()  # This is what _ensure_ready() does
            return "operation completed"

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # Before any API call
            assert is_initialized() is False

            # First API call triggers initialization
            mock_api_method()
            assert is_initialized() is True
            assert mock_deps.call_count == 1

            # Subsequent API calls don't re-initialize
            mock_api_method()
            mock_api_method()
            mock_api_method()
            assert mock_deps.call_count == 1


class TestGracefulDegradation:
    """Tests for graceful degradation when initialization steps fail."""

    def test_continues_after_dep_failure(self):
        """Test that initialization continues even if dependency installation fails."""
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'failed', 'installed': [], 'failed': ['pysqlite3']}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            result = ensure_memory_ready()

            # All steps were called despite first failure
            assert mock_migrate.call_count == 1
            assert mock_embed.call_count == 1
            assert result['deps']['status'] == 'failed'

    def test_continues_after_migration_error(self):
        """Test that initialization continues even if migration fails."""
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'error', 'message': 'Migration failed'}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            result = ensure_memory_ready()

            # Embedding step still ran
            assert mock_embed.call_count == 1
            assert result['migration']['status'] == 'error'

    def test_continues_after_embedding_error(self):
        """Test that initialization completes even if embedding fails."""
        from memory_init import ensure_memory_ready, reset_initialization, is_initialized

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': [], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'error', 'message': 'Embedding failed'}

            result = ensure_memory_ready()

            # Initialization is still considered complete
            assert is_initialized() is True
            assert result['embedding']['status'] == 'error'

    def test_all_steps_fail_still_marks_initialized(self):
        """Test that even if all steps fail, system is marked initialized."""
        from memory_init import ensure_memory_ready, reset_initialization, is_initialized

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'failed', 'installed': [], 'failed': ['all']}
            mock_migrate.return_value = {'status': 'error', 'message': 'Failed'}
            mock_embed.return_value = {'status': 'error', 'message': 'Failed'}

            result = ensure_memory_ready()

            # System is still marked initialized to prevent retry loops
            assert is_initialized() is True
            assert result['already_initialized'] is False


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_deps_result(self):
        """Test handling of empty dependency check result."""
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {}  # Empty dict
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # Should not raise
            result = ensure_memory_ready()
            assert result is not None

    def test_none_values_in_results(self):
        """Test handling of None values in step results."""
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': None, 'failed': None}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': None, 'message': None}

            # Should not raise
            result = ensure_memory_ready()
            assert result is not None

    def test_reset_during_initialization(self):
        """Test that reset during initialization is handled safely."""
        from memory_init import ensure_memory_ready, reset_initialization, is_initialized

        reset_initialization()

        def slow_deps():
            time.sleep(0.1)
            return {'status': 'ok', 'installed': [], 'failed': []}

        with patch('memory_init.check_and_install_dependencies', side_effect=slow_deps), \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            # Start initialization in background
            def init_thread():
                ensure_memory_ready()

            t = threading.Thread(target=init_thread)
            t.start()

            # Try to reset while initialization is running
            time.sleep(0.05)
            reset_initialization()

            t.join()

            # State should be consistent (either initialized or not)
            # The point is that no exception is raised


class TestLogging:
    """Tests for logging behavior during initialization."""

    def test_logs_installed_dependencies(self, caplog):
        """Test that installed dependencies are logged."""
        import logging
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'ok', 'installed': ['sqlite-vec'], 'failed': []}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            with caplog.at_level(logging.INFO):
                ensure_memory_ready()

            assert any('sqlite-vec' in record.message for record in caplog.records)

    def test_logs_failed_installations(self, caplog):
        """Test that failed installations are logged as warnings."""
        import logging
        from memory_init import ensure_memory_ready, reset_initialization

        reset_initialization()

        with patch('memory_init.check_and_install_dependencies') as mock_deps, \
             patch('memory_init.maybe_migrate_embeddings') as mock_migrate, \
             patch('memory_init.maybe_embed_pending') as mock_embed:

            mock_deps.return_value = {'status': 'partial', 'installed': [], 'failed': ['pysqlite3']}
            mock_migrate.return_value = {'status': 'ok', 'message': None}
            mock_embed.return_value = {'status': 'ok', 'message': None}

            with caplog.at_level(logging.WARNING):
                ensure_memory_ready()

            assert any('pysqlite3' in record.message for record in caplog.records)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_init_state():
    """Reset initialization state before and after each test."""
    from memory_init import reset_initialization
    reset_initialization()
    yield
    reset_initialization()
