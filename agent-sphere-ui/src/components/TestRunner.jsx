import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:5000/api";

export default function TestRunner({ showNotification, theme = 'matrix' }) {
  const [myAgents, setMyAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [testSuite, setTestSuite] = useState(null);
  const [testResults, setTestResults] = useState(null);
  const [testHistory, setTestHistory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  // Theme colors
  const accentColor = theme === 'classic' ? '#667eea' : theme === 'cyber' ? '#00d9ff' : '#00ff41';
  const cardBg = theme === 'classic' ? 'white' : 'rgba(0, 0, 0, 0.4)';
  const cardBorder = theme === 'classic' ? '#e0e0e0' : theme === 'cyber' ? 'rgba(0, 217, 255, 0.3)' : 'rgba(0, 255, 65, 0.3)';
  const lightBg = theme === 'classic' ? '#f8f9ff' : 'rgba(0, 255, 65, 0.05)';
  const textColor = theme === 'classic' ? '#333' : 'rgba(255, 255, 255, 0.9)';
  const mutedColor = theme === 'classic' ? '#666' : 'rgba(255, 255, 255, 0.6)';

  // Quick test form
  const [quickTestInput, setQuickTestInput] = useState("");
  const [quickTestExpected, setQuickTestExpected] = useState("");

  // New test form
  const [showNewTestForm, setShowNewTestForm] = useState(false);
  const [newTest, setNewTest] = useState({
    name: "",
    input: "",
    expected_contains: "",
  });

  useEffect(() => {
    fetchMyAgents();
  }, []);

  useEffect(() => {
    if (selectedAgent) {
      fetchTestSuite(selectedAgent);
      fetchTestHistory(selectedAgent);
    }
  }, [selectedAgent]);

  const fetchMyAgents = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${API_URL}/agents/custom/my-agents/default_user`
      );
      const data = await response.json();
      setMyAgents(data.agents || []);
    } catch (error) {
      console.error("Error fetching agents:", error);
      showNotification?.("Failed to fetch agents", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchTestSuite = async (agentId) => {
    try {
      const response = await fetch(
        `${API_URL}/testing/agents/${agentId}/suite`
      );
      if (response.ok) {
        const data = await response.json();
        setTestSuite(data);
      } else {
        setTestSuite(null);
      }
    } catch (error) {
      console.error("Error fetching test suite:", error);
    }
  };

  const fetchTestHistory = async (agentId) => {
    try {
      const response = await fetch(
        `${API_URL}/testing/agents/${agentId}/history`
      );
      const data = await response.json();
      setTestHistory(data);
    } catch (error) {
      console.error("Error fetching test history:", error);
    }
  };

  const createTestSuite = async () => {
    if (!selectedAgent) return;

    try {
      const agentName =
        myAgents.find((a) => a.id === selectedAgent)?.name || "Agent";

      const response = await fetch(
        `${API_URL}/testing/agents/${selectedAgent}/suite`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            agent_name: agentName,
            tests: [],
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTestSuite(data.suite);
        showNotification?.("Test suite created!", "success");
      }
    } catch (error) {
      console.error("Error creating test suite:", error);
      showNotification?.("Failed to create test suite", "error");
    }
  };

  const addTestToSuite = async () => {
    if (!newTest.name || !newTest.input) {
      showNotification?.("Please fill in test name and input", "error");
      return;
    }

    try {
      const agentName =
        myAgents.find((a) => a.id === selectedAgent)?.name || "Agent";

      const tests = testSuite?.tests || [];
      tests.push(newTest);

      const response = await fetch(
        `${API_URL}/testing/agents/${selectedAgent}/suite`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            agent_name: agentName,
            tests: tests,
          }),
        }
      );

      if (response.ok) {
        showNotification?.("Test added to suite!", "success");
        fetchTestSuite(selectedAgent);
        setNewTest({ name: "", input: "", expected_contains: "" });
        setShowNewTestForm(false);
      }
    } catch (error) {
      console.error("Error adding test:", error);
      showNotification?.("Failed to add test", "error");
    }
  };

  const runTests = async () => {
    if (!selectedAgent) return;

    setRunning(true);
    showNotification?.("Running tests...", "info");

    try {
      const response = await fetch(
        `${API_URL}/testing/agents/${selectedAgent}/run`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ agent_type: "custom" }),
        }
      );

      const data = await response.json();
      setTestResults(data);

      if (data.success) {
        if (data.pass_rate === 100) {
          showNotification?.(
            `✅ All tests passed! (${data.passed}/${data.total_tests})`,
            "success"
          );
        } else {
          showNotification?.(
            `Tests completed: ${data.passed}/${data.total_tests} passed`,
            "warning"
          );
        }
      }

      fetchTestHistory(selectedAgent);
    } catch (error) {
      console.error("Error running tests:", error);
      showNotification?.("Failed to run tests", "error");
    } finally {
      setRunning(false);
    }
  };

  const runQuickTest = async () => {
    if (!quickTestInput) {
      showNotification?.("Please enter test input", "error");
      return;
    }

    setRunning(true);
    try {
      const response = await fetch(
        `${API_URL}/testing/agents/${selectedAgent}/quick-test`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            input: quickTestInput,
            expected_contains: quickTestExpected || undefined,
            agent_type: "custom",
          }),
        }
      );

      const data = await response.json();

      if (data.passed) {
        showNotification?.("✅ Quick test passed!", "success");
      } else {
        showNotification?.(
          `❌ Quick test failed: ${data.error_message || "Check output"}`,
          "error"
        );
      }

      // Show results in a mini modal (you can enhance this)
      alert(
        `Test Result:\nPassed: ${data.passed}\nResponse Time: ${data.response_time_ms}ms\n\nActual Output:\n${data.actual_output}`
      );
    } catch (error) {
      console.error("Error running quick test:", error);
      showNotification?.("Failed to run quick test", "error");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2 style={{ marginBottom: "2rem" }}>🧪 Testing & Validation</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "300px 1fr",
          gap: "2rem",
        }}
      >
        {/* Left: Agent List */}
        <div>
          <h3 style={{ marginBottom: "1rem" }}>Select Agent</h3>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.5rem",
              }}
            >
              {myAgents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent.id)}
                  style={{
                    padding: "0.75rem",
                    background:
                      selectedAgent === agent.id
                        ? (theme === 'classic' ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : accentColor)
                        : cardBg,
                    border: `2px solid ${selectedAgent === agent.id ? accentColor : cardBorder}`,
                    borderRadius: "8px",
                    cursor: "pointer",
                    textAlign: "left",
                    color: selectedAgent === agent.id ? (theme === 'classic' ? "white" : "#0d0208") : textColor,
                    fontWeight: selectedAgent === agent.id ? "bold" : "normal",
                    transition: "all 0.3s ease",
                  }}
                >
                  <div>{agent.name}</div>
                  <div style={{ fontSize: "0.8rem", opacity: 0.8 }}>
                    {agent.role}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right: Testing Interface */}
        <div>
          {selectedAgent ? (
            <div>
              {/* Quick Test Section */}
              <div
                style={{
                  background: lightBg,
                  border: `2px solid ${cardBorder}`,
                  borderRadius: "10px",
                  padding: "1.5rem",
                  marginBottom: "2rem",
                }}
              >
                <h3 style={{ marginTop: 0, marginBottom: "1rem" }}>
                  ⚡ Quick Test
                </h3>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.75rem",
                  }}
                >
                  <input
                    type="text"
                    placeholder="Test input (e.g., 'convert hello to uppercase')"
                    value={quickTestInput}
                    onChange={(e) => setQuickTestInput(e.target.value)}
                    style={{
                      padding: "0.75rem",
                      border: "2px solid #ddd",
                      borderRadius: "6px",
                      fontSize: "0.95rem",
                    }}
                  />
                  <input
                    type="text"
                    placeholder="Expected text (optional)"
                    value={quickTestExpected}
                    onChange={(e) => setQuickTestExpected(e.target.value)}
                    style={{
                      padding: "0.75rem",
                      border: "2px solid #ddd",
                      borderRadius: "6px",
                      fontSize: "0.95rem",
                    }}
                  />
                  <button
                    onClick={runQuickTest}
                    disabled={running || !quickTestInput}
                    className="primary-btn"
                    style={{ width: "100%" }}
                  >
                    {running ? "⏳ Testing..." : "▶️ Run Quick Test"}
                  </button>
                </div>
              </div>

              {/* Test Suite Section */}
              <div
                style={{
                  background: cardBg,
                  border: `2px solid ${cardBorder}`,
                  borderRadius: "10px",
                  padding: "1.5rem",
                  marginBottom: "2rem",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "1rem",
                  }}
                >
                  <h3 style={{ margin: 0 }}>📋 Test Suite</h3>
                  {testSuite && (
                    <button
                      onClick={runTests}
                      disabled={running || !testSuite?.tests?.length}
                      className="primary-btn"
                    >
                      {running ? "⏳ Running..." : "▶️ Run All Tests"}
                    </button>
                  )}
                </div>

                {!testSuite ? (
                  <div style={{ textAlign: "center", padding: "2rem" }}>
                    <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>
                      📝
                    </div>
                    <p style={{ color: mutedColor, marginBottom: "1rem" }}>
                      No test suite found for this agent
                    </p>
                    <button onClick={createTestSuite} className="primary-btn">
                      Create Test Suite
                    </button>
                  </div>
                ) : (
                  <div>
                    <div style={{ marginBottom: "1rem", color: "#666" }}>
                      {testSuite.test_count} test(s) in suite
                    </div>

                    {/* Test List */}
                    {testSuite.tests && testSuite.tests.length > 0 && (
                      <div
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.75rem",
                          marginBottom: "1rem",
                        }}
                      >
                        {testSuite.tests.map((test, index) => (
                          <div
                            key={index}
                            style={{
                              padding: "1rem",
                              background: lightBg,
                              border: `2px solid ${cardBorder}`,
                              borderRadius: "8px",
                            }}
                          >
                            <div
                              style={{
                                fontWeight: "bold",
                                marginBottom: "0.5rem",
                              }}
                            >
                              {test.name}
                            </div>
                            <div
                              style={{
                                fontSize: "0.9rem",
                                color: mutedColor,
                                marginBottom: "0.25rem",
                              }}
                            >
                              Input: {test.input_message}
                            </div>
                            {test.expected_output && (
                              <div
                                style={{ fontSize: "0.9rem", color: "#666" }}
                              >
                                Expected: {test.expected_output}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Add Test Button */}
                    {!showNewTestForm ? (
                      <button
                        onClick={() => setShowNewTestForm(true)}
                        className="secondary-btn"
                        style={{ width: "100%" }}
                      >
                        ➕ Add Test Case
                      </button>
                    ) : (
                      <div
                        style={{
                          padding: "1rem",
                          background: lightBg,
                          border: "2px solid #667eea",
                          borderRadius: "8px",
                        }}
                      >
                        <h4 style={{ marginTop: 0 }}>New Test Case</h4>
                        <div
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "0.75rem",
                          }}
                        >
                          <input
                            type="text"
                            placeholder="Test name"
                            value={newTest.name}
                            onChange={(e) =>
                              setNewTest({ ...newTest, name: e.target.value })
                            }
                            style={{
                              padding: "0.75rem",
                              border: "2px solid #ddd",
                              borderRadius: "6px",
                            }}
                          />
                          <input
                            type="text"
                            placeholder="Test input"
                            value={newTest.input}
                            onChange={(e) =>
                              setNewTest({ ...newTest, input: e.target.value })
                            }
                            style={{
                              padding: "0.75rem",
                              border: "2px solid #ddd",
                              borderRadius: "6px",
                            }}
                          />
                          <input
                            type="text"
                            placeholder="Expected contains (optional)"
                            value={newTest.expected_contains}
                            onChange={(e) =>
                              setNewTest({
                                ...newTest,
                                expected_contains: e.target.value,
                              })
                            }
                            style={{
                              padding: "0.75rem",
                              border: "2px solid #ddd",
                              borderRadius: "6px",
                            }}
                          />
                          <div style={{ display: "flex", gap: "0.5rem" }}>
                            <button
                              onClick={addTestToSuite}
                              className="primary-btn"
                              style={{ flex: 1 }}
                            >
                              ✅ Add Test
                            </button>
                            <button
                              onClick={() => {
                                setShowNewTestForm(false);
                                setNewTest({
                                  name: "",
                                  input: "",
                                  expected_contains: "",
                                });
                              }}
                              className="secondary-btn"
                            >
                              ❌ Cancel
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Test Results Section */}
              {testResults && (
                <div
                  style={{
                    background: cardBg,
                    border: `2px solid ${cardBorder}`,
                    borderRadius: "10px",
                    padding: "1.5rem",
                    marginBottom: "2rem",
                  }}
                >
                  <h3 style={{ marginTop: 0, marginBottom: "1rem" }}>
                    📊 Test Results
                  </h3>

                  {/* Summary */}
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "repeat(auto-fit, minmax(150px, 1fr))",
                      gap: "1rem",
                      marginBottom: "1.5rem",
                    }}
                  >
                    <div
                      style={{
                        padding: "1rem",
                        background: "#e8f5e9",
                        borderRadius: "8px",
                        textAlign: "center",
                      }}
                    >
                      <div
                        style={{
                          fontSize: "2rem",
                          fontWeight: "bold",
                          color: "#4caf50",
                        }}
                      >
                        {testResults.passed}
                      </div>
                      <div style={{ fontSize: "0.9rem", color: "#666" }}>
                        Passed
                      </div>
                    </div>
                    <div
                      style={{
                        padding: "1rem",
                        background: "#ffebee",
                        borderRadius: "8px",
                        textAlign: "center",
                      }}
                    >
                      <div
                        style={{
                          fontSize: "2rem",
                          fontWeight: "bold",
                          color: "#f44336",
                        }}
                      >
                        {testResults.failed}
                      </div>
                      <div style={{ fontSize: "0.9rem", color: "#666" }}>
                        Failed
                      </div>
                    </div>
                    <div
                      style={{
                        padding: "1rem",
                        background: lightBg,
                        borderRadius: "8px",
                        textAlign: "center",
                      }}
                    >
                      <div
                        style={{
                          fontSize: "2rem",
                          fontWeight: "bold",
                          color: accentColor,
                        }}
                      >
                        {testResults.pass_rate}%
                      </div>
                      <div style={{ fontSize: "0.9rem", color: "#666" }}>
                        Pass Rate
                      </div>
                    </div>
                    <div
                      style={{
                        padding: "1rem",
                        background: lightBg,
                        borderRadius: "8px",
                        textAlign: "center",
                      }}
                    >
                      <div
                        style={{
                          fontSize: "2rem",
                          fontWeight: "bold",
                          color: accentColor,
                        }}
                      >
                        {testResults.avg_response_time_ms}ms
                      </div>
                      <div style={{ fontSize: "0.9rem", color: "#666" }}>
                        Avg Time
                      </div>
                    </div>
                  </div>

                  {/* Individual Test Results */}
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.75rem",
                    }}
                  >
                    {testResults.test_results.map((result, index) => (
                      <div
                        key={index}
                        style={{
                          padding: "1rem",
                          background: result.passed ? "#e8f5e9" : "#ffebee",
                          border: `2px solid ${
                            result.passed ? "#4caf50" : "#f44336"
                          }`,
                          borderRadius: "8px",
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
                          <strong>
                            {result.passed ? "✅" : "❌"} {result.test_name}
                          </strong>
                          <span
                            style={{
                              fontSize: "0.85rem",
                              color: mutedColor,
                            }}
                          >
                            {result.response_time_ms}ms
                          </span>
                        </div>
                        {result.error_message && (
                          <div
                            style={{
                              fontSize: "0.9rem",
                              color: "#d32f2f",
                              marginTop: "0.5rem",
                            }}
                          >
                            {result.error_message}
                          </div>
                        )}
                        {result.actual_output && (
                          <details style={{ marginTop: "0.5rem" }}>
                            <summary
                              style={{ cursor: "pointer", fontSize: "0.9rem" }}
                            >
                              View Output
                            </summary>
                            <div
                              style={{
                                marginTop: "0.5rem",
                                padding: "0.5rem",
                                background: "rgba(0,0,0,0.05)",
                                borderRadius: "4px",
                                fontSize: "0.85rem",
                                fontFamily: "monospace",
                                whiteSpace: "pre-wrap",
                              }}
                            >
                              {result.actual_output}
                            </div>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Test History Section */}
              {testHistory && testHistory.summary && (
                <div
                  style={{
                    background: cardBg,
                    border: `2px solid ${cardBorder}`,
                    borderRadius: "10px",
                    padding: "1.5rem",
                  }}
                >
                  <h3 style={{ marginTop: 0, marginBottom: "1rem" }}>
                    📜 Test History
                  </h3>

                  {/* Summary */}
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "repeat(auto-fit, minmax(150px, 1fr))",
                      gap: "1rem",
                      marginBottom: "1.5rem",
                    }}
                  >
                    <div
                      style={{
                        padding: "1rem",
                        background: lightBg,
                        borderRadius: "8px",
                        textAlign: "center",
                      }}
                    >
                      <div
                        style={{
                          fontSize: "1.5rem",
                          fontWeight: "bold",
                          color: accentColor,
                        }}
                      >
                        {testHistory.summary.total_test_runs}
                      </div>
                      <div style={{ fontSize: "0.9rem", color: "#666" }}>
                        Test Runs
                      </div>
                    </div>
                    <div
                      style={{
                        padding: "1rem",
                        background: lightBg,
                        borderRadius: "8px",
                        textAlign: "center",
                      }}
                    >
                      <div
                        style={{
                          fontSize: "1.5rem",
                          fontWeight: "bold",
                          color: accentColor,
                        }}
                      >
                        {testHistory.summary.overall_pass_rate}%
                      </div>
                      <div style={{ fontSize: "0.9rem", color: "#666" }}>
                        Overall Pass Rate
                      </div>
                    </div>
                  </div>

                  {/* Recent Runs */}
                  {testHistory.summary.recent_runs.length > 0 && (
                    <div>
                      <h4 style={{ marginBottom: "0.75rem" }}>Recent Runs</h4>
                      <div
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.5rem",
                        }}
                      >
                        {testHistory.summary.recent_runs.map((run, index) => (
                          <div
                            key={index}
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              padding: "0.75rem",
                              background: lightBg,
                              borderRadius: "6px",
                              border: "1px solid #e0e0e0",
                            }}
                          >
                            <span style={{ fontSize: "0.9rem" }}>
                              {run.date}
                            </span>
                            <div style={{ display: "flex", gap: "1rem" }}>
                              <span
                                style={{
                                  color: "#4caf50",
                                  fontWeight: "bold",
                                }}
                              >
                                ✅ {run.passed}
                              </span>
                              <span
                                style={{
                                  color: "#f44336",
                                  fontWeight: "bold",
                                }}
                              >
                                ❌ {run.failed}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div
              style={{
                background: "#f8f9ff",
                border: "2px dashed #667eea",
                borderRadius: "10px",
                padding: "3rem",
                textAlign: "center",
                color: mutedColor,
              }}
            >
              <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🧪</div>
              <div style={{ fontSize: "1.1rem" }}>
                Select an agent to start testing
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
