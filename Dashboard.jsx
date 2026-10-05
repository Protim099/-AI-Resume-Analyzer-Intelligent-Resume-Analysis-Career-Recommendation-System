import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, Line } from "react-chartjs-2";
import { Award, FileText, FileUp, GitCompare, TrendingUp } from "lucide-react";
import api, { errMsg, fmtDate, scoreColor } from "../api";
import { Alert, Empty, PageHeader, Spinner, StatCard } from "../components/ui";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [s, setS] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { api.get("/dashboard/stats").then((r) => setS(r.data)).catch((e) => setError(errMsg(e))); }, []);

  if (error) return <Alert>{error}</Alert>;
  if (!s) return <Spinner />;
  const first = user?.full_name?.split(" ")[0];

  return (
    <>
      <PageHeader title={`Hello, ${first}`} subtitle="Here is how your resumes are performing.">
        <Link to="/upload" className="btn-primary"><FileUp className="h-4 w-4" />Upload resume</Link>
      </PageHeader>
      {s.total_resumes === 0 ? (
        <Empty icon={FileText} title="No resumes yet" text="Upload a PDF or DOCX resume to get your first ATS score and recommendations." action={<Link to="/upload" className="btn-primary">Upload your resume</Link>} />
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard icon={FileText} label="Resumes" value={s.total_resumes} hint={`${s.total_analyses} analyses run`} />
            <StatCard icon={Award} label="Latest ATS score" value={s.latest_ats ?? "-"} hint={`Best: ${Math.round(s.best_ats)}`} />
            <StatCard icon={TrendingUp} label="Average ATS score" value={s.average_ats} />
            <StatCard icon={GitCompare} label="Avg. job match" value={s.average_match != null ? `${s.average_match}%` : "-"} hint={`${s.job_matches} job comparisons`} />
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="card p-5 lg:col-span-2">
              <h2 className="font-bold">ATS score over time</h2>
              <div className="mt-4 h-64">
                <Line data={{ labels: s.ats_trend.map((p) => fmtDate(p.date)), datasets: [{ data: s.ats_trend.map((p) => p.score), borderColor: "#0f766e", backgroundColor: "rgba(15,118,110,.12)", fill: true, tension: 0.3, pointRadius: 4 }] }}
                  options={{ maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100 } } }} />
              </div>
            </div>
            <div className="card p-5">
              <h2 className="font-bold">Your top skills</h2>
              <div className="mt-4 h-64">
                <Bar data={{ labels: s.top_skills.map((k) => k.name), datasets: [{ data: s.top_skills.map((k) => k.count), backgroundColor: "#14b8a6", borderRadius: 4 }] }}
                  options={{ indexAxis: "y", maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { precision: 0 } } } }} />
              </div>
            </div>
          </div>
          <div className="card overflow-hidden">
            <div className="flex items-center justify-between p-5"><h2 className="font-bold">Recent analyses</h2><Link to="/history" className="text-sm font-semibold text-brand-700">View all</Link></div>
            <div className="overflow-x-auto"><table className="w-full"><thead><tr><th className="th">Resume</th><th className="th">Type</th><th className="th">ATS</th><th className="th">Job match</th><th className="th">Date</th><th className="th"></th></tr></thead>
              <tbody>{s.recent.map((a) => (
                <tr key={a.id}><td className="td font-medium">{a.resume_filename}</td><td className="td">{a.job_title || "General ATS"}</td>
                  <td className="td font-bold" style={{ color: scoreColor(a.ats_score) }}>{Math.round(a.ats_score)}</td>
                  <td className="td">{a.job_match_score != null ? `${a.job_match_score}%` : "-"}</td><td className="td">{fmtDate(a.created_at)}</td>
                  <td className="td text-right"><Link className="font-semibold text-brand-700" to={`/analysis/${a.id}`}>Open</Link></td></tr>))}</tbody></table></div>
          </div>
        </div>
      )}
    </>
  );
}
