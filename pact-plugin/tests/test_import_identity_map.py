"""Tests for tests/import_identity_map.py — the layer-4 harness prototype.

Mechanism tests use synthetic fixtures; live-session tests assert only what
conftest.py guarantees in EVERY invocation shape (hooks/ on sys.path, so
`shared` resolves) — bare `working_memory` needs a carrier insert and is
asserted conditionally so this file passes STANDALONE as well as in the gate.
"""

import json
import sys
import textwrap

from import_identity_map import (
    capture_map,
    diff_maps,
    imported_names,
    resolve_origins,
)


def _write(tmp_path, source):
    f = tmp_path / "test_sample.py"
    f.write_text(textwrap.dedent(source))
    return f


def test_imported_names_catches_module_and_function_level(tmp_path):
    f = _write(
        tmp_path,
        """\
        import os
        import working_memory
        from shared.marker_schema import MARKER_SCHEMA_VERSION

        def test_x():
            from bootstrap_gate import main
            import scripts.config
        """,
    )
    names = imported_names(f)
    assert "os" in names
    assert "working_memory" in names
    assert "shared.marker_schema" in names  # full dotted path, not 'shared'
    assert "bootstrap_gate" in names        # function-level import found
    assert "scripts.config" in names


def test_imported_names_skips_relative_imports(tmp_path):
    f = _write(tmp_path, "from .helpers import thing\n")
    assert imported_names(f) == set()


def test_resolve_origins_shared_resolves_in_every_shape():
    # hooks/ is conftest-provided in all measured invocation shapes (gate,
    # repo-root by-path, tests-dir cwd, CI), so this must hold standalone too.
    origins = resolve_origins(["shared.marker_schema"])
    assert origins["shared.marker_schema"] == "hooks/shared/marker_schema.py"


def test_resolve_origins_working_memory_conditional_on_carrier():
    # scripts/ reaches sys.path only via a per-file insert or carrier masking;
    # standalone this file has neither. Both outcomes prove the mechanism:
    # resolvable -> correct file; unresolvable -> recorded None, not omitted.
    origins = resolve_origins(["working_memory"])
    if any(p.endswith("pact-memory/scripts") for p in sys.path):
        assert origins["working_memory"] == (
            "skills/pact-memory/scripts/working_memory.py"
        )
    else:
        assert origins["working_memory"] is None


def test_resolve_origins_omits_externals():
    assert resolve_origins(["json", "pathlib", "pytest"]) == {}


def test_resolve_origins_missing_module_recorded_none():
    assert resolve_origins(["no_such_module_xyz"]) == {"no_such_module_xyz": None}


def test_capture_map_keys_repo_relative(tmp_path):
    f = _write(tmp_path, "import json\n")
    result = capture_map([f])
    key = next(iter(result))  # tmp files are outside PLUGIN_ROOT
    assert result[key] == {}  # json is external -> omitted


def test_map_is_json_diffable():
    m = {"tests/test_a.py": {"shared.marker_schema": "hooks/shared/marker_schema.py"}}
    assert json.loads(json.dumps(m, sort_keys=True)) == m


def test_diff_maps_empty_when_identical():
    m = {"t.py": {"working_memory": "skills/pact-memory/scripts/working_memory.py"}}
    assert diff_maps(m, dict(m)) == []


def test_diff_maps_flags_precedence_flip():
    b = {"t.py": {"config": "skills/pact-memory/scripts/config.py"}}
    c = {"t.py": {"config": "skills/other/scripts/config.py"}}
    diffs = diff_maps(b, c)
    assert len(diffs) == 1 and "config" in diffs[0]


def test_diff_maps_rename_normalization_allows_bare_to_package():
    origin = "skills/pact-memory/scripts/working_memory.py"
    b = {"t.py": {"working_memory": origin}}
    c = {"t.py": {"scripts.working_memory": origin}}
    renames = {"working_memory": "scripts.working_memory"}
    assert diff_maps(b, c, renames=renames) == []


def test_diff_maps_rename_still_flags_origin_change():
    b = {"t.py": {"working_memory": "skills/pact-memory/scripts/working_memory.py"}}
    c = {"t.py": {"scripts.working_memory": "elsewhere/working_memory.py"}}
    renames = {"working_memory": "scripts.working_memory"}
    assert diff_maps(b, c, renames=renames) != []


def test_diff_maps_flags_missing_file():
    b = {"t.py": {"x": "hooks/x.py"}}
    assert diff_maps(b, {}) != []


def _fresh_state(monkeypatch):
    import import_identity_map as iim

    monkeypatch.setattr(
        iim, "_state", {"sessionstart_path": None, "collected_files": set()}
    )
    return iim


def test_hook_emits_map_when_outermost(tmp_path, monkeypatch):
    iim = _fresh_state(monkeypatch)
    out = tmp_path / "map.json"
    monkeypatch.setenv("PACT_IDENTITY_MAP_OUT", str(out))
    monkeypatch.delenv("PACT_IDENTITY_MAP_ACTIVE", raising=False)
    iim.pytest_sessionstart(None)
    iim.pytest_sessionfinish(None, 0)
    assert out.exists()
    assert "map" in json.loads(out.read_text())


def test_hook_skips_emission_when_nested(tmp_path, monkeypatch):
    iim = _fresh_state(monkeypatch)
    out = tmp_path / "map.json"
    monkeypatch.setenv("PACT_IDENTITY_MAP_OUT", str(out))
    monkeypatch.setenv("PACT_IDENTITY_MAP_ACTIVE", "1")  # inherited mark
    iim.pytest_sessionstart(None)
    iim.pytest_sessionfinish(None, 0)
    assert not out.exists()


def test_hook_silent_without_out_env(monkeypatch):
    iim = _fresh_state(monkeypatch)
    monkeypatch.delenv("PACT_IDENTITY_MAP_OUT", raising=False)
    monkeypatch.delenv("PACT_IDENTITY_MAP_ACTIVE", raising=False)
    iim.pytest_sessionstart(None)
    iim.pytest_sessionfinish(None, 0)  # no exception, no file
