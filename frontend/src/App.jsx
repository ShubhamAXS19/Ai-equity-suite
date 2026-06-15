import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { SettingsProvider, useSettings } from "./context/SettingsContext";
import Layout from "./components/Layout";
import SettingsPanel from "./components/SettingsPanel";
import TutorialOverlay from "./components/TutorialOverlay";
import { getTutorialSteps } from "./tutorial/steps";
import ResearchPage from "./pages/ResearchPage";
import AnalyzerPage from "./pages/AnalyzerPage";
import NewsPage from "./pages/NewsPage";

function AppShell() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [tutorialActive, setTutorialActive] = useState(false);
  const [helpPulseKey, setHelpPulseKey] = useState(0);
  const { tutorialSeen, markTutorialSeen } = useSettings();
  const location = useLocation();

  useEffect(() => {
    if (!tutorialSeen) {
      // Small delay so the initial layout has rendered and target elements exist
      const t = setTimeout(() => setTutorialActive(true), 600);
      return () => clearTimeout(t);
    }
  }, [tutorialSeen]);

  // Pulse the Help button a few times whenever the user switches tabs, as a
  // gentle nudge that a tour is available for that section.
  useEffect(() => {
    setHelpPulseKey((k) => k + 1);
  }, [location.pathname]);

  const closeTutorial = () => {
    setTutorialActive(false);
    markTutorialSeen();
  };

  return (
    <>
      <Layout
        onOpenSettings={() => setSettingsOpen(true)}
        onOpenTutorial={() => setTutorialActive(true)}
        helpPulseKey={helpPulseKey}
      >
        <Routes>
          <Route path="/" element={<ResearchPage />} />
          <Route path="/analyzer" element={<AnalyzerPage />} />
          <Route path="/news" element={<NewsPage />} />
        </Routes>
      </Layout>

      <SettingsPanel
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onOpenTutorial={() => {
          setSettingsOpen(false);
          setTutorialActive(true);
        }}
      />

      {tutorialActive && (
        <TutorialOverlay
          steps={getTutorialSteps(location.pathname)}
          onComplete={closeTutorial}
          onSkip={closeTutorial}
        />
      )}
    </>
  );
}

export default function App() {
  return (
    <SettingsProvider>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </SettingsProvider>
  );
}
