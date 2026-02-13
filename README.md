# Agent Sphere

A complete, self-hosted AI agent platform with a web UI for home automation, calendar/email management, financial planning, scheduled automation, webhook triggers, and multi-LLM support.

## 🎯 Overview

- **Core Agent Framework** — Reasoning loop with tool usage
- **Specialized Agents** — Home Assistant, Google Calendar/Gmail, Finance
- **Smart Multi-Agent Orchestrator** — Routes queries to the right agents automatically
- **Custom Agent Builder** — Create and publish your own AI agents via UI or code
- **Agent Marketplace** — Browse and deploy pre-built agent templates
- **Visual Workflow Builder** — Drag-and-drop multi-agent workflow design
- **Tool Builder** — Create custom tools and attach them to any agent
- **Scheduled Tasks** — Natural language cron/interval/one-shot job creation; jobs survive restarts
- **Webhooks** — Unique HTTP trigger URLs per agent; external services POST to fire any agent
- **Multi-LLM Support** — Ollama (local), Anthropic Claude, OpenAI GPT, Google Gemini with automatic failover
- **Analytics Dashboard** — Track performance, response times, and usage metrics
- **Testing Framework** — Automated test suites and quick ad-hoc testing
- **Real API Integrations** — Home Assistant, Google Calendar, Gmail
- **Web UI Dashboard** — React-based interface with Matrix / Cyber / Classic themes
- **REST API + WebSocket** — Flask backend with real-time updates

---

## 📁 Project Structure

```
agent-sphere/
├── agent-sphere-system/          # Backend Python application
│   ├── base/
│   │   ├── agent_framework.py    # Core Agent & Tool classes (LLM-agnostic)
│   │   └── api_server.py         # Flask REST API + WebSocket server
│   ├── agents/
│   │   ├── home_agent.py         # Home Assistant integration
│   │   ├── google/
│   │   │   ├── google_auth.py
│   │   │   ├── gmail_agent.py
│   │   │   ├── google_calendar_agent.py
│   │   │   └── google_unified_agent.py
│   │   ├── finance_agent.py
│   │   └── custom_agents.py
│   ├── llm/                      # Multi-LLM router
│   │   ├── llm_config.py         # Provider config & API key storage
│   │   └── llm_router.py         # Unified interface + failover
│   ├── scheduler/                # Cron/scheduled task engine
│   │   ├── scheduler_engine.py   # APScheduler with SQLite persistence
│   │   └── schedule_intent.py    # LLM-based natural language intent detection
│   ├── webhook/                  # HTTP trigger system
│   │   └── webhook_manager.py    # Token management, execution log
│   ├── workflow/                 # Workflow engine
│   ├── analytics/                # Analytics tracking
│   ├── testing/                  # Agent testing framework
│   ├── templates/                # Agent templates
│   ├── data/                     # Runtime data (configs, logs, job store)
│   └── requirements.txt
│
└── agent-sphere-ui/              # Frontend React application
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── HomeAutomation.jsx
    │   │   ├── ScheduleManager.jsx   # Cron job UI
    │   │   ├── WebhookManager.jsx    # Webhook UI
    │   │   ├── LLMSettings.jsx       # Multi-LLM config UI
    │   │   ├── AgentBuilder.jsx
    │   │   ├── WorkflowBuilder.jsx
    │   │   ├── ToolBuilder.jsx
    │   │   ├── AnalyticsDashboard.jsx
    │   │   ├── TestRunner.jsx
    │   │   └── TemplateBrowser.jsx
    │   └── App.css
    └── package.json
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Ollama with at least one model pulled (optional if using a cloud LLM)
- Home Assistant instance (optional)
- Google Cloud Platform account (for Calendar/Gmail, optional)

### Step 1: Ollama (local LLM)

Download from [ollama.ai](https://ollama.ai)

```bash
ollama pull qwen2.5:14b
ollama serve
```

Runs on `http://localhost:11434` by default. You can change the URL later in the 🧠 LLM Settings tab.

### Step 2: Backend

```bash
cd agent-sphere-system
pip install -r requirements.txt
```

### Step 3: Frontend

```bash
cd agent-sphere-ui
npm install
```

---

## 🔧 Configuration

### Home Assistant

