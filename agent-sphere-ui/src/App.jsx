import React, { useState, useEffect, useRef } from "react";
import io from "socket.io-client";
import "./App.css";

const API_URL = "http://localhost:5000/api";
const SOCKET_URL = "http://localhost:5000";

export default function App() {
  const [activeTab, setActiveTab] = useState("agents");
  const [agents, setAgents] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState("home");
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [homeStatus, setHomeStatus] = useState(null);
  const [financialData, setFinancialData] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState({
    workflow_id: "",
    name: "",
    description: "",
  });

  const socketRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize WebSocket and Voice
  useEffect(() => {
    // WebSocket connection
    socketRef.current = io(SOCKET_URL);

    socketRef.current.on("connect", () => {
      console.log("WebSocket connected");
      showNotification("Connected to server", "success");
    });

    socketRef.current.on("system_update", (data) => {
      handleSystemUpdate(data);
    });

    socketRef.current.on("notification", (notification) => {
      setNotifications((prev) => [...prev, notification]);
      showBrowserNotification(notification);
    });

    // Voice recognition
    if ("webkitSpeechRecognition" in window) {
      recognitionRef.current = new window.webkitSpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setMessage(transcript);
      };
    }

    // Request notification permission
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }

    return () => {
      if (socketRef.current) socketRef.current.disconnect();
    };
  }, []);

  useEffect(() => {
    fetchAgents();
    fetchWorkflows();
    fetchTemplates();
    fetchNotifications();
  }, []);

  useEffect(() => {
    if (activeTab === "home") {
      fetchHomeStatus();
      const interval = setInterval(fetchHomeStatus, 5000);
      return () => clearInterval(interval);
    } else if (activeTab === "finance") {
      fetchFinancialData();
    }
  }, [activeTab]);

  useEffect(() => {
    document.body.classList.toggle("dark-mode", darkMode);
  }, [darkMode]);

  const handleSystemUpdate = (data) => {
    if (data.type === "home_update") {
      fetchHomeStatus();
    } else if (data.type === "finance_update") {
      fetchFinancialData();
    } else if (data.type === "workflow_completed") {
      fetchWorkflows();
      showNotification(
        `Workflow ${data.data.workflow_id} completed`,
        "success"
      );
    }
  };

  const showBrowserNotification = (notification) => {
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(notification.title, {
        body: notification.message,
        icon: "/logo192.png",
      });
    }
  };

  const showNotification = (message, type = "info") => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toISOString(),
    };
    setNotifications((prev) => [...prev, notification]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== notification.id));
    }, 5000);
  };

  const startVoiceInput = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
      setVoiceEnabled(true);
      setTimeout(() => setVoiceEnabled(false), 5000);
    }
  };

  // API Calls
  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_URL}/agents`);
      const data = await response.json();
      setAgents(data.agents);
    } catch (error) {
      console.error("Error fetching agents:", error);
      showNotification("Failed to fetch agents", "error");
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await fetch(`${API_URL}/workflows`);
      const data = await response.json();
      setWorkflows(data.workflows);
    } catch (error) {
      console.error("Error fetching workflows:", error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_URL}/templates`);
      const data = await response.json();
      setTemplates(data.templates);
    } catch (error) {
      console.error("Error fetching templates:", error);
    }
  };

  const fetchNotifications = async () => {
    try {
      const response = await fetch(`${API_URL}/notifications`);
      const data = await response.json();
      setNotifications(data.notifications || []);
    } catch (error) {
      console.error("Error fetching notifications:", error);
    }
  };

  const fetchHomeStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/home/status`);
      const data = await response.json();
      setHomeStatus(data);
    } catch (error) {
      console.error("Error fetching home status:", error);
    }
  };

  const fetchFinancialData = async () => {
    try {
      const response = await fetch(`${API_URL}/finance/summary`);
      const data = await response.json();
      setFinancialData(data);
    } catch (error) {
      console.error("Error fetching financial data:", error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/agents/${selectedAgent}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      const data = await response.json();

      setChatHistory([
        ...chatHistory,
        { type: "user", text: message },
        { type: "assistant", text: data.response },
      ]);
      setMessage("");
      showNotification("Response received", "success");
    } catch (error) {
      console.error("Error sending message:", error);
      showNotification("Failed to send message", "error");
    } finally {
      setLoading(false);
    }
  };

  const toggleLight = async (room) => {
    try {
      await fetch(`${API_URL}/home/light/${room}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state: !homeStatus.lights[room] }),
      });
      fetchHomeStatus();
    } catch (error) {
      console.error("Error toggling light:", error);
    }
  };

  const setTemperature = async (temp) => {
    try {
      await fetch(`${API_URL}/home/thermostat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ temperature: temp }),
      });
      fetchHomeStatus();
      showNotification(`Temperature set to ${temp}°F`, "success");
    } catch (error) {
      console.error("Error setting temperature:", error);
    }
  };

  const createWorkflow = async () => {
    if (!newWorkflow.workflow_id || !newWorkflow.name) {
      showNotification("Please fill in all fields", "error");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/workflows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newWorkflow),
      });

      if (response.ok) {
        setNewWorkflow({ workflow_id: "", name: "", description: "" });
        fetchWorkflows();
        showNotification("Workflow created successfully!", "success");
      }
    } catch (error) {
      console.error("Error creating workflow:", error);
      showNotification("Failed to create workflow", "error");
    }
  };

  const executeWorkflow = async (workflowId) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/workflows/${workflowId}/execute`,
        {
          method: "POST",
        }
      );
      const data = await response.json();
      showNotification(
        `Workflow ${data.success ? "completed" : "failed"}!`,
        data.success ? "success" : "error"
      );
      fetchWorkflows();
    } catch (error) {
      console.error("Error executing workflow:", error);
      showNotification("Failed to execute workflow", "error");
    } finally {
      setLoading(false);
    }
  };

  const createFromTemplate = async (templateId) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/templates/${templateId}/create`,
        {
          method: "POST",
        }
      );
      const data = await response.json();
      showNotification(
        `Workflow '${data.name}' created with ${data.tasks} tasks!`,
        "success"
      );
      fetchWorkflows();
    } catch (error) {
      console.error("Error creating from template:", error);
      showNotification("Failed to create from template", "error");
    } finally {
      setLoading(false);
    }
  };

  const exportWorkflow = async (workflowId) => {
    try {
      const response = await fetch(`${API_URL}/workflows/${workflowId}`);
      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `workflow_${workflowId}.json`;
      a.click();
      showNotification("Workflow exported", "success");
    } catch (error) {
      console.error("Error exporting workflow:", error);
      showNotification("Failed to export workflow", "error");
    }
  };

  return (
    <div className={`app ${darkMode ? "dark" : ""}`}>
      <header className="header">
        <h1>🤖 Multi-Agent AI System</h1>
        <p>Home Automation • Calendar • Finance • Workflows</p>
        <div className="header-controls">
          <button onClick={() => setDarkMode(!darkMode)} className="icon-btn">
            {darkMode ? "☀️" : "🌙"}
          </button>
          <button
            onClick={startVoiceInput}
            className={`icon-btn ${voiceEnabled ? "active" : ""}`}
          >
            🎤
          </button>
        </div>
      </header>

      {notifications.length > 0 && (
        <div className="notifications">
          {notifications.map((notif) => (
            <div key={notif.id} className={`notification ${notif.type}`}>
              {notif.message}
            </div>
          ))}
        </div>
      )}

      <nav className="navigation">
        <button
          className={`nav-btn ${activeTab === "agents" ? "active" : ""}`}
          onClick={() => setActiveTab("agents")}
        >
          💬 Agents
        </button>
        <button
          className={`nav-btn ${activeTab === "home" ? "active" : ""}`}
          onClick={() => setActiveTab("home")}
        >
          🏠 Home
        </button>
        <button
          className={`nav-btn ${activeTab === "finance" ? "active" : ""}`}
          onClick={() => setActiveTab("finance")}
        >
          💰 Finance
        </button>
        <button
          className={`nav-btn ${activeTab === "workflows" ? "active" : ""}`}
          onClick={() => setActiveTab("workflows")}
        >
          ⚙️ Workflows
        </button>
      </nav>

      <main className="content">
        {activeTab === "agents" && (
          <section className="section">
            <h2>AI Agents Chat</h2>

            <div className="agent-selector">
              {agents.map((agent) => (
                <button
                  key={agent.id}
                  className={`agent-btn ${
                    selectedAgent === agent.id ? "active" : ""
                  }`}
                  onClick={() => {
                    setSelectedAgent(agent.id);
                    setChatHistory([]);
                  }}
                >
                  <strong>{agent.name}</strong>
                  <p>{agent.role}</p>
                  <span className={`status ${agent.status}`}>
                    {agent.status}
                  </span>
                </button>
              ))}
            </div>

            <div className="chat-container">
              <div className="chat-history">
                {chatHistory.length === 0 && (
                  <div className="empty-chat">
                    Start a conversation with{" "}
                    {agents.find((a) => a.id === selectedAgent)?.name ||
                      "an agent"}
                  </div>
                )}
                {chatHistory.map((msg, idx) => (
                  <div key={idx} className={`chat-message ${msg.type}`}>
                    <strong>{msg.type === "user" ? "You" : "Agent"}:</strong>
                    <p>{msg.text}</p>
                  </div>
                ))}
                {loading && (
                  <div className="chat-message assistant">
                    <strong>Agent:</strong>
                    <p className="typing">Thinking...</p>
                  </div>
                )}
              </div>

              <form onSubmit={sendMessage} className="chat-form">
                <input
                  type="text"
                  placeholder="Ask me anything..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={startVoiceInput}
                  className="voice-btn"
                >
                  🎤
                </button>
                <button type="submit" disabled={loading}>
                  {loading ? "⏳" : "📤"}
                </button>
              </form>
            </div>
          </section>
        )}

        {activeTab === "home" && (
          <section className="section">
            <h2>🏠 Home Automation</h2>

            {homeStatus && (
              <div className="home-grid">
                <div className="home-card">
                  <h3>💡 Lights</h3>
                  <div className="control-group">
                    {Object.entries(homeStatus.lights).map(([room, status]) => (
                      <button
                        key={room}
                        className={`light-btn ${status ? "on" : "off"}`}
                        onClick={() => toggleLight(room)}
                      >
                        <span className="light-icon">
                          {status ? "💡" : "🔘"}
                        </span>
                        {room.replace("_", " ")}: {status ? "ON" : "OFF"}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="home-card">
                  <h3>🌡️ Thermostat</h3>
                  <p>Current: {homeStatus.thermostat.current_temp}°F</p>
                  <p>Target: {homeStatus.thermostat.target_temp}°F</p>
                  <p>Mode: {homeStatus.thermostat.mode}</p>
                  <div className="temp-controls">
                    {[68, 70, 72, 74, 76].map((temp) => (
                      <button
                        key={temp}
                        className={`temp-btn ${
                          homeStatus.thermostat.target_temp === temp
                            ? "active"
                            : ""
                        }`}
                        onClick={() => setTemperature(temp)}
                      >
                        {temp}°F
                      </button>
                    ))}
                  </div>
                </div>

                <div className="home-card">
                  <h3>🔐 Security</h3>
                  <p>
                    Door:{" "}
                    {homeStatus.security.door_locked
                      ? "🔒 Locked"
                      : "🔓 Unlocked"}
                  </p>
                  <p>
                    Garage:{" "}
                    {homeStatus.security.garage_open ? "🚗 Open" : "✓ Closed"}
                  </p>
                  <p>
                    Motion:{" "}
                    {homeStatus.security.motion_detected
                      ? "⚠️ Detected"
                      : "✓ Clear"}
                  </p>
                </div>

                <div className="home-card">
                  <h3>📺 Devices</h3>
                  <div className="device-list">
                    {Object.entries(homeStatus.devices).map(
                      ([device, status]) => (
                        <div key={device} className="device-item">
                          <span>{device.replace("_", " ")}:</span>
                          <span className={status.on ? "on" : "off"}>
                            {status.on ? "✓ ON" : "✗ OFF"}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        {activeTab === "finance" && (
          <section className="section">
            <h2>💰 Financial Overview</h2>

            {financialData && (
              <>
                <div className="finance-grid">
                  <div className="finance-card highlight">
                    <h3>Net Worth</h3>
                    <p className="big-number">{financialData.net_worth}</p>
                  </div>

                  <div className="finance-card">
                    <h3>Liquid Assets</h3>
                    <p className="big-number">{financialData.liquid_assets}</p>
                  </div>

                  <div className="finance-card">
                    <h3>Investments</h3>
                    <p className="big-number">{financialData.investments}</p>
                  </div>

                  <div className="finance-card">
                    <h3>Monthly Spending</h3>
                    <p className="big-number">
                      {financialData.monthly_spending}
                    </p>
                  </div>

                  <div className="finance-card">
                    <h3>Active Goals</h3>
                    <p className="big-number">{financialData.active_goals}</p>
                  </div>

                  <div className="finance-card">
                    <h3>Recurring Monthly</h3>
                    <p className="big-number">
                      {financialData.recurring_expenses}
                    </p>
                  </div>
                </div>

                <div className="quick-actions">
                  <h3>Quick Actions</h3>
                  <button
                    className="action-btn"
                    onClick={() =>
                      window.open(`${API_URL}/finance/spending`, "_blank")
                    }
                  >
                    📊 Spending Analysis
                  </button>
                  <button
                    className="action-btn"
                    onClick={() =>
                      window.open(`${API_URL}/finance/portfolio`, "_blank")
                    }
                  >
                    💹 Portfolio Details
                  </button>
                  <button
                    className="action-btn"
                    onClick={() =>
                      window.open(`${API_URL}/finance/goals`, "_blank")
                    }
                  >
                    🎯 Financial Goals
                  </button>
                </div>
              </>
            )}
          </section>
        )}

        {activeTab === "workflows" && (
          <section className="section">
            <h2>⚙️ Workflow Management</h2>

            <div className="workflow-section">
              <h3>Create New Workflow</h3>
              <form className="form-group">
                <input
                  type="text"
                  placeholder="Workflow ID (e.g., morning_routine)"
                  value={newWorkflow.workflow_id}
                  onChange={(e) =>
                    setNewWorkflow({
                      ...newWorkflow,
                      workflow_id: e.target.value,
                    })
                  }
                />
                <input
                  type="text"
                  placeholder="Workflow Name"
                  value={newWorkflow.name}
                  onChange={(e) =>
                    setNewWorkflow({ ...newWorkflow, name: e.target.value })
                  }
                />
                <input
                  type="text"
                  placeholder="Description (optional)"
                  value={newWorkflow.description}
                  onChange={(e) =>
                    setNewWorkflow({
                      ...newWorkflow,
                      description: e.target.value,
                    })
                  }
                />
                <button
                  type="button"
                  onClick={createWorkflow}
                  className="primary-btn"
                >
                  Create Workflow
                </button>
              </form>
            </div>

            <div className="workflow-section">
              <h3>Templates Library</h3>
              <div className="templates-grid">
                {templates.map((template) => (
                  <div key={template.id} className="template-card">
                    <h4>{template.name}</h4>
                    <p>{template.description}</p>
                    <small>📋 {template.tasks} tasks</small>
                    <button
                      onClick={() => createFromTemplate(template.id)}
                      disabled={loading}
                      className="secondary-btn"
                    >
                      {loading ? "Creating..." : "Use Template"}
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="workflow-section">
              <h3>Your Workflows</h3>
              {workflows.length === 0 ? (
                <p className="empty-state">
                  No workflows yet. Create one above!
                </p>
              ) : (
                <div className="workflows-list">
                  {workflows.map((workflow) => (
                    <div key={workflow.workflow_id} className="workflow-item">
                      <div className="workflow-info">
                        <h4>{workflow.name}</h4>
                        <p>{workflow.description}</p>
                        <small>
                          Status: <strong>{workflow.status}</strong> | Tasks:{" "}
                          {workflow.completed_tasks}/{workflow.task_count}
                        </small>
                      </div>
                      <div className="workflow-actions">
                        <button
                          onClick={() => executeWorkflow(workflow.workflow_id)}
                          disabled={loading}
                          className="primary-btn"
                        >
                          {loading ? "⏳" : "▶️"} Execute
                        </button>
                        <button
                          onClick={() => exportWorkflow(workflow.workflow_id)}
                          className="secondary-btn"
                        >
                          💾 Export
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>🔗 Connected via WebSocket • Powered by Ollama Qwen2.5:14b</p>
      </footer>
    </div>
  );
}
