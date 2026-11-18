# SahAI-Coop Frontend

> AI-powered cooperative assistant for rural Maharashtra farmers — multilingual, voice-enabled, source-cited.

---

## Overview

**SahAI-Coop** is a final-year project that brings together a FastAPI AI backend and a pure-HTML/CSS/JS frontend to help farmers and cooperative members navigate complex government schemes, crop insurance, PACS services, land documents, and cooperative rules — in English, Hindi, and Marathi.

This `frontend/` directory contains the complete client-side application. It requires **no build step, no npm, no webpack** — just a web server and a running backend.

---

## Project Structure

```
frontend/
├── index.html          # Home / Landing page (hero, topic cards, how-it-works)
├── auth.html           # Login & Registration page (tab-switched form)
├── chat.html           # Full chatbot interface (session list + message thread)
├── README.md           # This file
├── css/
│   └── styles.css      # Complete design system — variables, components, layouts
└── js/
    ├── api.js          # Backend API client, session management, toast notifications
    └── app.js          # Shared utilities — theme, modals, badges, date formatting
```

### File Responsibilities

| File | Responsibility |
|------|----------------|
| `index.html` | Marketing/landing page; topic showcase; links to auth & chat |
| `auth.html` | Login and registration (tab UI); on success redirects to `chat.html` |
| `chat.html` | Core product page; session sidebar; message thread; voice input |
| `styles.css` | Single source of truth for all CSS; glassmorphism dark-green theme |
| `api.js` | All `fetch` calls to FastAPI; `window.API` global; localStorage helpers; toasts |
| `app.js` | Theme init; nav active state; shared modals; `window.APP` global |

---

## Prerequisites

