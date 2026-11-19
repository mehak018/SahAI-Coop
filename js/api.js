/**
 * api.js — SahAI-Coop API Integration Layer
 *
 * Comprehensive API client for the SahAI-Coop FastAPI backend.
 * Backend base URL: http://localhost:8000
 * All routes are prefixed with /api
 *
 * Sections:
 *   1. Configuration & Constants
 *   2. Core request() wrapper
 *   3. Auth API functions
 *   4. Chat API functions
 *   5. Topics & Sample Questions API functions
 *   6. LocalStorage session helpers
 *   7. Toast notification system
 *   8. Exports (named + window.API)
 */

// =============================================================================
// 1. CONFIGURATION & CONSTANTS
// =============================================================================

/** Default backend URLs */
const DEFAULT_LOCAL_BACKEND = 'http://localhost:8000';
const DEFAULT_CLOUD_BACKEND = 'https://sahai-backend.onrender.com';

/** Resolves backend URL based on environment or explicit setting */
function resolveBackendUrl() {
  if (typeof window === 'undefined') return DEFAULT_LOCAL_BACKEND;
  if (window.SAHAI_BACKEND_URL) return window.SAHAI_BACKEND_URL;
  const custom = localStorage.getItem('sahai_backend_url');
  if (custom && custom.trim()) return custom.trim();
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return DEFAULT_LOCAL_BACKEND;
  }
  return DEFAULT_CLOUD_BACKEND;
}

/** Base URL of the FastAPI backend */
const BASE_URL = resolveBackendUrl();

/** API path prefix */
const API_PREFIX = '/api';

/** LocalStorage key for the JWT token */
const TOKEN_KEY = 'sahai_token';

/** LocalStorage key for the cached user object */
const USER_KEY = 'sahai_user';

/** Default request timeout in milliseconds */
const REQUEST_TIMEOUT_MS = 10_000;

/** Longer timeout for AI/RAG chat message generation */
const CHAT_TIMEOUT_MS = 35_000;

// =============================================================================
// 2. CORE REQUEST WRAPPER
// =============================================================================

/**
 * Core HTTP request wrapper.
 *
 * Automatically:
 *  - Sets Content-Type: application/json
 *  - Injects Authorization: Bearer <token> from localStorage when a token exists
 *  - Enforces a 10-second timeout via AbortController
 *  - Parses FastAPI HTTPException `{detail: "..."}` error format into descriptive Error objects
 *
 * @param {string} endpoint  - Path relative to /api (e.g. '/auth/login')
 * @param {RequestInit} [options={}] - Standard fetch options (method, body, headers, …)
 * @returns {Promise<any>} Parsed JSON response body
 * @throws {Error} With a human-readable message derived from the response or network failure
 */
async function request(endpoint, options = {}) {
  const timeoutMs = options.timeoutMs || REQUEST_TIMEOUT_MS;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const url = `${BASE_URL}${API_PREFIX}${endpoint}`;

  // Build headers
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  // Inject bearer token when available
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const { timeoutMs: _ignored, ...fetchOptions } = options;

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Try to parse the response body as JSON regardless of status,
    // so we can read FastAPI's {detail: "..."} error format.
    let data;
    const contentType = response.headers.get('Content-Type') || '';
    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      // FastAPI HTTPException format: { detail: "message" }
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

      if (data && typeof data === 'object') {
        if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          // Pydantic validation errors return an array of {loc, msg, type}
          errorMessage = data.detail.map((e) => e.msg || JSON.stringify(e)).join('; ');
        } else if (data.message) {
          errorMessage = data.message;
        }
      } else if (typeof data === 'string' && data.length) {
        errorMessage = data;
      }

      const err = new Error(errorMessage);
      err.status = response.status;
      err.responseData = data;
      throw err;
    }

    return data;
  } catch (err) {
    clearTimeout(timeoutId);

    if (err.name === 'AbortError') {
      throw new Error(
        `Request timed out after ${timeoutMs / 1000}s. ` +
          'Please check that the backend server (port 8000) is running and try again.'
      );
    }

    // Re-throw errors that already have our custom format
    if (err.status !== undefined) {
      throw err;
    }

    // Network / other errors
    throw new Error(
      `Network error: Unable to reach the server at ${BASE_URL}. ` +
        `Details: ${err.message}`
    );
  }
}

// =============================================================================
// 3. AUTH API FUNCTIONS
// =============================================================================

/**
 * Register a new user account.
 *
 * POST /api/auth/register
 *
 * @param {string} name               - Full name
 * @param {string} email              - Email address
 * @param {string} password           - Password (min 8 chars recommended)
 * @param {string} [language='en']    - Preferred language code ('en' | 'hi' | 'mr')
 * @returns {Promise<{access_token: string, token_type: string, user: object}>}
 */
