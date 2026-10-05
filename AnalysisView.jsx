import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Bar } from "react-chartjs-2";
import { AlertTriangle, CheckCircle2, Download, FileSearch, Lightbulb } from "lucide-react";
import api, { errMsg, fmtDate, scoreColor } from "../api";
import { Alert, Chips, Empty, PageHeader, PriorityBadge, ProgressBar, ScoreRing, Spinner } from "../components/ui";
import { downloadReport } from "../components/download";

export default function AnalysisView() {
  const { id } = useParams();
  const nav = useNavigate();
  const [list, setList] = useState(null);
  const [a, setA] = useState(null);
  const [error, setError] = useState("");
  const [dl, setDl] = useState(false);

  useEffect(() => { api.get("/analysis").then((r) => setList(r.data)).catch((e) => setError(errMsg(e))); }, []);
  useEffect(() => {
    if (!list) return;
    const target = id || list[0]?.id;
    if (!target) return;
    setA(null);
    api.get(`/analysis/${target}`).then((r) => setA(r.data)).catch((e) => setError(errMsg(e)));
  }, [id, list]);

  if (error) return <Alert>{error}</Alert>;
  if (!list) return <Spinner />;
  if (list.length === 0) return <Empty icon={FileSearch} title="No analyses yet" text="Upload a resume and we will analyze it automatically." action={<Link to="/upload" className="btn-primary">Upload resume</Link>} />;
  if (!a) return <Spinner label="Loading analysis..." />;

  const r = a.resume, c = r.contact;
  const bd = Object.entries(a.ats_breakdown);
  const download = async () => { setDl(true); const m = await downloadReport(a.id); if (m) setError(m); setDl(false); };
  const byCat = r.skills.reduce((acc, s) => ((acc[s.category] = [...(acc[s.category] || []), s.name]), acc), {});

  return (
    <>
      <PageHeader title="Resume analysis" subtitle={`${a.resume_filename} - analyzed ${fmtDate(a.created_at)}${a.job_title ? ` for "${a.job_title}"` : ""}`}>
        <select className="input !w-auto" value={a.id} onChange={(e) => nav(`/analysis/${e.target.value}`)} aria-label="Choose analysis">
          {list.map((x) => <option key={x.id} value={x.id}>#{x.id} - {x.resume_filename} - {x.job_title || "ATS"} ({fmtDate(x.created_at)})</option>)}
        </select>
        <button className="btn-primary" onClick={download} disabled={dl}><Download className="h-4 w-4" />{dl ? "Preparing..." : "Download report"}</button>
      </PageHeader>

      <div className="space-y-6">
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="card p-6 text-center">
            <h2 className="mb-4 font-bold">ATS score</h2>
            <ScoreRing score={a.ats_score} />
            <p className="mt-4 text-xs text-slate-500">{a.metrics.word_count} words - {a.metrics.pages} page(s) - {a.metrics.technical_skills} technical skills</p>
          </div>
          <div className="card p-6 lg:col-span-2">
            <h2 className="mb-4 font-bold">Score breakdown</h2>
            <div className="h-56">
              <Bar data={{ labels: bd.map(([k]) => k), datasets: [{ label: "Score", data: bd.map(([, v]) => Math.round((v.score / v.max) * 100)), backgroundColor: bd.map(([, v]) => scoreColor((v.score / v.max) * 100)), borderRadius: 4 }] }}
                options={{ maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => { const v = bd[ctx.dataIndex][1]; return `${v.score} / ${v.max} points`; } } } }, scales: { y: { min: 0, max: 100, ticks: { callback: (v) => `${v}%` } } } }} />
            </div>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="card p-6"><h2 className="mb-3 flex items-center gap-2 font-bold"><CheckCircle2 className="h-5 w-5 text-emerald-600" />Strengths</h2>
            {a.strengths.length ? <ul className="space-y-2 text-sm">{a.strengths.map((s) => <li key={s} className="flex gap-2"><span className="text-emerald-600">+</span>{s}</li>)}</ul> : <p className="text-sm text-slate-500">No standout strengths detected yet.</p>}</div>
          <div className="card p-6"><h2 className="mb-3 flex items-center gap-2 font-bold"><AlertTriangle className="h-5 w-5 text-amber-600" />Issues to fix</h2>
            {a.issues.length ? <ul className="space-y-2 text-sm">{a.issues.map((s) => <li key={s} className="flex gap-2"><span className="text-amber-600">!</span>{s}</li>)}</ul> : <p className="text-sm text-slate-500">No issues found.</p>}</div>
        </div>

        <div className="card p-6">
          <h2 className="mb-4 flex items-center gap-2 font-bold"><Lightbulb className="h-5 w-5 text-brand-700" />Recommendations</h2>
          <ul className="divide-y divide-slate-100">{a.recommendations.map((x, i) => (
            <li key={i} className="flex items-start gap-3 py-3 text-sm"><PriorityBadge p={x.priority} /><div><div className="text-xs font-semibold text-slate-500">{x.category}</div>{x.text}</div></li>))}</ul>
        </div>

        <div className="card p-6">
          <h2 className="mb-4 font-bold">Information extracted from your resume</h2>
          <div className="grid gap-x-8 gap-y-4 text-sm sm:grid-cols-2">
            {[["Name", c.name], ["Email", c.email], ["Phone", c.phone], ["LinkedIn", c.linkedin], ["GitHub", c.github], ["Experience", `${r.experience_years} years`]].map(([k, v]) => (
              <div key={k}><div className="text-xs font-semibold text-slate-500">{k}</div><div className="break-all">{v || <span className="text-slate-400">Not found</span>}</div></div>))}
          </div>
          <h3 className="mb-2 mt-6 text-sm font-bold">Skills ({r.skills.length})</h3>
          <div className="space-y-3">{Object.entries(byCat).map(([cat, names]) => <div key={cat}><div className="mb-1 text-xs font-semibold text-slate-500">{cat}</div><Chips items={names} tone={cat === "Soft Skills" ? "slate" : "teal"} /></div>)}</div>
          <Section title="Education" empty={!r.education.length}>{r.education.map((e, i) => <Row key={i} main={e.degree} sub={[e.institution, e.year, e.grade && `GPA ${e.grade}`].filter(Boolean).join(" - ")} />)}</Section>
          <Section title="Work experience" empty={!r.experience.length}>{r.experience.map((e, i) => <Row key={i} main={e.title} sub={[e.company, e.duration].filter(Boolean).join(" - ")} body={e.description} />)}</Section>
          <Section title="Projects" empty={!r.projects.length}>{r.projects.map((p, i) => <Row key={i} main={p.name} sub={p.technologies?.join(", ")} body={p.description} />)}</Section>
          <Section title="Certifications" empty={!r.certifications.length}><ul className="list-disc space-y-1 pl-5 text-sm">{r.certifications.map((x) => <li key={x}>{x}</li>)}</ul></Section>
        </div>

        <div className="card p-6">
          <h2 className="mb-4 font-bold">Suggested job roles</h2>
          <div className="grid gap-4 sm:grid-cols-2">{a.suggested_roles.map((x) => <ProgressBar key={x.role} value={x.match} label={x.role} />)}</div>
          <Link to={`/skill-gap/${a.id}`} className="mt-5 inline-block text-sm font-semibold text-brand-700">See skill gaps and what to learn</Link>
        </div>
      </div>
    </>
  );
}

const Section = ({ title, empty, children }) => (
  <>
    <h3 className="mb-2 mt-6 text-sm font-bold">{title}</h3>
    {empty ? <p className="text-sm text-slate-400">Not detected</p> : <div className="space-y-3">{children}</div>}
  </>
);
const Row = ({ main, sub, body }) => (
  <div className="rounded-lg border border-slate-100 bg-slate-50 p-3 text-sm">
    <div className="font-semibold">{main || "-"}</div>{sub && <div className="text-slate-500">{sub}</div>}
    {body && <p className="mt-1.5 whitespace-pre-line text-slate-600">{body}</p>}
  </div>
);
