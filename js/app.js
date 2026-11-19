/**
 * SahAI-Coop Frontend — Shared Application Logic
 * Loaded on all pages. Assumes window.API is available from api.js
 *
 * Sections:
 *  1. Theme & Appearance
 *  2. Navigation Active State
 *  3. Language Utilities
 *  4. Shared UI Components
 *  5. Keyboard Shortcuts
 *  6. Modals (generic + specific)
 *  7. Init & window.APP export
 */

// ============================================================
// 1. THEME & APPEARANCE
// ============================================================

/**
 * initTheme()
 * Reads localStorage key `sahai_theme`. Defaults to 'dark'.
 * Applies `data-theme` attribute and matching CSS class to <body>.
 */
function initTheme() {
  const saved = localStorage.getItem('sahai_theme') || 'dark';
  document.body.setAttribute('data-theme', saved);
  document.body.classList.remove('theme-dark', 'theme-light');
  document.body.classList.add(saved === 'light' ? 'theme-light' : 'theme-dark');

  // Wire theme toggle buttons if present
  document.querySelectorAll('[data-action="toggle-theme"]').forEach(btn => {
    btn.addEventListener('click', () => {
      const current = localStorage.getItem('sahai_theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem('sahai_theme', next);
      initTheme();
    });
  });
}

// ============================================================
// 2. NAVIGATION ACTIVE STATE
// ============================================================

/**
 * setActiveNavLink()
 * Reads the current page filename from window.location.pathname,
 * then adds the 'active' class to any matching `.nav-link` element.
 */
function setActiveNavLink() {
  const path = window.location.pathname;
  const filename = path.substring(path.lastIndexOf('/') + 1) || 'index.html';

  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    const href = link.getAttribute('href') || '';
    const linkFile = href.substring(href.lastIndexOf('/') + 1);
    if (
      linkFile === filename ||
      (filename === '' && (linkFile === 'index.html' || linkFile === ''))
    ) {
      link.classList.add('active');
    }
  });
}

// ============================================================
// 3. LANGUAGE UTILITIES
// ============================================================

/** Supported language labels */
const LANGUAGE_LABELS = {
  en: 'English',
  hi: 'हिंदी',
  mr: 'मराठी',
};

/** Corresponding flag emoji */
const LANGUAGE_FLAGS = {
  en: '🇬🇧',
  hi: '🇮🇳',
  mr: '🇮🇳',
};

/**
 * getLanguageLabel(code)
 * Returns the display label for a language code.
 * @param {string} code - 'en' | 'hi' | 'mr'
 * @returns {string}
 */
function getLanguageLabel(code) {
  return LANGUAGE_LABELS[code] || code;
}

/**
 * formatDate(isoString)
 * Returns a localized, friendly date/time string.
 * @param {string} isoString - ISO 8601 date string
 * @returns {string}
 */
function formatDate(isoString) {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}

/**
 * formatRelativeTime(isoString)
 * Returns a human-readable relative time string.
 * @param {string} isoString - ISO 8601 date string
 * @returns {string} e.g. "just now", "5 minutes ago", "2 hours ago"
 */
function formatRelativeTime(isoString) {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHr = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr / 24);

    if (diffSec < 10) return 'just now';
    if (diffSec < 60) return `${diffSec} seconds ago`;
    if (diffMin < 2) return '1 minute ago';
    if (diffMin < 60) return `${diffMin} minutes ago`;
    if (diffHr < 2) return '1 hour ago';
    if (diffHr < 24) return `${diffHr} hours ago`;
    if (diffDay < 2) return 'yesterday';
    if (diffDay < 7) return `${diffDay} days ago`;
    return formatDate(isoString);
  } catch {
    return isoString;
  }
}

// ============================================================
// 4. SHARED UI COMPONENTS
// ============================================================

/**
 * createSpinner(size)
 * Returns a spinner DOM element styled via CSS class.
 * @param {'sm'|'md'|'lg'} [size='md']
 * @returns {HTMLElement}
 */
