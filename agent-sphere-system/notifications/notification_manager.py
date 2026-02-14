"""
Notification Manager — persistent, read/unread notifications with alert keyword matching.

Storage: data/notifications.json (capped at MAX_ENTRIES)
Settings: data/notification_settings.json
"""
import json
import os
import uuid
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
NOTIF_FILE = os.path.join(DATA_DIR, "notifications.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "notification_settings.json")

MAX_ENTRIES = 200

VALID_TYPES = {"info", "success", "warning", "error"}

_DEFAULT_SETTINGS = {
    "alert_keywords": ["error", "failed", "critical", "alert", "down", "offline"],
    "budget_threshold": 1000.0,          # monthly spend threshold for finance agent
    "notify_on_schedule_success": True,
    "notify_on_schedule_failure": True,
    "notify_on_webhook": True,
    "notify_on_keyword_match": True,
    "browser_push_enabled": False,
    "push_subscriptions": [],            # list of Web Push subscription objects
}


class NotificationManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._lock = threading.Lock()
        self._notifs: List[Dict] = []
        self._settings: Dict = dict(_DEFAULT_SETTINGS)
        self._broadcast_fn = None   # set by api_server: fn(event, data)
        self._load()

    # ── persistence ──────────────────────────────────────────────────────────

    def _load(self):
        if os.path.exists(NOTIF_FILE):
            try:
                with open(NOTIF_FILE) as f:
                    self._notifs = json.load(f)
            except Exception as e:
                logger.warning("Could not load notifications.json: %s", e)
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE) as f:
                    data = json.load(f)
                self._settings.update(data)
            except Exception as e:
                logger.warning("Could not load notification_settings.json: %s", e)

    def _save(self):
        try:
            with open(NOTIF_FILE, "w") as f:
                json.dump(self._notifs, f, indent=2)
        except Exception as e:
            logger.error("Failed to save notifications: %s", e)

    def _save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            logger.error("Failed to save notification settings: %s", e)

    # ── settings ─────────────────────────────────────────────────────────────

    def get_settings(self) -> Dict:
        return dict(self._settings)

    def update_settings(self, data: Dict) -> Dict:
        allowed = set(_DEFAULT_SETTINGS.keys()) - {"push_subscriptions"}
        for k, v in data.items():
            if k in allowed:
                self._settings[k] = v
        self._save_settings()
        return self.get_settings()

    def set_broadcast(self, fn):
        self._broadcast_fn = fn

    # ── push subscriptions ────────────────────────────────────────────────────

    def add_push_subscription(self, subscription: Dict):
        subs = self._settings.get("push_subscriptions", [])
        endpoint = subscription.get("endpoint", "")
        if not any(s.get("endpoint") == endpoint for s in subs):
            subs.append(subscription)
            self._settings["push_subscriptions"] = subs
            self._save_settings()

    def remove_push_subscription(self, endpoint: str):
        subs = [s for s in self._settings.get("push_subscriptions", [])
                if s.get("endpoint") != endpoint]
        self._settings["push_subscriptions"] = subs
        self._save_settings()

    def get_push_subscriptions(self) -> List[Dict]:
        return self._settings.get("push_subscriptions", [])

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def add(
        self,
        title: str,
        message: str,
        notif_type: str = "info",
        source: str = "system",    # scheduler / webhook / agent / manual
        agent_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        if notif_type not in VALID_TYPES:
            notif_type = "info"

        entry = {
            "id": uuid.uuid4().hex[:12],
            "title": title,
            "message": message[:500],
            "type": notif_type,
            "source": source,
            "agent_id": agent_id or "",
            "metadata": metadata or {},
            "read": False,
            "created_at": datetime.now().isoformat(),
        }

        with self._lock:
            self._notifs.append(entry)
            # Cap at MAX_ENTRIES — remove oldest first
            if len(self._notifs) > MAX_ENTRIES:
                self._notifs = self._notifs[-MAX_ENTRIES:]
            self._save()

        # Broadcast via WebSocket
        if self._broadcast_fn:
            try:
                self._broadcast_fn("notification", entry)
            except Exception:
                pass

        return entry

    def get_all(self, limit: int = 50, unread_only: bool = False) -> List[Dict]:
        with self._lock:
            notifs = list(reversed(self._notifs))  # newest first
        if unread_only:
            notifs = [n for n in notifs if not n.get("read")]
        return notifs[:limit]

    def unread_count(self) -> int:
        with self._lock:
            return sum(1 for n in self._notifs if not n.get("read"))

    def mark_read(self, notif_id: str) -> bool:
        with self._lock:
            for n in self._notifs:
                if n["id"] == notif_id:
                    n["read"] = True
                    self._save()
                    return True
        return False

    def mark_all_read(self):
        with self._lock:
            for n in self._notifs:
                n["read"] = True
            self._save()

    def clear_all(self):
        with self._lock:
            self._notifs = []
            self._save()

    # ── alert keyword matching ─────────────────────────────────────────────────

    def check_response_for_alerts(self, response: str, agent_id: str = ""):
        """Scan agent response for configured alert keywords and create a notification."""
        if not self._settings.get("notify_on_keyword_match"):
            return
        keywords = self._settings.get("alert_keywords", [])
        response_lower = response.lower()
        matched = [kw for kw in keywords if kw.lower() in response_lower]
        if matched:
            self.add(
                title="⚠️ Alert keyword detected",
                message=f"Keywords [{', '.join(matched)}] found in response from '{agent_id}'.\n\n{response[:200]}",
                notif_type="warning",
                source="agent",
                agent_id=agent_id,
                metadata={"keywords": matched},
            )

    def check_budget_alert(self, monthly_spend: float, agent_id: str = "finance"):
        """Notify if monthly spend exceeds configured threshold."""
        threshold = self._settings.get("budget_threshold", 1000.0)
        if monthly_spend >= threshold:
            self.add(
                title="💰 Budget threshold exceeded",
                message=f"Monthly spend ${monthly_spend:.2f} exceeds threshold ${threshold:.2f}.",
                notif_type="warning",
                source="agent",
                agent_id=agent_id,
            )

    # ── convenience wrappers ──────────────────────────────────────────────────

    def notify_schedule_result(self, job_name: str, agent_id: str, result: str, success: bool):
        settings = self._settings
        if success and not settings.get("notify_on_schedule_success"):
            return
        if not success and not settings.get("notify_on_schedule_failure"):
            return
        self.add(
            title=f"{'✅' if success else '❌'} Schedule: {job_name}",
            message=result[:300],
            notif_type="success" if success else "error",
            source="scheduler",
            agent_id=agent_id,
            metadata={"job_name": job_name, "success": success},
        )

    def notify_webhook_trigger(self, webhook_name: str, agent_id: str, result: str, success: bool):
        if not self._settings.get("notify_on_webhook"):
            return
        self.add(
            title=f"🔗 Webhook: {webhook_name}",
            message=result[:300],
            notif_type="success" if success else "error",
            source="webhook",
            agent_id=agent_id,
            metadata={"webhook_name": webhook_name, "success": success},
        )


notification_manager = NotificationManager()
