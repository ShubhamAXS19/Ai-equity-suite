import { ExternalLink } from "lucide-react";

const MATERIALITY_STYLES = {
  High: "bg-red-100 text-red-700 border-red-200",
  Medium: "bg-amber-100 text-amber-700 border-amber-200",
  Low: "bg-green-100 text-green-700 border-green-200",
};

const CATEGORY_STYLES = {
  Earnings: "bg-blue-50 text-blue-700 border-blue-200",
  "M&A": "bg-purple-50 text-purple-700 border-purple-200",
  Regulatory: "bg-indigo-50 text-indigo-700 border-indigo-200",
  "Leadership Change": "bg-teal-50 text-teal-700 border-teal-200",
  Other: "bg-slate-50 text-slate-600 border-slate-200",
};

function formatDate(iso) {
  if (!iso) return "";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
  } catch {
    return iso;
  }
}

export default function NewsArticleCard({ article }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
      <div className="flex items-start justify-between gap-3 flex-wrap mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={`px-2 py-0.5 rounded-full border text-xs font-medium ${
              MATERIALITY_STYLES[article.materiality] || MATERIALITY_STYLES.Low
            }`}
          >
            {article.materiality} Materiality
          </span>
          <span
            className={`px-2 py-0.5 rounded-full border text-xs font-medium ${
              CATEGORY_STYLES[article.category] || CATEGORY_STYLES.Other
            }`}
          >
            {article.category}
          </span>
          <span className="text-xs text-slate-400">{article.ticker}</span>
        </div>
        <span className="text-xs text-slate-400">{formatDate(article.published)}</span>
      </div>

      <a
        href={article.link}
        target="_blank"
        rel="noreferrer"
        className="text-sm font-medium text-slate-800 hover:text-brand-600 flex items-start gap-1.5 mb-1.5"
      >
        {article.title}
        <ExternalLink size={12} className="mt-0.5 flex-shrink-0" />
      </a>

      {article.summary && <p className="text-sm text-slate-600 leading-relaxed mb-1.5">{article.summary}</p>}

      <p className="text-xs text-slate-400">{article.source}</p>
    </div>
  );
}
