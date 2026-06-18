import { useEffect, useState } from 'react';
import { Power, ArrowRightLeft, ScissorsLineDashed, Wand2 } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';

export default function Controls({ nodes, toggleNode }) {
  const [actionLog, setActionLog] = useState([]);
  const [action, setAction] = useState('shift_load');
  const [source, setSource] = useState('');
  const [target, setTarget] = useState('');
  const [amount, setAmount] = useState(50);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const refreshLog = () => api.getActionLog().then(setActionLog);

  useEffect(() => {
    refreshLog();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setFeedback(null);
    try {
      const payload = {
        action,
        source_node_id: source || undefined,
        target_node_id: action === 'shift_load' ? target || undefined : undefined,
        amount_kw: action === 'rebalance_auto' ? undefined : Number(amount)
      };
      const res = await api.sendBalanceAction(payload);
      setFeedback({ ok: true, text: `Action ${res.action_id} ${res.status}.` });
      refreshLog();
    } catch (err) {
      setFeedback({ ok: false, text: err.message });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="p-8 space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-panel border border-line rounded-xl p-6">
          <h3 className="font-display text-sm font-semibold text-ink mb-4">Manual Load Balancing</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex gap-2">
              {[
                { id: 'shift_load', label: 'Shift Load', icon: ArrowRightLeft },
                { id: 'shed_load', label: 'Shed Load', icon: ScissorsLineDashed },
                { id: 'rebalance_auto', label: 'Auto Rebalance', icon: Wand2 }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  type="button"
                  key={id}
                  onClick={() => setAction(id)}
                  className={`flex-1 flex flex-col items-center gap-1.5 py-3 rounded-lg border text-xs font-medium transition-colors ${
                    action === id ? 'border-normal/40 bg-normal/10 text-normal' : 'border-line text-muted hover:text-ink'
                  }`}
                >
                  <Icon size={16} />
                  {label}
                </button>
              ))}
            </div>

            {action !== 'rebalance_auto' && (
              <div className="grid grid-cols-2 gap-3">
                <label className="text-xs text-muted">
                  Source substation
                  <select
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                    required
                    className="mt-1 w-full bg-raised border border-line text-ink text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-normal"
                  >
                    <option value="">Select…</option>
                    {nodes.map((n) => (
                      <option key={n.id} value={n.id}>
                        {n.name}
                      </option>
                    ))}
                  </select>
                </label>
                {action === 'shift_load' && (
                  <label className="text-xs text-muted">
                    Target substation
                    <select
                      value={target}
                      onChange={(e) => setTarget(e.target.value)}
                      required
                      className="mt-1 w-full bg-raised border border-line text-ink text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-normal"
                    >
                      <option value="">Select…</option>
                      {nodes
                        .filter((n) => n.id !== source)
                        .map((n) => (
                          <option key={n.id} value={n.id}>
                            {n.name}
                          </option>
                        ))}
                    </select>
                  </label>
                )}
              </div>
            )}

            {action !== 'rebalance_auto' && (
              <label className="text-xs text-muted block">
                Amount (kW)
                <input
                  type="number"
                  min="1"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="mt-1 w-full bg-raised border border-line text-ink text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-normal font-mono"
                />
              </label>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-normal text-base font-semibold text-sm py-2.5 rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {submitting ? 'Executing…' : 'Execute action'}
            </button>

            {feedback && (
              <p className={`text-xs ${feedback.ok ? 'text-normal' : 'text-crit'}`}>{feedback.text}</p>
            )}
          </form>
        </div>

        <div className="bg-panel border border-line rounded-xl p-6">
          <h3 className="font-display text-sm font-semibold text-ink mb-4">Substation Power</h3>
          <ul className="space-y-2">
            {nodes.map((n) => (
              <li key={n.id} className="flex items-center justify-between py-2 border-b border-line/60 last:border-0">
                <div>
                  <p className="text-sm text-ink font-medium">{n.name}</p>
                  <p className="text-xs text-muted">{n.region}</p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={n.status} />
                  <button
                    onClick={() => toggleNode(n.id, !n.enabled)}
                    className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors ${
                      n.enabled
                        ? 'border-line text-muted hover:text-crit hover:border-crit/40'
                        : 'border-normal/40 text-normal'
                    }`}
                  >
                    <Power size={13} />
                    {n.enabled ? 'Disable' : 'Enable'}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="bg-panel border border-line rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-line">
          <h3 className="font-display text-sm font-semibold text-ink">Action Log</h3>
        </div>
        {actionLog.length === 0 ? (
          <p className="px-6 py-8 text-sm text-muted text-center">No control actions taken yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted uppercase tracking-wide border-b border-line">
                <th className="px-6 py-3 font-medium">Action</th>
                <th className="px-6 py-3 font-medium">From</th>
                <th className="px-6 py-3 font-medium">To</th>
                <th className="px-6 py-3 font-medium">Amount</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {actionLog.map((a) => (
                <tr key={a.id} className="border-b border-line/60 last:border-0">
                  <td className="px-6 py-3 text-ink capitalize">{a.action.replace('_', ' ')}</td>
                  <td className="px-6 py-3 text-muted">{nodes.find((n) => n.id === a.source_node_id)?.name || '—'}</td>
                  <td className="px-6 py-3 text-muted">{nodes.find((n) => n.id === a.target_node_id)?.name || '—'}</td>
                  <td className="px-6 py-3 text-ink font-mono">{a.amount_kw ? `${a.amount_kw} kW` : '—'}</td>
                  <td className="px-6 py-3">
                    <StatusBadge status={a.status === 'completed' ? 'normal' : 'warning'} />
                  </td>
                  <td className="px-6 py-3 text-muted font-mono text-xs">{new Date(a.created_at).toLocaleTimeString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
