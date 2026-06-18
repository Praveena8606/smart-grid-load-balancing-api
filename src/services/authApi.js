/**
 * ============================================================================
 * AUTH API CLIENT
 * ============================================================================
 * Same pattern as services/api.js: this is the only file that knows how to
 * talk to auth endpoints. Swap VITE_USE_MOCK to "false" once your backend
 * implements the contract below — no component changes needed.
 *
 * --------------------------------------------------------------------------
 * EXPECTED API CONTRACT
 * --------------------------------------------------------------------------
 * POST /api/v1/auth/register
 *    body: { name, email, password }
 *    -> { user: { id, name, email }, token }
 *    errors: 409 if email already registered
 *
 * POST /api/v1/auth/login
 *    body: { email, password }
 *    -> { user: { id, name, email }, token }
 *    errors: 401 on bad credentials
 *
 * POST /api/v1/auth/logout
 *    header: Authorization: Bearer <token>
 *    -> { success: true }
 *
 * GET  /api/v1/auth/me
 *    header: Authorization: Bearer <token>
 *    -> { user: { id, name, email } }
 *    errors: 401 if token invalid/expired
 *
 * Real implementation notes for whoever builds the backend:
 *  - Hash passwords (bcrypt/argon2) — never store plaintext.
 *  - Prefer short-lived JWTs + refresh tokens, or server-side sessions with
 *    an httpOnly cookie. The mock below uses a plain token in localStorage
 *    purely for demo purposes; don't carry that pattern into production.
 * ============================================================================
 */

import * as mockAuth from './mockAuth';

const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? 'true') === 'true';
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const token = localStorage.getItem('gridops_token');
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    ...options
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const authApi = {
  register: (payload) =>
    USE_MOCK
      ? mockAuth.register(payload)
      : request('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(payload) }),

  login: (payload) =>
    USE_MOCK
      ? mockAuth.login(payload)
      : request('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(payload) }),

  logout: () => (USE_MOCK ? mockAuth.logout() : request('/api/v1/auth/logout', { method: 'POST' })),

  me: () => (USE_MOCK ? mockAuth.me() : request('/api/v1/auth/me'))
};