async function registerUser(name, email, password, language = 'en') {
  const data = await request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      name,
      email,
      password,
      preferred_language: language,
    }),
  });
  return data;
}

/**
 * Log in with email and password.
 *
 * POST /api/auth/login
 *
 * @param {string} email    - Registered email address
 * @param {string} password - Account password
 * @returns {Promise<{access_token: string, token_type: string, user: object}>}
 */
async function loginUser(email, password) {
  const data = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  return data;
}

/**
 * Get the currently authenticated user's profile.
 *
 * GET /api/auth/me  (requires Bearer token)
 *
 * @returns {Promise<{id: string, name: string, email: string, preferred_language: string, created_at: string}>}
 */
async function getCurrentUser() {
  return request('/auth/me', { method: 'GET' });
}

// =============================================================================
// 4. CHAT API FUNCTIONS
// =============================================================================

/**
 * Create a new chat session for a user.
 *
 * POST /api/chat/sessions
 *
 * @param {string} userId - UUID of the authenticated user
 * @param {string} title  - Human-readable session title
 * @returns {Promise<{id: string, user_id: string, title: string, created_at: string, message_count: number}>}
 */
async function createSession(userId, title) {
  return request('/chat/sessions', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, title }),
  });
}

/**
 * Retrieve all chat sessions belonging to a user.
 *
 * GET /api/chat/sessions/{user_id}
 *
 * @param {string} userId - UUID of the user
 * @returns {Promise<Array<{id: string, user_id: string, title: string, created_at: string, message_count: number}>>}
 */
async function getUserSessions(userId) {
  return request(`/chat/sessions/${encodeURIComponent(userId)}`, {
    method: 'GET',
  });
}

/**
 * Send a message in a chat session and receive the bot's reply.
 *
 * POST /api/chat/message
 *
 * @param {string} sessionId - UUID of the chat session
 * @param {string} content   - The user's message text
 * @param {string} [language='en'] - Language code for the reply ('en' | 'hi' | 'mr')
 * @returns {Promise<{user_message: MessageResponse, bot_message: MessageResponse}>}
 *   MessageResponse: {id, session_id, sender, content, language, topic_category, source_reference, timestamp}
 */
async function sendMessage(sessionId, content, language = 'en') {
  return request('/chat/message', {
    method: 'POST',
    timeoutMs: CHAT_TIMEOUT_MS,
    body: JSON.stringify({ session_id: sessionId, content, language }),
  });
}

/**
 * Fetch the full message history for a session.
 *
 * GET /api/chat/history/{session_id}
 *
 * @param {string} sessionId - UUID of the chat session
 * @returns {Promise<{session_id: string, title: string, messages: MessageResponse[]}>}
 */
async function getHistory(sessionId) {
  return request(`/chat/history/${encodeURIComponent(sessionId)}`, {
    method: 'GET',
  });
}

// =============================================================================
// 5. TOPICS & SAMPLE QUESTIONS
// =============================================================================

/**
 * Get all available topic categories.
 *
 * GET /api/topics
 *
 * @returns {Promise<Array<{id: string, name: string, description: string, icon: string}>>}
 */
async function getTopics() {
  return request('/topics', { method: 'GET' });
}

/**
 * Get sample questions, optionally filtered by topic and language.
 *
 * GET /api/sample-questions?topic_category=&language=en
 *
 * @param {string} [topicCategory=''] - Filter by topic category slug (empty = all)
 * @param {string} [language='en']    - Language code for the questions
 * @returns {Promise<Array<{id: string, question_text: string, topic_category: string, language: string}>>}
 */
async function getSampleQuestions(topicCategory = '', language = 'en') {
  const params = new URLSearchParams();
  if (topicCategory) params.set('topic_category', topicCategory);
  params.set('language', language);
  return request(`/sample-questions?${params.toString()}`, { method: 'GET' });
}

// =============================================================================
// 6. LOCALSTORAGE SESSION HELPERS
// =============================================================================

/**
 * Persist a successful auth response (token + user) to localStorage.
 *
 * @param {{ access_token: string, token_type: string, user: object }} tokenResponse
 */
function saveSession(tokenResponse) {
  if (!tokenResponse || !tokenResponse.access_token) {
    console.error('[API] saveSession: invalid tokenResponse', tokenResponse);
    return;
  }
  localStorage.setItem(TOKEN_KEY, tokenResponse.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(tokenResponse.user || {}));
}

/**
 * Read the stored JWT access token.
 *
 * @returns {string|null} The token string, or null if not logged in
 */
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Read the cached user object from localStorage.
 *
 * @returns {object|null} Parsed user object, or null
 */
