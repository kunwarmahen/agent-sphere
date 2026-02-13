import React, { useState, useEffect, useCallback } from "react";

const API_URL = "http://localhost:5000/api";

const CATEGORY_COLORS = {
  fact:       "#00cfff",
  preference: "#a855f7",
  context:    "#f0a500",
  summary:    "#00ff9d",
};

const SOURCE_LABELS = {
  manual:  "Manual",
  command: "/remember",
  auto:    "Auto-extracted",
  compact: "Compacted",
};

const IMPORTANCE_STARS = (n) => "★".repeat(n) + "☆".repeat(5 - n);

export default function MemoryManager({ theme, showNotification }) {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("orchestrator");
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ content: "", category: "fact", importance: 3 });
  const [adding, setAdding] = useState(false);
  const [showAdd, setShowAdd] = useState(false);

  const accent = theme === "matrix" ? "#00ff9d" : theme === "cyber" ? "#00cfff" : "#a855f7";
  const cardBg = "rgba(255,255,255,0.04)";
  const border = `1px solid ${accent}22`;

  const fetchAgents = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/memory/agents`);
      const data = await r.json();
      const list = data.agents || [];
      // Always include common agents even if they have no memories yet
      const merged = [...new Set(["orchestrator", "home", "calendar", "finance", ...list])];
      setAgents(merged);
    } catch {
      showNotification?.("Failed to load memory agents", "error");
    }
  }, [showNotification]);

  const fetchMemories = useCallback(async (agentId) => {
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/memory/${agentId}`);
      const data = await r.json();
      setMemories(data.memories || []);
    } catch {
      showNotification?.("Failed to load memories", "error");
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);
  useEffect(() => { fetchMemories(selectedAgent); }, [selectedAgent, fetchMemories]);

  async function addMemory(e) {
    e.preventDefault();
    if (!form.content.trim()) { showNotification?.("Content is required", "error"); return; }
    setAdding(true);
    try {
      const r = await fetch(`${API_URL}/memory/${selectedAgent}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, source: "manual" }),
      });
      const data = await r.json();
      if (data.success) {
        showNotification?.("Memory saved", "success");
        setForm({ content: "", category: "fact", importance: 3 });
        setShowAdd(false);
        fetchMemories(selectedAgent);
      } else {
        showNotification?.(data.error || "Save failed", "error");
      }
    } catch {
      showNotification?.("Request failed", "error");
    } finally {
      setAdding(false);
    }
  }

  async function deleteMemory(memId) {
    try {
      const r = await fetch(`${API_URL}/memory/${selectedAgent}/${memId}`, { method: "DELETE" });
      const data = await r.json();
      if (data.success) {
        setMemories(prev => prev.filter(m => m.id !== memId));
        showNotification?.("Memory deleted", "success");
      }
    } catch {
      showNotification?.("Delete failed", "error");
    }
  }

  async function clearAll() {
    if (!window.confirm(`Clear all memories for "${selectedAgent}"?`)) return;
    try {
      const r = await fetch(`${API_URL}/memory/${selectedAgent}`, { method: "DELETE" });
      const data = await r.json();
      if (data.success) {
        setMemories([]);
        showNotification?.("All memories cleared", "success");
      }
    } catch {
      showNotification?.("Clear failed", "error");
    }
  }

  const inputStyle = {
    width: "100%",
    background: "rgba(255,255,255,0.06)",
    border: `1px solid ${accent}33`,
    borderRadius: "8px",
    color: "#fff",
    padding: "8px 12px",
    fontSize: "0.88rem",
    outline: "none",
    boxSizing: "border-box",
    fontFamily: "monospace",
  };

  const btn = (color = accent) => ({
    padding: "6px 14px",
    borderRadius: "6px",
    border: `1px solid ${color}44`,
    background: `${color}12`,
    color: color,
    cursor: "pointer",
    fontSize: "0.8rem",
    fontWeight: "600",
    transition: "all 0.2s",
  });

  const byCategory = memories.reduce((acc, m) => {
    const cat = m.category || "fact";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(m);
    return acc;
  }, {});

  return (
    <div style={{ padding: "1.5rem", maxWidth: "960px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
        <div>
          <h2 style={{ color: accent, margin: 0, fontSize: "1.6rem" }}>🧩 Long-term Memory</h2>
          <p style={{ color: "#888", margin: "4px 0 0", fontSize: "0.85rem" }}>
            Facts and context agents remember across sessions. Type{" "}
            <code style={{ color: accent, background: `${accent}11`, padding: "1px 6px", borderRadius: "4px" }}>
              /remember &lt;fact&gt;
            </code>{" "}
            in chat to add, or{" "}
            <code style={{ color: "#f0a500", background: "#f0a50011", padding: "1px 6px", borderRadius: "4px" }}>
              /forget &lt;keyword&gt;
            </code>{" "}
            to remove.
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button style={btn()} onClick={() => setShowAdd(s => !s)}>
            {showAdd ? "✕ Cancel" : "+ Add Memory"}
          </button>
          {memories.length > 0 && (
            <button style={btn("#ff4444")} onClick={clearAll}>🗑 Clear All</button>
          )}
        </div>
      </div>

      {/* Agent selector */}
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        {agents.map(a => (
          <button
            key={a}
            style={{
              padding: "6px 16px",
              borderRadius: "8px",
              border: `1px solid ${a === selectedAgent ? accent : "#555"}`,
              background: a === selectedAgent ? `${accent}22` : "transparent",
              color: a === selectedAgent ? accent : "#888",
              cursor: "pointer",
              fontSize: "0.82rem",
              fontWeight: a === selectedAgent ? "700" : "400",
            }}
            onClick={() => setSelectedAgent(a)}
          >
            {a}
            {a === selectedAgent && memories.length > 0 && (
              <span style={{ marginLeft: "6px", fontSize: "0.7rem", opacity: 0.7 }}>
                ({memories.length})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Add form */}
      {showAdd && (
        <div style={{ background: cardBg, border, borderRadius: "12px", padding: "20px", marginBottom: "1.5rem" }}>
          <h3 style={{ color: "#ccc", margin: "0 0 14px", fontSize: "0.95rem" }}>
            Add memory for <span style={{ color: accent }}>{selectedAgent}</span>
          </h3>
          <form onSubmit={addMemory} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>Fact / Content *</label>
              <textarea
                style={{ ...inputStyle, height: "70px", resize: "vertical" }}
                placeholder="e.g. User prefers metric units. User lives in London."
                value={form.content}
                onChange={e => setForm(p => ({ ...p, content: e.target.value }))}
              />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>Category</label>
                <select style={inputStyle} value={form.category}
                  onChange={e => setForm(p => ({ ...p, category: e.target.value }))}>
                  <option value="fact">Fact</option>
                  <option value="preference">Preference</option>
                  <option value="context">Context</option>
                  <option value="summary">Summary</option>
                </select>
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>
                  Importance: {IMPORTANCE_STARS(form.importance)}
                </label>
                <input
                  type="range" min="1" max="5" value={form.importance}
                  onChange={e => setForm(p => ({ ...p, importance: parseInt(e.target.value) }))}
                  style={{ width: "100%", accentColor: accent }}
                />
              </div>
            </div>
            <div>
              <button type="submit" style={{ ...btn(accent), padding: "8px 20px" }} disabled={adding}>
                {adding ? "Saving…" : "Save Memory"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Memory list */}
      {loading && <div style={{ textAlign: "center", color: "#555", padding: "3rem" }}>Loading memories…</div>}
      {!loading && memories.length === 0 && (
        <div style={{ textAlign: "center", color: "#555", padding: "3rem" }}>
          No memories stored for <strong style={{ color: "#888" }}>{selectedAgent}</strong> yet.<br />
          <span style={{ fontSize: "0.82rem", marginTop: "6px", display: "block" }}>
            Chat and use <code style={{ color: accent }}>/remember</code> to build up context.
          </span>
        </div>
      )}
      {!loading && Object.entries(byCategory).map(([cat, mems]) => (
        <div key={cat} style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
            <span style={{
              fontSize: "0.72rem", padding: "2px 10px", borderRadius: "10px",
              background: `${CATEGORY_COLORS[cat] || accent}22`,
              color: CATEGORY_COLORS[cat] || accent,
              border: `1px solid ${CATEGORY_COLORS[cat] || accent}44`,
              fontWeight: "700", letterSpacing: "0.05em",
            }}>
              {cat.toUpperCase()}
            </span>
            <span style={{ color: "#555", fontSize: "0.75rem" }}>{mems.length} {mems.length === 1 ? "entry" : "entries"}</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {mems.map(m => (
              <div key={m.id} style={{
                background: cardBg,
                border: `1px solid ${CATEGORY_COLORS[m.category] || accent}22`,
                borderRadius: "10px",
                padding: "12px 16px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                gap: "12px",
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ color: "#ddd", fontSize: "0.88rem", lineHeight: "1.5" }}>{m.content}</div>
                  <div style={{ marginTop: "6px", display: "flex", gap: "12px", fontSize: "0.72rem", color: "#555" }}>
                    <span title="Importance" style={{ color: CATEGORY_COLORS[m.category] || accent, opacity: 0.7 }}>
                      {IMPORTANCE_STARS(m.importance || 3)}
                    </span>
                    <span>{SOURCE_LABELS[m.source] || m.source}</span>
                    <span>{new Date(m.created_at).toLocaleString()}</span>
                  </div>
                </div>
                <button
                  style={{ ...btn("#ff4444"), padding: "4px 10px", fontSize: "0.75rem", flexShrink: 0 }}
                  onClick={() => deleteMemory(m.id)}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Usage tip */}
      <div style={{ marginTop: "20px", background: "rgba(0,0,0,0.2)", border, borderRadius: "10px", padding: "14px 18px" }}>
        <div style={{ color: "#555", fontSize: "0.78rem" }}>
          <span style={{ color: accent, fontWeight: "600" }}>Tips:</span>
          {" "}Memories are automatically injected into the agent's system prompt on every call.
          High-importance memories are always included; lower-importance ones may be omitted when memory is full.
          Auto-extracted memories (importance 2) are harvested in the background from every chat turn.
        </div>
      </div>
    </div>
  );
}
