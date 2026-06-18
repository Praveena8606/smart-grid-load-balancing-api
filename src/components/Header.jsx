import { useEffect, useState } from 'react';

export default function Header({ title, subtitle, connected }) {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="h-16 border-b border-line flex items-center justify-between px-8 sticky top-0 bg-base/95 backdrop-blur z-10">
      <div>
        <h1 className="font-display text-lg font-semibold text-ink leading-none">{title}</h1>
        {subtitle && <p className="text-xs text-muted mt-1">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-2 text-xs font-mono text-muted">
          <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-normal pulse' : 'bg-muted'}`} />
          {connected ? 'LIVE' : 'CONNECTING'}
        </div>
        <time className="text-sm font-mono text-muted tabular-nums">
          {now.toLocaleTimeString([], { hour12: false })}
        </time>
      </div>
    </header>
  );
}
