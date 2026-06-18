const DOT_COLOR = {
  normal: '#2DD4BF',
  warning: '#F59E0B',
  critical: '#F8717A',
  offline: '#475569'
};

export default function GridPulseStrip({ nodes }) {
  return (
    <div className="bg-panel border border-line rounded-xl p-6 overflow-x-auto">
      <div className="flex items-center justify-between mb-5">
        <h3 className="font-display text-sm font-semibold text-ink">Grid Topology</h3>
        <span className="text-xs text-muted font-mono">{nodes.length} substations</span>
      </div>
      <div className="relative flex items-center min-w-[640px]">
        <div className="absolute left-0 right-0 h-px bg-line top-1/2 -translate-y-1/2" />
        {nodes.map((node, i) => {
          const pct = Math.min(100, Math.round((node.current_load_kw / node.capacity_kw) * 100));
          const color = DOT_COLOR[node.status] || DOT_COLOR.normal;
          return (
            <div key={node.id} className="relative flex-1 flex flex-col items-center gap-2 z-10">
              <span className="text-[10px] font-mono text-muted">{pct}%</span>
              <div
                className={`relative w-4 h-4 rounded-full border-2 ${
                  node.status === 'critical' || node.status === 'warning' ? 'pulse' : ''
                }`}
                style={{
                  backgroundColor: node.enabled ? color : 'transparent',
                  borderColor: color,
                  boxShadow: node.enabled ? `0 0 12px 2px ${color}66` : 'none'
                }}
              />
              <span className="text-xs font-medium text-ink whitespace-nowrap">{node.name}</span>
              <span className="text-[10px] text-muted whitespace-nowrap">{node.region}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
