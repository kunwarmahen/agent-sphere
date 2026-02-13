"""
LLM Router — unified interface for all LLM providers with automatic failover.
Usage:
    from llm.llm_router import llm_router
    response = llm_router.chat(messages, provider="anthropic")
"""
import logging
from typing import Dict, List, Optional

from llm.llm_config import llm_config, PROVIDERS

logger = logging.getLogger(__name__)


class LLMRouter:
    """Routes LLM calls to the configured provider with failover support."""

    # ── Provider implementations ──────────────────────────────────────────────

    def _call_ollama(self, messages: List[Dict], model: str, base_url: str) -> str:
        import requests
        url = base_url.rstrip("/") or "http://localhost:11434"
        resp = requests.post(
            f"{url}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=120
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def _call_anthropic(self, messages: List[Dict], model: str, api_key: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        # Separate system message from conversation
        system = ""
        filtered = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                filtered.append({"role": m["role"], "content": m["content"]})

        kwargs = {"model": model, "max_tokens": 4096, "messages": filtered}
        if system:
            kwargs["system"] = system

        response = client.messages.create(**kwargs)
        return response.content[0].text

    def _call_openai(self, messages: List[Dict], model: str, api_key: str) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=4096
        )
        return resp.choices[0].message.content

    def _call_google(self, messages: List[Dict], model: str, api_key: str) -> str:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        gemini = genai.GenerativeModel(model)

        # Convert messages to Gemini format
        history = []
        last_user_msg = ""
        for m in messages:
            if m["role"] == "system":
                # Prepend system message to first user message
                last_user_msg = m["content"] + "\n\n"
            elif m["role"] == "user":
                history.append({"role": "user", "parts": [last_user_msg + m["content"]]})
                last_user_msg = ""
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})

        if not history:
            return "No messages to process"

        # Last user message starts the chat
        chat_history = history[:-1]
        last_msg = history[-1]["parts"][0] if history[-1]["role"] == "user" else ""

        chat = gemini.start_chat(history=chat_history)
        response = chat.send_message(last_msg)
        return response.text

    # ── Core routing ──────────────────────────────────────────────────────────

    def _call_provider(self, provider: str, messages: List[Dict]) -> str:
        """Call a specific provider. Raises on failure."""
        cfg = llm_config.get_provider_config(provider)
        model = cfg.get("model") or PROVIDERS[provider]["default_model"]

        if provider == "ollama":
            base_url = cfg.get("base_url", "http://localhost:11434")
            return self._call_ollama(messages, model, base_url)
        elif provider == "anthropic":
            api_key = cfg.get("api_key", "")
            if not api_key:
                raise ValueError("Anthropic API key not configured")
            return self._call_anthropic(messages, model, api_key)
        elif provider == "openai":
            api_key = cfg.get("api_key", "")
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            return self._call_openai(messages, model, api_key)
        elif provider == "google":
            api_key = cfg.get("api_key", "")
            if not api_key:
                raise ValueError("Google API key not configured")
            return self._call_google(messages, model, api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def chat(
        self,
        messages: List[Dict],
        provider: Optional[str] = None,
        use_failover: bool = True,
    ) -> str:
        """
        Call the LLM with automatic failover.
        provider: override which provider to use (None = use default)
        use_failover: if True, try failover_order on failure
        """
        primary = provider or llm_config.get_default_provider()
        failover = llm_config.get_failover_order() if use_failover else []

        # Build attempt order: primary first, then failover (deduped)
        order = [primary]
        for p in failover:
            if p != primary:
                order.append(p)

        last_error = None
        for p in order:
            try:
                logger.debug(f"[LLM] Trying provider: {p}")
                result = self._call_provider(p, messages)
                if p != primary:
                    logger.info(f"[LLM] Failover succeeded with: {p}")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"[LLM] Provider '{p}' failed: {e}")

        # All providers failed — return error string (never raise, agents handle errors)
        err = f"Error: All LLM providers failed. Last error: {last_error}"
        logger.error(f"[LLM] {err}")
        return err

    def test_provider(self, provider: str) -> Dict:
        """Test connectivity to a provider with a simple ping message."""
        try:
            result = self._call_provider(
                provider,
                [{"role": "user", "content": "Reply with exactly: OK"}]
            )
            return {"success": True, "provider": provider, "response": result[:100]}
        except Exception as e:
            return {"success": False, "provider": provider, "error": str(e)}


# Singleton
llm_router = LLMRouter()
