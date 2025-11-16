# claii/providers/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List

from google.genai import types  # we can generalize later

class LLMProvider(ABC):
    """Abstract interface all providers must implement."""

    @abstractmethod
    def generate(
        self,
        messages: List[types.Content],
        tools: list[Any] | None,
        system_prompt: str,
    ) -> Any:
        """Return the provider-native response object."""
        raise NotImplementedError
