import { TrendingUp, TrendingDown, Loader2, AlertTriangle } from "lucide-react";
import DataSourceBadge from "./DataSourceBadge";

function formatCurrency(value, currency = "INR") {
  if (value === null || value === undefined) return "—";
  if (Math.abs(value) >= 1e12) return `₹${(value / 1e12).toFixed(2)}T`;
  if (Math.abs(value) >= 1e9) return `₹${(value / 1e9).toFixed(2)}B`;
  if (Math.abs(value) >= 1e7) return `₹${(value / 1e7).toFixed(2)}Cr`;
  return `₹${value.toLocaleString("en-IN")}`;
}

function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined) return "—";
  return value.toFixed(decimals);
}

function GrowthBadge({ value }) {
  if (value === null || value === undefined) {
    return <span className="text-slate-400 text-sm">—</span>;
  }
  const positive = value >= 0;
  const Icon = positive ? TrendingUp : TrendingDown;
  return (
    <span
      className={`inline-flex items-center gap-1 text-sm font-medium ${
        positive ? "text-green-600" : "text-red-600"
      }`}
    >
      <Icon size={14} />
      {positive ? "+" : ""}
      {value.toFixed(1)}%
    </span>
  );
}

export default function SnapshotCard({ snapshot, loading, error, warning, cached }) {
  if (loading) {
    return (
      <div
        data-tutorial="snapshot-card"
        className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center justify-center min-h-[260px]"
      >
        <Loader2 className="animate-spin text-brand-500" size={28} />
      </div>
    );
  }

  if (error) {
    return (
      <div
        data-tutorial="snapshot-card"
        className="bg-white rounded-xl shadow-sm border border-red-200 p-6 min-h-[260px] flex flex-col items-center justify-center text-center gap-2"
      >
        <AlertTriangle className="text-red-400" size={28} />
        <p className="text-sm text-red-600 font-medium">Couldn't load snapshot</p>
        <p className="text-xs text-slate-500">{error}</p>
      </div>
    );
  }

  if (!snapshot) {
    return (
      <div
        data-tutorial="snapshot-card"
        className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 min-h-[260px] flex items-center justify-center text-slate-400 text-sm"
      >
        Select a company to view its snapshot
      </div>
    );
  }

  const stats = [
    { label: "Current Price", value: formatCurrency(snapshot.current_price, snapshot.currency) },
    { label: "Market Cap", value: formatCurrency(snapshot.market_cap, snapshot.currency) },
    { label: "P/E Ratio", value: formatNumber(snapshot.pe_ratio) },
    { label: "P/B Ratio", value: formatNumber(snapshot.pb_ratio) },
    {
      label: "52-Week Range",
      value: `${formatNumber(snapshot.week52_low, 2)} – ${formatNumber(snapshot.week52_high, 2)}`,
    },
    {
      label: `Revenue (${snapshot.fiscal_year || "Latest FY"})`,
      value: formatCurrency(snapshot.latest_revenue, snapshot.currency),
      growth: snapshot.revenue_yoy_growth,
    },
    {
      label: `Net Profit (${snapshot.fiscal_year || "Latest FY"})`,
      value: formatCurrency(snapshot.latest_net_profit, snapshot.currency),
      growth: snapshot.net_profit_yoy_growth,
    },
  ];

  return (
    <div
      data-tutorial="snapshot-card"
      className="bg-white rounded-xl shadow-sm border border-slate-200 p-6"
    >
      <div className="flex items-start justify-between mb-4 gap-4 flex-wrap">
        <div>
          <h3 className="text-lg font-semibold text-slate-800">{snapshot.name}</h3>
          <p className="text-sm text-slate-400">{snapshot.ticker}</p>
        </div>
        <DataSourceBadge showLLM={false} />
      </div>

      {(warning || cached) && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-700 flex items-center gap-2">
          <AlertTriangle size={14} />
          {warning || "Showing cached data from a previous fetch."}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {stats.map((s) => (
          <div key={s.label} className="border border-slate-100 rounded-lg p-3">
            <p className="text-xs text-slate-400 mb-1">{s.label}</p>
            <div className="flex items-center gap-2">
              <p className="text-base font-semibold text-slate-800">{s.value}</p>
              {"growth" in s && <GrowthBadge value={s.growth} />}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
