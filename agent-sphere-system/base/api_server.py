"""
Flask API Server - RESTful API for the multi-agent system with WebSocket support
"""

import os
import uuid
import tempfile
import whisper
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter

from typing import Dict, Any
import json
import logging
from datetime import datetime

from base.agent_framework import Agent
# from agents.home_agent_default import home_agent, controller as home_controller # Dummy Home agent with mock data
from agents.home_agent import home_agent, controller as home_controller # Home agent for smart home control
# from agents.calendar_agent import calendar_agent, manager as calendar_manager  # Dummy agent with mock data
from agents.google.google_unified_agent import calendar_agent, manager as calendar_manager  # Real Google API
from agents.finance_agent import finance_agent, planner as finance_planner
from agents.custom_agents import custom_agent_manager
from tools.dynamic_tools import dynamic_tool_builder

from agents.planning_agent import create_llm_orchestrator
from workflow.workflow_engine import WorkflowEngine, WorkflowTask
from workflow.workflow_templates import WorkflowTemplates
from werkzeug.utils import secure_filename

from store.config import Config
from store.storage_backends import get_storage_backend
from analytics.analytics import agent_analytics, ExecutionTimer
from testing.testing import agent_tester, TestCase
from templates.templates import agent_template_library
from scheduler.scheduler_engine import scheduler_engine
from scheduler.schedule_intent import (
    detect_schedule_intent, build_confirmation_message, intent_to_job_spec,
    store_pending, pop_pending, has_pending, is_confirmation, is_cancellation
)


# Initialize Flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize workflow engine
workflow_engine = WorkflowEngine()
workflow_engine.register_agent("home", home_agent)
workflow_engine.register_agent("calendar", calendar_agent)
workflow_engine.register_agent("finance", finance_agent)

# Initialize the sequential orchestrator
# orchestrator = create_orchestrator(workflow_engine.agents)
orchestrator = create_llm_orchestrator(
    workflow_engine.agents,  # Built-in agents
    custom_agent_manager      # Custom agents manager
)

# Store agent conversations
conversations = {
    "home": [],
    "calendar": [],
    "finance": []
}

# Store active connections
active_connections = []
notification_history = []

# Load Whisper model once at startup (change 'base' to 'small', 'medium', 'large' for better accuracy)
whisper_model = whisper.load_model("base")

# Initialize rate limiter
limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    active_connections.append(request.sid)
    emit('connection_status', {'status': 'connected', 'id': request.sid})
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_connections:
        active_connections.remove(request.sid)
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('subscribe')
def handle_subscribe(data):
    room = data.get('room', 'general')
    emit('subscribed', {'room': room, 'status': 'success'})

def broadcast_update(event_type, data):
    """Broadcast real-time updates to all connected clients"""
    socketio.emit('system_update', {'type': event_type, 'data': data, 'timestamp': datetime.now().isoformat()})

# Start the scheduler now that broadcast_update is defined
scheduler_engine.set_broadcast(broadcast_update)
scheduler_engine.start()

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Multi-Agent AI System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "agents": {
            "home": "active",
            "calendar": "active",
            "finance": "active"
        },
        "workflows": len(workflow_engine.workflows),
        "active_connections": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }), 200

# ============================================================================
# AGENT ENDPOINTS
# ============================================================================

@app.route('/api/agents', methods=['GET'])
def list_agents():
    return jsonify({
        "agents": [
            {
                "id": "home",
                "name": "JARVIS",
                "role": "Home Automation Manager",
                "description": "Control smart home devices",
                "status": "active"
            },
            {
                "id": "calendar",
                "name": "Assistant",
                "role": "Calendar & Email Manager",
                "description": "Manage calendar and emails",
                "status": "active"
            },
            {
                "id": "finance",
                "name": "FinanceBot",
                "role": "Financial Planning Assistant",
                "description": "Manage finances and investments",
                "status": "active"
            }
        ]
    }), 200

