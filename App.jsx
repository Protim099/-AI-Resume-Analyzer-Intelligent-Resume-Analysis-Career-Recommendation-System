import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { Spinner } from "./components/ui";
import { useAuth } from "./context/AuthContext";
import Admin from "./pages/Admin";
import AnalysisView from "./pages/AnalysisView";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import JobMatching from "./pages/JobMatching";
import Landing from "./pages/Landing";
import { Login, Register } from "./pages/AuthPages";
import Profile from "./pages/Profile";
import SkillGap from "./pages/SkillGap";
import Upload from "./pages/Upload";

function Guard({ admin, children }) {
  const { user, loading } = useAuth();
  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" replace />;
  if (admin && user.role !== "admin") return <Navigate to="/dashboard" replace />;
  return children;
}

export default function App() {
  const { user, loading } = useAuth();
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={!loading && user ? <Navigate to="/dashboard" replace /> : <Login />} />
      <Route path="/register" element={!loading && user ? <Navigate to="/dashboard" replace /> : <Register />} />
      <Route element={<Guard><Layout /></Guard>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/analysis" element={<AnalysisView />} />
        <Route path="/analysis/:id" element={<AnalysisView />} />
        <Route path="/job-matching" element={<JobMatching />} />
        <Route path="/skill-gap" element={<SkillGap />} />
        <Route path="/skill-gap/:id" element={<SkillGap />} />
        <Route path="/history" element={<History />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/admin" element={<Guard admin><Admin /></Guard>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
