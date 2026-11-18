# SahAI-Coop RAG AI Engine (SIH26088)

Hybrid **Vector + BM25 Retrieval-Augmented Generation (RAG)** microservice powered by **Google Gemini API** for multilingual (English, Hindi, Marathi) cooperative governance and farmer legal assistance.

## Architecture
- **Knowledge Base (`app/knowledge_base/`)**: Curated Markdown, TXT, and PDF guides covering PMFBY, PACS/KCC, Land Documents (7/12 & 8A), Cooperative Laws & Member Rights, Grievance Redressal, and Government Schemes.
- **Hybrid Retriever (`app/rag/`)**:
  - Dense semantic search via Gemini Embeddings + NumPy cosine similarity (persisted to `data/vector_index.json`).
  - Unicode/Devanagari-aware BM25 lexical search with cross-lingual keyword expansion.
  - Reciprocal Rank Fusion (RRF) combining both rankings.
- **Grounded Generation (`app/llm/`)**: Uses the official `google-genai` SDK (`gemini-2.5-flash` with fallback) and multi-turn conversation history.

## Quick Start

1. **Get a free Gemini API Key** at [Google AI Studio](https://aistudio.google.com/apikey).
2. **Paste it into `ai-engine/.env`**:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. **Install dependencies & run**:
   ```powershell
   cd ai-engine
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python run.py
   ```
4. **Verify**:
   - Swagger UI: `http://localhost:8001/docs`
   - Health check: `http://localhost:8001/api/rag/health`

## Adding Your Own PDFs or Scheme Documents
Drop any `.pdf`, `.md`, or `.txt` file into `app/knowledge_base/<category>/` and call `POST http://localhost:8001/api/rag/reindex` (or upload directly via `POST /api/rag/upload` in Swagger UI).
