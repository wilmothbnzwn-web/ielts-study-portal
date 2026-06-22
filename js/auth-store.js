/**
 * IELTS Study Portal — Auth Store
 *
 * Creates the Supabase client singleton and provides a lightweight
 * pub/sub auth state store for vanilla JS. All modules that import
 * this file share the same supabase instance and authStore object.
 *
 * Usage:
 *   import { supabase, authStore, initAuth } from './auth-store.js';
 *   await initAuth();                    // recover session on page load
 *   authStore.subscribe(({ user }) => {  // react to auth changes
 *     console.log(user?.email);
 *   });
 */

import { SUPABASE_URL, SUPABASE_ANON_KEY } from './env.js';

// ── Supabase client singleton ───────────────────────────────────
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Need to reference createClient from the Supabase SDK (loaded via import map)
// The import map resolves '@supabase/supabase-js' to the CDN bundle.
// We re-import it here so auth-store.js is self-contained.
import { createClient } from '@supabase/supabase-js';

// ── Reactive auth store (pub/sub) ───────────────────────────────
let _user = null;
let _session = null;
const _listeners = new Set();

function notify() {
  const state = { user: _user, session: _session };
  _listeners.forEach(fn => {
    try { fn(state); } catch (e) { console.error('authStore listener error:', e); }
  });
}

export const authStore = {
  get user() { return _user; },
  get session() { return _session; },
  get isAuthenticated() { return !!_user; },

  /**
   * Subscribe to auth state changes. Returns an unsubscribe function.
   * The callback is called immediately with the current state.
   */
  subscribe(fn) {
    _listeners.add(fn);
    fn({ user: _user, session: _session }); // immediate first call
    return () => _listeners.delete(fn);
  },

  /** @internal — set by initAuth and sign-in/out handlers */
  _setState(user, session) {
    _user = user;
    _session = session;
    notify();
  },

  /** @internal — clear state on sign-out */
  _clear() {
    _user = null;
    _session = null;
    notify();
  },
};

// ── Session recovery & listener ──────────────────────────────────

/**
 * Call once per page load. Recovers the Supabase session from the
 * stored refresh token, then listens for future auth state changes.
 */
export async function initAuth() {
  // Recover existing session
  const { data } = await supabase.auth.getSession();
  if (data.session) {
    authStore._setState(data.session.user, data.session);
  }

  // Listen for future auth changes
  supabase.auth.onAuthStateChange((event, session) => {
    if (event === 'SIGNED_IN' && session) {
      authStore._setState(session.user, session);
    } else if (event === 'SIGNED_OUT') {
      authStore._clear();
    } else if (event === 'TOKEN_REFRESHED' && session) {
      authStore._setState(session.user, session);
    }
  });
}
