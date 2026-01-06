# Multi-Agent AI System

A complete AI agent framework with web UI for home automation, calendar/email management, and financial planning, powered by **Ollama Qwen2.5:14b**.

## 🎯 Overview

This project features:

- **Core Agent Framework** - Reasoning loop with tool usage
- **Specialized Agents** - Home Assistant, Google Calendar/Gmail, Finance
- **Custom Agent Builder** - Create and publish your own AI agents
- **Agent Marketplace** - Browse and use pre-built agent templates
- **Smart Multi-Agent Assistant** - Orchestrates multiple agents automatically
- **Visual Workflow Builder** - Drag-and-drop workflow design
- **Tool Builder** - Create custom tools for agents
- **Analytics Dashboard** - Track performance and usage metrics
- **Testing Framework** - Automated testing and quality assurance
- **Real API Integrations** - Home Assistant, Google Calendar, Gmail
- **Web UI Dashboard** - React-based interface with Matrix/Cyber/Classic themes
- **REST API Server** - Flask backend with WebSocket support
- **Local LLM Integration** - Ollama-based reasoning

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

**Main Navigation:**
- 🏠 **Dashboard** - Home automation control center
- 💬 **Chat** - Talk to agents or use Smart Assistant
  - 💬 Agent Chat - Direct chat with individual agents
  - 🧠 Smart Assistant - Multi-agent orchestrator
- 📅 **Calendar** - View events and emails
- 💰 **Finance** - Budget tracking and financial planning

**Development Tools:**
- 🤖 **Agents** - Build and manage agents
  - 🛠️ Marketplace - Create new agents
  - 🤖 My Agents - Your custom agents
  - 📚 Templates - Pre-built agent templates
- 🔧 **Builder** - Visual tools and automation
  - 🎨 Visual Builder - Drag-and-drop workflows
  - 🔧 Tool Builder - Create custom tools
  - ⚙️ Workflows - Manage workflow automation
- 📊 **Insights** - Analytics and quality assurance
  - 📊 Analytics - Performance metrics
  - 🧪 Testing - Automated testing

**UI Themes:**
- 🟢 **Matrix** - Terminal green aesthetic (default)
- 🔵 **Cyber** - Cyberpunk blue theme
- 🟣 **Classic** - Purple gradient theme

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

For advanced users, create agents via Python API:

```python
from agents.custom_agents import CustomAgentManager

manager = CustomAgentManager()

agent_config = {
    "name": "My Custom Agent",
    "role": "Specialized assistant",
    "system_instructions": "Your detailed instructions here...",
    "tools": ["web_search", "file_operations"],
    "user_id": "your_user_id"
}

agent = manager.create_agent(agent_config)
```

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

### Creating Custom Agents (Code-Based)

For developers who want to create agents with custom API integrations or complex logic beyond what the UI builder provides.

#### Step 1: Understand the Agent Framework

All agents inherit from the base `Agent` class in `base/agent_framework.py`:

```python
class Agent:
    def __init__(self, name, role, system_instructions, tools=None):
        self.name = name
        self.role = role
        self.system_instructions = system_instructions
        self.tools = tools or {}
        self.ollama_base_url = "http://localhost:11434"
        self.model = "qwen2.5:14b"
```

**Key Components:**
- **name**: Agent identifier (e.g., "home", "calendar", "finance")
- **role**: Brief description of agent's purpose
- **system_instructions**: Detailed prompt defining agent behavior
- **tools**: Dictionary of Tool objects the agent can use

#### Step 2: Create Your Agent File

Create a new file in `agent-sphere-system/agents/` (e.g., `weather_agent.py`):

