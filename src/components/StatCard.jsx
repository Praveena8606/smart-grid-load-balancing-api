export default function StatCard({ label, value, unit, accent = 'normal', icon: Icon, hint }) {
  const colorMap = {
    normal: 'text-normal',
    info: 'text-info',
    warn: 'text-warn',
    crit: 'text-crit'
  };
  return (
    <div className="bg-panel border border-line rounded-xl p-5 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted uppercase tracking-wide">{label}</span>
        {Icon && <Icon size={16} className={colorMap[accent]} />}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl font-display font-semibold text-ink tabular-nums">{value}</span>
        {unit && <span className="text-sm text-muted">{unit}</span>}
      </div>
      {hint && <span className="text-xs text-muted">{hint}</span>}
    </div>
  );
}