function createSpinner(size = 'md') {
  const wrapper = document.createElement('span');
  wrapper.className = `spinner spinner--${size}`;
  wrapper.setAttribute('aria-label', 'Loading…');
  wrapper.setAttribute('role', 'status');

  const inner = document.createElement('span');
  inner.className = 'spinner__ring';
  wrapper.appendChild(inner);
  return wrapper;
}

/** Topic color mapping (Tailwind-inspired CSS variable names) */
const TOPIC_COLORS = {
  crop_insurance:      { bg: 'var(--badge-green-bg)',   text: 'var(--badge-green-text)',   border: 'var(--badge-green-border)'  },
  documents:           { bg: 'var(--badge-blue-bg)',    text: 'var(--badge-blue-text)',    border: 'var(--badge-blue-border)'   },
  pacs:                { bg: 'var(--badge-teal-bg)',    text: 'var(--badge-teal-text)',    border: 'var(--badge-teal-border)'   },
  grievance:           { bg: 'var(--badge-amber-bg)',   text: 'var(--badge-amber-text)',   border: 'var(--badge-amber-border)'  },
  cooperative_rules:   { bg: 'var(--badge-forest-bg)',  text: 'var(--badge-forest-text)',  border: 'var(--badge-forest-border)' },
  government_schemes:  { bg: 'var(--badge-gold-bg)',    text: 'var(--badge-gold-text)',    border: 'var(--badge-gold-border)'   },
};

/** Topic display names */
const TOPIC_NAMES = {
  crop_insurance:     'Crop Insurance',
  documents:          'Documents',
  pacs:               'PACS Services',
  grievance:          'Grievance',
  cooperative_rules:  'Cooperative Rules',
  government_schemes: 'Government Schemes',
};

/**
 * createTopicBadge(topicCategory)
 * Returns a colored <span> badge for the given topic category.
 * @param {string} topicCategory
 * @returns {HTMLSpanElement}
 */
function createTopicBadge(topicCategory) {
  const badge = document.createElement('span');
  badge.className = 'topic-badge';

  const color = TOPIC_COLORS[topicCategory];
  if (color) {
    badge.style.backgroundColor = color.bg;
    badge.style.color            = color.text;
    badge.style.border           = `1px solid ${color.border}`;
  } else {
    badge.style.backgroundColor = 'var(--color-surface-3)';
    badge.style.color            = 'var(--color-text-muted)';
    badge.style.border           = '1px solid var(--color-border)';
  }

  badge.textContent = TOPIC_NAMES[topicCategory] || topicCategory;
  return badge;
}

/**
 * createSourceLink(sourceRef)
 * Parses sourceRef (plain URL string or JSON "{title, url}") and returns
 * a styled anchor element.
 * @param {string} sourceRef
 * @returns {HTMLAnchorElement}
 */
function createSourceLink(sourceRef) {
  const anchor = document.createElement('a');
  anchor.className = 'source-link';
  anchor.target = '_blank';
  anchor.rel = 'noopener noreferrer';

  if (!sourceRef) {
    anchor.textContent = 'Source';
    anchor.href = '#';
    return anchor;
  }

  // Try to parse as JSON {title, url}
  if (sourceRef.trim().startsWith('{')) {
    try {
      const parsed = JSON.parse(sourceRef);
      anchor.href = parsed.url || '#';
      anchor.textContent = parsed.title || parsed.url || 'Source';
      return anchor;
    } catch {
      // fall through to plain URL handling
    }
  }

  // Plain URL or plain text
  if (sourceRef.startsWith('http://') || sourceRef.startsWith('https://')) {
    anchor.href = sourceRef;
    try {
      anchor.textContent = new URL(sourceRef).hostname;
    } catch {
      anchor.textContent = sourceRef;
    }
  } else {
    anchor.href = '#';
    anchor.textContent = sourceRef;
  }

  return anchor;
}