```python
from base.agent_framework import Agent, Tool
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Define your tools
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

def get_forecast(location: str, days: int = 5) -> str:
    """Get weather forecast for a location"""
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/forecast"

    try:
        response = requests.get(url, params={
            "q": location,
            "appid": api_key,
            "units": "metric",
            "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
        })
        response.raise_for_status()
        data = response.json()

        forecast_text = f"5-Day Forecast for {location}:\n\n"
        for item in data['list'][::8]:  # Get one per day
            date = item['dt_txt']
            temp = item['main']['temp']
            desc = item['weather'][0]['description']
            forecast_text += f"{date}: {temp}°C, {desc}\n"

        return forecast_text
    except Exception as e:
        return f"Error fetching forecast: {str(e)}"

# Create Tool objects
weather_tool = Tool(
    name="get_current_weather",
    description="Get the current weather for a specific location. Use city name or 'city, country code'",
    func=get_current_weather,
    params={"location": "string (required) - City name or 'city, country code'"}
)

forecast_tool = Tool(
    name="get_forecast",
    description="Get 5-day weather forecast for a location",
    func=get_forecast,
    params={
        "location": "string (required) - City name",
        "days": "integer (optional, default: 5) - Number of days"
    }
)

# Define system instructions
SYSTEM_INSTRUCTIONS = """
You are a helpful weather assistant. You can provide current weather information
and forecasts for any location in the world.

When users ask about weather:
1. Determine the location from their query
2. Use get_current_weather for current conditions
3. Use get_forecast for future weather predictions
4. Present information in a clear, readable format
5. Suggest appropriate clothing or activities based on weather

Always be friendly and provide helpful weather-related advice.
"""

# Create the agent
weather_agent = Agent(
    name="weather",
    role="Weather information and forecasts",
    system_instructions=SYSTEM_INSTRUCTIONS,
    tools={
        "get_current_weather": weather_tool,
        "get_forecast": forecast_tool
    }
)

# Test function for standalone execution
if __name__ == "__main__":
    print("🌤️  Weather Agent Test")
    print("-" * 50)

    # Test current weather
    response = weather_agent.chat("What's the weather in London?")
    print(f"Response: {response}")

    # Test forecast
    response = weather_agent.chat("Give me the forecast for New York")
    print(f"\nForecast Response: {response}")
```

#### Step 3: Configure Environment Variables

Add required API keys to `.env`:

```bash
# Weather API (example)
WEATHER_API_KEY=your_openweathermap_api_key_here
```

#### Step 4: Integrate with API Server

Update `agent-sphere-system/base/api_server.py` to include your new agent:

```python
# At the top of the file, import your agent
from agents.weather_agent import weather_agent

# In the agents dictionary (around line 30), add your agent
agents = {
    "home": home_agent,
    "calendar": calendar_agent,
    "finance": finance_agent,
    "weather": weather_agent,  # Add your new agent
}

# Add a status endpoint (optional, around line 150)
@app.route('/api/weather/current/<location>', methods=['GET'])
def get_weather_status(location):
    """Get current weather for a location"""
    try:
        result = weather_agent.tools["get_current_weather"].func(location)
        return jsonify({"success": True, "weather": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

#### Step 5: Add Agent to Frontend UI

Update `agent-sphere-ui/src/App.jsx`:

1. **Add agent to the agents array** (around line 275):

```javascript
const [agents, setAgents] = useState([
  {
    id: "home",
    name: "Home Assistant",
    role: "Smart home control",
    status: "active",
  },
  {
    id: "calendar",
    name: "Calendar & Email",
    role: "Schedule and communication",
    status: "active",
  },
  {
    id: "finance",
    name: "Finance Manager",
    role: "Budget and expenses",
    status: "active",
  },
  {
    id: "weather",
    name: "Weather Assistant",
    role: "Weather info and forecasts",
    status: "active",
  },
]);
```

2. **Add a dedicated tab for your agent** (optional):

```javascript
{activeTab === "weather" && (
  <section className="section">
    <h2>🌤️ Weather Information</h2>

    {/* Add custom UI components here */}
    <div className="weather-dashboard">
      {/* Display current weather */}
      {/* Show forecasts */}
      {/* Quick location search */}
    </div>

    {/* Chat interface */}
    <div className="chat-container">
      {/* Reuse existing chat components */}
    </div>
  </section>
)}
```

#### Step 6: Test Your Agent

**Standalone Testing:**
```bash
cd agent-sphere-system
python agents/weather_agent.py
```

**Via API:**
```bash
# Start the backend
python -m base.api_server

