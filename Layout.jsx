import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { BarChart3, FileSearch, FileUp, GitCompare, History, LayoutDashboard, LogOut, Menu, ShieldCheck, Target, User, X } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/upload", label: "Upload Resume", icon: FileUp },
  { to: "/analysis", label: "Resume Analysis", icon: FileSearch },
  { to: "/job-matching", label: "Job Matching", icon: GitCompare },
  { to: "/skill-gap", label: "Skill Gap", icon: Target },
  { to: "/history", label: "History", icon: History },
  { to: "/profile", label: "Profile", icon: User },
];

export const Logo = ({ dark }) => (
  <div className="flex items-center gap-2.5">
    <div className="grid h-9 w-9 place-items-center rounded-lg bg-brand-700 text-white"><BarChart3 className="h-5 w-5" /></div>
    <span className={`text-lg font-extrabold tracking-tight ${dark ? "text-white" : "text-ink"}`}>ResumeIQ</span>
  </div>
);

export default function Layout() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const items = user?.role === "admin" ? [...nav, { to: "/admin", label: "Admin", icon: ShieldCheck }] : nav;

  const link = ({ isActive }) =>
    `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${isActive ? "bg-white/10 text-white" : "text-slate-300 hover:bg-white/5 hover:text-white"}`;

  return (
    <div className="min-h-screen lg:flex">
      <aside className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-ink p-4 transition-transform lg:static lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="mb-6 flex items-center justify-between px-1 pt-1">
          <Logo dark />
          <button className="text-slate-300 lg:hidden" onClick={() => setOpen(false)} aria-label="Close menu"><X /></button>
        </div>
        <nav className="flex-1 space-y-1" aria-label="Main">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className={link} onClick={() => setOpen(false)}><Icon className="h-4.5 w-4.5 h-[18px] w-[18px]" />{label}</NavLink>
          ))}
        </nav>
        <div className="mt-4 border-t border-white/10 pt-4">
          <div className="mb-3 px-1">
            <div className="truncate text-sm font-semibold text-white">{user?.full_name}</div>
            <div className="truncate text-xs text-slate-400">{user?.email}</div>
          </div>
          <button onClick={async () => { await logout(); navigate("/"); }} className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-300 hover:bg-white/5 hover:text-white">
            <LogOut className="h-[18px] w-[18px]" /> Log out
          </button>
        </div>
      </aside>
      {open && <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={() => setOpen(false)} />}
      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur lg:hidden">
          <button onClick={() => setOpen(true)} aria-label="Open menu"><Menu /></button><Logo />
        </header>
        <main className="mx-auto max-w-6xl p-4 sm:p-6 lg:p-8"><Outlet /></main>
      </div>
    </div>
  );
}
