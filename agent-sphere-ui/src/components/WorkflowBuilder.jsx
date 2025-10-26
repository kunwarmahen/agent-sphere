import React, { useState, useCallback, useRef, useEffect } from "react";

const WorkflowBuilder = ({ initialWorkflow }) => {
  const [nodes, setNodes] = useState(initialWorkflow?.nodes || []);
  const [connections, setConnections] = useState(
    initialWorkflow?.connections || []
  );
  const [workflowName, setWorkflowName] = useState(
    initialWorkflow?.name || "New Workflow"
  );
  const [selectedNode, setSelectedNode] = useState(null);
  const [draggingNode, setDraggingNode] = useState(null);
  const [connecting, setConnecting] = useState(null);
  const [showNodeMenu, setShowNodeMenu] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  const [executing, setExecuting] = useState(false);
  const [executionResults, setExecutionResults] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [showCodeModal, setShowCodeModal] = useState(false);
  const [generatedCode, setGeneratedCode] = useState("");
  const [executionPath, setExecutionPath] = useState([]);
  const [executedNodes, setExecutedNodes] = useState(new Set());
  const [executedConnections, setExecutedConnections] = useState(new Set());
  const [canvasSize, setCanvasSize] = useState({ width: 2000, height: 1500 });
  const [viewBox, setViewBox] = useState("0 0 2000 1500");

  const canvasRef = useRef(null);

  const API_URL = "http://localhost:5000/api";

  const nodeTypes = [
    { type: "start", icon: "▶️", label: "Start", color: "#4caf50" },
    { type: "agent", icon: "🤖", label: "Agent Task", color: "#2196f3" },
    { type: "condition", icon: "❓", label: "Condition", color: "#ff9800" },
    { type: "branch", icon: "🔀", label: "Branch", color: "#9c27b0" },
    { type: "end", icon: "⹹️", label: "End", color: "#f44336" },
  ];

  const agents = ["home", "calendar", "finance"];
  const operators = [
    "contains",
    "equals",
    "greater_than",
    "less_than",
    "not_contains",
  ];

  // Calculate canvas bounds based on nodes
  const calculateCanvasBounds = (nodesList) => {
    if (nodesList.length === 0) {
      return { minX: 0, minY: 0, maxX: 2000, maxY: 1500 };
    }

    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    nodesList.forEach((node) => {
      const x = node.position.x;
      const y = node.position.y;
      const nodeWidth = 150;
      const nodeHeight = 80;

      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x + nodeWidth);
      maxY = Math.max(maxY, y + nodeHeight);
    });

    const padding = 200;
    return {
      minX: Math.max(0, minX - padding),
      minY: Math.max(0, minY - padding),
      maxX: maxX + padding,
      maxY: maxY + padding,
    };
  };

  // Update canvas size when nodes change
  const updateCanvasSize = (nodesList) => {
    const bounds = calculateCanvasBounds(nodesList);
    const width = Math.max(2000, bounds.maxX - bounds.minX + 100);
    const height = Math.max(1500, bounds.maxY - bounds.minY + 100);

    setCanvasSize({ width, height });
    setViewBox(`${bounds.minX - 50} ${bounds.minY - 50} ${width} ${height}`);
  };

  // Fit workflow to view
  const fitToView = () => {
    if (nodes.length === 0) return;

    const bounds = calculateCanvasBounds(nodes);
    const padding = 100;

    if (canvasRef.current) {
      const width = canvasRef.current.clientWidth;
      const height = canvasRef.current.clientHeight;
      const graphWidth = bounds.maxX - bounds.minX + padding * 2;
      const graphHeight = bounds.maxY - bounds.minY + padding * 2;

      const zoomX = width / graphWidth;
      const zoomY = height / graphHeight;
      const newZoom = Math.min(zoomX, zoomY, 1.5); // Max zoom 1.5 instead of 2

      setZoom(newZoom);
      setPan({
        x:
          (width - (bounds.maxX - bounds.minX) * newZoom) / 2 -
          bounds.minX * newZoom,
        y:
          (height - (bounds.maxY - bounds.minY) * newZoom) / 2 -
          bounds.minY * newZoom,
      });
    }
  };

  // Update canvas size when nodes change
  useEffect(() => {
    updateCanvasSize(nodes);
  }, [nodes]);

  const addNode = (type, position) => {
    const newNode = {
      id: `node_${Date.now()}`,
      type,
      position: position || { x: 100, y: 100 },
      data: {
        label: type === "start" ? "Start" : type === "end" ? "End" : "New Node",
        agent: type === "agent" ? "home" : null,
        request: "",
        condition:
          type === "condition"
            ? { field: "result", operator: "contains", value: "" }
            : null,
        branches: type === "branch" ? [] : null,
      },
    };
    setNodes([...nodes, newNode]);
    setShowNodeMenu(false);
  };

  const showNotification = (message, type = "info") => {
    const id = Date.now();
    setNotifications((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 3000);
  };

  const updateNode = (nodeId, updates) => {
    setNodes(
      nodes.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...updates } }
          : node
      )
    );
  };

  const deleteNode = (nodeId) => {
    setNodes(nodes.filter((node) => node.id !== nodeId));
    setConnections(
      connections.filter((conn) => conn.from !== nodeId && conn.to !== nodeId)
    );
    if (selectedNode?.id === nodeId) setSelectedNode(null);
  };

  const addConnection = (from, to, label = "") => {
    const newConnection = {
      id: `conn_${Date.now()}`,
      from,
      to,
      label,
    };
    setConnections([...connections, newConnection]);
    setConnecting(null);
  };

  const deleteConnection = (connId) => {
    setConnections(connections.filter((conn) => conn.id !== connId));
  };

  const handleCanvasClick = (e) => {
    if (e.target === canvasRef.current) {
      setSelectedNode(null);
      if (showNodeMenu) setShowNodeMenu(false);
    }
  };

  const handleCanvasRightClick = (e) => {
    e.preventDefault();
    const rect = canvasRef.current.getBoundingClientRect();
    setMenuPosition({
      x: (e.clientX - rect.left - pan.x) / zoom,
      y: (e.clientY - rect.top - pan.y) / zoom,
    });
    setShowNodeMenu(true);
  };

  const handleNodeDragStart = (e, nodeId) => {
    e.stopPropagation();
    setDraggingNode(nodeId);
  };

  const handleNodeDrag = useCallback(
    (e) => {
      if (!draggingNode || !canvasRef.current) return;

      const rect = canvasRef.current.getBoundingClientRect();
      const scrollX = canvasRef.current.scrollLeft || 0;
      const scrollY = canvasRef.current.scrollTop || 0;

      const x = (e.clientX - rect.left + scrollX) / zoom - pan.x / zoom;
      const y = (e.clientY - rect.top + scrollY) / zoom - pan.y / zoom;

      setNodes((nodes) =>
        nodes.map((node) =>
          node.id === draggingNode
            ? { ...node, position: { x: x - 75, y: y - 40 } }
            : node
        )
      );
    },
    [draggingNode, zoom, pan]
  );

  const handleNodeDragEnd = () => {
    setDraggingNode(null);
  };

  const handleConnectStart = (nodeId) => {
    setConnecting({ from: nodeId });
  };

  const handleConnectEnd = (nodeId) => {
    if (connecting && connecting.from !== nodeId) {
      addConnection(connecting.from, nodeId);
    }
    setConnecting(null);
  };

  const exportWorkflow = () => {
    const workflow = {
      name: workflowName,
      nodes,
      connections,
    };
    const blob = new Blob([JSON.stringify(workflow, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${workflowName.replace(/\s+/g, "_")}.json`;
    a.click();
  };

  const importWorkflow = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const workflow = JSON.parse(e.target.result);
        setWorkflowName(workflow.name || "Imported Workflow");
        setNodes(workflow.nodes || []);
        setConnections(workflow.connections || []);
        setSelectedNode(null);
        showNotification("Workflow imported successfully!", "success");
      } catch (error) {
        showNotification(
          "Error importing workflow: Invalid JSON file",
          "error"
        );
        console.error("Import error:", error);
      }
    };
    reader.readAsText(file);
    event.target.value = "";
  };

  const loadExample = () => {
    const exampleWorkflow = {
      name: "Smart Morning Routine",
      nodes: [
        {
          id: "node_start",
          type: "start",
          position: { x: 250, y: 50 },
          data: { label: "Start" },
        },
        {
          id: "node_check_calendar",
          type: "agent",
          position: { x: 250, y: 150 },
          data: {
            label: "Check Calendar",
            agent: "calendar",
            request: "Do I have any meetings in the next 2 hours?",
          },
        },
        {
          id: "node_condition",
          type: "condition",
          position: { x: 250, y: 280 },
          data: {
            label: "Has Meeting?",
            condition: {
              field: "result",
              operator: "contains",
              value: "meeting",
            },
          },
        },
        {
          id: "node_busy_path",
          type: "agent",
          position: { x: 100, y: 420 },
          data: {
            label: "Prepare Office",
            agent: "home",
            request:
              "Turn on office lights to 100% brightness and set temperature to 70 degrees",
          },
        },
        {
          id: "node_relaxed_path",
          type: "agent",
          position: { x: 400, y: 420 },
          data: {
            label: "Relaxed Morning",
            agent: "home",
            request: "Turn on lights to 60% brightness and play relaxing music",
          },
        },
        {
          id: "node_coffee",
          type: "agent",
          position: { x: 250, y: 560 },
          data: {
            label: "Make Coffee",
            agent: "home",
            request: "Start the coffee maker",
          },
        },
        {
          id: "node_end",
          type: "end",
          position: { x: 250, y: 680 },
          data: { label: "End" },
        },
      ],
      connections: [
        {
          id: "conn_1",
          from: "node_start",
          to: "node_check_calendar",
          label: "",
        },
        {
          id: "conn_2",
          from: "node_check_calendar",
          to: "node_condition",
          label: "",
        },
        {
          id: "conn_3",
          from: "node_condition",
          to: "node_busy_path",
          label: "Yes - Has Meeting",
        },
        {
          id: "conn_4",
          from: "node_condition",
          to: "node_relaxed_path",
          label: "No - Free Time",
        },
        { id: "conn_5", from: "node_busy_path", to: "node_coffee", label: "" },
        {
          id: "conn_6",
          from: "node_relaxed_path",
          to: "node_coffee",
          label: "",
        },
        { id: "conn_7", from: "node_coffee", to: "node_end", label: "" },
      ],
    };

    setWorkflowName(exampleWorkflow.name);
    setNodes(exampleWorkflow.nodes);
    setConnections(exampleWorkflow.connections);
    setSelectedNode(null);
    showNotification("Example workflow loaded!", "success");
  };

  const clearWorkflow = () => {
    if (window.confirm("Are you sure you want to clear the entire workflow?")) {
      setNodes([]);
      setConnections([]);
      setSelectedNode(null);
      setWorkflowName("New Workflow");
      clearExecutionPath();
    }
  };

  const generateCode = () => {
    let code = `from workflow_engine import WorkflowEngine, WorkflowTask, Branch, Condition, ConditionOperator\n\n`;
    code += `# Create workflow\n`;
    code += `engine = WorkflowEngine()\n`;
    code += `workflow = engine.create_workflow("${workflowName.replace(
      /\s+/g,
      "_"
    )}", "${workflowName}")\n\n`;

    nodes.forEach((node) => {
      if (node.type === "agent") {
        code += `${node.id} = WorkflowTask(\n`;
        code += `    "${node.id}",\n`;
        code += `    "${node.data.agent}",\n`;
        code += `    "${node.data.request}"\n`;
        code += `)\n\n`;
      }
    });

    connections.forEach((conn) => {
      const fromNode = nodes.find((n) => n.id === conn.from);
      const toNode = nodes.find((n) => n.id === conn.to);
      if (fromNode && toNode) {
        code += `${fromNode.id}.next_task_id = "${toNode.id}"\n`;
      }
    });

    return code;
  };

  const convertToBackendWorkflow = () => {
    const workflow = {
      workflow_id: workflowName.replace(/\s+/g, "_").toLowerCase(),
      name: workflowName,
      description: `Visual workflow with ${nodes.length} nodes`,
      tasks: [],
    };

    const startNode = nodes.find((n) => n.type === "start");
    if (!startNode) {
      throw new Error("Workflow must have a start node");
    }

    const firstConn = connections.find((c) => c.from === startNode.id);
    if (!firstConn) {
      throw new Error("Start node must be connected to another node");
    }

    const visited = new Set();
    let currentNodeId = firstConn.to;
    const taskMap = {};

    // First pass: collect all agent nodes
    while (currentNodeId && !visited.has(currentNodeId)) {
      visited.add(currentNodeId);

      const node = nodes.find((n) => n.id === currentNodeId);
      if (!node || node.type === "end") break;

      if (node.type === "agent") {
        taskMap[currentNodeId] = {
          task_id: node.id,
          agent_name: node.data.agent || "home",
          request: node.data.request || "No request specified",
          retry_count: 1,
          on_failure: "stop",
          next_task_id: null,
        };
      }

      const nextConn = connections.find((c) => c.from === currentNodeId);
      currentNodeId = nextConn ? nextConn.to : null;
    }

    // Second pass: link tasks
    visited.clear();
    currentNodeId = firstConn.to;
    let previousTaskId = null;

    while (currentNodeId && !visited.has(currentNodeId)) {
      visited.add(currentNodeId);

      const node = nodes.find((n) => n.id === currentNodeId);
      if (!node || node.type === "end") break;

      if (node.type === "agent") {
        const currentTask = taskMap[currentNodeId];

        if (previousTaskId && taskMap[previousTaskId]) {
          taskMap[previousTaskId].next_task_id = currentTask.task_id;
        }

        previousTaskId = currentNodeId;
        workflow.tasks.push(currentTask);
      } else if (node.type === "condition") {
        const branches = connections.filter((c) => c.from === currentNodeId);
        if (branches.length > 0) {
          currentNodeId = branches[0].to;
          continue;
        }
      }

      const nextConn = connections.find((c) => c.from === currentNodeId);
      currentNodeId = nextConn ? nextConn.to : null;
    }

    if (workflow.tasks.length > 0) {
      workflow.start_task_id = workflow.tasks[0].task_id;
    }

    return workflow;
  };

  const clearExecutionPath = () => {
    setExecutedNodes(new Set());
    setExecutedConnections(new Set());
    setExecutionPath([]);
    setExecutionResults(null);
    setShowResults(false);
  };

  const executeWorkflow = async () => {
    try {
      setExecuting(true);
      setExecutionResults(null);
      setExecutedNodes(new Set());
      setExecutedConnections(new Set());
      setExecutionPath([]);

      if (nodes.length === 0) {
        showNotification(
          "Cannot execute empty workflow. Add some nodes first!",
          "error"
        );
        return;
      }

      const hasStart = nodes.some((n) => n.type === "start");
      if (!hasStart) {
        showNotification("Workflow must have a Start node", "error");
        return;
      }

      const hasAgentTask = nodes.some((n) => n.type === "agent");
      if (!hasAgentTask) {
        showNotification("Workflow must have at least one Agent Task", "error");
        return;
      }

      const workflowData = convertToBackendWorkflow();

      const createResponse = await fetch(`${API_URL}/workflows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workflow_id: workflowData.workflow_id,
          name: workflowData.name,
          description: workflowData.description,
        }),
      });

      if (!createResponse.ok) {
        throw new Error("Failed to create workflow on server");
      }

      for (const task of workflowData.tasks) {
        const taskPayload = {
          task_id: task.task_id,
          agent_name: task.agent_name,
          request: task.request,
          retry_count: task.retry_count,
          on_failure: task.on_failure,
        };

        if (task.next_task_id) {
          taskPayload.next_task_id = task.next_task_id;
        }

        const addResponse = await fetch(
          `${API_URL}/workflows/${workflowData.workflow_id}/tasks`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(taskPayload),
          }
        );

        if (!addResponse.ok) {
          throw new Error(`Failed to add task ${task.task_id}`);
        }
      }

      const executeResponse = await fetch(
        `${API_URL}/workflows/${workflowData.workflow_id}/execute`,
        {
          method: "POST",
        }
      );

      const result = await executeResponse.json();
      setExecutionResults(result);
      setShowResults(true);

      if (result.execution_path && result.execution_path.length > 0) {
        const pathSet = new Set(result.execution_path);
        setExecutedNodes(pathSet);
        setExecutionPath(result.execution_path);

        const connSet = new Set();
        for (let i = 0; i < result.execution_path.length - 1; i++) {
          const fromId = result.execution_path[i];
          const toId = result.execution_path[i + 1];
          const conn = connections.find(
            (c) => c.from === fromId && c.to === toId
          );
          if (conn) {
            connSet.add(conn.id);
          }
        }
        setExecutedConnections(connSet);

        for (let i = 0; i < result.execution_path.length; i++) {
          await new Promise((resolve) => setTimeout(resolve, 800));
        }
      }

      showNotification("Workflow executed successfully!", "success");
    } catch (error) {
      console.error("Execution error:", error);
      showNotification(`Execution failed: ${error.message}`, "error");
    } finally {
      setExecuting(false);
    }
  };

  const saveWorkflowToServer = async () => {
    try {
      const workflowData = convertToBackendWorkflow();

      const response = await fetch(`${API_URL}/workflows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workflow_id: workflowData.workflow_id,
          name: workflowData.name,
          description: workflowData.description,
        }),
      });

      if (response.ok) {
        for (const task of workflowData.tasks) {
          const taskPayload = {
            task_id: task.task_id,
            agent_name: task.agent_name,
            request: task.request,
            retry_count: task.retry_count,
            on_failure: task.on_failure,
          };

          if (task.next_task_id) {
            taskPayload.next_task_id = task.next_task_id;
          }

          const addResponse = await fetch(
            `${API_URL}/workflows/${workflowData.workflow_id}/tasks`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(taskPayload),
            }
          );

          if (!addResponse.ok) {
            throw new Error(`Failed to add task ${task.task_id}`);
          }
        }
        showNotification("Workflow saved to server successfully!", "success");
      } else {
        showNotification("Failed to save workflow to server", "error");
      }
    } catch (error) {
      console.error("Save error:", error);
      showNotification(`Save failed: ${error.message}`, "error");
    }
  };

  useEffect(() => {
    if (draggingNode) {
      window.addEventListener("mousemove", handleNodeDrag);
      window.addEventListener("mouseup", handleNodeDragEnd);
      return () => {
        window.removeEventListener("mousemove", handleNodeDrag);
        window.removeEventListener("mouseup", handleNodeDragEnd);
      };
    }
  }, [draggingNode, handleNodeDrag]);

  const getNodeCenter = (node) => ({
    x: node.position.x + 75,
    y: node.position.y + 40,
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "#1e1e2e",
        color: "#fff",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Toolbar */}
      <div
        style={{
          padding: "1rem",
          background: "#2d3561",
          borderBottom: "2px solid #3d4577",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1rem",
          overflowX: "auto",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            minWidth: "300px",
          }}
        >
          <h2 style={{ margin: 0, fontSize: "1.5rem", whiteSpace: "nowrap" }}>
            🎨 Visual Workflow Builder
          </h2>
          <input
            type="text"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            style={{
              padding: "0.5rem",
              background: "#1e1e2e",
              border: "1px solid #667eea",
              borderRadius: "4px",
              color: "#fff",
              fontSize: "1rem",
            }}
          />
        </div>

        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {nodeTypes.map((nodeType) => (
            <button
              key={nodeType.type}
              onClick={() =>
                addNode(nodeType.type, { x: 100 + nodes.length * 50, y: 100 })
              }
              style={{
                padding: "0.5rem 1rem",
                background: nodeType.color,
                border: "none",
                borderRadius: "4px",
                color: "#fff",
                cursor: "pointer",
                fontSize: "0.9rem",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                whiteSpace: "nowrap",
              }}
            >
              <span>{nodeType.icon}</span>
              <span>{nodeType.label}</span>
            </button>
          ))}
        </div>

        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <button
            onClick={() => setZoom((z) => Math.max(0.5, z - 0.1))}
            style={{
              padding: "0.5rem 1rem",
              background: "#667eea",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            🔍−
          </button>
          <button
            onClick={() => setZoom((z) => Math.min(2, z + 0.1))}
            style={{
              padding: "0.5rem 1rem",
              background: "#667eea",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            🔍+
          </button>
          <button
            onClick={fitToView}
            style={{
              padding: "0.5rem 1rem",
              background: "#00bcd4",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              fontWeight: "bold",
              whiteSpace: "nowrap",
            }}
          >
            🎯 Fit to View
          </button>
          <label
            style={{
              padding: "0.5rem 1rem",
              background: "#2196f3",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              whiteSpace: "nowrap",
            }}
          >
            📂 Import
            <input
              type="file"
              accept=".json"
              onChange={importWorkflow}
              style={{ display: "none" }}
            />
          </label>
          <button
            onClick={exportWorkflow}
            style={{
              padding: "0.5rem 1rem",
              background: "#4caf50",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            💾 Export
          </button>
          <button
            onClick={loadExample}
            style={{
              padding: "0.5rem 1rem",
              background: "#9c27b0",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            ✨ Example
          </button>
          <button
            onClick={saveWorkflowToServer}
            style={{
              padding: "0.5rem 1rem",
              background: "#00bcd4",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            💾 Save to Server
          </button>
          <button
            onClick={executeWorkflow}
            disabled={executing}
            style={{
              padding: "0.5rem 1rem",
              background: executing ? "#999" : "#4caf50",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: executing ? "not-allowed" : "pointer",
              fontWeight: "bold",
              whiteSpace: "nowrap",
            }}
          >
            {executing ? "⏳ Executing..." : "▶️ Execute"}
          </button>
          <button
            onClick={() => {
              setShowCodeModal(true);
              setGeneratedCode(generateCode());
            }}
            style={{
              padding: "0.5rem 1rem",
              background: "#ff9800",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            💻 Code
          </button>
          <button
            onClick={clearWorkflow}
            style={{
              padding: "0.5rem 1rem",
              background: "#f44336",
              border: "none",
              borderRadius: "4px",
              color: "#fff",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      {/* Execution Results Modal */}
      {showResults && executionResults && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.7)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 2000,
          }}
        >
          <div
            style={{
              background: "#2d3561",
              borderRadius: "12px",
              padding: "2rem",
              maxWidth: "600px",
              maxHeight: "80vh",
              overflow: "auto",
              boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "1.5rem",
              }}
            >
              <h2 style={{ margin: 0, color: "#fff" }}>
                {executionResults.success
                  ? "✅ Execution Successful"
                  : "❌ Execution Failed"}
              </h2>
              <button
                onClick={() => setShowResults(false)}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "#fff",
                  fontSize: "1.5rem",
                  cursor: "pointer",
                }}
              >
                ✕
              </button>
            </div>

            <div style={{ color: "#fff" }}>
              <div style={{ marginBottom: "1rem" }}>
                <strong>Status:</strong> {executionResults.status}
              </div>
              <div style={{ marginBottom: "1rem" }}>
                <strong>Duration:</strong>{" "}
                {executionResults.duration_seconds?.toFixed(2)}s
              </div>
              {executionResults.execution_path && (
                <div style={{ marginBottom: "1rem" }}>
                  <strong>Execution Path:</strong>
                  <div
                    style={{
                      background: "#1e1e2e",
                      padding: "1rem",
                      borderRadius: "8px",
                      marginTop: "0.5rem",
                      fontFamily: "monospace",
                    }}
                  >
                    {executionResults.execution_path.join(" → ")}
                  </div>
                </div>
              )}
              {executionResults.results && (
                <div>
                  <strong>Task Results:</strong>
                  <div
                    style={{
                      background: "#1e1e2e",
                      padding: "1rem",
                      borderRadius: "8px",
                      marginTop: "0.5rem",
                      maxHeight: "300px",
                      overflow: "auto",
                    }}
                  >
                    {executionResults.results.map((result, idx) => (
                      <div
                        key={idx}
                        style={{
                          marginBottom: "1rem",
                          paddingBottom: "1rem",
                          borderBottom:
                            idx < executionResults.results.length - 1
                              ? "1px solid #3d4577"
                              : "none",
                        }}
                      >
                        <div
                          style={{
                            color: "#4caf50",
                            marginBottom: "0.5rem",
                            fontWeight: "bold",
                          }}
                        >
                          ✓ Task: {result.task_id}
                        </div>
                        <div style={{ fontSize: "0.9rem", color: "#aaa" }}>
                          Status: {result.status}
                        </div>
                        {result.result && (
                          <div
                            style={{
                              fontSize: "0.9rem",
                              color: "#ccc",
                              marginTop: "0.5rem",
                            }}
                          >
                            Result:{" "}
                            {typeof result.result === "string"
                              ? result.result
                              : JSON.stringify(result.result)}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
              <button
                onClick={() => setShowResults(false)}
                style={{
                  flex: 1,
                  padding: "0.75rem 1.5rem",
                  background: "#667eea",
                  border: "none",
                  borderRadius: "8px",
                  color: "#fff",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
              >
                Close
              </button>
              <button
                onClick={clearExecutionPath}
                style={{
                  flex: 1,
                  padding: "0.75rem 1.5rem",
                  background: "#ff9800",
                  border: "none",
                  borderRadius: "8px",
                  color: "#fff",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
              >
                Clear Highlights
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Code Modal */}
      {showCodeModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.7)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 2000,
          }}
        >
          <div
            style={{
              background: "#2d3561",
              borderRadius: "12px",
              padding: "2rem",
              maxWidth: "800px",
              width: "90%",
              maxHeight: "80vh",
              overflow: "auto",
              boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
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
              <h2 style={{ margin: 0, color: "#fff" }}>
                Generated Python Code
              </h2>
              <button
                onClick={() => setShowCodeModal(false)}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "#fff",
                  fontSize: "1.5rem",
                  cursor: "pointer",
                }}
              >
                ✕
              </button>
            </div>

            <pre
              style={{
                background: "#1e1e2e",
                padding: "1.5rem",
                borderRadius: "8px",
                color: "#fff",
                overflow: "auto",
                maxHeight: "500px",
                fontFamily: "monospace",
                fontSize: "0.9rem",
                lineHeight: "1.5",
              }}
            >
              <code>{generatedCode}</code>
            </pre>

            <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(generatedCode);
                  showNotification("Code copied to clipboard!", "success");
                }}
                style={{
                  flex: 1,
                  padding: "0.75rem",
                  background: "#4caf50",
                  border: "none",
                  borderRadius: "8px",
                  color: "#fff",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
              >
                📋 Copy to Clipboard
              </button>
              <button
                onClick={() => setShowCodeModal(false)}
                style={{
                  flex: 1,
                  padding: "0.75rem",
                  background: "#667eea",
                  border: "none",
                  borderRadius: "8px",
                  color: "#fff",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Notifications */}
      {notifications.length > 0 && (
        <div
          style={{
            position: "fixed",
            top: "80px",
            right: "20px",
            zIndex: 3000,
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
          }}
        >
          {notifications.map((notif) => (
            <div
              key={notif.id}
              style={{
                padding: "1rem",
                background:
                  notif.type === "success"
                    ? "#4caf50"
                    : notif.type === "error"
                    ? "#f44336"
                    : "#2196f3",
                color: "#fff",
                borderRadius: "8px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                minWidth: "250px",
                animation: "slideIn 0.3s ease",
              }}
            >
              {notif.message}
            </div>
          ))}
        </div>
      )}

      {/* Main Canvas Area */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Canvas */}
        <div
          ref={canvasRef}
          onClick={handleCanvasClick}
          onContextMenu={handleCanvasRightClick}
          style={{
            flex: 1,
            position: "relative",
            background: `
              linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px),
              linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px)
            `,
            backgroundSize: `${20 * zoom}px ${20 * zoom}px`,
            backgroundPosition: `${pan.x}px ${pan.y}px`,
            cursor: draggingNode ? "grabbing" : "default",
            overflow: "auto",
            width: "100%",
            height: "100%",
          }}
        >
          <svg
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: `${canvasSize.width}px`,
              height: `${canvasSize.height}px`,
              pointerEvents: "none",
              minWidth: "100%",
              minHeight: "100%",
            }}
          >
            {connections.map((conn) => {
              const fromNode = nodes.find((n) => n.id === conn.from);
              const toNode = nodes.find((n) => n.id === conn.to);
              if (!fromNode || !toNode) return null;

              const from = getNodeCenter(fromNode);
              const to = getNodeCenter(toNode);
              const fromX = from.x * zoom + pan.x;
              const fromY = from.y * zoom + pan.y;
              const toX = to.x * zoom + pan.x;
              const toY = to.y * zoom + pan.y;

              const isExecuted = executedConnections.has(conn.id);

              return (
                <g key={conn.id}>
                  <line
                    x1={fromX}
                    y1={fromY}
                    x2={toX}
                    y2={toY}
                    stroke={isExecuted ? "#4caf50" : "#667eea"}
                    strokeWidth={isExecuted ? "3" : "2"}
                    markerEnd={
                      isExecuted ? "url(#arrowhead-green)" : "url(#arrowhead)"
                    }
                    style={{
                      transition: "all 0.3s ease",
                      filter: isExecuted
                        ? "drop-shadow(0 0 8px rgba(76, 175, 80, 0.8))"
                        : "none",
                    }}
                  />
                  {conn.label && (
                    <text
                      x={(fromX + toX) / 2}
                      y={(fromY + toY) / 2}
                      fill="#fff"
                      fontSize="12"
                      textAnchor="middle"
                      style={{
                        background: "#2d3561",
                        padding: "2px 4px",
                      }}
                    >
                      {conn.label}
                    </text>
                  )}
                </g>
              );
            })}
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="10"
                refX="9"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 10 3, 0 6" fill="#667eea" />
              </marker>
              <marker
                id="arrowhead-green"
                markerWidth="10"
                markerHeight="10"
                refX="9"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 10 3, 0 6" fill="#4caf50" />
              </marker>
            </defs>
          </svg>

          {nodes.map((node) => {
            const nodeType = nodeTypes.find((t) => t.type === node.type);
            const isExecuted = executedNodes.has(node.id);

            return (
              <div
                key={node.id}
                onMouseDown={(e) => handleNodeDragStart(e, node.id)}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedNode(node);
                }}
                style={{
                  position: "absolute",
                  left: `${node.position.x * zoom + pan.x}px`,
                  top: `${node.position.y * zoom + pan.y}px`,
                  width: "150px",
                  padding: "1rem",
                  background: isExecuted
                    ? "#1a5f1a"
                    : selectedNode?.id === node.id
                    ? "#3d4577"
                    : "#2d3561",
                  border: isExecuted
                    ? "3px solid #4caf50"
                    : `2px solid ${nodeType?.color || "#667eea"}`,
                  borderRadius: "8px",
                  cursor: draggingNode === node.id ? "grabbing" : "grab",
                  boxShadow: isExecuted
                    ? "0 0 15px rgba(76, 175, 80, 0.6), 0 4px 12px rgba(0,0,0,0.3)"
                    : "0 4px 12px rgba(0,0,0,0.3)",
                  transition:
                    draggingNode === node.id ? "none" : "all 0.3s ease",
                  zIndex: selectedNode?.id === node.id ? 100 : 10,
                  transformOrigin: "top left",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: "0.5rem",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                    }}
                  >
                    <span style={{ fontSize: "1.2rem" }}>{nodeType?.icon}</span>
                    <strong style={{ fontSize: "0.9rem" }}>
                      {node.data.label}
                    </strong>
                  </div>
                  {isExecuted && (
                    <span style={{ fontSize: "1rem", color: "#4caf50" }}>
                      ✓
                    </span>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteNode(node.id);
                    }}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "#f44336",
                      cursor: "pointer",
                      fontSize: "1rem",
                    }}
                  >
                    ✕
                  </button>
                </div>

                {node.type === "agent" && (
                  <div style={{ fontSize: "0.8rem", color: "#aaa" }}>
                    Agent: {node.data.agent}
                  </div>
                )}

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginTop: "0.5rem",
                  }}
                >
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleConnectStart(node.id);
                    }}
                    style={{
                      padding: "0.25rem 0.5rem",
                      background: "#667eea",
                      border: "none",
                      borderRadius: "4px",
                      color: "#fff",
                      cursor: "pointer",
                      fontSize: "0.75rem",
                    }}
                  >
                    ➡️ Connect
                  </button>
                  {connecting && connecting.from !== node.id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleConnectEnd(node.id);
                      }}
                      style={{
                        padding: "0.25rem 0.5rem",
                        background: "#4caf50",
                        border: "none",
                        borderRadius: "4px",
                        color: "#fff",
                        cursor: "pointer",
                        fontSize: "0.75rem",
                      }}
                    >
                      ✓ Link Here
                    </button>
                  )}
                </div>
              </div>
            );
          })}

          {showNodeMenu && (
            <div
              style={{
                position: "absolute",
                left: menuPosition.x * zoom + pan.x,
                top: menuPosition.y * zoom + pan.y,
                background: "#2d3561",
                border: "2px solid #667eea",
                borderRadius: "8px",
                padding: "0.5rem",
                boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
                zIndex: 1000,
              }}
            >
              <div
                style={{
                  marginBottom: "0.5rem",
                  fontWeight: "bold",
                  fontSize: "0.9rem",
                }}
              >
                Add Node
              </div>
              {nodeTypes.map((nodeType) => (
                <button
                  key={nodeType.type}
                  onClick={() => addNode(nodeType.type, menuPosition)}
                  style={{
                    display: "block",
                    width: "100%",
                    padding: "0.5rem",
                    margin: "0.25rem 0",
                    background: nodeType.color,
                    border: "none",
                    borderRadius: "4px",
                    color: "#fff",
                    cursor: "pointer",
                    textAlign: "left",
                  }}
                >
                  {nodeType.icon} {nodeType.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Properties Panel */}
        {selectedNode && (
          <div
            style={{
              width: "300px",
              background: "#2d3561",
              borderLeft: "2px solid #3d4577",
              padding: "1rem",
              overflowY: "auto",
            }}
          >
            <h3 style={{ marginTop: 0 }}>Node Properties</h3>

            <div style={{ marginBottom: "1rem" }}>
              <label
                style={{
                  display: "block",
                  marginBottom: "0.5rem",
                  fontSize: "0.9rem",
                }}
              >
                Label
              </label>
              <input
                type="text"
                value={selectedNode.data.label}
                onChange={(e) => {
                  updateNode(selectedNode.id, { label: e.target.value });
                  setSelectedNode({
                    ...selectedNode,
                    data: { ...selectedNode.data, label: e.target.value },
                  });
                }}
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  background: "#1e1e2e",
                  border: "1px solid #667eea",
                  borderRadius: "4px",
                  color: "#fff",
                }}
              />
            </div>

            {selectedNode.type === "agent" && (
              <>
                <div style={{ marginBottom: "1rem" }}>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "0.5rem",
                      fontSize: "0.9rem",
                    }}
                  >
                    Agent
                  </label>
                  <select
                    value={selectedNode.data.agent}
                    onChange={(e) => {
                      updateNode(selectedNode.id, { agent: e.target.value });
                      setSelectedNode({
                        ...selectedNode,
                        data: { ...selectedNode.data, agent: e.target.value },
                      });
                    }}
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      background: "#1e1e2e",
                      border: "1px solid #667eea",
                      borderRadius: "4px",
                      color: "#fff",
                    }}
                  >
                    {agents.map((agent) => (
                      <option key={agent} value={agent}>
                        {agent}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ marginBottom: "1rem" }}>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "0.5rem",
                      fontSize: "0.9rem",
                    }}
                  >
                    Request
                  </label>
                  <textarea
                    value={selectedNode.data.request}
                    onChange={(e) => {
                      updateNode(selectedNode.id, { request: e.target.value });
                      setSelectedNode({
                        ...selectedNode,
                        data: {
                          ...selectedNode.data,
                          request: e.target.value,
                        },
                      });
                    }}
                    rows="4"
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      background: "#1e1e2e",
                      border: "1px solid #667eea",
                      borderRadius: "4px",
                      color: "#fff",
                      resize: "vertical",
                    }}
                    placeholder="Enter the request for the agent..."
                  />
                </div>
              </>
            )}

            {selectedNode.type === "condition" && (
              <>
                <div style={{ marginBottom: "1rem" }}>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "0.5rem",
                      fontSize: "0.9rem",
                    }}
                  >
                    Field
                  </label>
                  <input
                    type="text"
                    value={selectedNode.data.condition.field}
                    onChange={(e) => {
                      const newCondition = {
                        ...selectedNode.data.condition,
                        field: e.target.value,
                      };
                      updateNode(selectedNode.id, { condition: newCondition });
                      setSelectedNode({
                        ...selectedNode,
                        data: {
                          ...selectedNode.data,
                          condition: newCondition,
                        },
                      });
                    }}
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      background: "#1e1e2e",
                      border: "1px solid #667eea",
                      borderRadius: "4px",
                      color: "#fff",
                    }}
                  />
                </div>

                <div style={{ marginBottom: "1rem" }}>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "0.5rem",
                      fontSize: "0.9rem",
                    }}
                  >
                    Operator
                  </label>
                  <select
                    value={selectedNode.data.condition.operator}
                    onChange={(e) => {
                      const newCondition = {
                        ...selectedNode.data.condition,
                        operator: e.target.value,
                      };
                      updateNode(selectedNode.id, { condition: newCondition });
                      setSelectedNode({
                        ...selectedNode,
                        data: {
                          ...selectedNode.data,
                          condition: newCondition,
                        },
                      });
                    }}
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      background: "#1e1e2e",
                      border: "1px solid #667eea",
                      borderRadius: "4px",
                      color: "#fff",
                    }}
                  >
                    {operators.map((op) => (
                      <option key={op} value={op}>
                        {op}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ marginBottom: "1rem" }}>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "0.5rem",
                      fontSize: "0.9rem",
                    }}
                  >
                    Value
                  </label>
                  <input
                    type="text"
                    value={selectedNode.data.condition.value}
                    onChange={(e) => {
                      const newCondition = {
                        ...selectedNode.data.condition,
                        value: e.target.value,
                      };
                      updateNode(selectedNode.id, { condition: newCondition });
                      setSelectedNode({
                        ...selectedNode,
                        data: {
                          ...selectedNode.data,
                          condition: newCondition,
                        },
                      });
                    }}
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      background: "#1e1e2e",
                      border: "1px solid #667eea",
                      borderRadius: "4px",
                      color: "#fff",
                    }}
                  />
                </div>
              </>
            )}

            <div style={{ marginTop: "2rem" }}>
              <button
                onClick={() => deleteNode(selectedNode.id)}
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  background: "#f44336",
                  border: "none",
                  borderRadius: "4px",
                  color: "#fff",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
              >
                🗑️ Delete Node
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowBuilder;
