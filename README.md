# Multi-Agent AI System

A complete AI agent framework with web UI for home automation, calendar/email management, and financial planning, powered by **Ollama Qwen2.5:14b**.

## 🎯 Overview

This project features:

- **Core Agent Framework** - Reasoning loop with tool usage
- **Three Specialized Agents** - Home Assistant, Google Calendar/Gmail, Finance
- **Real API Integrations** - Home Assistant, Google Calendar, Gmail
- **Web UI Dashboard** - React-based interface
- **REST API Server** - Flask backend with WebSocket support
- **Local LLM Integration** - Ollama-based reasoning
- **Workflow Engine** - Multi-agent task coordination

## 📁 Project Structure

```
agent-sphere/
├── agent-sphere-system/          # Backend Python application
│   ├── base/
│   │   ├── agent_framework.py    # Core Agent & Tool classes
│   │   └── api_server.py         # Flask REST API server
│   ├── agents/
│   │   ├── home_agent.py         # Home Assistant integration
│   │   ├── google/
│   │   │   ├── google_auth.py    # Google OAuth handler
│   │   │   ├── gmail_agent.py    # Gmail API integration
│   │   │   ├── google_calendar_agent.py  # Calendar API integration
│   │   │   └── google_unified_agent.py   # Combined Gmail + Calendar
│   │   ├── finance_agent.py      # Financial planning agent
│   │   └── custom_agents.py      # Custom agent builder
│   ├── workflow/                 # Workflow engine
│   ├── analytics/                # Analytics tracking
│   ├── testing/                  # Agent testing framework
│   └── templates/                # Agent templates
│
└── agent-sphere-ui/              # Frontend React application
    ├── src/
    │   ├── App.jsx               # Main application
    │   ├── components/           # React components
    │   └── App.css              # Styles
    └── package.json
```

## ⚙️ Installation

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Ollama with Qwen2.5:14b model
- Home Assistant instance (optional)
- Google Cloud Platform account (for Calendar/Gmail)

### Step 1: Install Ollama

