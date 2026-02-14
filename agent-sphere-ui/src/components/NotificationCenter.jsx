import React, { useState, useEffect, useRef, useCallback } from "react";

const API_URL = "http://localhost:5000/api";

const TYPE_META = {
  success: { icon: "✅", color: "#39d353" },
  error:   { icon: "❌", color: "#ff7b72" },
  warning: { icon: "⚠️", color: "#f0a500" },
  info:    { icon: "ℹ️", color: "#58a6ff" },
};

const SOURCE_LABEL = {
  scheduler: "Scheduler",
  webhook:   "Webhook",
  agent:     "Agent",
  manual:    "Manual",
  system:    "System",
};

function relTime(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const s = Math.floor(diff / 1000);
  if (s < 60) return "just now";
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

// ── Bell button + badge ───────────────────────────────────────────────────────

export function NotificationBell({ unreadCount, onClick, accent }) {
  return (
    <button
      onClick={onClick}
      style={{
        position: "relative",
        background: "transparent",
        border: `1px solid ${accent}44`,
        borderRadius: 8,
        padding: "6px 10px",
        cursor: "pointer",
        color: accent,
        fontSize: 16,
        display: "flex",
        alignItems: "center",
        gap: 4,
      }}
      title="Notifications"
    >
      🔔
      {unreadCount > 0 && (
        <span
          style={{
            position: "absolute",
            top: -6,
            right: -6,
            background: "#ff7b72",
            color: "#fff",
            borderRadius: "50%",
            width: 18,
            height: 18,
            fontSize: 10,
            fontWeight: 700,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            lineHeight: 1,
          }}
        >
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </button>
  );
}

// ── Main notification center panel ───────────────────────────────────────────

export default function NotificationCenter({ theme, showNotification, onUnreadChange }) {
  const [open, setOpen] = useState(false);
  const [view, setView] = useState("list");   // list | settings
  const [notifs, setNotifs] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [settings, setSettings] = useState(null);
  const [savingSettings, setSavingSettings] = useState(false);
  const [keywordsInput, setKeywordsInput] = useState("");
  const [budgetInput, setBudgetInput] = useState("");
  const [pushSupported, setPushSupported] = useState(false);
  const [pushSubscribed, setPushSubscribed] = useState(false);
  const panelRef = useRef(null);

  const accent = theme === "matrix" ? "#00ff9d" : theme === "cyber" ? "#00cfff" : "#a855f7";
  const cardBg = "rgba(13,17,23,0.97)";
  const border = `1px solid ${accent}33`;

  // ── data fetching ──────────────────────────────────────────────────────────

  const fetchNotifs = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/notifications?limit=50`);
      const data = await r.json();
      setNotifs(data.notifications || []);
      const uc = data.unread_count ?? 0;
      setUnreadCount(uc);
      onUnreadChange?.(uc);
    } catch { /* silent */ }
  }, [onUnreadChange]);

  const fetchSettings = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/notifications/settings`);
      const data = await r.json();
      setSettings(data);
      setKeywordsInput((data.alert_keywords || []).join(", "));
      setBudgetInput(String(data.budget_threshold ?? 1000));
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    fetchNotifs();
    fetchSettings();
    const id = setInterval(fetchNotifs, 15000);
    return () => clearInterval(id);
  }, [fetchNotifs, fetchSettings]);

  // ── browser push support ───────────────────────────────────────────────────

  useEffect(() => {
    if ("serviceWorker" in navigator && "PushManager" in window) {
      setPushSupported(true);
      navigator.serviceWorker.ready.then(reg => {
        reg.pushManager.getSubscription().then(sub => {
          setPushSubscribed(!!sub);
        });
      });
    }
  }, []);

  async function subscribePush() {
    try {
      const reg = await navigator.serviceWorker.ready;
      // Use a dummy VAPID key placeholder — replace with real key in production
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U",
      });
      await fetch(`${API_URL}/notifications/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sub.toJSON()),
      });
      setPushSubscribed(true);
      showNotification?.("Browser push enabled", "success");
    } catch (e) {
      showNotification?.(`Push setup failed: ${e.message}`, "error");
    }
  }

  async function unsubscribePush() {
    try {
      const reg = await navigator.serviceWorker.ready;
      const sub = await reg.pushManager.getSubscription();
      if (sub) {
        await fetch(`${API_URL}/notifications/unsubscribe`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ endpoint: sub.endpoint }),
        });
        await sub.unsubscribe();
      }
      setPushSubscribed(false);
      showNotification?.("Browser push disabled", "info");
    } catch (e) {
      showNotification?.(`Unsubscribe failed: ${e.message}`, "error");
    }
  }

  // ── actions ────────────────────────────────────────────────────────────────

  async function markRead(id) {
    await fetch(`${API_URL}/notifications/${id}/read`, { method: "POST" });
    setNotifs(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
    setUnreadCount(prev => {
      const next = Math.max(0, prev - 1);
      onUnreadChange?.(next);
      return next;
    });
  }

  async function markAllRead() {
    await fetch(`${API_URL}/notifications/read-all`, { method: "POST" });
    setNotifs(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
    onUnreadChange?.(0);
  }

  async function clearAll() {
    await fetch(`${API_URL}/notifications`, { method: "DELETE" });
    setNotifs([]);
    setUnreadCount(0);
    onUnreadChange?.(0);
  }

  async function saveSettings() {
    setSavingSettings(true);
    try {
      const keywords = keywordsInput.split(/[\s,]+/).map(s => s.trim()).filter(Boolean);
      const budget = parseFloat(budgetInput) || 1000;
      await fetch(`${API_URL}/notifications/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...settings,
          alert_keywords: keywords,
          budget_threshold: budget,
        }),
      });
      await fetchSettings();
      showNotification?.("Notification settings saved", "success");
    } catch {
      showNotification?.("Failed to save settings", "error");
    } finally {
      setSavingSettings(false);
    }
  }

  // ── click outside to close ─────────────────────────────────────────────────

  useEffect(() => {
    function handle(e) {
      if (open && panelRef.current && !panelRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handle);
    return () => document.removeEventListener("mousedown", handle);
  }, [open]);

  // ── styles ─────────────────────────────────────────────────────────────────

  const S = {
    wrap: { position: "relative", display: "inline-block" },
    panel: {
      position: "absolute",
      top: "calc(100% + 8px)",
      right: 0,
      width: 380,
      maxHeight: 560,
      background: cardBg,
      border,
      borderRadius: 12,
      boxShadow: `0 8px 32px rgba(0,0,0,0.6), 0 0 0 1px ${accent}22`,
      zIndex: 1000,
      display: "flex",
      flexDirection: "column",
      overflow: "hidden",
      fontFamily: "monospace",
    },
    header: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "12px 16px",
      borderBottom: border,
      flexShrink: 0,
    },
    headerTitle: { fontSize: 13, fontWeight: 700, color: accent },
    tabBar: {
      display: "flex",
      gap: 4,
      padding: "6px 10px",
      borderBottom: border,
      flexShrink: 0,
    },
    tab: (active) => ({
      background: active ? `${accent}22` : "transparent",
      border: `1px solid ${active ? accent : "transparent"}`,
      borderRadius: 6,
      padding: "4px 12px",
      fontSize: 11,
      color: active ? accent : "#8b949e",
      cursor: "pointer",
      fontFamily: "monospace",
    }),
    list: {
      overflowY: "auto",
      flex: 1,
    },
    item: (read) => ({
      padding: "10px 14px",
      borderBottom: `1px solid ${accent}11`,
      background: read ? "transparent" : `${accent}06`,
      cursor: "pointer",
      transition: "background 0.15s",
    }),
    itemTitle: { fontSize: 12, fontWeight: 600, color: "#e6edf3", marginBottom: 3 },
    itemMsg: { fontSize: 11, color: "#8b949e", lineHeight: 1.5, wordBreak: "break-word" },
    itemMeta: { display: "flex", gap: 8, marginTop: 4, alignItems: "center" },
    sourceBadge: (src) => ({
      fontSize: 10,
      padding: "1px 7px",
      borderRadius: 999,
      background: `${accent}18`,
      color: accent,
      border: `1px solid ${accent}33`,
    }),
    timeLabel: { fontSize: 10, color: "#6e7681" },
    unreadDot: {
      width: 7,
      height: 7,
      borderRadius: "50%",
      background: accent,
      flexShrink: 0,
    },
    empty: {
      textAlign: "center",
      color: "#8b949e",
      fontSize: 12,
      padding: "32px 16px",
    },
    settingsWrap: {
      padding: "12px 16px",
      overflowY: "auto",
      flex: 1,
    },
    label: { fontSize: 11, color: "#8b949e", marginBottom: 5, display: "block" },
    input: {
      width: "100%",
      background: "rgba(255,255,255,0.05)",
      border: `1px solid ${accent}33`,
      borderRadius: 6,
      padding: "7px 10px",
      color: "#e6edf3",
      fontSize: 12,
      fontFamily: "monospace",
      boxSizing: "border-box",
      marginBottom: 12,
    },
    toggle: (on) => ({
      width: 36,
      height: 20,
      borderRadius: 10,
      background: on ? accent : "#30363d",
      border: "none",
      cursor: "pointer",
      flexShrink: 0,
      transition: "background 0.2s",
    }),
    toggleRow: {
      display: "flex",
      alignItems: "center",
      gap: 10,
      marginBottom: 10,
    },
    toggleLabel: { fontSize: 12, color: "#e6edf3" },
    btn: {
      background: accent,
      color: "#0d1117",
      border: "none",
      borderRadius: 6,
      padding: "7px 14px",
      fontWeight: 700,
      fontSize: 12,
      cursor: "pointer",
      fontFamily: "monospace",
    },
    btnGhost: {
      background: "transparent",
      color: "#8b949e",
      border: "1px solid #30363d",
      borderRadius: 6,
      padding: "6px 12px",
      fontSize: 11,
      cursor: "pointer",
      fontFamily: "monospace",
    },
    footer: {
      display: "flex",
      gap: 8,
      padding: "8px 12px",
      borderTop: border,
      flexShrink: 0,
    },
  };

  const unreadItems = notifs.filter(n => !n.read).length;

  return (
    <div style={S.wrap} ref={panelRef}>
      {/* Bell button */}
      <NotificationBell
        unreadCount={unreadCount}
        onClick={() => { setOpen(v => !v); if (!open) fetchNotifs(); }}
        accent={accent}
      />

      {/* Panel */}
      {open && (
        <div style={S.panel}>
          {/* Header */}
          <div style={S.header}>
            <span style={S.headerTitle}>
              🔔 Notifications {unreadItems > 0 && (
                <span style={{ color: "#ff7b72", fontSize: 11 }}>({unreadItems} unread)</span>
              )}
            </span>
            <button onClick={() => setOpen(false)} style={{ background: "none", border: "none", color: "#8b949e", cursor: "pointer", fontSize: 16 }}>✕</button>
          </div>

          {/* Tab bar */}
          <div style={S.tabBar}>
            <button style={S.tab(view === "list")} onClick={() => setView("list")}>Feed</button>
            <button style={S.tab(view === "settings")} onClick={() => { setView("settings"); fetchSettings(); }}>Settings</button>
          </div>

          {/* Feed view */}
          {view === "list" && (
            <>
              <div style={S.list}>
                {notifs.length === 0 ? (
                  <div style={S.empty}>No notifications yet.<br />Scheduled job results, webhook triggers, and alerts will appear here.</div>
                ) : notifs.map(n => {
                  const meta = TYPE_META[n.type] || TYPE_META.info;
                  return (
                    <div
                      key={n.id}
                      style={S.item(n.read)}
                      onClick={() => !n.read && markRead(n.id)}
                    >
                      <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                        {!n.read && <div style={S.unreadDot} />}
                        <div style={{ flex: 1 }}>
                          <div style={{ ...S.itemTitle, color: meta.color }}>
                            {meta.icon} {n.title}
                          </div>
                          <div style={S.itemMsg}>{n.message}</div>
                          <div style={S.itemMeta}>
                            <span style={S.sourceBadge(n.source)}>
                              {SOURCE_LABEL[n.source] || n.source}
                            </span>
                            {n.agent_id && (
                              <span style={{ fontSize: 10, color: "#6e7681" }}>{n.agent_id}</span>
                            )}
                            <span style={S.timeLabel}>{relTime(n.created_at)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div style={S.footer}>
                <button style={S.btn} onClick={markAllRead} disabled={unreadItems === 0}>
                  Mark all read
                </button>
                <button style={S.btnGhost} onClick={clearAll}>Clear all</button>
              </div>
            </>
          )}

          {/* Settings view */}
          {view === "settings" && settings && (
            <div style={S.settingsWrap}>
              <label style={S.label}>Alert keywords (comma-separated)</label>
              <input
                style={S.input}
                value={keywordsInput}
                onChange={e => setKeywordsInput(e.target.value)}
                placeholder="error, failed, critical, alert"
              />

              <label style={S.label}>Budget threshold ($)</label>
              <input
                style={S.input}
                type="number"
                value={budgetInput}
                onChange={e => setBudgetInput(e.target.value)}
                placeholder="1000"
              />

              {[
                ["notify_on_schedule_success", "Notify on scheduled job success"],
                ["notify_on_schedule_failure", "Notify on scheduled job failure"],
                ["notify_on_webhook",          "Notify on webhook trigger"],
                ["notify_on_keyword_match",    "Notify on alert keyword in response"],
              ].map(([key, label]) => (
                <div key={key} style={S.toggleRow}>
                  <button
                    style={S.toggle(settings[key])}
                    onClick={() => setSettings(prev => ({ ...prev, [key]: !prev[key] }))}
                  />
                  <span style={S.toggleLabel}>{label}</span>
                </div>
              ))}

              {/* Browser push */}
              <div style={{ marginTop: 8, borderTop: `1px solid ${accent}22`, paddingTop: 12 }}>
                <div style={{ fontSize: 12, color: accent, fontWeight: 700, marginBottom: 8 }}>
                  Browser Push (background)
                </div>
                {!pushSupported ? (
                  <div style={{ fontSize: 11, color: "#8b949e" }}>Not supported in this browser.</div>
                ) : (
                  <div style={S.toggleRow}>
                    <button
                      style={S.toggle(pushSubscribed)}
                      onClick={pushSubscribed ? unsubscribePush : subscribePush}
                    />
                    <span style={S.toggleLabel}>
                      {pushSubscribed ? "Enabled — receive push when tab is closed" : "Enable background push"}
                    </span>
                  </div>
                )}
              </div>

              <button
                style={{ ...S.btn, marginTop: 12, width: "100%" }}
                onClick={saveSettings}
                disabled={savingSettings}
              >
                {savingSettings ? "Saving…" : "Save Settings"}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
