import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  ArrowLeftRight,
  PiggyBank,
  Target,
  Sparkles,
  Upload,
  LogOut,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { to: "/budgets", label: "Budgets", icon: PiggyBank },
  { to: "/goals", label: "Goals", icon: Target },
  { to: "/import", label: "Import CSV", icon: Upload },
  { to: "/assistant", label: "AI Assistant", icon: Sparkles },
];

export default function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 shrink-0 border-r border-ink-border bg-ink-surface/50 flex flex-col">
        <div className="px-6 py-6">
          <div className="flex items-baseline gap-2">
            <span className="font-display text-2xl font-semibold tracking-tight">FinSight</span>
            <span className="font-display text-2xl text-emerald">AI</span>
          </div>
          <p className="text-xs text-paper-faint mt-1">Ledger &amp; forecast</p>
        </div>

        <nav className="flex-1 px-3 space-y-1">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition ${
                  isActive
                    ? "bg-emerald/10 text-emerald border border-emerald/20"
                    : "text-paper-muted hover:text-paper hover:bg-ink-raised"
                }`
              }
            >
              <Icon size={18} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-ink-border">
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="w-9 h-9 rounded-full bg-gold/15 border border-gold/30 flex items-center justify-center font-display text-gold font-semibold">
              {user?.full_name?.[0]?.toUpperCase() ?? "?"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-paper truncate">{user?.full_name}</p>
              <p className="text-xs text-paper-faint truncate">{user?.email}</p>
            </div>
            <button
              onClick={logout}
              className="text-paper-faint hover:text-coral transition p-1.5 rounded-lg hover:bg-coral/10"
              aria-label="Log out"
              title="Log out"
            >
              <LogOut size={17} />
            </button>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
