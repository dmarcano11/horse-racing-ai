"""Semantic search retriever for race data."""
from sentence_transformers import SentenceTransformer
from src.rag.vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)
MODEL_NAME = 'all-MiniLM-L6-v2'


class RaceRetriever:
    """Retrieves relevant race context for LLM queries."""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.model = None

    def _load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query: str, limit: int = 5,
               track: str = None, date: str = None) -> list:
        """
        Semantic search for relevant races.

        Args:
            query: Natural language search query
            limit: Number of results to return
            track: Optional track filter
            date: Optional date filter

        Returns:
            List of relevant race documents with metadata
        """
        self._load_model()

        if self.vector_store.get_count() == 0:
            logger.warning("Vector store is empty - no races indexed yet")
            return []

        # Encode query
        query_embedding = self.model.encode(query).tolist()

        # Build filter
        where = {}
        if track:
            where['track'] = track
        if date:
            where['date'] = date

        # Query vector store
        results = self.vector_store.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where if where else None
        )

        # Format results
        formatted = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted.append({
                    'document': doc,
                    'metadata': results['metadatas'][0][i],
                    'relevance_score': round(
                        1 - results['distances'][0][i], 3
                    )
                })

        return formatted

    def get_context_for_query(self, query: str, race_id: int = None) -> str:
        """
        Get formatted context string for LLM.
        Combines semantic search with specific race data if provided.
        """
        context_parts = []

        # Add specific race context if provided
        if race_id:
            context_parts.append(
                f"[Current Race ID: {race_id} - "
                f"use get_race_details tool for full info]"
            )

        # Semantic search for relevant historical context
        search_results = self.search(query, limit=3)

        if search_results:
            context_parts.append("\n=== RELEVANT HISTORICAL RACES ===")
            for i, result in enumerate(search_results, 1):
                score = result['relevance_score']
                if score > 0.3:  # Only include relevant results
                    context_parts.append(
                        f"\n[Race {i} - Relevance: {score:.2f}]\n"
                        f"{result['document']}"
                    )

        return "\n".join(context_parts) if context_parts else ""