/**
 * IELTS Study Portal — Route Guard
 *
 * Include this module on any page that requires authentication.
 * If the user is not logged in, they are redirected to /login.html
 * with the current URL as a redirect parameter (so they come back
 * after logging in).
 *
 * Usage:
 *   <script type="module" src="/js/auth-guard.js"></script>
 *
 * Pages that use this guard: collection.html, mock-test.html
 */

import { initAuth, authStore } from './auth-store.js';

await initAuth();

if (!authStore.isAuthenticated) {
  const currentPath = window.location.pathname + window.location.search;
  // Don't redirect if we're already on the login page
  if (!currentPath.includes('/login.html') && !currentPath.includes('/register.html')) {
    window.location.href = `/login.html?redirect=${encodeURIComponent(currentPath)}`;
  }
}
