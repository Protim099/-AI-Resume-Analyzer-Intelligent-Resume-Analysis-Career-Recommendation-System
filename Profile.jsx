import { useState } from "react";
import api, { errMsg, fmtDate } from "../api";
import { Alert, PageHeader } from "../components/ui";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user, setUser } = useAuth();
  const [name, setName] = useState(user.full_name);
  const [pw, setPw] = useState({ current_password: "", new_password: "" });
  const [msg, setMsg] = useState({ p: "", pe: "", w: "", we: "" });

  const saveProfile = async (e) => {
    e.preventDefault(); setMsg((m) => ({ ...m, p: "", pe: "" }));
    try { const { data } = await api.put("/users/me", { full_name: name }); setUser(data); setMsg((m) => ({ ...m, p: "Profile updated." })); }
    catch (err) { setMsg((m) => ({ ...m, pe: errMsg(err) })); }
  };
  const savePw = async (e) => {
    e.preventDefault(); setMsg((m) => ({ ...m, w: "", we: "" }));
    try { await api.put("/users/me/password", pw); setPw({ current_password: "", new_password: "" }); setMsg((m) => ({ ...m, w: "Password changed." })); }
    catch (err) { setMsg((m) => ({ ...m, we: errMsg(err) })); }
  };

  return (
    <>
      <PageHeader title="Profile" subtitle="Manage your account details and password." />
      <div className="grid max-w-4xl gap-6 md:grid-cols-2">
        <form onSubmit={saveProfile} className="card space-y-4 p-6">
          <h2 className="font-bold">Account</h2><Alert type="success">{msg.p}</Alert><Alert>{msg.pe}</Alert>
          <div><label className="label" htmlFor="n">Full name</label><input id="n" required minLength={2} className="input" value={name} onChange={(e) => setName(e.target.value)} /></div>
          <div><label className="label" htmlFor="e">Email</label><input id="e" className="input bg-slate-50" value={user.email} disabled /></div>
          <p className="text-xs text-slate-500">Role: {user.role} - Member since {fmtDate(user.created_at)}</p>
          <button className="btn-primary">Save changes</button>
        </form>
        <form onSubmit={savePw} className="card space-y-4 p-6">
          <h2 className="font-bold">Change password</h2><Alert type="success">{msg.w}</Alert><Alert>{msg.we}</Alert>
          <div><label className="label" htmlFor="cp">Current password</label><input id="cp" type="password" required className="input" autoComplete="current-password" value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} /></div>
          <div><label className="label" htmlFor="np">New password</label><input id="np" type="password" required minLength={8} className="input" autoComplete="new-password" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} />
            <p className="mt-1 text-xs text-slate-500">At least 8 characters, with a letter and a number.</p></div>
          <button className="btn-primary">Update password</button>
        </form>
      </div>
    </>
  );
}
