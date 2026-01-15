"""
PACT Memory Setup and Initialization

Location: pact-plugin/skills/pact-memory/scripts/setup_memory.py

Handles auto-initialization of the PACT Memory system including:
- Database schema creation
- GGUF model download with progress
- Dependency checking

Used by:
- Hooks: session_init.py for startup initialization
- CLI: Manual setup commands
"""

import hashlib
import logging
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .config import (
    DEFAULT_MODEL_PATH,
    MODEL_SIZE_MB,
    MODEL_URL,
    MODELS_DIR,
    PACT_MEMORY_DIR,
)

# Configure logging
logger = logging.getLogger(__name__)


def ensure_directories() -> None:
    """Create required directories if they don't exist."""
    PACT_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def check_dependencies() -> Dict[str, Any]:
    """
    Check the status of required dependencies.

    Returns:
        Dictionary with dependency status:
        - sqlite_vec: bool - Is sqlite-vec installed?
        - sqlite_lembed: bool - Is sqlite-lembed installed?
        - sentence_transformers: bool - Is sentence-transformers installed?
        - model_exists: bool - Does the GGUF model exist?
        - model_path: str - Path to the model file
    """
    status: Dict[str, Any] = {
        "sqlite_vec": False,
        "sqlite_lembed": False,
        "sentence_transformers": False,
        "model_exists": DEFAULT_MODEL_PATH.exists(),
        "model_path": str(DEFAULT_MODEL_PATH)
    }

    # Check sqlite-vec
    try:
        import sqlite_vec
        status["sqlite_vec"] = True
    except ImportError:
        pass

    # Check sqlite-lembed
    try:
        import sqlite_lembed
        status["sqlite_lembed"] = True
    except ImportError:
        pass

    # Check sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        status["sentence_transformers"] = True
    except ImportError:
        pass

    return status


