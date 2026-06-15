import { useState } from "react";
import { X, CheckCircle2, XCircle, Loader2, KeyRound, HelpCircle } from "lucide-react";
import { useSettings } from "../context/SettingsContext";
import { api } from "../api/client";

export default function SettingsPanel({ open, onClose, onOpenTutorial }) {
  const { claudeKey, insightSentryKey, updateClaudeKey, updateInsightSentryKey, serverStatus } =
    useSettings();

  const [claudeInput, setClaudeInput] = useState(claudeKey);
  const [insightInput, setInsightInput] = useState(insightSentryKey);
  const [claudeStatus, setClaudeStatus] = useState(null); // null | 'checking' | 'valid' | 'invalid'
  const [insightStatus, setInsightStatus] = useState(null);

  if (!open) return null;

  const handleSaveClaude = async () => {
    if (!claudeInput.trim()) {
      updateClaudeKey("");
      setClaudeStatus(null);
      return;
    }
    setClaudeStatus("checking");
    try {
      const res = await api.checkClaudeKey(claudeInput.trim());
      if (res.valid) {
        updateClaudeKey(claudeInput.trim());
        setClaudeStatus("valid");
      } else {
        setClaudeStatus("invalid");
      }
    } catch {
      setClaudeStatus("invalid");
    }
  };

  const handleSaveInsight = async () => {
    if (!insightInput.trim()) {
      updateInsightSentryKey("");
      setInsightStatus(null);
      return;
    }
    setInsightStatus("checking");
    try {
      const res = await api.checkInsightSentryKey(insightInput.trim());
      if (res.valid) {
        updateInsightSentryKey(insightInput.trim());
        setInsightStatus("valid");
      } else {
        setInsightStatus("invalid");
      }
    } catch {
      setInsightStatus("invalid");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative w-full max-w-md bg-white h-full shadow-xl p-6 overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <KeyRound size={18} /> Settings
          </h2>
          <button onClick={onClose} className="p-1 rounded hover:bg-slate-100">
            <X size={18} />
          </button>
        </div>

        <p className="text-sm text-slate-500 mb-6">
          Bring your own API keys for better accuracy, or leave them blank to use the built-in
          free fallbacks (Groq for AI, Yahoo Finance for market data). Keys are stored only in
          your browser (localStorage) and sent directly to our backend per-request — never saved
          on the server.
        </p>

        <button
          onClick={onOpenTutorial}
          className="w-full mb-6 flex items-center justify-center gap-2 text-sm text-brand-600 border border-brand-200 bg-brand-50 rounded-lg py-2 hover:bg-brand-100 transition"
        >
          <HelpCircle size={16} /> Replay the interactive tutorial
        </button>

        {/* Claude key */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-1">Claude API Key</label>
          <p className="text-xs text-slate-500 mb-2">
            Used to generate research briefs, financial commentary, and news summaries with
            Anthropic's Claude. Get a key at{" "}
            <a
              href="https://console.anthropic.com/"
              target="_blank"
              rel="noreferrer"
              className="text-brand-600 underline"
            >
              console.anthropic.com
            </a>
            . Without this, the app uses Groq's free Llama 3.3 model — capable, but generally
            less accurate and nuanced than Claude for financial analysis.
          </p>
          <div className="flex gap-2">
            <input
              type="password"
              value={claudeInput}
              onChange={(e) => setClaudeInput(e.target.value)}
              placeholder="sk-ant-..."
              className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <button
              onClick={handleSaveClaude}
              className="px-3 py-2 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700"
            >
              Save
            </button>
          </div>
          <StatusLine status={claudeStatus} validLabel="Claude key verified" />
          {!claudeKey.trim() && (
            <p className="text-xs text-amber-600 mt-1">
              No Claude key set — falling back to Groq{" "}
              {serverStatus.groq_fallback_available ? "(available)" : "(not configured on server)"}
              .
            </p>
          )}
        </div>

        {/* InsightSentry key */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-1">InsightSentry API Key</label>
          <p className="text-xs text-slate-500 mb-2">
            InsightSentry provides real-time and fundamental market data for NSE stocks. Without
            this, the app uses the free yfinance library, which can be slower, occasionally rate
            limited, or slightly delayed compared to a paid data provider.
          </p>
          <div className="flex gap-2">
            <input
              type="password"
              value={insightInput}
              onChange={(e) => setInsightInput(e.target.value)}
              placeholder="Your InsightSentry API key"
              className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <button
              onClick={handleSaveInsight}
              className="px-3 py-2 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700"
            >
              Save
            </button>
          </div>
          <StatusLine status={insightStatus} validLabel="Key saved" />
          {!insightSentryKey.trim() && (
            <p className="text-xs text-amber-600 mt-1">
              No InsightSentry key set — using yfinance for market data.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function StatusLine({ status, validLabel }) {
  if (status === "checking")
    return (
      <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
        <Loader2 size={12} className="animate-spin" /> Checking key...
      </p>
    );
  if (status === "valid")
    return (
      <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
        <CheckCircle2 size={12} /> {validLabel}
      </p>
    );
  if (status === "invalid")
    return (
      <p className="text-xs text-red-600 mt-1 flex items-center gap-1">
        <XCircle size={12} /> Couldn't verify this key — check it and try again.
      </p>
    );
  return null;
}
