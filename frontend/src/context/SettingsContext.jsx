import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api } from "../api/client";

const SettingsContext = createContext(null);

export function SettingsProvider({ children }) {
  const [claudeKey, setClaudeKey] = useState(() => localStorage.getItem("claude_api_key") || "");
  const [insightSentryKey, setInsightSentryKey] = useState(
    () => localStorage.getItem("insightsentry_api_key") || ""
  );
  const [serverStatus, setServerStatus] = useState({
    groq_fallback_available: false,
    insightsentry_server_fallback_available: false,
  });
  const [tutorialSeen, setTutorialSeen] = useState(
    () => localStorage.getItem("tutorial_seen") === "true"
  );

  useEffect(() => {
    api.getSettingsStatus().then(setServerStatus).catch(() => {});
  }, []);

  const updateClaudeKey = useCallback((key) => {
    setClaudeKey(key);
    if (key.trim()) {
      localStorage.setItem("claude_api_key", key.trim());
    } else {
      localStorage.removeItem("claude_api_key");
    }
  }, []);

  const updateInsightSentryKey = useCallback((key) => {
    setInsightSentryKey(key);
    if (key.trim()) {
      localStorage.setItem("insightsentry_api_key", key.trim());
    } else {
      localStorage.removeItem("insightsentry_api_key");
    }
  }, []);

  const markTutorialSeen = useCallback(() => {
    setTutorialSeen(true);
    localStorage.setItem("tutorial_seen", "true");
  }, []);

  const resetTutorial = useCallback(() => {
    setTutorialSeen(false);
    localStorage.removeItem("tutorial_seen");
  }, []);

  // Derived: which providers are actually active for this user/session
  const llmProvider = claudeKey.trim() ? "claude" : (serverStatus.groq_fallback_available ? "groq" : "groq");
  const marketDataProvider = insightSentryKey.trim() ? "insightsentry" : "yfinance";

  const value = {
    claudeKey,
    insightSentryKey,
    updateClaudeKey,
    updateInsightSentryKey,
    serverStatus,
    llmProvider,
    marketDataProvider,
    tutorialSeen,
    markTutorialSeen,
    resetTutorial,
  };

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error("useSettings must be used within SettingsProvider");
  return ctx;
}
