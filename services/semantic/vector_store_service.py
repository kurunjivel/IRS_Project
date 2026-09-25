"""
Vector Store Service — Phase 7.

Manages ChromaDB vector database collection for canonical skill embeddings.
Supports idempotent upserts, metadata storage, and similarity search.
"""

import os
import logging
from typing import List, Dict, Optional, Any
from config import SEMANTIC_MATCHING_CONFIG

logger = logging.getLogger(__name__)

_CHROMA_CLIENT = None
_CHROMA_COLLECTION = None
_CHROMA_INITIALIZED = False


def _get_chroma_collection():
    """Singleton getter for ChromaDB collection."""
    global _CHROMA_CLIENT, _CHROMA_COLLECTION, _CHROMA_INITIALIZED
    if _CHROMA_INITIALIZED:
        return _CHROMA_COLLECTION

    try:
        import chromadb
        from chromadb.config import Settings

        db_path = SEMANTIC_MATCHING_CONFIG.get("chroma_db_path", "./.chroma_db")
        os.makedirs(db_path, exist_ok=True)

        logger.info("Initializing ChromaDB client at '%s'...", db_path)
        _CHROMA_CLIENT = chromadb.PersistentClient(path=db_path)
        _CHROMA_COLLECTION = _CHROMA_CLIENT.get_or_create_collection(
            name="irs_skills",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("ChromaDB collection 'irs_skills' ready.")
    except Exception as e:
        logger.warning("Could not initialize ChromaDB: %s. Vector storage disabled.", e)
        _CHROMA_CLIENT = None
        _CHROMA_COLLECTION = None
    finally:
        _CHROMA_INITIALIZED = True

    return _CHROMA_COLLECTION


class VectorStoreService:
    """Service to interact with ChromaDB vector storage."""

    def __init__(self) -> None:
        self._collection = _get_chroma_collection()

    @property
    def is_available(self) -> bool:
        """Check if ChromaDB is available."""
        return self._collection is not None

    def upsert_skill(
        self,
        skill_id: str,
        skill_name: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Idempotent upsert of a skill embedding vector into ChromaDB.
        """
        if not self.is_available or not embedding:
            return False

        meta = {
            "canonical_name": skill_name,
            "original_name": metadata.get("original_name", skill_name) if metadata else skill_name,
            "category": metadata.get("category", "General") if metadata else "General",
        }

        try:
            self._collection.upsert(
                ids=[skill_id],
                embeddings=[embedding],
                metadatas=[meta],
                documents=[skill_name],
            )
            return True
        except Exception as e:
            logger.error("Failed to upsert skill '%s' into ChromaDB: %s", skill_name, e)
            return False

    def search_similar(
        self,
        query_embedding: List[float],
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Query ChromaDB for top-N similar skills given a query vector.

        Returns list of dicts:
        [
            {
                "skill_name": str,
                "similarity_score": float (0.0 to 1.0),
                "metadata": dict
            }
        ]
        """
        if not self.is_available or not query_embedding:
            return []

        try:
            res = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["metadatas", "distances", "documents"],
            )

            results = []
            if res and "distances" in res and res["distances"] and res["distances"][0]:
                distances = res["distances"][0]
                metadatas = res["metadatas"][0] if "metadatas" in res and res["metadatas"] else []
                documents = res["documents"][0] if "documents" in res and res["documents"] else []

                for dist, meta, doc in zip(distances, metadatas, documents):
                    # ChromaDB cosine distance d in [0, 2], similarity = max(0, 1 - d)
                    similarity = max(0.0, min(1.0, 1.0 - float(dist)))
                    results.append({
                        "skill_name": meta.get("canonical_name", doc),
                        "similarity_score": round(similarity, 4),
                        "metadata": meta,
                    })

            return results
        except Exception as e:
            logger.error("ChromaDB vector query failed: %s", e)
            return []
