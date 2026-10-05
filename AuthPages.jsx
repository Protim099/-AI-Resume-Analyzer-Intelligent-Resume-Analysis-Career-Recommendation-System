import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { errMsg } from "../api";
import { Alert } from "../components/ui";
import { Logo } from "../components/Layout";
import { useAuth } from "../context/AuthContext";

function Shell({ title, subtitle, children, footer }) {
  return (
    <div className="grid min-h-screen place-items-center bg-slate-50 p-4">
      <div className="w-full max-w-md">
        <Link to="/" className="mb-6 flex justify-center"><Logo /></Link>
        <div className="card p-7">
          <h1 className="text-2xl font-extrabold">{title}</h1>
          <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
          <div className="mt-6">{children}</div>
        </div>
        <p className="mt-5 text-center text-sm text-slate-600">{footer}</p>
      </div>
    </div>
  );
}

export function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try { const u = await login(f.email, f.password); nav(u.role === "admin" ? "/admin" : "/dashboard"); }
    catch (err) { setError(errMsg(err)); } finally { setBusy(false); }
  };
  return (
    <Shell title="Welcome back" subtitle="Log in to see your resume analyses." footer={<>New here? <Link className="font-semibold text-brand-700" to="/register">Create an account</Link></>}>
      <form onSubmit={submit} className="space-y-4">
        <Alert>{error}</Alert>
        <div><label className="label" htmlFor="email">Email</label><input id="email" type="email" required autoComplete="email" className="input" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></div>
        <div><label className="label" htmlFor="password">Password</label><input id="password" type="password" required autoComplete="current-password" className="input" value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></div>
        <button className="btn-primary w-full" disabled={busy}>{busy && <Loader2 className="h-4 w-4 animate-spin" />}Log in</button>
      </form>
    </Shell>
  );
}

export function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState({ name: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (f.password !== f.confirm) return setError("Passwords do not match.");
    setBusy(true);
    try { await register(f.name, f.email, f.password); nav("/upload"); }
    catch (err) { setError(errMsg(err)); } finally { setBusy(false); }
  };
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  return (
    <Shell title="Create your account" subtitle="Free. Takes less than a minute." footer={<>Already registered? <Link className="font-semibold text-brand-700" to="/login">Log in</Link></>}>
      <form onSubmit={submit} className="space-y-4">
        <Alert>{error}</Alert>
        <div><label className="label" htmlFor="name">Full name</label><input id="name" required minLength={2} className="input" value={f.name} onChange={set("name")} /></div>
        <div><label className="label" htmlFor="email">Email</label><input id="email" type="email" required className="input" value={f.email} onChange={set("email")} /></div>
        <div><label className="label" htmlFor="password">Password</label><input id="password" type="password" required minLength={8} autoComplete="new-password" className="input" value={f.password} onChange={set("password")} />
          <p className="mt-1 text-xs text-slate-500">At least 8 characters, with a letter and a number.</p></div>
        <div><label className="label" htmlFor="confirm">Confirm password</label><input id="confirm" type="password" required className="input" value={f.confirm} onChange={set("confirm")} /></div>
        <button className="btn-primary w-full" disabled={busy}>{busy && <Loader2 className="h-4 w-4 animate-spin" />}Create account</button>
      </form>
    </Shell>
  );
}