1. In Home Assistant go to **Profile → Long-Lived Access Tokens → Create Token**.
2. Create `agent-sphere-system/.env`:

```bash
HA_BASE_URL=http://your-home-assistant:8123/api
HA_ACCESS_TOKEN=your_token_here
```

### Google Calendar & Gmail

1. Create a Google Cloud project and enable the **Google Calendar API** and **Gmail API**.
2. Create an OAuth 2.0 credential (Desktop app) and download the JSON file.
3. Rename it to `credentials.json` and place it in `agent-sphere-system/`.
4. On first run a browser window opens for OAuth. A `token.json` is created automatically.

> **Never commit `credentials.json` or `token.json`** — they are already in `.gitignore`.

### Cloud LLM providers (optional)

Configure directly in the UI under **🧠 LLM Settings** after starting the server. Keys are stored locally in `data/llm_config.json` and never sent externally.

---

## 🚀 Running

```bash
# Terminal 1 — backend
cd agent-sphere-system
python -m base.api_server

# Terminal 2 — frontend
cd agent-sphere-ui
npm start
```

- Backend: `http://localhost:5000`
- Frontend: `http://localhost:3000`

---

## 🗺️ Navigation

| Tab | Description |
|---|---|
| 🏠 **Home** | Home Assistant control center |
| 💬 **Chat / Orchestrator** | Direct agent chat + Smart multi-agent assistant |
| 📅 **Calendar** | Events and email via Google |
| 💰 **Finance** | Budget and expense tracking |
| ⏰ **Schedules** | Create and manage scheduled jobs |
| 🔗 **Webhooks** | HTTP trigger URLs for agents |
| 🤖 **Agents** | Marketplace, custom agents, templates |
| 🔧 **Builder** | Visual workflow, tool builder, workflow manager |
| 📊 **Insights** | Analytics and testing |
| 🧠 **LLM** | Provider config, API keys, failover order |

**UI Themes:** 🟢 Matrix · 🔵 Cyber · 🟣 Classic

---

## ⏰ Scheduled Tasks

The scheduler lets you automate any agent task on a schedule — set it up by typing naturally in the Smart Assistant chat, or create jobs manually in the **⏰ Schedules** tab.

### Natural language chat (Smart Assistant)

```
"Summarize my unread emails every morning at 8am"
"Check home device status every 30 minutes"
"Run financial summary every Sunday at 6pm"
```

The assistant detects scheduling intent, asks for confirmation, then creates the job automatically. Jobs persist across server restarts via SQLite.

### Schedule types

| Type | Example |
|---|---|
| **Cron** | Daily at a fixed time, specific days of week |
| **Interval** | Every N hours / minutes |
| **One-shot** | Run once at a specific datetime |

### Schedules tab

- View all jobs with next-run time and status
- Pause / resume / delete individual jobs
- Run any job immediately
- View per-job execution history

### Manual creation via API

```bash
# Interval job — every 30 minutes
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_type": "interval",
    "name": "Email check",
    "agent_id": "calendar",
    "prompt": "Summarize my unread emails",
    "minutes": 30
  }'

# Cron job — weekdays at 9am
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_type": "cron",
    "name": "Daily briefing",
    "agent_id": "orchestrator",
    "prompt": "Give me a morning briefing: calendar, emails, and home status",
    "hour": 9,
    "minute": 0,
    "day_of_week": "mon-fri"
  }'
```

---

## 🔗 Webhooks

Each webhook is a unique secret URL. POST to it from any external service — CI/CD, monitoring, IFTTT, n8n, Zapier — and the configured agent runs immediately with the payload injected into the prompt.

### Create a webhook

**Via UI:** Open **🔗 Webhooks → + Create**, fill in name, agent, and prompt template.

**Via API:**
```bash
curl -X POST http://localhost:5000/api/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alert Handler",
    "agent_id": "orchestrator",
    "prompt_template": "I received an alert. Message: {{payload.message}}. Severity: {{payload.severity}}. Summarise and suggest an action."
  }'
```

Response includes the `token` field.

### Trigger it

```bash
curl -X POST http://localhost:5000/api/trigger/<token> \
  -H "Content-Type: application/json" \
  -d '{"message": "Disk usage at 94%", "severity": "high"}'
```

