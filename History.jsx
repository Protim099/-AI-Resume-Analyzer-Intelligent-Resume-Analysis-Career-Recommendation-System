import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Download, History as HistoryIcon, Trash2 } from "lucide-react";
import api, { errMsg, fmtDate, fmtDateTime, scoreColor } from "../api";
import { Alert, Empty, PageHeader, Spinner } from "../components/ui";
import { downloadReport } from "../components/download";

const ACTIONS = { resume_upload: "Uploaded resume", ats_analysis: "ATS analysis", job_match: "Job match", report_download: "Downloaded report", resume_delete: "Deleted resume", analysis_delete: "Deleted analysis" };

export default function History() {
  const [rows, setRows] = useState(null);
  const [log, setLog] = useState([]);
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState("");

  const load = () => {
    api.get("/analysis").then((r) => setRows(r.data)).catch((e) => setError(errMsg(e)));
    api.get("/history").then((r) => setLog(r.data)).catch(() => {});
  };
  useEffect(load, []);

  const shown = useMemo(() => (rows || []).filter((r) =>
    (filter === "all" || (filter === "job" ? r.has_job_match : !r.has_job_match)) &&
    `${r.resume_filename} ${r.job_title || ""}`.toLowerCase().includes(q.toLowerCase())), [rows, q, filter]);

  const remove = async (id) => {
    if (!confirm("Delete this analysis?")) return;
    try { await api.delete(`/analysis/${id}`); load(); } catch (e) { setError(errMsg(e)); }
  };

  if (!rows) return error ? <Alert>{error}</Alert> : <Spinner />;
  return (
    <>
      <PageHeader title="Analysis history" subtitle="Every analysis you have run, saved in your account." />
      <div className="space-y-6">
        <Alert>{error}</Alert>
        {rows.length === 0 ? <Empty icon={HistoryIcon} title="No history yet" text="Your analyses will be listed here." action={<Link to="/upload" className="btn-primary">Upload resume</Link>} /> : (
          <div className="card overflow-hidden">
            <div className="flex flex-wrap gap-3 p-5">
              <input className="input !w-64" placeholder="Search by resume or job" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search" />
              <select className="input !w-auto" value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filter">
                <option value="all">All analyses</option><option value="ats">ATS only</option><option value="job">Job matches</option></select>
            </div>
            <div className="overflow-x-auto"><table className="w-full"><thead><tr><th className="th">#</th><th className="th">Resume</th><th className="th">Job</th><th className="th">ATS</th><th className="th">Match</th><th className="th">Date</th><th className="th"></th></tr></thead>
              <tbody>{shown.map((a) => (
                <tr key={a.id}><td className="td text-slate-400">{a.id}</td><td className="td font-medium">{a.resume_filename}</td><td className="td">{a.job_title || <span className="text-slate-400">General</span>}</td>
                  <td className="td font-bold" style={{ color: scoreColor(a.ats_score) }}>{Math.round(a.ats_score)}</td><td className="td">{a.job_match_score != null ? `${a.job_match_score}%` : "-"}</td><td className="td">{fmtDate(a.created_at)}</td>
                  <td className="td"><div className="flex items-center justify-end gap-3"><Link className="font-semibold text-brand-700" to={`/analysis/${a.id}`}>View</Link>
                    <button aria-label="Download report" className="text-slate-500 hover:text-brand-700" onClick={() => downloadReport(a.id)}><Download className="h-4 w-4" /></button>
                    <button aria-label="Delete analysis" className="text-red-500 hover:text-red-700" onClick={() => remove(a.id)}><Trash2 className="h-4 w-4" /></button></div></td></tr>))}
                {shown.length === 0 && <tr><td className="td text-slate-500" colSpan={7}>No analyses match your search.</td></tr>}</tbody></table></div>
          </div>)}
        {log.length > 0 && (
          <div className="card p-6"><h2 className="mb-4 font-bold">Recent activity</h2>
            <ul className="divide-y divide-slate-100">{log.slice(0, 15).map((h) => (
              <li key={h.id} className="flex flex-wrap items-center justify-between gap-2 py-2.5 text-sm"><span><span className="font-semibold">{ACTIONS[h.action] || h.action}</span> <span className="text-slate-500">{h.details}</span></span><span className="text-xs text-slate-400">{fmtDateTime(h.created_at)}</span></li>))}</ul></div>)}
      </div>
    </>
  );
}