Download from [ollama.ai](https://ollama.ai)

```bash
ollama pull qwen2.5:14b
ollama serve
```

Keep Ollama running in the background on `http://localhost:11434`

### Step 2: Install Backend Dependencies

```bash
cd agent-sphere-system
pip install -r requirements.txt
```

**Required packages:**
- flask
- flask-cors
- flask-socketio
- google-auth
- google-auth-oauthlib
- google-api-python-client
- requests
- python-dotenv

### Step 3: Install Frontend Dependencies

```bash
cd agent-sphere-ui
npm install
```

## 🔧 Configuration

### Home Assistant Setup

1. Get your Home Assistant URL and create a Long-Lived Access Token:
   - Go to your Home Assistant → Profile → Long-Lived Access Tokens
   - Click "Create Token"
   - Copy the token

2. Create `.env` file in `agent-sphere-system/`:

```bash
HA_BASE_URL=http://your-home-assistant:8123/api
HA_ACCESS_TOKEN=your_long_lived_access_token_here
```

### Google Calendar & Gmail Setup

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project
   - Enable APIs: Google Calendar API, Gmail API

2. **Create OAuth Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Download the JSON file

3. **Configure Credentials:**
   - Rename downloaded file to `credentials.json`
   - Place in `agent-sphere-system/` directory
   - **DO NOT commit this file to git** (already in .gitignore)

4. **First-time OAuth Flow:**
   - On first run, a browser window will open
   - Sign in with your Google account
   - Grant permissions for Calendar and Gmail access
   - A `token.json` file will be created automatically
   - **DO NOT commit token.json to git**

### Environment Variables (Optional)

Create `agent-sphere-system/.env`:

```bash
# Home Assistant
HA_BASE_URL=http://localhost:8123/api
HA_ACCESS_TOKEN=your_token_here

# Ollama (defaults shown)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
```

## 🚀 Running the Application

### Start Backend Server

```bash
cd agent-sphere-system
python -m base.api_server
```

Server runs on `http://localhost:5000`

**API Endpoints:**
- `/api/agents/<agent_id>/chat` - Chat with agents
- `/api/home/status` - Home automation status
- `/api/calendar/events` - Calendar events
- `/api/calendar/emails` - Gmail messages
- `/api/workflows/execute` - Run workflows

### Start Frontend UI

```bash
cd agent-sphere-ui
npm start
```

UI opens at `http://localhost:3000`

### Access the Dashboard

Open browser to `http://localhost:3000` and you'll see:

- 🏠 **Home Automation** - Control lights, thermostats, fans, switches
- 📅 **Calendar & Email** - View events, read/send emails
- 💰 **Finance** - Budget tracking and financial planning
- 🔧 **Workflows** - Multi-agent task automation
- 🤖 **Custom Agents** - Build your own agents
- 📊 **Analytics** - Usage metrics and performance

## 🏠 Home Assistant Agent

**Capabilities:**

- Control lights (on/off, brightness)
- Manage thermostats (temperature, mode)
- Control fans (on/off, speed)
- Manage switches
- View real-time device status

**Supported Entities:**
- `light.*` - Smart lights
- `climate.*` - Thermostats
- `fan.*` - Fans
- `switch.*` - Switches
- `lock.*` - Smart locks
- `cover.*` - Garage doors

**Example Requests:**

```
"Turn on the living room lights"
"Set upstairs thermostat to 72 degrees"
"Is the master bedroom fan on?"
"Turn off all lights in the kitchen"
```

**Entity Mapping:**

The agent uses specific entity IDs. Check `agents/home_agent.py` for your entity mappings or use:

```
"Get status of all devices"  # Lists all entities with their IDs
```

## 📅 Calendar & Email Agent

**Capabilities:**

- Read unread emails from Gmail
- Send emails via Gmail
- View upcoming calendar events
- Schedule new events
- Check busy/free times

**Example Requests:**

```
"Do I have any unread emails?"
"What's on my calendar today?"
"Schedule a meeting called 'Review' tomorrow at 2pm for 30 minutes"
"Send an email to john@example.com about the project update"
```

**Important Notes:**

- Event times must include timezone: `2026-01-06T14:00:00-05:00`
- Email IDs are strings, not integers
- First run requires OAuth authentication in browser

## 💰 Financial Planning Agent

**Capabilities:**

- Track account balances
- Record transactions
- Analyze spending by category
- Monitor budget
- Track financial goals

**Example Requests:**

```
"What's my financial summary?"
"Show me spending analysis"
"Add $100 expense for groceries"
"How much have I saved for vacation?"
```

## 🔄 Multi-Agent Workflows

Create workflows that coordinate multiple agents:

```json
{
  "name": "Morning Routine",
  "tasks": [
    {
      "agent": "home",
      "action": "Turn on kitchen lights"
    },
    {
      "agent": "calendar",
      "action": "What's on my calendar today?"
    },
    {
      "agent": "finance",
      "action": "Show me yesterday's spending"
    }
  ]
}
```

## 🤖 Custom Agents

Build your own agents via the UI:

1. Go to "Custom Agents" tab
2. Click "Create New Agent"
3. Define name, role, and system instructions
4. Select tools from available tool library
5. Test and publish

## 🐛 Troubleshooting

### "Cannot connect to Ollama"

- Ensure `ollama serve` is running
- Check `http://localhost:11434` is accessible
- Verify Qwen2.5:14b is installed: `ollama list`

### Home Assistant not working

- Check `HA_BASE_URL` in `.env`
- Verify access token is valid
- Test: `curl -H "Authorization: Bearer YOUR_TOKEN" http://your-ha:8123/api/states`

### Google Calendar/Gmail errors

**"insufficientPermissions" (403 error):**
1. Delete `token.json`
2. Update scopes in `agents/google/google_auth.py` if needed
3. Restart backend to trigger OAuth re-authentication
4. Grant all requested permissions

**"credentials.json not found":**
- Download OAuth credentials from Google Cloud Console
- Save as `credentials.json` in `agent-sphere-system/`

### Frontend not loading data

- Check backend is running on port 5000
- Check browser console for CORS errors
- Verify API endpoints in browser: `http://localhost:5000/api/home/status`

### Agent not understanding requests

- Increase `max_iterations` in `agent_framework.py`
- Check system instructions in agent definition
- Verify tool descriptions are clear
- View agent reasoning with `verbose=True`

## 🔐 Security Notes

**Never commit these files:**
- `credentials.json` - OAuth client credentials
- `token.json` - Access tokens for your Google account
- `.env` - Home Assistant tokens and API keys

These are already in `.gitignore`.

**OAuth Scopes:**
- `https://www.googleapis.com/auth/calendar` - Full calendar access
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- `https://www.googleapis.com/auth/gmail.send` - Send emails

## 📚 API Documentation

### Chat with Agent

```bash
POST /api/agents/home/chat
{
  "message": "Turn on living room lights"
}
```

### Get Home Status

```bash
GET /api/home/status
```

### Get Calendar Events

```bash
GET /api/calendar/events?days=7
```

### Get Emails

```bash
GET /api/calendar/emails?limit=10&unread_only=true
```

## 🎓 Development

### Adding New Tools

```python
from base.agent_framework import Tool

def my_custom_tool(param1: str) -> str:
    return f"Result: {param1}"

new_tool = Tool(
    name="my_tool",
    description="Does something useful",
    func=my_custom_tool,
    params={"param1": "str (required)"}
)

agent.tools["my_tool"] = new_tool
```

### Adding New Agents

See `agents/custom_agents.py` for the custom agent framework.

### Modifying UI

React components are in `agent-sphere-ui/src/components/`

### Testing

```bash
# Test individual agents
python agents/home_agent.py
python agents/google/google_unified_agent.py
python agents/finance_agent.py
```

## 📝 License

Open source - feel free to modify and extend!

## 🚀 Next Steps

1. Configure your Home Assistant integration
2. Set up Google Calendar/Gmail OAuth
3. Build custom agents for your use cases
4. Create workflows to automate daily tasks
5. Extend with additional API integrations

Enjoy building! 🎉
