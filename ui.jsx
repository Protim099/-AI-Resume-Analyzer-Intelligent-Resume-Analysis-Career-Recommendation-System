import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import { Doughnut } from "react-chartjs-2";
import { ArcElement, BarElement, CategoryScale, Chart as ChartJS, Filler, Legend, LinearScale, LineElement, PointElement, Tooltip } from "chart.js";
import { scoreColor, scoreLabel } from "../api";

ChartJS.register(ArcElement, BarElement, CategoryScale, Filler, Legend, LinearScale, LineElement, PointElement, Tooltip);
ChartJS.defaults.font.family = '"Plus Jakarta Sans", system-ui, sans-serif';

export const Spinner = ({ label = "Loading..." }) => (
  <div className="flex items-center justify-center gap-2 py-16 text-slate-500" role="status">
    <Loader2 className="h-5 w-5 animate-spin" /> <span className="text-sm">{label}</span>
  </div>
);

export const Alert = ({ type = "error", children }) =>
  children ? (
    <div role="alert" className={`flex items-start gap-2 rounded-lg border px-3.5 py-3 text-sm ${
      type === "error" ? "border-red-200 bg-red-50 text-red-700" : "border-emerald-200 bg-emerald-50 text-emerald-700"}`}>
      {type === "error" ? <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" /> : <CheckCircle2 className="h-4 w-4 mt-0.5 shrink-0" />}
      <span>{children}</span>
    </div>
  ) : null;

export const PageHeader = ({ title, subtitle, children }) => (
  <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
    <div>
      <h1 className="text-2xl font-extrabold">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
    </div>
    <div className="flex flex-wrap gap-2">{children}</div>
  </div>
);

export const StatCard = ({ icon: Icon, label, value, hint }) => (
  <div className="card p-5">
    <div className="flex items-center gap-3">
      <div className="rounded-lg bg-brand-50 p-2.5 text-brand-700"><Icon className="h-5 w-5" /></div>
      <div className="text-sm font-medium text-slate-500">{label}</div>
    </div>
    <div className="mt-3 text-3xl font-extrabold text-ink">{value}</div>
    {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
  </div>
);

export const ProgressBar = ({ value, max = 100, color, label, right }) => {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div>
      {(label || right) && (
        <div className="mb-1 flex justify-between text-xs font-medium text-slate-600"><span>{label}</span><span>{right ?? `${Math.round(pct)}%`}</span></div>
      )}
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100" role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100}>
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: color || scoreColor(pct) }} />
      </div>
    </div>
  );
};

export function ScoreRing({ score, size = 180, caption }) {
  const color = scoreColor(score);
  const data = { datasets: [{ data: [score, 100 - score], backgroundColor: [color, "#e2e8f0"], borderWidth: 0, cutout: "78%" }] };
  return (
    <div className="relative mx-auto" style={{ width: size, height: size }}>
      <Doughnut data={data} options={{ plugins: { tooltip: { enabled: false }, legend: { display: false } }, animation: { duration: 600 } }} />
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-4xl font-extrabold text-ink">{Math.round(score)}</div>
        <div className="text-xs font-semibold" style={{ color }}>{caption || scoreLabel(score)}</div>
      </div>
    </div>
  );
}

export const Chips = ({ items, tone = "slate", empty = "None" }) => {
  const tones = { slate: "bg-slate-100 text-slate-700", green: "bg-emerald-50 text-emerald-700", red: "bg-red-50 text-red-700", teal: "bg-brand-50 text-brand-800" };
  if (!items?.length) return <span className="text-sm text-slate-400">{empty}</span>;
  return <div className="flex flex-wrap gap-1.5">{items.map((t) => <span key={t} className={`chip ${tones[tone]}`}>{t}</span>)}</div>;
};

export const PriorityBadge = ({ p }) => {
  const t = { high: "bg-red-50 text-red-700", medium: "bg-amber-50 text-amber-700", low: "bg-slate-100 text-slate-600" }[p] || "bg-slate-100 text-slate-600";
  return <span className={`chip ${t} capitalize`}>{p}</span>;
};

export const Empty = ({ icon: Icon, title, text, action }) => (
  <div className="card flex flex-col items-center px-6 py-14 text-center">
    <div className="rounded-full bg-slate-100 p-3 text-slate-400"><Icon className="h-6 w-6" /></div>
    <h3 className="mt-4 text-base font-bold">{title}</h3>
    <p className="mt-1 max-w-sm text-sm text-slate-500">{text}</p>
    {action && <div className="mt-5">{action}</div>}
  </div>
);
