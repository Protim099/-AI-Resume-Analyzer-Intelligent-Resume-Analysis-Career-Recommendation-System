import { useEffect, useState } from "react";
import { Bar, Line } from "react-chartjs-2";
import { Activity, FileText, Trash2, Users } from "lucide-react";
import api, { errMsg, fmtDate } from "../api";
import { Alert, PageHeader, Spinner, StatCard } from "../components/ui";
import { useAuth } from "../context/AuthContext";

export default function Admin() {
  const { user: me } = useAuth();
  const [s, setS] = useState(null);
  const [users, setUsers] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [error, setError] = useState("");

  const load = () => {
    api.get("/admin/stats").then((r) => setS(r.data)).catch((e) => setError(errMsg(e)));
    api.get("/admin/users").then((r) => setUsers(r.data)).catch(() => {});
    api.get("/admin/resumes").then((r) => setResumes(r.data)).catch(() => {});
  };
  useEffect(load, []);

  const patch = async (id, body) => { try { await api.patch(`/admin/users/${id}`, body); load(); } catch (e) { setError(errMsg(e)); } };
  const del = async (u) => {
    if (!confirm(`Delete ${u.email} and all of their data?`)) return;
    try { await api.delete(`/admin/users/${u.id}`); load(); } catch (e) { setError(errMsg(e)); }
  };

  if (!s) return error ? <Alert>{error}</Alert> : <Spinner />;
  return (
    <>
      <PageHeader title="Admin dashboard" subtitle="Platform usage across all users." />
      <div className="space-y-6">
        <Alert>{error}</Alert>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard icon={Users} label="Users" value={s.total_users} />
          <StatCard icon={FileText} label="Resumes" value={s.total_resumes} />
          <StatCard icon={Activity} label="Analyses" value={s.total_analyses} />
          <StatCard icon={Activity} label="Average ATS score" value={s.average_ats} hint={s.average_match != null ? `Avg. job match ${s.average_match}%` : undefined} />
        </div>
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="card p-5"><h2 className="font-bold">Popular skills</h2><div className="mt-4 h-72">
            <Bar data={{ labels: s.popular_skills.map((k) => k.name), datasets: [{ data: s.popular_skills.map((k) => k.count), backgroundColor: "#14b8a6", borderRadius: 4 }] }} options={{ indexAxis: "y", maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { precision: 0 } } } }} /></div></div>
          <div className="card p-5"><h2 className="font-bold">ATS score distribution</h2><div className="mt-4 h-72">
            <Bar data={{ labels: s.ats_distribution.map((k) => k.range), datasets: [{ data: s.ats_distribution.map((k) => k.count), backgroundColor: ["#dc2626", "#d97706", "#65a30d", "#0f9488"], borderRadius: 4 }] }} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { ticks: { precision: 0 } } } }} /></div></div>
          <div className="card p-5"><h2 className="font-bold">Sign-ups, last 14 days</h2><div className="mt-4 h-72">
            <Line data={{ labels: s.signups.map((k) => k.date.slice(5)), datasets: [{ data: s.signups.map((k) => k.count), borderColor: "#0f766e", backgroundColor: "rgba(15,118,110,.12)", fill: true, tension: 0.3 }] }} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { ticks: { precision: 0 } } } }} /></div></div>
        </div>
        <div className="card overflow-hidden"><h2 className="p-5 font-bold">Users</h2>
          <div className="overflow-x-auto"><table className="w-full"><thead><tr><th className="th">Name</th><th className="th">Email</th><th className="th">Role</th><th className="th">Resumes</th><th className="th">Analyses</th><th className="th">Joined</th><th className="th">Status</th><th className="th"></th></tr></thead>
            <tbody>{users.map((u) => (
              <tr key={u.id}><td className="td font-medium">{u.full_name}</td><td className="td">{u.email}</td>
                <td className="td"><select className="rounded border border-slate-300 px-1.5 py-1 text-xs" value={u.role} disabled={u.id === me.id} onChange={(e) => patch(u.id, { role: e.target.value })} aria-label={`Role for ${u.email}`}><option>user</option><option>admin</option></select></td>
                <td className="td">{u.resumes}</td><td className="td">{u.analyses}</td><td className="td">{fmtDate(u.created_at)}</td>
                <td className="td"><button disabled={u.id === me.id} onClick={() => patch(u.id, { is_active: !u.is_active })} className={`chip ${u.is_active ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"} disabled:opacity-60`}>{u.is_active ? "Active" : "Disabled"}</button></td>
                <td className="td text-right"><button disabled={u.id === me.id} className="text-red-500 hover:text-red-700 disabled:opacity-30" aria-label={`Delete ${u.email}`} onClick={() => del(u)}><Trash2 className="h-4 w-4" /></button></td></tr>))}</tbody></table></div></div>
        <div className="card overflow-hidden"><h2 className="p-5 font-bold">Latest resumes</h2>
          <div className="overflow-x-auto"><table className="w-full"><thead><tr><th className="th">File</th><th className="th">Owner</th><th className="th">Skills found</th><th className="th">Uploaded</th></tr></thead>
            <tbody>{resumes.slice(0, 10).map((r) => <tr key={r.id}><td className="td font-medium">{r.filename}</td><td className="td">{r.owner}</td><td className="td">{r.skills}</td><td className="td">{fmtDate(r.uploaded_at)}</td></tr>)}
              {resumes.length === 0 && <tr><td className="td text-slate-500" colSpan={4}>No resumes uploaded yet.</td></tr>}</tbody></table></div></div>
      </div>
    </>
  );
}
