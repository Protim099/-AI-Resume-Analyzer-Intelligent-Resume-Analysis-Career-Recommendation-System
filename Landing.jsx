import { Link } from "react-router-dom";
import { ArrowRight, BarChart3, BrainCircuit, FileSearch, GitCompare, Lightbulb, ShieldCheck, Target } from "lucide-react";
import { Logo } from "../components/Layout";
import { useAuth } from "../context/AuthContext";

const features = [
  { icon: FileSearch, title: "Smart resume parsing", text: "Reads PDF and DOCX files and pulls out your contact details, education, experience, projects and certifications." },
  { icon: BarChart3, title: "ATS score out of 100", text: "See how an applicant tracking system rates your resume, with a score for each area and the exact fixes to make." },
  { icon: GitCompare, title: "Job description matching", text: "Paste a job posting and get a match score based on skills, keywords and the meaning of the text." },
  { icon: Target, title: "Skill gap analysis", text: "Find out which skills you are missing for the roles you want, and which technologies to learn first." },
  { icon: Lightbulb, title: "Career role suggestions", text: "Get job roles that fit the skills already on your resume, ranked by how closely they match." },
  { icon: ShieldCheck, title: "Private by default", text: "Your resumes are tied to your account. Only you can view, download or delete them." },
];
const steps = ["Upload your resume", "We read and structure it", "Get your ATS score", "Compare with a job", "Follow the action plan"];

export default function Landing() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen bg-white">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
        <Logo />
        <div className="flex items-center gap-2">
          {user ? <Link to="/dashboard" className="btn-primary">Open dashboard</Link> : (<>
            <Link to="/login" className="btn-secondary">Log in</Link>
            <Link to="/register" className="btn-primary">Create account</Link>
          </>)}
        </div>
      </header>

      <section className="mx-auto grid max-w-6xl items-center gap-10 px-5 py-14 lg:grid-cols-2 lg:py-20">
        <div>
          <h1 className="text-4xl font-extrabold leading-[1.1] sm:text-5xl">Find out why your resume gets rejected, then fix it.</h1>
          <p className="mt-5 max-w-xl text-lg text-slate-600">Upload your resume and get an ATS score, a list of missing skills for the job you want, and a clear plan to improve it.</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to={user ? "/upload" : "/register"} className="btn-primary px-6 py-3 text-base">Analyze my resume <ArrowRight className="h-4 w-4" /></Link>
            <a href="#how" className="btn-secondary px-6 py-3 text-base">How it works</a>
          </div>
        </div>
        <div className="card p-6 shadow-lg" aria-hidden="true">
          <div className="flex items-center gap-5">
            <div className="grid h-28 w-28 place-items-center rounded-full border-[10px] border-brand-600 border-r-slate-200 text-3xl font-extrabold text-ink">82</div>
            <div><div className="text-sm text-slate-500">ATS score</div><div className="text-xl font-bold">Good - 3 fixes away from Excellent</div></div>
          </div>
          <div className="mt-6 space-y-3">
            {[["Skills", 85], ["Experience", 70], ["Formatting", 90], ["Content quality", 62]].map(([l, v]) => (
              <div key={l}><div className="mb-1 flex justify-between text-xs font-medium text-slate-600"><span>{l}</span><span>{v}%</span></div>
                <div className="h-2 rounded-full bg-slate-100"><div className="h-2 rounded-full bg-brand-600" style={{ width: `${v}%` }} /></div></div>
            ))}
          </div>
          <div className="mt-6 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">Missing for this job: Kubernetes, CI/CD, Microservices</div>
        </div>
      </section>

      <section className="bg-slate-50 py-16">
        <div className="mx-auto max-w-6xl px-5">
          <h2 className="text-3xl font-extrabold">Everything you need to improve a resume</h2>
          <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {features.map(({ icon: Icon, title, text }) => (
              <div key={title} className="card p-6"><Icon className="h-6 w-6 text-brand-700" /><h3 className="mt-4 font-bold">{title}</h3><p className="mt-1.5 text-sm text-slate-600">{text}</p></div>
            ))}
          </div>
        </div>
      </section>

      <section id="how" className="mx-auto max-w-6xl px-5 py-16">
        <h2 className="text-3xl font-extrabold">How it works</h2>
        <ol className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {steps.map((s, i) => (
            <li key={s} className="card p-5"><div className="grid h-8 w-8 place-items-center rounded-full bg-brand-700 text-sm font-bold text-white">{i + 1}</div><div className="mt-3 font-semibold">{s}</div></li>
          ))}
        </ol>
        <p className="mt-6 flex items-center gap-2 text-sm text-slate-500"><BrainCircuit className="h-4 w-4" /> Built with spaCy, scikit-learn and Sentence Transformers.</p>
      </section>
      <footer className="border-t border-slate-200 py-6 text-center text-sm text-slate-500">ResumeIQ - AI Resume Analyzer & Career Assistant</footer>
    </div>
  );
}
