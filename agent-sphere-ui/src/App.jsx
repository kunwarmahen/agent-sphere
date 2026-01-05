import React, { useState, useEffect, useRef } from "react";
import io from "socket.io-client";
import WorkflowBuilder from "./components/WorkflowBuilder";
import AgentBuilder from "./components/AgentBuilder";
import ToolBuilder from "./components/ToolBuilder";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import TestRunner from "./components/TestRunner";
import TemplateBrowser from "./components/TemplateBrowser";

import "./App.css";

const API_URL = "http://localhost:5000/api";
const SOCKET_URL = "http://localhost:5000";

// Format markdown-style responses to JSX
const formatAgentResponse = (text) => {
  const lines = text.split("\n");
  const elements = [];
  let currentList = [];
  let listType = null;

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    if (!trimmed) {
      if (currentList.length > 0) {
        const ListTag = listType === "numbered" ? "ol" : "ul";
        elements.push(
          <ListTag
            key={`list-${index}`}
            style={{ marginLeft: "1rem", marginBottom: "0.5rem" }}
          >
            {currentList.map((item, i) => (
              <li key={i} style={{ marginBottom: "0.3rem" }}>
                {item}
              </li>
            ))}
          </ListTag>
        );
        currentList = [];
        listType = null;
      }
      elements.push(
        <div key={`empty-${index}`} style={{ height: "0.5rem" }} />
      );
      return;
    }

    // Handle bold text with ** (e.g., **Security:)
    if (trimmed.includes("**")) {
      if (currentList.length > 0) {
        const ListTag = listType === "numbered" ? "ol" : "ul";
        elements.push(
          <ListTag
            key={`list-${index}`}
            style={{ marginLeft: "1rem", marginBottom: "0.5rem" }}
          >
            {currentList.map((item, i) => (
              <li key={i} style={{ marginBottom: "0.3rem" }}>
                {item}
              </li>
            ))}
          </ListTag>
        );
        currentList = [];
        listType = null;
      }

      const cleanText = trimmed.replace(/\*\*/g, "");
      elements.push(
        <div
          key={`bold-${index}`}
          style={{
            fontWeight: "700",
            marginTop: "0.5rem",
            marginBottom: "0.25rem",
            fontSize: "1.05em",
          }}
        >
          {cleanText}
        </div>
      );
      return;
    }

    if (trimmed.startsWith("#")) {
      if (currentList.length > 0) {
        const ListTag = listType === "numbered" ? "ol" : "ul";
        elements.push(
          <ListTag
            key={`list-${index}`}
            style={{ marginLeft: "1rem", marginBottom: "0.5rem" }}
          >
            {currentList.map((item, i) => (
              <li key={i} style={{ marginBottom: "0.3rem" }}>
                {item}
              </li>
            ))}
          </ListTag>
        );
        currentList = [];
        listType = null;
      }

      const headingLevel = trimmed.match(/^#+/)[0].length;
      const headingText = trimmed.replace(/^#+\s/, "");
      const HeadingTag = `h${Math.min(headingLevel + 2, 6)}`;

      elements.push(
        React.createElement(
          HeadingTag,
          {
            key: `heading-${index}`,
            style: {
              marginTop: "0.5rem",
              marginBottom: "0.5rem",
              fontSize: headingLevel === 1 ? "1.3rem" : "1.1rem",
            },
          },
          headingText
        )
      );
      return;
    }

    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (listType && listType !== "bullet") {
        const ListTag = listType === "numbered" ? "ol" : "ul";
        elements.push(
          <ListTag
            key={`list-${index}`}
            style={{ marginLeft: "1rem", marginBottom: "0.5rem" }}
          >
            {currentList.map((item, i) => (
              <li key={i} style={{ marginBottom: "0.3rem" }}>
                {item}
              </li>
            ))}
          </ListTag>
        );
        currentList = [];
      }

      listType = "bullet";
      const itemText = trimmed.replace(/^[-*]\s/, "");
      const formattedItem = parseInlineFormatting(itemText);
      currentList.push(formattedItem);
      return;
    }

    if (/^\d+\.\s/.test(trimmed)) {
      if (listType && listType !== "numbered") {
        const ListTag = listType === "numbered" ? "ol" : "ul";
        elements.push(
          <ListTag
            key={`list-${index}`}
            style={{ marginLeft: "1rem", marginBottom: "0.5rem" }}
          >
            {currentList.map((item, i) => (
              <li key={i} style={{ marginBottom: "0.3rem" }}>
                {item}
              </li>
            ))}
          </ListTag>
        );
        currentList = [];
      }

      listType = "numbered";
      const itemText = trimmed.replace(/^\d+\.\s/, "");
      const formattedItem = parseInlineFormatting(itemText);
      currentList.push(formattedItem);
      return;
    }

    if (trimmed) {
      if (currentList.length > 0) {
        const ListTag = listType === "numbered" ? "ol" : "ul";
        elements.push(
          <ListTag
            key={`list-${index}`}
            style={{ marginLeft: "1rem", marginBottom: "0.5rem" }}
          >
            {currentList.map((item, i) => (
              <li key={i} style={{ marginBottom: "0.3rem" }}>
                {item}
              </li>
            ))}
          </ListTag>
        );
        currentList = [];
        listType = null;
      }

      const formattedText = parseInlineFormatting(trimmed);
      elements.push(
        <p
          key={`para-${index}`}
          style={{ marginBottom: "0.5rem", lineHeight: "1.5" }}
        >
          {formattedText}
        </p>
      );
    }
  });

  if (currentList.length > 0) {
    const ListTag = listType === "numbered" ? "ol" : "ul";
    elements.push(
      <ListTag
        key={`list-final`}
        style={{ marginLeft: "1rem", marginBottom: "0.5rem" }}
      >
        {currentList.map((item, i) => (
          <li key={i} style={{ marginBottom: "0.3rem" }}>
            {item}
          </li>
        ))}
      </ListTag>
    );
  }

  return elements;
};