// ============================================================
// 5. KEYBOARD SHORTCUTS
// ============================================================

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeModal();
  }
});

// ============================================================
// 6. MODALS
// ============================================================

/** Internal reference to the currently active modal overlay */
let _activeModal = null;

/**
 * showModal(title, content, actions)
 * Creates and mounts a glassmorphic modal overlay.
 * @param {string}      title   - Modal heading text
 * @param {string|Node} content - HTML string or DOM node for the body
 * @param {Array<{label:string, onClick:Function, primary?:boolean}>} [actions] - Footer buttons
 */
function showModal(title, content, actions = []) {
  // Remove any existing modal
  closeModal();

  // Overlay
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', title);

  // Close on backdrop click
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal();
  });

  // Panel
  const panel = document.createElement('div');
  panel.className = 'modal-panel glass-card';

  // Header
  const header = document.createElement('div');
  header.className = 'modal-header';

  const titleEl = document.createElement('h2');
  titleEl.className = 'modal-title';
  titleEl.textContent = title;

  const closeBtn = document.createElement('button');
  closeBtn.className = 'modal-close btn-ghost';
  closeBtn.setAttribute('aria-label', 'Close modal');
  closeBtn.innerHTML = '&times;';
  closeBtn.addEventListener('click', closeModal);

  header.appendChild(titleEl);
  header.appendChild(closeBtn);

  // Body
  const body = document.createElement('div');
  body.className = 'modal-body';
  if (typeof content === 'string') {
    body.innerHTML = content;
  } else if (content instanceof Node) {
    body.appendChild(content);
  }

  // Footer
  if (actions.length > 0) {
    const footer = document.createElement('div');
    footer.className = 'modal-footer';
    actions.forEach(({ label, onClick, primary }) => {
      const btn = document.createElement('button');
      btn.className = primary ? 'btn-primary' : 'btn-secondary';
      btn.textContent = label;
      btn.addEventListener('click', () => {
        if (typeof onClick === 'function') onClick();
      });
      footer.appendChild(btn);
    });
    panel.appendChild(header);
    panel.appendChild(body);
    panel.appendChild(footer);
  } else {
    panel.appendChild(header);
    panel.appendChild(body);
  }

  overlay.appendChild(panel);
  document.body.appendChild(overlay);

  // Animate in
  requestAnimationFrame(() => overlay.classList.add('modal-overlay--visible'));

  _activeModal = overlay;
  return overlay;
}

/**
 * closeModal()
 * Removes the currently active modal from the DOM with a fade-out animation.
 */
function closeModal() {
  if (!_activeModal) return;
  const modal = _activeModal;
  _activeModal = null;
  modal.classList.remove('modal-overlay--visible');
  modal.classList.add('modal-overlay--hiding');
  modal.addEventListener('transitionend', () => modal.remove(), { once: true });
  // Fallback in case transition doesn't fire
  setTimeout(() => { if (modal.parentNode) modal.remove(); }, 400);
}

// ============================================================
// 6a. DISCLAIMER MODAL
// ============================================================

/**
 * showDisclaimerModal()
 * Displays the legal disclaimer for SahAI-Coop.
 */
function showDisclaimerModal() {
  const content = `
    <div class="disclaimer-content">
      <div class="disclaimer-icon" aria-hidden="true">⚖️</div>
      <p class="disclaimer-lead">
        <strong>SahAI-Coop</strong> provides general guidance based on official government
        documents and publicly available agricultural cooperative regulations.
      </p>
      <div class="disclaimer-warning glass-card">
        <strong>⚠️ This is NOT legal advice.</strong><br>
        The information provided is for educational and informational purposes only.
        It does not constitute legal, financial, or professional advice of any kind.
      </div>
      <ul class="disclaimer-list">
        <li>Always verify information with the relevant government authority.</li>
        <li>For official matters, consult a registered legal counsel or government office.</li>
        <li>Cooperative rules may vary by state — check local Maharashtra law where applicable.</li>
        <li>Agricultural insurance claims must be filed via official PMFBY channels.</li>
      </ul>
      <p class="disclaimer-contact">
        For official support, visit your nearest
        <strong>Primary Agricultural Credit Society (PACS)</strong> or the
        <a href="https://pgportal.gov.in" target="_blank" rel="noopener noreferrer">
          Centralized Public Grievance Redress and Monitoring System
        </a>.
      </p>
    </div>
  `;

  showModal('Legal Disclaimer', content, [
    { label: 'I Understand', onClick: closeModal, primary: true },
  ]);
}