Query parameters also work (no body required):

```bash
curl -X POST "http://localhost:5000/api/trigger/<token>?message=Server+restarted&severity=low"
```

### Prompt template variables

| Placeholder | Replaced with |
|---|---|
| `{{payload}}` | Full JSON payload as string |
| `{{payload.key}}` | Value of a specific key in the payload |

### Webhook management

- **Enable / Disable** — disable without deleting
- **Regenerate token** — rotates the secret; old URL stops working
- **Execution log** — view every trigger with payload, response, duration, success/fail

---

## 🧠 Multi-LLM Support

Configure one or more AI providers and set a failover order. If the primary provider fails, the system automatically tries the next one.

### Supported providers

| Provider | Models | Needs API key |
|---|---|---|
| **Ollama** (local) | qwen2.5:14b, llama3.2, mistral, phi3, ... | No |
| **Anthropic** | claude-3-5-sonnet, claude-3-haiku, ... | Yes |
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-3.5-turbo, ... | Yes |
| **Google** | gemini-1.5-pro, gemini-1.5-flash, ... | Yes |

### Setup

1. Open the **🧠 LLM** tab in the UI.
2. Enable the providers you want to use.
3. Paste API keys (stored locally, never sent externally).
4. Select the default provider.
5. Configure the failover order.
6. Click **Test** to verify connectivity.

### Agent-level provider override

Individual agents can be pinned to a specific provider:

```python
from base.agent_framework import Agent

agent = Agent(
    name="my_agent",
    role="Specialist",
    tools=[...],
    llm_provider="anthropic"   # or "openai", "google", "ollama", None (= system default)
)
```

### Failover order

```bash
# Set via API
curl -X POST http://localhost:5000/api/llm/failover \
  -H "Content-Type: application/json" \
  -d '{"order": ["ollama", "anthropic", "openai"]}'
```

---

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

---

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

---

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

---

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

---

## 🤖 Custom Agents - Build & Publish

The Agent Marketplace provides a complete platform for building, testing, and publishing custom AI agents tailored to your specific needs.

### Creating Custom Agents

**Via the UI (Recommended):**

1. **Navigate to Agents Tab**
   - Click **🤖 Agents** in the main navigation
   - Select **🛠️ Marketplace** sub-tab
   - Click **"Create New Agent"**

2. **Define Agent Properties**
   ```
   Name: Your Agent Name (e.g., "Customer Support Agent")
   Role: Brief description (e.g., "Handles customer inquiries")
   System Instructions: Detailed behavior guidelines
   ```

3. **Configure System Instructions**
   - Define the agent's personality and behavior
   - Specify response format and tone
   - Add domain-specific knowledge
   - Set constraints and limitations

   **Example:**
   ```
   You are a helpful customer support agent specializing in technical troubleshooting.
   Always be polite, concise, and solution-oriented. Ask clarifying questions when
   needed. Provide step-by-step instructions for technical issues.
   ```

4. **Select Tools**
   - Choose from available tool library
   - Common tools: web search, file operations, API calls
   - Custom tools can be added via Tool Builder

5. **Test Your Agent**
   - Use the built-in chat interface to test responses
   - Verify tool usage is working correctly
   - Iterate on instructions based on test results

6. **Publish & Deploy**
   - Click **"Save Agent"** to publish
   - Agent appears in **🤖 My Agents** sub-tab
   - Use immediately via chat interface

### Managing Custom Agents

**My Agents Tab:**
- View all your created agents
- Edit agent configuration
- Test agent performance
- Delete agents you no longer need
- Chat with any of your custom agents

**Best Practices:**
- Start with clear, specific system instructions
- Test thoroughly before deploying
- Use relevant tools for your agent's purpose
- Keep instructions concise but comprehensive
- Document expected behavior and limitations

### Agent Templates

**Templates Tab** provides pre-built agent configurations:

**Available Templates:**
- 🏠 **Home Assistant** - Smart home control
- 💼 **Business Analyst** - Data analysis and reporting
- 🔒 **Security Monitor** - Security alerts and monitoring
- 📊 **Data Processor** - ETL and data transformation
- 🎯 **Task Manager** - Project and task organization
- 📈 **Analytics Expert** - Metrics and insights

