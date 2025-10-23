# Multi-Agent AI System from Scratch

A complete AI agent framework built without external agent frameworks. Features three specialized agents for home automation, calendar/email management, and financial planning, powered by **Ollama Qwen2.5:14b**.

## 🎯 Overview

This project demonstrates:

- **Core Agent Framework** - Reasoning loop with tool usage
- **Three Specialized Agents** - Home, Calendar, Finance
- **Real-World Scenarios** - Multi-agent coordination
- **No External Frameworks** - Pure Python implementation
- **Local LLM Integration** - Ollama-based reasoning

## 📁 Project Structure

```
agent-sphere-system/
├── agent_framework.py      # Core Agent & Tool classes
├── home_agent.py          # Home automation agent (JARVIS)
├── calendar_agent.py      # Calendar & email agent (Assistant)
├── finance_agent.py       # Financial planning agent (FinanceBot)
├── demo_scenario.py       # Real-world scenario demonstrations
├── main.py               # Interactive CLI entry point
└── README.md            # This file
```

## ⚙️ Installation

### Prerequisites

- Python 3.8+
- Ollama running locally with Qwen2.5:14b model
- requests library

### Step 1: Install Ollama

Download from [ollama.ai](https://ollama.ai)

### Step 2: Pull Qwen Model

```bash
ollama pull qwen2.5:14b
```

### Step 3: Start Ollama Service

```bash
ollama serve
```

Keep this running in the background. It starts a server on `http://localhost:11434`

### Step 4: Install Python Dependencies

```bash
pip install requests
```

## 🚀 Quick Start

### Option 1: Interactive Mode

```bash
python main.py
```

Then select an agent to interact with. Type your requests in natural language!

### Option 2: Run Scenarios

```bash
python demo_scenario.py
```

Shows real-world multi-agent coordination in action.

### Option 3: Test Individual Agents

```bash
# Test home automation
python home_agent.py

# Test calendar & email
python calendar_agent.py

# Test financial planning
python finance_agent.py
```

## 🏠 Home Automation Agent (JARVIS)

**Capabilities:**

- 🔦 Control lights (on/off, brightness, color temperature)
- 🌡️ Manage thermostat (temperature, heating/cooling mode)
- 🔐 Security (lock/unlock doors, garage control)
- 📺 Smart device control (TV, coffee maker, washing machine)
- 📊 Home status reports
- 🎬 Automation scenes

**Example Requests:**

```
"Turn on the living room lights with 80% brightness"
"Set thermostat to 72 degrees in cooling mode"
"Lock the door and close the garage"
"Turn on coffee maker and TV"
"Show me the current home status"
```

## 📅 Calendar & Email Agent (Assistant)

**Capabilities:**

- 📧 Read and manage emails
- 📨 Send emails with CC/BCC
- 📅 View calendar events
- 🗓️ Schedule new events
- ⏰ Reschedule existing events
- 🔍 Find free time slots
- 📝 Reply to emails

**Example Requests:**

```
"Show me my unread emails"
"What's on my calendar for the next 3 days?"
"When am I free for a 1-hour meeting?"
"Schedule a team meeting tomorrow at 2 PM"
"Send an email to alice@company.com about the project update"
```

## 💰 Financial Planning Agent (FinanceBot)

**Capabilities:**

- 💳 Account balance tracking
- 💸 Transaction recording
- 📊 Spending analysis by category
- 📈 Investment portfolio management
- 🎯 Financial goals tracking
- 💡 Savings projections
- 💳 Budget monitoring

**Example Requests:**

```
"What's my financial summary?"
"Show me my spending analysis for the last month"
"How are my investments performing?"
"Add $500 to my vacation fund"
"If I save $600/month, where will I be in 2 years?"
```

## 🔄 Agent Architecture

### Tool Class

```python
tool = Tool(
    name="toggle_light",
    description="Turn lights on/off",
    func=toggle_light_function,
    params={"room": "str", "state": "bool"}
)
```

### Agent Loop

1. **Receive** - Get user request
2. **Think** - Call LLM with system prompt and tools
3. **Decide** - Parse LLM response for tool calls
4. **Act** - Execute selected tool
5. **Reflect** - Add results to memory, continue or finish

### Real Ollama Integration

```python
# The system automatically calls your local Ollama instance
response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen2.5:14b",
        "messages": messages,
        "stream": False
    }
)
```

## 📚 Real-World Scenarios

### Scenario 1: Morning Routine

Agent coordinates home automation and calendar to get you ready for the day.

### Scenario 2: Financial Planning

Month-end financial review with spending analysis and goal progress.

### Scenario 3: Busy Day Management

Complex multi-task coordination across all three agents.

### Scenario 4: Emergency Response

High-paced scenario requiring rapid multi-agent coordination.

## 🛠️ Extending the System

### Add a New Tool

```python
def my_custom_function(param1: str, param2: int) -> str:
    return f"Result: {param1} with {param2}"

new_tool = Tool(
    name="my_tool",
    description="Does something custom",
    func=my_custom_function,
    params={"param1": "str", "param2": "int"}
)

agent.tools["my_tool"] = new_tool
```

### Create a New Agent

```python
from agent_framework import Agent, Tool

# Create tools
my_tools = [tool1, tool2, tool3]

# Create agent
my_agent = Agent(
    name="MyAgent",
    role="Specific Role",
    tools=my_tools,
    system_instructions="Custom instructions..."
)

# Use it
response = my_agent.think_and_act("Your request here")
```

### Integration with Real APIs

Replace the `_call_ollama` method in `agent_framework.py`:

```python
def _call_ollama(self, messages: List[Dict]) -> str:
    # Use OpenAI, Claude, or any other LLM API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content
```

## 🔍 How Reasoning Works

1. **System Prompt** - Agent gets its role, available tools, and instructions
2. **Memory** - Conversation history maintains context
3. **LLM Reasoning** - Qwen2.5:14b decides which tool to use
4. **Tool Parsing** - System extracts action and parameters
5. **Execution** - Tool is executed with given parameters
6. **Feedback Loop** - Result added to memory for next iteration

## ⚡ Performance Tips

- **Model Size**: Qwen2.5:14b is fast enough for real-time use
- **Timeout**: 120 seconds for complex reasoning
- **Memory**: Agents maintain full conversation history
- **Parallel**: Multiple agents can run simultaneously

## 🐛 Troubleshooting

### "Cannot connect to Ollama"

- Make sure `ollama serve` is running
- Check that Qwen model is downloaded: `ollama list`
- Verify localhost:11434 is accessible

### Agent gives wrong responses

- Increase iterations: `agent.max_iterations = 15`
- Add more specific system instructions
- Check tool definitions are clear

### Slow responses

- Qwen2.5:14b needs 8GB+ VRAM
- Reduce `max_iterations`
- Use smaller model if needed

## 📖 Example Usage

```python
from home_agent import home_agent

# Single query
response = home_agent.think_and_act("Turn on living room lights")
print(response)

# Multi-turn conversation
home_agent.think_and_act("What's my home status?")
home_agent.think_and_act("Set temperature to 75")
home_agent.think_and_act("Lock the door")

# Clear memory for fresh conversation
home_agent.clear_memory()
```

## 🎓 Learning Outcomes

This project teaches:

- AI agent architecture and design patterns
- Tool calling and function execution
- LLM integration and prompt engineering
- State management in agents
- Multi-agent coordination
- Error handling and recovery

## 📝 License

Open source - feel free to modify and extend!

## 🤝 Contributing

Ideas for extensions:

- Add weather API integration
- Implement persistent database storage
- Create web UI dashboard
- Add voice input/output
- Build mobile app
- Implement agent-to-agent communication

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Verify Ollama is running
3. Review agent tool definitions
4. Check system memory and resources

## 🚀 Next Steps

1. **Customize** - Add your own tools and agents
2. **Integrate** - Connect to real APIs (Gmail, Google Calendar, banking APIs)
3. **Deploy** - Create web interface with Flask/FastAPI
4. **Monitor** - Add logging and performance metrics
5. **Scale** - Run multiple agents in parallel

Enjoy building! 🎉
