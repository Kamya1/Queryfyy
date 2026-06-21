<div align="center">

<br />

<img src="https://img.shields.io/badge/Queryfyy-AI%20Assessment%20Engine-6366F1?style=for-the-badge&labelColor=0F0F0F" alt="Queryfyy" height="40"/>

<br /><br />

**Transform any study material into exam-ready assessments — in seconds.**

<p>
  <a href="#quickstart"><strong>Quickstart</strong></a> ·
  <a href="#architecture"><strong>Architecture</strong></a> ·
  <a href="#configuration"><strong>Configuration</strong></a> ·
  <a href="#deployment"><strong>Deployment</strong></a> ·
  <a href="#api-reference"><strong>API Reference</strong></a>
</p>

<br />

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Groq](https://img.shields.io/badge/LLM-LLaMA%203.3%2070B-F55036?style=flat-square)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-FF6B35?style=flat-square)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

</div>

---

## Overview

Queryfyy is a full-stack RAG (Retrieval-Augmented Generation) platform that automates professional assessment creation from any document. Rather than sending entire documents to an LLM, Queryfyy semantically chunks, embeds, and retrieves only the most relevant content — producing accurate, grounded questions at every difficulty level.

Built for educators, e-learning platforms, and content teams who need reliable, repeatable question generation at scale.

---

## Features

**Document Ingestion**
Upload PDF, DOCX, PPTX, or TXT. Text is extracted, cleaned, and semantically chunked automatically — no preprocessing required.

**RAG Pipeline**
Sentence Transformer embeddings → ChromaDB vector store → top-k semantic retrieval. Every question is grounded in the source material.

**Six Question Types**
Multiple Choice, True/False, Fill-in-the-Blank, Short Answer, Long Answer, and Numerical — configurable per generation request.

**Bloom's Taxonomy Difficulty**
Easy (recall), Medium (application), Hard (synthesis and analysis) — controlled via a single parameter.

**Quality Assurance**
Built-in relevance scoring, context coverage metrics, difficulty calibration, confidence scores, and near-duplicate detection across regeneration attempts.

**Export Anywhere**
One-click export to PDF (with teacher answer sheet), DOCX, or Google Forms. Student PDFs are clean — no internal AI metadata.

**Analytics**
Per-session quality metrics available at `/analytics` and `/results`.

---

## Architecture

```
Upload (PDF / DOCX / PPTX / TXT)
        │
        ▼
  Text Extraction
  Text Cleaning
        │
        ▼
  Semantic Chunking
        │
        ▼
┌──────────────────────┐
│   EmbeddingService   │   all-MiniLM-L6-v2
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  VectorStore         │   ChromaDB · in-memory fallback
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  RetrievalService    │   top-k similarity search
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  QuestionGenerator   │   Groq · LLaMA-3.3-70B-Versatile
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  EvaluationService   │   Quality scoring · Deduplication
└──────────┬───────────┘
           │
   ┌───────┼───────┐
   ▼       ▼       ▼
 PDF     DOCX   Google    DatabaseManager
Export  Export   Forms      (Analytics)
```

---

## Project Structure

```
queryfyy/
├── app.py                     # Flask routes and RAG orchestration
│
├── services/
│   ├── embeddingService.py    # Lazy-loaded Sentence Transformer + embedding cache
│   ├── retrievalService.py    # Semantic chunk retrieval helpers
│   ├── questionGenerator.py   # Context-aware JSON generation and deduplication
│   └── evaluationService.py   # Relevance, coverage, difficulty, and confidence scoring
│
├── vectorstore/
│   └── vector_store.py        # Chunking + ChromaDB / in-memory vector storage
│
├── database/
│   └── sqlite_db.py           # PostgreSQL/Supabase with SQLite fallback
│
├── templates/
│   └── index.html             # Single-page UI (Jinja2)
│
├── static/                    # CSS and JS assets
│
├── api/
│   └── index.py               # Vercel serverless entry point
│
├── requirements.txt           # Vercel-safe core dependencies
├── optional-requirements.txt  # Full local ML stack (Sentence Transformers + ChromaDB)
├── render.yaml                # Render deployment config
├── vercel.json                # Vercel deployment config
├── runtime.txt                # Pins Python 3.11
└── tests_question_count.py    # Basic test suite
```

---

## Quickstart

### Prerequisites

- Python 3.11+
- [Groq API key](https://console.groq.com/) — free tier available
- *(Optional)* PostgreSQL / Supabase for production persistence
- *(Optional)* Google Cloud service account for Google Forms export

### Installation

```bash
# Clone the repository
git clone https://github.com/Kamya1/Queryfyy.git
cd Queryfyy

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate             # Windows

# Install core dependencies
pip install -r requirements.txt

# (Optional) Full local ML stack — Sentence Transformers + ChromaDB
pip install -r optional-requirements.txt
```

### Environment Setup

Create a `.env` file in the project root:

```env
# LLM
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=8192
GROQ_TIMEOUT=60
GROQ_MAX_RETRIES=3

# Database
QUERYFY_DB_PATH=queryfy.db
DATABASE_URL=postgresql://user:password@host:5432/dbname   # optional

# Google Forms (optional — all three variants supported)
SERVICE_ACCOUNT_JSON={"type":"service_account",...}
# SERVICE_ACCOUNT_JSON_BASE64=<base64_encoded_json>
# SERVICE_ACCOUNT_FILE=service-account.json

# RAG Tuning
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=80
RAG_TOP_K=6

# Server
PORT=5000
```

> If no `SERVICE_ACCOUNT_*` variable is set, the Google Forms export option is automatically hidden in the UI.

### Run

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Required. Your Groq API key. |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Model identifier. |
| `GROQ_TEMPERATURE` | `0.7` | Generation temperature. |
| `GROQ_MAX_TOKENS` | `8192` | Maximum tokens per generation call. |
| `GROQ_TIMEOUT` | `60` | Request timeout in seconds. |
| `GROQ_MAX_RETRIES` | `3` | Retry attempts on transient failures. |
| `RAG_CHUNK_SIZE` | `500` | Target token count per document chunk. |
| `RAG_CHUNK_OVERLAP` | `80` | Overlap between adjacent chunks. |
| `RAG_TOP_K` | `6` | Number of chunks retrieved per query. |
| `QUERYFY_DB_PATH` | `queryfy.db` | SQLite path for local runs. |
| `DATABASE_URL` | — | PostgreSQL / Supabase connection string. |
| `CHROMA_PERSIST_DIR` | `vectorstore/chroma/` | Override ChromaDB persistence path. |

---

## Deployment

### Render

Render is supported out of the box via `render.yaml`. Set your environment variables in Render's dashboard, then deploy.

```bash
# Production start command
gunicorn app:app
```

`runtime.txt` pins Python 3.11 to ensure ChromaDB installs within its supported NumPy version range.

### Vercel

Vercel is supported via `vercel.json` and `api/index.py`.

- When `VERCEL=1` is set, all file writes (uploads, SQLite, ChromaDB data) go to the platform temp directory.
- On Python 3.13 environments, ChromaDB is skipped via a dependency marker and the in-memory vector fallback is used automatically.
- `npm run build` is intentionally a no-op — Queryfyy serves its frontend through Flask templates with no Node build pipeline.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main application UI |
| `POST` | `/generate` | Generate questions from an uploaded document |
| `GET` | `/health` | Service health check |
| `GET` | `/analytics` | Session analytics and usage statistics |
| `GET` | `/results` | Quality scores from the latest generation |

### `GET /health`

Returns the status of all service dependencies.

```json
{
  "groq_key": "configured",
  "groq_model": "llama-3.3-70b-versatile",
  "google_forms": "disabled",
  "vector_store": "chromadb",
  "db_path": "queryfy.db"
}
```

### `POST /generate`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | `File` | Yes | PDF, DOCX, PPTX, or TXT |
| `question_types` | `string[]` | Yes | e.g. `["mcq", "true_false"]` |
| `difficulty` | `string` | Yes | `easy`, `medium`, or `hard` |
| `count` | `integer` | Yes | Total number of questions to generate |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| LLM | Groq API — LLaMA-3.3-70B-Versatile |
| Embeddings | Sentence Transformers — `all-MiniLM-L6-v2` |
| Vector Store | ChromaDB (in-memory fallback on serverless) |
| Database | PostgreSQL / Supabase — SQLite fallback |
| Export | ReportLab (PDF), python-docx (DOCX), Google Forms API |
| Frontend | HTML, CSS, JavaScript via Jinja2 templates |
| Deployment | Render, Vercel |

---

## Notes

- Uploaded files are written to `tempfile.gettempdir()` and deleted immediately after processing.
- `requirements.txt` is kept Vercel-safe (lightweight). Install `optional-requirements.txt` on Render or local environments for the full Sentence Transformers and ChromaDB stack.
- Without `DATABASE_URL` or `SUPABASE_DB_URL`, Queryfyy defaults to SQLite at the path set by `QUERYFY_DB_PATH`.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
