/**
 * Mock auth backend. Persists to localStorage so registered accounts and
 * sessions survive a page refresh — purely for demo purposes. A real backend
 * would hash passwords and issue real tokens; this does neither, on purpose,
 * to keep it obviously "not for production" while still letting the full
 * register -> login -> protected route flow work end to end.
 */

const USERS_KEY = 'gridops_users';
const TOKEN_KEY = 'gridops_token';

function loadUsers() {
  try {
    const raw = localStorage.getItem(USERS_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    /* fall through to seed */
  }
  const seeded = [{ id: 'user-1', name: 'Demo Operator', email: 'demo@gridops.io', password: 'demo1234' }];
  localStorage.setItem(USERS_KEY, JSON.stringify(seeded));
  return seeded;
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function publicUser(u) {
  return { id: u.id, name: u.name, email: u.email };
}

function delay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function register({ name, email, password }) {
  await delay();
  const users = loadUsers();
  if (users.some((u) => u.email.toLowerCase() === email.toLowerCase())) {
    throw new Error('An account with that email already exists.');
  }
  const user = { id: `user-${users.length + 1}`, name, email, password };
  users.push(user);
  saveUsers(users);
  const token = btoa(`${email}:${Date.now()}`);
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(`session_${token}`, user.id);
  return { user: publicUser(user), token };
}

export async function login({ email, password }) {
  await delay();
  const users = loadUsers();
  const user = users.find((u) => u.email.toLowerCase() === email.toLowerCase());
  if (!user || user.password !== password) {
    throw new Error('Incorrect email or password.');
  }
  const token = btoa(`${email}:${Date.now()}`);
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(`session_${token}`, user.id);
  return { user: publicUser(user), token };
}

export async function logout() {
  await delay(100);
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) localStorage.removeItem(`session_${token}`);
  localStorage.removeItem(TOKEN_KEY);
  return { success: true };
}

export async function me() {
  await delay(150);
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) throw new Error('Not authenticated.');
  const userId = localStorage.getItem(`session_${token}`);
  const users = loadUsers();
  const user = users.find((u) => u.id === userId);
  if (!user) throw new Error('Session expired.');
  return { user: publicUser(user) };
}
