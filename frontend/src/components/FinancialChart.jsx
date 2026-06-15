import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Loader2, AlertTriangle } from "lucide-react";

function formatCrores(value) {
  if (value === null || value === undefined) return "—";
  return `₹${(value / 1e7).toFixed(0)}Cr`;
}

export default function FinancialChart({ data, loading, error }) {
  if (loading) {
    return (
      <div
        data-tutorial="financial-chart"
        className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center justify-center min-h-[320px]"
      >
        <Loader2 className="animate-spin text-brand-500" size={28} />
      </div>
    );
  }

  if (error || !data || !data.series || data.series.years.length === 0) {
    return (
      <div
        data-tutorial="financial-chart"
        className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 min-h-[320px] flex items-center justify-center text-slate-400 text-sm"
      >
        {error ? (
          <span className="flex items-center gap-2 text-red-500">
            <AlertTriangle size={16} /> Couldn't load chart
          </span>
        ) : (
          "No chart data available"
        )}
      </div>
    );
  }

  const { years, revenue, net_profit, net_margin_pct } = data.series;
  const chartData = years.map((year, i) => ({
    year,
    revenue: revenue[i],
    net_profit: net_profit[i],
    net_margin_pct: net_margin_pct[i],
  }));

  return (
    <div data-tutorial="financial-chart" className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h3 className="text-sm font-semibold text-slate-800 mb-1">
        Revenue, Net Profit &amp; Net Margin Trend
      </h3>
      <p className="text-xs text-slate-400 mb-4">
        Bars show revenue and net profit (left axis, ₹ Crores); line shows net margin % (right
        axis).
      </p>
      <ResponsiveContainer width="100%" height={320}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eef0f4" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis
            yAxisId="left"
            tickFormatter={formatCrores}
            tick={{ fontSize: 11 }}
            width={70}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 11 }}
            width={50}
          />
          <Tooltip
            formatter={(value, name) => {
              if (name === "Net Margin") return [`${value}%`, name];
              return [formatCrores(value), name];
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar yAxisId="left" dataKey="revenue" name="Revenue" fill="#3b6fd6" radius={[4, 4, 0, 0]} />
          <Bar yAxisId="left" dataKey="net_profit" name="Net Profit" fill="#9bbcf2" radius={[4, 4, 0, 0]} />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="net_margin_pct"
            name="Net Margin"
            stroke="#16a34a"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