**Using Templates:**
1. Browse templates in **📚 Templates** sub-tab
2. Click **"Create from Template"**
3. Customize to your needs
4. Save and deploy

### Programmatic Agent Creation

For advanced users, create agents via Python:

```python
from base.agent_framework import Agent, Tool

def my_tool(param: str) -> str:
    return f"Result: {param}"

new_tool = Tool(
    name="my_tool",
    description="Does something useful",
    func=my_tool,
    params={"param": "str (required)"}
)

agent = Agent(
    name="my_agent",
    role="Specialized assistant",
    tools=[new_tool],
    system_instructions="Your detailed instructions here...",
    llm_provider=None   # None = system default; or "anthropic", "openai", "google", "ollama"
)

result = agent.think_and_act("Your request here")
```

Register the agent in `base/api_server.py` to expose it via the REST API.

---

## 🔧 Workflow Builder & Automation

The Builder tab provides powerful visual tools for creating multi-agent workflows and custom integrations.

### Visual Workflow Builder

**Access:** Click **🔧 Builder** → **🎨 Visual Builder**

**Features:**
- Drag-and-drop workflow design
- Visual task orchestration
- Multi-agent coordination
- Conditional logic and branching
- Real-time execution preview

**Creating a Workflow:**

1. **Start a New Workflow**
   - Click **"Create Workflow"** in Workflows tab
   - Enter Workflow ID (e.g., `morning_routine`)
   - Add name and description
   - Click **"Create & Open in Builder"**

2. **Add Tasks in Visual Builder**
   - Drag agents from the sidebar
   - Connect tasks with arrows
   - Define task actions and parameters
   - Set conditions and dependencies

3. **Configure Task Actions**
   ```
   Task 1: Turn on kitchen lights (Home Agent)
   Task 2: Check calendar for today (Calendar Agent)
   Task 3: Read unread emails (Calendar Agent)
   Task 4: Show financial summary (Finance Agent)
   ```

4. **Add Conditional Logic**
   - Branch based on agent responses
   - Skip tasks based on conditions
   - Handle errors gracefully
   - Implement retry logic

5. **Execute & Monitor**
   - Click **"▶️ Execute"** to run workflow
   - Watch real-time progress
   - View task results
   - Check execution logs

### Tool Builder

**Access:** Click **🔧 Builder** → **🔧 Tool Builder**

Build custom tools that agents can use:

**Creating a Custom Tool:**

1. **Define Tool Properties**
   ```
   Name: weather_check
   Description: Get current weather for a location
   Parameters:
     - location (string, required)
     - units (string, optional: celsius/fahrenheit)
   ```

2. **Implement Tool Logic**
   ```python
   def weather_check(location: str, units: str = "celsius"):
       # Your API call or logic here
       response = requests.get(f"https://api.weather.com/{location}")
       return response.json()
   ```

3. **Test Tool**
   - Use the test interface
   - Verify parameter validation
   - Check response format

4. **Publish Tool**
   - Tool becomes available to all agents
   - Agents can discover and use automatically

### Workflow Management

**Access:** Click **🔧 Builder** → **⚙️ Workflows**

**Features:**
- View all created workflows
- Execute workflows on-demand
- Edit workflow configuration
- Export/Import workflows
- View execution history

**Workflow Templates:**
- 🌅 **Morning Routine** - Lights, calendar, email check
- 🌙 **Evening Shutdown** - Lock doors, set thermostat, turn off lights
- 📧 **Email Digest** - Compile and summarize daily emails
- 🏠 **Away Mode** - Activate security settings
- 📊 **Daily Report** - Aggregate metrics from multiple sources

**Example Workflow JSON:**
```json
{
  "workflow_id": "morning_routine",
  "name": "Morning Routine",
  "description": "Start my day right",
  "tasks": [
    {
      "id": "task1",
      "agent": "home",
      "action": "Turn on kitchen lights",
      "on_success": "task2"
    },
    {
      "id": "task2",
      "agent": "calendar",
      "action": "What's on my calendar today?",
      "on_success": "task3"
    },
    {
      "id": "task3",
      "agent": "calendar",
      "action": "Show me unread emails",
      "on_success": "task4"
    },
    {
      "id": "task4",
      "agent": "finance",
      "action": "What's my account balance?"
    }
  ]
}
```

