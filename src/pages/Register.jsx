import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Zap } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const { register, error, clearError } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' });
  const [localError, setLocalError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    clearError();
    setLocalError(null);

    if (form.password.length < 8) {
      setLocalError('Password must be at least 8 characters.');
      return;
    }
    if (form.password !== form.confirm) {
      setLocalError('Passwords do not match.');
      return;
    }

    setSubmitting(true);
    const ok = await register({ name: form.name, email: form.email, password: form.password });
    setSubmitting(false);
    if (ok) navigate('/dashboard', { replace: true });
  }

  const shownError = localError || error;

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-8">
          <Zap className="text-normal" size={22} strokeWidth={2.5} />
          <span className="font-display text-lg font-semibold text-ink tracking-tight">GridOps</span>
        </div>

        <div className="bg-panel border border-line rounded-xl p-7">
          <h1 className="font-display text-lg font-semibold text-ink mb-1">Create account</h1>
          <p className="text-sm text-muted mb-6">Set up access to your grid dashboard.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <label className="block text-xs text-muted">
              Full name
              <input
                type="text"
                required
                value={form.name}
                onChange={update('name')}
                placeholder="Jane Operator"
                className="mt-1 w-full bg-raised border border-line text-ink text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:ring-1 focus:ring-normal"
              />
            </label>
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
            <div className="grid grid-cols-2 gap-3">
              <label className="block text-xs text-muted">
                Password
                <input
                  type="password"
                  required
                  value={form.password}
                  onChange={update('password')}
                  placeholder="At least 8 chars"
                  className="mt-1 w-full bg-raised border border-line text-ink text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:ring-1 focus:ring-normal"
                />
              </label>
              <label className="block text-xs text-muted">
                Confirm
                <input
                  type="password"
                  required
                  value={form.confirm}
                  onChange={update('confirm')}
                  placeholder="Repeat password"
                  className="mt-1 w-full bg-raised border border-line text-ink text-sm rounded-lg px-3 py-2.5 focus:outline-none focus:ring-1 focus:ring-normal"
                />
              </label>
            </div>

            {shownError && <p className="text-xs text-crit">{shownError}</p>}

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-normal text-base font-semibold text-sm py-2.5 rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {submitting ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="mt-5 text-xs text-muted text-center">
            Already have an account?{' '}
            <Link to="/login" className="text-normal font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