def download_model(
    url: str = MODEL_URL,
    path: Optional[Path] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    force: bool = False
) -> bool:
    """
    Download the GGUF model file with progress reporting.

    Args:
        url: URL to download the model from.
        path: Local path to save the model. Uses default if not provided.
        progress_callback: Optional callback(downloaded_bytes, total_bytes).
        force: Download even if file already exists.

    Returns:
        True if download successful or file already exists, False on failure.
    """
    target_path = path or DEFAULT_MODEL_PATH

    # Check if already exists
    if target_path.exists() and not force:
        logger.info(f"Model already exists: {target_path}")
        return True

    # Ensure directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading model from {url}")
    logger.info(f"Target: {target_path}")

    try:
        # Create request with headers
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "PACT-Memory/1.0"}
        )

        # Open URL and get content length
        with urllib.request.urlopen(request, timeout=60) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 8192

            # Use temp file during download
            temp_path = target_path.with_suffix(".tmp")

            with open(temp_path, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    f.write(chunk)
                    downloaded += len(chunk)

                    if progress_callback:
                        progress_callback(downloaded, total_size)

            # Rename temp file to final path
            temp_path.rename(target_path)

        logger.info(f"Download complete: {target_path}")
        return True

    except urllib.error.URLError as e:
        logger.error(f"Download failed (network error): {e}")
        return False
    except OSError as e:
        logger.error(f"Download failed (file error): {e}")
        return False
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False


def download_model_with_progress(
    url: str = MODEL_URL,
    path: Optional[Path] = None,
    force: bool = False
) -> bool:
    """
    Download model with console progress bar.

    Args:
        url: URL to download the model from.
        path: Local path to save the model.
        force: Download even if file already exists.

    Returns:
        True if download successful.
    """
    def show_progress(downloaded: int, total: int) -> None:
        if total > 0:
            percent = (downloaded / total) * 100
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total / (1024 * 1024)

            # Simple progress bar
            bar_width = 30
            filled = int(bar_width * downloaded / total)
            bar = "=" * filled + "-" * (bar_width - filled)

            print(
                f"\r[{bar}] {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                end="",
                flush=True
            )

    result = download_model(url, path, show_progress, force)

    if result:
        print()  # New line after progress bar

    return result


def ensure_initialized(
    download_model_if_missing: bool = False,
    show_progress: bool = True
) -> bool:
    """
    Ensure the memory system is fully initialized.

    Performs all setup tasks:
    1. Creates required directories
    2. Initializes database schema
    3. Optionally downloads model if missing

    Args:
        download_model_if_missing: Download GGUF model if not present.
        show_progress: Show progress bar during download.

    Returns:
        True if system is ready for use.
    """
    # Create directories
    ensure_directories()

    # Initialize database
    try:
        from .database import initialize_database
        initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

    # Check dependencies
    deps = check_dependencies()

    # Download model if needed
    if download_model_if_missing and not deps["model_exists"]:
        if deps["sqlite_lembed"]:
            logger.info("sqlite-lembed available, downloading model...")
            if show_progress:
                download_model_with_progress()
            else:
                download_model()
        else:
            logger.info(
                "sqlite-lembed not installed, skipping model download. "
                "Install with: pip install sqlite-lembed"
            )

    return True


def get_setup_status() -> Dict[str, Any]:
    """
    Get comprehensive setup status.

    Returns:
        Dictionary with full status information.
    """
    deps = check_dependencies()

    # Determine overall status
    can_use_semantic = (
        (deps["sqlite_lembed"] and deps["model_exists"]) or
        deps["sentence_transformers"]
    )

    return {
        "initialized": PACT_MEMORY_DIR.exists(),
        "dependencies": deps,
        "can_use_semantic_search": can_use_semantic,
        "paths": {
            "memory_dir": str(PACT_MEMORY_DIR),
            "models_dir": str(MODELS_DIR),
            "model_path": str(DEFAULT_MODEL_PATH)
        },
        "recommendations": _get_recommendations(deps)
    }


def _get_recommendations(deps: Dict[str, Any]) -> list:
    """Generate setup recommendations based on current status."""
    recommendations = []

    if not deps["sqlite_vec"]:
        recommendations.append(
            "Install sqlite-vec for vector search: pip install sqlite-vec"
        )

    if not deps["sqlite_lembed"] and not deps["sentence_transformers"]:
        recommendations.append(
            "Install sqlite-lembed for local embeddings: pip install sqlite-lembed"
        )
        recommendations.append(
            "Or install sentence-transformers as fallback: pip install sentence-transformers"
        )

    if deps["sqlite_lembed"] and not deps["model_exists"]:
        recommendations.append(
            f"Download the embedding model: {MODEL_URL}"
        )

    return recommendations


def print_setup_status() -> None:
    """Print formatted setup status to console."""
    status = get_setup_status()

    print("\n=== PACT Memory Setup Status ===\n")

    print("Initialization:")
    print(f"  Memory directory: {'OK' if status['initialized'] else 'Missing'}")
    print(f"  Path: {status['paths']['memory_dir']}")

    print("\nDependencies:")
    deps = status["dependencies"]
    print(f"  sqlite-vec:           {'Installed' if deps['sqlite_vec'] else 'Not installed'}")
    print(f"  sqlite-lembed:        {'Installed' if deps['sqlite_lembed'] else 'Not installed'}")
    print(f"  sentence-transformers: {'Installed' if deps['sentence_transformers'] else 'Not installed'}")
    print(f"  GGUF model:           {'Present' if deps['model_exists'] else 'Not downloaded'}")

    print("\nCapabilities:")
    print(f"  Semantic search: {'Available' if status['can_use_semantic_search'] else 'Unavailable'}")
    print(f"  Keyword search:  Available")
    print(f"  Graph search:    Available")

    if status["recommendations"]:
        print("\nRecommendations:")
        for rec in status["recommendations"]:
            print(f"  - {rec}")

    print()


def setup_cli() -> None:
    """
    CLI entry point for setup commands.

    Usage:
        python -m pact_memory.scripts.setup_memory [command]

    Commands:
        status  - Show setup status
        init    - Initialize database and directories
        model   - Download the embedding model
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="PACT Memory setup utility"
    )
    parser.add_argument(
        "command",
        choices=["status", "init", "model"],
        default="status",
        nargs="?",
        help="Command to run"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download of model"
    )

    args = parser.parse_args()

    if args.command == "status":
        print_setup_status()

    elif args.command == "init":
        print("Initializing PACT Memory...")
        if ensure_initialized(download_model_if_missing=False):
            print("Initialization complete!")
        else:
            print("Initialization failed. Check logs for details.")
            sys.exit(1)

    elif args.command == "model":
        deps = check_dependencies()
        if not deps["sqlite_lembed"]:
            print("sqlite-lembed is not installed. Model download skipped.")
            print("Install with: pip install sqlite-lembed")
            sys.exit(1)

        print(f"Downloading model to {DEFAULT_MODEL_PATH}...")
        if download_model_with_progress(force=args.force):
            print("Model download complete!")
        else:
            print("Model download failed. Check logs for details.")
            sys.exit(1)


if __name__ == "__main__":
    setup_cli()
