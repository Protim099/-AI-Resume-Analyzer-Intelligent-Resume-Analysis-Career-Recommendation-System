import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Download, FileUp, GitCompare, Loader2 } from "lucide-react";
import api, { errMsg } from "../api";
import { Alert, Chips, Empty, PageHeader, ProgressBar, ScoreRing, Spinner } from "../components/ui";
import { downloadReport } from "../components/download";

export default function JobMatching() {
  const fileRef = useRef();
  const [resumes, setResumes] = useState(null);
  const [form, setForm] = useState({ resume_id: "", job_title: "", job_description: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [res, setRes] = useState(null);

  useEffect(() => {
    api.get("/resumes").then((r) => { setResumes(r.data); if (r.data[0]) setForm((f) => ({ ...f, resume_id: r.data[0].id })); }).catch((e) => setError(errMsg(e)));
  }, []);

  const loadFile = async (f) => {
    if (!f) return;
    const fd = new FormData(); fd.append("file", f);
    try { const { data } = await api.post("/jobs/extract-text", fd); setForm((x) => ({ ...x, job_description: data.text })); setError(""); }
    catch (e) { setError(errMsg(e)); }
  };

  const submit = async (e) => {
    e.preventDefault(); setError(""); setBusy(true); setRes(null);
    try { const { data } = await api.post("/analysis/match", { ...form, resume_id: Number(form.resume_id) }); setRes(data); }
    catch (err) { setError(errMsg(err)); } finally { setBusy(false); }
  };

  if (!resumes) return error ? <Alert>{error}</Alert> : <Spinner />;
  if (!resumes.length) return <Empty icon={GitCompare} title="Upload a resume first" text="Job matching compares one of your resumes with a job description." action={<Link to="/upload" className="btn-primary">Upload resume</Link>} />;

  return (
    <>
      <PageHeader title="Job matching" subtitle="Paste a job description to see how well your resume fits." />
      <div className="grid gap-6 lg:grid-cols-5">
        <form onSubmit={submit} className="card space-y-4 p-6 lg:col-span-2">
          <Alert>{error}</Alert>
          <div><label className="label" htmlFor="resume">Resume</label>
            <select id="resume" className="input" value={form.resume_id} onChange={(e) => setForm({ ...form, resume_id: e.target.value })}>{resumes.map((r) => <option key={r.id} value={r.id}>{r.filename}</option>)}</select></div>
          <div><label className="label" htmlFor="title">Job title</label><input id="title" className="input" placeholder="e.g. Backend Developer" value={form.job_title} onChange={(e) => setForm({ ...form, job_title: e.target.value })} /></div>
          <div>
            <div className="mb-1.5 flex items-center justify-between"><label className="label !mb-0" htmlFor="jd">Job description</label>
              <button type="button" className="inline-flex items-center gap-1 text-xs font-semibold text-brand-700" onClick={() => fileRef.current.click()}><FileUp className="h-3.5 w-3.5" />Upload file</button>
              <input ref={fileRef} type="file" accept=".pdf,.docx,.txt" hidden onChange={(e) => loadFile(e.target.files[0])} /></div>
            <textarea id="jd" required minLength={30} rows={12} className="input" placeholder="Paste the full job posting here..." value={form.job_description} onChange={(e) => setForm({ ...form, job_description: e.target.value })} />
          </div>
          <button className="btn-primary w-full" disabled={busy}>{busy && <Loader2 className="h-4 w-4 animate-spin" />}{busy ? "Comparing..." : "Compare with resume"}</button>
        </form>

        <div className="space-y-6 lg:col-span-3">
          {busy && <div className="card"><Spinner label="Running semantic similarity and skill matching..." /></div>}
          {!busy && !res && <div className="card p-10 text-center text-sm text-slate-500">Your match score, matched skills and missing skills will appear here.</div>}
          {res && (<>
            <div className="card p-6">
              <div className="grid items-center gap-6 sm:grid-cols-2">
                <div><ScoreRing score={res.job_match_score} caption="Job match" /></div>
                <div className="space-y-4">
                  {res.skill_match_score != null && <ProgressBar label="Skills overlap" value={res.skill_match_score} />}
                  <ProgressBar label="Semantic similarity" value={res.semantic_score} />
                  <ProgressBar label="Keyword similarity" value={res.keyword_score} />
                  <p className="text-xs text-slate-400">Method: {res.similarity_method}</p>
                </div>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <Link to={`/analysis/${res.id}`} className="btn-secondary">Full analysis</Link>
                <Link to={`/skill-gap/${res.id}`} className="btn-secondary">Skill gaps</Link>
                <button className="btn-secondary" onClick={() => downloadReport(res.id)}><Download className="h-4 w-4" />Report</button>
              </div>
            </div>
            <div className="card p-6"><h2 className="mb-3 font-bold">Matched skills ({res.matched_skills.length})</h2><Chips tone="green" items={res.matched_skills.map((s) => s.name)} empty="No skills from the job description were found in your resume." /></div>
            <div className="card p-6"><h2 className="mb-3 font-bold">Missing skills ({res.missing_skills.length})</h2><Chips tone="red" items={res.missing_skills.map((s) => s.name)} empty="You cover every skill mentioned in the job description." />
              {res.missing_keywords.length > 0 && (<><h3 className="mb-2 mt-5 text-sm font-bold">Other keywords in the posting</h3><Chips items={res.missing_keywords} /></>)}</div>
            <div className="card p-6"><h2 className="mb-3 font-bold">How to improve this match</h2>
              <ul className="space-y-2 text-sm">{res.recommendations.filter((r) => ["Job Match", "Keywords"].includes(r.category)).map((r, i) => <li key={i} className="flex gap-2"><span className="text-brand-700">-</span>{r.text}</li>)}</ul></div>
          </>)}
        </div>
      </div>
    </>
  );
}
