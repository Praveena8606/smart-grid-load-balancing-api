import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Zap } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: '', password: '' });
  const [submitting, setSubmitting] = useState(false);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    clearError();
    setSubmitting(true);
    const ok = await login(form);
    setSubmitting(false);
    if (ok) {
      navigate(location.state?.from || '/dashboard', { replace: true });
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-8">
          <Zap className="text-normal" size={22} strokeWidth={2.5} />
          <span className="font-display text-lg font-semibold text-ink tracking-tight">GridOps</span>
        </div>

        <div className="bg-panel border border-line rounded-xl p-7">
          <h1 className="font-display text-lg font-semibold text-ink mb-1">Sign in</h1>
          <p className="text-sm text-muted mb-6">Monitor and control your grid.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <label className="block text-xs text-muted">
              Email
              <input
                type="email"
                required
                value={form.email}
                onChange={update('email')}
                placeholder="you@utility.com"
                className="mt-1 w-full bg-raised border border-line text-ink text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:ring-1 focus:ring-normal"
              />
            </label>
            <label className="block text-xs text-muted">
              Password
              <input
                type="password"
                required
                value={form.password}
                onChange={update('password')}
                placeholder="Enter your password"
                className="mt-1 w-full bg-raised border border-line text-ink text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:ring-1 focus:ring-normal"
              />
            </label>

            {error && <p className="text-xs text-crit">{error}</p>}

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-normal text-base font-semibold text-sm py-2.5 rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {submitting ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="mt-5 text-xs text-muted text-center">
            No account?{' '}
            <Link to="/register" className="text-normal font-medium hover:underline">
              Create one
            </Link>
          </p>
        </div>

        <p className="mt-4 text-xs text-muted text-center font-mono">
          demo: demo@gridops.io / demo1234
        </p>
      </div>
    </div>
  );
}
