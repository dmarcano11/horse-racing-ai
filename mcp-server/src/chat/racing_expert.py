"""Racing expert persona and conversation handler."""
from src.rag.retriever import RaceRetriever
from src.chat.llm_handler import LLMHandler
from src.mcp.server import MCPServer
import logging
import json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert horse racing analyst and handicapper with 
20+ years of experience. You have access to real-time race data, ML predictions, 
and historical race results through your tools.

## Your Expertise:
- Reading and interpreting race cards
- Analyzing jockey and trainer statistics  
- Understanding track conditions and their impact
- Interpreting morning line odds vs actual probabilities
- Identifying value bets using ML model predictions
- Explaining complex racing concepts in plain English

## Your ML Model:
- Random Forest classifier trained on 1,300+ races
- 55 features per runner including jockey/trainer stats, pace, odds
- ROC-AUC of 0.604 (18% better than random)
- Best used to identify value when model probability > implied odds probability

## Communication Style:
- Be direct and confident in your analysis
- Always explain your reasoning
- Mention the model's limitations honestly
- Never guarantee winners - racing is inherently unpredictable
- Format responses clearly with key picks highlighted

## Important Notes:
- When asked about specific races, use the race data provided in context
- When model probability significantly exceeds implied odds probability, flag as VALUE
- Always remind users to bet responsibly
"""


class RacingExpert:
    """Orchestrates RAG + MCP + LLM for intelligent racing analysis."""

    def __init__(self, retriever: RaceRetriever, llm_handler: LLMHandler):
        self.retriever = retriever
        self.llm = llm_handler
        self.mcp = MCPServer()

    def chat(
        self,
        message: str,
        conversation_history: list = None,
        race_id: int = None
    ) -> dict:
        """
        Process a user message and return expert analysis.

        Args:
            message: User's question
            conversation_history: Previous messages
            race_id: Optional specific race context

        Returns:
            Dict with response and metadata
        """
        if conversation_history is None:
            conversation_history = []

        # 1. Gather context using MCP tools
        context = self._gather_context(message, race_id)

        # 2. Build messages for LLM
        messages = self._build_messages(
            message, conversation_history, context
        )

        # 3. Get LLM response
        response_text = self.llm.chat(messages)

        return {
            'response': response_text,
            'context_used': {
                'race_id': race_id,
                'rag_results': len(context.get('rag_results', [])),
                'tools_called': context.get('tools_called', [])
            }
        }

    def _gather_context(self, message: str, race_id: int = None) -> dict:
        """Gather relevant context using MCP tools and RAG."""
        context = {
            'race_data': None,
            'predictions': None,
            'rag_results': [],
            'tools_called': []
        }

        # Get specific race data if race_id provided
        if race_id:
            try:
                race_data = self.mcp.execute(
                    'get_race_details', {'race_id': race_id}
                )
                context['race_data'] = race_data
                context['tools_called'].append('get_race_details')
                logger.info(f"Fetched race data for race {race_id}")
            except Exception as e:
                logger.warning(f"Could not fetch race {race_id}: {e}")

        # Detect if message is asking about today's races
        if any(word in message.lower() for word in
               ['today', 'tonight', 'races today', 'running today']):
            try:
                races = self.mcp.execute('get_todays_races', {})
                context['todays_races'] = races
                context['tools_called'].append('get_todays_races')
            except Exception as e:
                logger.warning(f"Could not fetch today's races: {e}")

        # RAG search for relevant historical context
        try:
            rag_results = self.retriever.search(message, limit=3)
            context['rag_results'] = rag_results
        except Exception as e:
            logger.warning(f"RAG search failed: {e}")

        return context

    def _build_messages(
        self,
        message: str,
        history: list,
        context: dict
    ) -> list:
        """Build message list for LLM."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add context as system message
        context_text = self._format_context(context)
        if context_text:
            messages.append({
                "role": "system",
                "content": f"## Current Context:\n{context_text}"
            })

        # Add conversation history (last 10 messages to stay within context)
        for msg in history[-10:]:
            if msg.get('role') in ['user', 'assistant']:
                messages.append(msg)

        # Add current message
        messages.append({"role": "user", "content": message})

        return messages

    def _format_context(self, context: dict) -> str:
        """Format context data for LLM consumption."""
        parts = []

        # Race card data
        if context.get('race_data'):
            race_data = context['race_data']
            race = race_data.get('race', {})

            parts.append(f"### Race Card")
            parts.append(
                f"Race {race.get('raceNumber')} at "
                f"{race.get('trackName')} - "
                f"{race.get('distanceValue')}{race.get('distanceUnit', 'F')} "
                f"{race.get('surface', '')} - "
                f"Purse: ${race.get('purse', 0):,}"
            )

            runners = race_data.get('runners', [])
            if runners:
                parts.append("\nRunners (sorted by ML rank):")
                for r in runners:
                    prob = r.get('winProbabilityNormalized', 0)
                    ml_odds = r.get('morningLineOdds', '—')
                    rank = r.get('modelRank', '—')
                    result = f" → FINISHED {r['finishPosition']}" \
                        if r.get('finishPosition') else ""
                    parts.append(
                        f"  #{r.get('postPosition', '?')} "
                        f"{r.get('horseName', 'Unknown')} | "
                        f"ML: {ml_odds} | "
                        f"AI Prob: {prob*100:.1f}% | "
                        f"Rank: {rank}{result}"
                    )

        # Today's races summary
        if context.get('todays_races'):
            races = context['todays_races']
            parts.append(
                f"\n### Today's Racing\n"
                f"{races.get('race_count', 0)} races available on "
                f"{races.get('date', 'today')}"
            )

        # RAG historical context
        if context.get('rag_results'):
            relevant = [r for r in context['rag_results']
                       if r.get('relevance_score', 0) > 0.35]
            if relevant:
                parts.append("\n### Relevant Historical Races")
                for r in relevant[:2]:
                    parts.append(
                        f"[Relevance: {r['relevance_score']:.2f}]\n"
                        f"{r['document'][:300]}..."
                    )

        return "\n".join(parts)