import { useSettings } from "../context/SettingsContext";
import { Info } from "lucide-react";

const LLM_LABELS = {
  claude: "Claude (your key)",
  groq: "Groq (fallback)",
};

const MARKET_LABELS = {
  insightsentry: "InsightSentry (your key)",
  yfinance: "Yahoo Finance (fallback)",
};

/**
 * Small inline badge row shown on cards that depend on AI or market data,
 * so the user always knows which provider produced the numbers/text and
 * whether a fallback (less accurate) source is in use.
 */
export default function DataSourceBadge({ showLLM = true, showMarketData = true }) {
  const { llmProvider, marketDataProvider } = useSettings();

  const usingFallback =
    (showLLM && llmProvider === "groq") || (showMarketData && marketDataProvider === "yfinance");

  return (
    <div className="flex flex-wrap items-center gap-2 text-xs">
      {showMarketData && (
        <span
          className={`px-2 py-0.5 rounded-full border ${
            marketDataProvider === "insightsentry"
              ? "bg-green-50 text-green-700 border-green-200"
              : "bg-amber-50 text-amber-700 border-amber-200"
          }`}
        >
          Data: {MARKET_LABELS[marketDataProvider]}
        </span>
      )}
      {showLLM && (
        <span
          className={`px-2 py-0.5 rounded-full border ${
            llmProvider === "claude"
              ? "bg-green-50 text-green-700 border-green-200"
              : "bg-amber-50 text-amber-700 border-amber-200"
          }`}
        >
          AI: {LLM_LABELS[llmProvider]}
        </span>
      )}
      {usingFallback && (
        <span className="flex items-center gap-1 text-slate-500">
          <Info size={12} />
          Using free fallback sources — results may be less accurate or current. Add your own
          keys in Settings for higher quality.
        </span>
      )}
    </div>
  );
}