# Test the chat endpoint
curl -X POST http://localhost:5000/api/agents/weather/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Paris?"}'

# Test custom endpoint (if you added one)
curl http://localhost:5000/api/weather/current/London
```

**Via UI:**
1. Start the frontend: `cd agent-sphere-ui && npm start`
2. Navigate to the Chat tab
3. Select "Weather Assistant" from the agent list
4. Ask: "What's the weather in Tokyo?"

#### Best Practices for Custom Agents

**1. Tool Design:**
- Keep tools focused on single responsibilities
- Provide clear, descriptive tool names
- Include comprehensive parameter descriptions
- Handle errors gracefully and return user-friendly messages

**2. System Instructions:**
- Be specific about agent capabilities
- Define clear boundaries of what the agent can/cannot do
- Include response formatting guidelines
- Add examples of desired behavior

**3. Error Handling:**
```python
def robust_api_call(param):
    try:
        # Your API call
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

**4. Environment Configuration:**
- Use environment variables for API keys
- Provide clear setup instructions
- Include validation for required configuration
- Use sensible defaults where possible

**5. Testing:**
- Write unit tests for each tool
- Test edge cases and error scenarios
- Validate API responses
- Test agent reasoning with various queries

#### Example: Complete Agent Structure

```
agent-sphere-system/
├── agents/
│   ├── weather_agent.py         # Your new agent
│   └── weather/                 # Optional: organize complex agents
│       ├── __init__.py
│       ├── weather_api.py       # API wrapper
│       ├── tools.py             # Tool definitions
│       └── prompts.py           # System instructions
├── base/
│   └── api_server.py            # Update to include agent
└── .env                         # Add configuration
```

#### Advanced: Multi-API Agents

For agents that integrate multiple APIs (like the Google Calendar/Gmail agent):

```python
class WeatherManager:
    """Manages multiple weather data sources"""

    def __init__(self):
        self.openweather_api = OpenWeatherAPI()
        self.weatherapi_com = WeatherAPIcom()
        self.cache = {}

    def get_current_weather(self, location):
        # Try primary API
        try:
            return self.openweather_api.current(location)
        except:
            # Fallback to secondary API
            return self.weatherapi_com.current(location)

    def get_cached_weather(self, location):
        # Implement caching to reduce API calls
        if location in self.cache:
            return self.cache[location]
        result = self.get_current_weather(location)
        self.cache[location] = result
        return result

# Use the manager in your tools
manager = WeatherManager()

weather_tool = Tool(
    name="get_weather",
    description="Get current weather with automatic fallback",
    func=manager.get_current_weather,
    params={"location": "string (required)"}
)
```

#### Debugging Tips

**Enable verbose logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In your agent
response = agent.chat("test query", verbose=True)
```

**Check tool execution:**
```python
# Test tool directly
result = agent.tools["get_current_weather"].func("London")
print(result)
```

**Monitor API calls:**
```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Add retry logic
session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

### Modifying UI

React components are in `agent-sphere-ui/src/components/`

**Key Components:**
- `HomeAutomation.jsx` - Home automation UI
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
python agents/weather_agent.py  # Your custom agent

# Run test suite (if you've created tests)
python -m pytest tests/

# Test specific agent functionality
python -c "from agents.weather_agent import weather_agent; \
           print(weather_agent.chat('What is the weather in London?'))"
```

## 📝 License

Open source - feel free to modify and extend!

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

**Monitor & Optimize:**
9. Track agent performance in Analytics
10. Set up automated testing for quality assurance
11. Monitor usage patterns and optimize
12. Export reports and share insights

**Advanced:**
13. Extend with additional API integrations
14. Create complex conditional workflows
15. Build domain-specific agent suites
16. Contribute templates to the marketplace

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

Enjoy building! 🎉
