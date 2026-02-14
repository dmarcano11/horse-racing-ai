"""MCP Server - tools for interacting with horse racing data."""
import sys
import requests
from pathlib import Path
from datetime import date
import logging

DATA_INGESTION_PATH = str(
    Path(__file__).parent.parent.parent.parent / 'data-ingestion'
)
if DATA_INGESTION_PATH not in sys.path:
    sys.path.insert(0, DATA_INGESTION_PATH)

if 'src' in sys.modules:
    del sys.modules['src']

logger = logging.getLogger(__name__)
SPRING_BOOT_URL = "http://localhost:8080"


class MCPServer:
    """MCP tools for horse racing data access."""

    def list_tools(self) -> list:
        """Return list of available tools."""
        return [
            {
                'name': 'get_todays_races',
                'description': 'Get all races for today or a specific date',
                'parameters': {
                    'date': 'YYYY-MM-DD format (optional, defaults to today)',
                    'track': 'Track code filter e.g. AQU (optional)'
                }
            },
            {
                'name': 'get_race_details',
                'description': 'Get full race card with runners and ML predictions',
                'parameters': {
                    'race_id': 'Database race ID (required)'
                }
            },
            {
                'name': 'get_predictions',
                'description': 'Get ML win probability predictions for a race',
                'parameters': {
                    'race_id': 'Database race ID (required)',
                }
            },
            {
                'name': 'search_historical_races',
                'description': 'Semantic search through historical race data',
                'parameters': {
                    'query': 'Natural language search query (required)',
                    'limit': 'Number of results (optional, default 5)'
                }
            },
            {
                'name': 'get_track_stats',
                'description': 'Get performance statistics for a track',
                'parameters': {
                    'track_code': 'Track code e.g. AQU (required)'
                }
            }
        ]

    def execute(self, tool_name: str, params: dict) -> dict:
        """Execute an MCP tool."""
        tools = {
            'get_todays_races': self._get_todays_races,
            'get_race_details': self._get_race_details,
            'get_predictions': self._get_predictions,
            'search_historical_races': self._search_historical_races,
            'get_track_stats': self._get_track_stats,
        }

        if tool_name not in tools:
            return {'error': f"Unknown tool: {tool_name}"}

        try:
            return tools[tool_name](params)
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            return {'error': str(e)}

    def _get_todays_races(self, params: dict) -> dict:
        """Get races for a date."""
        race_date = params.get('date', str(date.today()))
        track = params.get('track')

        try:
            response = requests.get(
                f"{SPRING_BOOT_URL}/api/races",
                params={'date': race_date},
                timeout=5
            )
            races = response.json()

            # Filter by track if specified
            if track:
                races = [r for r in races
                         if r.get('trackCode', '').upper() == track.upper()]

            return {
                'date': race_date,
                'race_count': len(races),
                'races': races
            }
        except Exception as e:
            return {'error': f"Could not fetch races: {e}"}

    def _get_race_details(self, params: dict) -> dict:
        """Get full race card."""
        race_id = params.get('race_id')
        if not race_id:
            return {'error': 'race_id required'}

        try:
            response = requests.get(
                f"{SPRING_BOOT_URL}/api/races/{race_id}/card",
                params={'predictions': 'true'},
                timeout=15  # Longer timeout for ML predictions
            )
            return response.json()
        except Exception as e:
            return {'error': f"Could not fetch race details: {e}"}

    def _get_predictions(self, params: dict) -> dict:
        """Get ML predictions for a race."""
        race_id = params.get('race_id')
        if not race_id:
            return {'error': 'race_id required'}

        try:
            response = requests.get(
                f"{SPRING_BOOT_URL}/api/predictions/race/{race_id}",
                timeout=15
            )
            return response.json()
        except Exception as e:
            return {'error': f"Could not fetch predictions: {e}"}

    def _search_historical_races(self, params: dict) -> dict:
        """Semantic search through race history."""
        from src.rag.vector_store import VectorStore
        from src.rag.retriever import RaceRetriever

        query = params.get('query')
        if not query:
            return {'error': 'query required'}

        limit = int(params.get('limit', 5))

        try:
            vs = VectorStore()
            retriever = RaceRetriever(vs)
            results = retriever.search(query, limit=limit)

            return {
                'query': query,
                'results': results,
                'count': len(results)
            }
        except Exception as e:
            return {'error': f"Search failed: {e}"}

    def _get_track_stats(self, params: dict) -> dict:
        """Get track statistics."""
        track_code = params.get('track_code')
        if not track_code:
            return {'error': 'track_code required'}

        try:
            # Get track from Spring Boot
            tracks_response = requests.get(
                f"{SPRING_BOOT_URL}/api/tracks",
                timeout=5
            )
            tracks = tracks_response.json()
            track = next(
                (t for t in tracks
                 if t['trackId'].upper() == track_code.upper()),
                None
            )

            if not track:
                return {'error': f"Track {track_code} not found"}

            return {
                'track': track,
                'note': 'Detailed stats available after more data is collected'
            }
        except Exception as e:
            return {'error': f"Could not fetch track stats: {e}"}