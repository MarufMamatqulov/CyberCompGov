import { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BarChart3,
  BookOpen,
  ClipboardCheck,
  IdCard,
  LogOut,
  Menu,
  Scale,
  Shield,
  X,
} from "lucide-react";
import { useAuth } from "../auth";

export function Emblem({ size = 40 }: { size?: number }) {
  return <img src="/emblem.svg" width={size} height={size} alt="Gerb" aria-hidden />;
}

const ROLE_CONFIG: Record<string, { label: string; badgeClass: string; roleDesc: string }> = {
  admin: {
    label: "Attestatsiya komissiyasi raisi",
    badgeClass: "bg-amber-100 text-amber-900 border-amber-300",
    roleDesc: "Komissiya",
  },
  expert: {
    label: "Mustaqil ekspert / Auditor",
    badgeClass: "bg-purple-100 text-purple-900 border-purple-300",
    roleDesc: "Ekspertiza guruhi",
  },
  supervisor: {
    label: "Tashkilot AKT rahbari",
    badgeClass: "bg-emerald-100 text-emerald-900 border-emerald-300",
    roleDesc: "Idora mas’uli",
  },
  officer: {
    label: "AKT mas’ul mutaxassisi",
    badgeClass: "bg-sky-100 text-sky-900 border-sky-300",
    roleDesc: "Attestatsiya nomzodi",
  },
};

export default function Layout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const role = user?.role ?? "officer";
  const isLeadership = role === "admin" || role === "expert" || role === "supervisor";
  const roleInfo = ROLE_CONFIG[role] ?? ROLE_CONFIG.officer;

  // Build navigation links according to role
  const links = [
    ...(isLeadership
      ? [
          {
            to: "/dashboard",
            label: role === "supervisor" ? "Tashkilot xodimlari paneli" : "Rahbariyat va monitoring paneli",
            icon: BarChart3,
          },
        ]
      : []),
    ...(role === "admin" || role === "officer"
      ? [{ to: "/assessment", label: "Kompleks baholash", icon: ClipboardCheck }]
      : []),
    {
      to: isLeadership ? "/passport/2" : `/passport/${user?.id ?? 2}`,
      label: isLeadership ? "Diagnostika pasporti" : "Mening pasportim",
      icon: IdCard,
    },
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
              isActive
                ? "bg-white/20 text-white font-semibold shadow-sm"
                : "text-blue-100 hover:bg-white/10 hover:text-white"
            }`
          }
        >
          <Icon size={18} /> {label}
        </NavLink>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen bg-slate-50 md:flex">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col bg-navy p-4 text-white transition md:static md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="mb-6 flex items-center gap-3 px-1">
          <Emblem />
          <div>
            <div className="text-lg font-bold leading-tight">CyberComp-Gov</div>
            <div className="text-[11px] leading-tight text-blue-200">
              Axborot xavfsizligi kompetensiyalarini baholash tizimi
            </div>
          </div>
          <button
            className="ml-auto md:hidden text-slate-300 hover:text-white"
            onClick={() => setOpen(false)}
            aria-label="Yopish"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">{nav}</div>

        {/* User Card in Sidebar */}
        <div className="mt-auto rounded-xl bg-white/10 p-3.5 text-xs border border-white/10">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white/20 text-xs font-bold text-white">
              {user?.full_name?.charAt(0) ?? "U"}
            </span>
            <div className="min-w-0 flex-1">
              <div className="truncate font-semibold text-white">{user?.full_name}</div>
              <div className="truncate text-[11px] text-blue-200">{roleInfo.label}</div>
            </div>
          </div>
          <div className="mt-2 text-[11px] text-blue-100/80 truncate">
            {user?.agency}
          </div>
          <button
            onClick={() => {
              signOut();
              navigate("/login");
            }}
            className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-white/10 py-1.5 text-xs text-blue-100 transition hover:bg-white/20 hover:text-white"
          >
            <LogOut size={13} /> Tizimdan chiqish
          </button>
        </div>
      </aside>

      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm md:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Main Container */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top Navbar */}
        <header className="sticky top-0 z-20 flex items-center justify-between gap-4 border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur md:px-8">
          <div className="flex items-center gap-3">
            <button
              className="rounded-lg p-1 text-slate-600 hover:bg-slate-100 md:hidden"
              onClick={() => setOpen(true)}
              aria-label="Menyu"
            >
              <Menu size={22} />
            </button>
            <div>
              <div className="hidden items-center gap-2 text-xs font-semibold text-slate-700 sm:flex">
                <span>CyberComp-Gov · Axborot xavfsizligi kompetensiyalarini baholash tizimi</span>
                <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-800 border border-amber-200">
                  Sinov talqini (Beta)
                </span>
              </div>
              <div className="text-xs text-slate-500 sm:hidden">
                CyberComp-Gov (Beta)
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold shadow-sm ${roleInfo.badgeClass}`}
            >
              <Shield size={12} className="inline mr-1 -mt-0.5" />
              {roleInfo.label}
            </span>
            <span className="hidden text-xs text-slate-500 md:inline">
              {user?.agency}
            </span>
          </div>
        </header>

        {/* Page Content */}
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 md:px-8">
          <Outlet />
        </main>

        {/* Global Official Footer */}
        <footer className="mt-auto border-t border-slate-200 bg-white px-4 py-5 text-xs text-slate-500 md:px-8">
          <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 md:flex-row">
            <div>
              © 2026 CyberComp-Gov. Barcha huquqlar himoyalangan.
            </div>
            <div className="flex items-center gap-4">
              <Link to="/privacy-policy" className="hover:text-slate-800 hover:underline">
                Maxfiylik siyosati
              </Link>
              <span>·</span>
              <Link to="/terms" className="hover:text-slate-800 hover:underline">
                Foydalanish shartlari
              </Link>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
