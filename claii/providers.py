# claii/providers.py

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


class GeminiProvider:
    """
    Thin wrapper around Google Gemini so the agent code doesn't depend
    directly on the SDK. Later I'll add OpenAIProvider, AnthropicProvider, etc.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-001") -> None:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(
        self,
        *,
        messages: list[types.Content],
        tools: list[types.Tool],
        system_prompt: str,
    ):
        """
        Normalised interface the agent can call.
        """
        return self.client.models.generate_content(
            model=self.model_name,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=tools,
                system_instruction=system_prompt,
            ),
        )


def get_provider() -> GeminiProvider:
    """
    For now always return Gemini; later we can branch on env vars, config files, flags, etc.
    """
    return GeminiProvider()
