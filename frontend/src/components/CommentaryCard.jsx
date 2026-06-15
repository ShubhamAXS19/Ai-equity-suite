import { Sparkles, Loader2, AlertTriangle, RefreshCw, ShieldCheck } from "lucide-react";
import DataSourceBadge from "./DataSourceBadge";

const REVIEWER_NAME = "[Your Name]"; // TODO: replace with your name before sharing this project

export default function CommentaryCard({ commentary, loading, error, cached, onGenerate, onRefresh }) {
  if (!commentary && !loading && !error) {
    return (
      <div
        data-tutorial="commentary-card"
        className="bg-violet-50 rounded-xl border border-violet-200 p-6 flex flex-col items-center justify-center text-center gap-3 min-h-[160px]"
      >
        <Sparkles className="text-violet-400" size={28} />
        <p className="text-sm text-slate-600 max-w-sm">
          Generate an AI commentary identifying notable trends and anomalies in the ratio table
          above, written for a non-technical stakeholder.
        </p>
        <button
          data-tutorial="generate-commentary-btn"
          onClick={onGenerate}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition"
        >
          <Sparkles size={16} /> Generate Commentary
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div
        data-tutorial="commentary-card"
        className="bg-violet-50 rounded-xl border border-violet-200 p-6 flex flex-col items-center justify-center gap-3 min-h-[160px]"
      >
        <Loader2 className="animate-spin text-violet-500" size={28} />
        <p className="text-sm text-slate-500">Analyzing trends...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        data-tutorial="commentary-card"
        className="bg-violet-50 rounded-xl border border-red-200 p-6 flex flex-col items-center justify-center text-center gap-2 min-h-[160px]"
      >
        <AlertTriangle className="text-red-400" size={28} />
        <p className="text-sm text-red-600 font-medium">Couldn't generate commentary</p>
        <p className="text-xs text-slate-500 max-w-md">{error}</p>
        <button
          onClick={onGenerate}
          className="flex items-center gap-2 mt-2 px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition"
        >
          <RefreshCw size={14} /> Try Again
        </button>
      </div>
    );
  }

  return (
    <div data-tutorial="commentary-card" className="bg-violet-50 rounded-xl border border-violet-200 p-6">
      <div className="flex items-start justify-between gap-4 flex-wrap mb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="text-violet-500" size={18} />
          <h3 className="text-sm font-semibold text-violet-800 uppercase tracking-wide">
            AI-Generated Commentary (Reviewed)
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <DataSourceBadge showMarketData={false} />
          <button
            onClick={onRefresh}
            title="Regenerate (bypasses today's cache)"
            className="p-1.5 rounded-lg border border-violet-200 hover:bg-violet-100 text-violet-500"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      <div className="mb-3 flex items-center gap-2 px-3 py-2 rounded-lg bg-white/70 border border-violet-100 text-xs text-violet-700">
        <ShieldCheck size={14} />
        AI-generated — reviewed by {REVIEWER_NAME}
        {cached && <span className="text-slate-400 ml-2">(cached for today)</span>}
      </div>

      <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">{commentary}</p>
    </div>
  );
}
