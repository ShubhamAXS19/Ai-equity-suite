import { useState } from "react";
import { Plus, X, Loader2 } from "lucide-react";

export default function WatchlistManager({ companies, watchlist, onAdd, onRemove, loading }) {
  const [adding, setAdding] = useState(false);
  const [selected, setSelected] = useState("");

  const watchlistTickers = new Set(watchlist.map((w) => w.ticker));
  const availableCompanies = companies.filter((c) => !watchlistTickers.has(c.ticker));

  const handleAdd = () => {
    if (!selected) return;
    onAdd(selected);
    setSelected("");
    setAdding(false);
  };

  return (
    <div data-tutorial="watchlist-manager" className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-slate-800">Watchlist</h3>
        {!adding && availableCompanies.length > 0 && (
          <button
            onClick={() => setAdding(true)}
            className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
          >
            <Plus size={14} /> Add company
          </button>
        )}
      </div>

      {adding && (
        <div className="flex gap-2 mb-3">
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            className="flex-1 border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">Select a company...</option>
            {availableCompanies.map((c) => (
              <option key={c.ticker} value={c.ticker}>
                {c.name} ({c.ticker})
              </option>
            ))}
          </select>
          <button
            onClick={handleAdd}
            disabled={!selected}
            className="px-3 py-1.5 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50"
          >
            Add
          </button>
          <button
            onClick={() => {
              setAdding(false);
              setSelected("");
            }}
            className="px-3 py-1.5 text-sm border border-slate-200 rounded-lg hover:bg-slate-50"
          >
            Cancel
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-6">
          <Loader2 className="animate-spin text-brand-500" size={20} />
        </div>
      ) : watchlist.length === 0 ? (
        <p className="text-sm text-slate-400 py-2">
          Your watchlist is empty. Add a company to start monitoring news.
        </p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {watchlist.map((w) => (
            <span
              key={w.ticker}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 text-sm text-slate-700"
            >
              {w.name}
              <button
                onClick={() => onRemove(w.ticker)}
                className="text-slate-400 hover:text-red-500"
                title="Remove from watchlist"
              >
                <X size={13} />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
