# claii/providers/google_genai.py
import os
from typing import Any, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .base import LLMProvider

class GoogleGenAIProvider(LLMProvider):
    def __init__(self, model: str = "gemini-2.0-flash-001") -> None:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        messages: List[types.Content],
        tools: list[Any] | None,
        system_prompt: str,
    ) -> Any:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=tools or [],
        )
        return self.client.models.generate_content(
            model=self.model,
            contents=messages,
            config=config,
        )