| Requirement | Details |
|------------|---------|
| **FastAPI backend** | Running on `http://localhost:8000` (see [Backend Setup](#backend-setup-quick-reference)) |
| **Modern browser** | Chrome 90+ recommended (required for Voice Input via Web Speech API) |
| **Build tools** | ❌ None — pure HTML/CSS/JS, no npm or compilation needed |

---

## Running the Frontend

### Option 1: VS Code Live Server *(Recommended)*

1. Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension in VS Code.
2. Open the `frontend/` folder in VS Code.
3. Right-click `index.html` → **Open with Live Server**.
4. Browser opens at `http://127.0.0.1:5500/index.html`.

> [!TIP]
> Live Server automatically hot-reloads when you save any file — ideal for development.

### Option 2: Python HTTP Server

```bash
# From the project root
cd frontend
python -m http.server 3000
# Visit http://localhost:3000
```

Works with Python 3.x. No dependencies required.

### Option 3: Node.js `serve`

```bash
# From the project root (no install needed)
npx serve frontend -p 3000
# Visit http://localhost:3000
```

---

## Backend Setup (Quick Reference)

The frontend communicates exclusively with the FastAPI backend at `http://localhost:8000`.

```bash
# From the project root
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API docs are available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

> [!IMPORTANT]
> The backend must be running **before** you open the frontend, or all API calls will fail with a network error.

---

## Features

| Feature | Status | Notes |
|---------|--------|-------|
| Authentication (Login / Register) | ✅ | JWT Bearer tokens, stored in localStorage |
| Multilingual chat | ✅ | English, Hindi (हिंदी), Marathi (मराठी) |
| Voice input | ✅ | Web Speech API — Chrome/Edge only |
| Topic-categorized responses | ✅ | 6 categories with colored badges |
| Source citations | ✅ | Inline links to official documents |
| Responsive / mobile-friendly | ✅ | Flexbox + Grid, breakpoints at 768px & 480px |
| Session history & management | ✅ | Sidebar list; persistent across page loads |
| Glassmorphism dark-green theme | ✅ | CSS custom properties; light mode switchable |
| Sample questions | ✅ | Per-topic starter prompts |
| Disclaimer & sources modals | ✅ | Declarative `data-modal` attribute trigger |

---

## API Integration

All requests go to `http://localhost:8000/api`. The `api.js` module handles authentication headers, timeouts (10 s), and error parsing automatically.

### Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/auth/register` | Create new account |
| `POST` | `/api/auth/login` | Obtain JWT token |
| `GET`  | `/api/auth/me` | Fetch current user profile |
| `POST` | `/api/chat/sessions` | Create a new chat session |
| `GET`  | `/api/chat/sessions/{user_id}` | List user's sessions |
| `POST` | `/api/chat/message` | Send message, receive AI reply |
| `GET`  | `/api/chat/history/{session_id}` | Load full session history |
| `GET`  | `/api/topics` | List topic categories |
| `GET`  | `/api/sample-questions` | Fetch starter prompts |

### `window.API` Global

`api.js` exposes a `window.API` object used by all pages:

```javascript
window.API = {
  // Auth
  registerUser, loginUser, getCurrentUser,
  // Sessions
  createSession, getUserSessions,
  // Chat
  sendMessage, getHistory,
  // Discovery
  getTopics, getSampleQuestions,
  // Session storage
  saveSession, getToken, getUser, clearSession, isLoggedIn,
  // Toast notifications
  showToast,
};
```

### `window.APP` Global

`app.js` exposes shared UI utilities:

```javascript
window.APP = {
  showModal, closeModal,
  showDisclaimerModal, showSourcesModal, showHelpModal,
  formatDate, formatRelativeTime,
  createSpinner, createTopicBadge, createSourceLink,
  LANGUAGE_LABELS, LANGUAGE_FLAGS, getLanguageLabel,
  initTheme,
};
```

---

## Browser Support

| Browser | Voice Input | Everything Else |
|---------|-------------|-----------------|
| Chrome 90+ | ✅ Full | ✅ Full |
| Edge 90+ | ✅ Full | ✅ Full |
| Firefox 100+ | ❌ Not supported | ✅ Full |
| Safari 15+ | ⚠️ Partial | ✅ Full |
| Mobile Chrome (Android) | ✅ Full | ✅ Full |
| Mobile Safari (iOS) | ⚠️ Partial | ✅ Full |

> [!NOTE]
> Voice input uses the [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition), which requires microphone permission. The mic button is hidden automatically in unsupported browsers.

---

## Design System

All styles live in `css/styles.css` and are driven by CSS custom properties.

### Color Palette

```css
/* Core greens */
--color-primary:        #1B4D3E  /* Deep forest green */
--color-primary-light:  #2E7D32
--color-primary-dark:   #0D2B22

/* Accent & feedback */
--color-accent:         #4CAF50  /* Vibrant green */
--color-accent-light:   #81C784
--color-gold:           #F9A825  /* Wheat/gold for highlights */

/* Surfaces (dark by default) */
--color-surface:        #0F1F17
--color-surface-2:      #162B1E
--color-surface-3:      #1E3828

/* Typography */
--color-text:           #E8F5E9
--color-text-muted:     #A5D6A7
--color-text-dim:       #66BB6A
```

### Key Component Classes

| Class | Description |
|-------|-------------|
| `.glass-card` | Glassmorphism panel — `backdrop-filter: blur(20px)` + border |
| `.neuro-btn` | Neumorphic button with dark shadow lift |
| `.btn-primary` | Green gradient pill button with hover glow |
| `.btn-secondary` | Outlined button |
| `.btn-ghost` | Transparent icon/text button |
| `.form-input` | Glassmorphic input with green focus ring |
| `.nav-header` | Sticky top navigation bar |
| `.nav-link.active` | Active nav link with green underline indicator |
| `.topic-badge` | Inline colored category label |
| `.spinner--sm/md/lg` | CSS animated loading spinner |
| `.modal-overlay` | Full-screen modal backdrop |
| `.modal-panel` | Centered modal content card |
| `.text-gradient` | Green-to-teal text gradient via `background-clip` |

---

## Troubleshooting

### ❌ All API calls fail / "Network Error"

**Cause:** FastAPI backend is not running.  
**Fix:** Start the backend with `uvicorn main:app --reload --port 8000`.

---

### ❌ CORS error in browser console

**Cause:** Backend does not allow requests from your frontend origin.  
**Fix:** Ensure `main.py` includes:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Add your Live Server / HTTP server origin to `allow_origins`.

---

### ❌ Voice input button not visible or not working

**Cause:** Browser does not support the Web Speech API, or microphone permission was denied.  
**Fix:**
1. Use **Google Chrome** or **Microsoft Edge**.
2. When prompted, click **Allow** to grant microphone access.
3. If denied, reset permissions: `chrome://settings/content/microphone`.

---

### ❌ Page shows "Session expired" immediately

**Cause:** JWT token in localStorage has expired or is malformed.  
**Fix:** Open DevTools → Application → Local Storage → delete `sahai_token` and `sahai_user`, then log in again.

---

### ❌ Styles look broken / unstyled

**Cause:** `styles.css` path is incorrect, or the file server is not serving the `css/` directory.  
**Fix:** Confirm the `<link>` tag in each HTML file points to `css/styles.css`, and that you are serving from inside the `frontend/` directory (not its parent).

---

## Contributing

This is a Final Year Project. If you have suggestions or find bugs:

1. Open an issue on the project GitHub repository.
2. For cooperative/agriculture content corrections, cite the relevant official document.

---

## License

Academic / Educational Use Only. All third-party content (government scheme descriptions, regulatory text) belongs to the respective issuing bodies.
