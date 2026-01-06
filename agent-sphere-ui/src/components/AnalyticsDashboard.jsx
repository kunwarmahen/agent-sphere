import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:5000/api";

export default function AnalyticsDashboard({ showNotification, theme = 'matrix' }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [allAgentStats, setAllAgentStats] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentDetails, setAgentDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState("all");

  useEffect(() => {
    fetchDashboardData();
    fetchAllAgentStats();
  }, []);

  useEffect(() => {
    if (selectedAgent) {
      fetchAgentDetails(selectedAgent);
    }
  }, [selectedAgent]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_URL}/analytics/dashboard`);
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      showNotification?.("Failed to fetch analytics dashboard", "error");
    }
  };

  const fetchAllAgentStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/analytics/agents`);
      const data = await response.json();
      setAllAgentStats(data.agents || []);
    } catch (error) {
      console.error("Error fetching agent stats:", error);
      showNotification?.("Failed to fetch agent statistics", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchAgentDetails = async (agentId) => {
    try {
      const response = await fetch(`${API_URL}/analytics/agents/${agentId}`);
      const data = await response.json();
      setAgentDetails(data);
    } catch (error) {
      console.error("Error fetching agent details:", error);
      showNotification?.("Failed to fetch agent details", "error");
    }
  };

  const getHealthColor = (successRate) => {
    if (successRate >= 95) return "#4caf50";
    if (successRate >= 85) return "#ff9800";
    return "#f44336";
  };

  const getHealthLabel = (successRate) => {
    if (successRate >= 95) return "Excellent";
    if (successRate >= 85) return "Good";
    if (successRate >= 70) return "Fair";
    return "Poor";
  };

  // Theme colors
  const accentColor = theme === 'classic' ? '#667eea' : theme === 'cyber' ? '#00d9ff' : '#00ff41';
  const cardBg = theme === 'classic' ? 'white' : 'rgba(0, 0, 0, 0.4)';
  const cardBorder = theme === 'classic' ? '#e0e0e0' : theme === 'cyber' ? 'rgba(0, 217, 255, 0.3)' : 'rgba(0, 255, 65, 0.3)';
  const lightBg = theme === 'classic' ? '#f8f9ff' : 'rgba(0, 255, 65, 0.05)';
  const textColor = theme === 'classic' ? '#333' : 'rgba(255, 255, 255, 0.9)';
  const mutedColor = theme === 'classic' ? '#666' : 'rgba(255, 255, 255, 0.6)';

  return (
    <div style={{ padding: "2rem" }}>
      <h2 style={{ marginBottom: "2rem" }}>📊 Analytics Dashboard</h2>

      {/* Overall Summary */}
      {dashboardData && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1.5rem",
            marginBottom: "2rem",
          }}
        >
          <div
            style={{
              background: theme === 'classic' ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : `linear-gradient(135deg, ${accentColor}22 0%, ${accentColor}11 100%)`,
              padding: "1.5rem",
              borderRadius: "12px",
              color: theme === 'classic' ? "white" : accentColor,
              boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
              border: theme === 'classic' ? 'none' : `1px solid ${cardBorder}`,
            }}
          >
            <div style={{ fontSize: "2rem", fontWeight: "bold" }}>
              {dashboardData.total_agents}
            </div>
            <div style={{ opacity: 0.9, marginTop: "0.5rem" }}>
              Total Agents
            </div>
          </div>

          <div
            style={{
              background: theme === 'classic' ? "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)" : `linear-gradient(135deg, ${accentColor}22 0%, ${accentColor}11 100%)`,
              padding: "1.5rem",
              borderRadius: "12px",
              color: theme === 'classic' ? "white" : accentColor,
              boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
              border: theme === 'classic' ? 'none' : `1px solid ${cardBorder}`,
            }}
          >
            <div style={{ fontSize: "2rem", fontWeight: "bold" }}>
              {dashboardData.total_executions.toLocaleString()}
            </div>
            <div style={{ opacity: 0.9, marginTop: "0.5rem" }}>
              Total Executions
            </div>
          </div>

          <div
            style={{
              background: theme === 'classic' ? "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)" : `linear-gradient(135deg, ${accentColor}22 0%, ${accentColor}11 100%)`,
              padding: "1.5rem",
              borderRadius: "12px",
              color: theme === 'classic' ? "white" : accentColor,
              boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
              border: theme === 'classic' ? 'none' : `1px solid ${cardBorder}`,
            }}
          >
            <div style={{ fontSize: "2rem", fontWeight: "bold" }}>
              {dashboardData.avg_success_rate.toFixed(1)}%
            </div>
            <div style={{ opacity: 0.9, marginTop: "0.5rem" }}>
              Avg Success Rate
            </div>
          </div>
        </div>
      )}

      {/* Agent List */}
      <div
        style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "2rem" }}
      >
        {/* Left: Agent List */}
        <div>
          <h3 style={{ marginBottom: "1rem" }}>All Agents</h3>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.75rem",
                maxHeight: "600px",
                overflowY: "auto",
              }}
            >
              {allAgentStats.map((agent) => (
                <div
                  key={agent.agent_id}
                  onClick={() => setSelectedAgent(agent.agent_id)}
                  style={{
                    padding: "1rem",
                    background:
                      selectedAgent === agent.agent_id
                        ? (theme === 'classic' ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : accentColor)
                        : cardBg,
                    border: `2px solid ${selectedAgent === agent.agent_id ? accentColor : cardBorder}`,
                    borderRadius: "10px",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                    color: selectedAgent === agent.agent_id ? (theme === 'classic' ? "white" : "#0d0208") : textColor,
                  }}
                  onMouseEnter={(e) => {
                    if (selectedAgent !== agent.agent_id) {
                      e.currentTarget.style.borderColor = accentColor;
                      e.currentTarget.style.transform = "translateY(-2px)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedAgent !== agent.agent_id) {
                      e.currentTarget.style.borderColor = cardBorder;
                      e.currentTarget.style.transform = "none";
                    }
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "0.5rem",
                    }}
                  >
                    <strong style={{ fontSize: "0.95rem" }}>
                      {agent.agent_id}
                    </strong>
                    <span
                      style={{
                        padding: "0.2rem 0.5rem",
                        borderRadius: "12px",
                        fontSize: "0.75rem",
                        background:
                          selectedAgent === agent.agent_id
                            ? "rgba(255,255,255,0.3)"
                            : getHealthColor(agent.success_rate),
                        color: "white",
                        fontWeight: "bold",
                      }}
                    >
                      {agent.success_rate.toFixed(0)}%
                    </span>
                  </div>
                  <div
                    style={{
                      fontSize: "0.85rem",
                      opacity: 0.8,
                      display: "flex",
                      justifyContent: "space-between",
                    }}
                  >
                    <span>📊 {agent.total_executions} runs</span>
                    <span>⚡ {agent.avg_response_time_ms}ms</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Agent Details */}
        <div>
          <h3 style={{ marginBottom: "1rem" }}>
            {selectedAgent ? "Agent Details" : "Select an agent"}
          </h3>
          {agentDetails ? (
            <div
              style={{
                background: cardBg,
                border: `2px solid ${cardBorder}`,
                borderRadius: "10px",
                padding: "1.5rem",
              }}
            >
              {/* Health Score */}
              <div
                style={{
                  padding: "1.5rem",
                  background: `linear-gradient(135deg, ${getHealthColor(
                    agentDetails.success_rate
                  )} 0%, ${getHealthColor(agentDetails.success_rate)}dd 100%)`,
                  borderRadius: "10px",
                  color: "white",
                  marginBottom: "1.5rem",
                }}
              >
                <div style={{ fontSize: "1.2rem", fontWeight: "bold" }}>
                  Health: {getHealthLabel(agentDetails.success_rate)}
                </div>
                <div
                  style={{
                    fontSize: "2.5rem",
                    fontWeight: "bold",
                    marginTop: "0.5rem",
                  }}
                >
                  {agentDetails.success_rate.toFixed(1)}%
                </div>
                <div style={{ opacity: 0.9, marginTop: "0.5rem" }}>
                  Success Rate
                </div>
              </div>

              {/* Metrics Grid */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gap: "1rem",
                  marginBottom: "1.5rem",
                }}
              >
                <div
                  style={{
                    padding: "1rem",
                    background: lightBg,
                    borderRadius: "8px",
                    border: `2px solid ${cardBorder}`,
                  }}
                >
                  <div style={{ color: mutedColor, fontSize: "0.85rem" }}>
                    Total Runs
                  </div>
                  <div
                    style={{
                      fontSize: "1.8rem",
                      fontWeight: "bold",
                      color: accentColor,
                    }}
                  >
                    {agentDetails.total_executions}
                  </div>
                </div>

                <div
                  style={{
                    padding: "1rem",
                    background: lightBg,
                    borderRadius: "8px",
                    border: `2px solid ${cardBorder}`,
                  }}
                >
                  <div style={{ color: mutedColor, fontSize: "0.85rem" }}>
                    Avg Response
                  </div>
                  <div
                    style={{
                      fontSize: "1.8rem",
                      fontWeight: "bold",
                      color: accentColor,
                    }}
                  >
                    {agentDetails.avg_response_time_ms}ms
                  </div>
                </div>

                <div
                  style={{
                    padding: "1rem",
                    background: theme === 'classic' ? "#fff3e0" : lightBg,
                    borderRadius: "8px",
                    border: theme === 'classic' ? "2px solid #ffe0b2" : `2px solid ${cardBorder}`,
                  }}
                >
                  <div style={{ color: mutedColor, fontSize: "0.85rem" }}>
                    Total Errors
                  </div>
                  <div
                    style={{
                      fontSize: "1.8rem",
                      fontWeight: "bold",
                      color: theme === 'classic' ? "#ff9800" : accentColor,
                    }}
                  >
                    {agentDetails.total_errors}
                  </div>
                </div>

                <div
                  style={{
                    padding: "1rem",
                    background: lightBg,
                    borderRadius: "8px",
                    border: `2px solid ${cardBorder}`,
                  }}
                >
                  <div style={{ color: mutedColor, fontSize: "0.85rem" }}>
                    Tools Used
                  </div>
                  <div
                    style={{
                      fontSize: "1.8rem",
                      fontWeight: "bold",
                      color: accentColor,
                    }}
                  >
                    {agentDetails.most_used_tools.length}
                  </div>
                </div>
              </div>

              {/* Most Used Tools */}
              {agentDetails.most_used_tools.length > 0 && (
                <div style={{ marginBottom: "1.5rem" }}>
                  <h4 style={{ marginBottom: "0.75rem" }}>
                    🔧 Most Used Tools
                  </h4>
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.5rem",
                    }}
                  >
                    {agentDetails.most_used_tools.map((tool, index) => (
                      <div
                        key={index}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: "0.75rem",
                          background: lightBg,
                          borderRadius: "6px",
                          border: `1px solid ${cardBorder}`,
                        }}
                      >
                        <span style={{ fontWeight: "500", color: textColor }}>{tool.tool}</span>
                        <span
                          style={{
                            background: accentColor,
                            color: theme === 'classic' ? "white" : "#0d0208",
                            padding: "0.25rem 0.75rem",
                            borderRadius: "12px",
                            fontSize: "0.85rem",
                            fontWeight: "bold",
                          }}
                        >
                          {tool.count} uses
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Executions by Day */}
              {Object.keys(agentDetails.executions_by_day).length > 0 && (
                <div style={{ marginBottom: "1.5rem" }}>
                  <h4 style={{ marginBottom: "0.75rem" }}>
                    📈 Recent Activity
                  </h4>
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.5rem",
                    }}
                  >
                    {Object.entries(agentDetails.executions_by_day)
                      .slice(-7)
                      .reverse()
                      .map(([date, count]) => (
                        <div
                          key={date}
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            padding: "0.5rem",
                            background: lightBg,
                            borderRadius: "6px",
                          }}
                        >
                          <span style={{ fontSize: "0.9rem", color: textColor }}>{date}</span>
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "0.5rem",
                            }}
                          >
                            <div
                              style={{
                                width: `${Math.min(count * 3, 150)}px`,
                                height: "8px",
                                background: accentColor,
                                borderRadius: "4px",
                              }}
                            />
                            <span
                              style={{ fontWeight: "bold", minWidth: "30px", color: textColor }}
                            >
                              {count}
                            </span>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Recent Errors */}
              {agentDetails.recent_errors.length > 0 && (
                <div>
                  <h4 style={{ marginBottom: "0.75rem", color: "#f44336" }}>
                    ⚠️ Recent Errors
                  </h4>
                  <div
                    style={{
                      maxHeight: "200px",
                      overflowY: "auto",
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.5rem",
                    }}
                  >
                    {agentDetails.recent_errors.map((error, index) => (
                      <div
                        key={index}
                        style={{
                          padding: "0.75rem",
                          background: theme === 'classic' ? "#ffebee" : "rgba(255, 0, 0, 0.1)",
                          border: theme === 'classic' ? "1px solid #ffcdd2" : "1px solid rgba(255, 0, 0, 0.3)",
                          borderRadius: "6px",
                        }}
                      >
                        <div
                          style={{
                            fontSize: "0.75rem",
                            color: mutedColor,
                            marginBottom: "0.25rem",
                          }}
                        >
                          {new Date(error.time).toLocaleString()}
                        </div>
                        <div style={{ fontSize: "0.9rem", color: theme === 'classic' ? "#c62828" : "#ff6b6b" }}>
                          {error.error}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div
              style={{
                background: lightBg,
                border: `2px dashed ${accentColor}`,
                borderRadius: "10px",
                padding: "3rem",
                textAlign: "center",
                color: mutedColor,
              }}
            >
              <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📊</div>
              <div style={{ fontSize: "1.1rem" }}>
                Select an agent to view detailed analytics
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
