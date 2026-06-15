import { useState, useEffect } from "react";
import { api } from "../api/client";
import CompanySelector from "../components/CompanySelector";
import SnapshotCard from "../components/SnapshotCard";
import BriefCard from "../components/BriefCard";

export default function ResearchPage() {
  const [companies, setCompanies] = useState([]);
  const [ticker, setTicker] = useState("");

  // Snapshot state
  const [snapshot, setSnapshot] = useState(null);
  const [snapshotLoading, setSnapshotLoading] = useState(false);
  const [snapshotError, setSnapshotError] = useState(null);
  const [warning, setWarning] = useState(null);
  const [cached, setCached] = useState(false);

  // Brief state
  const [brief, setBrief] = useState(null);
  const [briefLoading, setBriefLoading] = useState(false);
  const [briefError, setBriefError] = useState(null);
  const [briefDataSources, setBriefDataSources] = useState(null);
  const [briefCached, setBriefCached] = useState(false);

  useEffect(() => {
    api
      .getCompanies()
      .then((res) => {
        setCompanies(res.companies);
        if (res.companies.length > 0) {
          setTicker(res.companies[0].ticker);
        }
      })
      .catch((e) => setSnapshotError(e.message));
  }, []);

  useEffect(() => {
    if (!ticker) return;

    // Reset brief state when company changes - briefs are per-company
    setBrief(null);
    setBriefError(null);
    setBriefCached(false);

    setSnapshotLoading(true);
    setSnapshotError(null);
    setWarning(null);
    setCached(false);

    api
      .getSnapshot(ticker)
      .then((res) => {
        setSnapshot(res.snapshot);
        setWarning(res.warning || null);
        setCached(!!res.cached);
      })
      .catch((e) => {
        setSnapshot(null);
        setSnapshotError(e.message);
      })
      .finally(() => setSnapshotLoading(false));
  }, [ticker]);

  const generateBrief = (forceRefresh = false) => {
    setBriefLoading(true);
    setBriefError(null);

    api
      .getBrief(ticker, { forceRefresh })
      .then((res) => {
        setBrief(res.brief);
        setBriefDataSources(res.data_sources);
        setBriefCached(!!res.cached);
      })
      .catch((e) => {
        setBrief(null);
        setBriefError(e.message);
      })
      .finally(() => setBriefLoading(false));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-800 mb-1">Research Brief</h2>
        <p className="text-sm text-slate-500">
          Select an NSE-listed company to view its latest snapshot and generate an AI research
          brief.
        </p>
      </div>

      <CompanySelector companies={companies} value={ticker} onChange={setTicker} />

      <SnapshotCard
        snapshot={snapshot}
        loading={snapshotLoading}
        error={snapshotError}
        warning={warning}
        cached={cached}
      />

      <BriefCard
        brief={brief}
        loading={briefLoading}
        error={briefError}
        dataSources={briefDataSources}
        cached={briefCached}
        onGenerate={() => generateBrief(false)}
        onRefresh={() => generateBrief(true)}
      />
    </div>
  );
}
