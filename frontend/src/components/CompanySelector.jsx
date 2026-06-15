import { useState, useRef, useEffect } from "react";
import { ChevronDown, Search } from "lucide-react";

export default function CompanySelector({ companies, value, onChange }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const selected = companies.find((c) => c.ticker === value);

  const filtered = companies.filter(
    (c) =>
      c.name.toLowerCase().includes(query.toLowerCase()) ||
      c.ticker.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div data-tutorial="company-selector" ref={containerRef} className="relative w-full max-w-sm">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between bg-white border border-slate-300 rounded-lg px-4 py-2.5 text-sm hover:border-brand-400 transition"
      >
        <span className={selected ? "text-slate-800 font-medium" : "text-slate-400"}>
          {selected ? `${selected.name} (${selected.ticker})` : "Select a company..."}
        </span>
        <ChevronDown size={16} className="text-slate-400" />
      </button>

      {open && (
        <div className="absolute z-20 mt-1 w-full bg-white border border-slate-200 rounded-lg shadow-lg overflow-hidden">
          <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-100">
            <Search size={14} className="text-slate-400" />
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search companies..."
              className="w-full text-sm outline-none"
            />
          </div>
          <div className="max-h-64 overflow-y-auto">
            {filtered.length === 0 && (
              <p className="px-4 py-3 text-sm text-slate-400">No companies found</p>
            )}
            {filtered.map((c) => (
              <button
                key={c.ticker}
                onClick={() => {
                  onChange(c.ticker);
                  setOpen(false);
                  setQuery("");
                }}
                className={`w-full text-left px-4 py-2 text-sm hover:bg-brand-50 transition ${
                  c.ticker === value ? "bg-brand-50 text-brand-700 font-medium" : "text-slate-700"
                }`}
              >
                {c.name} <span className="text-slate-400">({c.ticker})</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
