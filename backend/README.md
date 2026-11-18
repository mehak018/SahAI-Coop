# SahAI-Coop Backend (SIH26088)
## Multilingual Cooperative Governance & Legal Assistance Chatbot

FastAPI-powered backend handling Citizen/Farmer Authentication, Session Management, Chat History, Topic Discovery, Pre-indexed Knowledge Retrieval, and AI/RAG engine hooks for English, Hindi, and Marathi.

---

## 1. Architecture Overview

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Auth & DB session dependencies
│   │   └── routes/
│   │       ├── auth.py          # User registration, login, profile
│   │       ├── chat.py          # Sessions, message exchange, history
│   │       └── topics.py        # Topic cards & suggested questions
│   ├── core/
│   │   ├── config.py            # Pydantic v2 settings & environment variables
│   │   └── security.py          # Bcrypt hashing & JWT lifecycle
│   ├── database/
│   │   ├── base.py              # DeclarativeBase model registry
│   │   └── session.py           # MySQL connection pooling & SessionLocal
│   ├── middleware/
│   │   ├── cors.py              # Cross-Origin configuration for React
│   │   └── error_handler.py     # Centralized HTTP & validation exception handlers
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── user.py              # Users table
│   │   ├── chat_session.py      # Chat sessions table
│   │   ├── message.py           # Messages table
│   │   └── sample_response.py   # Sample responses / Knowledge base table
│   ├── repositories/            # Data access layer
│   │   ├── user_repository.py
│   │   ├── chat_repository.py
│   │   └── knowledge_repository.py
│   ├── schemas/                 # Pydantic validation schemas
│   │   ├── user.py
│   │   ├── chat.py
│   │   ├── topic.py
│   │   └── common.py
│   └── services/                # Business logic
│       ├── auth_service.py
│       ├── chat_service.py
│       ├── topic_service.py
│       └── rag_hook.py          # External RAG module integration hook
├── tests/                       # Pytest automated test suite (14 test cases)
├── .env.example                 # Example environment variables
├── requirements.txt             # Production & dev dependencies
├── run.py                       # Server runner
└── README.md                    # Setup & documentation guide
```

---

## 2. Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **MySQL Server 8.0+** running locally or remotely (default port 3306)

---

## 3. Environment Setup & Installation

### Step 1: Create and Activate a Virtual Environment
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Activate on Linux/macOS
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure `DATABASE_URL` matches your local MySQL username and password:
```env
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/sahai_coop_db
SECRET_KEY=sahai_coop_super_secret_jwt_key_sih26088_production_change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://127.0.0.1:3000","http://127.0.0.1:5173"]
```

---

## 4. Database Setup & Seeding

Run the automated database initializer from the root directory:
```bash
# Creates sahai_coop_db, applies table schema, and loads multilingual seed data
python database/init_db.py
```

To drop and re-seed from scratch:
```bash
python database/init_db.py --drop --seed
```

---

## 5. Starting the Backend Server

### Using `run.py`:
```bash
cd backend
python run.py
```

### Using `uvicorn` directly:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server endpoints:
- **API Base:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/api/health`

---

## 6. Running Automated Tests

Run the full pytest suite (uses SQLite in-memory for zero side-effects):
```bash
python -m pytest backend/tests -v
```

---

## 7. API Reference Summary

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new user with hashed password (bcrypt) & language |
| `POST` | `/api/auth/login` | Authenticate user & return JWT Bearer token |
| `GET` | `/api/auth/me` | Retrieve profile of authenticated user |

### Chat & Messaging (`/api/chat`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat/sessions` | Create a new conversational session |
| `GET` | `/api/chat/sessions/{user_id}` | Fetch all previous sessions for a user |
| `POST` | `/api/chat/message` | Send question, query RAG hook / sample DB, save bot response & sources |
| `GET` | `/api/chat/history/{session_id}` | Retrieve chronological message history for a session |

### Topics & Discovery (`/api`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/topics` | Get available topic categories (PMFBY, PACS, Grievances, etc.) for UI cards |
| `GET` | `/api/sample-questions` | Fetch popular suggested quick questions (`?language=en|hi|mr`) |

---

## 8. AI/RAG Engine Integration (For AI Teammate)
The chat pipeline includes a designated hook in `app/services/rag_hook.py`.
1. Set `AI_RAG_ENABLED=True` and `AI_RAG_SERVICE_URL=http://localhost:8001/api/rag/query` in `.env`.
2. When enabled, incoming queries are sent to your microservice first.
3. If the AI service is offline or returns empty, the backend automatically falls back to verified responses in the MySQL knowledge base.
