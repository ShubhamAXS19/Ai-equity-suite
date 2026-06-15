import { Loader2, AlertTriangle } from "lucide-react";
import DataSourceBadge from "./DataSourceBadge";

function fmtCurrency(value) {
  if (value === null || value === undefined) return "—";
  if (Math.abs(value) >= 1e12) return `₹${(value / 1e12).toFixed(2)}T`;
  if (Math.abs(value) >= 1e9) return `₹${(value / 1e9).toFixed(2)}B`;
  if (Math.abs(value) >= 1e7) return `₹${(value / 1e7).toFixed(2)}Cr`;
  return `₹${value.toLocaleString("en-IN")}`;
}

function fmtPct(value) {
  if (value === null || value === undefined) return "—";
  return `${value}%`;
}

function fmtRatio(value) {
  if (value === null || value === undefined) return "—";
  return `${value}x`;
}

const COLUMNS = [
  { key: "revenue", label: "Revenue", fmt: fmtCurrency },
  { key: "net_profit", label: "Net Profit", fmt: fmtCurrency },
  { key: "gross_margin_pct", label: "Gross Margin", fmt: fmtPct },
  { key: "operating_margin_pct", label: "Operating Margin", fmt: fmtPct },
  { key: "net_margin_pct", label: "Net Margin", fmt: fmtPct },
  { key: "current_ratio", label: "Current Ratio", fmt: fmtRatio },
  { key: "debt_to_equity", label: "Debt-to-Equity", fmt: fmtRatio },
  { key: "roe_pct", label: "ROE", fmt: fmtPct },
  { key: "interest_coverage", label: "Interest Coverage", fmt: fmtRatio },
];

export default function RatioTable({ data, loading, error, warning, cached }) {
  if (loading) {
    return (
      <div
        data-tutorial="ratio-table"
        className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center justify-center min-h-[260px]"
      >
        <Loader2 className="animate-spin text-brand-500" size={28} />
      </div>
    );
  }

  if (error) {
    return (
      <div
        data-tutorial="ratio-table"
        className="bg-white rounded-xl shadow-sm border border-red-200 p-6 min-h-[200px] flex flex-col items-center justify-center text-center gap-2"
      >
        <AlertTriangle className="text-red-400" size={28} />
        <p className="text-sm text-red-600 font-medium">Couldn't load financial data</p>
        <p className="text-xs text-slate-500">{error}</p>
      </div>
    );
  }

  if (!data || !data.ratio_table || data.ratio_table.length === 0) {
    return (
      <div
        data-tutorial="ratio-table"
        className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 min-h-[200px] flex items-center justify-center text-slate-400 text-sm"
      >
        No financial data available
      </div>
    );
  }

  // ratio_table is most-recent-first; show oldest-to-newest left-to-right
  const years = [...data.ratio_table].reverse();

  return (
    <div data-tutorial="ratio-table" className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-start justify-between mb-4 gap-4 flex-wrap">
        <div>
          <h3 className="text-lg font-semibold text-slate-800">{data.company?.name}</h3>
          <p className="text-sm text-slate-400">{data.company?.ticker}</p>
        </div>
        <DataSourceBadge showLLM={false} />
      </div>

      {(warning || cached) && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-700 flex items-center gap-2">
          <AlertTriangle size={14} />
          {warning || "Showing cached data from a previous fetch."}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left py-2 pr-4 font-medium text-slate-500">Metric</th>
              {years.map((row) => (
                <th key={row.year} className="text-right py-2 px-3 font-medium text-slate-500">
                  {row.year}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {COLUMNS.map((col) => (
              <tr key={col.key} className="border-b border-slate-100 last:border-0">
                <td className="py-2 pr-4 text-slate-600">{col.label}</td>
                {years.map((row) => (
                  <td key={row.year} className="text-right py-2 px-3 font-medium text-slate-800">
                    {col.fmt(row[col.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
