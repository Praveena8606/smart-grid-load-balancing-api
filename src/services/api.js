/**
 * ============================================================================
 * SMART GRID API CLIENT
 * ============================================================================
 * This file is the ONLY place that knows how to talk to the backend.
 * Every page/component calls functions from here — never fetch() directly
 * in a component. That means swapping mock data for your real API later
 * is a one-line change (see USE_MOCK below).
 *
 * --------------------------------------------------------------------------
 * EXPECTED API CONTRACT (build your backend to match this)
 * --------------------------------------------------------------------------
 * Base URL: import.meta.env.VITE_API_BASE_URL  (e.g. http://localhost:8000)
 *
 * GET  /api/v1/grid/nodes
 *    -> [{ id, name, region, capacity_kw, current_load_kw,
 *          status: "normal"|"warning"|"critical"|"offline",
 *          voltage_kv, enabled }]
 *
 * GET  /api/v1/grid/summary
 *    -> { total_capacity_kw, total_load_kw, utilization_pct,
 *          active_nodes, alerts_count, last_updated }
 *
 * GET  /api/v1/grid/load-history?node_id=all&range=1h|24h|7d
 *    -> { node_id, range, series: [{ timestamp, load_kw }] }
 *
 * GET  /api/v1/forecast?node_id=&horizon=24h|7d
 *    -> { node_id, horizon, model, generated_at,
 *          series: [{ timestamp, actual_load_kw|null, predicted_load_kw,
 *                      lower_bound_kw, upper_bound_kw }],
 *          accuracy: { mape, rmse } }
 *
 * GET  /api/v1/alerts?status=active|resolved&severity=info|warning|critical
 *    -> [{ id, node_id, node_name, severity, message,
 *          triggered_at, resolved_at, status }]
 *
 * POST /api/v1/alerts/:id/acknowledge
 *    -> { id, status: "resolved" }
 *
 * POST /api/v1/grid/balance
 *    body: { action: "shift_load"|"shed_load"|"rebalance_auto",
 *             source_node_id, target_node_id, amount_kw }
 *    -> { action_id, status: "queued"|"executing"|"completed"|"failed" }
 *
 * POST /api/v1/grid/nodes/:id/toggle
 *    body: { enabled: true|false }
 *    -> { id, enabled }
 *
 * GET  /api/v1/grid/actions
 *    -> [{ id, action, source_node_id, target_node_id, amount_kw,
 *          status, created_at }]
 *
 * WS   /ws/live
 *    server -> client messages:
 *      { type: "node_update", node_id, current_load_kw, voltage_kv, status, timestamp }
 *      { type: "alert", id, node_id, node_name, severity, message, triggered_at, status }
 * ============================================================================
 */

import * as mock from './mockData';

const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? 'true') === 'true';
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

export const api = {
  getNodes: () => (USE_MOCK ? mock.getNodes() : request('/api/v1/grid/nodes')),

  getSummary: () => (USE_MOCK ? mock.getSummary() : request('/api/v1/grid/summary')),

  getLoadHistory: (nodeId = 'all', range = '24h') =>
    USE_MOCK
      ? mock.getLoadHistory(nodeId, range)
      : request(`/api/v1/grid/load-history?node_id=${nodeId}&range=${range}`),

  getForecast: (nodeId = 'all', horizon = '24h') =>
    USE_MOCK
      ? mock.getForecast(nodeId, horizon)
      : request(`/api/v1/forecast?node_id=${nodeId}&horizon=${horizon}`),

  getAlerts: (status = 'active') =>
    USE_MOCK ? mock.getAlerts(status) : request(`/api/v1/alerts?status=${status}`),

  acknowledgeAlert: (id) =>
    USE_MOCK
      ? mock.acknowledgeAlert(id)
      : request(`/api/v1/alerts/${id}/acknowledge`, { method: 'POST' }),

  sendBalanceAction: (payload) =>
    USE_MOCK
      ? mock.sendBalanceAction(payload)
      : request('/api/v1/grid/balance', { method: 'POST', body: JSON.stringify(payload) }),

  toggleNode: (id, enabled) =>
    USE_MOCK
      ? mock.toggleNode(id, enabled)
      : request(`/api/v1/grid/nodes/${id}/toggle`, {
          method: 'POST',
          body: JSON.stringify({ enabled })
        }),

  getActionLog: () => (USE_MOCK ? mock.getActionLog() : request('/api/v1/grid/actions')),

  /**
   * Subscribes to live node + alert updates.
   * In mock mode this is a setInterval ticker; in real mode it's a WebSocket.
   * Returns an unsubscribe function.
   */
  subscribeLive: (onMessage) => {
    if (USE_MOCK) return mock.subscribeLive(onMessage);

    const wsUrl = BASE_URL.replace(/^http/, 'ws') + '/ws/live';
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (evt) => {
      try {
        onMessage(JSON.parse(evt.data));
      } catch (e) {
        console.error('Bad WS message', e);
      }
    };
    return () => ws.close();
  }
};
