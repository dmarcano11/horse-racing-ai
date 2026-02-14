"""OpenRouter LLM integration."""
from openai import OpenAI
import os
import logging

logger = logging.getLogger(__name__)


class LLMHandler:
    """Handles communication with OpenRouter LLM API."""

    def __init__(self):
        self.client = None
        self.model = "anthropic/claude-haiku-4-5"  # Fast + cheap
        self._initialize()

    def _initialize(self):
        """Initialize OpenRouter client."""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.error("OPENROUTER_API_KEY not set!")
            return

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        logger.info("✓ OpenRouter client initialized")

    def is_ready(self) -> bool:
        return self.client is not None

    def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """
        Send messages to LLM and get response.

        Args:
            messages: List of {role, content} dicts
            temperature: Creativity (0=focused, 1=creative)
            max_tokens: Max response length
            stream: Whether to stream response

        Returns:
            Response text
        """
        if not self.client:
            raise RuntimeError("LLM client not initialized")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers={
                "HTTP-Referer": "https://horse-racing-ai.com",
                "X-Title": "Horse Racing AI"
            }
        )

        return response.choices[0].message.content

    def chat_stream(self, messages: list):
        """Stream response tokens for real-time UI updates."""
        if not self.client:
            raise RuntimeError("LLM client not initialized")

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            stream=True,
            extra_headers={
                "HTTP-Referer": "https://horse-racing-ai.com",
                "X-Title": "Horse Racing AI"
            }
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content