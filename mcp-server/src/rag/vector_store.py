"""ChromaDB vector store for race data."""
import chromadb
from chromadb.config import Settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Store ChromaDB data in mcp-server/data/
CHROMA_PATH = Path(__file__).parent.parent.parent / 'data' / 'chroma'


class VectorStore:
    """ChromaDB wrapper for race embeddings."""

    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize()

    def _initialize(self):
        """Initialize ChromaDB client and collection."""
        try:
            CHROMA_PATH.mkdir(parents=True, exist_ok=True)

            # Start fresh if existing DB is corrupt/incompatible
            try:
                self.client = chromadb.PersistentClient(
                    path=str(CHROMA_PATH),
                    settings=Settings(anonymized_telemetry=False)
                )
                self.collection = self.client.get_or_create_collection(
                    name="horse_races",
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception:
                # Wipe and recreate if DB is incompatible
                logger.warning("ChromaDB incompatible - resetting...")
                import shutil
                shutil.rmtree(str(CHROMA_PATH))
                CHROMA_PATH.mkdir(parents=True, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=str(CHROMA_PATH),
                    settings=Settings(anonymized_telemetry=False)
                )
                self.collection = self.client.get_or_create_collection(
                    name="horse_races",
                    metadata={"hnsw:space": "cosine"}
                )

            count = self.collection.count()
            logger.info(f"✓ Vector store ready - {count} races indexed")

        except Exception as e:
            logger.error(f"Vector store init failed: {e}")
            # Don't raise - allow app to start, embedding can happen later
            self.client = None
            self.collection = None

    def is_ready(self) -> bool:
        return self.client is not None and self.collection is not None

    def add_races(self, documents: list, embeddings: list,
                  metadatas: list, ids: list):
        """Add race documents to vector store."""
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(ids)} races to vector store")

    def query(self, query_embeddings: list, n_results: int = 5,
              where: dict = None) -> dict:
        """Query vector store for similar races."""
        kwargs = {
            'query_embeddings': query_embeddings,
            'n_results': min(n_results, self.collection.count() or 1),
            'include': ['documents', 'metadatas', 'distances']
        }
        if where:
            kwargs['where'] = where

        return self.collection.query(**kwargs)

    def get_count(self) -> int:
        """Get number of indexed races."""
        return self.collection.count()

    def reset(self):
        """Clear all embeddings (use carefully!)."""
        self.client.delete_collection("horse_races")
        self.collection = self.client.get_or_create_collection(
            name="horse_races",
            metadata={"hnsw:space": "cosine"}
        )
        logger.warning("Vector store reset - all embeddings cleared")