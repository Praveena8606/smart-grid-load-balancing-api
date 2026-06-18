import { useEffect, useState } from 'react';
import { Gauge, Zap, Server, AlertTriangle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../services/api';
import GridPulseStrip from '../components/GridPulseStrip';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';

export default function Overview({ nodes, summary }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    api.getLoadHistory('all', '24h').then((res) => {
      setHistory(
        res.series.map((p) => ({
          time: new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          load: p.load_kw
        }))
      );
    });
  }, []);

  return (
    <div className="p-8 space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          label="Total Load"
          value={summary ? summary.total_load_kw.toLocaleString() : '—'}
          unit="kW"
          icon={Zap}
          accent="normal"
        />
        <StatCard
          label="Utilization"
          value={summary ? summary.utilization_pct : '—'}
          unit="%"
          icon={Gauge}
          accent={summary && summary.utilization_pct > 85 ? 'crit' : 'info'}
        />
        <StatCard
          label="Active Substations"
          value={summary ? summary.active_nodes : '—'}
          unit={`/ ${nodes.length}`}
          icon={Server}
          accent="info"
        />
        <StatCard
          label="Active Alerts"
          value={summary ? summary.alerts_count : '—'}
          icon={AlertTriangle}
          accent={summary && summary.alerts_count > 0 ? 'warn' : 'normal'}
        />
      </div>

      <GridPulseStrip nodes={nodes} />

      <div className="bg-panel border border-line rounded-xl p-6">
        <h3 className="font-display text-sm font-semibold text-ink mb-4">Grid Load — Last 24 Hours</h3>
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={history}>
            <defs>
              <linearGradient id="loadFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2DD4BF" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#2DD4BF" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#233047" strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="time" stroke="#8B97AC" fontSize={11} tickLine={false} axisLine={false} interval={11} />
            <YAxis stroke="#8B97AC" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ background: '#182438', border: '1px solid #233047', borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: '#8B97AC' }}
            />
            <Area type="monotone" dataKey="load" stroke="#2DD4BF" strokeWidth={2} fill="url(#loadFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-panel border border-line rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-line">
          <h3 className="font-display text-sm font-semibold text-ink">Substations</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-muted uppercase tracking-wide border-b border-line">
              <th className="px-6 py-3 font-medium">Name</th>
              <th className="px-6 py-3 font-medium">Region</th>
              <th className="px-6 py-3 font-medium">Load</th>
              <th className="px-6 py-3 font-medium">Capacity</th>
              <th className="px-6 py-3 font-medium">Voltage</th>
              <th className="px-6 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {nodes.map((n) => (
              <tr key={n.id} className="border-b border-line/60 last:border-0">
                <td className="px-6 py-3 text-ink font-medium">{n.name}</td>
                <td className="px-6 py-3 text-muted">{n.region}</td>
                <td className="px-6 py-3 text-ink font-mono tabular-nums">{n.current_load_kw.toLocaleString()} kW</td>
                <td className="px-6 py-3 text-muted font-mono tabular-nums">{n.capacity_kw.toLocaleString()} kW</td>
                <td className="px-6 py-3 text-muted font-mono tabular-nums">{n.voltage_kv?.toFixed(2)} kV</td>
                <td className="px-6 py-3">
                  <StatusBadge status={n.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
