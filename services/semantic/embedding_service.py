"""
Embedding Service — Phase 7.

Loads sentence-transformers model 'all-MiniLM-L6-v2' once at startup (singleton pattern)
and generates vector embeddings for skill texts. Includes graceful fallback handling.
"""

import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

_GLOBAL_MODEL = None
_MODEL_INITIALIZED = False


def _get_embedding_model():
    """Singleton getter for SentenceTransformer model."""
    global _GLOBAL_MODEL, _MODEL_INITIALIZED
    if _MODEL_INITIALIZED:
        return _GLOBAL_MODEL

    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Initializing SentenceTransformer model 'all-MiniLM-L6-v2'...")
        _GLOBAL_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SentenceTransformer model loaded successfully.")
    except Exception as e:
        logger.warning("Could not initialize SentenceTransformer model: %s. Falling back to exact matching mode.", e)
        _GLOBAL_MODEL = None
    finally:
        _MODEL_INITIALIZED = True

    return _GLOBAL_MODEL


_EMBEDDING_CACHE: dict[str, List[float]] = {}


class EmbeddingService:
    """Service to generate dense vector embeddings for skill strings."""

    def __init__(self) -> None:
        self._model = _get_embedding_model()

    @property
    def is_available(self) -> bool:
        """Check if embedding model is ready."""
        return self._model is not None

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for a single skill text.

        Returns list of floats or None if model unavailable.
        """
        if not self.is_available or not text:
            return None
        
        cleaned = text.strip().lower()
        if cleaned in _EMBEDDING_CACHE:
            return _EMBEDDING_CACHE[cleaned]

        try:
            vec = self._model.encode(text, convert_to_numpy=True).tolist()
            _EMBEDDING_CACHE[cleaned] = vec
            return vec
        except Exception as e:
            logger.error("Error generating embedding for '%s': %s", text, e)
            return None

    def generate_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Batch generate embedding vectors for a list of skill texts.
        """
        if not self.is_available or not texts:
            return None
        try:
            vecs = self._model.encode(texts, convert_to_numpy=True)
            return vecs.tolist()
        except Exception as e:
            logger.error("Error generating batch embeddings: %s", e)
            return None