**Executing Workflows:**

Via UI:
- Navigate to Workflows tab
- Click **"▶️ Execute"** on any workflow
- Monitor progress in real-time

Via API:
```bash
POST /api/workflows/execute
{
  "workflow_id": "morning_routine"
}
```

Via Smart Assistant:
```
"Run my morning routine workflow"
```

---

## 📊 Insights - Analytics & Testing

Monitor performance, track usage, and ensure quality with comprehensive analytics and testing tools.

### Analytics Dashboard

**Access:** Click **📊 Insights** → **📊 Analytics**

**Metrics Tracked:**

**System Overview:**
- Total agents deployed
- Total executions across all agents
- Average success rate
- System health score

**Per-Agent Metrics:**
- Execution count
- Success/failure rate
- Average response time
- Error logs
- Most used tools
- Daily activity trends

**Performance Insights:**
- Response time distribution
- Peak usage hours
- Tool usage patterns
- Common error types
- Success rate trends

**Viewing Analytics:**

1. **Select an Agent**
   - Click on any agent from the list
   - View detailed metrics

2. **Analyze Performance**
   - Check success rate (aim for >95%)
   - Review response times
   - Identify frequently used tools
   - Spot error patterns

3. **Review Activity**
   - See daily execution trends
   - Identify usage patterns
   - Plan for peak times

4. **Export Reports**
   - Generate PDF reports
   - Export CSV data
   - Share metrics with team

### Testing Framework

**Access:** Click **📊 Insights** → **🧪 Testing**

**Features:**
- Automated test suites
- Quick ad-hoc testing
- Regression testing
- Performance benchmarking
- Test history tracking

**Creating Test Suites:**

1. **Select Agent to Test**
   - Choose from your custom agents
   - Or test system agents

2. **Create Test Suite**
   - Click **"Create Test Suite"**
   - Name your test suite

3. **Add Test Cases**
   ```
   Test Name: Check Weather Query
   Input: "What's the weather in New York?"
   Expected Contains: "temperature"
   ```

4. **Run Tests**
   - Click **"▶️ Run Tests"**
   - View pass/fail results
   - Check response times
   - Review error messages

**Quick Testing:**

Test agents without creating a suite:

1. Enter test input
2. Optionally specify expected output
3. Click **"Run Quick Test"**
4. View results immediately

**Test Results:**
- ✅ **Passed** - Response contains expected content
- ❌ **Failed** - Missing expected content or error
- ⏱️ **Response Time** - Performance metric
- 📝 **Actual Output** - Full agent response

**Example Test Suite:**

```json
{
  "agent_id": "custom_weather_agent",
  "tests": [
    {
      "name": "Basic Weather Query",
      "input": "What's the weather in London?",
      "expected_contains": "temperature"
    },
    {
      "name": "Multi-City Query",
      "input": "Compare weather in NYC and LA",
      "expected_contains": "New York"
    },
    {
      "name": "Error Handling",
      "input": "Weather in InvalidCityName123",
      "expected_contains": "not found"
    }
  ]
}
```

**Best Practices:**
- Test after every agent modification
- Create regression test suites
- Test edge cases and error scenarios
- Monitor test pass rates over time
- Set up automated testing schedules

**Viewing Test History:**
- See all past test runs
- Compare results over time
- Identify regressions
- Track improvements

---

## 📚 API Reference

### Agents & Chat

```
GET  /api/agents                          List all agents
POST /api/agents/<id>/chat                Chat with an agent
POST /api/orchestrator/execute            Smart multi-agent query
```

### Schedules

```
GET    /api/schedules                     List all jobs
POST   /api/schedules                     Create a job
GET    /api/schedules/<id>                Get a job
DELETE /api/schedules/<id>                Delete a job
POST   /api/schedules/<id>/pause          Pause a job
POST   /api/schedules/<id>/resume         Resume a job
POST   /api/schedules/<id>/run-now        Run a job immediately
GET    /api/schedules/history             Execution history
```

### Webhooks

