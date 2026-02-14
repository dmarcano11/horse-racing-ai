"""Converts race data to vector embeddings."""
import sys
import importlib
from pathlib import Path
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Fix: explicitly add data-ingestion and remove src cache conflict
DATA_INGESTION_PATH = str(
    Path(__file__).parent.parent.parent.parent / 'data-ingestion'
)

# Insert at 0 so it takes priority over mcp-server/src
if DATA_INGESTION_PATH not in sys.path:
    sys.path.insert(0, DATA_INGESTION_PATH)

# Clear any cached 'src' module that points to mcp-server/src
if 'src' in sys.modules:
    del sys.modules['src']
if 'src.db' in sys.modules:
    del sys.modules['src.db']

from src.db.session import get_db_context
from src.db.models import Race, Meet, Track, Runner, Horse, Jockey, Trainer
from src.db.models import RaceResult, RunnerResult
from src.rag.vector_store import VectorStore

MODEL_NAME = 'all-MiniLM-L6-v2'


class RaceEmbedder:
    """Embeds race data into vector store for semantic search."""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.model = None

    def _load_model(self):
        """Lazy load the embedding model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {MODEL_NAME}")
            self.model = SentenceTransformer(MODEL_NAME)
            logger.info("✓ Embedding model loaded")

    def race_to_text(self, race, meet, runners, results=None) -> str:
        """
        Convert race data to searchable text document.

        This is what gets embedded - richer text = better search.
        """
        lines = []

        # Race basics
        track_name = meet.track.track_name if meet.track else 'Unknown'
        lines.append(f"Race {race.race_number} at {track_name}")
        lines.append(f"Date: {meet.date}")

        if race.race_name:
            lines.append(f"Race Name: {race.race_name}")

        # Race conditions
        if race.distance_value:
            lines.append(f"Distance: {race.distance_value} {race.distance_unit or 'F'}")

        if race.surface:
            lines.append(f"Surface: {race.surface}")

        if race.race_type:
            lines.append(f"Race Type: {race.race_type}")

        if race.race_class:
            lines.append(f"Class: {race.race_class}")

        if race.purse:
            lines.append(f"Purse: ${race.purse:,}")

        if race.grade:
            lines.append(f"Grade: {race.grade}")

        # Runners
        if runners:
            lines.append(f"Field Size: {len(runners)} horses")
            runner_texts = []
            for r in runners:
                horse_name = r.horse.name if r.horse else 'Unknown'
                jockey_name = f"{r.jockey.first_name or ''} {r.jockey.last_name or ''}".strip() if r.jockey else 'Unknown'
                odds = r.morning_line_odds or '—'
                runner_texts.append(
                    f"{horse_name} (Jockey: {jockey_name}, ML: {odds})"
                )
            lines.append("Runners: " + ", ".join(runner_texts))

        # Results (if available)
        if results:
            result_texts = []
            for rr in sorted(results, key=lambda x: x.finish_position or 99):
                if rr.runner and rr.runner.horse:
                    pos = rr.finish_position
                    horse = rr.runner.horse.name
                    payoff = f"${rr.win_payoff:.2f}" if rr.win_payoff else ""
                    result_texts.append(f"{pos}. {horse} {payoff}")
            if result_texts:
                lines.append("Results: " + ", ".join(result_texts[:3]))

        return "\n".join(lines)

    def embed_all_races(self) -> int:
        """Embed all races from database into vector store."""
        self._load_model()

        embedded_count = 0

        with get_db_context() as db:
            races = db.query(Race).join(Meet).order_by(Meet.date).all()
            logger.info(f"Embedding {len(races)} races...")

            batch_docs = []
            batch_embeddings = []
            batch_metadatas = []
            batch_ids = []
            batch_size = 50

            for race in races:
                try:
                    meet = db.query(Meet).filter(Meet.id == race.meet_id).first()
                    if not meet:
                        continue

                    # Load track
                    if meet.track is None:
                        from src.db.models import Track
                        meet.track = db.query(Track).filter(
                            Track.id == meet.track_id
                        ).first()

                    # Load runners
                    runners = db.query(Runner).filter(
                        Runner.race_id == race.id,
                        Runner.is_scratched == False
                    ).all()

                    # Load horse/jockey for each runner
                    for r in runners:
                        if r.horse_id:
                            r.horse = db.query(Horse).filter(
                                Horse.id == r.horse_id
                            ).first()
                        if r.jockey_id:
                            r.jockey = db.query(Jockey).filter(
                                Jockey.id == r.jockey_id
                            ).first()

                    # Load results
                    results = []
                    if race.has_results:
                        race_result = db.query(RaceResult).filter(
                            RaceResult.race_id == race.id
                        ).first()
                        if race_result:
                            rr_list = db.query(RunnerResult).filter(
                                RunnerResult.race_result_id == race_result.id
                            ).all()
                            for rr in rr_list:
                                rr.runner = db.query(Runner).filter(
                                    Runner.id == rr.runner_id
                                ).first()
                                if rr.runner and rr.runner.horse_id:
                                    rr.runner.horse = db.query(Horse).filter(
                                        Horse.id == rr.runner.horse_id
                                    ).first()
                            results = rr_list

                    # Convert to text
                    doc_text = self.race_to_text(race, meet, runners, results)

                    # Create embedding
                    embedding = self.model.encode(doc_text).tolist()

                    # Metadata for filtering
                    track_name = meet.track.track_name if meet.track else 'Unknown'
                    metadata = {
                        'race_id': race.id,
                        'race_number': race.race_number or 0,
                        'track': track_name,
                        'date': str(meet.date),
                        'surface': race.surface or '',
                        'race_type': str(race.race_type or ''),
                        'has_results': bool(race.has_results),
                        'purse': race.purse or 0
                    }

                    batch_docs.append(doc_text)
                    batch_embeddings.append(embedding)
                    batch_metadatas.append(metadata)
                    batch_ids.append(f"race_{race.id}")

                    # Add in batches
                    if len(batch_ids) >= batch_size:
                        self.vector_store.add_races(
                            batch_docs, batch_embeddings,
                            batch_metadatas, batch_ids
                        )
                        embedded_count += len(batch_ids)
                        logger.info(f"  Embedded {embedded_count}/{len(races)} races...")
                        batch_docs, batch_embeddings = [], []
                        batch_metadatas, batch_ids = [], []

                except Exception as e:
                    logger.warning(f"Failed to embed race {race.id}: {e}")
                    continue

            # Add remaining
            if batch_ids:
                self.vector_store.add_races(
                    batch_docs, batch_embeddings,
                    batch_metadatas, batch_ids
                )
                embedded_count += len(batch_ids)

        logger.info(f"✓ Embedded {embedded_count} races total")
        return embedded_count