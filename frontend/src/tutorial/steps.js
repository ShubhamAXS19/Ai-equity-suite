/**
 * Tutorial steps shown on first visit (or when replayed from Settings).
 *
 * Steps are grouped by route so each tab can have its own focused tour.
 * `shellSteps` cover the app-wide elements (title, nav, settings) and are
 * shown once, then each route's specific steps are appended depending on
 * which page the user is currently on.
 *
 * Phase 1 adds the Research Brief generation steps. Steps for the
 * Financial Analyzer and News Monitor tabs will be appended in later
 * phases via `routeSteps`.
 */

export const shellSteps = [
  {
    target: "[data-tutorial='app-title']",
    title: "Welcome to the AI Equity Research Suite",
    body:
      "This is a portfolio project that brings together three tools analysts use every day: " +
      "research briefs, financial statement analysis, and news monitoring — all powered by AI. " +
      "This quick tour will show you around.",
    placement: "bottom",
  },
  {
    target: "[data-tutorial='nav-research']",
    title: "Research Brief",
    body:
      "Pick any NSE-listed company to see a live snapshot (price, P/E, P/B, revenue growth) and " +
      "generate a one-page AI research brief covering business overview, financials, recent " +
      "developments, and key risks.",
    placement: "bottom",
  },
  {
    target: "[data-tutorial='nav-analyzer']",
    title: "Financial Analyzer",
    body:
      "Dive into multi-year financial ratios (margins, ROE, debt-to-equity, and more) with " +
      "charts and AI-generated commentary on trends and anomalies. Coming in Phase 2.",
    placement: "bottom",
  },
  {
    target: "[data-tutorial='nav-news']",
    title: "News Monitor",
    body:
      "Track news for a watchlist of companies, with AI summaries and materiality tags " +
      "(High/Medium/Low). Coming in Phase 3.",
    placement: "bottom",
  },
  {
    target: "[data-tutorial='settings-button']",
    title: "Bring Your Own API Keys",
    body:
      "Claude (Anthropic) writes the AI commentary, and InsightSentry provides market data. " +
      "If you have your own keys, add them here for the best accuracy. If not, the app " +
      "automatically falls back to Groq's free Llama model for AI and Yahoo Finance (yfinance) " +
      "for market data — results may be slightly less accurate or timely, but everything still " +
      "works out of the box.",
    placement: "left",
  },
];

/**
 * Route-specific steps, appended after `shellSteps` when the user is on
 * that route. Keyed by the React Router path.
 */
export const routeSteps = {
  "/": [
    {
      target: "[data-tutorial='company-selector']",
      title: "Choose a Company",
      body:
        "Search or select from 15 large-cap NSE companies. The snapshot and brief below update " +
        "for whichever company you pick.",
      placement: "bottom",
    },
    {
      target: "[data-tutorial='snapshot-card']",
      title: "Snapshot Card",
      body:
        "Key stats at a glance: current price, market cap, valuation ratios, 52-week range, and " +
        "the latest revenue/profit with year-over-year growth. A small badge shows which data " +
        "source (InsightSentry or yfinance) produced these numbers.",
      placement: "top",
    },
    {
      target: "[data-tutorial='brief-card']",
      title: "Generate an AI Research Brief",
      body:
        "Click 'Generate Brief' to have Claude (or Groq, if no key is set) write a one-page " +
        "brief — business overview, financial interpretation, recent developments, and key " +
        "risks — using the snapshot data shown above. Briefs are cached per day, so repeat " +
        "demos won't re-call the API.",
      placement: "top",
    },
  ],
  "/analyzer": [
    {
      target: "[data-tutorial='company-selector']",
      title: "Choose a Company",
      body:
        "Select a company to load up to 4 years of its income statement and balance sheet data, " +
        "computed into key financial ratios.",
      placement: "bottom",
    },
    {
      target: "[data-tutorial='ratio-table']",
      title: "Computed Financial Ratios",
      body:
        "These ratios — margins, current ratio, debt-to-equity, ROE, and interest coverage — " +
        "are computed directly from the raw financial statements using pandas. This is the " +
        "'Computed Financial Data' section: no AI involved here, just math.",
      placement: "top",
    },
    {
      target: "[data-tutorial='financial-chart']",
      title: "Visualize the Trend",
      body:
        "Revenue and net profit are shown as bars (left axis), with net margin plotted as a " +
        "line (right axis) so you can quickly spot whether profitability is keeping pace with " +
        "revenue growth.",
      placement: "top",
    },
    {
      target: "[data-tutorial='commentary-card']",
      title: "AI Commentary",
      body:
        "Click 'Generate Commentary' to have Claude (or Groq) review the ratio table and write " +
        "a plain-English summary of notable trends and anomalies — for example, margin " +
        "compression despite revenue growth, or rising debt. This section is clearly separated " +
        "from the computed data above so it's always obvious what's calculated vs. AI-written.",
      placement: "top",
    },
  ],
  "/news": [
    {
      target: "[data-tutorial='watchlist-manager']",
      title: "Your Watchlist",
      body:
        "Five companies are tracked by default. Add or remove companies from the 15 NSE " +
        "large-caps to customize which news gets monitored.",
      placement: "bottom",
    },
    {
      target: "[data-tutorial='fetch-news-section']",
      title: "Fetch Raw News",
      body:
        "Click 'Fetch News' to pull the latest articles from Moneycontrol, Economic Times " +
        "Markets, and LiveMint Markets, filtered to mentions of your watchlist companies. " +
        "This is the raw, unprocessed feed — no AI involved yet.",
      placement: "top",
    },
    {
      target: "[data-tutorial='digest-generate-section']",
      title: "Generate the AI Digest",
      body:
        "Click 'Generate Digest' to have Claude (or Groq) summarize each new article and tag " +
        "it with a materiality level (High/Medium/Low) and category (Earnings, M&A, " +
        "Regulatory, etc.). Already-processed articles are skipped, so this is safe to click " +
        "repeatedly.",
      placement: "top",
    },
    {
      target: "[data-tutorial='digest-filters']",
      title: "Filter the Digest",
      body:
        "Filter by company, materiality, or category, and use the date picker to view past " +
        "digests — each day's results are saved as a snapshot.",
      placement: "bottom",
    },
    {
      target: "[data-tutorial='digest-view']",
      title: "The Digest",
      body:
        "Articles are sorted by materiality (High first) then date, each with a color-coded " +
        "badge, category tag, and AI summary. A daily scheduler also runs this pipeline " +
        "automatically in the background.",
      placement: "top",
    },
  ],
};

/**
 * Builds the full step list for the tutorial overlay based on the current
 * route. Always starts with shellSteps, then appends that route's steps
 * (if any).
 */
export function getTutorialSteps(pathname) {
  const extra = routeSteps[pathname] || [];
  return [...shellSteps, ...extra];
}
