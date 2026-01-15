"""
PACT Memory Embedding Service

Location: pact-plugin/skills/pact-memory/scripts/embeddings.py

Embedding generation for semantic search in the PACT Memory skill.
Supports multiple backends with graceful fallbacks:
1. sqlite-lembed with GGUF model (preferred - local, fast)
2. sentence-transformers (fallback - requires more deps)
3. None (ultimate fallback - search degrades to keyword-only)

Used by:
- search.py: Generates query embeddings for semantic search
- memory_api.py: Generates embeddings when saving memories
"""

import logging
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .config import (
    DEFAULT_MODEL_PATH,
    EMBEDDING_DIMENSION,
    MODEL_URL,
    MODELS_DIR,
    PACT_MEMORY_DIR,
)

# Configure logging
logger = logging.getLogger(__name__)


class EmbeddingBackend:
    """
    Abstract interface for embedding backends.

    Implementations provide generate() method to convert text to vectors.
    """

    def generate(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text."""
        raise NotImplementedError

    def is_available(self) -> bool:
        """Check if this backend is ready to use."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Backend name for logging."""
        raise NotImplementedError


class SqliteLembedBackend(EmbeddingBackend):
    """
    Embedding backend using sqlite-lembed with GGUF model.

    This is the preferred backend as it:
    - Works locally without API calls
    - Is fast and efficient
    - Uses the same SQLite connection as the database
    """

    def __init__(self, model_path: Optional[Path] = None):
        self._model_path = model_path or DEFAULT_MODEL_PATH
        self._conn: Optional[sqlite3.Connection] = None
        self._initialized = False
        self._available: Optional[bool] = None

    @property
    def name(self) -> str:
        return "sqlite-lembed"

    def is_available(self) -> bool:
        """Check if sqlite-lembed and model are available."""
        if self._available is not None:
            return self._available

        # Check if model file exists
        if not self._model_path.exists():
            logger.debug(f"Model file not found: {self._model_path}")
            self._available = False
            return False

        # Try to load sqlite-lembed
        try:
            import sqlite_lembed
            self._available = True
            return True
        except ImportError:
            logger.debug("sqlite-lembed not installed")
            self._available = False
            return False

    def _ensure_initialized(self) -> bool:
        """Initialize the embedding connection if needed."""
        if self._initialized:
            return True

        if not self.is_available():
            return False

        try:
            import sqlite_lembed

            # Create in-memory connection for embedding generation
            self._conn = sqlite3.connect(":memory:")
            self._conn.enable_load_extension(True)
            sqlite_lembed.load(self._conn)

            # Register the model
            self._conn.execute(
                "INSERT INTO temp.lembed_models(name, model) VALUES (?, lembed_model_from_file(?))",
                ("embed", str(self._model_path))
            )

            self._initialized = True
            logger.info(f"Initialized sqlite-lembed with model: {self._model_path.name}")
            return True

        except Exception as e:
            logger.warning(f"Failed to initialize sqlite-lembed: {e}")
            self._available = False
            return False

    def generate(self, text: str) -> Optional[List[float]]:
        """Generate embedding using sqlite-lembed."""
        if not self._ensure_initialized():
            return None

        try:
            cursor = self._conn.execute(
                "SELECT lembed('embed', ?)",
                (text,)
            )
            result = cursor.fetchone()
            if result and result[0]:
                # sqlite-lembed returns a blob, convert to list of floats
                import struct
                blob = result[0]
                num_floats = len(blob) // 4
                embedding = list(struct.unpack(f'{num_floats}f', blob))
                return embedding
            return None
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return None

    def close(self) -> None:
        """Close the in-memory connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
        self._initialized = False


class SentenceTransformersBackend(EmbeddingBackend):
    """
    Fallback embedding backend using sentence-transformers.

    Uses the same MiniLM model but through the Hugging Face library.
    Requires more dependencies but works without sqlite-lembed.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = None
        self._available: Optional[bool] = None

    @property
    def name(self) -> str:
        return "sentence-transformers"

    def is_available(self) -> bool:
        """Check if sentence-transformers is installed."""
        if self._available is not None:
            return self._available

        try:
            from sentence_transformers import SentenceTransformer
            self._available = True
            return True
        except ImportError:
            logger.debug("sentence-transformers not installed")
            self._available = False
            return False

    def _ensure_initialized(self) -> bool:
        """Load the model if needed."""
        if self._model is not None:
            return True

        if not self.is_available():
            return False

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
            logger.info(f"Loaded sentence-transformers model: {self._model_name}")
            return True
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers model: {e}")
            self._available = False
            return False

    def generate(self, text: str) -> Optional[List[float]]:
        """Generate embedding using sentence-transformers."""
        if not self._ensure_initialized():
            return None

        try:
            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return None


class EmbeddingService:
    """
    High-level embedding service with automatic backend selection.

    Tries backends in order of preference:
    1. sqlite-lembed (local GGUF model)
    2. sentence-transformers (Hugging Face model)
    3. Returns None (keyword search fallback)
    """

    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize the embedding service.

        Args:
            model_path: Optional custom path to GGUF model file.
        """
        self._backends: List[EmbeddingBackend] = [
            SqliteLembedBackend(model_path),
            SentenceTransformersBackend()
        ]
        self._active_backend: Optional[EmbeddingBackend] = None

    def _get_backend(self) -> Optional[EmbeddingBackend]:
        """Find the first available backend."""
        if self._active_backend is not None:
            return self._active_backend

        for backend in self._backends:
            if backend.is_available():
                logger.info(f"Using embedding backend: {backend.name}")
                self._active_backend = backend
                return backend

        logger.warning(
            "No embedding backend available. "
            "Install sqlite-lembed or sentence-transformers for semantic search."
        )
        return None

    def generate(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text.

        Args:
            text: Input text to embed.

        Returns:
            List of floats representing the embedding, or None if unavailable.
        """
        if not text or not text.strip():
            return None

        backend = self._get_backend()
        if backend is None:
            return None

        return backend.generate(text)

    def is_available(self) -> bool:
        """Check if any embedding backend is available."""
        return self._get_backend() is not None

    @property
    def backend_name(self) -> Optional[str]:
        """Get the name of the active backend."""
        backend = self._get_backend()
        return backend.name if backend else None


# Module-level singleton for convenience
_lock = threading.Lock()
_service: Optional[EmbeddingService] = None


def get_embedding_service(model_path: Optional[Path] = None) -> EmbeddingService:
    """
    Get the embedding service singleton.

    Args:
        model_path: Optional custom path to GGUF model.

    Returns:
        EmbeddingService instance.
    """
    global _service
    with _lock:
        if _service is None:
            _service = EmbeddingService(model_path)
    return _service


def reset_embedding_service() -> None:
    """Reset the singleton instance. Useful for testing."""
    global _service
    with _lock:
        if _service is not None:
            # Close any open connections
            for backend in _service._backends:
                if hasattr(backend, 'close'):
                    backend.close()
        _service = None


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate embedding for text using the default service.

    Convenience function for simple use cases.

    Args:
        text: Input text to embed.

    Returns:
        List of floats representing the embedding, or None if unavailable.
    """
    return get_embedding_service().generate(text)


def generate_embedding_text(memory: Dict[str, Any]) -> str:
    """
    Generate combined text from memory fields for embedding.

    Combines context, goal, lessons, and decisions into a single
    text block optimized for semantic similarity search.

    Uses MemoryObject.get_searchable_text() as the single source of truth.

    Args:
        memory: Memory dictionary with context, goal, lessons_learned, etc.

    Returns:
        Combined text suitable for embedding generation.
    """
    from .models import MemoryObject
    memory_obj = MemoryObject.from_dict(memory)
    return memory_obj.get_searchable_text()


def check_embedding_availability() -> Dict[str, Any]:
    """
    Check the status of embedding backends.

    Returns:
        Dictionary with availability info for each backend.
    """
    service = get_embedding_service()

    return {
        "available": service.is_available(),
        "active_backend": service.backend_name,
        "model_path": str(DEFAULT_MODEL_PATH),
        "model_exists": DEFAULT_MODEL_PATH.exists(),
        "backends": {
            "sqlite-lembed": SqliteLembedBackend().is_available(),
            "sentence-transformers": SentenceTransformersBackend().is_available()
        }
    }
