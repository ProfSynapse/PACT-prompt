"""
Location: pact-plugin/hooks/shared/project_scope.py
Summary: Predicates answering "are these two directories the same project?".
Used by: scripts/archive_pin.py (pin archival resolution) and
         skills/pact-memory/scripts/working_memory.py (working-memory
         projection), both of which resolve a CLAUDE.md and must tell a
         legitimate fall-through from a wrong-project one.

WHY THIS IS NOT IN git_helpers.py. That module is a narrow subprocess
wrapper whose docstring scopes it to "try/except + subprocess boilerplate
only", with callers owning the decision. `same_repository` IS a decision, so
it lives here and COMPOSES `run_git` rather than widening that contract.

WHY NOT IN THE MODULE THAT FIRST NEEDED IT. This began as a private helper in
archive_pin.py, where the defect was found. A function's home follows its
SUBJECT, not its discovery site — and the subject here is project identity,
which is neither pin archival nor memory projection. Importing archive_pin to
reach it is worse than it looks: that module loads two hook modules at import
time and registers them in sys.modules under bare top-level names, so a
consumer would acquire a global namespace mutation to borrow one predicate.
"""

from __future__ import annotations

from pathlib import Path

try:
    from .git_helpers import run_git
except ImportError:  # loaded as a top-level module rather than a package member
    from git_helpers import run_git


def same_repository(env_dir: Path, base: Path) -> bool:
    """True when `base` is the main repo of the git checkout at `env_dir`.

    🔴 THIS IS NOT SYMMETRIC AND THE ARGUMENT ORDER CHANGES THE ANSWER. It
    asks "is `base` the MAIN REPO OF the checkout at `env_dir`" — NOT "are
    these two directories related". Swapping the arguments silently returns a
    different verdict, and nothing will fail to tell you:

        same_repository(worktree, main_repo)  -> True   (main IS the main repo)
        same_repository(main_repo, worktree)  -> False  (a worktree is not one)
        same_repository(subdir,    repo_root) -> True
        same_repository(repo_root, subdir)    -> False  (a subdir is not one)

    Callers and the direction each uses: archive_pin passes
    (declared_env_dir, resolved_base); the working-memory escape guard passes
    (declared_scope, resolved_root). Both ask the same question — "did
    resolution land on the main repo of the scope I declared" — so both put
    the DECLARATION first. Put the declaration first or invert the meaning.

    THE DISCRIMINATOR BETWEEN A LEGITIMATE FALL-THROUGH AND A WRONG-PROJECT
    ONE. A resolver that probes a declared directory and finds no CLAUDE.md
    continues to its git anchors. That is CORRECT when it lands back inside
    the same project — PACT's own spawned paths set CLAUDE_PROJECT_DIR to a
    worktree, where CLAUDE.md is gitignored and therefore absent, and the
    git-common-dir step then finds the MAIN repo's file, which is the intended
    answer. A blanket "declared dir has no CLAUDE.md -> refuse" rule breaks
    that on every such invocation — a cardinal over-block.

    So the question is not "did we fall through" but "did we fall through to
    somewhere still in the same project". `--git-common-dir` answers it: every
    worktree of a repo shares one common dir, so its parent is the main root
    for both the worktree and the main checkout.

    FAIL-SAFE IS FALSE, WHICH MEANS REFUSE. Any git error, timeout, or
    non-repo directory returns False. Declining to guess is the safe direction
    on a write path: refusing costs a recoverable skip, while guessing wrong
    writes into a project nobody named.
    """
    # `run_git` absorbs TimeoutExpired and FileNotFoundError only. The original
    # predicate caught OSError entire, and that breadth is load-bearing here:
    # a PermissionError reaching a caller as an exception instead of a refusal
    # would turn a fail-safe into a crash on a write path.
    try:
        result = run_git(
            ["-C", str(env_dir), "rev-parse", "--git-common-dir"], timeout=5
        )
    except OSError:
        return False
    if result is None or result.returncode != 0 or not result.stdout.strip():
        return False
    common_dir = Path(result.stdout.strip())
    if not common_dir.is_absolute():
        common_dir = Path(env_dir) / common_dir
    try:
        return common_dir.resolve().parent == Path(base).resolve()
    except OSError:
        return False
