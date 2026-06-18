import { useEffect, useRef, useState, useCallback } from 'react';
import { api } from '../services/api';

/**
 * Single source of truth for live node state, summary, and alerts.
 * Mount once at the App level and pass down, so every page reflects
 * the same live data without duplicate subscriptions.
 */
export function useLiveGrid() {
  const [nodes, setNodes] = useState([]);
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);
  const nodesRef = useRef([]);

  const refreshSummary = useCallback(() => {
    api.getSummary().then(setSummary);
  }, []);

  useEffect(() => {
    api.getNodes().then((n) => {
      nodes_set(n);
    });
    api.getAlerts('active').then(setAlerts);
    refreshSummary();

    function nodes_set(n) {
      nodesRef.current = n;
      setNodes(n);
    }

    const unsubscribe = api.subscribeLive((msg) => {
      setConnected(true);
      if (msg.type === 'node_update') {
        nodesRef.current = nodesRef.current.map((n) =>
          n.id === msg.node_id
            ? { ...n, current_load_kw: msg.current_load_kw, voltage_kv: msg.voltage_kv, status: msg.status }
            : n
        );
        setNodes([...nodesRef.current]);
      }
      if (msg.type === 'alert') {
        setAlerts((prev) => [msg, ...prev].slice(0, 50));
      }
    });

    const summaryInterval = setInterval(refreshSummary, 3000);

    return () => {
      unsubscribe();
      clearInterval(summaryInterval);
    };
  }, [refreshSummary]);

  const toggleNode = useCallback((id, enabled) => {
    return api.toggleNode(id, enabled).then(() => api.getNodes()).then((n) => {
      nodesRef.current = n;
      setNodes(n);
    });
  }, []);

  const acknowledgeAlert = useCallback((id) => {
    return api.acknowledgeAlert(id).then(() => {
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    });
  }, []);

  return { nodes, summary, alerts, connected, toggleNode, acknowledgeAlert, refreshSummary };
}