const parseInlineFormatting = (text) => {
  const parts = [];
  let lastIndex = 0;

  const regex = /\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`/g;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    if (match[1]) {
      parts.push(
        <strong key={`bold-${match.index}`} style={{ fontWeight: "700" }}>
          {match[1]}
        </strong>
      );
    } else if (match[2]) {
      parts.push(
        <em key={`italic-${match.index}`} style={{ fontStyle: "italic" }}>
          {match[2]}
        </em>
      );
    } else if (match[3]) {
      parts.push(
        <code
          key={`code-${match.index}`}
          style={{
            backgroundColor: "rgba(0,0,0,0.2)",
            padding: "2px 6px",
            borderRadius: "3px",
            fontFamily: "monospace",
            fontSize: "0.85em",
          }}
        >
          {match[3]}
        </code>
      );
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
};

export default function App() {
  const [activeTab, setActiveTab] = useState("agents");
  const [agents, setAgents] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState("home");
  const [message, setMessage] = useState("");
  const [chatHistories, setChatHistories] = useState({
    home: [],
    calendar: [],
    finance: [],
  });
  const [homeStatus, setHomeStatus] = useState(null);
  const [financialData, setFinancialData] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [visualBuilderWorkflow, setVisualBuilderWorkflow] = useState(null);
  const [newWorkflow, setNewWorkflow] = useState({
    workflow_id: "",
    name: "",
    description: "",
  });

  const [orchestratorQuery, setOrchestratorQuery] = useState("");
  const [orchestratorHistory, setOrchestratorHistory] = useState([]);
  const [orchestratorAnalysis, setOrchestratorAnalysis] = useState(null);
  const [orchestratorLoading, setOrchestratorLoading] = useState(false);
  const [analysisModal, setAnalysisModal] = useState(null);

  const [scenes, setScenes] = useState([]);

  const [todayEvents, setTodayEvents] = useState([]);
  const [todayEmails, setTodayEmails] = useState([]);
  const [calendarDataLoading, setCalendarDataLoading] = useState(false);

  const [customAgentsList, setCustomAgentsList] = useState([]);
  const [selectedCustomAgent, setSelectedCustomAgent] = useState(null);
  const [customAgentChatHistory, setCustomAgentChatHistory] = useState({});
  const [customAgentMessage, setCustomAgentMessage] = useState("");

  const socketRef = useRef(null);
  const recognitionRef = useRef(null);
  const chatHistoryRef = useRef(null);
  const customAgentChatRef = useRef(null);

  useEffect(() => {
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

    // ============================================================================
    // WHISPER AUDIO TRANSCRIPTION SETUP
    // ============================================================================

    let mediaRecorder = null;
    let audioChunks = [];
    let micInitialized = false;

    const initializeAudioCapture = async () => {
      if (micInitialized) return; // Prevent multiple initializations

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        mediaRecorder = new MediaRecorder(stream);
        micInitialized = true;

        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
          audioChunks = [];

          // Send to backend for Whisper transcription
          await transcribeWithWhisper(audioBlob);
        };

        console.log("Microphone initialized successfully");
      } catch (error) {
        console.error("Microphone access error:", error);
        let errorMsg = "Microphone access denied";

        if (error.name === "NotAllowedError") {
          errorMsg =
            "🔐 Microphone permission denied. Enable it in browser settings.";
        } else if (error.name === "NotFoundError") {
          errorMsg = "🔇 No microphone found. Check your audio device.";
        }

        showNotification(errorMsg, "error");
      }
    };

    const transcribeWithWhisper = async (audioBlob) => {
      try {
        const formData = new FormData();
        formData.append("audio", audioBlob, "audio.webm");

        showNotification("🔄 Transcribing audio...", "info");

        const response = await fetch(`${API_URL}/transcribe`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Transcription failed");
        }

        // Set message based on current tab
        if (activeTab === "orchestrator") {
          setOrchestratorQuery(data.text);
        } else if (activeTab === "customAgents") {
          setCustomAgentMessage(data.text);
        } else if (activeTab === "agents") {
          setMessage(data.text);
        }

        showNotification(
          "✅ Voice input received - Review and send",
          "success"
        );
      } catch (error) {
        console.error("Transcription error:", error);
        showNotification(`❌ ${error.message}`, "error");
      } finally {
        setVoiceEnabled(false);
      }
    };

    // Initialize audio capture on component mount (only once)
    initializeAudioCapture();

    // Store in ref for access in other functions
    recognitionRef.current = {
      get mediaRecorder() {
        return mediaRecorder;
      },
      get audioChunks() {
        return audioChunks;
      },
      set audioChunks(value) {
        audioChunks = value;
      },
    };

    // ============================================================================
    // BROWSER NOTIFICATIONS
    // ============================================================================

    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }

    return () => {
      if (socketRef.current) socketRef.current.disconnect();

      // Stop recording if active
      if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
      }

      // Stop all audio tracks
      if (mediaRecorder && mediaRecorder.stream) {
        mediaRecorder.stream.getTracks().forEach((track) => track.stop());
      }
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
    } else if (activeTab === "agents") {
      fetchCustomAgents();
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === "home") {
      fetchScenes();
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === "calendar") {
      fetchTodayCalendarData();
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

  useEffect(() => {
    const timer = setTimeout(() => {
      if (chatHistoryRef.current) {
        chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [chatHistories, selectedAgent, loading]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (customAgentChatRef.current) {
        customAgentChatRef.current.scrollTop =
          customAgentChatRef.current.scrollHeight;
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [customAgentChatHistory, selectedCustomAgent, loading]);

  useEffect(() => {
    const timer = setTimeout(() => {
      const orchestratorChat = document.querySelector(
        ".orchestrator-chat-history"
      );
      if (orchestratorChat) {
        orchestratorChat.scrollTop = orchestratorChat.scrollHeight;
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [orchestratorHistory, orchestratorLoading]);

  const showBrowserNotification = (notification) => {
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(notification.title, {
        body: notification.message,
        icon: "/logo192.png",
      });
    }
  };

  const getChatHistory = () => {
    return chatHistories[selectedAgent] || [];
  };

  const updateChatHistory = (newHistory) => {
    setChatHistories((prev) => ({
      ...prev,
      [selectedAgent]: newHistory,
    }));
  };

  const fetchTodayCalendarData = async () => {
    setCalendarDataLoading(true);
    try {
      // Fetch today's events (0 days ahead = today only)
      const eventsResponse = await fetch(`${API_URL}/calendar/events?days=0`);
      const eventsData = await eventsResponse.json();

      // Fetch emails
      const emailsResponse = await fetch(
        `${API_URL}/calendar/emails?limit=10&unread_only=false`
      );
      const emailsData = await emailsResponse.json();

      setTodayEvents(eventsData.events || []);
      setTodayEmails(emailsData.emails || []);
    } catch (error) {
      console.error("Error fetching calendar data:", error);
      showNotification("Failed to fetch calendar data", "error");
    } finally {
      setCalendarDataLoading(false);
    }
  };

  const navigateToAgent = (agentId) => {
    setSelectedAgent(agentId);
    setActiveTab("agents");
    showNotification(`Switched to ${agentId} agent`, "success");
  };

  const navigateToAgentWithQuestion = (agentId, question) => {
    // Set the agent and message first
    setSelectedAgent(agentId);
    setActiveTab("agents");
    setMessage(question);
    showNotification(`Asking ${agentId} agent...`, "info");

    // Use a longer timeout to ensure state updates
    setTimeout(() => {
      sendQuestionToAgent(agentId, question);
    }, 800);
  };

  const sendQuestionToAgent = async (agentId, questionText) => {
    if (!questionText.trim() || loading) return;

    setLoading(true);
    showNotification("⏳ Sending message...", "info");

    try {
      const response = await fetch(`${API_URL}/agents/${agentId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: questionText }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (!data.response) {
        throw new Error("Empty response from server");
      }

      const currentHistory = getChatHistory();
      updateChatHistory([
        ...currentHistory,
        { type: "user", text: questionText },
        { type: "assistant", text: data.response },
      ]);

      // Clear input after successful send
      setMessage("");
      showNotification("✅ Response received", "success");
    } catch (error) {
      console.error("Error sending message:", error);
      showNotification(`❌ Failed to send message: ${error.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const executeOrchestratorQuery = async (query) => {
    if (!query.trim()) return;

    setOrchestratorLoading(true);
    showNotification("🧠 Analyzing and executing your request...", "info");

    try {
      // First check if custom agents can help
      const customAgentsResponse = await fetch(
        `${API_URL}/agents/custom/my-agents/default_user`
      );
      const customAgentsData = await customAgentsResponse.json();
      const customAgents = customAgentsData.agents || [];

      // Build custom agents into the orchestrator context
      let customAgentsContext = "";
      if (customAgents.length > 0) {
        customAgentsContext = "\n\nAvailable Custom Agents:\n";
        customAgents.forEach((agent) => {
          customAgentsContext += `- ${agent.name} (${agent.role}): ${agent.description}\n`;
          if (agent.tools && agent.tools.length > 0) {
            customAgentsContext += `  Tools: ${agent.tools.join(", ")}\n`;
          }
        });
      }

      const response = await fetch(`${API_URL}/orchestrator/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query + customAgentsContext,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      setOrchestratorHistory([
        ...orchestratorHistory,
        {
          type: "user",
          text: query,
          timestamp: new Date().toISOString(),
        },
        {
          type: "assistant",
          text: data.execution.final_response,
          analysis: data.analysis,
          execution: data.execution,
          timestamp: new Date().toISOString(),
        },
      ]);

      setOrchestratorQuery("");
      setOrchestratorAnalysis(data.analysis);
      showNotification("✅ Request completed successfully", "success");
    } catch (error) {
      console.error("Error executing orchestrator query:", error);
      showNotification(`❌ Error: ${error.message}`, "error");
    } finally {
      setOrchestratorLoading(false);
    }
  };

  const clearOrchestratorHistory = async () => {
    if (
      window.confirm("Are you sure you want to clear the orchestrator history?")
    ) {
      try {
        await fetch(`${API_URL}/orchestrator/clear`, {
          method: "POST",
        });
        setOrchestratorHistory([]);
        setOrchestratorAnalysis(null);
        showNotification("History cleared", "success");
      } catch (error) {
        showNotification("Failed to clear history", "error");
      }
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

  const fetchScenes = async () => {
    try {
      const response = await fetch(`${API_URL}/home/scenes`);
      const data = await response.json();
      setScenes(data.scenes || []);
    } catch (error) {
      console.error("Error fetching scenes:", error);
    }
  };

  const executeScene = async (sceneName) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/home/scenes/${sceneName}/execute`,
        {
          method: "POST",
        }
      );
      const data = await response.json();
      showNotification(`✅ Scene "${sceneName}" executed`, "success");
      fetchScenes();
    } catch (error) {
      console.error("Error executing scene:", error);
      showNotification(`❌ Failed to execute scene: ${error.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const deleteScene = async (sceneName) => {
    if (!window.confirm(`Delete scene "${sceneName}"?`)) return;

    try {
      const response = await fetch(`${API_URL}/home/scenes/${sceneName}`, {
        method: "DELETE",
      });
      const data = await response.json();
      showNotification(`Scene "${sceneName}" deleted`, "success");
      fetchScenes();
    } catch (error) {
      console.error("Error deleting scene:", error);
      showNotification(`Failed to delete scene`, "error");
    }
  };

  const startVoiceInput = (location = "header") => {
    try {
      const mediaRecorder = recognitionRef.current?.mediaRecorder;

      if (!mediaRecorder) {
        showNotification("🔇 Microphone not ready. Please refresh.", "error");
        return;
      }

      if (mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        showNotification("⏹️ Processing audio...", "info");
        setVoiceEnabled(false);
      } else {
        recognitionRef.current.audioChunks = [];
        mediaRecorder.start();
        setVoiceEnabled(true);

        // Different notification based on location
        if (location === "chat") {
          showNotification("🎤 Recording... Speak your message", "info");
        } else {
          showNotification(
            "🎤 Recording... Speak now (click again to stop)",
            "info"
          );
        }
      }
    } catch (error) {
      console.error("Error toggling voice:", error);
      showNotification("Failed to access microphone", "error");
      setVoiceEnabled(false);
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_URL}/agents`);
      const data = await response.json();

      // Fetch custom agents too
      const customResponse = await fetch(
        `${API_URL}/agents/custom/my-agents/default_user`
      );
      const customData = await customResponse.json();

      // Convert custom agents to the same format
      const customAgents = (customData.agents || []).map((agent) => ({
        id: agent.id,
        name: agent.name,
        role: agent.role,
        status: "active",
        isCustom: true,
        tools: agent.tools,
      }));

      // Combine built-in and custom agents
      const allAgents = [...data.agents, ...customAgents];
      setAgents(allAgents);
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

  const fetchCustomAgents = async () => {
    try {
      const response = await fetch(
        `${API_URL}/agents/custom/my-agents/default_user`
      );
      const data = await response.json();
      setCustomAgentsList(data.agents || []);

      // Select first custom agent by default
      if (data.agents && data.agents.length > 0 && !selectedCustomAgent) {
        setSelectedCustomAgent(data.agents[0].id);
      }
    } catch (error) {
      console.error("Error fetching custom agents:", error);
    }
  };

  const sendCustomAgentMessage = async (e) => {
    if (e) e.preventDefault();

    if (!customAgentMessage.trim() || !selectedCustomAgent) return;

    setLoading(true);
    showNotification("⏳ Sending message...", "info");

    try {
      const response = await fetch(
        `${API_URL}/agents/custom/${selectedCustomAgent}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: customAgentMessage }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (!data.response) {
        throw new Error("Empty response from server");
      }

      const currentHistory = customAgentChatHistory[selectedCustomAgent] || [];
      setCustomAgentChatHistory({
        ...customAgentChatHistory,
        [selectedCustomAgent]: [
          ...currentHistory,
          { type: "user", text: customAgentMessage },
          {
            type: "assistant",
            text: data.response,
            tools: data.tools_available,
          },
        ],
      });

      setCustomAgentMessage("");
      showNotification("✅ Response received", "success");
    } catch (error) {
      console.error("Error sending message:", error);
      showNotification(`❌ Failed to send message: ${error.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    showNotification("⏳ Sending message...", "info");

    try {
      // Check if it's a custom agent
      const agent = agents.find((a) => a.id === selectedAgent);
      const endpoint = agent?.isCustom
        ? `${API_URL}/agents/custom/${selectedAgent}/chat`
        : `${API_URL}/agents/${selectedAgent}/chat`;

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (!data.response) {
        throw new Error("Empty response from server");
      }

      const currentHistory = getChatHistory();
      updateChatHistory([
        ...currentHistory,
        { type: "user", text: message },
        { type: "assistant", text: data.response },
      ]);

      setMessage("");
      showNotification("✅ Response received", "success");
    } catch (error) {
      console.error("Error sending message:", error);
      showNotification(`❌ Failed to send message: ${error.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const clearChatHistory = () => {
    if (
      window.confirm(
        `Clear chat history with ${
          agents.find((a) => a.id === selectedAgent)?.name || "this agent"
        }?`
      )
    ) {
      updateChatHistory([]);
      showNotification("Chat history cleared", "success");
    }
  };

  const toggleDoorLock = async () => {
    try {
      const newLockState = !homeStatus.security.door_locked;
      await fetch(`${API_URL}/home/door`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lock: newLockState }),
      });
      fetchHomeStatus();
      showNotification(
        `Door ${newLockState ? "locked" : "unlocked"}`,
        "success"
      );
    } catch (error) {
      console.error("Error toggling door lock:", error);
      showNotification("Failed to toggle door lock", "error");
    }
  };

  const toggleGarageDoor = async () => {
    try {
      const newGarageState = !homeStatus.security.garage_open;
      await fetch(`${API_URL}/home/garage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ open_garage: newGarageState }),
      });
      fetchHomeStatus();
      showNotification(
        `Garage ${newGarageState ? "opened" : "closed"}`,
        "success"
      );
    } catch (error) {
      console.error("Error toggling garage:", error);
      showNotification("Failed to toggle garage door", "error");
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

  const toggleDevice = async (device) => {
    try {
      // First, get current state
      const currentState = homeStatus.devices[device].on;

      await fetch(`${API_URL}/home/device/${device}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ on: !currentState }),
      });

      fetchHomeStatus();
      showNotification(
        `${device.replace("_", " ").toUpperCase()} turned ${
          !currentState ? "on" : "off"
        }`,
        "success"
      );
    } catch (error) {
      console.error("Error toggling device:", error);
      showNotification("Failed to toggle device", "error");
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

  const openWorkflowInVisualBuilder = async (workflowId) => {
    try {
      const response = await fetch(`${API_URL}/workflows/${workflowId}`);
      const workflowData = await response.json();

      // Convert backend workflow format to visual builder format
      const visualWorkflow = {
        name: workflowData.name,
        nodes: [],
        connections: [],
      };

      // Create Start node
      const startNode = {
        id: "node_start",
        type: "start",
        position: { x: 250, y: 50 },
        data: { label: "Start" },
      };
      visualWorkflow.nodes.push(startNode);

      // Create nodes for each task
      let yPosition = 150;
      const nodeMap = {}; // Map task IDs to node IDs

      workflowData.tasks.forEach((task, index) => {
        const nodeId = `node_${task.task_id}`;
        nodeMap[task.task_id] = nodeId;

        const node = {
          id: nodeId,
          type: "agent",
          position: { x: 250, y: yPosition },
          data: {
            label: task.task_id.replace(/_/g, " "),
            agent: task.agent_name,
            request: task.request,
          },
        };
        visualWorkflow.nodes.push(node);
        yPosition += 120;
      });

      // Create End node
      const endNode = {
        id: "node_end",
        type: "end",
        position: { x: 250, y: yPosition + 50 },
        data: { label: "End" },
      };
      visualWorkflow.nodes.push(endNode);

      // Create connections based on task linking
      let connIndex = 0;

      // Connect start to first task
      if (workflowData.tasks.length > 0) {
        visualWorkflow.connections.push({
          id: `conn_${connIndex++}`,
          from: "node_start",
          to: `node_${workflowData.tasks[0].task_id}`,
          label: "",
        });
      }

      // Connect tasks based on next_task_id
      workflowData.tasks.forEach((task) => {
        if (task.next_task_id) {
          visualWorkflow.connections.push({
            id: `conn_${connIndex++}`,
            from: `node_${task.task_id}`,
            to: `node_${task.next_task_id}`,
            label: "",
          });
        }
      });

      // Find last task and connect to end
      const lastTask = workflowData.tasks[workflowData.tasks.length - 1];
      if (lastTask) {
        visualWorkflow.connections.push({
          id: `conn_${connIndex++}`,
          from: `node_${lastTask.task_id}`,
          to: "node_end",
          label: "",
        });
      }

      setVisualBuilderWorkflow(visualWorkflow);
      setActiveTab("builder");
      showNotification("Workflow opened in Visual Builder", "success");
    } catch (error) {
      console.error("Error opening workflow:", error);
      showNotification("Failed to open workflow in Visual Builder", "error");
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

        // Create initial visual workflow for builder
        const visualWorkflow = {
          name: newWorkflow.name,
          nodes: [
            {
              id: "node_start",
              type: "start",
              position: { x: 250, y: 50 },
              data: { label: "Start" },
            },
            {
              id: "node_end",
              type: "end",
              position: { x: 250, y: 200 },
              data: { label: "End" },
            },
          ],
          connections: [
            {
              id: "conn_1",
              from: "node_start",
              to: "node_end",
              label: "",
            },
          ],
        };

        setVisualBuilderWorkflow(visualWorkflow);
        setActiveTab("builder");
        showNotification(
          "Workflow created! Open in Visual Builder to add tasks.",
          "success"
        );
        fetchWorkflows();
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
            onClick={() => startVoiceInput("header")}
            className={`icon-btn ${voiceEnabled ? "active" : ""}`}
            title={
              voiceEnabled
                ? "Click to stop recording"
                : "Click to start recording"
            }
          >
            {voiceEnabled ? "⏹️" : "🎤"}
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
          className={`nav-btn ${activeTab === "orchestrator" ? "active" : ""}`}
          onClick={() => setActiveTab("orchestrator")}
        >
          🧠 Smart Assistant
        </button>
        <button
          className={`nav-btn ${activeTab === "agents" ? "active" : ""}`}
          onClick={() => setActiveTab("agents")}
        >
          💬 Agents
        </button>
        <button
          className={`nav-btn ${activeTab === "customAgents" ? "active" : ""}`}
          onClick={() => {
            setActiveTab("customAgents");
            fetchCustomAgents();
          }}
        >
          🤖 Custom Agents
        </button>
        <button
          className={`nav-btn ${activeTab === "home" ? "active" : ""}`}
          onClick={() => setActiveTab("home")}
        >
          🏠 Home
        </button>
        <button
          className={`nav-btn ${activeTab === "calendar" ? "active" : ""}`}
          onClick={() => setActiveTab("calendar")}
        >
          📅 Calendar
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
        <button
          className={`nav-btn ${
            activeTab === "agentMarketplace" ? "active" : ""
          }`}
          onClick={() => setActiveTab("agentMarketplace")}
        >
          🛠️ Agent Marketplace
        </button>
        <button
          className={`nav-btn ${activeTab === "toolBuilder" ? "active" : ""}`}
          onClick={() => setActiveTab("toolBuilder")}
        >
          🔧 Tool Builder
        </button>
        <button
          className={`nav-btn ${activeTab === "builder" ? "active" : ""}`}
          onClick={() => setActiveTab("builder")}
        >
          🎨 Visual Builder
        </button>
        <button
          className={`nav-btn ${activeTab === "analytics" ? "active" : ""}`}
          onClick={() => setActiveTab("analytics")}
        >
          📊 Analytics
        </button>

        <button
          className={`nav-btn ${activeTab === "testing" ? "active" : ""}`}
          onClick={() => setActiveTab("testing")}
        >
          🧪 Testing
        </button>

        <button
          className={`nav-btn ${activeTab === "templates" ? "active" : ""}`}
          onClick={() => setActiveTab("templates")}
        >
          📚 Templates
        </button>
      </nav>
      <main className="content">
        {activeTab === "builder" && (
          <WorkflowBuilder initialWorkflow={visualBuilderWorkflow} />
        )}
        {activeTab === "agentMarketplace" && (
          <AgentBuilder
            activeTab={activeTab}
            loading={loading}
            showNotification={showNotification}
          />
        )}
        {activeTab === "toolBuilder" && (
          <section className="section">
            <ToolBuilder showNotification={showNotification} />
          </section>
        )}

        {activeTab === "analytics" && (
          <AnalyticsDashboard showNotification={showNotification} />
        )}

        {activeTab === "testing" && (
          <TestRunner showNotification={showNotification} />
        )}

        {activeTab === "templates" && (
          <TemplateBrowser showNotification={showNotification} />
        )}

        {activeTab === "customAgents" && (
          <section className="section">
            <h2>🤖 Custom Agents</h2>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "250px 1fr",
                gap: "1.5rem",
                minHeight: "600px",
              }}
            >
              {/* Custom Agents List */}
              <div
                style={{
                  background: "#f8f9ff",
                  borderRadius: "10px",
                  border: "2px solid #e0e0e0",
                  padding: "1rem",
                  maxHeight: "600px",
                  overflowY: "auto",
                }}
              >
                <h3
                  style={{ marginTop: 0, color: "#667eea", fontSize: "1.1rem" }}
                >
                  Your Agents
                </h3>
                {customAgentsList.length === 0 ? (
                  <p style={{ color: "#999", fontSize: "0.9rem" }}>
                    No custom agents yet. Create one in Agent Marketplace tab.
                  </p>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.5rem",
                    }}
                  >
                    {customAgentsList.map((agent) => (
                      <button
                        key={agent.id}
                        onClick={() => {
                          setSelectedCustomAgent(agent.id);
                          if (!customAgentChatHistory[agent.id]) {
                            setCustomAgentChatHistory({
                              ...customAgentChatHistory,
                              [agent.id]: [],
                            });
                          }
                        }}
                        style={{
                          padding: "0.75rem",
                          border:
                            selectedCustomAgent === agent.id
                              ? "2px solid #667eea"
                              : "2px solid #ddd",
                          borderRadius: "8px",
                          background:
                            selectedCustomAgent === agent.id
                              ? "#667eea"
                              : "white",
                          color:
                            selectedCustomAgent === agent.id ? "white" : "#333",
                          cursor: "pointer",
                          textAlign: "left",
                          transition: "all 0.3s ease",
                          fontWeight:
                            selectedCustomAgent === agent.id
                              ? "bold"
                              : "normal",
                        }}
                      >
                        <div style={{ fontSize: "0.9rem" }}>{agent.name}</div>
                        <div style={{ fontSize: "0.75rem", opacity: 0.8 }}>
                          {agent.role}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Chat Interface */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 0,
                  background:
                    "linear-gradient(135deg, #5a4a8a 0%, #463d73 100%)",
                  borderRadius: "10px",
                  overflow: "hidden",
                  border: "2px solid #e0e0e0",
                }}
              >
                {selectedCustomAgent ? (
                  <>
                    {/* Agent Info Header */}
                    <div
                      style={{
                        padding: "1rem",
                        background: "rgba(0,0,0,0.2)",
                        borderBottom: "1px solid rgba(255,255,255,0.2)",
                        color: "white",
                      }}
                    >
                      <h3 style={{ margin: 0, fontSize: "1.1rem" }}>
                        {
                          customAgentsList.find(
                            (a) => a.id === selectedCustomAgent
                          )?.name
                        }
                      </h3>
                      <p
                        style={{
                          margin: "0.25rem 0 0 0",
                          fontSize: "0.85rem",
                          opacity: 0.8,
                        }}
                      >
                        {
                          customAgentsList.find(
                            (a) => a.id === selectedCustomAgent
                          )?.role
                        }
                      </p>
                    </div>

                    {/* Chat History */}
                    <div
                      className="chat-history"
                      ref={customAgentChatRef}
                      style={{ flex: 1, padding: "1.5rem" }}
                    >
                      {(customAgentChatHistory[selectedCustomAgent] || [])
                        .length === 0 && (
                        <div className="empty-chat">
                          Start a conversation with{" "}
                          {
                            customAgentsList.find(
                              (a) => a.id === selectedCustomAgent
                            )?.name
                          }
                        </div>
                      )}
                      {(customAgentChatHistory[selectedCustomAgent] || []).map(
                        (msg, idx) => (
                          <div
                            key={idx}
                            className={`chat-message ${msg.type}-modern`}
                          >
                            <strong>
                              {msg.type === "user"
                                ? "👤 You"
                                : "🤖 " +
                                  customAgentsList.find(
                                    (a) => a.id === selectedCustomAgent
                                  )?.name}
                            </strong>
                            {msg.type === "user" ? (
                              <p>{msg.text}</p>
                            ) : (
                              <div>
                                <div>{formatAgentResponse(msg.text)}</div>
                                {msg.tools && msg.tools.length > 0 && (
                                  <div
                                    style={{
                                      marginTop: "0.75rem",
                                      padding: "0.5rem",
                                      background: "rgba(255,255,255,0.1)",
                                      borderRadius: "6px",
                                      fontSize: "0.8rem",
                                    }}
                                  >
                                    <strong>Available Tools:</strong>
                                    <div style={{ marginTop: "0.25rem" }}>
                                      {msg.tools.map((tool, i) => (
                                        <span
                                          key={i}
                                          style={{
                                            display: "inline-block",
                                            background: "rgba(255,255,255,0.2)",
                                            padding: "0.2rem 0.4rem",
                                            borderRadius: "3px",
                                            marginRight: "0.5rem",
                                            marginBottom: "0.25rem",
                                          }}
                                        >
                                          {tool}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )
                      )}
                      {loading && (
                        <div className="chat-message assistant-modern">
                          <strong>🤖 Agent</strong>
                          <p className="typing">Thinking...</p>
                        </div>
                      )}
                    </div>

                    {/* Chat Form */}
                    <form
                      onSubmit={sendCustomAgentMessage}
                      className="chat-form"
                    >
                      <input
                        type="text"
                        placeholder="Ask your custom agent..."
                        value={customAgentMessage}
                        onChange={(e) => setCustomAgentMessage(e.target.value)}
                        disabled={loading}
                      />
                      <button
                        type="button"
                        onClick={() => startVoiceInput("customAgent")}
                        className={`voice-btn-chat ${
                          voiceEnabled ? "recording" : ""
                        }`}
                        disabled={loading}
                      >
                        {voiceEnabled ? "⏹️ Stop" : "🎤"}
                      </button>
                      <button type="submit" disabled={loading}>
                        {loading ? "⏳" : "📤"}
                      </button>
                    </form>
                  </>
                ) : (
                  <div className="empty-chat">
                    No custom agents available. Create one first!
                  </div>
                )}
              </div>
            </div>
          </section>
        )}
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
              <div
                style={{
                  padding: "0.5rem 1rem",
                  borderBottom: "1px solid rgba(255,255,255,0.2)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span
                  style={{ color: "rgba(255,255,255,0.7)", fontSize: "0.9rem" }}
                >
                  💬 {agents.find((a) => a.id === selectedAgent)?.name}'s Chat
                </span>
                <button
                  onClick={clearChatHistory}
                  style={{
                    background: "transparent",
                    border: "1px solid rgba(255,255,255,0.3)",
                    color: "rgba(255,255,255,0.7)",
                    padding: "0.3rem 0.8rem",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "0.8rem",
                    transition: "all 0.3s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = "rgba(255,255,255,0.1)";
                    e.target.style.borderColor = "rgba(255,255,255,0.5)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = "transparent";
                    e.target.style.borderColor = "rgba(255,255,255,0.3)";
                  }}
                >
                  🗑️ Clear
                </button>
              </div>
              <div className="chat-history" ref={chatHistoryRef}>
                {getChatHistory().length === 0 && (
                  <div className="empty-chat">
                    Start a conversation with{" "}
                    {agents.find((a) => a.id === selectedAgent)?.name ||
                      "an agent"}
                  </div>
                )}
                {getChatHistory().map((msg, idx) => (
                  <div key={idx} className={`chat-message ${msg.type}-modern`}>
                    <strong>
                      {msg.type === "user" ? "👤 You" : "🤖 Agent"}
                    </strong>
                    {msg.type === "user" ? (
                      <p>{msg.text}</p>
                    ) : (
                      <div>{formatAgentResponse(msg.text)}</div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="chat-message assistant-modern">
                    <strong>🤖 Agent</strong>
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
                <button type="submit" disabled={loading || !message.trim()}>
                  {loading ? "⏳" : "📤"}
                </button>
                <button
                  type="button"
                  onClick={() => startVoiceInput("chat")}
                  className={`voice-btn-chat ${
                    voiceEnabled ? "recording" : ""
                  }`}
                  disabled={loading}
                  title="Click to record voice message"
                >
                  {voiceEnabled ? "⏹️ Stop" : "🎤 Record"}
                </button>
              </form>
            </div>
          </section>
        )}
        {activeTab === "orchestrator" && (
          <section className="section">
            <h2>🧠 Smart Multi-Agent Assistant</h2>
            <p
              style={{
                color: "#666",
                marginBottom: "1.5rem",
                fontSize: "0.95rem",
              }}
            >
              Ask complex questions and I'll automatically coordinate multiple
              agents to solve your request. For example: "Schedule a meeting
              tomorrow and send invitations" or "Turn on the living room lights
              and set temperature to 72 degrees"
            </p>

            {/* Chat History */}
            <div className="chat-container">
              <div
                style={{
                  padding: "0.5rem 1rem",
                  borderBottom: "1px solid rgba(255,255,255,0.2)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span
                  style={{ color: "rgba(255,255,255,0.7)", fontSize: "0.9rem" }}
                >
                  💬 Conversation History
                </span>
                <button
                  onClick={clearOrchestratorHistory}
                  style={{
                    background: "transparent",
                    border: "1px solid rgba(255,255,255,0.3)",
                    color: "rgba(255,255,255,0.7)",
                    padding: "0.3rem 0.8rem",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "0.8rem",
                    transition: "all 0.3s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = "rgba(255,255,255,0.1)";
                    e.target.style.borderColor = "rgba(255,255,255,0.5)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = "transparent";
                    e.target.style.borderColor = "rgba(255,255,255,0.3)";
                  }}
                >
                  🗑️ Clear
                </button>
              </div>

              <div
                className="chat-history orchestrator-chat-history"
                ref={chatHistoryRef}
              >
                {orchestratorHistory.length === 0 && (
                  <div className="empty-chat">
                    Ask me anything! I'll coordinate the right agents to help
                    you.
                  </div>
                )}
                {orchestratorHistory.map((msg, idx) => (
                  <div key={idx} className={`chat-message ${msg.type}-modern`}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "0.5rem",
                      }}
                    >
                      <strong>
                        {msg.type === "user" ? "👤 You" : "🧠 Smart Assistant"}
                      </strong>

                      {/* Info Icon for Analysis - Only show on assistant responses with analysis */}
                      {msg.type === "assistant" && msg.analysis && (
                        <button
                          onClick={() => setAnalysisModal(msg.analysis)}
                          style={{
                            background: "transparent",
                            border: "none",
                            cursor: "pointer",
                            fontSize: "1rem",
                            padding: "0",
                            marginLeft: "auto",
                          }}
                          title="Click to view analysis"
                        >
                          ℹ️
                        </button>
                      )}
                    </div>

                    {msg.type === "user" ? (
                      <p>{msg.text}</p>
                    ) : (
                      <div>
                        <div>{formatAgentResponse(msg.text)}</div>
                        {msg.execution && (
                          <div
                            style={{
                              marginTop: "1rem",
                              padding: "0.75rem",
                              background: "rgba(255,255,255,0.1)",
                              borderRadius: "8px",
                              fontSize: "0.85rem",
                            }}
                          >
                            <strong>Execution Details:</strong>
                            <p style={{ margin: "0.5rem 0" }}>
                              ✅ Completed {msg.execution.steps_executed.length}{" "}
                              step(s)
                            </p>
                            <p style={{ margin: "0.5rem 0" }}>
                              🤖 Agents Used:{" "}
                              {msg.analysis.detected_agents.join(", ")}
                            </p>
                            {msg.execution.errors.length > 0 && (
                              <p
                                style={{ margin: "0.5rem 0", color: "#ffb3b3" }}
                              >
                                ⚠️ {msg.execution.errors.length} error(s)
                                occurred
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
                {orchestratorLoading && (
                  <div className="chat-message assistant-modern">
                    <strong>🧠 Smart Assistant</strong>
                    <p className="typing">Analyzing and executing...</p>
                  </div>
                )}
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  executeOrchestratorQuery(orchestratorQuery);
                }}
                className="chat-form"
              >
                <input
                  type="text"
                  placeholder="Ask me to do something complex..."
                  value={orchestratorQuery}
                  onChange={(e) => setOrchestratorQuery(e.target.value)}
                  disabled={orchestratorLoading}
                />
                <button
                  type="button"
                  onClick={() => startVoiceInput("orchestrator")}
                  className={`voice-btn-chat ${
                    voiceEnabled ? "recording" : ""
                  }`}
                  disabled={orchestratorLoading}
                  title="Click to record"
                >
                  {voiceEnabled ? "⏹️ Stop" : "🎤"}
                </button>
                <button type="submit" disabled={orchestratorLoading}>
                  {orchestratorLoading ? "⏳" : "📤"}
                </button>
              </form>
            </div>

            {/* Analysis Modal */}
            {analysisModal && (
              <div
                style={{
                  position: "fixed",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: "rgba(0,0,0,0.5)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  zIndex: 1000,
                  backdropFilter: "blur(5px)",
                }}
                onClick={() => setAnalysisModal(null)}
              >
                <div
                  style={{
                    background: "white",
                    borderRadius: "15px",
                    padding: "2rem",
                    maxWidth: "600px",
                    width: "90%",
                    maxHeight: "80vh",
                    overflowY: "auto",
                    boxShadow: "0 10px 40px rgba(0,0,0,0.3)",
                  }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "1.5rem",
                    }}
                  >
                    <h2 style={{ color: "#667eea", margin: 0 }}>
                      📊 Request Analysis
                    </h2>
                    <button
                      onClick={() => setAnalysisModal(null)}
                      style={{
                        background: "transparent",
                        border: "none",
                        fontSize: "1.5rem",
                        cursor: "pointer",
                      }}
                    >
                      ✕
                    </button>
                  </div>

                  <div style={{ color: "#333", lineHeight: "1.6" }}>
                    <div style={{ marginBottom: "1rem" }}>
                      <strong style={{ color: "#667eea" }}>Reasoning:</strong>
                      <p style={{ margin: "0.5rem 0", color: "#666" }}>
                        {analysisModal.reasoning}
                      </p>
                    </div>

                    <div style={{ marginBottom: "1rem" }}>
                      <strong style={{ color: "#667eea" }}>
                        Agents Required:
                      </strong>
                      <div
                        style={{
                          display: "flex",
                          gap: "0.5rem",
                          flexWrap: "wrap",
                          margin: "0.5rem 0",
                        }}
                      >
                        {analysisModal.detected_agents.map((agent) => (
                          <span
                            key={agent}
                            style={{
                              background: "#667eea",
                              color: "white",
                              padding: "0.4rem 0.8rem",
                              borderRadius: "20px",
                              fontSize: "0.9rem",
                            }}
                          >
                            🤖 {agent}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <strong style={{ color: "#667eea" }}>
                        Execution Steps:
                      </strong>
                      <ol
                        style={{
                          margin: "0.5rem 0",
                          paddingLeft: "1.5rem",
                          color: "#666",
                        }}
                      >
                        {analysisModal.execution_steps.map((step, idx) => (
                          <li key={idx} style={{ marginBottom: "0.5rem" }}>
                            <strong>{step.task}</strong>
                            <p
                              style={{
                                margin: "0.25rem 0",
                                fontSize: "0.9rem",
                              }}
                            >
                              Agent: {step.agent} • Context: {step.context}
                            </p>
                          </li>
                        ))}
                      </ol>
                    </div>
                  </div>
                </div>
              </div>
            )}
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
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.75rem",
                    }}
                  >
                    {/* Door Lock Control */}
                    <button
                      onClick={toggleDoorLock}
                      className={`device-btn ${
                        homeStatus.security.door_locked ? "on" : "off"
                      }`}
                      style={{ justifyContent: "space-between" }}
                    >
                      <span className="device-name">
                        {homeStatus.security.door_locked ? "🔒" : "🔓"} Front
                        Door
                      </span>
                      <span
                        className={`device-status ${
                          homeStatus.security.door_locked ? "on" : "off"
                        }`}
                      >
                        {homeStatus.security.door_locked
                          ? "Locked"
                          : "Unlocked"}
                      </span>
                    </button>

                    {/* Garage Door Control */}
                    <button
                      onClick={toggleGarageDoor}
                      className={`device-btn ${
                        homeStatus.security.garage_open ? "off" : "on"
                      }`}
                      style={{ justifyContent: "space-between" }}
                    >
                      <span className="device-name">
                        {homeStatus.security.garage_open ? "🚗" : "🚪"} Garage
                      </span>
                      <span
                        className={`device-status ${
                          homeStatus.security.garage_open ? "off" : "on"
                        }`}
                      >
                        {homeStatus.security.garage_open ? "Open" : "Closed"}
                      </span>
                    </button>

                    {/* Motion Detection Status (Read-only) */}
                    <div
                      style={{
                        padding: "0.75rem 1rem",
                        background: homeStatus.security.motion_detected
                          ? "#fff3cd"
                          : "#d4edda",
                        border: `2px solid ${
                          homeStatus.security.motion_detected
                            ? "#ffc107"
                            : "#28a745"
                        }`,
                        borderRadius: "8px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <span style={{ fontWeight: 600, color: "#333" }}>
                        {homeStatus.security.motion_detected ? "⚠️" : "✅"}{" "}
                        Motion Sensor
                      </span>
                      <span
                        style={{
                          fontWeight: 700,
                          color: homeStatus.security.motion_detected
                            ? "#ff6b00"
                            : "#28a745",
                        }}
                      >
                        {homeStatus.security.motion_detected
                          ? "Motion Detected"
                          : "Clear"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="home-card">
                  <h3>📺 Devices</h3>
                  <div className="device-list">
                    {Object.entries(homeStatus.devices).map(
                      ([device, status]) => (
                        <button
                          key={device}
                          onClick={() => toggleDevice(device)}
                          className={`device-btn ${status.on ? "on" : "off"}`}
                        >
                          <span className="device-name">
                            {device.replace("_", " ")}
                          </span>
                          <span
                            className={`device-status ${
                              status.on ? "on" : "off"
                            }`}
                          >
                            {status.on ? "✔ ON" : "✘ OFF"}
                          </span>
                        </button>
                      )
                    )}
                  </div>
                </div>

                {/* Scenes Section */}
                <div className="home-card">
                  <h3>🎬 Automation Scenes</h3>
                  {scenes.length === 0 ? (
                    <p style={{ color: "#999", fontSize: "0.9rem" }}>
                      No scenes created yet. Ask the Home Agent to create scenes
                      like "Sleeping Mode", "Movie Time", etc.
                    </p>
                  ) : (
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "0.75rem",
                      }}
                    >
                      {scenes.map((scene) => (
                        <div
                          key={scene.name}
                          style={{
                            padding: "1rem",
                            background: "#f0f4ff",
                            borderRadius: "8px",
                            border: "2px solid #667eea",
                          }}
                        >
                          {/* Scene Header and Title */}
                          <div style={{ marginBottom: "0.75rem" }}>
                            <strong
                              style={{
                                color: "#667eea",
                                display: "block",
                                marginBottom: "0.25rem",
                                fontSize: "1rem",
                              }}
                            >
                              {scene.name}
                            </strong>
                            <small style={{ color: "#666" }}>
                              {scene.action_count} action
                              {scene.action_count !== 1 ? "s" : ""} • Executed{" "}
                              {scene.executions} time
                              {scene.executions !== 1 ? "s" : ""}
                            </small>
                          </div>

                          {/* Details - Expandable */}
                          <details
                            style={{
                              cursor: "pointer",
                              marginBottom: "0.75rem",
                            }}
                          >
                            <summary
                              style={{ color: "#667eea", fontSize: "0.85rem" }}
                            >
                              📋 View Actions
                            </summary>
                            <div
                              style={{
                                marginTop: "0.5rem",
                                paddingLeft: "1rem",
                                fontSize: "0.8rem",
                                color: "#666",
                              }}
                            >
                              {scene.actions.map((action, idx) => (
                                <div
                                  key={idx}
                                  style={{
                                    marginBottom: "0.25rem",
                                    fontFamily: "monospace",
                                  }}
                                >
                                  • {action}
                                </div>
                              ))}
                            </div>
                          </details>

                          {/* Action Buttons - Below Details */}
                          <div style={{ display: "flex", gap: "0.5rem" }}>
                            <button
                              onClick={() => executeScene(scene.name)}
                              disabled={loading}
                              className="primary-btn"
                              style={{
                                flex: 1,
                                padding: "0.5rem 1rem",
                                fontSize: "0.9rem",
                              }}
                            >
                              ▶️ Execute
                            </button>
                            <button
                              onClick={() => deleteScene(scene.name)}
                              disabled={loading}
                              className="secondary-btn"
                              style={{
                                padding: "0.5rem 1rem",
                                fontSize: "0.9rem",
                                color: "#f44336",
                                borderColor: "#f44336",
                              }}
                            >
                              🗑️ Delete
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </section>
        )}
        {activeTab === "calendar" && (
          <section className="section">
            <h2>📅 Calendar & Email</h2>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                gap: "1.5rem",
              }}
            >
              {/* Today's Events */}
              <div className="home-card">
                <h3>📆 Today's Events</h3>
                {calendarDataLoading ? (
                  <p style={{ color: "#999" }}>Loading...</p>
                ) : todayEvents.length === 0 ? (
                  <p style={{ color: "#999", fontSize: "0.9rem" }}>
                    No events scheduled for today
                  </p>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.75rem",
                    }}
                  >
                    {todayEvents.map((event) => (
                      <div
                        key={event.id}
                        style={{
                          padding: "0.75rem",
                          background: "#f0f4ff",
                          borderRadius: "8px",
                          borderLeft: "4px solid #667eea",
                        }}
                      >
                        <strong
                          style={{
                            color: "#667eea",
                            display: "block",
                            marginBottom: "0.25rem",
                          }}
                        >
                          {event.title}
                        </strong>
                        <small
                          style={{
                            color: "#666",
                            display: "block",
                            marginBottom: "0.25rem",
                          }}
                        >
                          ⏰{" "}
                          {new Date(event.start).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </small>
                        {event.location && (
                          <small
                            style={{
                              color: "#666",
                              display: "block",
                              marginBottom: "0.25rem",
                            }}
                          >
                            📍 {event.location}
                          </small>
                        )}
                        {event.attendees && event.attendees.length > 0 && (
                          <small style={{ color: "#999", display: "block" }}>
                            👥 {event.attendees.length} attendee(s)
                          </small>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                <button
                  className="primary-btn"
                  onClick={() => navigateToAgent("calendar")}
                  style={{ width: "100%", marginTop: "1rem" }}
                >
                  📅 View Full Calendar
                </button>
              </div>

              {/* Today's Emails */}
              <div className="home-card">
                <h3>📧 Today's Emails</h3>
                {calendarDataLoading ? (
                  <p style={{ color: "#999" }}>Loading...</p>
                ) : todayEmails.length === 0 ? (
                  <p style={{ color: "#999", fontSize: "0.9rem" }}>
                    No emails from today
                  </p>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.75rem",
                    }}
                  >
                    {todayEmails.map((email) => (
                      <div
                        key={email.id}
                        style={{
                          padding: "0.75rem",
                          background: email.read ? "#f5f5f5" : "#e3f2fd",
                          borderRadius: "8px",
                          borderLeft: `4px solid ${
                            email.read ? "#999" : "#2196f3"
                          }`,
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "start",
                            gap: "0.5rem",
                          }}
                        >
                          <div style={{ flex: 1 }}>
                            <strong
                              style={{
                                color: "#333",
                                display: "block",
                                marginBottom: "0.25rem",
                                fontWeight: email.read ? 500 : 700,
                              }}
                            >
                              {email.subject}
                            </strong>
                            <small
                              style={{
                                color: "#666",
                                display: "block",
                                marginBottom: "0.25rem",
                              }}
                            >
                              From: {email.from}
                            </small>
                            <small style={{ color: "#999" }}>
                              {new Date(email.date).toLocaleDateString()}
                            </small>
                          </div>
                          {email.starred && (
                            <span style={{ fontSize: "1.2rem" }}>⭐</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                <button
                  className="primary-btn"
                  onClick={() => navigateToAgent("calendar")}
                  style={{ width: "100%", marginTop: "1rem" }}
                >
                  ✉️ Check All Emails
                </button>
              </div>

              {/* Quick Actions */}
              <div className="home-card">
                <h3>⚡ Quick Actions</h3>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.5rem",
                  }}
                >
                  <button
                    className="secondary-btn"
                    style={{ width: "100%" }}
                    onClick={() =>
                      navigateToAgentWithQuestion(
                        "calendar",
                        "Show me my calendar events for the next 7 days"
                      )
                    }
                    disabled={calendarDataLoading}
                  >
                    📅 View My Calendar
                  </button>
                  <button
                    className="secondary-btn"
                    style={{ width: "100%" }}
                    onClick={() =>
                      navigateToAgentWithQuestion(
                        "calendar",
                        "Show me my unread emails"
                      )
                    }
                    disabled={calendarDataLoading}
                  >
                    📧 Check Emails
                  </button>
                  <button
                    className="secondary-btn"
                    style={{ width: "100%" }}
                    onClick={() =>
                      navigateToAgentWithQuestion(
                        "calendar",
                        "Find the next available free time slot for a 1-hour meeting"
                      )
                    }
                    disabled={calendarDataLoading}
                  >
                    ⏰ Find Free Time
                  </button>
                </div>
              </div>
            </div>

            {/* Chat with Calendar Agent */}
            <div
              style={{
                marginTop: "2rem",
                padding: "1.5rem",
                background: "#f8f9ff",
                borderRadius: "10px",
                border: "2px solid #e0e0e0",
              }}
            >
              <h3>💬 Chat with Calendar Agent</h3>
              <p style={{ color: "#666", marginBottom: "1rem" }}>
                Use the chat interface to manage your calendar and emails. Ask
                about events, schedule meetings, check emails, and more!
              </p>
              <button
                className="primary-btn"
                onClick={() => navigateToAgent("calendar")}
              >
                Go to Chat
              </button>
            </div>
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
              <h3>Create New Workflow or Use Template</h3>

              {/* Template Selection */}
              <div style={{ marginBottom: "1.5rem" }}>
                <label
                  style={{
                    display: "block",
                    marginBottom: "0.5rem",
                    fontWeight: "bold",
                  }}
                >
                  Quick Start - Select Template:
                </label>
                <div className="templates-grid">
                  {templates.map((template) => (
                    <div key={template.id} className="template-card">
                      <h4>{template.name}</h4>
                      <p>{template.description}</p>
                      <small>📋 {template.tasks} tasks</small>
                      <button
                        onClick={() => createFromTemplate(template.id)}
                        disabled={loading}
                        className="primary-btn"
                        style={{ width: "100%" }}
                      >
                        {loading ? "Creating..." : "✨ Use Template"}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Manual Creation */}
              <hr style={{ margin: "2rem 0", borderColor: "#ccc" }} />

              <h4>Or Create From Scratch</h4>
              <p style={{ color: "#666", fontSize: "0.9rem" }}>
                💡 Tip: Create a workflow here, then open it in the Visual
                Builder to add tasks with a visual interface.
              </p>

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
                  style={{ width: "100%" }}
                >
                  📝 Create & Open in Builder
                </button>
              </form>
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
                          onClick={() =>
                            openWorkflowInVisualBuilder(workflow.workflow_id)
                          }
                          className="secondary-btn"
                        >
                          🎨 View Builder
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
