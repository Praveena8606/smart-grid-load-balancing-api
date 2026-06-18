/**
 * Mock backend. Mirrors the shapes described in api.js exactly, so that
 * switching VITE_USE_MOCK=false against a real server requires no
 * changes to any component.
 */

const REGIONS = ['North Grid', 'East Grid', 'South Grid', 'West Grid'];

function makeNode(i) {
  const capacity = [800, 1200, 950, 1500, 700, 1100, 1000, 1300][i];
  return {
    id: `node-${i + 1}`,
    name: `Substation ${String.fromCharCode(65 + i)}`,
    region: REGIONS[i % REGIONS.length],
    capacity_kw: capacity,
    current_load_kw: Math.round(capacity * (0.45 + Math.random() * 0.25)),
    voltage_kv: 11 + Math.random() * 0.4 - 0.2,
    status: 'normal',
    enabled: true
  };
}

let nodes = Array.from({ length: 8 }, (_, i) => makeNode(i));
let alerts = [];
let actionLog = [];
let alertSeq = 1;
let actionSeq = 1;

function statusFor(node) {
  const pct = node.current_load_kw / node.capacity_kw;
  if (!node.enabled) return 'offline';
  if (pct >= 0.92) return 'critical';
  if (pct >= 0.78) return 'warning';
  return 'normal';
}

function maybeRaiseAlert(node) {
  const status = statusFor(node);
  if (status === 'warning' || status === 'critical') {
    const already = alerts.find(
      (a) => a.node_id === node.id && a.status === 'active' && a.severity === status
    );
    if (!already) {
      const alert = {
        id: `alert-${alertSeq++}`,
        node_id: node.id,
        node_name: node.name,
        severity: status === 'critical' ? 'critical' : 'warning',
        message:
          status === 'critical'
            ? `${node.name} load at ${Math.round((node.current_load_kw / node.capacity_kw) * 100)}% of capacity — overload risk`
            : `${node.name} approaching capacity (${Math.round((node.current_load_kw / node.capacity_kw) * 100)}%)`,
        triggered_at: new Date().toISOString(),
        resolved_at: null,
        status: 'active'
      };
      alerts = [alert, ...alerts].slice(0, 50);
      return alert;
    }
  }
  return null;
}

function tickNodes() {
  const newAlerts = [];
  nodes = nodes.map((n) => {
    if (!n.enabled) return { ...n, status: 'offline' };
    const drift = (Math.random() - 0.5) * n.capacity_kw * 0.06;
    let load = n.current_load_kw + drift;
    load = Math.max(n.capacity_kw * 0.2, Math.min(n.capacity_kw * 1.02, load));
    const updated = {
      ...n,
      current_load_kw: Math.round(load),
      voltage_kv: +(11 + Math.random() * 0.4 - 0.2).toFixed(2)
    };
    updated.status = statusFor(updated);
    const alert = maybeRaiseAlert(updated);
    if (alert) newAlerts.push(alert);
    return updated;
  });
  return newAlerts;
}

// ---- Public mock API ----

export function getNodes() {
  return Promise.resolve(nodes.map((n) => ({ ...n })));
}

export function getSummary() {
  const total_capacity_kw = nodes.reduce((s, n) => s + n.capacity_kw, 0);
  const total_load_kw = nodes.reduce((s, n) => s + (n.enabled ? n.current_load_kw : 0), 0);
  return Promise.resolve({
    total_capacity_kw,
    total_load_kw,
    utilization_pct: +((total_load_kw / total_capacity_kw) * 100).toFixed(1),
    active_nodes: nodes.filter((n) => n.enabled).length,
    alerts_count: alerts.filter((a) => a.status === 'active').length,
    last_updated: new Date().toISOString()
  });
}

export function getLoadHistory(nodeId = 'all', range = '24h') {
  const points = range === '7d' ? 168 : range === '1h' ? 60 : 96;
  const stepMs = range === '7d' ? 3600_000 : range === '1h' ? 60_000 : 900_000;
  const now = Date.now();
  const baseCapacity =
    nodeId === 'all'
      ? nodes.reduce((s, n) => s + n.capacity_kw, 0)
      : nodes.find((n) => n.id === nodeId)?.capacity_kw || 1000;

  const series = Array.from({ length: points }, (_, i) => {
    const t = now - (points - i) * stepMs;
    const hour = new Date(t).getHours();
    const dailyCurve = 0.55 + 0.3 * Math.sin(((hour - 7) / 24) * Math.PI * 2 - Math.PI / 2);
    const noise = (Math.random() - 0.5) * 0.06;
    const load_kw = Math.round(baseCapacity * Math.max(0.25, dailyCurve + noise));
    return { timestamp: new Date(t).toISOString(), load_kw };
  });

  return Promise.resolve({ node_id: nodeId, range, series });
}

