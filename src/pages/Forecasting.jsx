import { useEffect, useState } from 'react';
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Target, Activity } from 'lucide-react';
import { api } from '../services/api';
import StatCard from '../components/StatCard';

export default function Forecasting({ nodes }) {
  const [nodeId, setNodeId] = useState('all');
  const [horizon, setHorizon] = useState('24h');
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getForecast(nodeId, horizon).then((res) => {
      setForecast(res);
      setLoading(false);
    });
  }, [nodeId, horizon]);

  const chartData =
    forecast?.series.map((p) => ({
      time: new Date(p.timestamp).toLocaleString([], {
        month: horizon === '7d' ? 'short' : undefined,
        day: horizon === '7d' ? 'numeric' : undefined,
        hour: '2-digit',
        minute: horizon === '7d' ? undefined : '2-digit'
      }),
      actual: p.actual_load_kw,
      predicted: p.predicted_load_kw,
      band: [p.lower_bound_kw, p.upper_bound_kw]
    })) || [];

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center gap-3">
        <select
          value={nodeId}
          onChange={(e) => setNodeId(e.target.value)}
          className="bg-panel border border-line text-ink text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-normal"
        >
          <option value="all">Whole Grid</option>
          {nodes.map((n) => (
            <option key={n.id} value={n.id}>
              {n.name}
            </option>
          ))}
        </select>
        <div className="flex bg-panel border border-line rounded-lg p-1">
          {['24h', '7d'].map((h) => (
            <button
              key={h}
              onClick={() => setHorizon(h)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                horizon === h ? 'bg-normal/15 text-normal' : 'text-muted hover:text-ink'
              }`}
            >
              {h === '24h' ? 'Next 24h' : 'Next 7 days'}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <StatCard
          label="Model"
          value={forecast?.model || '—'}
          icon={Activity}
          accent="info"
          hint="Active forecasting model"
        />
        <StatCard label="MAPE" value={forecast?.accuracy.mape ?? '—'} unit="%" icon={Target} accent="normal" hint="Mean absolute % error" />
        <StatCard label="RMSE" value={forecast?.accuracy.rmse ?? '—'} unit="kW" icon={Target} accent="normal" hint="Root mean squared error" />
      </div>

      <div className="bg-panel border border-line rounded-xl p-6">
        <h3 className="font-display text-sm font-semibold text-ink mb-1">
          Forecasted Load — {horizon === '24h' ? 'Next 24 Hours' : 'Next 7 Days'}
        </h3>
        <p className="text-xs text-muted mb-4">Shaded band shows the model's confidence interval.</p>
        {loading ? (
          <div className="h-64 flex items-center justify-center text-muted text-sm">Loading forecast…</div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={chartData}>
              <CartesianGrid stroke="#233047" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="time" stroke="#8B97AC" fontSize={11} tickLine={false} axisLine={false} interval={horizon === '7d' ? 23 : 2} />
              <YAxis stroke="#8B97AC" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: '#182438', border: '1px solid #233047', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#8B97AC' }}
              />
              <Legend wrapperStyle={{ fontSize: 12, color: '#8B97AC' }} />
              <Area dataKey="band" stroke="none" fill="#38BDF8" fillOpacity={0.12} name="Confidence band" />
              <Line type="monotone" dataKey="actual" stroke="#2DD4BF" strokeWidth={2} dot={false} name="Actual" connectNulls />
              <Line
                type="monotone"
                dataKey="predicted"
                stroke="#38BDF8"
                strokeWidth={2}
                strokeDasharray="4 3"
                dot={false}
                name="Predicted"
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
