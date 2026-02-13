"""
Webhook Manager - HTTP trigger endpoints for agents and workflows
Each webhook gets a unique secret token; external services POST to it
to trigger the configured agent/workflow with an optional payload.
"""
import json
import os
import uuid
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
WEBHOOKS_FILE = os.path.join(DATA_DIR, "webhooks.json")
WEBHOOK_LOG_FILE = os.path.join(DATA_DIR, "webhook_log.json")

MAX_LOG_ENTRIES = 500


class WebhookManager:
    """Store and manage webhook registrations and their execution history."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._hooks: Dict[str, Dict] = {}   # token -> hook dict
        self._log: List[Dict] = []
        self._load()

    # ------------------------------------------------------------------ #
    # Persistence                                                          #
    # ------------------------------------------------------------------ #

    def _load(self):
        if os.path.exists(WEBHOOKS_FILE):
            try:
                with open(WEBHOOKS_FILE) as f:
                    self._hooks = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load webhooks: {e}")
                self._hooks = {}

        if os.path.exists(WEBHOOK_LOG_FILE):
            try:
                with open(WEBHOOK_LOG_FILE) as f:
                    self._log = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load webhook log: {e}")
                self._log = []

    def _save_hooks(self):
        try:
            with open(WEBHOOKS_FILE, "w") as f:
                json.dump(self._hooks, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save webhooks: {e}")

    def _save_log(self):
        try:
            # Keep only the most recent entries
            if len(self._log) > MAX_LOG_ENTRIES:
                self._log = self._log[-MAX_LOG_ENTRIES:]
            with open(WEBHOOK_LOG_FILE, "w") as f:
                json.dump(self._log, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save webhook log: {e}")

    # ------------------------------------------------------------------ #
    # CRUD                                                                 #
    # ------------------------------------------------------------------ #

    def create(
        self,
        name: str,
        agent_id: str,
        prompt_template: str,
        description: str = "",
        workflow_id: Optional[str] = None,
    ) -> Dict:
        """Create a new webhook; returns the full hook dict including token."""
        token = uuid.uuid4().hex
        hook = {
            "token": token,
            "name": name,
            "description": description,
            "agent_id": agent_id,
            "workflow_id": workflow_id,
            "prompt_template": prompt_template,
            "created_at": datetime.now().isoformat(),
            "last_triggered": None,
            "trigger_count": 0,
            "enabled": True,
        }
        self._hooks[token] = hook
        self._save_hooks()
        logger.info(f"Webhook created: {name} (token={token[:8]}…)")
        return {"success": True, "webhook": hook}

    def get(self, token: str) -> Optional[Dict]:
        return self._hooks.get(token)

    def list_all(self) -> List[Dict]:
        return list(self._hooks.values())

    def delete(self, token: str) -> Dict:
        if token not in self._hooks:
            return {"success": False, "error": "Webhook not found"}
        name = self._hooks[token]["name"]
        del self._hooks[token]
        self._save_hooks()
        logger.info(f"Webhook deleted: {name}")
        return {"success": True}

    def toggle(self, token: str, enabled: bool) -> Dict:
        if token not in self._hooks:
            return {"success": False, "error": "Webhook not found"}
        self._hooks[token]["enabled"] = enabled
        self._save_hooks()
        return {"success": True}

    def regenerate_token(self, old_token: str) -> Dict:
        """Replace the secret token (invalidates old URL)."""
        if old_token not in self._hooks:
            return {"success": False, "error": "Webhook not found"}
        hook = self._hooks.pop(old_token)
        new_token = uuid.uuid4().hex
        hook["token"] = new_token
        self._hooks[new_token] = hook
        self._save_hooks()
        return {"success": True, "webhook": hook}

    # ------------------------------------------------------------------ #
    # Execution                                                            #
    # ------------------------------------------------------------------ #

    def record_trigger(
        self,
        token: str,
        payload: Dict,
        result: str,
        success: bool,
        duration_ms: int,
    ):
        """Record a webhook execution in the log and update statistics."""
        hook = self._hooks.get(token)
        if hook:
            hook["last_triggered"] = datetime.now().isoformat()
            hook["trigger_count"] = hook.get("trigger_count", 0) + 1
            self._save_hooks()

        entry = {
            "id": uuid.uuid4().hex[:12],
            "token": token,
            "webhook_name": hook["name"] if hook else "unknown",
            "triggered_at": datetime.now().isoformat(),
            "payload": payload,
            "result": result[:500] if isinstance(result, str) else str(result)[:500],
            "success": success,
            "duration_ms": duration_ms,
        }
        self._log.append(entry)
        self._save_log()
        return entry

    def get_log(
        self,
        token: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        entries = self._log if token is None else [e for e in self._log if e["token"] == token]
        return list(reversed(entries[-limit:]))

    def build_prompt(self, hook: Dict, payload: Dict) -> str:
        """Substitute {{payload.*}} placeholders in the prompt template."""
        prompt = hook.get("prompt_template", "")
        # Replace {{payload}} with full JSON
        prompt = prompt.replace("{{payload}}", json.dumps(payload))
        # Replace {{payload.key}} with individual values
        for key, value in payload.items():
            prompt = prompt.replace(f"{{{{payload.{key}}}}}", str(value))
        return prompt


# Singleton
webhook_manager = WebhookManager()
