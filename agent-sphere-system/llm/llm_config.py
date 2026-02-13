"""
LLM Config Manager — stores provider API keys and default settings locally.
Keys are saved in data/llm_config.json (never committed to git).
"""
import json
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'llm_config.json')
os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

PROVIDERS = {
    "ollama": {
        "name": "Ollama (Local)",
        "description": "Local models via Ollama — no API key needed",
        "requires_key": False,
        "models": ["qwen2.5:14b", "llama3.1:8b", "mistral:7b", "gemma2:9b"],
        "default_model": "qwen2.5:14b",
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "description": "Claude Sonnet 4.5 / Opus 4.6 via Anthropic API",
        "requires_key": True,
        "models": ["claude-sonnet-4-5-20250929", "claude-opus-4-6", "claude-haiku-4-5-20251001"],
        "default_model": "claude-sonnet-4-5-20250929",
    },
    "openai": {
        "name": "OpenAI",
        "description": "GPT-4o and variants via OpenAI API",
        "requires_key": True,
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "default_model": "gpt-4o",
    },
    "google": {
        "name": "Google Gemini",
        "description": "Gemini 1.5 Pro / Flash via Google AI API",
        "requires_key": True,
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"],
        "default_model": "gemini-1.5-flash",
    },
}

_DEFAULT_CONFIG = {
    "default_provider": "ollama",
    "default_model": "qwen2.5:14b",
    "failover_order": ["ollama"],   # providers to try in order on failure
    "providers": {
        "ollama": {"enabled": True, "api_key": "", "base_url": "http://localhost:11434", "model": "qwen2.5:14b"},
        "anthropic": {"enabled": False, "api_key": "", "model": "claude-sonnet-4-5-20250929"},
        "openai": {"enabled": False, "api_key": "", "model": "gpt-4o"},
        "google": {"enabled": False, "api_key": "", "model": "gemini-1.5-flash"},
    }
}


class LLMConfigManager:

    def __init__(self):
        self._config = self._load()

    def _load(self) -> Dict:
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH) as f:
                    saved = json.load(f)
                    # Merge with defaults so new keys appear automatically
                    merged = dict(_DEFAULT_CONFIG)
                    merged.update(saved)
                    return merged
            except Exception:
                pass
        return dict(_DEFAULT_CONFIG)

    def _save(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self._config, f, indent=2)

    # ── Getters ──────────────────────────────────────────────────────────────

    def get_provider_config(self, provider: str) -> Dict:
        return self._config["providers"].get(provider, {})

    def get_api_key(self, provider: str) -> str:
        return self.get_provider_config(provider).get("api_key", "")

    def get_model(self, provider: str) -> str:
        return self.get_provider_config(provider).get("model", PROVIDERS.get(provider, {}).get("default_model", ""))

    def get_base_url(self, provider: str) -> str:
        return self.get_provider_config(provider).get("base_url", "")

    def get_default_provider(self) -> str:
        return self._config.get("default_provider", "ollama")

    def get_failover_order(self) -> List[str]:
        return self._config.get("failover_order", ["ollama"])

    def is_enabled(self, provider: str) -> bool:
        return self.get_provider_config(provider).get("enabled", False)

    def list_enabled_providers(self) -> List[str]:
        return [p for p in PROVIDERS if self.is_enabled(p)]

    # ── Setters ──────────────────────────────────────────────────────────────

    def set_provider(self, provider: str, api_key: str = None, model: str = None,
                     enabled: bool = None, base_url: str = None) -> Dict:
        if provider not in PROVIDERS:
            return {"success": False, "error": f"Unknown provider: {provider}"}

        cfg = self._config["providers"].setdefault(provider, {})
        if api_key is not None:
            cfg["api_key"] = api_key
        if model is not None:
            cfg["model"] = model
        if enabled is not None:
            cfg["enabled"] = enabled
        if base_url is not None:
            cfg["base_url"] = base_url

        # Auto-enable ollama (no key needed)
        if provider == "ollama":
            cfg["enabled"] = True

        self._save()
        return {"success": True, "provider": provider}

    def set_default_provider(self, provider: str, model: str = None) -> Dict:
        if provider not in PROVIDERS:
            return {"success": False, "error": f"Unknown provider: {provider}"}
        self._config["default_provider"] = provider
        if model:
            self._config["default_model"] = model
        self._save()
        return {"success": True}

    def set_failover_order(self, order: List[str]) -> Dict:
        valid = [p for p in order if p in PROVIDERS]
        self._config["failover_order"] = valid
        self._save()
        return {"success": True, "failover_order": valid}

    def to_dict(self, mask_keys: bool = True) -> Dict:
        """Return config dict, optionally masking API keys."""
        import copy
        cfg = copy.deepcopy(self._config)
        if mask_keys:
            for p_cfg in cfg["providers"].values():
                key = p_cfg.get("api_key", "")
                p_cfg["api_key"] = ("•" * 8 + key[-4:]) if len(key) > 4 else ("•" * len(key))
        cfg["provider_metadata"] = PROVIDERS
        return cfg


# Singleton
llm_config = LLMConfigManager()
