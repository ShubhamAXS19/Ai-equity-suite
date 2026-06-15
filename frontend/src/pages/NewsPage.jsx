import { useState, useEffect } from "react";
import { api } from "../api/client";
import { Loader2, RefreshCw, Sparkles, AlertTriangle, ExternalLink } from "lucide-react";
import WatchlistManager from "../components/WatchlistManager";
import NewsArticleCard from "../components/NewsArticleCard";
import DigestFilters from "../components/DigestFilters";
import DataSourceBadge from "../components/DataSourceBadge";

export default function NewsPage() {
  const [companies, setCompanies] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [watchlistLoading, setWatchlistLoading] = useState(true);

  // Raw fetch state (Phase 3.1)
  const [rawArticles, setRawArticles] = useState(null);
  const [rawLoading, setRawLoading] = useState(false);
  const [rawError, setRawError] = useState(null);
  const [rawWarning, setRawWarning] = useState(null);
  const [rawCached, setRawCached] = useState(false);

  // Summarization state (Phase 3.2)
  const [summarizing, setSummarizing] = useState(false);
  const [summarizeError, setSummarizeError] = useState(null);
  const [summarizeResult, setSummarizeResult] = useState(null);

  // Digest state
  const [digestArticles, setDigestArticles] = useState([]);
  const [digestLoading, setDigestLoading] = useState(true);
  const [digestError, setDigestError] = useState(null);
  const [digestDates, setDigestDates] = useState([]);
  const [filters, setFilters] = useState({});

  useEffect(() => {
    api.getCompanies().then((res) => setCompanies(res.companies)).catch(() => {});
    loadWatchlist();
    loadDigestDates();
  }, []);

  useEffect(() => {
    loadDigest();
  }, [filters]);

  const loadWatchlist = () => {
    setWatchlistLoading(true);
    api
      .getWatchlist()
      .then((res) => setWatchlist(res.watchlist))
      .catch(() => {})
      .finally(() => setWatchlistLoading(false));
  };

  const loadDigestDates = () => {
    api
      .getDigestDates()
      .then((res) => setDigestDates(res.dates))
      .catch(() => {});
  };

  const loadDigest = () => {
    setDigestLoading(true);
    setDigestError(null);
    api
      .getDigest(filters)
      .then((res) => setDigestArticles(res.articles))
      .catch((e) => setDigestError(e.message))
      .finally(() => setDigestLoading(false));
  };

  const handleAddToWatchlist = (ticker) => {
    api
      .addToWatchlist(ticker)
      .then(() => loadWatchlist())
      .catch((e) => alert(e.message));
  };

  const handleRemoveFromWatchlist = (ticker) => {
    api
      .removeFromWatchlist(ticker)
      .then(() => loadWatchlist())
      .catch((e) => alert(e.message));
  };

  const handleFetchNews = () => {
    setRawLoading(true);
    setRawError(null);
    setRawWarning(null);
    setRawCached(false);

    api
      .fetchNews()
      .then((res) => {
        setRawArticles(res.articles);
        setRawWarning(res.warning || null);
        setRawCached(!!res.cached);
      })
      .catch((e) => {
        setRawArticles(null);
        setRawError(e.message);
      })
      .finally(() => setRawLoading(false));
  };

  const handleGenerateDigest = () => {
    setSummarizing(true);
    setSummarizeError(null);
    setSummarizeResult(null);

    api
      .summarizeNews()
      .then((res) => {
        setSummarizeResult(res);
        loadDigestDates();
        // Refresh digest to show today's date by default
        setFilters((f) => ({ ...f, digestDate: res.digest_date }));
      })
      .catch((e) => setSummarizeError(e.message))
      .finally(() => setSummarizing(false));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-800 mb-1">News Monitor</h2>
        <p className="text-sm text-slate-500">
          Track news for your watchlist, with AI-generated summaries and materiality tagging.
        </p>
      </div>

      <WatchlistManager
        companies={companies}
        watchlist={watchlist}
        onAdd={handleAddToWatchlist}
        onRemove={handleRemoveFromWatchlist}
        loading={watchlistLoading}
      />

      {/* Phase 3.1: manual raw fetch */}
      <div data-tutorial="fetch-news-section" className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
          <h3 className="text-sm font-semibold text-slate-800">Raw News Feed</h3>
          <button
            onClick={handleFetchNews}
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-700 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition"
          >
            <RefreshCw size={14} className={rawLoading ? "animate-spin" : ""} /> Fetch News
          </button>
        </div>

        {rawWarning && (
          <div className="mb-3 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-700 flex items-center gap-2">
            <AlertTriangle size={14} /> {rawWarning}
          </div>
        )}

        {rawError && (
          <div className="mb-3 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-xs text-red-600 flex items-center gap-2">
            <AlertTriangle size={14} /> {rawError}
          </div>
        )}

        {rawArticles === null ? (
          <p className="text-sm text-slate-400 py-2">
            Click "Fetch News" to pull the latest matched articles for your watchlist from
            Moneycontrol, Economic Times Markets, and LiveMint Markets.
          </p>
        ) : rawArticles.length === 0 ? (
          <p className="text-sm text-slate-400 py-2">
            No matching articles found for your watchlist right now.
          </p>
        ) : (
          <ul className="space-y-1.5 max-h-64 overflow-y-auto">
            {rawArticles.map((a) => (
              <li key={a.id} className="text-sm flex items-start gap-2">
                <span className="text-xs text-slate-400 mt-0.5 flex-shrink-0">{a.ticker}</span>
                <a
                  href={a.link}
                  target="_blank"
                  rel="noreferrer"
                  className="text-slate-700 hover:text-brand-600 flex items-center gap-1"
                >
                  {a.title} <ExternalLink size={11} className="flex-shrink-0" />
                </a>
                <span className="text-xs text-slate-400 ml-auto flex-shrink-0">{a.source}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Phase 3.2: AI summarization */}
      <div data-tutorial="digest-generate-section" className="bg-violet-50 rounded-xl border border-violet-200 p-6">
        <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Sparkles className="text-violet-500" size={18} />
            <h3 className="text-sm font-semibold text-violet-800 uppercase tracking-wide">
              AI Digest Generation
            </h3>
          </div>
          <div className="flex items-center gap-2">
            <DataSourceBadge showMarketData={false} />
            <button
              onClick={handleGenerateDigest}
              disabled={summarizing}
              className="flex items-center gap-2 px-3 py-1.5 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition disabled:opacity-60"
            >
              {summarizing ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
              {summarizing ? "Summarizing..." : "Generate Digest"}
            </button>
          </div>
        </div>

        <p className="text-sm text-slate-600 mb-2">
          Summarizes new matched articles with AI, tagging each with a materiality level
          (High/Medium/Low) and category. Already-processed articles are skipped.
        </p>

        {summarizeError && (
          <div className="px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-xs text-red-600 flex items-center gap-2">
            <AlertTriangle size={14} /> {summarizeError}
          </div>
        )}

        {summarizeResult && (
          <div className="px-3 py-2 rounded-lg bg-white/70 border border-violet-100 text-xs text-violet-700">
            Processed {summarizeResult.processed} new article
            {summarizeResult.processed === 1 ? "" : "s"}
            {summarizeResult.skipped > 0 && ` (${summarizeResult.skipped} already processed)`} for{" "}
            {summarizeResult.digest_date}.
          </div>
        )}
      </div>

      {/* Digest view */}
      <div data-tutorial="digest-view" className="space-y-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h3 className="text-sm font-semibold text-slate-800">Digest</h3>
          <DigestFilters
            companies={companies}
            watchlist={watchlist}
            filters={filters}
            onChange={setFilters}
            digestDates={digestDates}
          />
        </div>

        {digestLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="animate-spin text-brand-500" size={24} />
          </div>
        ) : digestError ? (
          <div className="bg-white rounded-xl border border-red-200 p-6 text-center text-sm text-red-600">
            {digestError}
          </div>
        ) : digestArticles.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-6 text-center text-sm text-slate-400">
            No articles match the current filters.
          </div>
        ) : (
          <div className="space-y-3">
            {digestArticles.map((a) => (
              <NewsArticleCard key={a.id} article={a} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
