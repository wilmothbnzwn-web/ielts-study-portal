/**
 * IELTS Study Portal — Shared Navbar
 *
 * Renders the consistent site header with navigation links
 * and a reactive user menu (sign in/out). Injects into
 * <div id="navbar-container"></div> on every page.
 *
 * Usage:
 *   import { renderNavbar } from './js/navbar.js';
 *   renderNavbar();
 */

import { authStore } from './auth-store.js';
import { supabase } from './auth-store.js';

// ── Determine which page is active ───────────────────────────────
function activeClass(path) {
  const current = window.location.pathname;
  // Normalize: "/" and "/index.html" are the same
  if (path === '/' && (current === '/' || current === '/index.html')) {
    return 'bg-brand-800 text-white rounded-lg font-medium';
  }
  if (path === '/vocab' && (current === '/vocab' || current === '/vocabulary.html' || current.startsWith('/vocab/deck/'))) {
    return 'bg-brand-800 text-white rounded-lg font-medium';
  }
  if (path !== '/' && current.endsWith(path)) {
    return 'bg-brand-800 text-white rounded-lg font-medium';
  }
  return 'text-brand-500 hover:text-brand-900 rounded-lg transition-colors';
}

// ── Desktop nav links ────────────────────────────────────────────
function desktopLinks() {
  const links = [
    { href: '/', label: '首页' },
    { href: '/reading-library.html', label: '题库大厅' },
    { href: '/mock-test.html', label: '机考模拟' },
    { href: '/writing.html', label: '写作' },
    { href: '/reading.html', label: '阅读' },
    { href: '/vocab', label: '词汇' },
    { href: '/collection.html', label: '我的收集' },
  ];
  return links.map(l =>
    `<a href="${l.href}" class="px-3 py-2 text-sm ${activeClass(l.href)}">${l.label}</a>`
  ).join('');
}

// ── Mobile nav links ─────────────────────────────────────────────
function mobileLinks() {
  const current = window.location.pathname;
  function mc(path, label) {
    const isActive = (path === '/' && (current === '/' || current === '/index.html')) ||
                     (path === '/vocab' && (current === '/vocab' || current === '/vocabulary.html' || current.startsWith('/vocab/deck/'))) ||
                     (path !== '/' && current.endsWith(path));
    return `<a href="${path}" class="text-xs px-2 py-1.5 rounded-md ${isActive ? 'bg-brand-800 text-white' : 'bg-brand-50 text-brand-700'}">${label}</a>`;
  }
  return mc('/', '首页') +
    mc('/reading-library.html', '题库') +
    mc('/mock-test.html', '机考') +
    mc('/reading.html', '阅读') +
    mc('/vocab', '词汇') +
    mc('/collection.html', '收集');
}

// ── User menu (right side) ───────────────────────────────────────
function renderUserMenu(user) {
  if (user) {
    const email = escapeHtml(user.email || 'User');
    return `
      <div class="flex items-center gap-2 sm:gap-3 flex-shrink-0">
        <span class="text-xs sm:text-sm text-brand-500 hidden sm:inline" title="${email}">${email}</span>
        <button id="btn-logout"
          class="text-xs sm:text-sm px-3 py-1.5 border border-brand-200 rounded-lg text-brand-600 hover:bg-brand-50 hover:text-brand-900 transition-colors whitespace-nowrap">
          登出
        </button>
      </div>`;
  }
  return `
    <div class="flex items-center gap-2 flex-shrink-0">
      <a href="./login.html" class="text-xs sm:text-sm px-3 py-1.5 border border-brand-200 rounded-lg text-brand-600 hover:bg-brand-50 hover:text-brand-900 transition-colors whitespace-nowrap">登录</a>
      <a href="./register.html" class="text-xs sm:text-sm px-3 py-1.5 bg-brand-800 text-white rounded-lg hover:bg-brand-900 transition-colors whitespace-nowrap">注册</a>
    </div>`;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

// ── Main render function ─────────────────────────────────────────
export function renderNavbar() {
  let container = document.getElementById('navbar-container');
  if (!container) {
    // Create container if it doesn't exist
    container = document.createElement('div');
    container.id = 'navbar-container';
    document.body.prepend(container);
  }

  // Build the full navbar HTML
  container.innerHTML = `
    <header class="border-b border-brand-100 bg-white/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-2">
        <a href="./" class="flex items-center gap-2 sm:gap-3 no-underline flex-shrink-0">
          <div class="w-8 h-8 sm:w-9 sm:h-9 bg-brand-800 rounded-lg flex items-center justify-center text-white font-bold text-sm">I</div>
          <div class="hidden sm:block">
            <h1 class="text-lg font-bold text-brand-900 leading-tight">IELTS Study Portal</h1>
            <p class="text-xs text-brand-400">Academic Reading & Writing</p>
          </div>
        </a>
        <!-- Desktop nav -->
        <nav class="hidden sm:flex gap-1 text-sm">
          ${desktopLinks()}
        </nav>
        <!-- User menu (desktop) -->
        <div id="user-menu-desktop" class="hidden sm:block"></div>
        <!-- Mobile: nav + user menu -->
        <div class="sm:hidden flex items-center gap-1">
          ${mobileLinks()}
          <div id="user-menu-mobile" class="ml-1"></div>
        </div>
      </div>
    </header>`;

  // Reactive: update user menu when auth state changes
  const menuDesktop = document.getElementById('user-menu-desktop');
  const menuMobile = document.getElementById('user-menu-mobile');

  function updateMenu(state) {
    const html = renderUserMenu(state.user);
    if (menuDesktop) menuDesktop.innerHTML = html;
    if (menuMobile) menuMobile.innerHTML = html;

    // Bind logout handler
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', async () => {
        await supabase.auth.signOut();
        window.location.href = './';
      });
    }
  }

  // Subscribe to auth changes
  authStore.subscribe(updateMenu);
}
