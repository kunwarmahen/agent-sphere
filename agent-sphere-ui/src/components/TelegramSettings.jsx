import React, { useState, useEffect, useCallback } from "react";

const API_URL = "http://localhost:5000/api";

export default function TelegramSettings({ theme, showNotification }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  // Form state
  const [token, setToken] = useState("");
  const [tokenDirty, setTokenDirty] = useState(false);
  const [userIdsInput, setUserIdsInput] = useState("");
  const [enabled, setEnabled] = useState(false);
  const [notifySchedule, setNotifySchedule] = useState(true);

  const accent = theme === "matrix" ? "#00ff9d" : theme === "cyber" ? "#00cfff" : "#a855f7";
  const cardBg = "rgba(255,255,255,0.04)";
  const border = `1px solid ${accent}22`;

  const fetchConfig = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/telegram/config`);
      const data = await r.json();
      setConfig(data);
      setEnabled(!!data.enabled);
      setNotifySchedule(data.notify_on_schedule !== false);
      setUserIdsInput((data.allowed_user_ids || []).join(", "));
      // Don't pre-fill token — it's masked; only set if user types a new one
    } catch {
      showNotification?.("Failed to load Telegram config", "error");
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  useEffect(() => { fetchConfig(); }, [fetchConfig]);

  async function save() {
    setSaving(true);
    try {
      const ids = userIdsInput
        .split(/[\s,]+/)
        .map(s => parseInt(s.trim(), 10))
        .filter(n => !isNaN(n));

      const body = {
        enabled,
        allowed_user_ids: ids,
        notify_on_schedule: notifySchedule,
      };
      if (tokenDirty && token) {
        body.bot_token = token;
      }

      const r = await fetch(`${API_URL}/telegram/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await r.json();
      if (data.success) {
        showNotification?.("Telegram settings saved", "success");
        setTokenDirty(false);
        setToken("");
        fetchConfig();
      } else {
        showNotification?.(data.error || "Save failed", "error");
      }
    } catch {
      showNotification?.("Network error", "error");
    } finally {
      setSaving(false);
    }
  }

  async function sendTest() {
    setTesting(true);
    try {
      const r = await fetch(`${API_URL}/telegram/test`, { method: "POST" });
      const data = await r.json();
      if (data.success) {
        showNotification?.("Test message sent!", "success");
      } else {
        showNotification?.(data.error || "Test failed", "error");
      }
    } catch {
      showNotification?.("Network error", "error");
    } finally {
      setTesting(false);
    }
  }

  async function toggleBot(on) {
    try {
      const endpoint = on ? "start" : "stop";
      const r = await fetch(`${API_URL}/telegram/${endpoint}`, { method: "POST" });
      const data = await r.json();
      if (data.success) {
        showNotification?.(on ? "Bot started" : "Bot stopped", "success");
        fetchConfig();
      } else {
        showNotification?.(data.error || "Failed", "error");
      }
    } catch {
      showNotification?.("Network error", "error");
    }
  }

  const isRunning = config?.is_running;

  const S = {
    wrap: {
      maxWidth: 720,
      margin: "0 auto",
      padding: "24px 16px",
      color: "#e6edf3",
      fontFamily: "monospace",
    },
    header: {
      display: "flex",
      alignItems: "center",
      gap: 12,
      marginBottom: 8,
    },
    title: { fontSize: 22, fontWeight: 700, color: accent },
    subtitle: { fontSize: 13, color: "#8b949e", marginBottom: 24 },
    card: {
      background: cardBg,
      border,
      borderRadius: 10,
      padding: "20px 22px",
      marginBottom: 18,
    },
    label: { fontSize: 12, color: "#8b949e", marginBottom: 6, display: "block" },
    input: {
      width: "100%",
      background: "rgba(255,255,255,0.06)",
      border: `1px solid ${accent}40`,
      borderRadius: 6,
      padding: "8px 12px",
      color: "#e6edf3",
      fontSize: 13,
      fontFamily: "monospace",
      boxSizing: "border-box",
    },
    row: { display: "flex", gap: 12, alignItems: "center", marginBottom: 14 },
    toggle: {
      width: 44,
      height: 24,
      borderRadius: 12,
      cursor: "pointer",
      border: "none",
      transition: "background 0.2s",
      flexShrink: 0,
    },
    btnPrimary: {
      background: accent,
      color: "#0d1117",
      border: "none",
      borderRadius: 6,
      padding: "9px 20px",
      fontWeight: 700,
      fontSize: 13,
      cursor: "pointer",
      fontFamily: "monospace",
    },
    btnSecondary: {
      background: "transparent",
      color: accent,
      border: `1px solid ${accent}`,
      borderRadius: 6,
      padding: "8px 18px",
      fontWeight: 600,
      fontSize: 13,
      cursor: "pointer",
      fontFamily: "monospace",
    },
    statusBadge: (on) => ({
      display: "inline-block",
      padding: "2px 10px",
      borderRadius: 999,
      fontSize: 12,
      fontWeight: 700,
      background: on ? "#39d35322" : "#8b949e22",
      color: on ? "#39d353" : "#8b949e",
      border: `1px solid ${on ? "#39d353" : "#8b949e"}55`,
    }),
    tip: {
      background: `${accent}0d`,
      border: `1px solid ${accent}33`,
      borderRadius: 8,
      padding: "12px 16px",
      fontSize: 12,
      color: "#8b949e",
      lineHeight: 1.7,
      marginBottom: 18,
    },
    commandGrid: {
      display: "grid",
      gridTemplateColumns: "auto 1fr",
      gap: "6px 16px",
      fontSize: 12,
      marginTop: 8,
    },
    cmd: { color: accent, fontFamily: "monospace", fontWeight: 700 },
    cmdDesc: { color: "#8b949e" },
  };

  if (loading) {
    return (
      <div style={S.wrap}>
        <div style={{ color: "#8b949e", textAlign: "center", paddingTop: 40 }}>
          Loading Telegram config…
        </div>
      </div>
    );
  }

  return (
    <div style={S.wrap}>
      {/* Header */}
      <div style={S.header}>
        <span style={{ fontSize: 28 }}>✈️</span>
        <span style={S.title}>Telegram Integration</span>
        <span style={S.statusBadge(isRunning)}>
          {isRunning ? "● Running" : "○ Stopped"}
        </span>
      </div>
      <div style={S.subtitle}>
        Chat with your agents from anywhere using Telegram. Scheduled job results can also be pushed directly to your phone.
      </div>

      {/* Setup guide tip */}
      <div style={S.tip}>
        <strong style={{ color: accent }}>Quick setup</strong>
        <ol style={{ margin: "6px 0 0 16px", padding: 0 }}>
          <li>Open Telegram and message <strong>@BotFather</strong></li>
          <li>Send <code>/newbot</code> and follow the prompts to get your token</li>
          <li>Paste the token below, set your Telegram user ID (use <code>/myid</code> in the bot), and click Save</li>
          <li>Enable the bot and send it a message to confirm</li>
        </ol>
      </div>

      {/* Bot token */}
      <div style={S.card}>
        <div style={{ fontWeight: 700, color: accent, marginBottom: 14 }}>Bot Configuration</div>

        <label style={S.label}>Bot Token (from @BotFather)</label>
        <input
          style={{ ...S.input, marginBottom: 14 }}
          type="password"
          placeholder={config?.bot_token ? `Current: ${config.bot_token}` : "123456789:ABCdef…"}
          value={token}
          onChange={e => { setToken(e.target.value); setTokenDirty(true); }}
          autoComplete="off"
        />

        <label style={S.label}>Allowed User IDs (comma-separated — leave empty to allow all)</label>
        <input
          style={{ ...S.input, marginBottom: 6 }}
          type="text"
          placeholder="123456789, 987654321"
          value={userIdsInput}
          onChange={e => setUserIdsInput(e.target.value)}
        />
        <div style={{ fontSize: 11, color: "#8b949e", marginBottom: 14 }}>
          Your user ID: send <code>/myid</code> to your bot after it starts.
        </div>

        {/* Toggles */}
        <div style={S.row}>
          <button
            style={{
              ...S.toggle,
              background: enabled ? accent : "#30363d",
            }}
            onClick={() => setEnabled(v => !v)}
          />
          <span style={{ fontSize: 13 }}>Enable Telegram bot</span>
        </div>

        <div style={S.row}>
          <button
            style={{
              ...S.toggle,
              background: notifySchedule ? accent : "#30363d",
            }}
            onClick={() => setNotifySchedule(v => !v)}
          />
          <span style={{ fontSize: 13 }}>Push scheduled job results to Telegram</span>
        </div>

        {/* Actions */}
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 6 }}>
          <button
            style={S.btnPrimary}
            onClick={save}
            disabled={saving}
          >
            {saving ? "Saving…" : "Save Changes"}
          </button>

          {isRunning ? (
            <button style={S.btnSecondary} onClick={() => toggleBot(false)}>
              Stop Bot
            </button>
          ) : (
            <button style={S.btnSecondary} onClick={() => toggleBot(true)}>
              Start Bot
            </button>
          )}

          <button
            style={{ ...S.btnSecondary, opacity: isRunning ? 1 : 0.4 }}
            onClick={sendTest}
            disabled={!isRunning || testing}
          >
            {testing ? "Sending…" : "Send Test Message"}
          </button>
        </div>
      </div>

      {/* Commands reference */}
      <div style={S.card}>
        <div style={{ fontWeight: 700, color: accent, marginBottom: 12 }}>Bot Commands</div>
        <div style={S.commandGrid}>
          <span style={S.cmd}>/ask &lt;message&gt;</span>
          <span style={S.cmdDesc}>Chat with the smart orchestrator</span>

          <span style={S.cmd}>/ask home &lt;msg&gt;</span>
          <span style={S.cmdDesc}>Talk to the home assistant agent</span>

          <span style={S.cmd}>/ask calendar &lt;msg&gt;</span>
          <span style={S.cmdDesc}>Talk to the calendar/email agent</span>

          <span style={S.cmd}>/ask finance &lt;msg&gt;</span>
          <span style={S.cmdDesc}>Talk to the finance agent</span>

          <span style={S.cmd}>/agents</span>
          <span style={S.cmdDesc}>List all available agents</span>

          <span style={S.cmd}>/schedules</span>
          <span style={S.cmdDesc}>View active scheduled jobs</span>

          <span style={S.cmd}>/status</span>
          <span style={S.cmdDesc}>System status overview</span>

          <span style={S.cmd}>/myid</span>
          <span style={S.cmdDesc}>Show your Telegram user ID for allow-listing</span>

          <span style={S.cmd}>/help</span>
          <span style={S.cmdDesc}>Full command reference</span>
        </div>
        <div style={{ marginTop: 12, fontSize: 12, color: "#8b949e" }}>
          You can also send any plain message — it goes straight to the orchestrator.
        </div>
      </div>

      {/* Data location note */}
      <div style={{ fontSize: 11, color: "#8b949e", textAlign: "center" }}>
        Config stored in <code>data/telegram_config.json</code> — add this file to <code>.gitignore</code>.
      </div>
    </div>
  );
}
