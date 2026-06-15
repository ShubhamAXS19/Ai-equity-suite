import { NavLink } from "react-router-dom";
import { Settings as SettingsIcon, LineChart, FileBarChart, Newspaper, HelpCircle } from "lucide-react";

const navItems = [
  { to: "/", label: "Research Brief", icon: LineChart, tutorial: "nav-research" },
  { to: "/analyzer", label: "Financial Analyzer", icon: FileBarChart, tutorial: "nav-analyzer" },
  { to: "/news", label: "News Monitor", icon: Newspaper, tutorial: "nav-news" },
];

export default function Layout({ children, onOpenSettings, onOpenTutorial, helpPulseKey }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-4 flex-wrap">
          <h1 data-tutorial="app-title" className="text-lg font-bold text-slate-800">
            AI Equity Research Suite
          </h1>

          <nav className="flex items-center gap-1">
            {navItems.map(({ to, label, icon: Icon, tutorial }) => (
              <NavLink
                key={to}
                to={to}
                data-tutorial={tutorial}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-slate-500 hover:bg-slate-100 hover:text-slate-700"
                  }`
                }
              >
                <Icon size={15} />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-1">
            <button
              key={helpPulseKey}
              onClick={onOpenTutorial}
              title="Show tutorial / tour"
              className="help-pulse flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition"
            >
              <HelpCircle size={15} />
              Help
            </button>
            <button
              data-tutorial="settings-button"
              onClick={onOpenSettings}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition"
            >
              <SettingsIcon size={15} />
              Settings
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">{children}</main>

      <footer className="text-center text-xs text-slate-400 py-4">
        AI Equity Research Suite — Portfolio project. AI-generated content should be reviewed by a
        qualified analyst before use.
      </footer>
    </div>
  );
}
