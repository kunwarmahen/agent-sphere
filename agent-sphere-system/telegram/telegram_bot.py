"""
Telegram Bot — alternative chat interface for Agent Sphere.

Commands:
  /start          — welcome message
  /help           — command reference
  /ask <msg>      — chat with the smart orchestrator
  /ask <agent> <msg> — chat with a specific agent (home / calendar / finance / etc.)
  /agents         — list available agents
  /schedules      — list active scheduled jobs
  /status         — system status
  /myid           — show your Telegram user ID (useful for allow-listing)

Scheduled job results can be pushed here via push_message().

python-telegram-bot v20+ (asyncio-based) is used.
Install:  pip install "python-telegram-bot>=20.0"
"""
import asyncio
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

# ── lazy imports so the server boots even without the library installed ───────
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        CallbackQueryHandler, ContextTypes, filters,
    )
    _PTB_AVAILABLE = True
except ImportError:
    _PTB_AVAILABLE = False
    logger.warning("python-telegram-bot not installed — Telegram bot disabled. "
                   "Run: pip install 'python-telegram-bot>=20.0'")

from telegram.telegram_config import telegram_config

# Will be injected by api_server at startup
_execute_query = None   # callable(query, agent_id, session_key) -> str
_get_agents    = None   # callable() -> list[dict]
_get_schedules = None   # callable() -> list[dict]

# The running Application (set by start_bot)
_app: Optional[object] = None
_loop: Optional[asyncio.AbstractEventLoop] = None


def set_handlers(execute_query_fn, get_agents_fn, get_schedules_fn):
    """Called by api_server to wire up backend functions."""
    global _execute_query, _get_agents, _get_schedules
    _execute_query  = execute_query_fn
    _get_agents     = get_agents_fn
    _get_schedules  = get_schedules_fn


# ── auth guard ────────────────────────────────────────────────────────────────

def _auth(update: "Update") -> bool:
    uid = update.effective_user.id if update.effective_user else None
    return uid is not None and telegram_config.is_allowed(uid)


async def _deny(update: "Update"):
    await update.message.reply_text(
        "⛔ Unauthorised. Add your Telegram user ID in Agent Sphere → Telegram settings.\n"
        "Your ID: " + str(update.effective_user.id if update.effective_user else "?")
    )


# ── helpers ───────────────────────────────────────────────────────────────────

def _session_key(update: "Update") -> str:
    return f"tg_{update.effective_user.id}"


async def _run_query(query: str, agent_id: str, session_key: str) -> str:
    """Run a blocking agent query in a thread pool."""
    if _execute_query is None:
        return "Backend not wired — restart the server."
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _execute_query, query, agent_id, session_key)
    return result


# ── command handlers ──────────────────────────────────────────────────────────

async def cmd_start(update: "Update", ctx: "ContextTypes.DEFAULT_TYPE"):
    if not _auth(update):
        await _deny(update)
        return
    name = update.effective_user.first_name or "there"
    await update.message.reply_text(
        f"👋 Hi {name}! I'm your *Agent Sphere* assistant.\n\n"
        "Send me any message and I'll route it to the right agent, or use:\n"
        "• /ask — chat with the smart orchestrator\n"
        "• /agents — list available agents\n"
        "• /schedules — view scheduled jobs\n"
        "• /status — system status\n"
        "• /help — full command list",
        parse_mode="Markdown"
    )


async def cmd_help(update: "Update", ctx: "ContextTypes.DEFAULT_TYPE"):
    if not _auth(update):
        await _deny(update)
        return
    await update.message.reply_text(
        "*Agent Sphere — Telegram Commands*\n\n"
        "/ask \\<message\\> — smart orchestrator answers\n"
        "/ask home \\<message\\> — home assistant agent\n"
        "/ask calendar \\<message\\> — calendar/email agent\n"
        "/ask finance \\<message\\> — finance agent\n"
        "/ask \\<custom\\_agent\\> \\<message\\> — any custom agent\n\n"
        "/agents — list all agents\n"
        "/schedules — view active scheduled jobs\n"
        "/status — server & agent status\n"
        "/myid — show your Telegram user ID\n\n"
        "You can also just *send any message* and the orchestrator will handle it.",
        parse_mode="MarkdownV2"
    )


