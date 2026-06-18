import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Inbox } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';

export default function Alerts({ alerts, acknowledgeAlert }) {
  const [resolved, setResolved] = useState([]);
  const [tab, setTab] = useState('active');

  useEffect(() => {
    if (tab === 'resolved') {
      api.getAlerts('resolved').then(setResolved);
    }
  }, [tab]);

  const list = tab === 'active' ? alerts : resolved;

  return (
    <div className="p-8 space-y-6">
      <div className="flex bg-panel border border-line rounded-lg p-1 w-fit">
        {['active', 'resolved'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-colors ${
              tab === t ? 'bg-normal/15 text-normal' : 'text-muted hover:text-ink'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="bg-panel border border-line rounded-xl overflow-hidden">
        {list.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted gap-3">
            <Inbox size={28} />
            <p className="text-sm">No {tab} alerts. The grid is operating within normal parameters.</p>
          </div>
        ) : (
          <ul>
            {list.map((a) => (
              <li
                key={a.id}
                className="flex items-center justify-between px-6 py-4 border-b border-line/60 last:border-0"
              >
                <div className="flex items-start gap-3">
                  <AlertTriangle
                    size={18}
                    className={a.severity === 'critical' ? 'text-crit mt-0.5' : 'text-warn mt-0.5'}
                  />
                  <div>
                    <p className="text-sm text-ink font-medium">{a.message}</p>
                    <p className="text-xs text-muted mt-1 font-mono">
                      {a.node_name} · {new Date(a.triggered_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={a.severity} />
                  {tab === 'active' && (
                    <button
                      onClick={() => acknowledgeAlert(a.id)}
                      className="flex items-center gap-1.5 text-xs font-medium text-ink bg-raised hover:bg-line border border-line px-3 py-1.5 rounded-lg transition-colors"
                    >
                      <CheckCircle2 size={14} />
                      Acknowledge
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