@app.route('/api/agents/<agent_id>/chat', methods=['POST'])
def agent_chat(agent_id):
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        if agent_id not in workflow_engine.agents:
            return jsonify({"error": f"Agent '{agent_id}' not found"}), 404
        
        agent = workflow_engine.agents[agent_id]
        
        # Get response from agent
        response = agent.think_and_act(message, verbose=False)
        
        # Store conversation
        conversations[agent_id].append({
            "type": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        conversations[agent_id].append({
            "type": "assistant",
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Broadcast update
        broadcast_update('chat_message', {
            'agent_id': agent_id,
            'message': response
        })
        
        return jsonify({
            "agent_id": agent_id,
            "request": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error in agent_chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/agents/<agent_id>/history', methods=['GET'])
def agent_history(agent_id):
    if agent_id not in conversations:
        return jsonify({"error": f"Agent '{agent_id}' not found"}), 404
    
    limit = request.args.get('limit', 50, type=int)
    return jsonify({
        "agent_id": agent_id,
        "history": conversations[agent_id][-limit:]
    }), 200

@app.route('/api/agents/<agent_id>/clear', methods=['POST'])
def clear_agent_memory(agent_id):
    try:
        if agent_id in workflow_engine.agents:
            agent = workflow_engine.agents[agent_id]
            if hasattr(agent, 'clear_memory'):
                agent.clear_memory()
            conversations[agent_id] = []
            
            return jsonify({
                "message": f"Memory cleared for {agent_id}",
                "agent_id": agent_id
            }), 200
        else:
            return jsonify({"error": f"Agent '{agent_id}' not found"}), 404
    except Exception as e:
        logger.error(f"Error clearing memory: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# HOME AUTOMATION ENDPOINTS
# ============================================================================

@app.route('/api/home/status', methods=['GET'])
def home_status():
    try:
        import json as json_module
        status_str = home_controller.get_home_status()
        status = json_module.loads(status_str)
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting home status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/home/light/<room>', methods=['POST'])
def control_light(room):
    try:
        data = request.json
        state = data.get('state')
        brightness = data.get('brightness')
        color_temp = data.get('color_temp')
        
        result = home_controller.toggle_light(room, state, brightness, color_temp)
        
        # Broadcast update
        broadcast_update('home_update', {
            'type': 'light',
            'room': room,
            'state': state
        })
        
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error controlling light: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/home/thermostat', methods=['POST'])
def control_thermostat():
    try:
        data = request.json
        temperature = data.get('temperature')
        mode = data.get('mode')
        entity_id = data.get('entity_id')  # Optional: specific thermostat to control

        result = home_controller.set_thermostat(temperature, mode, entity_id)

        broadcast_update('home_update', {
            'type': 'thermostat',
            'temperature': temperature,
            'entity_id': entity_id
        })

        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error controlling thermostat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/home/door', methods=['POST'])
def control_door():
    try:
        data = request.json
        lock = data.get('lock', True)
        result = home_controller.lock_door(lock)
        
        broadcast_update('home_update', {
            'type': 'door',
            'locked': lock
        })
        
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error controlling door: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/home/garage', methods=['POST'])
def control_garage():
    """Control garage door"""
    try:
        data = request.json
        open_garage = data.get('open_garage')
        
        if open_garage is None:
            return jsonify({"error": "open_garage parameter is required"}), 400
        
        result = home_controller.control_garage(open_garage)
        
        broadcast_update('home_update', {
            'type': 'garage',
            'open': open_garage
        })
        
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error controlling garage: {str(e)}")
        return jsonify({"error": str(e)}), 500        

@app.route('/api/home/device/<device>', methods=['POST'])
def control_device(device):
    try:
        data = request.json
        on = data.get('on')
        result = home_controller.control_device(device, on)
        
        broadcast_update('home_update', {
            'type': 'device',
            'device': device,
            'on': on
        })
        
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error controlling device: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/home/log', methods=['GET'])
def get_home_log():
    try:
        limit = request.args.get('limit', 10, type=int)
        result = home_controller.get_device_log(limit)
        import json as json_module
        log = json_module.loads(result)
        return jsonify(log), 200
    except Exception as e:
        logger.error(f"Error getting home log: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# CALENDAR & EMAIL ENDPOINTS
# ============================================================================

@app.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    try:
        days = request.args.get('days', 7, type=int)
        
        # Call the calendar manager to get events
        result = calendar_manager.get_calendar_events(days)
        
        import json as json_module
        events = json_module.loads(result)
        
        return jsonify(events), 200
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "message": "Failed to fetch calendar events"
        }), 500

@app.route('/api/calendar/emails', methods=['GET'])
def get_emails():
    try:
        limit = request.args.get('limit', 5, type=int)
        unread_only = request.args.get('unread_only', True, type=bool)
        result = calendar_manager.read_emails(limit, unread_only)
        import json as json_module
        emails = json_module.loads(result)
        return jsonify(emails), 200
    except Exception as e:
        logger.error(f"Error getting emails: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/calendar/event', methods=['POST'])
def schedule_event():
    try:
        data = request.json
        title = data.get('title')
        start_time = data.get('start_time')
        duration = data.get('duration', 60)
        location = data.get('location', '')
        attendees = data.get('attendees', [])
        description = data.get('description', '')
        
        result = calendar_manager.schedule_event(title, start_time, duration, location, attendees, description)
        
        broadcast_update('calendar_update', {
            'type': 'event_scheduled',
            'title': title
        })
        
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error scheduling event: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/calendar/email/send', methods=['POST'])
def send_email():
    try:
        data = request.json
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        cc = data.get('cc', '')
        bcc = data.get('bcc', '')
        
        result = calendar_manager.send_email(to, subject, body, cc, bcc)
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/calendar/free-slot', methods=['GET'])
def find_free_slot():
    try:
        duration = request.args.get('duration', 60, type=int)
        result = calendar_manager.find_free_slot(duration)
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error finding free slot: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# FINANCE ENDPOINTS
# ============================================================================

@app.route('/api/finance/summary', methods=['GET'])
def get_financial_summary():
    try:
        result = finance_planner.get_financial_summary()
        import json as json_module
        summary = json_module.loads(result)
        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Error getting financial summary: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/finance/balances', methods=['GET'])
def get_balances():
    try:
        result = finance_planner.get_all_balances()
        import json as json_module
        balances = json_module.loads(result)
        return jsonify(balances), 200
    except Exception as e:
        logger.error(f"Error getting balances: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/finance/spending', methods=['GET'])
def get_spending_analysis():
    try:
        days = request.args.get('days', 30, type=int)
        result = finance_planner.get_spending_analysis(days)
        import json as json_module
        analysis = json_module.loads(result)
        return jsonify(analysis), 200
    except Exception as e:
        logger.error(f"Error getting spending analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/finance/portfolio', methods=['GET'])
def get_portfolio():
    try:
        result = finance_planner.get_investment_portfolio()
        import json as json_module
        portfolio = json_module.loads(result)
        return jsonify(portfolio), 200
    except Exception as e:
        logger.error(f"Error getting portfolio: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/finance/goals', methods=['GET'])
def get_goals():
    try:
        result = finance_planner.get_financial_goals()
        import json as json_module
        goals = json_module.loads(result)
        return jsonify(goals), 200
    except Exception as e:
        logger.error(f"Error getting goals: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/finance/transaction', methods=['POST'])
def record_transaction():
    try:
        data = request.json
        amount = data.get('amount')
        category = data.get('category')
        description = data.get('description', '')
        
        result = finance_planner.record_transaction(amount, category, description)
        
        broadcast_update('finance_update', {
            'type': 'transaction',
            'amount': amount,
            'category': category
        })
        
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error recording transaction: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

@app.route('/api/workflows', methods=['GET'])
def list_workflows():
    try:
        workflows = workflow_engine.list_workflows()
        return jsonify({"workflows": workflows}), 200
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    try:
        data = request.json
        workflow_id = data.get('workflow_id')
        name = data.get('name')
        description = data.get('description', '')
        
        workflow = workflow_engine.create_workflow(workflow_id, name, description)
        
        broadcast_update('workflow_created', {
            'workflow_id': workflow_id,
            'name': name
        })
        
        return jsonify({
            "message": "Workflow created",
            "workflow_id": workflow_id
        }), 201
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    try:
        workflow = workflow_engine.get_workflow(workflow_id)
        if not workflow:
            return jsonify({"error": "Workflow not found"}), 404
        
        return jsonify(workflow.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting workflow: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/workflows/<workflow_id>/tasks', methods=['POST'])
def add_task(workflow_id):
    try:
        workflow = workflow_engine.get_workflow(workflow_id)
        if not workflow:
            return jsonify({"error": "Workflow not found"}), 404
        
        data = request.json
        task = WorkflowTask(
            task_id=data.get('task_id'),
            agent_name=data.get('agent_name'),
            request=data.get('request'),
            retry_count=data.get('retry_count', 1),
            on_failure=data.get('on_failure', 'continue')  # Changed default to 'continue'
        )
        
        # Set next_task_id if provided
        if data.get('next_task_id'):
            task.next_task_id = data.get('next_task_id')
        
        # Auto-link: if workflow has tasks, link the last one to this new task
        if len(workflow.tasks) > 0:
            last_task_id = list(workflow.tasks.keys())[-1]
            last_task = workflow.tasks[last_task_id]
            if not last_task.next_task_id:  # Only link if not already linked
                last_task.next_task_id = task.task_id
        
        # Add task (first task becomes start task)
        is_first = len(workflow.tasks) == 0
        workflow.add_task(task, is_start=is_first)
        
        return jsonify({
            "message": "Task added",
            "task_id": task.task_id,
            "is_start": is_first,
            "linked_from": last_task_id if len(workflow.tasks) > 1 else None
        }), 201
    except Exception as e:
        logger.error(f"Error adding task: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/workflows/<workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    try:
        broadcast_update('workflow_started', {'workflow_id': workflow_id})
        
        result = workflow_engine.execute_workflow(workflow_id, verbose=False)
        
        broadcast_update('workflow_completed', {
            'workflow_id': workflow_id,
            'success': result['success']
        })
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/workflows/<workflow_id>/status', methods=['GET'])
def get_workflow_status(workflow_id):
    try:
        status = workflow_engine.get_workflow_status(workflow_id)
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/workflows/<workflow_id>/report', methods=['GET'])
def get_workflow_report(workflow_id):
    try:
        report = workflow_engine.get_execution_report(workflow_id)
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Error getting workflow report: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/workflows/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    try:
        workflow = workflow_engine.get_workflow(workflow_id)
        if not workflow:
            return jsonify({"error": "Workflow not found"}), 404
        
        del workflow_engine.workflows[workflow_id]
        return jsonify({"message": "Workflow deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting workflow: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# TEMPLATES ENDPOINTS
# ============================================================================

@app.route('/api/templates', methods=['GET'])
def list_templates():
    templates = WorkflowTemplates.list_templates()
    return jsonify({"templates": templates}), 200

@app.route('/api/templates/<template_id>/create', methods=['POST'])
def create_from_template(template_id):
    try:
        workflow = WorkflowTemplates.create_from_template(workflow_engine, template_id)
        if not workflow:
            return jsonify({"error": "Template not found"}), 404
        
        broadcast_update('workflow_created', {
            'workflow_id': workflow.workflow_id,
            'name': workflow.name,
            'from_template': template_id
        })
        
        return jsonify({
            "message": "Workflow created from template",
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "tasks": len(workflow.tasks)
        }), 201
    except Exception as e:
        logger.error(f"Error creating from template: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# NOTIFICATIONS
# ============================================================================

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    limit = request.args.get('limit', 20, type=int)
    return jsonify({"notifications": notification_history[-limit:]}), 200

@app.route('/api/notifications', methods=['POST'])
def create_notification():
    try:
        data = request.json
        notification = {
            'id': len(notification_history) + 1,
            'title': data.get('title'),
            'message': data.get('message'),
            'type': data.get('type', 'info'),
            'timestamp': datetime.now().isoformat()
        }
        notification_history.append(notification)
        
        broadcast_update('notification', notification)
        
        return jsonify(notification), 201
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# WHISPER SPEECH-TO-TEXT ENDPOINT
# ============================================================================

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio file using Whisper"""
    try:
        # Check if audio file is in request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        try:
            # Transcribe with Whisper
            logger.info(f"Transcribing audio file: {filename}")
            result = whisper_model.transcribe(temp_path, language="en")
            
            text = result["text"].strip()
            
            if not text:
                return jsonify({"error": "No speech detected in audio"}), 400
            
            logger.info(f"Transcription successful: {text}")
            
            return jsonify({
                "success": True,
                "text": text,
                "language": result.get("language", "en"),
                "duration": result.get("duration", 0)
            }), 200
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

@app.route('/api/transcribe/health', methods=['GET'])
def transcribe_health():
    """Check if Whisper is ready"""
    return jsonify({
        "status": "ready",
        "model": "whisper-base",
        "message": "Whisper speech-to-text service is running"
    }), 200

# ============================================================================
# MULTI-AGENT ORCHESTRATION ENDPOINTS
# ============================================================================

@app.route('/api/orchestrator/analyze', methods=['POST'])
def analyze_request():
    """Analyze a request to determine required agents"""
    try:
        data = request.json
        user_request = data.get('query', '').strip()
        
        if not user_request:
            return jsonify({"error": "Query is required"}), 400
        
        analysis = orchestrator.analyze_request(user_request)
        
        return jsonify({
            "analysis": analysis,
            "agents_available": list(workflow_engine.agents.keys())
        }), 200
    
    except Exception as e:
        logger.error(f"Error analyzing request: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/orchestrator/execute', methods=['POST'])
def execute_orchestrated_query():
    """Execute multi-agent orchestrated query"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        session_key = data.get('session_key', 'default')

        if not query:
            return jsonify({"error": "Query is required"}), 400

        # ── Schedule confirmation flow ──────────────────────────────────────
        if has_pending(session_key):
            if is_confirmation(query):
                job_spec = pop_pending(session_key)
                result = _create_job_from_spec(job_spec)
                reply = (
                    f"Schedule created! **{job_spec['name']}** will run {job_spec['schedule_desc']}.\n"
                    f"Job ID: `{job_spec['job_id']}`"
                    if result.get("success") else
                    f"Sorry, I couldn't create the schedule: {result.get('error')}"
                )
                _store_conversation(session_key, query, reply)
                return jsonify({
                    "query": query, "schedule_created": result.get("success"),
                    "execution": {"final_response": reply},
                    "timestamp": datetime.now().isoformat()
                }), 200
            elif is_cancellation(query):
                pop_pending(session_key)
                reply = "Okay, I've cancelled the schedule."
                _store_conversation(session_key, query, reply)
                return jsonify({
                    "query": query, "schedule_created": False,
                    "execution": {"final_response": reply},
                    "timestamp": datetime.now().isoformat()
                }), 200

        # ── Detect new scheduling intent ────────────────────────────────────
        intent = detect_schedule_intent(query)
        if intent:
            job_spec = intent_to_job_spec(intent)
            store_pending(session_key, job_spec)
            reply = build_confirmation_message(intent)
            _store_conversation(session_key, query, reply)
            broadcast_update('schedule_confirmation_pending', {
                'session_key': session_key, 'job_spec': job_spec
            })
            return jsonify({
                "query": query, "schedule_pending": True,
                "execution": {"final_response": reply},
                "timestamp": datetime.now().isoformat()
            }), 200

        # Step 1: Analyze the request
        analysis = orchestrator.analyze_request(query)

        # Step 2: Execute the plan sequentially
        execution_result = orchestrator.execute_sequential_plan(analysis)
        
        # Store in conversation history
        _store_conversation(session_key, query, execution_result["final_response"])
        
        # Broadcast update
        broadcast_update('orchestrator_execution', {
            'query': query,
            'agents_used': analysis['detected_agents'],
            'steps': len(execution_result['steps_executed'])
        })
        
        return jsonify({
            "query": query,
            "analysis": analysis,
            "execution": execution_result,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error executing orchestrated query: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/orchestrator/history', methods=['GET'])
def get_orchestrator_history():
    """Get orchestrator conversation history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = conversations.get("orchestrator", [])
        return jsonify({
            "history": history[-limit:],
            "total": len(history)
        }), 200
    except Exception as e:
        logger.error(f"Error getting orchestrator history: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/orchestrator/clear', methods=['POST'])
def clear_orchestrator_history():
    """Clear orchestrator history"""
    try:
        conversations["orchestrator"] = []
        return jsonify({
            "message": "Orchestrator history cleared"
        }), 200
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
# ============================================================================
# SCENE MGMTENT ENDPOINTS
# ============================================================================


@app.route('/api/home/scenes', methods=['GET'])
def get_scenes():
    """Get all available scenes"""
    try:
        result = home_controller.get_scenes()
        import json as json_module
        scenes = json_module.loads(result)
        return jsonify(scenes), 200
    except Exception as e:
        logger.error(f"Error getting scenes: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/home/scenes', methods=['POST'])
def create_scene():
    """Create a new scene"""
    try:
        data = request.json
        scene_name = data.get('scene_name')
        actions = data.get('actions', [])
        
        if not scene_name:
            return jsonify({"error": "scene_name is required"}), 400
        
        result = home_controller.create_scene(scene_name, actions)
        
        broadcast_update('scene_created', {
            'scene_name': scene_name,
            'action_count': len(actions)
        })
        
        return jsonify({"message": result, "scene_name": scene_name}), 201
    except Exception as e:
        logger.error(f"Error creating scene: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/home/scenes/<scene_name>/execute', methods=['POST'])
def execute_scene(scene_name):
    """Execute a scene"""
    try:
        result = home_controller.execute_scene(scene_name)
        
        broadcast_update('scene_executed', {
            'scene_name': scene_name,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({"message": result, "scene_name": scene_name}), 200
    except Exception as e:
        logger.error(f"Error executing scene: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/home/scenes/<scene_name>', methods=['DELETE'])
def delete_scene(scene_name):
    """Delete a scene"""
    try:
        result = home_controller.delete_scene(scene_name)
        
        broadcast_update('scene_deleted', {
            'scene_name': scene_name
        })
        
        return jsonify({"message": result}), 200
    except Exception as e:
        logger.error(f"Error deleting scene: {str(e)}")
        return jsonify({"error": str(e)}), 500    

# ============================================================================
# CUSTOM AGENT ENDPOINTS
# ============================================================================

@app.route('/api/agents/custom', methods=['POST'])
def create_custom_agent():
    """Create a new custom agent"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name') or not data.get('role'):
            return jsonify({"error": "name and role are required"}), 400
        
        # Add user info (you can enhance this with actual user authentication)
        data['created_by'] = data.get('created_by', 'default_user')
        
        result = custom_agent_manager.create_agent(data)
        
        if result["success"]:
            broadcast_update('custom_agent_created', {
                'agent_id': result['agent_id'],
                'name': data.get('name')
            })
        
        return jsonify(result), 201 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error creating custom agent: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/custom/<agent_id>', methods=['GET'])
def get_custom_agent(agent_id):
    """Get a custom agent details"""
    try:
        agent = custom_agent_manager.get_agent(agent_id)
        if not agent:
            return jsonify({"error": "Agent not found"}), 404
        return jsonify(agent), 200
    except Exception as e:
        logger.error(f"Error getting custom agent: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/custom/<agent_id>', methods=['PUT'])
def update_custom_agent(agent_id):
    """Update a custom agent"""
    try:
        data = request.json
        result = custom_agent_manager.update_agent(agent_id, data)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error updating custom agent: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/custom/<agent_id>', methods=['DELETE'])
def delete_custom_agent(agent_id):
    """Delete a custom agent"""
    try:
        result = custom_agent_manager.delete_agent(agent_id)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error deleting custom agent: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/custom/<agent_id>/publish', methods=['POST'])
def publish_agent(agent_id):
    """Publish an agent to marketplace"""
    try:
        result = custom_agent_manager.publish_agent(agent_id)
        
        if result["success"]:
            broadcast_update('agent_published', {
                'agent_id': agent_id,
                'name': result['agent'].get('name')
            })
        
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error publishing agent: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/custom/<agent_id>/unpublish', methods=['POST'])
def unpublish_agent(agent_id):
    """Unpublish an agent from marketplace"""
    try:
        result = custom_agent_manager.unpublish_agent(agent_id)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error unpublishing agent: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/custom/my-agents/<user_id>', methods=['GET'])
def get_my_agents(user_id):
    """Get all agents created by a user"""
    try:
        agents = custom_agent_manager.get_my_agents(user_id)
        return jsonify({"agents": agents}), 200
    except Exception as e:
        logger.error(f"Error getting user agents: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/marketplace', methods=['GET'])
def get_marketplace():
    """Get published agents from marketplace"""
    try:
        tags = request.args.getlist('tags')
        agents = custom_agent_manager.get_marketplace_agents(tags if tags else None)
        return jsonify({"agents": agents, "total": len(agents)}), 200
    except Exception as e:
        logger.error(f"Error getting marketplace agents: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/marketplace/<agent_id>/install', methods=['POST'])
def install_agent(agent_id):
    """Install a marketplace agent"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        result = custom_agent_manager.install_agent(agent_id, user_id)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error installing agent: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/marketplace/<agent_id>/rate', methods=['POST'])
def rate_agent(agent_id):
    """Rate and review a marketplace agent"""
    try:
        data = request.json
        rating = data.get('rating')
        review = data.get('review', '')
        
        if not rating:
            return jsonify({"error": "rating is required"}), 400
        
        result = custom_agent_manager.rate_agent(agent_id, rating, review)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error rating agent: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/tools/available', methods=['GET'])
def get_available_tools():
    """Get all available tools for custom agents"""
    try:
        from custom_agents import ToolBuilder
        tools = ToolBuilder.get_available_tools()
        
        # Organize by category
        categories = {}
        for tool_name, tool_info in tools.items():
            category = tool_info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append({
                "id": tool_name,
                "name": tool_info["name"],
                "description": tool_info["description"]
            })
        
        return jsonify({
            "success": True,
            "tools": tools,
            "categories": categories
        }), 200
    except Exception as e:
        logger.error(f"Error getting available tools: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/tools/<tool_name>', methods=['GET'])
def get_tool_details(tool_name):
    """Get detailed information about a tool"""
    try:
        from custom_agents import ToolBuilder
        tool = ToolBuilder.get_tool_info(tool_name)
        
        if not tool:
            return jsonify({"error": "Tool not found"}), 404
        
        return jsonify({
            "success": True,
            "tool": tool
        }), 200
    except Exception as e:
        logger.error(f"Error getting tool details: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/custom/<agent_id>/chat', methods=['POST'])
@limiter.limit("30 per minute")
def custom_agent_chat(agent_id):
    """Chat with a custom agent and automatically execute its tools (with analytics)"""
    
    # Use ExecutionTimer context manager for analytics
    with ExecutionTimer(agent_analytics, agent_id) as timer:
        try:
            data = request.json
            message = data.get('message', '').strip()
            
            if not message:
                return jsonify({"error": "Message is required"}), 400
            
            logger.info(f"[CUSTOM AGENT CHAT] Agent {agent_id} received message: {message}")
            
            agent_data = custom_agent_manager.get_agent(agent_id)
            if not agent_data:
                return jsonify({"error": f"Agent '{agent_id}' not found"}), 404
            
            # Get agent's custom tools
            agent_tools = agent_data.get('tools', [])
            custom_tool_ids = [t for t in agent_tools if t.startswith('custom_') or len(t) == 8]
            
            response = ""
            
            # If agent has custom tools, try to execute them automatically
            if custom_tool_ids:
                executed_results = []
                
                for tool_id in custom_tool_ids:
                    custom_tool = dynamic_tool_builder.get_tool(tool_id)
                    if not custom_tool:
                        continue
                    
                    # Track tool usage for analytics
                    timer.add_tool_used(custom_tool['name'])
                    
                    # Extract parameters from the message intelligently
                    params = {}
                    
                    # For text processing tools, check common patterns
                    if custom_tool['integration_type'] == 'custom_code':
                        import re
                        
                        # Priority 1: Extract text in quotes (both single and double)
                        quoted_text = re.findall(r'["\']([^"\']+)["\']', message)
                        if quoted_text:
                            params['text'] = quoted_text[0]
                            logger.info(f"[EXTRACTION] Found quoted text: {quoted_text[0]}")
                        else:
                            # Priority 2: Look for "convert X to" or "make X uppercase" patterns
                            patterns = [
                                r'convert\s+([^\s]+)\s+to',
                                r'make\s+([^\s]+)\s+',
                                r'transform\s+([^\s]+)',
                                r'process\s+([^\s]+)',
                                r'uppercase\s+([^\s]+)',
                                r'lowercase\s+([^\s]+)',
                            ]
                            
                            for pattern in patterns:
                                match = re.search(pattern, message.lower())
                                if match:
                                    params['text'] = match.group(1)
                                    logger.info(f"[EXTRACTION] Found via pattern '{pattern}': {match.group(1)}")
                                    break
                            
                            # Priority 3: If still no match, use the whole message
                            if 'text' not in params:
                                params['text'] = message
                                logger.info(f"[EXTRACTION] Using whole message as text")
                    
                    # Try executing the tool
                    try:
                        logger.info(f"[TOOL EXECUTION] Executing {custom_tool['name']} with params: {params}")
                        result = dynamic_tool_builder.execute_tool(tool_id, params)
                        
                        if result.get('success'):
                            executed_results.append({
                                'tool_name': custom_tool['name'],
                                'result': result.get('result', {}),
                                'success': True
                            })
                            logger.info(f"[TOOL SUCCESS] {custom_tool['name']} executed successfully")
                        else:
                            executed_results.append({
                                'tool_name': custom_tool['name'],
                                'error': result.get('error'),
                                'success': False
                            })
                            logger.error(f"[TOOL FAILED] {custom_tool['name']}: {result.get('error')}")
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_id}: {str(e)}")
                        continue
                
                # Build response based on execution results
                if executed_results:
                    response = f"I'm {agent_data['name']}, a {agent_data['role']}.\n\n"
                    
                    for exec_result in executed_results:
                        if exec_result['success']:
                            response += f"**{exec_result['tool_name']} Results:**\n\n"
                            
                            result_data = exec_result['result']
                            if isinstance(result_data, dict):
                                for key, value in result_data.items():
                                    response += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                            else:
                                response += f"{result_data}\n"
                            response += "\n"
                        else:
                            response += f"⚠️ {exec_result['tool_name']} failed: {exec_result.get('error', 'Unknown error')}\n\n"
                else:
                    response = f"I'm {agent_data['name']}, a {agent_data['role']}.\n\n"
                    response += f"I have access to these tools:\n"
                    for tool_id in custom_tool_ids:
                        tool = dynamic_tool_builder.get_tool(tool_id)
                        if tool:
                            response += f"- {tool['name']}: {tool['description']}\n"
                    response += f"\nHowever, I couldn't process your request. Please provide input in a clearer format."
            else:
                response = f"I'm {agent_data['name']}, a {agent_data['role']}.\n\n"
                response += f"Instructions: {agent_data['system_instructions']}\n\n"
                response += f"User message: {message}\n\n"
                response += "I don't have any custom tools configured yet. Please add tools to enable my capabilities."
            
            # Store conversation
            if "custom" not in conversations:
                conversations["custom"] = {}
            if agent_id not in conversations["custom"]:
                conversations["custom"][agent_id] = []
            
            conversations["custom"][agent_id].append({
                "type": "user",
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            conversations["custom"][agent_id].append({
                "type": "assistant",
                "message": response,
                "tools_available": agent_tools,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"[CUSTOM AGENT RESPONSE] Final response length: {len(response)}")
            
            return jsonify({
                "agent_id": agent_id,
                "agent_name": agent_data['name'],
                "request": message,
                "response": response,
                "tools_available": agent_tools,
                "timestamp": datetime.now().isoformat()
            }), 200
        
        except Exception as e:
            logger.error(f"Error in custom agent chat: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
# Add an endpoint to execute a tool from an agent
@app.route('/api/agents/custom/<agent_id>/execute-tool', methods=['POST'])
def execute_agent_tool(agent_id):
    """Execute a custom tool as part of agent interaction"""
    try:
        data = request.json
        tool_id = data.get('tool_id')
        params = data.get('params', {})
        
        if not tool_id:
            return jsonify({"error": "tool_id is required"}), 400
        
        # Verify agent has this tool
        agent_data = custom_agent_manager.get_agent(agent_id)
        if not agent_data or tool_id not in agent_data.get('tools', []):
            return jsonify({"error": "Agent doesn't have access to this tool"}), 403
        
        # Execute the tool
        result = dynamic_tool_builder.execute_tool(tool_id, params)
        
        return jsonify({
            "success": True,
            "tool_id": tool_id,
            "agent_id": agent_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error executing agent tool: {str(e)}")
        return jsonify({"error": str(e)}), 500
            
# ============================================================================
# DYNAMIC TOOLS ENDPOINTS
# ============================================================================

@app.route('/api/tools/integration-types', methods=['GET'])
def get_integration_types():
    """Get available integration types"""
    try:
        return jsonify({
            "success": True,
            "types": dynamic_tool_builder.INTEGRATION_TYPES
        }), 200
    except Exception as e:
        logger.error(f"Error getting integration types: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools', methods=['POST'])
def create_dynamic_tool():
    """Create a new dynamic tool"""
    try:
        data = request.json
        data['created_by'] = data.get('created_by', 'default_user')
        
        result = dynamic_tool_builder.create_tool(data)
        
        if result["success"]:
            broadcast_update('tool_created', {
                'tool_id': result['tool_id'],
                'name': data.get('name')
            })
        
        return jsonify(result), 201 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error creating tool: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools/<tool_id>', methods=['GET'])
def get_dynamic_tool(tool_id):
    """Get tool details"""
    try:
        tool = dynamic_tool_builder.get_tool(tool_id)
        if not tool:
            return jsonify({"error": "Tool not found"}), 404
        return jsonify(tool), 200
    except Exception as e:
        logger.error(f"Error getting tool: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools/<tool_id>', methods=['PUT'])
def update_dynamic_tool(tool_id):
    """Update a tool"""
    try:
        data = request.json
        result = dynamic_tool_builder.update_tool(tool_id, data)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error updating tool: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools/<tool_id>', methods=['DELETE'])
def delete_dynamic_tool(tool_id):
    """Delete a tool"""
    try:
        result = dynamic_tool_builder.delete_tool(tool_id)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error deleting tool: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools/<tool_id>/test', methods=['POST'])
def test_dynamic_tool(tool_id):
    """Test a tool"""
    try:
        data = request.json
        test_input = data.get('input', {})
        
        result = dynamic_tool_builder.test_tool(tool_id, test_input)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error testing tool: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools/<tool_id>/publish', methods=['POST'])
def publish_dynamic_tool(tool_id):
    """Publish a tool"""
    try:
        result = dynamic_tool_builder.publish_tool(tool_id)
        
        if result["success"]:
            broadcast_update('tool_published', {
                'tool_id': tool_id,
                'name': result['tool'].get('name')
            })
        
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error publishing tool: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools/user/<user_id>', methods=['GET'])
def get_user_tools(user_id):
    """Get all tools created by a user"""
    try:
        tools = dynamic_tool_builder.get_user_tools(user_id)
        return jsonify({
            "success": True,
            "tools": tools,
            "total": len(tools)
        }), 200
    except Exception as e:
        logger.error(f"Error getting user tools: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools/<tool_id>/execute', methods=['POST'])
def execute_dynamic_tool(tool_id):
    """Execute a tool"""
    try:
        data = request.json
        params = data.get('params', {})
        
        result = dynamic_tool_builder.execute_tool(tool_id, params)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error executing tool: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        "storage_backend": Config.STORAGE_BACKEND,
        "database_type": Config.DATABASE_TYPE if Config.STORAGE_BACKEND == 'database' else None,
        "analytics_enabled": Config.ENABLE_ANALYTICS,
        "testing_enabled": Config.ENABLE_TESTING
    }), 200


@app.route('/api/config/storage', methods=['POST'])
def switch_storage():
    """Switch storage backend"""
    try:
        data = request.json
        backend = data.get('backend', 'json')
        
        if backend not in ['json', 'database']:
            return jsonify({"error": "Backend must be 'json' or 'database'"}), 400
        
        Config.switch_storage_backend(backend)
        
        # Reinitialize managers with new backend
        global custom_agent_manager, dynamic_tool_builder
        from agents.custom_agents import CustomAgentManager
        from tools.dynamic_tools import DynamicToolBuilder
        
        custom_agent_manager = CustomAgentManager()
        dynamic_tool_builder = DynamicToolBuilder()
        
        return jsonify({
            "success": True,
            "message": f"Switched to {backend} storage",
            "backend": backend
        }), 200
    
    except Exception as e:
        logger.error(f"Error switching storage: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/analytics/agents/<agent_id>', methods=['GET'])
def get_agent_analytics(agent_id):
    """Get analytics for a specific agent"""
    try:
        stats = agent_analytics.get_agent_stats(agent_id)
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/agents', methods=['GET'])
def get_all_analytics():
    """Get analytics for all agents"""
    try:
        stats = agent_analytics.get_all_stats()
        return jsonify({"agents": stats}), 200
    except Exception as e:
        logger.error(f"Error getting all analytics: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get dashboard summary of all analytics"""
    try:
        all_stats = agent_analytics.get_all_stats()
        
        total_executions = sum(s['total_executions'] for s in all_stats)
        avg_success_rate = sum(s['success_rate'] for s in all_stats) / len(all_stats) if all_stats else 0
        
        return jsonify({
            "total_agents": len(all_stats),
            "total_executions": total_executions,
            "avg_success_rate": round(avg_success_rate, 2),
            "top_agents": all_stats[:5],  # Top 5 by usage
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# TESTING ENDPOINTS
# ============================================================================

@app.route('/api/testing/agents/<agent_id>/suite', methods=['POST'])
def create_test_suite(agent_id):
    """Create a test suite for an agent"""
    try:
        data = request.json
        agent_name = data.get('agent_name', f'Agent {agent_id}')
        tests = data.get('tests', [])
        
        suite = agent_tester.create_test_suite(agent_id, agent_name)
        
        for test_data in tests:
            suite.add_quick_test(
                name=test_data.get('name'),
                input_message=test_data.get('input'),
                expected_contains=test_data.get('expected_contains')
            )
        
        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "test_count": len(tests),
            "suite": suite.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating test suite: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/testing/agents/<agent_id>/suite', methods=['GET'])
def get_test_suite(agent_id):
    """Get test suite for an agent"""
    try:
        suite = agent_tester.get_test_suite(agent_id)
        return jsonify(suite.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting test suite: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/testing/agents/<agent_id>/run', methods=['POST'])
def run_agent_tests(agent_id):
    """Run all tests for an agent"""
    try:
        data = request.json
        agent_type = data.get('agent_type', 'custom')
        
        result = agent_tester.run_test_suite(agent_id, agent_type)
        
        broadcast_update('test_completed', {
            'agent_id': agent_id,
            'passed': result['passed'],
            'failed': result['failed']
        })
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/testing/agents/<agent_id>/history', methods=['GET'])
def get_test_history(agent_id):
    """Get test history for an agent"""
    try:
        history = agent_tester.get_test_history(agent_id)
        summary = agent_tester.get_test_summary(agent_id)
        
        return jsonify({
            "agent_id": agent_id,
            "summary": summary,
            "history": history[-50:]  # Last 50 tests
        }), 200
    except Exception as e:
        logger.error(f"Error getting test history: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/testing/agents/<agent_id>/quick-test', methods=['POST'])
def quick_test_agent(agent_id):
    """Run a quick ad-hoc test"""
    try:
        data = request.json
        test_input = data.get('input')
        expected_contains = data.get('expected_contains')
        agent_type = data.get('agent_type', 'custom')
        
        if not test_input:
            return jsonify({"error": "input is required"}), 400
        
        # Create temporary test case
        test_case = TestCase(
            name="Quick Test",
            input_message=test_input,
            expected_output=expected_contains
        )
        
        if expected_contains:
            test_case.validation_func = lambda response: expected_contains.lower() in response.lower()
        
        result = agent_tester.run_test(agent_id, test_case, agent_type)
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error running quick test: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# TEMPLATES ENDPOINTS
# ============================================================================

@app.route('/api/templates', methods=['GET'])
def list_agent_templates():
    """List all agent templates"""
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        search = request.args.get('search')
        
        if search:
            templates = agent_template_library.search_templates(search)
        else:
            templates = agent_template_library.list_templates(category, difficulty)
        
        categories = agent_template_library.get_categories()
        
        return jsonify({
            "templates": templates,
            "total": len(templates),
            "categories": categories
        }), 200
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/templates/<template_id>', methods=['GET'])
def get_template_details(template_id):
    """Get details of a specific template"""
    try:
        template = agent_template_library.get_template(template_id)
        
        if not template:
            return jsonify({"error": "Template not found"}), 404
        
        return jsonify(template.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/templates/<template_id>/create-agent', methods=['POST'])
def create_agent_from_template(template_id):
    """Create an agent from a template"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        
        result = agent_template_library.create_agent_from_template(
            template_id,
            custom_agent_manager,
            user_id
        )
        
        if result["success"]:
            broadcast_update('agent_created_from_template', {
                'agent_id': result['agent_id'],
                'template_id': template_id
            })
        
        return jsonify(result), 201 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error creating agent from template: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/templates/categories', methods=['GET'])
def get_template_categories():
    """Get all template categories"""
    try:
        categories = agent_template_library.get_categories()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/templates/search', methods=['GET'])
def search_templates():
    """Search templates"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        results = agent_template_library.search_templates(query)
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        }), 200
    except Exception as e:
        logger.error(f"Error searching templates: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# SCHEDULE HELPERS
# ============================================================================

def _store_conversation(session_key: str, user_msg: str, assistant_msg: str):
    conversations["orchestrator"] = conversations.get("orchestrator", [])
    conversations["orchestrator"].append({"type": "user", "message": user_msg, "timestamp": datetime.now().isoformat()})
    conversations["orchestrator"].append({"type": "assistant", "message": assistant_msg, "timestamp": datetime.now().isoformat()})


def _create_job_from_spec(spec: dict) -> dict:
    """Create an APScheduler job from a spec dict produced by intent_to_job_spec"""
    from datetime import datetime as dt
    stype = spec.get("schedule_type", "cron")
    common = dict(
        job_id=spec["job_id"],
        name=spec["name"],
        agent_id=spec["agent_id"],
        prompt=spec["prompt"],
        schedule_desc=spec["schedule_desc"],
    )
    if stype == "cron":
        c = spec.get("cron", {})
        return scheduler_engine.add_cron_job(
            **common,
            hour=c.get("hour"), minute=c.get("minute", 0),
            day_of_week=c.get("day_of_week", "*"),
            day=c.get("day", "*"), month=c.get("month", "*"),
        )
    elif stype == "interval":
        iv = spec.get("interval", {})
        return scheduler_engine.add_interval_job(
            **common, hours=iv.get("hours", 0), minutes=iv.get("minutes", 0),
        )
    elif stype == "one_shot":
        run_at = dt.fromisoformat(spec["run_at"])
        return scheduler_engine.add_one_shot_job(**common, run_at=run_at)
    return {"success": False, "error": f"Unknown schedule_type: {stype}"}


# ============================================================================
# SCHEDULE ENDPOINTS
# ============================================================================

@app.route('/api/schedules', methods=['GET'])
def list_schedules():
    """List all scheduled jobs"""
    try:
        jobs = scheduler_engine.list_jobs()
        return jsonify({"jobs": jobs, "total": len(jobs)}), 200
    except Exception as e:
        logger.error(f"Error listing schedules: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    """Manually create a scheduled job"""
    try:
        data = request.json
        schedule_type = data.get('schedule_type', 'cron')
        common = dict(
            job_id=data.get('job_id', f"job_{uuid.uuid4().hex[:8]}"),
            name=data.get('name', 'Untitled Job'),
            agent_id=data.get('agent_id', 'orchestrator'),
            prompt=data.get('prompt', ''),
            schedule_desc=data.get('schedule_desc', ''),
        )

        if schedule_type == 'cron':
            result = scheduler_engine.add_cron_job(
                **common,
                hour=data.get('hour'), minute=data.get('minute', 0),
                day_of_week=data.get('day_of_week', '*'),
                day=data.get('day', '*'), month=data.get('month', '*'),
            )
        elif schedule_type == 'interval':
            result = scheduler_engine.add_interval_job(
                **common, hours=data.get('hours', 0), minutes=data.get('minutes', 0),
            )
        elif schedule_type == 'one_shot':
            from datetime import datetime as dt
            result = scheduler_engine.add_one_shot_job(
                **common, run_at=dt.fromisoformat(data.get('run_at')),
            )
        else:
            return jsonify({"error": f"Unknown schedule_type: {schedule_type}"}), 400

        if result.get("success"):
            broadcast_update('schedule_created', result)
        return jsonify(result), 201 if result.get("success") else 400
    except Exception as e:
        logger.error(f"Error creating schedule: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/schedules/<job_id>', methods=['GET'])
def get_schedule(job_id):
    try:
        job = scheduler_engine.get_job(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        return jsonify(job), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/schedules/<job_id>', methods=['DELETE'])
def delete_schedule(job_id):
    try:
        result = scheduler_engine.delete_job(job_id)
        if result.get("success"):
            broadcast_update('schedule_deleted', {"job_id": job_id})
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/schedules/<job_id>/pause', methods=['POST'])
def pause_schedule(job_id):
    try:
        result = scheduler_engine.pause_job(job_id)
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/schedules/<job_id>/resume', methods=['POST'])
def resume_schedule(job_id):
    try:
        result = scheduler_engine.resume_job(job_id)
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/schedules/<job_id>/run-now', methods=['POST'])
def run_schedule_now(job_id):
    try:
        result = scheduler_engine.run_now(job_id)
        return jsonify(result), 200 if result.get("success") else 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/schedules/history', methods=['GET'])
def schedule_history():
    try:
        job_id = request.args.get('job_id')
        limit = request.args.get('limit', 50, type=int)
        history = scheduler_engine.get_execution_history(job_id, limit)
        return jsonify({"history": history, "total": len(history)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import atexit
    atexit.register(scheduler_engine.shutdown)

    print("\n" + "=" * 70)
    print("  MULTI-AGENT AI SYSTEM - FLASK API SERVER WITH WEBSOCKET")
    print("=" * 70)
    print("\n✅ Server starting on http://localhost:5000")
    print("✅ WebSocket available for real-time updates")
    print("✅ Scheduler running (cron jobs active)")
    print("\n📚 API Documentation:")
    print("   Health: GET /api/health")
    print("   Status: GET /api/status")
    print("   Agents: GET /api/agents")
    print("   Chat: POST /api/agents/<id>/chat")
    print("   Workflows: GET/POST /api/workflows")
    print("   Schedules: GET/POST /api/schedules")
    print("   Templates: GET /api/templates")
    print("   Notifications: GET /api/notifications")
    print("\n🔗 Connect your React app to http://localhost:5000")
    print("=" * 70 + "\n")

    socketio.run(app, debug=True, host='0.0.0.0', port=5000)