import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:5000/api";

export default function TemplateBrowser({ showNotification }) {
  const [templates, setTemplates] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchTemplates();
  }, [selectedCategory, selectedDifficulty]);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      let url = `${API_URL}/templates`;
      const params = [];

      if (selectedCategory !== "all") {
        params.push(`category=${selectedCategory}`);
      }
      if (selectedDifficulty !== "all") {
        params.push(`difficulty=${selectedDifficulty}`);
      }

      if (params?.length > 0) {
        url += `?${params.join("&")}`;
      }

      const response = await fetch(url);
      const data = await response.json();

      setTemplates(data.templates || []);
      setCategories(data.categories || []);
    } catch (error) {
      console.error("Error fetching templates:", error);
      showNotification?.("Failed to fetch templates", "error");
    } finally {
      setLoading(false);
    }
  };

  const searchTemplates = async () => {
    if (!searchQuery.trim()) {
      fetchTemplates();
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(
        `${API_URL}/templates/search?q=${encodeURIComponent(searchQuery)}`
      );
      const data = await response.json();
      setTemplates(data.results || []);
    } catch (error) {
      console.error("Error searching templates:", error);
      showNotification?.("Failed to search templates", "error");
    } finally {
      setLoading(false);
    }
  };

  const createAgentFromTemplate = async (templateId) => {
    setCreating(true);
    showNotification?.("Creating agent from template...", "info");

    try {
      const response = await fetch(
        `${API_URL}/templates/${templateId}/create-agent`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: "default_user" }),
        }
      );

      const data = await response.json();

      if (data.success) {
        showNotification?.(
          `✅ Agent "${data.agent.name}" created successfully!`,
          "success"
        );
        setSelectedTemplate(null);
      } else {
        showNotification?.(`❌ ${data.error}`, "error");
      }
    } catch (error) {
      console.error("Error creating agent:", error);
      showNotification?.("Failed to create agent", "error");
    } finally {
      setCreating(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case "beginner":
        return "#4caf50";
      case "intermediate":
        return "#ff9800";
      case "advanced":
        return "#f44336";
      default:
        return "#667eea";
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      Utility: "🔧",
      Business: "💼",
      Home: "🏠",
      Finance: "💰",
      Productivity: "📊",
      Analytics: "📈",
      Lifestyle: "🎯",
      Security: "🔒",
    };
    return icons[category] || "📦";
  };

  const filteredTemplates = templates.filter((template) => {
    if (searchQuery) {
      return true; // Already filtered by search
    }
    return true;
  });

  return (
    <div style={{ padding: "2rem" }}>
      <h2 style={{ marginBottom: "2rem" }}>📚 Agent Template Library</h2>

      {/* Search and Filters */}
      <div
        style={{
          background: "white",
          border: "2px solid #e0e0e0",
          borderRadius: "10px",
          padding: "1.5rem",
          marginBottom: "2rem",
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "2fr 1fr 1fr",
            gap: "1rem",
            marginBottom: "1rem",
          }}
        >
          {/* Search */}
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <input
              type="text"
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && searchTemplates()}
              style={{
                flex: 1,
                padding: "0.75rem",
                border: "2px solid #ddd",
                borderRadius: "6px",
                fontSize: "0.95rem",
              }}
            />
            <button
              onClick={searchTemplates}
              className="primary-btn"
              style={{ padding: "0.75rem 1.5rem" }}
            >
              🔍 Search
            </button>
          </div>

          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setSearchQuery("");
            }}
            style={{
              padding: "0.75rem",
              border: "2px solid #ddd",
              borderRadius: "6px",
              fontSize: "0.95rem",
            }}
          >
            <option value="all">All Categories</option>
            {categories?.map((cat) => (
              <option key={cat} value={cat}>
                {getCategoryIcon(cat)} {cat}
              </option>
            ))}
          </select>

          {/* Difficulty Filter */}
          <select
            value={selectedDifficulty}
            onChange={(e) => {
              setSelectedDifficulty(e.target.value);
              setSearchQuery("");
            }}
            style={{
              padding: "0.75rem",
              border: "2px solid #ddd",
              borderRadius: "6px",
              fontSize: "0.95rem",
            }}
          >
            <option value="all">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <div style={{ fontSize: "0.9rem", color: "#666" }}>
          {filteredTemplates?.length} template(s) found
        </div>
      </div>

      {/* Templates Grid */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>⏳</div>
          <div style={{ fontSize: "1.1rem", color: "#666" }}>
            Loading templates...
          </div>
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
            gap: "1.5rem",
          }}
        >
          {filteredTemplates?.map((template) => (
            <div
              key={template.template_id}
              onClick={() => setSelectedTemplate(template)}
              style={{
                background: "white",
                border: "2px solid #e0e0e0",
                borderRadius: "12px",
                padding: "1.5rem",
                cursor: "pointer",
                transition: "all 0.3s ease",
                position: "relative",
                overflow: "hidden",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#667eea";
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow =
                  "0 8px 16px rgba(102, 126, 234, 0.2)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "#e0e0e0";
                e.currentTarget.style.transform = "none";
                e.currentTarget.style.boxShadow = "none";
              }}
            >
              {/* Category Badge */}
              <div
                style={{
                  position: "absolute",
                  top: "1rem",
                  right: "1rem",
                  background: "#667eea",
                  color: "white",
                  padding: "0.25rem 0.75rem",
                  borderRadius: "12px",
                  fontSize: "0.75rem",
                  fontWeight: "bold",
                }}
              >
                {getCategoryIcon(template.category)} {template.category}
              </div>

              {/* Content */}
              <div style={{ marginTop: "1rem" }}>
                <h3
                  style={{
                    margin: "0 0 0.5rem 0",
                    color: "#333",
                    fontSize: "1.2rem",
                  }}
                >
                  {template.name}
                </h3>
                <div
                  style={{
                    color: "#666",
                    fontSize: "0.9rem",
                    marginBottom: "1rem",
                    fontStyle: "italic",
                  }}
                >
                  {template.role}
                </div>
                <p
                  style={{
                    color: "#666",
                    fontSize: "0.9rem",
                    lineHeight: "1.6",
                    marginBottom: "1rem",
                  }}
                >
                  {template.description}
                </p>

                {/* Tags */}
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "0.5rem",
                    marginBottom: "1rem",
                  }}
                >
                  {template.tags?.slice(0, 3)?.map((tag, index) => (
                    <span
                      key={index}
                      style={{
                        background: "#f8f9ff",
                        color: "#667eea",
                        padding: "0.25rem 0.5rem",
                        borderRadius: "4px",
                        fontSize: "0.75rem",
                      }}
                    >
                      #{tag}
                    </span>
                  ))}
                </div>

                {/* Difficulty Badge */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <span
                    style={{
                      padding: "0.3rem 0.75rem",
                      borderRadius: "12px",
                      fontSize: "0.8rem",
                      fontWeight: "bold",
                      background: getDifficultyColor(template.difficulty),
                      color: "white",
                    }}
                  >
                    {template.difficulty}
                  </span>
                  <span style={{ fontSize: "0.85rem", color: "#999" }}>
                    {template.tools?.length} tool(s)
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Template Details Modal */}
      {selectedTemplate && (
        <div
          onClick={() => setSelectedTemplate(null)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            backdropFilter: "blur(4px)",
            padding: "2rem",
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "white",
              borderRadius: "15px",
              padding: "2rem",
              maxWidth: "700px",
              width: "100%",
              maxHeight: "90vh",
              overflowY: "auto",
              boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
            }}
          >
            {/* Header */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "start",
                marginBottom: "1.5rem",
              }}
            >
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                    marginBottom: "0.5rem",
                  }}
                >
                  <span style={{ fontSize: "2rem" }}>
                    {getCategoryIcon(selectedTemplate.category)}
                  </span>
                  <h2 style={{ margin: 0 }}>{selectedTemplate.name}</h2>
                </div>
                <div
                  style={{
                    color: "#666",
                    fontSize: "1rem",
                    fontStyle: "italic",
                  }}
                >
                  {selectedTemplate.role}
                </div>
              </div>
              <button
                onClick={() => setSelectedTemplate(null)}
                style={{
                  background: "transparent",
                  border: "none",
                  fontSize: "1.5rem",
                  cursor: "pointer",
                  padding: "0.25rem",
                  color: "#999",
                }}
              >
                ✕
              </button>
            </div>

            {/* Badges */}
            <div
              style={{
                display: "flex",
                gap: "0.75rem",
                marginBottom: "1.5rem",
                flexWrap: "wrap",
              }}
            >
              <span
                style={{
                  background: "#667eea",
                  color: "white",
                  padding: "0.4rem 0.9rem",
                  borderRadius: "20px",
                  fontSize: "0.85rem",
                  fontWeight: "bold",
                }}
              >
                {selectedTemplate.category}
              </span>
              <span
                style={{
                  background: getDifficultyColor(selectedTemplate.difficulty),
                  color: "white",
                  padding: "0.4rem 0.9rem",
                  borderRadius: "20px",
                  fontSize: "0.85rem",
                  fontWeight: "bold",
                }}
              >
                {selectedTemplate.difficulty}
              </span>
            </div>

            {/* Description */}
            <div style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ color: "#667eea", marginBottom: "0.75rem" }}>
                📝 Description
              </h3>
              <p style={{ color: "#666", lineHeight: "1.6" }}>
                {selectedTemplate.description}
              </p>
            </div>

            {/* System Instructions */}
            <div style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ color: "#667eea", marginBottom: "0.75rem" }}>
                🎯 System Instructions
              </h3>
              <div
                style={{
                  background: "#f8f9ff",
                  padding: "1rem",
                  borderRadius: "8px",
                  border: "2px solid #e0e0e0",
                  color: "#666",
                  lineHeight: "1.6",
                  fontSize: "0.95rem",
                }}
              >
                {selectedTemplate.system_instructions}
              </div>
            </div>

            {/* Tools */}
            <div style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ color: "#667eea", marginBottom: "0.75rem" }}>
                🔧 Included Tools ({selectedTemplate.tools?.length})
              </h3>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {selectedTemplate.tools?.map((tool, index) => (
                  <span
                    key={index}
                    style={{
                      background: "#e8f5e9",
                      color: "#2e7d32",
                      padding: "0.5rem 1rem",
                      borderRadius: "6px",
                      fontSize: "0.85rem",
                      fontWeight: "500",
                    }}
                  >
                    {tool}
                  </span>
                ))}
              </div>
            </div>

            {/* Tags */}
            <div style={{ marginBottom: "2rem" }}>
              <h3 style={{ color: "#667eea", marginBottom: "0.75rem" }}>
                🏷️ Tags
              </h3>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {selectedTemplate.tags?.map((tag, index) => (
                  <span
                    key={index}
                    style={{
                      background: "#f8f9ff",
                      color: "#667eea",
                      padding: "0.4rem 0.8rem",
                      borderRadius: "6px",
                      fontSize: "0.85rem",
                    }}
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Create Button */}
            <div
              style={{
                display: "flex",
                gap: "1rem",
                borderTop: "2px solid #f0f0f0",
                paddingTop: "1.5rem",
              }}
            >
              <button
                onClick={() =>
                  createAgentFromTemplate(selectedTemplate.template_id)
                }
                disabled={creating}
                className="primary-btn"
                style={{
                  flex: 1,
                  padding: "1rem",
                  fontSize: "1rem",
                  fontWeight: "bold",
                }}
              >
                {creating ? "⏳ Creating..." : "✨ Create Agent from Template"}
              </button>
              <button
                onClick={() => setSelectedTemplate(null)}
                className="secondary-btn"
                style={{ padding: "1rem" }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredTemplates?.length === 0 && (
        <div
          style={{
            background: "#f8f9ff",
            border: "2px dashed #667eea",
            borderRadius: "10px",
            padding: "3rem",
            textAlign: "center",
            color: "#666",
          }}
        >
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🔍</div>
          <div style={{ fontSize: "1.1rem" }}>No templates found</div>
          <div style={{ fontSize: "0.9rem", marginTop: "0.5rem" }}>
            Try adjusting your filters or search query
          </div>
        </div>
      )}
    </div>
  );
}