```
GET    /api/webhooks                      List webhooks
POST   /api/webhooks                      Create webhook
DELETE /api/webhooks/<token>              Delete webhook
POST   /api/webhooks/<token>/toggle       Enable / disable
POST   /api/webhooks/<token>/regenerate   Rotate secret token
GET    /api/webhooks/log                  Execution log
POST   /api/trigger/<token>               External trigger (the public URL)
```

### LLM

```
GET  /api/llm/providers                   List providers + config
POST /api/llm/providers/<provider>        Set API key / model / enabled
POST /api/llm/default                     Set default provider
POST /api/llm/failover                    Set failover order
POST /api/llm/test/<provider>             Test provider connectivity
```

### Home / Calendar / Finance

```
GET  /api/home/status
GET  /api/calendar/events?days=7
GET  /api/calendar/emails?limit=10&unread_only=true
POST /api/workflows/execute
```

---

## 🐛 Troubleshooting

### "Cannot connect to Ollama"
- Run `ollama serve` and ensure `http://localhost:11434` is reachable.
- Or switch to a cloud provider in the 🧠 LLM Settings tab.

### Scheduler jobs not running
- Check the terminal for APScheduler errors.
- Verify `data/scheduler_jobs.sqlite` exists (created on first run).

### Webhook returns 404
- Check the token — tokens are case-sensitive.
- Verify the webhook is enabled in the UI.

### Google Calendar/Gmail errors
- **403 insufficientPermissions**: Delete `token.json` and restart to re-authenticate.
- **credentials.json not found**: Download from Google Cloud Console and place in `agent-sphere-system/`.

### Frontend not loading data
- Ensure backend is on port 5000.
- Check browser console for CORS errors.
- Test: `curl http://localhost:5000/api/health`

---

## 🔐 Security

**Never commit:**
- `credentials.json` — Google OAuth client credentials
- `token.json` — Google access/refresh tokens
- `.env` — Home Assistant tokens
- `data/llm_config.json` — Cloud LLM API keys

All are already in `.gitignore`.

Webhook tokens are random 32-character hex strings. Rotate them at any time with the **Regen Token** button.

---

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

### Creating Custom Agents (Code-Based)

For developers who want to create agents with custom API integrations or complex logic beyond what the UI builder provides.

#### Step 1: Understand the Agent Framework

All agents inherit from the base `Agent` class in `base/agent_framework.py`:

```python
class Agent:
    def __init__(self, name, role, system_instructions, tools=None, llm_provider=None):
        self.name = name
        self.role = role
        self.system_instructions = system_instructions
        self.tools = tools or {}
        self.llm_provider = llm_provider  # None = use system default
```

**Key Components:**
- **name**: Agent identifier (e.g., "home", "calendar", "finance")
- **role**: Brief description of agent's purpose
- **system_instructions**: Detailed prompt defining agent behavior
- **tools**: Dictionary of Tool objects the agent can use
- **llm_provider**: Pin to a specific LLM (`"ollama"`, `"anthropic"`, `"openai"`, `"google"`, or `None`)

#### Step 2: Create Your Agent File

Create a new file in `agent-sphere-system/agents/` (e.g., `weather_agent.py`):

```python
from base.agent_framework import Agent, Tool
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_current_weather(location: str) -> str:
    """Get current weather for a location"""
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather"

    try:
        response = requests.get(url, params={
            "q": location,
            "appid": api_key,
            "units": "metric"
        })
        response.raise_for_status()
        data = response.json()

        return f"""
        Location: {data['name']}, {data['sys']['country']}
        Temperature: {data['main']['temp']}°C
        Feels Like: {data['main']['feels_like']}°C
        Conditions: {data['weather'][0]['description']}
        Humidity: {data['main']['humidity']}%
        Wind Speed: {data['wind']['speed']} m/s
        """
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

weather_tool = Tool(
    name="get_current_weather",
    description="Get the current weather for a specific location. Use city name or 'city, country code'",
    func=get_current_weather,
    params={"location": "string (required) - City name or 'city, country code'"}
)

SYSTEM_INSTRUCTIONS = """
You are a helpful weather assistant. You can provide current weather information
and forecasts for any location in the world.

When users ask about weather:
1. Determine the location from their query
2. Use get_current_weather for current conditions
3. Present information in a clear, readable format
4. Suggest appropriate clothing or activities based on weather
"""

weather_agent = Agent(
    name="weather",
    role="Weather information and forecasts",
    system_instructions=SYSTEM_INSTRUCTIONS,
    tools={"get_current_weather": weather_tool},
    llm_provider=None   # Uses system default
)

if __name__ == "__main__":
    response = weather_agent.think_and_act("What's the weather in London?")
    print(response)
```

