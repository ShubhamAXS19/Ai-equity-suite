import { Sparkles, Loader2, AlertTriangle, RefreshCw, ShieldCheck } from "lucide-react";
import DataSourceBadge from "./DataSourceBadge";

const REVIEWER_NAME = "[Your Name]"; // TODO: replace with your name before sharing this project

export default function BriefCard({ brief, loading, error, dataSources, cached, onGenerate, onRefresh }) {
  if (!brief && !loading && !error) {
    return (
      <div
        data-tutorial="brief-card"
        className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center text-center gap-3 min-h-[200px]"
      >
        <Sparkles className="text-brand-400" size={28} />
        <p className="text-sm text-slate-500 max-w-sm">
          Generate a one-page AI research brief covering business overview, financial
          interpretation, recent developments, and key risks.
        </p>
        <button
          data-tutorial="generate-brief-btn"
          onClick={onGenerate}
          className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition"
        >
          <Sparkles size={16} /> Generate Brief
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div
        data-tutorial="brief-card"
        className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center gap-3 min-h-[200px]"
      >
        <Loader2 className="animate-spin text-brand-500" size={28} />
        <p className="text-sm text-slate-500">Generating research brief...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        data-tutorial="brief-card"
        className="bg-white rounded-xl shadow-sm border border-red-200 p-6 flex flex-col items-center justify-center text-center gap-2 min-h-[200px]"
      >
        <AlertTriangle className="text-red-400" size={28} />
        <p className="text-sm text-red-600 font-medium">Couldn't generate brief</p>
        <p className="text-xs text-slate-500 max-w-md">{error}</p>
        <button
          onClick={onGenerate}
          className="flex items-center gap-2 mt-2 px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition"
        >
          <RefreshCw size={14} /> Try Again
        </button>
      </div>
    );
  }

  const isUnstructured = brief._unstructured;

  return (
    <div data-tutorial="brief-card" className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-start justify-between gap-4 flex-wrap mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="text-brand-500" size={18} />
          <h3 className="text-lg font-semibold text-slate-800">AI Research Brief</h3>
        </div>
        <div className="flex items-center gap-2">
          <DataSourceBadge showMarketData={false} />
          <button
            onClick={onRefresh}
            title="Regenerate (bypasses today's cache)"
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-500"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      <div className="mb-4 flex items-center gap-2 px-3 py-2 rounded-lg bg-brand-50 border border-brand-100 text-xs text-brand-700">
        <ShieldCheck size={14} />
        AI-generated — reviewed by {REVIEWER_NAME}
        {cached && <span className="text-slate-400 ml-2">(cached for today)</span>}
      </div>

      {isUnstructured ? (
        <div className="space-y-2">
          <p className="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            This prompt version didn't return a structured response, so the raw output is shown
            below as-is.
          </p>
          <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
            {brief.business_overview}
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          <Section title="Business Overview">
            <p className="text-sm text-slate-700 leading-relaxed">{brief.business_overview}</p>
          </Section>

          <Section title="Financial Snapshot">
            <p className="text-sm text-slate-700 leading-relaxed">{brief.financial_snapshot}</p>
          </Section>

          <Section title="Recent Developments">
            <p className="text-xs text-slate-400 mb-1.5">
              Based on general knowledge — placeholder for a live news feed.
            </p>
            <ul className="list-disc list-inside space-y-1 text-sm text-slate-700">
              {(brief.recent_developments || []).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </Section>

          <Section title="Key Risks">
            <ul className="list-disc list-inside space-y-1 text-sm text-slate-700">
              {(brief.key_risks || []).map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </Section>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div>
      <h4 className="text-sm font-semibold text-slate-800 mb-1.5 uppercase tracking-wide text-xs">
        {title}
      </h4>
      {children}
    </div>
  );
}
