import type { ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./auth";
import Layout from "./components/Layout";
import { Spinner } from "./components/ui";
import AhpCalculator from "./pages/AhpCalculator";
import Assessment from "./pages/Assessment";
import Catalog from "./pages/Catalog";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import PassportPage from "./pages/Passport";
import Verify from "./pages/Verify";

function RequireAuth({ children, admin = false }: { children: ReactNode; admin?: boolean }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  if (admin && user.role !== "admin") return <Navigate to={`/passport/${user.id}`} replace />;
  return <>{children}</>;
}

function Home() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "admin" ? "/dashboard" : `/passport/${user.id}`} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/verify/:code" element={<Verify />} />
      <Route element={<RequireAuth><Layout /></RequireAuth>}>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<RequireAuth admin><Dashboard /></RequireAuth>} />
        <Route path="/assessment" element={<Assessment />} />
        <Route path="/passport/:officerId" element={<PassportPage />} />
        <Route path="/catalog" element={<Catalog />} />
        <Route path="/ahp-calculator" element={<AhpCalculator />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
