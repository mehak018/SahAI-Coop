# SahAI-Coop Database Architecture & Setup

This directory contains the database schemas, seed datasets, migration scripts, and initialization utilities for the **SahAI-Coop** project (SIH Problem Statement 26088: Multilingual Cooperative Governance & Legal Assistance Chatbot).

---

## 1. Relational Entity-Relationship (ER) Architecture

The database is built on **MySQL 8.0+** using the `utf8mb4` character set to natively store multi-byte Unicode scripts including **Marathi (Devanagari)**, **Hindi (Devanagari)**, and **English**.

The architecture adheres to minimal, non-redundant, fully linked relational design:

```
[ users ] (1)
    │
    │ 1:N (ON DELETE CASCADE)
    ▼
[ chat_sessions ] (1)
    │
    │ 1:N (ON DELETE CASCADE)
    ▼
[ messages ] (N)
    ▲
    │ (References topic & sources)
[ sample_responses / knowledge_base ]
```

### Table Specifications

#### 1. `users` Table
Stores user profile, credentials, and language preference.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Unique identifier for user |
| `name` | VARCHAR(255) | NOT NULL | User's full name |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | Login email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `preferred_language` | VARCHAR(10) | NOT NULL, DEFAULT 'en' | 'en' (English), 'hi' (Hindi), 'mr' (Marathi) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

#### 2. `chat_sessions` Table
Groups conversation history for clean session continuity.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Unique session identifier |
| `user_id` | INT | FK -> `users.id`, ON DELETE CASCADE | Associated user |
| `title` | VARCHAR(255) | NOT NULL, DEFAULT 'New Conversation' | Auto-generated or custom conversation title |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Session initiation timestamp |

#### 3. `messages` Table
Maintains persistent bidirectional conversational history.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Message identifier |
| `session_id` | INT | FK -> `chat_sessions.id`, ON DELETE CASCADE | Parent session |
| `sender` | VARCHAR(20) | NOT NULL | 'user' or 'bot' |
| `content` | TEXT | NOT NULL | Message text (supports multilingual strings) |
| `language` | VARCHAR(10) | NOT NULL, DEFAULT 'en' | Language code of the query/response |
| `topic_category` | VARCHAR(100) | NULL | Matched topic (e.g. 'Crop Insurance (PMFBY)', 'PACS Services') |
| `source_reference` | TEXT | NULL | Official links, citations, or legal scheme references |
| `timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp of message delivery |

#### 4. `sample_responses` (Knowledge Base) Table
Predefined authoritative knowledge base serving immediate fallback responses and structuring the foundation for the upcoming RAG pipeline.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INT | PK, AUTO_INCREMENT | Identifier |
| `topic_keyword` | VARCHAR(100) | NOT NULL, INDEX | Primary topic category |
| `question_pattern` | TEXT | NOT NULL | Keyword patterns and sample prompt variations |
| `answer_text` | TEXT | NOT NULL | Verified answer text in the designated language |
| `language` | VARCHAR(10) | NOT NULL, INDEX | Language code ('en', 'hi', 'mr') |
| `source_title` | VARCHAR(255) | NOT NULL | Title of official department/scheme |
| `source_url` | VARCHAR(500) | NOT NULL | Official URL (e.g., https://pmfby.gov.in) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

---

## 2. Directory Structure

```
database/
├── README.md               # Database documentation & manual
├── init_db.py              # Automated CLI initialization script
├── schemas/
│   └── schema.sql          # Complete DDL SQL schema
├── seeds/
│   └── seed_data.sql       # Seed data for topics, answers, and demo user
└── migrations/             # Schema migration scripts
```

---

## 3. How to Set Up & Initialize the Database

### Method A: Automated CLI Script (Recommended)
From the project root:
```bash
# 1. Ensure MySQL server is running locally on port 3306
# 2. Run the initialization script (creates DB, tables, and populates seed data)
python database/init_db.py

# Optional: To drop existing database and re-seed from scratch:
python database/init_db.py --drop --seed
```

### Method B: Manual MySQL Import
Using MySQL CLI or Workbench:
```bash
# Log into MySQL
mysql -u root -p

# Execute Schema DDL
source database/schemas/schema.sql;

# Execute Seeds
source database/seeds/seed_data.sql;
```

---

## 4. Connection Details
The FastAPI backend connects to MySQL using:
```
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:3306/sahai_coop_db
```
Configure your credentials in `backend/.env`.
