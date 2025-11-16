# claii/config.py
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    provider: str = os.getenv("CLAII_PROVIDER", "google-genai")
    model: str = os.getenv("CLAII_MODEL", "gemini-2.0-flash-001")

def get_provider_config() -> ProviderConfig:
    return ProviderConfig()
