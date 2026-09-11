"""Plugin-root conftest for the PACT plugin suite.

Location: pact-plugin/conftest.py

Summary: Owns skills-adjacent coverage ONLY. Pin test files living beside
skill artifacts (skills/<skill>/test_*.py) sit outside tests/conftest.py's
subtree, so this conftest guarantees every skills/*/scripts dir is importable
for them. tests/conftest.py owns the full path block for tests/; the
membership guard keeps the overlap a no-op when both conftests load in one
run.

Used by: pytest (loaded for every run rooted at or below pact-plugin/).
The plugin root itself is inserted explicitly below (lead-ruled: deliberate
source, not reliance on pytest's conftest-basedir mechanics); the telegram
test family's `from telegram.X import ...` imports resolve through it.

NO-IMPORT CHARTER: this file path-INSERTS only. Never import from a scripts
dir at conftest scope — a missing optional dependency there becomes a total
suite collection failure.
"""

import sys
from pathlib import Path

for _scripts_dir in sorted(Path(__file__).parent.glob("skills/*/scripts")):
    _entry = str(_scripts_dir)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

# The plugin root itself, for the telegram test family's package imports.
_plugin_root = str(Path(__file__).parent)
if _plugin_root not in sys.path:
    sys.path.insert(0, _plugin_root)