async def cmd_myid(update: "Update", ctx: "ContextTypes.DEFAULT_TYPE"):
    uid = update.effective_user.id if update.effective_user else "?"
    await update.message.reply_text(f"Your Telegram user ID: `{uid}`", parse_mode="Markdown")


async def cmd_agents(update: "Update", ctx: "ContextTypes.DEFAULT_TYPE"):
    if not _auth(update):
        await _deny(update)
        return
    if _get_agents is None:
        await update.message.reply_text("Backend not ready.")
        return
    agents = _get_agents()
    lines = ["*Available Agents*\n"]
    for a in agents:
        lines.append(f"• *{a.get('id', '?')}* — {a.get('role', a.get('description', ''))}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_schedules(update: "Update", ctx: "ContextTypes.DEFAULT_TYPE"):
    if not _auth(update):
        await _deny(update)
        return
    if _get_schedules is None:
        await update.message.reply_text("Backend not ready.")
        return
    jobs = _get_schedules()
    if not jobs:
        await update.message.reply_text("No scheduled jobs found.")
        return
    lines = ["*Scheduled Jobs*\n"]
    for j in jobs[:10]:
        status = "▶️" if j.get("status") == "active" else "⏸"
        next_run = j.get("next_run_time", "—")
        if next_run and next_run != "—":
            next_run = next_run[:16].replace("T", " ")
        lines.append(f"{status} *{j.get('name', j.get('id'))}*")
        lines.append(f"   Agent: `{j.get('agent_id', '?')}` | Next: {next_run}")
    if len(jobs) > 10:
        lines.append(f"\n_...and {len(jobs)-10} more_")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_status(update: "Update", ctx: "ContextTypes.DEFAULT_TYPE"):
    if not _auth(update):
        await _deny(update)
        return
    agents_ok = _get_agents is not None
    sched_ok  = _get_schedules is not None
    jobs = _get_schedules() if sched_ok else []
    active = sum(1 for j in jobs if j.get("status") == "active")
    await update.message.reply_text(
        f"*Agent Sphere Status*\n\n"
        f"✅ API: online\n"
        f"{'✅' if agents_ok else '❌'} Agents: {'ready' if agents_ok else 'unavailable'}\n"
        f"{'✅' if sched_ok else '❌'} Scheduler: {active} active jobs\n"
        f"✅ Telegram: connected",
        parse_mode="Markdown"
    )


async def cmd_ask(update: "Update", ctx: "ContextTypes.DEFAULT_TYPE"):
    """
    /ask <message>              — orchestrator
    /ask <agent_id> <message>   — specific agent
    """
    if not _auth(update):
        await _deny(update)
        return

    text = " ".join(ctx.args) if ctx.args else ""
    if not text.strip():
        await update.message.reply_text("Usage: /ask <message>  or  /ask <agent_id> <message>")
        return

    known_agents = {"home", "calendar", "finance", "orchestrator"}
    if _get_agents:
        for a in _get_agents():
            known_agents.add(a.get("id", ""))

    parts = text.split(None, 1)
    if parts[0].lower() in known_agents and len(parts) == 2:
        agent_id = parts[0].lower()
        query    = parts[1]
    else:
        agent_id = "orchestrator"
        query    = text

    thinking_msg = await update.message.reply_text("⏳ Thinking…")
    try:
        response = await _run_query(query, agent_id, _session_key(update))
        await thinking_msg.edit_text(response[:4096])
    except Exception as e:
        logger.exception("Error processing Telegram /ask")
        await thinking_msg.edit_text(f"❌ Error: {e}")


async def handle_message(update: "Update", ctx: "ContextTypes.DEFAULT_TYPE"):
    """Plain text messages → orchestrator (same as /ask without agent prefix)."""
    if not _auth(update):
        await _deny(update)
        return
    query = update.message.text or ""
    if not query.strip():
        return
    thinking_msg = await update.message.reply_text("⏳ Thinking…")
    try:
        response = await _run_query(query, "orchestrator", _session_key(update))
        await thinking_msg.edit_text(response[:4096])
    except Exception as e:
        logger.exception("Error handling Telegram message")
        await thinking_msg.edit_text(f"❌ Error: {e}")


# ── inline keyboard — schedule confirmation ───────────────────────────────────

async def handle_callback(update: "Update", ctx: "ContextTypes.DEFAULT_TYPE"):
    """Handle inline keyboard button presses (e.g. schedule confirm/cancel)."""
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data.startswith("confirm_schedule:"):
        session = data.split(":", 1)[1]
        response = await _run_query("yes", "orchestrator", session)
        await query.edit_message_text(f"✅ {response[:4096]}")
    elif data.startswith("cancel_schedule:"):
        session = data.split(":", 1)[1]
        response = await _run_query("no", "orchestrator", session)
        await query.edit_message_text(f"❌ {response[:4096]}")


# ── push notifications ────────────────────────────────────────────────────────

def push_message(text: str, chat_id: Optional[int] = None):
    """
    Push a message to Telegram from non-async code (e.g. scheduler callback).
    If chat_id is None, sends to all allowed_user_ids.
    """
    if not telegram_config.enabled or _app is None or _loop is None:
        return
    recipients = [chat_id] if chat_id else telegram_config.allowed_user_ids
    if not recipients:
        logger.debug("push_message: no recipients configured")
        return

    async def _send():
        for uid in recipients:
            try:
                await _app.bot.send_message(chat_id=uid, text=text[:4096])
            except Exception as e:
                logger.warning("Telegram push to %s failed: %s", uid, e)

    if _loop.is_running():
        asyncio.run_coroutine_threadsafe(_send(), _loop)
    else:
        _loop.run_until_complete(_send())


def push_schedule_result(job_name: str, agent_id: str, result: str, success: bool):
    """Convenience wrapper called by the scheduler after each job run."""
    if not telegram_config.notify_on_schedule:
        return
    icon = "✅" if success else "❌"
    text = f"{icon} *Scheduled job:* {job_name}\n*Agent:* {agent_id}\n\n{result[:300]}"
    # Strip markdown for push_message (plain text)
    plain = text.replace("*", "").replace("_", "")
    push_message(plain)


# ── bot lifecycle ─────────────────────────────────────────────────────────────

def build_application(token: str) -> "Application":
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("help",      cmd_help))
    app.add_handler(CommandHandler("myid",      cmd_myid))
    app.add_handler(CommandHandler("agents",    cmd_agents))
    app.add_handler(CommandHandler("schedules", cmd_schedules))
    app.add_handler(CommandHandler("status",    cmd_status))
    app.add_handler(CommandHandler("ask",       cmd_ask))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app


