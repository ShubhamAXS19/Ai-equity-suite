import { useState, useEffect } from "react";
import { api } from "../api/client";
import CompanySelector from "../components/CompanySelector";
import RatioTable from "../components/RatioTable";
import FinancialChart from "../components/FinancialChart";
import CommentaryCard from "../components/CommentaryCard";

export default function AnalyzerPage() {
  const [companies, setCompanies] = useState([]);
  const [ticker, setTicker] = useState("");

  // Ratio data state
  const [ratioData, setRatioData] = useState(null);
  const [ratioLoading, setRatioLoading] = useState(false);
  const [ratioError, setRatioError] = useState(null);
  const [warning, setWarning] = useState(null);
  const [cached, setCached] = useState(false);

  // Commentary state
  const [commentary, setCommentary] = useState(null);
  const [commentaryLoading, setCommentaryLoading] = useState(false);
  const [commentaryError, setCommentaryError] = useState(null);
  const [commentaryCached, setCommentaryCached] = useState(false);

  useEffect(() => {
    api
      .getCompanies()
      .then((res) => {
        setCompanies(res.companies);
        if (res.companies.length > 0) {
          // Default to RELIANCE.NS if present (it has full seed data),
          // otherwise the first company.
          const reliance = res.companies.find((c) => c.ticker === "RELIANCE.NS");
          setTicker(reliance ? reliance.ticker : res.companies[0].ticker);
        }
      })
      .catch((e) => setRatioError(e.message));
  }, []);

  useEffect(() => {
    if (!ticker) return;

    setCommentary(null);
    setCommentaryError(null);
    setCommentaryCached(false);

    setRatioLoading(true);
    setRatioError(null);
    setWarning(null);
    setCached(false);

    api
      .getRatios(ticker)
      .then((res) => {
        setRatioData(res);
        setWarning(res.warning || null);
        setCached(!!res.cached);
      })
      .catch((e) => {
        setRatioData(null);
        setRatioError(e.message);
      })
      .finally(() => setRatioLoading(false));
  }, [ticker]);

  const generateCommentary = (forceRefresh = false) => {
    setCommentaryLoading(true);
    setCommentaryError(null);

    api
      .getCommentary(ticker, { forceRefresh })
      .then((res) => {
        setCommentary(res.commentary);
        setCommentaryCached(!!res.cached);
      })
      .catch((e) => {
        setCommentary(null);
        setCommentaryError(e.message);
      })
      .finally(() => setCommentaryLoading(false));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-800 mb-1">Financial Analyzer</h2>
        <p className="text-sm text-slate-500">
          Multi-year financial ratios computed from income statement, balance sheet, and cash
          flow data, with AI commentary on trends and anomalies.
        </p>
      </div>

      <CompanySelector companies={companies} value={ticker} onChange={setTicker} />

      <RatioTable data={ratioData} loading={ratioLoading} error={ratioError} warning={warning} cached={cached} />

      <FinancialChart data={ratioData} loading={ratioLoading} error={ratioError} />

      <CommentaryCard
        commentary={commentary}
        loading={commentaryLoading}
        error={commentaryError}
        cached={commentaryCached}
        onGenerate={() => generateCommentary(false)}
        onRefresh={() => generateCommentary(true)}
      />
    </div>
  );
}
