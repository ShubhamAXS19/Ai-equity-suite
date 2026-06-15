import { useState, useEffect, useRef } from "react";
import { X, ArrowRight, ArrowLeft } from "lucide-react";

/**
 * Interactive spotlight tutorial.
 *
 * `steps` is an array of:
 *   {
 *     target: "[data-tutorial='nav-research']",  // CSS selector for the element to highlight
 *     title: "Research Brief",
 *     body: "Generate AI research briefs ...",
 *     placement: "bottom" | "top" | "left" | "right" (optional, default "bottom")
 *   }
 *
 * The overlay darkens the screen, cuts a highlight "hole" around the target
 * element, and shows a tooltip with Next/Back/Skip controls.
 */
export default function TutorialOverlay({ steps, onComplete, onSkip }) {
  const [stepIndex, setStepIndex] = useState(0);
  const [rect, setRect] = useState(null);
  const tooltipRef = useRef(null);

  const step = steps[stepIndex];

  useEffect(() => {
    if (!step) return;

    const updateRect = () => {
      const el = document.querySelector(step.target);
      if (el) {
        const r = el.getBoundingClientRect();
        setRect(r);
        el.scrollIntoView({ behavior: "smooth", block: "center" });
      } else {
        setRect(null);
      }
    };

    updateRect();
    window.addEventListener("resize", updateRect);
    // re-check briefly after scroll/render settles
    const t = setTimeout(updateRect, 300);

    return () => {
      window.removeEventListener("resize", updateRect);
      clearTimeout(t);
    };
  }, [stepIndex, step]);

  if (!step) return null;

  const isLast = stepIndex === steps.length - 1;

  const goNext = () => {
    if (isLast) {
      onComplete();
    } else {
      setStepIndex((i) => i + 1);
    }
  };

  const goBack = () => setStepIndex((i) => Math.max(0, i - 1));

  const padding = 8;
  const highlightStyle = rect
    ? {
        top: rect.top - padding,
        left: rect.left - padding,
        width: rect.width + padding * 2,
        height: rect.height + padding * 2,
      }
    : null;

  // Tooltip position relative to highlighted element
  const placement = step.placement || "bottom";
  let tooltipStyle = { top: "50%", left: "50%", transform: "translate(-50%, -50%)" };
  if (rect) {
    const gap = 16;
    if (placement === "bottom") {
      tooltipStyle = {
        top: rect.bottom + gap,
        left: Math.max(16, Math.min(rect.left, window.innerWidth - 340)),
      };
    } else if (placement === "top") {
      tooltipStyle = {
        top: Math.max(16, rect.top - gap - 160),
        left: Math.max(16, Math.min(rect.left, window.innerWidth - 340)),
      };
    } else if (placement === "right") {
      tooltipStyle = { top: rect.top, left: Math.min(rect.right + gap, window.innerWidth - 340) };
    } else if (placement === "left") {
      tooltipStyle = { top: rect.top, left: Math.max(16, rect.left - gap - 320) };
    }
  }

  return (
    <div className="fixed inset-0 z-[100]">
      {/* Dim background */}
      <div className="absolute inset-0 bg-black/50 transition-opacity" />

      {/* Highlight cutout */}
      {highlightStyle && (
        <div
          className="absolute rounded-lg ring-4 ring-brand-400 ring-offset-2 ring-offset-transparent transition-all duration-300 pointer-events-none"
          style={{
            ...highlightStyle,
            boxShadow: "0 0 0 9999px rgba(0,0,0,0.5)",
            background: "transparent",
          }}
        />
      )}

      {/* Tooltip */}
      <div
        ref={tooltipRef}
        className="absolute w-80 bg-white rounded-xl shadow-2xl p-4 transition-all duration-300"
        style={tooltipStyle}
      >
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-slate-800">{step.title}</h3>
          <button onClick={onSkip} className="text-slate-400 hover:text-slate-600">
            <X size={16} />
          </button>
        </div>
        <p className="text-sm text-slate-600 mb-4 leading-relaxed">{step.body}</p>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">
            Step {stepIndex + 1} of {steps.length}
          </span>
          <div className="flex gap-2">
            {stepIndex > 0 && (
              <button
                onClick={goBack}
                className="flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50"
              >
                <ArrowLeft size={14} /> Back
              </button>
            )}
            <button
              onClick={goNext}
              className="flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg bg-brand-600 text-white hover:bg-brand-700"
            >
              {isLast ? "Done" : "Next"} <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
