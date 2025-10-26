import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:5000/api";

export default function ToolBuilder({ showNotification }) {
  const [myTools, setMyTools] = useState([]);
  const [integrationTypes, setIntegrationTypes] = useState({});
  const [showToolForm, setShowToolForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIntegrationType, setSelectedIntegrationType] =
    useState("http");
  const [newTool, setNewTool] = useState({
    name: "",
    description: "",
    integration_type: "http",
    config: {},
    parameters: {},
  });
  const [testInput, setTestInput] = useState("{}");
  const [testResult, setTestResult] = useState(null);
  const [showGuide, setShowGuide] = useState(null);

  useEffect(() => {
    fetchIntegrationTypes();
    fetchMyTools();
  }, []);

  const fetchIntegrationTypes = async () => {
    try {
      const response = await fetch(`${API_URL}/tools/integration-types`);
      const data = await response.json();
      setIntegrationTypes(data.types || {});
    } catch (error) {
      console.error("Error fetching integration types:", error);
    }
  };

  const handleUseTemplate = (template) => {
    setNewTool(template);
    setShowToolForm(true);
    setShowGuide(null);
    showNotification(
      "✅ Template loaded! Customize and create your tool.",
      "success"
    );
  };

  const fetchMyTools = async () => {
    try {
      const response = await fetch(`${API_URL}/tools/user/default_user`);
      const data = await response.json();
      setMyTools(data.tools || []);
    } catch (error) {
      console.error("Error fetching tools:", error);
    }
  };

  const createTool = async () => {
    if (!newTool.name.trim() || !newTool.description.trim()) {
      showNotification("Name and Description are required", "error");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/tools`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newTool,
          created_by: "default_user",
        }),
      });

      const data = await response.json();

      if (response.ok) {
        showNotification(`✅ Tool "${newTool.name}" created!`, "success");
        setNewTool({
          name: "",
          description: "",
          integration_type: "http",
          config: {},
          parameters: {},
        });
        setShowToolForm(false);
        fetchMyTools();
      } else {
        showNotification(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      showNotification("Failed to create tool", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const testTool = async (toolId) => {
    try {
      let input;
      try {
        input = JSON.parse(testInput);
      } catch {
        showNotification("Invalid JSON in test input", "error");
        return;
      }

      const response = await fetch(`${API_URL}/tools/${toolId}/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input }),
      });

      const data = await response.json();
      setTestResult(data);

      if (data.success) {
        showNotification("✅ Tool test successful!", "success");
      } else {
        showNotification(`Test failed: ${data.error}`, "error");
      }
    } catch (error) {
      showNotification("Failed to test tool", "error");
    }
  };

  const publishTool = async (toolId) => {
    try {
      const response = await fetch(`${API_URL}/tools/${toolId}/publish`, {
        method: "POST",
      });

      const data = await response.json();

      if (response.ok) {
        showNotification("✅ Tool published!", "success");
        fetchMyTools();
      } else {
        showNotification(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      showNotification("Failed to publish tool", "error");
    }
  };

  const deleteTool = async (toolId) => {
    if (!window.confirm("Delete this tool?")) return;

    try {
      const response = await fetch(`${API_URL}/tools/${toolId}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (response.ok) {
        showNotification("Tool deleted", "success");
        fetchMyTools();
      } else {
        showNotification(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      showNotification("Failed to delete tool", "error");
    }
  };

  const renderConfigForm = () => {
    const type = newTool.integration_type;

    switch (type) {
      case "http":
        return (
          <>
            <input
              type="text"
              placeholder="URL (e.g., https://api.example.com/endpoint)"
              value={newTool.config.url || ""}
              onChange={(e) =>
                setNewTool({
                  ...newTool,
                  config: { ...newTool.config, url: e.target.value },
                })
              }
            />
            <select
              value={newTool.config.method || "GET"}
              onChange={(e) =>
                setNewTool({
                  ...newTool,
                  config: { ...newTool.config, method: e.target.value },
                })
              }
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
            </select>
            <textarea
              placeholder="Headers (JSON format, optional)"
              value={JSON.stringify(newTool.config.headers || {}, null, 2)}
              onChange={(e) => {
                try {
                  const headers = JSON.parse(e.target.value);
                  setNewTool({
                    ...newTool,
                    config: { ...newTool.config, headers },
                  });
                } catch {}
              }}
              style={{ minHeight: "80px", fontFamily: "monospace" }}
            />
          </>
        );
      case "mcp":
        return (
          <>
            <input
              type="text"
              placeholder="MCP Server URL (e.g., http://localhost:3000)"
              value={newTool.config.server_url || ""}
              onChange={(e) =>
                setNewTool({
                  ...newTool,
                  config: { ...newTool.config, server_url: e.target.value },
                })
              }
            />
            <input
              type="text"
              placeholder="Method Name (e.g., get_data)"
              value={newTool.config.method || ""}
              onChange={(e) =>
                setNewTool({
                  ...newTool,
                  config: { ...newTool.config, method: e.target.value },
                })
              }
            />
          </>
        );
      case "webhook":
        return (
          <>
            <input
              type="text"
              placeholder="Webhook URL"
              value={newTool.config.webhook_url || ""}
              onChange={(e) =>
                setNewTool({
                  ...newTool,
                  config: { ...newTool.config, webhook_url: e.target.value },
                })
              }
            />
            <textarea
              placeholder="Headers (JSON format, optional)"
              value={JSON.stringify(newTool.config.headers || {}, null, 2)}
              onChange={(e) => {
                try {
                  const headers = JSON.parse(e.target.value);
                  setNewTool({
                    ...newTool,
                    config: { ...newTool.config, headers },
                  });
                } catch {}
              }}
              style={{ minHeight: "80px", fontFamily: "monospace" }}
            />
          </>
        );
      case "custom_code":
        return (
          <>
            <textarea
              placeholder="Python code (use 'input' variable and set 'result' variable)"
              value={newTool.config.code || ""}
              onChange={(e) =>
                setNewTool({
                  ...newTool,
                  config: { ...newTool.config, code: e.target.value },
                })
              }
              style={{ minHeight: "150px", fontFamily: "monospace" }}
            />
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div style={{ padding: "0" }}>
      <h2>🔧 Custom Tool Builder</h2>

      {/* Create Tool Section */}
      <div className="workflow-section">
        <h3>➕ Create New Tool</h3>
        {!showToolForm ? (
          <button className="primary-btn" onClick={() => setShowToolForm(true)}>
            ✨ Create Custom Tool
          </button>
        ) : (
          <div className="form-group">
            <input
              type="text"
              placeholder="Tool Name (e.g., Weather API Tool)"
              value={newTool.name}
              onChange={(e) => setNewTool({ ...newTool, name: e.target.value })}
            />
            <textarea
              placeholder="Tool Description"
              value={newTool.description}
              onChange={(e) =>
                setNewTool({ ...newTool, description: e.target.value })
              }
              style={{ minHeight: "60px" }}
            />

            {/* Integration Type Selection */}
            <label
              style={{
                fontWeight: "bold",
                display: "block",
                marginBottom: "0.5rem",
              }}
            >
              Integration Type
            </label>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
                gap: "0.5rem",
                marginBottom: "1rem",
              }}
            >
              {Object.entries(integrationTypes).map(([type, label]) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => {
                    setNewTool({ ...newTool, integration_type: type });
                    setSelectedIntegrationType(type);
                  }}
                  style={{
                    padding: "0.75rem",
                    border:
                      newTool.integration_type === type
                        ? "2px solid #667eea"
                        : "2px solid #ddd",
                    borderRadius: "8px",
                    background:
                      newTool.integration_type === type ? "#f0f4ff" : "white",
                    cursor: "pointer",
                    fontWeight:
                      newTool.integration_type === type ? "bold" : "normal",
                  }}
                >
                  {type === "http" && "🌐"}
                  {type === "mcp" && "🤝"}
                  {type === "webhook" && "🪝"}
                  {type === "custom_code" && "💻"} {label.split(" ")[0]}
                </button>
              ))}
            </div>

            {/* Integration-Specific Config */}
            <label
              style={{
                fontWeight: "bold",
                display: "block",
                marginBottom: "0.5rem",
              }}
            >
              Configuration
            </label>
            {renderConfigForm()}

            {/* Parameters */}
            <label
              style={{
                fontWeight: "bold",
                display: "block",
                marginBottom: "0.5rem",
                marginTop: "1rem",
              }}
            >
              Parameters (JSON)
            </label>
            <textarea
              placeholder='{"param1": "type1", "param2": "type2"}'
              value={JSON.stringify(newTool.parameters, null, 2)}
              onChange={(e) => {
                try {
                  const params = JSON.parse(e.target.value);
                  setNewTool({ ...newTool, parameters: params });
                } catch {}
              }}
              style={{ minHeight: "80px", fontFamily: "monospace" }}
            />

            <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
              <button
                className="primary-btn"
                onClick={createTool}
                disabled={isLoading}
                style={{ flex: 1 }}
              >
                ✅ Create Tool
              </button>
              <button
                className="secondary-btn"
                onClick={() => setShowToolForm(false)}
              >
                ❌ Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* My Tools */}
      <div className="workflow-section">
        <h3>📦 My Tools</h3>
        {myTools.length === 0 ? (
          <p className="empty-state">No tools created yet. Create one above!</p>
        ) : (
          <div className="workflows-list">
            {myTools.map((tool) => (
              <div key={tool.id} style={{ marginBottom: "1.5rem" }}>
                <div className="workflow-item">
                  <div className="workflow-info">
                    <h4>{tool.name}</h4>
                    <p>{tool.description}</p>
                    <small>
                      Type: <strong>{tool.integration_type}</strong> | Status:{" "}
                      <strong>{tool.status}</strong> | Version: {tool.version}
                    </small>
                  </div>
                  <div className="workflow-actions">
                    {tool.status === "draft" && (
                      <>
                        <button
                          onClick={() => testTool(tool.id)}
                          className="secondary-btn"
                        >
                          🧪 Test
                        </button>
                        <button
                          onClick={() => publishTool(tool.id)}
                          className="primary-btn"
                        >
                          📤 Publish
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => deleteTool(tool.id)}
                      className="secondary-btn"
                      style={{ color: "#f44336", borderColor: "#f44336" }}
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>

                {/* Test Result */}
                {testResult && (
                  <div
                    style={{
                      marginTop: "1rem",
                      padding: "1rem",
                      background: testResult.success ? "#d4edda" : "#f8d7da",
                      borderRadius: "8px",
                      border: `2px solid ${
                        testResult.success ? "#28a745" : "#f44336"
                      }`,
                    }}
                  >
                    <strong
                      style={{
                        color: testResult.success ? "#155724" : "#721c24",
                      }}
                    >
                      {testResult.success ? "✅ Test Passed" : "❌ Test Failed"}
                    </strong>
                    <pre
                      style={{
                        marginTop: "0.5rem",
                        padding: "0.5rem",
                        background: "rgba(0,0,0,0.1)",
                        borderRadius: "4px",
                        fontSize: "0.85rem",
                        overflow: "auto",
                      }}
                    >
                      {JSON.stringify(testResult, null, 2)}
                    </pre>

                    {/* Test Input Form */}
                    <textarea
                      placeholder="Test input (JSON format)"
                      value={testInput}
                      onChange={(e) => setTestInput(e.target.value)}
                      style={{
                        width: "100%",
                        minHeight: "60px",
                        fontFamily: "monospace",
                        fontSize: "0.85rem",
                        marginTop: "0.5rem",
                        padding: "0.5rem",
                      }}
                    />
                  </div>
                )}

                {/* Test Input Form (Initial) */}
                {!testResult && (
                  <div
                    style={{
                      marginTop: "1rem",
                      padding: "1rem",
                      background: "#f8f9ff",
                      borderRadius: "8px",
                      border: "2px solid #e0e0e0",
                    }}
                  >
                    <label
                      style={{
                        fontWeight: "bold",
                        display: "block",
                        marginBottom: "0.5rem",
                      }}
                    >
                      Test Input
                    </label>
                    <textarea
                      placeholder="Test input (JSON format)"
                      value={testInput}
                      onChange={(e) => setTestInput(e.target.value)}
                      style={{
                        width: "100%",
                        minHeight: "80px",
                        fontFamily: "monospace",
                        fontSize: "0.85rem",
                        padding: "0.5rem",
                        border: "1px solid #ddd",
                        borderRadius: "4px",
                      }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Integration Guide */}
      <div className="workflow-section">
        <h3>📖 Integration Guide</h3>
        <p style={{ color: "#666", marginBottom: "1rem" }}>
          Click on any integration type below to see a guide and template
        </p>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1rem",
          }}
        >
          {/* HTTP Guide */}
          <button
            onClick={() => setShowGuide(showGuide === "http" ? null : "http")}
            style={{
              padding: "1rem",
              background: "#e3f2fd",
              borderRadius: "10px",
              border: "2px solid #2196f3",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              cursor: "pointer",
              transition: "all 0.3s ease",
              textAlign: "left",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "none";
              e.currentTarget.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";
            }}
          >
            <h4
              style={{
                color: "#1976d2",
                marginBottom: "0.5rem",
                fontSize: "1rem",
              }}
            >
              🌐 HTTP/REST API
            </h4>
            <p
              style={{
                fontSize: "0.9rem",
                color: "#555",
                lineHeight: "1.5",
                margin: "0",
              }}
            >
              Connect to any HTTP API endpoint
            </p>
          </button>

          {/* MCP Guide */}
          <button
            onClick={() => setShowGuide(showGuide === "mcp" ? null : "mcp")}
            style={{
              padding: "1rem",
              background: "#f3e5f5",
              borderRadius: "10px",
              border: "2px solid #9c27b0",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              cursor: "pointer",
              transition: "all 0.3s ease",
              textAlign: "left",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "none";
              e.currentTarget.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";
            }}
          >
            <h4
              style={{
                color: "#7b1fa2",
                marginBottom: "0.5rem",
                fontSize: "1rem",
              }}
            >
              🤝 MCP Server
            </h4>
            <p
              style={{
                fontSize: "0.9rem",
                color: "#555",
                lineHeight: "1.5",
                margin: "0",
              }}
            >
              Model Context Protocol integrations
            </p>
          </button>

          {/* Webhook Guide */}
          <button
            onClick={() =>
              setShowGuide(showGuide === "webhook" ? null : "webhook")
            }
            style={{
              padding: "1rem",
              background: "#fce4ec",
              borderRadius: "10px",
              border: "2px solid #e91e63",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              cursor: "pointer",
              transition: "all 0.3s ease",
              textAlign: "left",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "none";
              e.currentTarget.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";
            }}
          >
            <h4
              style={{
                color: "#c2185b",
                marginBottom: "0.5rem",
                fontSize: "1rem",
              }}
            >
              🪝 Webhook
            </h4>
            <p
              style={{
                fontSize: "0.9rem",
                color: "#555",
                lineHeight: "1.5",
                margin: "0",
              }}
            >
              Send data to webhook endpoints
            </p>
          </button>

          {/* Custom Code Guide */}
          <button
            onClick={() =>
              setShowGuide(showGuide === "custom_code" ? null : "custom_code")
            }
            style={{
              padding: "1rem",
              background: "#e8f5e9",
              borderRadius: "10px",
              border: "2px solid #4caf50",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              cursor: "pointer",
              transition: "all 0.3s ease",
              textAlign: "left",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "none";
              e.currentTarget.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";
            }}
          >
            <h4
              style={{
                color: "#2e7d32",
                marginBottom: "0.5rem",
                fontSize: "1rem",
              }}
            >
              💻 Custom Code
            </h4>
            <p
              style={{
                fontSize: "0.9rem",
                color: "#555",
                lineHeight: "1.5",
                margin: "0",
              }}
            >
              Write Python code for complex logic
            </p>
          </button>
        </div>

        {/* Guide Details */}
        {showGuide === "http" && (
          <div
            style={{
              marginTop: "1.5rem",
              padding: "1.5rem",
              background: "#e3f2fd",
              borderRadius: "10px",
              border: "2px solid #2196f3",
            }}
          >
            <h4 style={{ color: "#1976d2", marginBottom: "1rem" }}>
              🌐 HTTP/REST API Guide
            </h4>
            <div style={{ color: "#555", lineHeight: "1.8" }}>
              <p>
                <strong>What is it?</strong> Connect to any HTTP REST API
                endpoint (GET, POST, PUT, DELETE)
              </p>
              <p>
                <strong>When to use:</strong>
              </p>
              <ul>
                <li>Weather APIs (OpenWeather, Weather.com)</li>
                <li>Payment processing (Stripe, PayPal)</li>
                <li>Data retrieval (Google Maps, GitHub API)</li>
                <li>Any cloud service with REST API</li>
              </ul>
              <p>
                <strong>Example:</strong> OpenWeather API
              </p>
              <div
                style={{
                  background: "white",
                  padding: "1rem",
                  borderRadius: "8px",
                  marginTop: "0.5rem",
                  fontFamily: "monospace",
                  fontSize: "0.85rem",
                }}
              >
                URL: https://api.openweathermap.org/data/2.5/weather?q=London
                <br />
                Method: GET
                <br />
                Headers: {`{"Authorization": "Bearer YOUR_API_KEY"}`}
              </div>
              <button
                className="primary-btn"
                onClick={() =>
                  handleUseTemplate({
                    name: "Weather API Tool",
                    description: "Get weather information for any city",
                    integration_type: "http",
                    config: {
                      url: "https://api.openweathermap.org/data/2.5/weather",
                      method: "GET",
                      headers: { Authorization: "Bearer YOUR_API_KEY" },
                    },
                    parameters: { city: "string", units: "metric|imperial" },
                  })
                }
                style={{ marginTop: "1rem" }}
              >
                📋 Use This Template
              </button>
            </div>
          </div>
        )}

        {showGuide === "mcp" && (
          <div
            style={{
              marginTop: "1.5rem",
              padding: "1.5rem",
              background: "#f3e5f5",
              borderRadius: "10px",
              border: "2px solid #9c27b0",
            }}
          >
            <h4 style={{ color: "#7b1fa2", marginBottom: "1rem" }}>
              🤝 MCP Server Guide
            </h4>
            <div style={{ color: "#555", lineHeight: "1.8" }}>
              <p>
                <strong>What is it?</strong> Model Context Protocol - AI-native
                communication protocol
              </p>
              <p>
                <strong>When to use:</strong>
              </p>
              <ul>
                <li>Local LLM servers (Ollama, LM Studio)</li>
                <li>Claude API integrations</li>
                <li>Custom MCP server implementations</li>
                <li>Advanced AI reasoning tasks</li>
              </ul>
              <p>
                <strong>Example:</strong> Local Ollama Server
              </p>
              <div
                style={{
                  background: "white",
                  padding: "1rem",
                  borderRadius: "8px",
                  marginTop: "0.5rem",
                  fontFamily: "monospace",
                  fontSize: "0.85rem",
                }}
              >
                Server URL: http://localhost:11434
                <br />
                Method: generate
                <br />
                Params: {`{"prompt": "...", "model": "..."}`}
              </div>
              <button
                className="primary-btn"
                onClick={() =>
                  handleUseTemplate({
                    name: "Ollama Local LLM",
                    description: "Query local Ollama LLM server",
                    integration_type: "mcp",
                    config: {
                      server_url: "http://localhost:11434",
                      method: "generate",
                    },
                    parameters: { prompt: "string", model: "string" },
                  })
                }
                style={{ marginTop: "1rem" }}
              >
                📋 Use This Template
              </button>
            </div>
          </div>
        )}

        {showGuide === "webhook" && (
          <div
            style={{
              marginTop: "1.5rem",
              padding: "1.5rem",
              background: "#fce4ec",
              borderRadius: "10px",
              border: "2px solid #e91e63",
            }}
          >
            <h4 style={{ color: "#c2185b", marginBottom: "1rem" }}>
              🪝 Webhook Guide
            </h4>
            <div style={{ color: "#555", lineHeight: "1.8" }}>
              <p>
                <strong>What is it?</strong> Send data to external endpoints
                (Slack, Discord, Zapier, IFTTT)
              </p>
              <p>
                <strong>When to use:</strong>
              </p>
              <ul>
                <li>Send messages to Slack/Discord</li>
                <li>Trigger Zapier automations</li>
                <li>Log data to external services</li>
                <li>Notify systems about events</li>
              </ul>
              <p>
                <strong>Example:</strong> Slack Webhook
              </p>
              <div
                style={{
                  background: "white",
                  padding: "1rem",
                  borderRadius: "8px",
                  marginTop: "0.5rem",
                  fontFamily: "monospace",
                  fontSize: "0.85rem",
                }}
              >
                Webhook URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
                <br />
                Data: {`{"text": "message", "channel": "#general"}`}
              </div>
              <button
                className="primary-btn"
                onClick={() =>
                  handleUseTemplate({
                    name: "Slack Notification",
                    description: "Send messages to Slack channel",
                    integration_type: "webhook",
                    config: {
                      webhook_url:
                        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                      headers: { "Content-Type": "application/json" },
                    },
                    parameters: { text: "string", channel: "string" },
                  })
                }
                style={{ marginTop: "1rem" }}
              >
                📋 Use This Template
              </button>
            </div>
          </div>
        )}

        {showGuide === "custom_code" && (
          <div
            style={{
              marginTop: "1.5rem",
              padding: "1.5rem",
              background: "#e8f5e9",
              borderRadius: "10px",
              border: "2px solid #4caf50",
            }}
          >
            <h4 style={{ color: "#2e7d32", marginBottom: "1rem" }}>
              💻 Custom Code Guide
            </h4>
            <div style={{ color: "#555", lineHeight: "1.8" }}>
              <p>
                <strong>What is it?</strong> Write Python code to process data
                however you want
              </p>
              <p>
                <strong>When to use:</strong>
              </p>
              <ul>
                <li>Complex data transformations</li>
                <li>Custom calculations</li>
                <li>Conditional logic</li>
                <li>Data validation and formatting</li>
              </ul>
              <p>
                <strong>Example:</strong> Text Transformation
              </p>
              <div
                style={{
                  background: "white",
                  padding: "1rem",
                  borderRadius: "8px",
                  marginTop: "0.5rem",
                  fontFamily: "monospace",
                  fontSize: "0.85rem",
                }}
              >
                text = input.get("text", "")
                <br />
                result = {`{"upper": text.upper(), "length": len(text)}`}
              </div>
              <button
                className="primary-btn"
                onClick={() =>
                  handleUseTemplate({
                    name: "Text Processor",
                    description: "Transform and analyze text",
                    integration_type: "custom_code",
                    config: {
                      code: `# Use 'input' variable, set 'result' variable
text = input.get("text", "")
words = text.split()
result = {
    "original": text,
    "uppercase": text.upper(),
    "lowercase": text.lower(),
    "word_count": len(words),
    "length": len(text)
}`,
                    },
                    parameters: { text: "string" },
                  })
                }
                style={{ marginTop: "1rem" }}
              >
                📋 Use This Template
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