def _run_bot(token: str):
    """Target function for the background daemon thread."""
    global _app, _loop
    try:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
        _app = build_application(token)
        logger.info("Telegram bot starting (polling)…")
        _app.run_polling(close_loop=False)
    except Exception as e:
        logger.error("Telegram bot crashed: %s", e)


_bot_thread: Optional[threading.Thread] = None


def start_bot():
    """Start the bot in a background daemon thread. Safe to call multiple times."""
    global _bot_thread
    if not _PTB_AVAILABLE:
        logger.warning("python-telegram-bot not installed — Telegram bot not started.")
        return
    if not telegram_config.enabled:
        logger.info("Telegram bot disabled (no token or disabled in config).")
        return
    if _bot_thread and _bot_thread.is_alive():
        logger.info("Telegram bot already running.")
        return
    token = telegram_config.bot_token
    if not token:
        logger.warning("Telegram bot_token not set — skipping.")
        return
    _bot_thread = threading.Thread(target=_run_bot, args=(token,), daemon=True, name="telegram-bot")
    _bot_thread.start()
    logger.info("Telegram bot thread started.")


def stop_bot():
    global _app, _loop
    if _app is not None and _loop is not None and _loop.is_running():
        asyncio.run_coroutine_threadsafe(_app.stop(), _loop)
    _app = None


def is_running() -> bool:
    return _bot_thread is not None and _bot_thread.is_alive()
