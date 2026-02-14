"""MCP Server - RAG + Chat API for Horse Racing AI."""
import logging
import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag.vector_store import VectorStore
from src.rag.retriever import RaceRetriever
from src.chat.llm_handler import LLMHandler
from src.chat.racing_expert import RacingExpert

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize components (lazy - loaded on first request)
vector_store = VectorStore()
retriever = RaceRetriever(vector_store)
llm_handler = LLMHandler()
racing_expert = RacingExpert(retriever, llm_handler)


@app.route('/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({
        'status': 'healthy',
        'services': {
            'vector_store': vector_store.is_ready(),
            'llm': llm_handler.is_ready(),
        }
    })


@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint.

    Request:
    {
        "message": "Who should I bet on in Race 3 at Aqueduct?",
        "conversation_history": [...],  // optional
        "race_id": 502                  // optional context
    }
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'message required'}), 400

    message = data['message']
    history = data.get('conversation_history', [])
    race_id = data.get('race_id')

    logger.info(f"Chat request: {message[:100]}")

    try:
        response = racing_expert.chat(
            message=message,
            conversation_history=history,
            race_id=race_id
        )
        return jsonify(response)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/search', methods=['GET'])
def search():
    """
    Semantic search for historical races.

    Query params:
        q: search query
        limit: number of results (default 5)
    """
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 5))

    if not query:
        return jsonify({'error': 'q parameter required'}), 400

    try:
        results = retriever.search(query, limit=limit)
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/embed', methods=['POST'])
def embed_races():
    """
    Embed race data into vector store.
    Admin endpoint - call once to initialize or update.
    """
    from src.rag.embedder import RaceEmbedder
    embedder = RaceEmbedder(vector_store)

    try:
        count = embedder.embed_all_races()
        return jsonify({
            'status': 'success',
            'races_embedded': count
        })
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/mcp/tools', methods=['GET'])
def list_tools():
    """List available MCP tools."""
    from src.mcp.server import MCPServer
    mcp = MCPServer()
    return jsonify({'tools': mcp.list_tools()})


@app.route('/mcp/execute', methods=['POST'])
def execute_tool():
    """
    Execute an MCP tool.

    Request:
    {
        "tool": "get_todays_races",
        "params": {"date": "2026-02-07", "track": "AQU"}
    }
    """
    data = request.get_json()
    if not data or 'tool' not in data:
        return jsonify({'error': 'tool required'}), 400

    from src.mcp.server import MCPServer
    mcp = MCPServer()

    try:
        result = mcp.execute(data['tool'], data.get('params', {}))
        return jsonify(result)
    except Exception as e:
        logger.error(f"MCP tool error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting MCP Server...")
    logger.info(f"OpenRouter API key: {'✓ set' if os.getenv('OPENROUTER_API_KEY') else '✗ missing'}")

    app.run(host='0.0.0.0', port=5002, debug=True)