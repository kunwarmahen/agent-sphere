"""
Schedule Intent Detector
Analyzes chat messages to detect scheduling intent using the LLM.
Extracts: schedule type, timing, recurrence, agent/workflow, prompt.
"""

import json
import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:14b"

INTENT_SYSTEM_PROMPT = """You are a scheduling intent detector. Analyze the user message and determine if they want to schedule a recurring or future task.

SCHEDULING KEYWORDS to look for: every, daily, weekly, monthly, hourly, at [time], each morning/evening/night, remind me, schedule, automate, run at, set up a job, cron.

If this is a scheduling request, extract the details. If NOT a scheduling request (just a regular question or task), return is_schedule: false.

Today's date/time: {now}

Respond ONLY with raw JSON (no markdown):
{{
  "is_schedule": true/false,
  "confidence": 0.0-1.0,
  "job_name": "Short descriptive name for the job",
  "agent_id": "which agent: home | calendar | finance | orchestrator",
  "task_prompt": "The actual task to execute (rewritten as a clear instruction)",
  "schedule_type": "cron | interval | one_shot",
  "schedule_desc": "Human-readable description e.g. 'Every day at 7:00 AM'",
  "cron": {{
    "hour": null,
    "minute": 0,
    "day_of_week": "*",
    "day": "*",
    "month": "*"
  }},
  "interval": {{
    "hours": 0,
    "minutes": 0
  }},
  "one_shot_offset_minutes": null
}}

Rules:
- "every morning" = cron hour=7, minute=0
- "every evening" = cron hour=18, minute=0
- "every night" = cron hour=22, minute=0
- "every hour" = interval hours=1
- "every 30 minutes" = interval minutes=30
- "every day at 9am" = cron hour=9, minute=0
- "every Monday at 8am" = cron hour=8, minute=0, day_of_week=mon
- "in 30 minutes" = one_shot one_shot_offset_minutes=30
- "tomorrow at 3pm" = one_shot one_shot_offset_minutes=(calculate from now)
- weekday abbreviations: mon,tue,wed,thu,fri,sat,sun
- If no specific time mentioned for daily/weekly cron, default hour=8, minute=0
- agent_id should be "orchestrator" when the task spans multiple agents or is unclear
"""


def _call_ollama(prompt: str) -> str:
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT.format(now=datetime.now().strftime("%Y-%m-%d %H:%M"))},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except Exception as e:
        logger.error(f"[SCHEDULE_INTENT] Ollama error: {e}")
        return ""


def _extract_json(text: str) -> Optional[Dict]:
    """Extract JSON from LLM response"""
    try:
        start = text.find('{')
        if start == -1:
            return None
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    return json.loads(text[start:i+1])
    except Exception:
        pass
    return None


def detect_schedule_intent(message: str) -> Optional[Dict]:
    """
    Analyze a message for scheduling intent.
    Returns a schedule spec dict if scheduling is detected, None otherwise.
    """
    # Quick heuristic pre-filter — only call LLM if scheduling keywords present
    schedule_keywords = [
        'every', 'daily', 'weekly', 'monthly', 'hourly', 'each',
        'remind me', 'schedule', 'automate', 'run at', 'set up',
        'at ', 'every morning', 'every evening', 'every night',
        'cron', 'recurring', 'periodically', 'in 30 minutes',
        'tomorrow', 'each day', 'each week'
    ]
    lower_msg = message.lower()
    if not any(kw in lower_msg for kw in schedule_keywords):
        return None

    raw = _call_ollama(message)
    if not raw:
        return None

    parsed = _extract_json(raw)
    if not parsed or not parsed.get("is_schedule"):
        return None

    if parsed.get("confidence", 0) < 0.6:
        return None

    return parsed


def build_confirmation_message(intent: Dict) -> str:
    """Build a human-readable confirmation message for the user"""
    name = intent.get("job_name", "Scheduled Task")
    desc = intent.get("schedule_desc", "")
    task = intent.get("task_prompt", "")
    agent = intent.get("agent_id", "orchestrator")

    return (
        f"I'd like to schedule: **{name}**\n\n"
        f"- **Schedule**: {desc}\n"
        f"- **Agent**: {agent}\n"
        f"- **Task**: {task}\n\n"
        f"Shall I create this schedule? Reply **yes** to confirm or **no** to cancel."
    )


def intent_to_job_spec(intent: Dict) -> Dict:
    """
    Convert a detected intent into a job spec ready for SchedulerEngine.
    Returns a dict with job_id plus the right add_* kwargs.
    """
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    schedule_type = intent.get("schedule_type", "cron")
    name = intent.get("job_name", "Scheduled Task")
    agent_id = intent.get("agent_id", "orchestrator")
    prompt = intent.get("task_prompt", "")
    schedule_desc = intent.get("schedule_desc", "")

    spec = {
        "job_id": job_id,
        "name": name,
        "agent_id": agent_id,
        "prompt": prompt,
        "schedule_desc": schedule_desc,
        "schedule_type": schedule_type,
    }

    if schedule_type == "cron":
        cron = intent.get("cron", {})
        spec["cron"] = {
            "hour": cron.get("hour"),
            "minute": cron.get("minute", 0),
            "day_of_week": cron.get("day_of_week", "*"),
            "day": cron.get("day", "*"),
            "month": cron.get("month", "*"),
        }
    elif schedule_type == "interval":
        interval = intent.get("interval", {})
        spec["interval"] = {
            "hours": interval.get("hours", 0),
            "minutes": interval.get("minutes", 0),
        }
    elif schedule_type == "one_shot":
        offset = intent.get("one_shot_offset_minutes", 60)
        spec["run_at"] = (datetime.now() + timedelta(minutes=int(offset))).isoformat()

    return spec


# In-memory pending confirmations: session_key -> job_spec
_pending_confirmations: Dict[str, Dict] = {}


def store_pending(session_key: str, job_spec: Dict):
    _pending_confirmations[session_key] = job_spec


def pop_pending(session_key: str) -> Optional[Dict]:
    return _pending_confirmations.pop(session_key, None)


def has_pending(session_key: str) -> bool:
    return session_key in _pending_confirmations


def is_confirmation(message: str) -> bool:
    """Check if user message is confirming a pending schedule"""
    return message.strip().lower() in ('yes', 'yeah', 'confirm', 'ok', 'sure', 'create it', 'yes please', 'yep', 'y')


def is_cancellation(message: str) -> bool:
    """Check if user message is cancelling a pending schedule"""
    return message.strip().lower() in ('no', 'cancel', 'nope', 'n', 'no thanks', 'stop', 'nevermind')
