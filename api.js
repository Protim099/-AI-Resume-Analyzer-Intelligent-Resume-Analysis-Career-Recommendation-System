import axios from "axios";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "/api", timeout: 120000 });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const isAuthCall = err.config?.url?.startsWith("/auth/login") || err.config?.url?.startsWith("/auth/register");
    if (err.response?.status === 401 && !isAuthCall) {
      localStorage.removeItem("token");
      if (!location.pathname.startsWith("/login")) location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const errMsg = (err, fallback = "Something went wrong. Please try again.") => {
  if (!err.response) return "Cannot reach the server. Check that the backend is running.";
  const d = err.response.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((e) => e.msg).join("; ");
  return fallback;
};

export const fmtDate = (d) =>
  d ? new Date(d).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "-";
export const fmtDateTime = (d) =>
  d ? new Date(d).toLocaleString(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) : "-";

export const scoreColor = (s) => (s >= 80 ? "#0f9488" : s >= 65 ? "#65a30d" : s >= 50 ? "#d97706" : "#dc2626");
export const scoreLabel = (s) => (s >= 80 ? "Excellent" : s >= 65 ? "Good" : s >= 50 ? "Fair" : "Needs work");

export default api;
