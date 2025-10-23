"""
Flask API Server - RESTful API for the multi-agent system with WebSocket support
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from typing import Dict, Any
import json
import logging
from datetime import datetime

from agent_framework import Agent
from home_agent import home_agent, controller as home_controller
from calendar_agent import calendar_agent, manager as calendar_manager
from finance_agent import finance_agent, planner as finance_planner
from workflow_engine import WorkflowEngine, WorkflowTask
from workflow_templates import WorkflowTemplates

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

# Store agent conversations
conversations = {
    "home": [],
    "calendar": [],
    "finance": []
}

# Store active connections
active_connections = []
notification_history = []

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
        
        result = home_controller.set_thermostat(temperature, mode)
        
        broadcast_update('home_update', {
            'type': 'thermostat',
            'temperature': temperature
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
        result = calendar_manager.get_calendar_events(days)
        import json as json_module
        events = json_module.loads(result)
        return jsonify(events), 200
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
            on_failure=data.get('on_failure', 'stop')
        )
        
        workflow.add_task(task)
        return jsonify({"message": "Task added"}), 201
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
    print("\n" + "=" * 70)
    print("  MULTI-AGENT AI SYSTEM - FLASK API SERVER WITH WEBSOCKET")
    print("=" * 70)
    print("\n✅ Server starting on http://localhost:5000")
    print("✅ WebSocket available for real-time updates")
    print("\n📚 API Documentation:")
    print("   Health: GET /api/health")
    print("   Status: GET /api/status")
    print("   Agents: GET /api/agents")
    print("   Chat: POST /api/agents/<id>/chat")
    print("   Workflows: GET/POST /api/workflows")
    print("   Templates: GET /api/templates")
    print("   Notifications: GET /api/notifications")
    print("\n🔗 Connect your React app to http://localhost:5000")
    print("=" * 70 + "\n")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)