// ============================================================
// 6b. SOURCES MODAL
// ============================================================

/** Official reference sources used by SahAI-Coop */
const OFFICIAL_SOURCES = [
  {
    title:  'PMFBY — Pradhan Mantri Fasal Bima Yojana Guidelines',
    body:   'Ministry of Agriculture & Farmers Welfare, Government of India',
    url:    'https://pmfby.gov.in',
    icon:   '🌾',
  },
  {
    title:  'Maharashtra Cooperative Societies Act, 1960',
    body:   'Maharashtra Legislature & Cooperation Department',
    url:    'https://mahacoop.maharashtra.gov.in',
    icon:   '📜',
  },
  {
    title:  'NABARD Cooperative Finance Guidelines',
    body:   'National Bank for Agriculture and Rural Development',
    url:    'https://nabard.org',
    icon:   '🏦',
  },
  {
    title:  'PM-Kisan — PM Kisan Samman Nidhi',
    body:   'Ministry of Agriculture & Farmers Welfare, Government of India',
    url:    'https://pmkisan.gov.in',
    icon:   '👨‍🌾',
  },
  {
    title:  'RBI Circular on PACS Digitalisation',
    body:   'Reserve Bank of India',
    url:    'https://rbi.org.in',
    icon:   '🏛️',
  },
  {
    title:  'Centralized Public Grievance Redress Portal',
    body:   'Department of Administrative Reforms & Public Grievances, GoI',
    url:    'https://pgportal.gov.in',
    icon:   '📋',
  },
];

/**
 * showSourcesModal()
 * Shows a modal listing all official reference sources.
 */
function showSourcesModal() {
  const list = document.createElement('ul');
  list.className = 'sources-list';

  OFFICIAL_SOURCES.forEach(src => {
    const item = document.createElement('li');
    item.className = 'source-item glass-card';
    item.innerHTML = `
      <span class="source-item__icon" aria-hidden="true">${src.icon}</span>
      <div class="source-item__info">
        <a class="source-item__title" href="${src.url}" target="_blank" rel="noopener noreferrer">
          ${src.title}
        </a>
        <span class="source-item__body">${src.body}</span>
      </div>
      <a class="source-item__link btn-ghost" href="${src.url}" target="_blank" rel="noopener noreferrer"
         aria-label="Open ${src.title}">
        ↗
      </a>
    `;
    list.appendChild(item);
  });

  const wrapper = document.createElement('div');
  wrapper.className = 'sources-modal-content';
  const intro = document.createElement('p');
  intro.className = 'sources-intro';
  intro.textContent =
    'SahAI-Coop\'s knowledge base is built from the following official government and regulatory publications:';
  wrapper.appendChild(intro);
  wrapper.appendChild(list);

  showModal('Official Sources & References', wrapper, [
    { label: 'Close', onClick: closeModal, primary: false },
  ]);
}

// ============================================================
// 6c. HELP MODAL
// ============================================================

/**
 * showHelpModal()
 * Shows a comprehensive help guide for using SahAI-Coop.
 */
