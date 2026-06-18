const STYLES = {
  normal: 'bg-normal/15 text-normal border-normal/30',
  warning: 'bg-warn/15 text-warn border-warn/30',
  critical: 'bg-crit/15 text-crit border-crit/30',
  offline: 'bg-muted/15 text-muted border-muted/30',
  info: 'bg-info/15 text-info border-info/30',
  resolved: 'bg-muted/15 text-muted border-muted/30',
  active: 'bg-warn/15 text-warn border-warn/30'
};

export default function StatusBadge({ status }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border capitalize ${
        STYLES[status] || STYLES.normal
      }`}
    >
      {status}
    </span>
  );
}
