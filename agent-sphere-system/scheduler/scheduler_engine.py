"""
Scheduler Engine - APScheduler-based cron/interval/one-shot job management
Jobs are persisted in SQLite and survive server restarts.
"""

import json
import logging
import os
from datetime import datetime
from typing import Callable, Dict, List, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

logger = logging.getLogger(__name__)

# Path for persistent job store
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'schedules.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# In-memory execution history (last 200 entries)
job_execution_history: List[Dict] = []


# ─────────────────────────────────────────────────────────────────────────────
# Top-level callable — APScheduler serializes this as
# "scheduler.scheduler_engine:execute_scheduled_job" + args=[job_id]
# ─────────────────────────────────────────────────────────────────────────────

def execute_scheduled_job(job_id: str) -> None:
    """
    Entry point called by APScheduler for every scheduled job.
    Reads job metadata from the singleton engine, runs the orchestrator,
    records history, and broadcasts the result.
    """
    meta = scheduler_engine._meta.get(job_id, {})
    job_name = meta.get("name", job_id)
    prompt = meta.get("prompt", "")

    logger.info(f"[SCHEDULER] Running job '{job_name}' (id={job_id})")
    result = ""
    success = False
    try:
        from base.api_server import orchestrator  # lazy — avoids circular import
        analysis = orchestrator.analyze_request(prompt)
        execution = orchestrator.execute_sequential_plan(analysis)
        result = execution.get("final_response", "Job completed")
        success = True
        logger.info(f"[SCHEDULER] Job '{job_name}' completed successfully")
    except Exception as e:
        result = f"Error: {str(e)}"
        logger.error(f"[SCHEDULER] Job '{job_name}' failed: {e}")

    # Record in history
    job_execution_history.append({
        "job_id": job_id,
        "job_name": job_name,
        "success": success,
        "result": result[:500],
        "timestamp": datetime.now().isoformat()
    })
    if len(job_execution_history) > 200:
        job_execution_history.pop(0)

    # Broadcast via WebSocket if callback is set
    fn = scheduler_engine._broadcast_fn
    if fn:
        try:
            fn('schedule_job_result', {
                'job_id': job_id,
                'job_name': job_name,
                'success': success,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
        except Exception:
            pass

    # Push result to Telegram (non-blocking; no-op if bot is disabled)
    try:
        from telegram.telegram_bot import push_schedule_result
        agent_id = meta.get("agent_id", "orchestrator")
        push_schedule_result(job_name, agent_id, result, success)
    except Exception:
        pass

    # Persist in-app notification
    try:
        from notifications.notification_manager import notification_manager
        agent_id = meta.get("agent_id", "orchestrator")
        notification_manager.notify_schedule_result(job_name, agent_id, result, success)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────

class SchedulerEngine:
    """Manages scheduled agent/workflow jobs with APScheduler"""

    def __init__(self):
        jobstores = {
            'default': SQLAlchemyJobStore(url=f'sqlite:///{DB_PATH}')
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=4)
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 60
        }
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        self._broadcast_fn: Optional[Callable] = None
        self._meta_path = os.path.join(os.path.dirname(DB_PATH), 'schedules_meta.json')
        self._meta: Dict[str, Dict] = self._load_meta()

    def set_broadcast(self, fn: Callable):
        self._broadcast_fn = fn

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("[SCHEDULER] Started")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("[SCHEDULER] Stopped")

    # ── Meta persistence ──────────────────────────────────────────────────────

    def _load_meta(self) -> Dict:
        if os.path.exists(self._meta_path):
            try:
                with open(self._meta_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_meta(self):
        with open(self._meta_path, 'w') as f:
            json.dump(self._meta, f, indent=2)

    # ── Job creation ──────────────────────────────────────────────────────────

    def add_cron_job(
        self, job_id: str, name: str, agent_id: str, prompt: str,
        schedule_desc: str, hour: int = None, minute: int = 0,
        day_of_week: str = '*', day: str = '*', month: str = '*',
    ) -> Dict:
        trigger = CronTrigger(
            hour=hour, minute=minute,
            day_of_week=day_of_week, day=day, month=month
        )
        return self._add_job(job_id, name, agent_id, prompt, schedule_desc, trigger)

    def add_interval_job(
        self, job_id: str, name: str, agent_id: str, prompt: str,
        schedule_desc: str, hours: int = 0, minutes: int = 0,
    ) -> Dict:
        trigger = IntervalTrigger(hours=hours, minutes=minutes)
        return self._add_job(job_id, name, agent_id, prompt, schedule_desc, trigger)

    def add_one_shot_job(
        self, job_id: str, name: str, agent_id: str, prompt: str,
        schedule_desc: str, run_at: datetime,
    ) -> Dict:
        trigger = DateTrigger(run_date=run_at)
        return self._add_job(job_id, name, agent_id, prompt, schedule_desc, trigger)

    def _add_job(self, job_id: str, name: str, agent_id: str, prompt: str,
                 schedule_desc: str, trigger) -> Dict:
        # Save meta BEFORE registering with APScheduler so the top-level
        # function can find it when the scheduler restores persisted jobs.
        self._meta[job_id] = {
            "name": name,
            "agent_id": agent_id,
            "prompt": prompt,
            "schedule_desc": schedule_desc,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        self._save_meta()

        try:
            self.scheduler.add_job(
                execute_scheduled_job,   # top-level: serializable
                args=[job_id],           # only a plain string arg
                trigger=trigger,
                id=job_id,
                name=name,
                replace_existing=True
            )
        except Exception as e:
            # Roll back meta if scheduler registration fails
            self._meta.pop(job_id, None)
            self._save_meta()
            return {"success": False, "error": str(e)}

        job = self.scheduler.get_job(job_id)
        return {
            "success": True,
            "job_id": job_id,
            "name": name,
            "schedule_desc": schedule_desc,
            "next_run": job.next_run_time.isoformat() if job and job.next_run_time else None
        }

    # ── Job management ────────────────────────────────────────────────────────

    def list_jobs(self) -> List[Dict]:
        jobs = []
        for job in self.scheduler.get_jobs():
            meta = self._meta.get(job.id, {})
            jobs.append({
                "job_id": job.id,
                "name": job.name,
                "schedule_desc": meta.get("schedule_desc", ""),
                "agent_id": meta.get("agent_id", ""),
                "prompt": meta.get("prompt", ""),
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "created_at": meta.get("created_at", ""),
                "status": "paused" if job.next_run_time is None else "active"
            })
        return jobs

    def get_job(self, job_id: str) -> Optional[Dict]:
        job = self.scheduler.get_job(job_id)
        if not job:
            return None
        meta = self._meta.get(job_id, {})
        return {
            "job_id": job.id,
            "name": job.name,
            "schedule_desc": meta.get("schedule_desc", ""),
            "agent_id": meta.get("agent_id", ""),
            "prompt": meta.get("prompt", ""),
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "created_at": meta.get("created_at", ""),
            "status": "paused" if job.next_run_time is None else "active"
        }

    def pause_job(self, job_id: str) -> Dict:
        if not self.scheduler.get_job(job_id):
            return {"success": False, "error": "Job not found"}
        self.scheduler.pause_job(job_id)
        if job_id in self._meta:
            self._meta[job_id]["status"] = "paused"
            self._save_meta()
        return {"success": True, "job_id": job_id, "status": "paused"}

    def resume_job(self, job_id: str) -> Dict:
        if not self.scheduler.get_job(job_id):
            return {"success": False, "error": "Job not found"}
        self.scheduler.resume_job(job_id)
        if job_id in self._meta:
            self._meta[job_id]["status"] = "active"
            self._save_meta()
        return {"success": True, "job_id": job_id, "status": "active"}

    def delete_job(self, job_id: str) -> Dict:
        if not self.scheduler.get_job(job_id):
            return {"success": False, "error": "Job not found"}
        self.scheduler.remove_job(job_id)
        self._meta.pop(job_id, None)
        self._save_meta()
        return {"success": True, "job_id": job_id}

    def run_now(self, job_id: str) -> Dict:
        """Trigger a job immediately outside its schedule"""
        if job_id not in self._meta:
            return {"success": False, "error": "Job not found"}
        manual_id = f"{job_id}_manual_{int(datetime.now().timestamp())}"
        # Copy meta under the manual id so execute_scheduled_job can find it
        self._meta[manual_id] = dict(self._meta[job_id])
        self._save_meta()
        self.scheduler.add_job(
            execute_scheduled_job,
            args=[manual_id],
            trigger='date',
            id=manual_id
        )
        return {"success": True, "job_id": job_id, "message": "Job queued for immediate execution"}

    def get_execution_history(self, job_id: str = None, limit: int = 50) -> List[Dict]:
        history = job_execution_history
        if job_id:
            history = [e for e in history if e["job_id"] == job_id]
        return history[-limit:]


# Singleton — must be defined AFTER execute_scheduled_job so the top-level
# function can reference it at call time (not import time).
scheduler_engine = SchedulerEngine()