function showHelpModal() {
  const content = `
    <div class="help-content">

      <section class="help-section">
        <h3 class="help-section__title">🤖 How to Use the Chatbot</h3>
        <ol class="help-list">
          <li>Register or log in using the <strong>Auth</strong> page.</li>
          <li>Select a <strong>topic category</strong> from the sidebar or the home page, or type freely.</li>
          <li>Type your question in the message box and press <strong>Enter</strong> or click <strong>Send</strong>.</li>
          <li>Use the <strong>🎙 Voice</strong> button to dictate your question (Chrome recommended).</li>
          <li>Click any <strong>source link</strong> in a bot reply to view the official document.</li>
        </ol>
      </section>

      <section class="help-section">
        <h3 class="help-section__title">🌐 Supported Languages</h3>
        <ul class="help-list help-list--langs">
          <li>🇬🇧 <strong>English</strong> — Full support</li>
          <li>🇮🇳 <strong>हिंदी (Hindi)</strong> — Full support</li>
          <li>🇮🇳 <strong>मराठी (Marathi)</strong> — Full support</li>
        </ul>
        <p>Change your preferred language from the chat toolbar or your profile settings.</p>
      </section>

      <section class="help-section">
        <h3 class="help-section__title">📚 Topics Covered</h3>
        <ul class="help-list help-topics">
          <li>🌾 <strong>Crop Insurance</strong> — PMFBY claims, enrollment, and deadlines</li>
          <li>📄 <strong>Documents</strong> — 7/12 extracts, land records, and registration</li>
          <li>🏦 <strong>PACS Services</strong> — Loans, accounts, and cooperative membership</li>
          <li>📋 <strong>Grievances</strong> — Filing complaints and tracking status</li>
          <li>📜 <strong>Cooperative Rules</strong> — Maharashtra Cooperative Societies Act</li>
          <li>🏛️ <strong>Government Schemes</strong> — PM-Kisan, subsidies, and welfare programs</li>
        </ul>
      </section>

      <section class="help-section">
        <h3 class="help-section__title">⌨️ Keyboard Shortcuts</h3>
        <dl class="help-shortcuts">
          <dt><kbd>Enter</kbd></dt><dd>Send message</dd>
          <dt><kbd>Shift + Enter</kbd></dt><dd>New line in message</dd>
          <dt><kbd>Esc</kbd></dt><dd>Close modal / cancel action</dd>
        </dl>
      </section>

      <section class="help-section">
        <h3 class="help-section__title">📬 Contact & Feedback</h3>
        <p>
          This project is under active development as a Final Year Project.
          Feedback and bug reports are welcome via
          <a href="https://github.com/sahai-coop" target="_blank" rel="noopener noreferrer">
            GitHub Issues
          </a>.
        </p>
        <p>
          For official cooperative/agricultural matters, please contact your local
          <strong>PACS office</strong> or the
          <a href="https://pgportal.gov.in" target="_blank" rel="noopener noreferrer">
            Public Grievance Portal
          </a>.
        </p>
      </section>

    </div>
  `;

  showModal('Help & Guide', content, [
    { label: 'Got it!', onClick: closeModal, primary: true },
  ]);
}

// ============================================================
// 7. INIT & EXPORT
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  // Apply theme and nav state on every page
  initTheme();
  setActiveNavLink();

  // Wire up declarative modal triggers: [data-modal="disclaimer|sources|help"]
  document.querySelectorAll('[data-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.dataset.modal;
      if (type === 'disclaimer') showDisclaimerModal();
      else if (type === 'sources')    showSourcesModal();
      else if (type === 'help')       showHelpModal();
    });
  });
});

/**
 * window.APP
 * Public surface for all pages and inline scripts.
 */
window.APP = {
  // Modals
  showModal,
  closeModal,
  showDisclaimerModal,
  showSourcesModal,
  showHelpModal,

  // Date / locale
  formatDate,
  formatRelativeTime,

  // UI components
  createSpinner,
  createTopicBadge,
  createSourceLink,

  // Language constants
  LANGUAGE_LABELS,
  LANGUAGE_FLAGS,
  getLanguageLabel,

  // Theme
  initTheme,
};