export function getForecast(nodeId = 'all', horizon = '24h') {
  const points = horizon === '7d' ? 7 * 24 : 24;
  const stepMs = 3600_000;
  const now = Date.now();
  const baseCapacity =
    nodeId === 'all'
      ? nodes.reduce((s, n) => s + n.capacity_kw, 0)
      : nodes.find((n) => n.id === nodeId)?.capacity_kw || 1000;

  const series = Array.from({ length: points }, (_, i) => {
    const t = now - 12 * stepMs + i * stepMs;
    const isPast = t <= now;
    const hour = new Date(t).getHours();
    const dailyCurve = 0.55 + 0.3 * Math.sin(((hour - 7) / 24) * Math.PI * 2 - Math.PI / 2);
    const dayIndex = Math.floor(i / 24);
    const weeklyVariance = 1 + Math.sin(dayIndex * 0.9) * 0.04;
    const predicted = Math.round(baseCapacity * dailyCurve * weeklyVariance);
    const spread = Math.round(predicted * 0.08);
    return {
      timestamp: new Date(t).toISOString(),
      actual_load_kw: isPast ? Math.round(predicted * (0.96 + Math.random() * 0.08)) : null,
      predicted_load_kw: predicted,
      lower_bound_kw: predicted - spread,
      upper_bound_kw: predicted + spread
    };
  });

  return Promise.resolve({
    node_id: nodeId,
    horizon,
    model: 'LSTM-Ensemble-v2',
    generated_at: new Date().toISOString(),
    series,
    accuracy: { mape: +(3.1 + Math.random() * 1.5).toFixed(2), rmse: +(18 + Math.random() * 6).toFixed(1) }
  });
}

export function getAlerts(status = 'active') {
  const filtered = status === 'all' ? alerts : alerts.filter((a) => a.status === status);
  return Promise.resolve(filtered.map((a) => ({ ...a })));
}

export function acknowledgeAlert(id) {
  alerts = alerts.map((a) =>
    a.id === id ? { ...a, status: 'resolved', resolved_at: new Date().toISOString() } : a
  );
  return Promise.resolve({ id, status: 'resolved' });
}

export function sendBalanceAction(payload) {
  const action = {
    id: `action-${actionSeq++}`,
    ...payload,
    status: 'completed',
    created_at: new Date().toISOString()
  };
  actionLog = [action, ...actionLog].slice(0, 50);

  // Reflect the action on node loads so the UI feels responsive
  if (payload.action === 'shift_load' && payload.source_node_id && payload.target_node_id) {
    nodes = nodes.map((n) => {
      if (n.id === payload.source_node_id)
        return { ...n, current_load_kw: Math.max(0, n.current_load_kw - payload.amount_kw) };
      if (n.id === payload.target_node_id)
        return { ...n, current_load_kw: n.current_load_kw + payload.amount_kw };
      return n;
    });
  }
  if (payload.action === 'shed_load' && payload.source_node_id) {
    nodes = nodes.map((n) =>
      n.id === payload.source_node_id
        ? { ...n, current_load_kw: Math.max(0, n.current_load_kw - payload.amount_kw) }
        : n
    );
  }

  return Promise.resolve({ action_id: action.id, status: action.status });
}

export function toggleNode(id, enabled) {
  nodes = nodes.map((n) => (n.id === id ? { ...n, enabled } : n));
  return Promise.resolve({ id, enabled });
}

export function getActionLog() {
  return Promise.resolve(actionLog.map((a) => ({ ...a })));
}

export function subscribeLive(onMessage) {
  const interval = setInterval(() => {
    const newAlerts = tickNodes();
    nodes.forEach((n) => {
      onMessage({
        type: 'node_update',
        node_id: n.id,
        current_load_kw: n.current_load_kw,
        voltage_kv: n.voltage_kv,
        status: n.status,
        timestamp: new Date().toISOString()
      });
    });
    newAlerts.forEach((a) => onMessage({ type: 'alert', ...a }));
  }, 3000);

  return () => clearInterval(interval);
}
