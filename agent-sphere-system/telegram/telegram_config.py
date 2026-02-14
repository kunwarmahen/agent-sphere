"""
Telegram configuration — bot token, allowed user IDs, enable/disable.
Stored in data/telegram_config.json (never committed; add to .gitignore).
"""
import json
import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CONFIG_FILE = os.path.join(DATA_DIR, "telegram_config.json")

_DEFAULTS = {
    "enabled": False,
    "bot_token": "",
    "allowed_user_ids": [],   # list of int Telegram user IDs
    "notify_on_schedule": True,  # push scheduled-job results to Telegram
}


class TelegramConfig:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._cfg: dict = dict(_DEFAULTS)
        self._load()

    # ── persistence ──────────────────────────────────────────────────────────

    def _load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    data = json.load(f)
                self._cfg.update(data)
            except Exception as e:
                logger.warning("Could not load telegram_config.json: %s", e)

    def _save(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self._cfg, f, indent=2)

    # ── public API ───────────────────────────────────────────────────────────

    def get(self) -> dict:
        return dict(self._cfg)

    def update(self, data: dict) -> dict:
        allowed_keys = set(_DEFAULTS.keys())
        for k, v in data.items():
            if k in allowed_keys:
                self._cfg[k] = v
        self._save()
        return self.get()

    @property
    def enabled(self) -> bool:
        return bool(self._cfg.get("enabled")) and bool(self._cfg.get("bot_token"))

    @property
    def bot_token(self) -> str:
        return self._cfg.get("bot_token", "")

    @property
    def allowed_user_ids(self) -> List[int]:
        return [int(uid) for uid in self._cfg.get("allowed_user_ids", [])]

    @property
    def notify_on_schedule(self) -> bool:
        return bool(self._cfg.get("notify_on_schedule", True))

    def is_allowed(self, user_id: int) -> bool:
        """Return True if user_id is in the allowed list (or list is empty = allow all)."""
        allowed = self.allowed_user_ids
        if not allowed:
            return True
        return int(user_id) in allowed


telegram_config = TelegramConfig()
