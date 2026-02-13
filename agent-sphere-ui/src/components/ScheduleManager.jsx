import React, { useState, useEffect, useCallback } from "react";

const API_URL = "http://localhost:5000/api";

const STATUS_COLORS = {
  active: "#00ff9d",
  paused: "#f0a500",
  running: "#00cfff",
  failed: "#ff4d4d",
};

function formatNextRun(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  const now = new Date();
  const diff = d - now;
  if (diff < 0) return "overdue";
  if (diff < 60000) return "< 1 min";
  if (diff < 3600000) return `in ${Math.round(diff / 60000)} min`;
  if (diff < 86400000) return `in ${Math.round(diff / 3600000)}h`;
  return d.toLocaleDateString() + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function formatTs(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString() + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ScheduleManager({ theme, showNotification }) {
  const [jobs, setJobs] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState("jobs"); // jobs | history | create
  const [selectedJob, setSelectedJob] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);

  // Create form state
  const [form, setForm] = useState({
    name: "",
    agent_id: "orchestrator",
    prompt: "",
    schedule_type: "cron",
    schedule_desc: "",
    hour: "8",
    minute: "0",
    day_of_week: "*",
    hours: "1",
    minutes: "0",
    run_at: "",
  });

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/schedules`);
      const data = await r.json();
      setJobs(data.jobs || []);
    } catch (e) {
      showNotification?.("Failed to load schedules", "error");
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const fetchHistory = useCallback(async (jobId = null) => {
    try {
      const url = jobId
        ? `${API_URL}/schedules/history?job_id=${jobId}&limit=100`
        : `${API_URL}/schedules/history?limit=100`;
      const r = await fetch(url);
      const data = await r.json();
      setHistory(data.history || []);
    } catch (e) {
      // silently fail
    }
  }, []);

  useEffect(() => {
    fetchJobs();
    fetchHistory();
    const interval = setInterval(() => {
      fetchJobs();
      fetchHistory();
    }, 15000);
    return () => clearInterval(interval);
  }, [fetchJobs, fetchHistory]);

  async function handleAction(action, jobId) {
    setActionLoading(`${action}-${jobId}`);
    try {
      let r;
      if (action === "delete") {
        r = await fetch(`${API_URL}/schedules/${jobId}`, { method: "DELETE" });
      } else if (action === "pause") {
        r = await fetch(`${API_URL}/schedules/${jobId}/pause`, { method: "POST" });
      } else if (action === "resume") {
        r = await fetch(`${API_URL}/schedules/${jobId}/resume`, { method: "POST" });
      } else if (action === "run-now") {
        r = await fetch(`${API_URL}/schedules/${jobId}/run-now`, { method: "POST" });
      }
      const data = await r.json();
      if (data.success) {
        showNotification?.(`Job ${action}d successfully`, "success");
        fetchJobs();
      } else {
        showNotification?.(data.error || "Action failed", "error");
      }
    } catch (e) {
      showNotification?.("Request failed", "error");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    const body = {
      name: form.name,
      agent_id: form.agent_id,
      prompt: form.prompt,
      schedule_type: form.schedule_type,
      schedule_desc: form.schedule_desc,
    };
    if (form.schedule_type === "cron") {
      body.hour = parseInt(form.hour);
      body.minute = parseInt(form.minute);
      body.day_of_week = form.day_of_week;
    } else if (form.schedule_type === "interval") {
      body.hours = parseInt(form.hours);
      body.minutes = parseInt(form.minutes);
    } else if (form.schedule_type === "one_shot") {
      body.run_at = new Date(form.run_at).toISOString();
    }
    try {
      const r = await fetch(`${API_URL}/schedules`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await r.json();
      if (data.success) {
        showNotification?.(`Schedule "${form.name}" created`, "success");
        setActiveView("jobs");
        fetchJobs();
        setForm({ name: "", agent_id: "orchestrator", prompt: "", schedule_type: "cron", schedule_desc: "", hour: "8", minute: "0", day_of_week: "*", hours: "1", minutes: "0", run_at: "" });
      } else {
        showNotification?.(data.error || "Failed to create schedule", "error");
      }
    } catch (e) {
      showNotification?.("Request failed", "error");
    }
  }

  const accent = theme === "matrix" ? "#00ff9d" : theme === "cyber" ? "#00cfff" : "#a855f7";
  const cardBg = "rgba(255,255,255,0.04)";
  const border = `1px solid ${accent}22`;

  const subBtnStyle = (active) => ({
    padding: "6px 16px",
    borderRadius: "6px",
    border: `1px solid ${active ? accent : "transparent"}`,
    background: active ? `${accent}18` : "transparent",
    color: active ? accent : "#aaa",
    cursor: "pointer",
    fontSize: "0.85rem",
    fontWeight: active ? "600" : "400",
    transition: "all 0.2s",
  });

  const inputStyle = {
    width: "100%",
    background: "rgba(255,255,255,0.06)",
    border: `1px solid ${accent}33`,
    borderRadius: "8px",
    color: "#fff",
    padding: "8px 12px",
    fontSize: "0.9rem",
    outline: "none",
    boxSizing: "border-box",
  };

  const labelStyle = {
    display: "block",
    fontSize: "0.8rem",
    color: "#aaa",
    marginBottom: "4px",
    marginTop: "12px",
  };

  return (
    <div style={{ padding: "1.5rem", maxWidth: "1100px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h2 style={{ color: accent, margin: 0, fontSize: "1.6rem" }}>⏰ Scheduled Jobs</h2>
          <p style={{ color: "#888", margin: "4px 0 0", fontSize: "0.85rem" }}>
            {jobs.length} job{jobs.length !== 1 ? "s" : ""} · jobs persist across restarts
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button style={subBtnStyle(activeView === "jobs")} onClick={() => setActiveView("jobs")}>Jobs</button>
          <button style={subBtnStyle(activeView === "history")} onClick={() => { setActiveView("history"); fetchHistory(); }}>History</button>
          <button
            style={{ ...subBtnStyle(activeView === "create"), background: activeView === "create" ? `${accent}28` : `${accent}12`, color: accent }}
            onClick={() => setActiveView("create")}
          >
            + New Schedule
          </button>
          <button
            style={{ ...subBtnStyle(false), border: `1px solid ${accent}33` }}
            onClick={fetchJobs}
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* ── JOBS VIEW ── */}
      {activeView === "jobs" && (
        <div>
          {loading && <p style={{ color: "#888", textAlign: "center" }}>Loading...</p>}
          {!loading && jobs.length === 0 && (
            <div style={{ textAlign: "center", padding: "3rem", color: "#666" }}>
              <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>⏰</div>
              <p>No scheduled jobs yet.</p>
              <p style={{ fontSize: "0.85rem" }}>
                You can create one by clicking <strong style={{ color: accent }}>+ New Schedule</strong> or simply typing something like
                <em style={{ color: accent }}> "check my emails every morning at 8am"</em> in the Chat.
              </p>
            </div>
          )}
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {jobs.map((job) => (
              <div
                key={job.job_id}
                style={{
                  background: cardBg,
                  border: selectedJob === job.job_id ? `1px solid ${accent}66` : border,
                  borderRadius: "12px",
                  padding: "16px 20px",
                  cursor: "pointer",
                  transition: "border 0.2s",
                }}
                onClick={() => setSelectedJob(selectedJob === job.job_id ? null : job.job_id)}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <span style={{ fontWeight: "600", color: "#eee", fontSize: "1rem" }}>{job.name}</span>
                    <span style={{
                      marginLeft: "10px",
                      fontSize: "0.72rem",
                      padding: "2px 8px",
                      borderRadius: "10px",
                      background: `${STATUS_COLORS[job.status] || "#888"}22`,
                      color: STATUS_COLORS[job.status] || "#888",
                      border: `1px solid ${STATUS_COLORS[job.status] || "#888"}44`,
                    }}>
                      {job.status}
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: "8px" }}>
                    <button
                      style={{ padding: "4px 10px", borderRadius: "6px", border: `1px solid ${accent}33`, background: `${accent}10`, color: accent, cursor: "pointer", fontSize: "0.78rem" }}
                      onClick={(e) => { e.stopPropagation(); handleAction("run-now", job.job_id); }}
                      disabled={actionLoading === `run-now-${job.job_id}`}
                    >▶ Run now</button>
                    {job.status === "active" ? (
                      <button
                        style={{ padding: "4px 10px", borderRadius: "6px", border: "1px solid #f0a50033", background: "#f0a50010", color: "#f0a500", cursor: "pointer", fontSize: "0.78rem" }}
                        onClick={(e) => { e.stopPropagation(); handleAction("pause", job.job_id); }}
                      >⏸ Pause</button>
                    ) : (
                      <button
                        style={{ padding: "4px 10px", borderRadius: "6px", border: "1px solid #00ff9d33", background: "#00ff9d10", color: "#00ff9d", cursor: "pointer", fontSize: "0.78rem" }}
                        onClick={(e) => { e.stopPropagation(); handleAction("resume", job.job_id); }}
                      >▶ Resume</button>
                    )}
                    <button
                      style={{ padding: "4px 10px", borderRadius: "6px", border: "1px solid #ff4d4d33", background: "#ff4d4d10", color: "#ff4d4d", cursor: "pointer", fontSize: "0.78rem" }}
                      onClick={(e) => { e.stopPropagation(); handleAction("delete", job.job_id); }}
                    >✕ Delete</button>
                  </div>
                </div>

                <div style={{ marginTop: "8px", display: "flex", gap: "24px", flexWrap: "wrap" }}>
                  <span style={{ fontSize: "0.82rem", color: "#aaa" }}>
                    🕐 <strong style={{ color: "#ccc" }}>{job.schedule_desc || "custom schedule"}</strong>
                  </span>
                  <span style={{ fontSize: "0.82rem", color: "#aaa" }}>
                    Next run: <strong style={{ color: accent }}>{formatNextRun(job.next_run)}</strong>
                  </span>
                  <span style={{ fontSize: "0.82rem", color: "#aaa" }}>
                    Agent: <strong style={{ color: "#ccc" }}>{job.agent_id}</strong>
                  </span>
                </div>

                {selectedJob === job.job_id && (
                  <div style={{ marginTop: "12px", padding: "12px", background: "rgba(255,255,255,0.03)", borderRadius: "8px", borderTop: `1px solid ${accent}22` }}>
                    <div style={{ fontSize: "0.8rem", color: "#888", marginBottom: "4px" }}>Task prompt</div>
                    <div style={{ fontSize: "0.9rem", color: "#ddd" }}>{job.prompt || "—"}</div>
                    <div style={{ fontSize: "0.78rem", color: "#666", marginTop: "8px" }}>
                      Created: {formatTs(job.created_at)} · ID: <code style={{ color: "#888" }}>{job.job_id}</code>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── HISTORY VIEW ── */}
      {activeView === "history" && (
        <div>
          <h3 style={{ color: "#ccc", marginBottom: "1rem", fontSize: "1rem" }}>Execution History</h3>
          {history.length === 0 && <p style={{ color: "#666", textAlign: "center", padding: "2rem" }}>No executions yet.</p>}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {[...history].reverse().map((entry, i) => (
              <div key={i} style={{
                background: cardBg, border, borderRadius: "8px", padding: "12px 16px",
                borderLeft: `3px solid ${entry.success ? "#00ff9d" : "#ff4d4d"}`,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontWeight: "600", color: "#ddd", fontSize: "0.9rem" }}>{entry.job_name}</span>
                  <span style={{ fontSize: "0.78rem", color: "#888" }}>{formatTs(entry.timestamp)}</span>
                </div>
                <div style={{ marginTop: "6px", fontSize: "0.82rem", color: entry.success ? "#aaa" : "#ff8080" }}>
                  {entry.result || (entry.success ? "Completed" : "Failed")}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── CREATE VIEW ── */}
      {activeView === "create" && (
        <div style={{ maxWidth: "600px" }}>
          <h3 style={{ color: accent, marginBottom: "1.5rem" }}>Create New Schedule</h3>
          <form onSubmit={handleCreate}>
            <label style={labelStyle}>Job Name *</label>
            <input style={inputStyle} placeholder="e.g. Morning Email Check" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />

            <label style={labelStyle}>Agent</label>
            <select style={inputStyle} value={form.agent_id} onChange={e => setForm({ ...form, agent_id: e.target.value })}>
              <option value="orchestrator">orchestrator (auto-route)</option>
              <option value="calendar">calendar</option>
              <option value="home">home</option>
              <option value="finance">finance</option>
            </select>

            <label style={labelStyle}>Task Prompt *</label>
            <textarea style={{ ...inputStyle, minHeight: "80px", resize: "vertical" }} placeholder="e.g. Check my unread emails and summarize them" value={form.prompt} onChange={e => setForm({ ...form, prompt: e.target.value })} required />

            <label style={labelStyle}>Schedule Type</label>
            <select style={inputStyle} value={form.schedule_type} onChange={e => setForm({ ...form, schedule_type: e.target.value })}>
              <option value="cron">Cron (specific time)</option>
              <option value="interval">Interval (every N hours/minutes)</option>
              <option value="one_shot">One-shot (single run)</option>
            </select>

            {form.schedule_type === "cron" && (
              <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                <div style={{ flex: "1 1 100px" }}>
                  <label style={labelStyle}>Hour (0-23)</label>
                  <input style={inputStyle} type="number" min="0" max="23" value={form.hour} onChange={e => setForm({ ...form, hour: e.target.value })} />
                </div>
                <div style={{ flex: "1 1 100px" }}>
                  <label style={labelStyle}>Minute</label>
                  <input style={inputStyle} type="number" min="0" max="59" value={form.minute} onChange={e => setForm({ ...form, minute: e.target.value })} />
                </div>
                <div style={{ flex: "1 1 140px" }}>
                  <label style={labelStyle}>Day of week (* = daily)</label>
                  <select style={inputStyle} value={form.day_of_week} onChange={e => setForm({ ...form, day_of_week: e.target.value })}>
                    <option value="*">Every day</option>
                    <option value="mon-fri">Mon–Fri</option>
                    <option value="mon">Monday</option>
                    <option value="tue">Tuesday</option>
                    <option value="wed">Wednesday</option>
                    <option value="thu">Thursday</option>
                    <option value="fri">Friday</option>
                    <option value="sat">Saturday</option>
                    <option value="sun">Sunday</option>
                  </select>
                </div>
              </div>
            )}

            {form.schedule_type === "interval" && (
              <div style={{ display: "flex", gap: "12px" }}>
                <div style={{ flex: 1 }}>
                  <label style={labelStyle}>Every N hours</label>
                  <input style={inputStyle} type="number" min="0" value={form.hours} onChange={e => setForm({ ...form, hours: e.target.value })} />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={labelStyle}>+ N minutes</label>
                  <input style={inputStyle} type="number" min="0" value={form.minutes} onChange={e => setForm({ ...form, minutes: e.target.value })} />
                </div>
              </div>
            )}

            {form.schedule_type === "one_shot" && (
              <div>
                <label style={labelStyle}>Run at (date & time)</label>
                <input style={inputStyle} type="datetime-local" value={form.run_at} onChange={e => setForm({ ...form, run_at: e.target.value })} required />
              </div>
            )}

            <label style={labelStyle}>Description (shown in job list)</label>
            <input style={inputStyle} placeholder="e.g. Every day at 8:00 AM" value={form.schedule_desc} onChange={e => setForm({ ...form, schedule_desc: e.target.value })} />

            <div style={{ marginTop: "20px", display: "flex", gap: "12px" }}>
              <button
                type="submit"
                style={{ padding: "10px 24px", borderRadius: "8px", border: "none", background: accent, color: "#000", fontWeight: "700", cursor: "pointer", fontSize: "0.9rem" }}
              >
                Create Schedule
              </button>
              <button
                type="button"
                style={{ padding: "10px 20px", borderRadius: "8px", border: `1px solid #888`, background: "transparent", color: "#aaa", cursor: "pointer", fontSize: "0.9rem" }}
                onClick={() => setActiveView("jobs")}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
