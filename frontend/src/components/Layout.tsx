import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { BarChart3, BookOpen, ClipboardCheck, IdCard, LogOut, Menu, Scale, X } from "lucide-react";
import { useAuth } from "../auth";

export function Emblem({ size = 40 }: { size?: number }) {
  return <img src="/emblem.svg" width={size} height={size} alt="" aria-hidden />;
}

export default function Layout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const isAdmin = user?.role === "admin";

  const links = [
    ...(isAdmin ? [{ to: "/dashboard", label: "Rahbariyat paneli", icon: BarChart3 }] : []),
    { to: "/assessment", label: "Kompleks baholash", icon: ClipboardCheck },
    { to: user ? `/passport/${user.id}` : "/", label: isAdmin ? "Diagnostika pasporti" : "Mening pasportim", icon: IdCard },
    { to: "/catalog", label: "KSA katalogi (36)", icon: BookOpen },
    { to: "/ahp-calculator", label: "AHP kalkulyatori", icon: Scale },
  ];

  const nav = (
    <nav className="flex flex-col gap-1">
      {links.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={label}
          to={to}
          onClick={() => setOpen(false)}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
              isActive ? "bg-white/15 text-white" : "text-blue-100 hover:bg-white/10 hover:text-white"}`
          }
        >
          <Icon size={18} /> {label}
        </NavLink>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen bg-slate-50 md:flex">
      <aside className={`fixed inset-y-0 left-0 z-40 w-72 transform bg-navy p-4 text-white transition md:static md:translate-x-0 ${
        open ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="mb-6 flex items-center gap-3 px-1">
          <Emblem />
          <div>
            <div className="text-lg font-bold leading-tight">CyberComp-Gov</div>
            <div className="text-[11px] leading-tight text-blue-200">AKT xodimlari AX kompetensiyalarini baholash tizimi</div>
          </div>
          <button className="ml-auto md:hidden" onClick={() => setOpen(false)} aria-label="Yopish"><X /></button>
        </div>
        {nav}
        <div className="absolute inset-x-4 bottom-4 rounded-lg bg-white/10 p-3 text-xs">
          <div className="font-semibold">{user?.full_name}</div>
          <div className="mt-0.5 text-blue-200">{user?.position}</div>
          <button
            onClick={() => { signOut(); navigate("/login"); }}
            className="mt-3 flex items-center gap-2 text-blue-100 hover:text-white"
          >
            <LogOut size={14} /> Tizimdan chiqish
          </button>
        </div>
      </aside>
      {open && <div className="fixed inset-0 z-30 bg-black/40 md:hidden" onClick={() => setOpen(false)} />}
      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur md:px-8">
          <button className="md:hidden" onClick={() => setOpen(true)} aria-label="Menyu"><Menu /></button>
          <div className="text-xs text-slate-500">
            O‘zbekiston Respublikasi · Davlat organlari AKT mas’ul xodimlari attestatsiyasi
          </div>
          <span className="ml-auto rounded-full bg-navy-50 px-2.5 py-1 text-xs font-medium text-navy">
            {user?.role === "admin" ? "Attestatsiya komissiyasi" : `${user?.agency} · ${user?.category}`}
          </span>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6 md:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
