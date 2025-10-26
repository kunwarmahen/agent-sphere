import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:5000/api";

export default function AgentBuilder({ activeTab, loading, showNotification }) {
  const [myCustomAgents, setMyCustomAgents] = useState([]);
  const [marketplaceAgents, setMarketplaceAgents] = useState([]);
  const [availableTools, setAvailableTools] = useState({});
  const [selectedTools, setSelectedTools] = useState([]);
  const [customTools, setCustomTools] = useState([]);
  const [publishedTools, setPublishedTools] = useState([]);
  const [selectedCustomTools, setSelectedCustomTools] = useState([]);

  const [newAgentForm, setNewAgentForm] = useState({
    name: "",
    role: "",
    description: "",
    system_instructions: "",
    tools: [],
    tags: [],
  });
  const [showAgentBuilder, setShowAgentBuilder] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch data when component mounts or activeTab changes
  useEffect(() => {
    if (activeTab === "agentMarketplace") {
      fetchMyCustomAgents();
      fetchMarketplaceAgents();
    }
  }, [activeTab]);

  useEffect(() => {
    fetchAvailableTools();
    fetchCustomTools();
  }, []);

  const fetchMyCustomAgents = async () => {
    try {
      const response = await fetch(
        `${API_URL}/agents/custom/my-agents/default_user`
      );
      const data = await response.json();
      setMyCustomAgents(data.agents || []);
    } catch (error) {
      console.error("Error fetching custom agents:", error);
      showNotification("Failed to fetch your agents", "error");
    }
  };

  const fetchMarketplaceAgents = async () => {
    try {
      const response = await fetch(`${API_URL}/agents/marketplace`);
      const data = await response.json();
      setMarketplaceAgents(data.agents || []);
    } catch (error) {
      console.error("Error fetching marketplace:", error);
      showNotification("Failed to fetch marketplace agents", "error");
    }
  };

  const fetchAvailableTools = async () => {
    try {
      const response = await fetch(`${API_URL}/agents/tools/available`);
      const data = await response.json();
      setAvailableTools(data.categories || {});
    } catch (error) {
      console.error("Error fetching tools:", error);
    }
  };

  const fetchCustomTools = async () => {
    try {
      const response = await fetch(`${API_URL}/tools/user/default_user`);
      const data = await response.json();
      const published = (data.tools || []).filter(
        (tool) => tool.status === "published"
      );
      setPublishedTools(published);
    } catch (error) {
      console.error("Error fetching custom tools:", error);
    }
  };

  const toggleCustomTool = (toolId) => {
    if (selectedCustomTools.includes(toolId)) {
      setSelectedCustomTools(selectedCustomTools.filter((t) => t !== toolId));
    } else {
      setSelectedCustomTools([...selectedCustomTools, toolId]);
    }
  };

  const toggleTool = (toolId) => {
    if (selectedTools.includes(toolId)) {
      setSelectedTools(selectedTools.filter((t) => t !== toolId));
    } else {
      setSelectedTools([...selectedTools, toolId]);
    }
  };

  const createCustomAgent = async () => {
    if (!newAgentForm.name.trim() || !newAgentForm.role.trim()) {
      showNotification("Name and Role are required", "error");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/agents/custom`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newAgentForm,
          tools: [
            ...selectedTools, // Built-in tools
            ...selectedCustomTools, // Custom tools
          ],
          created_by: "default_user",
        }),
      });

      const data = await response.json();

      if (response.ok) {
        showNotification(
          `✅ Agent "${newAgentForm.name}" created successfully!`,
          "success"
        );
        setNewAgentForm({
          name: "",
          role: "",
          description: "",
          system_instructions: "",
          tools: [],
          tags: [],
        });
        setSelectedTools([]);
        setSelectedCustomTools([]);
        setShowAgentBuilder(false);
        fetchMyCustomAgents();
      } else {
        showNotification(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      showNotification("Failed to create agent", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const publishAgent = async (agentId) => {
    try {
      const response = await fetch(
        `${API_URL}/agents/custom/${agentId}/publish`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (response.ok) {
        showNotification("✅ Agent published to marketplace!", "success");
        fetchMyCustomAgents();
        fetchMarketplaceAgents();
      } else {
        showNotification(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      showNotification("Failed to publish agent", "error");
    }
  };

  const unpublishAgent = async (agentId) => {
    if (!window.confirm("Unpublish this agent from marketplace?")) return;

    try {
      const response = await fetch(
        `${API_URL}/agents/custom/${agentId}/unpublish`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (response.ok) {
        showNotification("Agent unpublished from marketplace", "success");
        fetchMyCustomAgents();
        fetchMarketplaceAgents();
      } else {
        showNotification(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      showNotification("Failed to unpublish agent", "error");
    }
  };

  const deleteAgent = async (agentId) => {
    if (!window.confirm("Delete this agent?")) return;

    try {
      const response = await fetch(`${API_URL}/agents/custom/${agentId}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (response.ok) {
        showNotification("Agent deleted", "success");
        fetchMyCustomAgents();
      } else {
        showNotification(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      showNotification("Failed to delete agent", "error");
    }
  };

  const installMarketplaceAgent = async (agentId) => {
    try {
      const response = await fetch(
        `${API_URL}/agents/marketplace/${agentId}/install`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: "default_user" }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        showNotification(`✅ Agent installed successfully!`, "success");
        fetchMyCustomAgents();
      } else {
        showNotification(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      showNotification("Failed to install agent", "error");
    }
  };

  if (activeTab !== "agentMarketplace") {
    return null;
  }

  return (
    <section className="section">
      <h2>🛠️ Agent Builder & Marketplace</h2>

      {/* Create Agent Section */}
      <div className="workflow-section">
        <h3>➕ Create New Agent</h3>
        {!showAgentBuilder ? (
          <button
            className="primary-btn"
            onClick={() => setShowAgentBuilder(true)}
          >
            ✨ Create Custom Agent
          </button>
        ) : (
          <div className="form-group">
            <input
              type="text"
              placeholder="Agent Name (e.g., Weather Agent)"
              value={newAgentForm.name}
              onChange={(e) =>
                setNewAgentForm({ ...newAgentForm, name: e.target.value })
              }
            />
            <input
              type="text"
              placeholder="Agent Role (e.g., Weather Information Provider)"
              value={newAgentForm.role}
              onChange={(e) =>
                setNewAgentForm({ ...newAgentForm, role: e.target.value })
              }
            />
            <textarea
              placeholder="Description"
              value={newAgentForm.description}
              onChange={(e) =>
                setNewAgentForm({
                  ...newAgentForm,
                  description: e.target.value,
                })
              }
              style={{ minHeight: "60px", fontFamily: "inherit" }}
            />
            <textarea
              placeholder="System Instructions for the Agent"
              value={newAgentForm.system_instructions}
              onChange={(e) =>
                setNewAgentForm({
                  ...newAgentForm,
                  system_instructions: e.target.value,
                })
              }
              style={{ minHeight: "80px", fontFamily: "inherit" }}
            />

            {/* Tools Selection */}
            <div style={{ marginTop: "1rem" }}>
              <label
                style={{
                  fontWeight: "bold",
                  display: "block",
                  marginBottom: "0.5rem",
                }}
              >
                🔧 Select Tools (Optional)
              </label>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
                  gap: "0.75rem",
                }}
              >
                {Object.entries(availableTools).map(([category, tools]) => (
                  <div key={category} style={{ gridColumn: "1 / -1" }}>
                    <h4
                      style={{
                        color: "#667eea",
                        fontSize: "0.9rem",
                        marginBottom: "0.5rem",
                        textTransform: "capitalize",
                      }}
                    >
                      {category}
                    </h4>
                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "repeat(auto-fill, minmax(150px, 1fr))",
                        gap: "0.5rem",
                      }}
                    >
                      {tools.map((tool) => (
                        <button
                          key={tool.id}
                          type="button"
                          onClick={() => toggleTool(tool.id)}
                          style={{
                            padding: "0.5rem",
                            border: selectedTools.includes(tool.id)
                              ? "2px solid #667eea"
                              : "2px solid #ddd",
                            borderRadius: "8px",
                            background: selectedTools.includes(tool.id)
                              ? "#f0f4ff"
                              : "white",
                            cursor: "pointer",
                            fontSize: "0.85rem",
                            transition: "all 0.3s ease",
                          }}
                          title={tool.description}
                        >
                          <div
                            style={{
                              fontWeight: selectedTools.includes(tool.id)
                                ? "bold"
                                : "normal",
                            }}
                          >
                            {selectedTools.includes(tool.id) ? "✓ " : ""}
                            {tool.name}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            {/* Custom Tools Selection */}
            <div style={{ marginTop: "1.5rem" }}>
              <label
                style={{
                  fontWeight: "bold",
                  display: "block",
                  marginBottom: "0.5rem",
                }}
              >
                🛠️ Custom Tools (Your Published Tools)
              </label>

              {publishedTools.length === 0 ? (
                <div
                  style={{
                    padding: "1rem",
                    background: "#fff3cd",
                    borderRadius: "8px",
                    border: "2px solid #ffc107",
                    color: "#856404",
                  }}
                >
                  <p style={{ margin: "0.5rem 0" }}>
                    📌 No published custom tools available yet.
                  </p>
                  <p style={{ margin: "0.5rem 0", fontSize: "0.9rem" }}>
                    Go to the <strong>Tool Builder</strong> tab to create and
                    publish tools first!
                  </p>
                </div>
              ) : (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns:
                      "repeat(auto-fill, minmax(160px, 1fr))",
                    gap: "0.75rem",
                    marginBottom: "1rem",
                  }}
                >
                  {publishedTools.map((tool) => (
                    <button
                      key={tool.id}
                      type="button"
                      onClick={() => toggleCustomTool(tool.id)}
                      style={{
                        padding: "0.75rem",
                        border: selectedCustomTools.includes(tool.id)
                          ? "2px solid #4caf50"
                          : "2px solid #ddd",
                        borderRadius: "8px",
                        background: selectedCustomTools.includes(tool.id)
                          ? "#e8f5e9"
                          : "white",
                        cursor: "pointer",
                        transition: "all 0.3s ease",
                        textAlign: "left",
                      }}
                      title={tool.description}
                    >
                      <div
                        style={{
                          fontWeight: selectedCustomTools.includes(tool.id)
                            ? "bold"
                            : "normal",
                          fontSize: "0.9rem",
                          marginBottom: "0.25rem",
                        }}
                      >
                        {selectedCustomTools.includes(tool.id) ? "✅ " : "○ "}
                        {tool.name}
                      </div>
                      <div
                        style={{
                          fontSize: "0.7rem",
                          color: "#666",
                          fontWeight: "normal",
                        }}
                      >
                        {tool.integration_type}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Selected Tools Summary */}
              {selectedCustomTools.length > 0 && (
                <div
                  style={{
                    padding: "0.75rem",
                    background: "#d4edda",
                    borderRadius: "8px",
                    border: "2px solid #28a745",
                  }}
                >
                  <strong style={{ color: "#155724" }}>
                    ✅ {selectedCustomTools.length} Custom Tool(s) Selected
                  </strong>
                  <div
                    style={{
                      marginTop: "0.5rem",
                      fontSize: "0.9rem",
                      color: "#155724",
                    }}
                  >
                    {publishedTools
                      .filter((t) => selectedCustomTools.includes(t.id))
                      .map((t) => (
                        <div key={t.id}>
                          • {t.name} ({t.integration_type})
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
            <input
              type="text"
              placeholder="Tags (comma-separated, e.g., weather, forecast, climate)"
              value={newAgentForm.tags.join(", ")}
              onChange={(e) =>
                setNewAgentForm({
                  ...newAgentForm,
                  tags: e.target.value.split(",").map((t) => t.trim()),
                })
              }
            />
            <div style={{ display: "flex", gap: "1rem" }}>
              <button
                className="primary-btn"
                onClick={() => {
                  createCustomAgent();
                }}
                disabled={isLoading}
                style={{ flex: 1 }}
              >
                ✅ Create Agent
              </button>
              <button
                className="secondary-btn"
                onClick={() => {
                  setShowAgentBuilder(false);
                  setSelectedTools([]);
                }}
              >
                ❌ Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* My Custom Agents */}
      <div className="workflow-section">
        <h3>📦 My Custom Agents</h3>
        {myCustomAgents.length === 0 ? (
          <p className="empty-state">No custom agents yet. Create one above!</p>
        ) : (
          <div className="workflows-list">
            {myCustomAgents.map((agent) => (
              <div key={agent.id} className="workflow-item">
                <div className="workflow-info">
                  <h4>{agent.name}</h4>
                  <p>{agent.description}</p>
                  <small>
                    Role: <strong>{agent.role}</strong> | Status:{" "}
                    <strong>{agent.status}</strong>
                  </small>
                  {agent.tags.length > 0 && (
                    <div style={{ marginTop: "0.5rem" }}>
                      {agent.tags.map((tag) => (
                        <span
                          key={tag}
                          style={{
                            display: "inline-block",
                            background: "#667eea",
                            color: "white",
                            padding: "0.25rem 0.5rem",
                            borderRadius: "4px",
                            fontSize: "0.75rem",
                            marginRight: "0.5rem",
                          }}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="workflow-actions">
                  {!agent.published ? (
                    <button
                      onClick={() => publishAgent(agent.id)}
                      className="primary-btn"
                    >
                      📤 Publish
                    </button>
                  ) : (
                    <button
                      onClick={() => unpublishAgent(agent.id)}
                      className="secondary-btn"
                    >
                      📥 Unpublish
                    </button>
                  )}
                  <button
                    onClick={() => deleteAgent(agent.id)}
                    className="secondary-btn"
                    style={{ color: "#f44336", borderColor: "#f44336" }}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Marketplace */}
      <div className="workflow-section">
        <h3>🌐 Agent Marketplace</h3>
        {marketplaceAgents.length === 0 ? (
          <p className="empty-state">No published agents in marketplace yet.</p>
        ) : (
          <div className="workflows-list">
            {marketplaceAgents.map((agent) => (
              <div key={agent.id} className="workflow-item">
                <div className="workflow-info">
                  <h4>{agent.name}</h4>
                  <p>{agent.description}</p>
                  <small>
                    By: <strong>{agent.created_by}</strong> | Rating: ⭐
                    {agent.rating.toFixed(1)}/5 | Downloads: {agent.downloads}
                  </small>
                  {agent.tags.length > 0 && (
                    <div style={{ marginTop: "0.5rem" }}>
                      {agent.tags.map((tag) => (
                        <span
                          key={tag}
                          style={{
                            display: "inline-block",
                            background: "#4caf50",
                            color: "white",
                            padding: "0.25rem 0.5rem",
                            borderRadius: "4px",
                            fontSize: "0.75rem",
                            marginRight: "0.5rem",
                          }}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="workflow-actions">
                  <button
                    onClick={() => installMarketplaceAgent(agent.id)}
                    className="primary-btn"
                  >
                    ⬇️ Install
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
