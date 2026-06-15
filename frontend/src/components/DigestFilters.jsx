import { Calendar } from "lucide-react";

const MATERIALITY_OPTIONS = ["High", "Medium", "Low"];
const CATEGORY_OPTIONS = ["Earnings", "M&A", "Regulatory", "Leadership Change", "Other"];

export default function DigestFilters({ companies, watchlist, filters, onChange, digestDates }) {
  const watchlistTickers = new Set(watchlist.map((w) => w.ticker));
  const watchlistCompanies = companies.filter((c) => watchlistTickers.has(c.ticker));

  return (
    <div data-tutorial="digest-filters" className="flex flex-wrap items-center gap-2">
      <select
        value={filters.company || ""}
        onChange={(e) => onChange({ ...filters, company: e.target.value || undefined })}
        className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        <option value="">All companies</option>
        {watchlistCompanies.map((c) => (
          <option key={c.ticker} value={c.ticker}>
            {c.name}
          </option>
        ))}
      </select>

      <select
        value={filters.materiality || ""}
        onChange={(e) => onChange({ ...filters, materiality: e.target.value || undefined })}
        className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        <option value="">All materiality</option>
        {MATERIALITY_OPTIONS.map((m) => (
          <option key={m} value={m}>
            {m}
          </option>
        ))}
      </select>

      <select
        value={filters.category || ""}
        onChange={(e) => onChange({ ...filters, category: e.target.value || undefined })}
        className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        <option value="">All categories</option>
        {CATEGORY_OPTIONS.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      {digestDates && digestDates.length > 0 && (
        <div className="flex items-center gap-1.5">
          <Calendar size={14} className="text-slate-400" />
          <select
            value={filters.digestDate || digestDates[0]}
            onChange={(e) => onChange({ ...filters, digestDate: e.target.value })}
            className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            {digestDates.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}