function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

/**
 * Remove all session data from localStorage (logout).
 */
function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Check whether the user currently has an active session.
 *
 * @returns {boolean}
 */
function isLoggedIn() {
  return Boolean(getToken());
}

// =============================================================================
// 7. TOAST NOTIFICATION SYSTEM
// =============================================================================

/**
 * @typedef {'success'|'error'|'info'|'warning'} ToastType
 */

/**
 * Configuration map for toast appearance per type.
 * @type {Record<ToastType, {icon: string, borderColor: string}>}
 */
const TOAST_CONFIG = {
  success: { icon: '✅', borderColor: '#4CAF50' },
  error:   { icon: '❌', borderColor: '#F44336' },
  info:    { icon: 'ℹ️',  borderColor: '#2196F3' },
  warning: { icon: '⚠️', borderColor: '#F9A825' },
};

/**
 * Ensure the shared toast container element exists in the DOM.
 * Creates it once and caches it.
 *
 * @returns {HTMLElement}
 */
function _getToastContainer() {
  let container = document.getElementById('sahai-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'sahai-toast-container';
    container.className = 'toast-container';
    // Inline fallback styles so toasts work even without styles.css loaded
    Object.assign(container.style, {
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      zIndex: '9999',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
      pointerEvents: 'none',
    });
    document.body.appendChild(container);
  }
  return container;
}

/**
 * Display a transient toast notification.
 *
 * @param {string}    message        - Text to display
 * @param {ToastType} [type='info']  - Visual style variant
 * @param {number}    [duration=3000] - Auto-dismiss delay in ms (0 = no auto-dismiss)
 * @returns {HTMLElement} The toast element (useful for manual removal)
 */
function showToast(message, type = 'info', duration = 3000) {
  const config = TOAST_CONFIG[type] || TOAST_CONFIG.info;
  const container = _getToastContainer();

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  // Inline fallback styles
  Object.assign(toast.style, {
    pointerEvents: 'auto',
    minWidth: '280px',
    maxWidth: '420px',
    padding: '14px 18px',
    borderRadius: '12px',
    background: 'rgba(27, 77, 62, 0.92)',
    backdropFilter: 'blur(20px)',
    border: `1px solid rgba(76, 175, 80, 0.3)`,
    borderLeft: `4px solid ${config.borderColor}`,
    boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
    color: '#E8F5E9',
    fontFamily: "'Inter', sans-serif",
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    animation: 'slideInRight 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards',
    cursor: 'pointer',
  });

  toast.innerHTML = `
    <span class="toast-icon" style="font-size:18px;flex-shrink:0">${config.icon}</span>
    <span class="toast-message" style="flex:1;line-height:1.4">${escapeHtml(message)}</span>
    <button class="toast-close" style="background:none;border:none;color:inherit;font-size:18px;cursor:pointer;padding:0;line-height:1;opacity:0.7" aria-label="Close">×</button>
  `;

  // Click to dismiss
  toast.addEventListener('click', () => removeToast(toast));

  container.appendChild(toast);

  // Auto-dismiss
  let timerId;
  if (duration > 0) {
    timerId = setTimeout(() => removeToast(toast), duration);
  }

  // Store timer so we can clear on manual dismiss
  toast._timerId = timerId;

  return toast;
}

/**
 * Animate and remove a toast element.
 *
 * @param {HTMLElement} toast
 */
function removeToast(toast) {
  if (!toast || !toast.parentNode) return;
  clearTimeout(toast._timerId);

  Object.assign(toast.style, {
    animation: 'slideOutRight 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards',
    opacity: '0',
    transform: 'translateX(110%)',
    transition: 'opacity 0.3s, transform 0.3s',
  });

  setTimeout(() => {
    if (toast.parentNode) toast.parentNode.removeChild(toast);
  }, 320);
}

// =============================================================================
// INTERNAL UTILITY
// =============================================================================

/**
 * Escape HTML special characters to prevent XSS in toast messages.
 *
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// =============================================================================
// 8. EXPORTS
// =============================================================================

// --- Global window.API attachment (for classic <script src="js/api.js"> tags) ---
const API = {
  BASE_URL,
  request,
  // Auth
  registerUser,
  loginUser,
  getCurrentUser,
  // Chat
  createSession,
  getUserSessions,
  sendMessage,
  getHistory,
  // Topics
  getTopics,
  getSampleQuestions,
  // Session helpers
  saveSession,
  getToken,
  getUser,
  clearSession,
  isLoggedIn,
  // Toast
  showToast,
  removeToast,
};

// Attach to window in browser environments
if (typeof window !== 'undefined') {
  window.API = API;
}

// Optional CommonJS export (for Node/test environments)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = API;
}
