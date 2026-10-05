import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle2, FileText, Trash2, UploadCloud } from "lucide-react";
import api, { errMsg, fmtDate, scoreColor } from "../api";
import { Alert, PageHeader, ProgressBar } from "../components/ui";

const STAGES = ["Uploading file", "Extracting text", "Reading sections and skills", "Calculating ATS score"];

export default function Upload() {
  const nav = useNavigate();
  const input = useRef();
  const [drag, setDrag] = useState(false);
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState(-1);
  const [error, setError] = useState("");
  const [resumes, setResumes] = useState([]);

  const load = useCallback(() => api.get("/resumes").then((r) => setResumes(r.data)).catch(() => {}), []);
  useEffect(() => { load(); }, [load]);

  const pick = (f) => {
    setError("");
    if (!f) return;
    const ext = f.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx"].includes(ext)) return setError("Only PDF and DOCX files are supported.");
    if (f.size > 5 * 1024 * 1024) return setError("File is too large. The limit is 5 MB.");
    setFile(f);
  };

  const submit = async () => {
    setError(""); setStage(0); setProgress(0);
    const form = new FormData();
    form.append("file", file);
    const timer = setInterval(() => setStage((s) => (s >= 1 && s < 3 ? s + 1 : s)), 1500);
    try {
      const { data } = await api.post("/resumes/upload", form, {
        onUploadProgress: (e) => { const p = Math.round((e.loaded * 100) / (e.total || 1)); setProgress(p); if (p >= 100) setStage(1); },
      });
      nav(`/analysis/${data.analysis_id}`);
    } catch (e) { setError(errMsg(e)); setStage(-1); } finally { clearInterval(timer); }
  };

  const remove = async (id) => {
    if (!confirm("Delete this resume and all of its analyses?")) return;
    try { await api.delete(`/resumes/${id}`); load(); } catch (e) { setError(errMsg(e)); }
  };
  const busy = stage >= 0;

  return (
    <>
      <PageHeader title="Upload resume" subtitle="PDF or DOCX, up to 5 MB. Use a text-based file, not a scanned image." />
      <div className="space-y-6">
        <Alert>{error}</Alert>
        <div
          onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)}
          onDrop={(e) => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files[0]); }}
          onClick={() => !busy && input.current.click()} role="button" tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && !busy && input.current.click()}
          className={`card cursor-pointer border-2 border-dashed p-10 text-center transition ${drag ? "border-brand-600 bg-brand-50" : "border-slate-300 hover:border-brand-500"}`}>
          <input ref={input} type="file" accept=".pdf,.docx" hidden onChange={(e) => pick(e.target.files[0])} />
          <UploadCloud className="mx-auto h-10 w-10 text-brand-700" />
          <p className="mt-3 font-semibold">Drag and drop your resume here</p>
          <p className="text-sm text-slate-500">or click to browse files</p>
        </div>

        {file && (
          <div className="card p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3"><FileText className="h-8 w-8 text-brand-700" />
                <div><div className="font-semibold">{file.name}</div><div className="text-xs text-slate-500">{(file.size / 1024).toFixed(0)} KB</div></div></div>
              <div className="flex gap-2">
                <button className="btn-secondary" disabled={busy} onClick={() => setFile(null)}>Remove</button>
                <button className="btn-primary" disabled={busy} onClick={submit}>{busy ? "Analyzing..." : "Analyze resume"}</button>
              </div>
            </div>
            {busy && (
              <div className="mt-5 space-y-3">
                <ProgressBar value={stage === 0 ? progress : 100} color="#0f766e" label={STAGES[Math.min(stage, 3)]} right={stage === 0 ? `${progress}%` : "In progress"} />
                <ul className="grid gap-1 text-xs text-slate-500 sm:grid-cols-4">
                  {STAGES.map((s, i) => <li key={s} className={`flex items-center gap-1.5 ${i <= stage ? "font-semibold text-brand-700" : ""}`}><CheckCircle2 className="h-3.5 w-3.5" />{s}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="card overflow-hidden">
          <h2 className="p-5 font-bold">Your resumes</h2>
          {resumes.length === 0 ? <p className="px-5 pb-6 text-sm text-slate-500">Nothing uploaded yet.</p> : (
            <div className="overflow-x-auto"><table className="w-full"><thead><tr><th className="th">File</th><th className="th">Name found</th><th className="th">Skills</th><th className="th">ATS</th><th className="th">Uploaded</th><th className="th"></th></tr></thead>
              <tbody>{resumes.map((r) => (
                <tr key={r.id}><td className="td font-medium">{r.filename}</td><td className="td">{r.full_name || "-"}</td><td className="td">{r.skills_count}</td>
                  <td className="td font-bold" style={{ color: scoreColor(r.latest_ats_score || 0) }}>{r.latest_ats_score != null ? Math.round(r.latest_ats_score) : "-"}</td>
                  <td className="td">{fmtDate(r.uploaded_at)}</td>
                  <td className="td text-right"><button className="text-red-600 hover:text-red-700" aria-label={`Delete ${r.filename}`} onClick={() => remove(r.id)}><Trash2 className="h-4 w-4" /></button></td></tr>))}</tbody></table></div>)}
        </div>
      </div>
    </>
  );
}
