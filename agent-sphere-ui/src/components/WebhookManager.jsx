import React, { useState, useEffect, useCallback } from "react";

const API_URL = "http://localhost:5000/api";
const TRIGGER_BASE = "http://localhost:5000/api/trigger";

export default function WebhookManager({ theme, showNotification }) {
  const [hooks, setHooks] = useState([]);
  const [log, setLog] = useState([]);
  const [view, setView] = useState("list"); // list | log | create
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    agent_id: "orchestrator",
    prompt_template: "",
  });

  const accent = theme === "matrix" ? "#00ff9d" : theme === "cyber" ? "#00cfff" : "#a855f7";
  const cardBg = "rgba(255,255,255,0.04)";
  const border = `1px solid ${accent}22`;

  const fetchHooks = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/webhooks`);
      const data = await r.json();
      setHooks(data.webhooks || []);
    } catch {
      showNotification?.("Failed to load webhooks", "error");
    }
  }, [showNotification]);

  const fetchLog = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/webhooks/log?limit=100`);
      const data = await r.json();
      setLog(data.log || []);
    } catch {
      showNotification?.("Failed to load webhook log", "error");
    }
  }, [showNotification]);

  useEffect(() => {
    fetchHooks();
  }, [fetchHooks]);

  useEffect(() => {
    if (view === "log") fetchLog();
  }, [view, fetchLog]);

  async function createWebhook(e) {
    e.preventDefault();
    if (!form.name.trim() || !form.prompt_template.trim()) {
      showNotification?.("Name and prompt template are required", "error");
      return;
    }
    setCreating(true);
    try {
      const r = await fetch(`${API_URL}/webhooks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await r.json();
      if (data.success) {
        showNotification?.(`Webhook "${form.name}" created`, "success");
        setForm({ name: "", description: "", agent_id: "orchestrator", prompt_template: "" });
        setView("list");
        fetchHooks();
      } else {
        showNotification?.(data.error || "Create failed", "error");
      }
    } catch {
      showNotification?.("Request failed", "error");
    } finally {
      setCreating(false);
    }
  }

  async function deleteHook(token, name) {
    if (!window.confirm(`Delete webhook "${name}"?`)) return;
    try {
      const r = await fetch(`${API_URL}/webhooks/${token}`, { method: "DELETE" });
      const data = await r.json();
      if (data.success) {
        showNotification?.(`Deleted "${name}"`, "success");
        fetchHooks();
      } else {
        showNotification?.(data.error || "Delete failed", "error");
      }
    } catch {
      showNotification?.("Request failed", "error");
    }
  }

  async function toggleHook(token, enabled) {
    try {
      await fetch(`${API_URL}/webhooks/${token}/toggle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled }),
      });
      fetchHooks();
    } catch {
      showNotification?.("Failed to toggle webhook", "error");
    }
  }

  async function regenerate(token) {
    if (!window.confirm("Regenerate token? The old URL will stop working.")) return;
    try {
      const r = await fetch(`${API_URL}/webhooks/${token}/regenerate`, { method: "POST" });
      const data = await r.json();
      if (data.success) {
        showNotification?.("Token regenerated", "success");
        fetchHooks();
      }
    } catch {
      showNotification?.("Request failed", "error");
    }
  }

  function copyUrl(token) {
    const url = `${TRIGGER_BASE}/${token}`;
    navigator.clipboard.writeText(url).then(() => {
      showNotification?.("URL copied to clipboard", "success");
    });
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

  return (
    <div style={{ padding: "1.5rem", maxWidth: "960px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
        <div>
          <h2 style={{ color: accent, margin: 0, fontSize: "1.6rem" }}>🔗 Webhooks</h2>
          <p style={{ color: "#888", margin: "4px 0 0", fontSize: "0.85rem" }}>
            HTTP trigger URLs — POST to <code style={{ color: accent }}>{"http://localhost:5000/api/trigger/<token>"}</code> from any external service.
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          {["list", "log", "create"].map(v => (
            <button key={v} style={{ ...btn(view === v ? accent : "#666"), background: view === v ? `${accent}22` : "transparent" }} onClick={() => setView(v)}>
              {v === "list" ? "📋 Webhooks" : v === "log" ? "📜 Log" : "+ Create"}
            </button>
          ))}
        </div>
      </div>

      {/* ── LIST ── */}
      {view === "list" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {hooks.length === 0 && (
            <div style={{ textAlign: "center", color: "#555", padding: "3rem" }}>
              No webhooks yet. Click <strong style={{ color: accent }}>+ Create</strong> to add one.
            </div>
          )}
          {hooks.map(hook => (
            <div key={hook.token} style={{ background: cardBg, border: hook.enabled ? `1px solid ${accent}33` : border, borderRadius: "12px", padding: "18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
                <div>
                  <div style={{ fontWeight: "700", color: "#eee", fontSize: "1rem", display: "flex", alignItems: "center", gap: "8px" }}>
                    {hook.name}
                    <span style={{ fontSize: "0.72rem", padding: "2px 8px", borderRadius: "10px", background: hook.enabled ? `${accent}22` : "#88888822", color: hook.enabled ? accent : "#888", border: `1px solid ${hook.enabled ? accent : "#888"}44` }}>
                      {hook.enabled ? "ACTIVE" : "DISABLED"}
                    </span>
                  </div>
                  {hook.description && <div style={{ color: "#888", fontSize: "0.8rem", marginTop: "2px" }}>{hook.description}</div>}
                  <div style={{ color: "#666", fontSize: "0.75rem", marginTop: "4px" }}>
                    Agent: <span style={{ color: "#aaa" }}>{hook.agent_id}</span>
                    {" · "}Triggered: <span style={{ color: "#aaa" }}>{hook.trigger_count}</span>
                    {hook.last_triggered && <>{" · "}Last: <span style={{ color: "#aaa" }}>{new Date(hook.last_triggered).toLocaleString()}</span></>}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", justifyContent: "flex-end" }}>
                  <button style={btn("#00cfff")} onClick={() => copyUrl(hook.token)}>📋 Copy URL</button>
                  <button style={btn(hook.enabled ? "#f0a500" : "#00ff9d")} onClick={() => toggleHook(hook.token, !hook.enabled)}>
                    {hook.enabled ? "Disable" : "Enable"}
                  </button>
                  <button style={btn("#f0a500")} onClick={() => regenerate(hook.token)}>🔄 Regen Token</button>
                  <button style={btn("#ff4444")} onClick={() => deleteHook(hook.token, hook.name)}>Delete</button>
                </div>
              </div>

              {/* URL display */}
              <div style={{ background: "rgba(0,0,0,0.25)", borderRadius: "6px", padding: "8px 12px", fontFamily: "monospace", fontSize: "0.78rem", color: "#aaa", wordBreak: "break-all", marginBottom: "8px" }}>
                POST {TRIGGER_BASE}/{hook.token}
              </div>

              {/* Prompt template preview */}
              <div>
                <div style={{ fontSize: "0.72rem", color: "#666", marginBottom: "3px" }}>Prompt template:</div>
                <div style={{ background: "rgba(0,0,0,0.2)", borderRadius: "6px", padding: "6px 10px", fontFamily: "monospace", fontSize: "0.77rem", color: "#888", whiteSpace: "pre-wrap", maxHeight: "60px", overflow: "hidden" }}>
                  {hook.prompt_template}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── LOG ── */}
      {view === "log" && (
        <div>
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "12px" }}>
            <button style={btn()} onClick={fetchLog}>↻ Refresh</button>
          </div>
          {log.length === 0 && (
            <div style={{ textAlign: "center", color: "#555", padding: "3rem" }}>No webhook executions yet.</div>
          )}
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {log.map(entry => (
              <div key={entry.id} style={{ background: cardBg, border: `1px solid ${entry.success ? "#00ff9d22" : "#ff444422"}`, borderRadius: "10px", padding: "14px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                  <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                    <span style={{ fontSize: "0.9rem" }}>{entry.success ? "✅" : "❌"}</span>
                    <span style={{ color: "#ddd", fontWeight: "600", fontSize: "0.9rem" }}>{entry.webhook_name}</span>
                    <span style={{ color: "#666", fontSize: "0.75rem", fontFamily: "monospace" }}>{entry.id}</span>
                  </div>
                  <div style={{ color: "#666", fontSize: "0.75rem" }}>
                    {new Date(entry.triggered_at).toLocaleString()} · {entry.duration_ms}ms
                  </div>
                </div>
                {Object.keys(entry.payload).length > 0 && (
                  <div style={{ background: "rgba(0,0,0,0.2)", borderRadius: "5px", padding: "5px 8px", fontFamily: "monospace", fontSize: "0.73rem", color: "#888", marginBottom: "5px" }}>
                    Payload: {JSON.stringify(entry.payload)}
                  </div>
                )}
                <div style={{ color: entry.success ? "#aaa" : "#ff8888", fontSize: "0.8rem", fontFamily: "monospace", whiteSpace: "pre-wrap" }}>
                  {entry.result || "(no output)"}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── CREATE ── */}
      {view === "create" && (
        <div style={{ background: cardBg, border, borderRadius: "12px", padding: "24px", maxWidth: "600px" }}>
          <h3 style={{ color: "#ccc", margin: "0 0 16px", fontSize: "1rem" }}>Create Webhook</h3>
          <form onSubmit={createWebhook} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>

            <div>
              <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>Name *</label>
              <input style={inputStyle} placeholder="e.g. Alert Summary" value={form.name}
                onChange={e => setForm(p => ({ ...p, name: e.target.value }))} />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>Description</label>
              <input style={inputStyle} placeholder="Optional description" value={form.description}
                onChange={e => setForm(p => ({ ...p, description: e.target.value }))} />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>Agent</label>
              <select style={inputStyle} value={form.agent_id}
                onChange={e => setForm(p => ({ ...p, agent_id: e.target.value }))}>
                <option value="orchestrator">orchestrator (auto-route)</option>
                <option value="home">home</option>
                <option value="calendar">calendar</option>
                <option value="finance">finance</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>
                Prompt Template *
                <span style={{ color: "#666", marginLeft: "8px" }}>
                  Use <code style={{ color: accent }}>{"{{payload}}"}</code> or <code style={{ color: accent }}>{"{{payload.key}}"}</code>
                </span>
              </label>
              <textarea
                style={{ ...inputStyle, height: "100px", resize: "vertical" }}
                placeholder={"Summarize this alert: {{payload.message}}\nSeverity: {{payload.severity}}"}
                value={form.prompt_template}
                onChange={e => setForm(p => ({ ...p, prompt_template: e.target.value }))}
              />
            </div>

            <div style={{ display: "flex", gap: "10px" }}>
              <button type="submit" style={{ ...btn(accent), padding: "9px 24px" }} disabled={creating}>
                {creating ? "Creating…" : "Create Webhook"}
              </button>
              <button type="button" style={btn("#888")} onClick={() => setView("list")}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Usage tip */}
      {view === "list" && hooks.length > 0 && (
        <div style={{ marginTop: "20px", background: "rgba(0,0,0,0.2)", border, borderRadius: "10px", padding: "14px 18px" }}>
          <div style={{ color: "#666", fontSize: "0.78rem", fontFamily: "monospace" }}>
            <span style={{ color: accent }}>Example:</span>{"  "}
            curl -X POST http://localhost:5000/api/trigger/&lt;token&gt; \<br />
            {"  "}-H "Content-Type: application/json" \<br />
            {"  "}-d '&#123;"message": "Disk usage over 90%", "severity": "high"&#125;'
          </div>
        </div>
      )}
    </div>
  );
}
