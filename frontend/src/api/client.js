const API_BASE = `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api`;

/**
 * Reads the user's API keys from localStorage and returns the headers
 * that should be attached to every backend request. If a key is empty,
 * the header is omitted entirely, and the backend falls back to
 * Groq (for LLM) or yfinance (for market data).
 */
function buildHeaders(extra = {}) {
  const claudeKey = localStorage.getItem("claude_api_key") || "";
  const insightSentryKey = localStorage.getItem("insightsentry_api_key") || "";

  const headers = { "Content-Type": "application/json", ...extra };
  if (claudeKey.trim()) headers["X-Claude-Key"] = claudeKey.trim();
  if (insightSentryKey.trim()) headers["X-InsightSentry-Key"] = insightSentryKey.trim();
  return headers;
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: buildHeaders(options.headers),
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch (_) {
      // ignore JSON parse errors on error body
    }
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }

  return res.json();
}

export const api = {
  getCompanies: () => request("/companies"),

  getSnapshot: (ticker) => request(`/research/company/${ticker}/snapshot`),

  getBrief: (ticker, { promptVersion, forceRefresh } = {}) => {
    const params = new URLSearchParams();
    if (promptVersion) params.set("prompt_version", promptVersion);
    if (forceRefresh) params.set("force_refresh", "true");
    const qs = params.toString();
    return request(`/research/company/${ticker}/brief${qs ? `?${qs}` : ""}`, {
      method: "POST",
    });
  },

  getPromptVersions: () => request("/research/prompt-versions"),

  getRatios: (ticker) => request(`/analyzer/company/${ticker}/ratios`),

  getCommentary: (ticker, { forceRefresh } = {}) => {
    const params = new URLSearchParams();
    if (forceRefresh) params.set("force_refresh", "true");
    const qs = params.toString();
    return request(`/analyzer/company/${ticker}/commentary${qs ? `?${qs}` : ""}`, {
      method: "POST",
    });
  },

  // --- News Monitor ---
  getWatchlist: () => request("/news/watchlist"),

  addToWatchlist: (ticker) =>
    request("/news/watchlist", { method: "POST", body: JSON.stringify({ ticker }) }),

  removeFromWatchlist: (ticker) =>
    request(`/news/watchlist/${ticker}`, { method: "DELETE" }),

  fetchNews: () => request("/news/fetch"),

  summarizeNews: () => request("/news/summarize", { method: "POST" }),

  getDigest: ({ company, materiality, category, digestDate } = {}) => {
    const params = new URLSearchParams();
    if (company) params.set("company", company);
    if (materiality) params.set("materiality", materiality);
    if (category) params.set("category", category);
    if (digestDate) params.set("digest_date", digestDate);
    const qs = params.toString();
    return request(`/news/digest${qs ? `?${qs}` : ""}`);
  },

  getDigestDates: () => request("/news/digest-dates"),

  getSettingsStatus: () => request("/settings/status"),

  checkClaudeKey: (key) =>
    request("/settings/check-claude-key", {
      method: "POST",
      body: JSON.stringify({ key }),
    }),

  checkInsightSentryKey: (key) =>
    request("/settings/check-insightsentry-key", {
      method: "POST",
      body: JSON.stringify({ key }),
    }),
};

export { API_BASE };