#### Step 3: Configure Environment Variables

Add required API keys to `.env`:

```bash
WEATHER_API_KEY=your_openweathermap_api_key_here
```

#### Step 4: Integrate with API Server

Update `agent-sphere-system/base/api_server.py` to include your new agent:

```python
from agents.weather_agent import weather_agent

# In the agents dictionary, add your agent
agents = {
    "home": home_agent,
    "calendar": calendar_agent,
    "finance": finance_agent,
    "weather": weather_agent,
}
```

#### Step 5: Test Your Agent

```bash
# Standalone
python agents/weather_agent.py

# Via API (after starting the backend)
curl -X POST http://localhost:5000/api/agents/weather/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Paris?"}'
```

#### Best Practices for Custom Agents

**Tool Design:**
- Keep tools focused on single responsibilities
- Provide clear, descriptive tool names
- Include comprehensive parameter descriptions
- Handle errors gracefully and return user-friendly messages

**System Instructions:**
- Be specific about agent capabilities
- Define clear boundaries of what the agent can/cannot do
- Include response formatting guidelines
- Add examples of desired behavior

**Error Handling:**
```python
def robust_api_call(param):
    try:
        response = api.call(param)
        return format_success(response)
    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        return f"API error: {e.response.status_code}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "An unexpected error occurred."
```

**Environment Configuration:**
- Use environment variables for API keys
- Provide clear setup instructions
- Include validation for required configuration
- Use sensible defaults where possible

### Modifying UI

React components are in `agent-sphere-ui/src/components/`

**Key Components:**
- `HomeAutomation.jsx` - Home automation UI
- `ScheduleManager.jsx` - Scheduled jobs UI
- `WebhookManager.jsx` - Webhook management UI
- `LLMSettings.jsx` - Multi-LLM configuration UI
- `AnalyticsDashboard.jsx` - Analytics dashboard
- `TestRunner.jsx` - Testing interface
- `TemplateBrowser.jsx` - Agent templates
- `AgentBuilder.jsx` - Agent marketplace
- `WorkflowBuilder.jsx` - Visual workflow designer
- `ToolBuilder.jsx` - Tool creation interface

### Testing

```bash
# Test individual agents
python agents/home_agent.py
python agents/google/google_unified_agent.py
python agents/finance_agent.py

# Test specific agent functionality
python -c "from agents.home_agent import home_agent; \
           print(home_agent.think_and_act('What lights are on?'))"
```

---

## 🎨 UI Features

**Theme Switcher:**
- Click the theme button in the top-right corner
- Cycle through Matrix (green), Cyber (blue), and Classic (purple) themes
- Theme persists across sessions
- All components are fully themed

**Smart Navigation:**
- Grouped tabs reduce clutter
- Sub-tabs organize related features
- Context-aware navigation
- Smooth transitions between views

**Responsive Design:**
- Works on desktop, tablet, and mobile
- Sidebar collapses on smaller screens
- Touch-friendly controls
- Adaptive layouts

---

## 🚀 Next Steps

**Getting Started:**
1. Configure your Home Assistant integration
2. Set up Google Calendar/Gmail OAuth
3. Explore the UI themes (Matrix/Cyber/Classic)
4. Try the Smart Multi-Agent Assistant

**Build & Customize:**
5. Create custom agents in the Marketplace
6. Use agent templates as starting points
7. Build custom tools for your agents
8. Design visual workflows for automation

**Automate:**
9. Set up scheduled tasks via natural language chat
10. Create webhooks to trigger agents from external services
11. Configure multi-LLM failover for reliability

**Monitor & Optimize:**
12. Track agent performance in Analytics
13. Set up automated testing for quality assurance
14. Monitor usage patterns and optimize
15. Export reports and share insights

**Advanced:**
16. Extend with additional API integrations
17. Create complex conditional workflows
18. Build domain-specific agent suites
19. Contribute templates to the marketplace

---

## 📝 License

Open source — modify and extend freely.
