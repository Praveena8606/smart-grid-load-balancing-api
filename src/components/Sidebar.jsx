import { NavLink } from 'react-router-dom';
import { Activity, TrendingUp, AlertTriangle, Sliders, Zap, LogOut } from 'lucide-react';

const links = [
  { to: '/dashboard', label: 'Overview', icon: Activity },
  { to: '/dashboard/forecasting', label: 'Forecasting', icon: TrendingUp },
  { to: '/dashboard/alerts', label: 'Alerts', icon: AlertTriangle },
  { to: '/dashboard/controls', label: 'Controls', icon: Sliders }
];

export default function Sidebar({ alertCount, user, onLogout }) {
  return (
    <aside className="w-60 shrink-0 bg-panel border-r border-line flex flex-col h-screen sticky top-0">
      <div className="flex items-center gap-2 px-5 h-16 border-b border-line">
        <Zap className="text-normal" size={20} strokeWidth={2.5} />
        <span className="font-display font-semibold text-ink tracking-tight">GridOps</span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/dashboard'}
            className={({ isActive }) =>
              `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-raised text-ink shadow-glow'
                  : 'text-muted hover:text-ink hover:bg-raised/60'
              }`
            }
          >
            <span className="flex items-center gap-3">
              <Icon size={17} strokeWidth={2} />
              {label}
            </span>
            {label === 'Alerts' && alertCount > 0 && (
              <span className="text-xs font-mono bg-crit/20 text-crit px-1.5 py-0.5 rounded-md">
                {alertCount}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-3 py-4 border-t border-line">
        <div className="flex items-center justify-between px-2 py-2 rounded-lg">
          <div className="min-w-0">
            <p className="text-sm text-ink font-medium truncate">{user?.name}</p>
            <p className="text-xs text-muted truncate">{user?.email}</p>
          </div>
          <button
            onClick={onLogout}
            title="Sign out"
            className="shrink-0 p-2 rounded-lg text-muted hover:text-crit hover:bg-raised transition-colors"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
