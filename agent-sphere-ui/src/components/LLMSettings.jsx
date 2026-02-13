import React, { useState, useEffect, useCallback } from "react";

const API_URL = "http://localhost:5000/api";

const PROVIDER_ICONS = {
  ollama: "🦙",
  anthropic: "🔮",
  openai: "⚡",
  google: "🌐",
};

export default function LLMSettings({ theme, showNotification }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(null);
  const [editKeys, setEditKeys] = useState({});   // provider -> draft key value
  const [editModels, setEditModels] = useState({}); // provider -> draft model
  const [saving, setSaving] = useState(null);
  const [failoverOrder, setFailoverOrder] = useState([]);

  const accent = theme === "matrix" ? "#00ff9d" : theme === "cyber" ? "#00cfff" : "#a855f7";
  const cardBg = "rgba(255,255,255,0.04)";
  const border = `1px solid ${accent}22`;

  const fetchConfig = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/llm/providers`);
      const data = await r.json();
      setConfig(data);
      setFailoverOrder(data.failover_order || ["ollama"]);
    } catch {
      showNotification?.("Failed to load LLM config", "error");
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  useEffect(() => { fetchConfig(); }, [fetchConfig]);

  async function saveProvider(provider) {
    setSaving(provider);
    const body = {};
    if (editKeys[provider] !== undefined) body.api_key = editKeys[provider];
    if (editModels[provider] !== undefined) body.model = editModels[provider];

    try {
      const r = await fetch(`${API_URL}/llm/providers/${provider}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await r.json();
      if (data.success) {
        showNotification?.(`${provider} settings saved`, "success");
        setEditKeys(prev => { const n = {...prev}; delete n[provider]; return n; });
        setEditModels(prev => { const n = {...prev}; delete n[provider]; return n; });
        fetchConfig();
      } else {
        showNotification?.(data.error || "Save failed", "error");
      }
    } catch {
      showNotification?.("Request failed", "error");
    } finally {
      setSaving(null);
    }
  }

  async function toggleProvider(provider, enabled) {
    try {
      await fetch(`${API_URL}/llm/providers/${provider}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled }),
      });
      fetchConfig();
    } catch {
      showNotification?.("Failed to toggle provider", "error");
    }
  }

  async function setDefault(provider) {
    try {
      await fetch(`${API_URL}/llm/default`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider }),
      });
      showNotification?.(`Default set to ${provider}`, "success");
      fetchConfig();
    } catch {
      showNotification?.("Failed to set default", "error");
    }
  }

  async function testProvider(provider) {
    setTesting(provider);
    try {
      const r = await fetch(`${API_URL}/llm/test/${provider}`, { method: "POST" });
      const data = await r.json();
      if (data.success) {
        showNotification?.(`${provider} ✓ Connected: "${data.response}"`, "success");
      } else {
        showNotification?.(`${provider} ✗ ${data.error}`, "error");
      }
    } catch {
      showNotification?.("Test request failed", "error");
    } finally {
      setTesting(null);
    }
  }

  async function saveFailover() {
    try {
      await fetch(`${API_URL}/llm/failover`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order: failoverOrder }),
      });
      showNotification?.("Failover order saved", "success");
      fetchConfig();
    } catch {
      showNotification?.("Failed to save failover order", "error");
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

  const btnStyle = (color = accent) => ({
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

  if (loading) return <div style={{ padding: "2rem", color: "#888", textAlign: "center" }}>Loading LLM settings...</div>;
  if (!config) return null;

  const providers = config.provider_metadata || {};
  const providerConfigs = config.providers || {};
  const defaultProvider = config.default_provider || "ollama";

  return (
    <div style={{ padding: "1.5rem", maxWidth: "900px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ color: accent, margin: 0, fontSize: "1.6rem" }}>🧠 LLM Settings</h2>
        <p style={{ color: "#888", margin: "4px 0 0", fontSize: "0.85rem" }}>
          Configure AI providers, API keys, and failover order. Keys are stored locally and never sent externally.
        </p>
      </div>

      {/* Provider Cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginBottom: "2rem" }}>
        {Object.entries(providers).map(([pid, meta]) => {
          const pcfg = providerConfigs[pid] || {};
          const isDefault = pid === defaultProvider;
          const isEnabled = pcfg.enabled;
          const needsKey = meta.requires_key;
          const hasKey = pcfg.api_key && pcfg.api_key.includes("•") && pcfg.api_key.length > 4;
          const draftKey = editKeys[pid];
          const draftModel = editModels[pid];
          const hasUnsaved = draftKey !== undefined || draftModel !== undefined;

          return (
            <div key={pid} style={{
              background: cardBg,
              border: isDefault ? `1px solid ${accent}55` : border,
              borderRadius: "12px",
              padding: "20px",
            }}>
              {/* Provider header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ fontSize: "1.6rem" }}>{PROVIDER_ICONS[pid]}</span>
                  <div>
                    <div style={{ fontWeight: "700", color: "#eee", fontSize: "1rem" }}>
                      {meta.name}
                      {isDefault && (
                        <span style={{ marginLeft: "8px", fontSize: "0.72rem", padding: "2px 8px", borderRadius: "10px", background: `${accent}22`, color: accent, border: `1px solid ${accent}44` }}>
                          DEFAULT
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: "0.8rem", color: "#888", marginTop: "2px" }}>{meta.description}</div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  {/* Enable toggle */}
                  <button
                    style={btnStyle(isEnabled ? "#00ff9d" : "#888")}
                    onClick={() => toggleProvider(pid, !isEnabled)}
                  >
                    {isEnabled ? "✓ Enabled" : "Disabled"}
                  </button>
                  {/* Set as default */}
                  {!isDefault && isEnabled && (
                    <button style={btnStyle(accent)} onClick={() => setDefault(pid)}>
                      Set Default
                    </button>
                  )}
                  {/* Test */}
                  <button
                    style={btnStyle("#00cfff")}
                    onClick={() => testProvider(pid)}
                    disabled={testing === pid}
                  >
                    {testing === pid ? "Testing..." : "Test"}
                  </button>
                </div>
              </div>

              {/* Config fields */}
              <div style={{ display: "grid", gridTemplateColumns: needsKey ? "1fr 1fr" : "1fr", gap: "12px" }}>
                {needsKey && (
                  <div>
                    <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>
                      API Key {hasKey ? <span style={{ color: "#00ff9d" }}>✓ saved</span> : <span style={{ color: "#f0a500" }}>⚠ not set</span>}
                    </label>
                    <input
                      type="password"
                      style={inputStyle}
                      placeholder={hasKey ? "••••••••  (enter new key to update)" : "Paste API key here"}
                      value={draftKey ?? ""}
                      onChange={e => setEditKeys(prev => ({ ...prev, [pid]: e.target.value }))}
                    />
                  </div>
                )}
                <div>
                  <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>Model</label>
                  <select
                    style={inputStyle}
                    value={draftModel ?? pcfg.model ?? meta.default_model}
                    onChange={e => setEditModels(prev => ({ ...prev, [pid]: e.target.value }))}
                  >
                    {(meta.models || []).map(m => <option key={m} value={m}>{m}</option>)}
                  </select>
                </div>
              </div>

              {/* Ollama base URL */}
              {pid === "ollama" && (
                <div style={{ marginTop: "10px" }}>
                  <label style={{ display: "block", fontSize: "0.78rem", color: "#aaa", marginBottom: "4px" }}>Ollama Base URL</label>
                  <input
                    style={inputStyle}
                    value={draftKey ?? pcfg.base_url ?? "http://localhost:11434"}
                    onChange={e => setEditKeys(prev => ({ ...prev, [pid]: e.target.value }))}
                    placeholder="http://localhost:11434"
                  />
                </div>
              )}

              {/* Save button */}
              {hasUnsaved && (
                <div style={{ marginTop: "12px" }}>
                  <button
                    style={{ ...btnStyle(accent), padding: "8px 20px" }}
                    onClick={() => saveProvider(pid)}
                    disabled={saving === pid}
                  >
                    {saving === pid ? "Saving..." : "Save Changes"}
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Failover Order */}
      <div style={{ background: cardBg, border, borderRadius: "12px", padding: "20px" }}>
        <h3 style={{ color: "#ccc", margin: "0 0 8px", fontSize: "1rem" }}>⚡ Failover Order</h3>
        <p style={{ color: "#888", fontSize: "0.82rem", margin: "0 0 12px" }}>
          If the primary provider fails, the system tries these in order.
        </p>
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "12px" }}>
          {["ollama", "anthropic", "openai", "google"].map(pid => {
            const idx = failoverOrder.indexOf(pid);
            const inOrder = idx !== -1;
            return (
              <button
                key={pid}
                style={{
                  padding: "6px 14px",
                  borderRadius: "8px",
                  border: `1px solid ${inOrder ? accent : "#555"}`,
                  background: inOrder ? `${accent}18` : "transparent",
                  color: inOrder ? accent : "#888",
                  cursor: "pointer",
                  fontSize: "0.82rem",
                }}
                onClick={() => {
                  if (inOrder) {
                    setFailoverOrder(prev => prev.filter(p => p !== pid));
                  } else {
                    setFailoverOrder(prev => [...prev, pid]);
                  }
                }}
              >
                {inOrder ? `${idx + 1}. ` : ""}{PROVIDER_ICONS[pid]} {pid}
              </button>
            );
          })}
        </div>
        <p style={{ color: "#666", fontSize: "0.78rem", margin: "0 0 10px" }}>
          Current order: {failoverOrder.join(" → ") || "none"}
        </p>
        <button style={btnStyle(accent)} onClick={saveFailover}>Save Failover Order</button>
      </div>
    </div>
  );
}
