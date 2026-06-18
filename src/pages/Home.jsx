import { Link } from 'react-router-dom';
import { Zap, Activity, TrendingUp, Sliders, ArrowRight } from 'lucide-react';

const NODE_DEMO = [
  { name: 'Substation A', region: 'North Grid', pct: 62, status: 'normal' },
  { name: 'Substation B', region: 'East Grid', pct: 81, status: 'warning' },
  { name: 'Substation C', region: 'South Grid', pct: 47, status: 'normal' },
  { name: 'Substation D', region: 'West Grid', pct: 95, status: 'critical' },
  { name: 'Substation E', region: 'North Grid', pct: 58, status: 'normal' }
];

const DOT_COLOR = { normal: '#2DD4BF', warning: '#F59E0B', critical: '#F8717A' };

const FEATURES = [
  {
    icon: Activity,
    title: 'Real-time monitoring',
    body: 'Watch load, voltage, and status across every substation as it happens, with automatic alerts the moment a node drifts toward its limit.'
  },
  {
    icon: TrendingUp,
    title: 'Demand forecasting',
    body: 'See predicted load 24 hours or 7 days out, with confidence bands and accuracy tracking, so capacity decisions are made ahead of time, not after.'
  },
  {
    icon: Sliders,
    title: 'Load balancing controls',
    body: 'Shift or shed load between substations manually, or trigger automated rebalancing, and keep a full audit log of every action taken.'
  }
];

export default function Home() {
  return (
    <div className="min-h-screen">
      <header className="h-16 flex items-center justify-between px-8 border-b border-line">
        <div className="flex items-center gap-2">
          <Zap className="text-normal" size={20} strokeWidth={2.5} />
          <span className="font-display font-semibold text-ink tracking-tight">GridOps</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-muted hover:text-ink transition-colors">
            Sign in
          </Link>
          <Link
            to="/register"
            className="text-sm font-semibold bg-normal text-base px-4 py-2 rounded-lg hover:opacity-90 transition-opacity"
          >
            Get started
          </Link>
        </div>
      </header>

      <main className="px-8 py-20 max-w-6xl mx-auto">
        <div className="grid grid-cols-2 gap-16 items-center">
          <div>
            <h1 className="font-display text-4xl font-semibold text-ink leading-tight tracking-tight">
              See every watt before it moves.
            </h1>
            <p className="mt-5 text-muted text-base leading-relaxed">
              GridOps monitors substation load in real time, forecasts demand days in advance, and
              gives operators direct control to rebalance before a warning becomes an outage.
            </p>
            <div className="mt-8 flex items-center gap-4">
              <Link
                to="/register"
                className="flex items-center gap-2 text-sm font-semibold bg-normal text-base px-5 py-3 rounded-lg hover:opacity-90 transition-opacity"
              >
                Create free account <ArrowRight size={16} />
              </Link>
              <Link to="/login" className="text-sm font-medium text-ink hover:text-normal transition-colors">
                Sign in to your grid
              </Link>
            </div>
          </div>

          <div className="bg-panel border border-line rounded-xl p-6">
            <div className="flex items-center justify-between mb-5">
              <span className="text-xs font-mono text-muted">live preview</span>
              <span className="flex items-center gap-1.5 text-xs font-mono text-muted">
                <span className="w-1.5 h-1.5 rounded-full bg-normal pulse" /> LIVE
              </span>
            </div>
            <ul className="space-y-3">
              {NODE_DEMO.map((n) => (
                <li key={n.name} className="flex items-center gap-3">
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: DOT_COLOR[n.status], boxShadow: `0 0 10px 2px ${DOT_COLOR[n.status]}55` }}
                  />
                  <span className="text-sm text-ink font-medium flex-1">{n.name}</span>
                  <span className="text-xs text-muted">{n.region}</span>
                  <span className="text-xs font-mono text-ink tabular-nums w-10 text-right">{n.pct}%</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-28 grid grid-cols-3 gap-6">
          {FEATURES.map(({ icon: Icon, title, body }) => (
            <div key={title} className="bg-panel border border-line rounded-xl p-6">
              <Icon className="text-normal mb-4" size={22} strokeWidth={2} />
              <h3 className="font-display text-base font-semibold text-ink mb-2">{title}</h3>
              <p className="text-sm text-muted leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </main>

      <footer className="px-8 py-8 border-t border-line text-center text-xs text-muted">
        GridOps · smart grid load balancing &amp; forecasting
      </footer>
    </div>
  );
}
