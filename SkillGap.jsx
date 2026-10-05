import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Bar } from "react-chartjs-2";
import { Target } from "lucide-react";
import api, { errMsg, fmtDate } from "../api";
import { Alert, Chips, Empty, PageHeader, PriorityBadge, Spinner } from "../components/ui";

export default function SkillGap() {
  const { id } = useParams();
  const nav = useNavigate();
  const [list, setList] = useState(null);
  const [a, setA] = useState(null);
  const [error, setError] = useState("");

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
  if (!list.length) return <Empty icon={Target} title="No analysis to review" text="Upload a resume to see your skill gaps." action={<Link to="/upload" className="btn-primary">Upload resume</Link>} />;
  if (!a) return <Spinner />;
  const roles = a.suggested_roles;

  return (
    <>
      <PageHeader title="Skill gap analysis" subtitle="Skills you are missing for the roles that fit you best.">
        <select className="input !w-auto" value={a.id} onChange={(e) => nav(`/skill-gap/${e.target.value}`)} aria-label="Choose analysis">
          {list.map((x) => <option key={x.id} value={x.id}>#{x.id} - {x.resume_filename} - {x.job_title || "ATS"} ({fmtDate(x.created_at)})</option>)}
        </select>
      </PageHeader>
      <div className="space-y-6">
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="card p-6"><h2 className="mb-4 font-bold">Best-fit roles</h2>
            {roles.length ? <div className="h-64"><Bar data={{ labels: roles.map((r) => r.role), datasets: [{ data: roles.map((r) => r.match), backgroundColor: "#0f766e", borderRadius: 4 }] }}
              options={{ indexAxis: "y", maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => `${c.raw}% match` } } }, scales: { x: { min: 0, max: 100, ticks: { callback: (v) => `${v}%` } } } }} /></div>
              : <p className="text-sm text-slate-500">Add more technical skills to your resume to get role suggestions.</p>}</div>
          <div className="card p-6"><h2 className="mb-4 font-bold">Role details</h2>
            <div className="space-y-4">{roles.slice(0, 3).map((r) => (
              <div key={r.role}><div className="font-semibold">{r.role} <span className="text-sm font-normal text-slate-500">({r.match}%)</span></div>
                <div className="mt-1.5 text-xs font-semibold text-slate-500">You have</div><Chips tone="green" items={r.matched} />
                <div className="mt-2 text-xs font-semibold text-slate-500">You need</div><Chips tone="red" items={r.missing} empty="Nothing essential missing" /></div>))}</div></div>
        </div>
        {a.has_job_match && a.missing_skills.length > 0 && (
          <div className="card p-6"><h2 className="mb-1 font-bold">Missing for "{a.job_title}"</h2><p className="mb-3 text-sm text-slate-500">These skills appear in the job description but not on your resume.</p><Chips tone="red" items={a.missing_skills.map((s) => s.name)} /></div>)}
        <div className="card overflow-hidden"><h2 className="p-6 pb-4 font-bold">Skill gaps</h2>
          {a.skill_gaps.length ? <div className="overflow-x-auto"><table className="w-full"><thead><tr><th className="th">Skill</th><th className="th">Category</th><th className="th">Priority</th><th className="th">Needed for</th></tr></thead>
            <tbody>{a.skill_gaps.map((g) => <tr key={g.skill}><td className="td font-semibold">{g.skill}</td><td className="td">{g.category}</td><td className="td"><PriorityBadge p={g.priority} /></td><td className="td text-slate-600">{[...new Set(g.roles)].join(", ")}</td></tr>)}</tbody></table></div>
            : <p className="px-6 pb-6 text-sm text-slate-500">No gaps found for your top roles.</p>}</div>
        <div className="card p-6"><h2 className="mb-4 font-bold">What to learn next</h2>
          <ol className="grid gap-3 sm:grid-cols-2">{a.learning_path.map((l, i) => (
            <li key={l.technology} className="flex items-start gap-3 rounded-lg border border-slate-100 bg-slate-50 p-3"><span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-brand-700 text-xs font-bold text-white">{i + 1}</span>
              <div><div className="font-semibold">{l.technology} <PriorityBadge p={l.priority} /></div><div className="text-xs text-slate-500">{l.reason}</div></div></li>))}</ol></div>
      </div>
    </>
  );
}
