<div align="center">

# 🔍 Queryfyy

### RAG-Powered AI Assessment Generator

**Transform any study material into professional, exam-ready question papers in seconds.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20LLaMA--3.3--70B-F55036?style=flat-square)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-FF6B35?style=flat-square)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Deploy on Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=flat-square&logo=render)](https://render.com/)
[![Deploy on Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=flat-square&logo=vercel)](https://vercel.com/)

</div>

---

## 📌 Overview

**Queryfyy** is a full-stack AI platform that automates assessment creation using a **Retrieval-Augmented Generation (RAG)** pipeline. Instead of sending entire documents to a language model, Queryfyy semantically chunks, embeds, and retrieves only the most relevant content — producing accurate, context-grounded questions every time.

Built for educators, content creators, and e-learning platforms, Queryfyy supports multiple question types, Bloom's Taxonomy difficulty levels, built-in quality evaluation, and one-click export to PDF, DOCX, or Google Forms.

---

## ✨ Features

| Category | Capabilities |
|---|---|
| **Document Ingestion** | Upload PDF, DOCX, PPTX, TXT — text is extracted, cleaned, and chunked automatically |
| **RAG Pipeline** | Semantic chunking → Sentence Transformer embeddings → ChromaDB vector store → top-k retrieval |
| **Question Generation** | MCQ, True/False, Fill-in-the-Blank, Short Answer, Long Answer, Numerical |
| **Difficulty Control** | Easy / Medium / Hard — guided by Bloom's Taxonomy (recall → analysis → synthesis) |
| **Quality Assurance** | Relevance scoring, context coverage, difficulty calibration, confidence scores, duplicate detection |
| **Export Options** | PDF, DOCX, Google Forms |
| **Analytics** | Per-session quality metrics via `/analytics` and `/results` endpoints |
| **Database** | PostgreSQL / Supabase with SQLite fallback for zero-config local runs |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Upload                          │
│              (PDF / DOCX / PPTX / TXT)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    Text Extraction
                    Text Cleaning
                            │
                    Semantic Chunking
                            │
               ┌────────────▼────────────┐
               │   EmbeddingService      │
               │  (all-MiniLM-L6-v2)    │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │  VectorStore (ChromaDB) │
               │  In-memory fallback     │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │   RetrievalService      │
               │   (top-k similarity)    │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │   QuestionGenerator     │
               │  (Groq / LLaMA-3.3-70B) │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │   EvaluationService     │
               │ Quality + Deduplication │
               └────────────┬────────────┘
                            │
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
           PDF/DOCX    Google Forms   DatabaseManager
           Export        Export        (Analytics)
```

---

## 📁 Project Structure

```
Queryfyy/
│
├── app.py                        # Flask routes & RAG orchestration
│
├── services/
│   ├── embeddingService.py       # Lazy-loaded Sentence Transformer + embedding cache
│   ├── retrievalService.py       # Semantic chunk retrieval helpers
│   ├── questionGenerator.py      # Context-aware JSON question generation & dedup
│   └── evaluationService.py      # Quality scoring (relevance, coverage, difficulty, confidence)
│
├── vectorstore/
│   └── vector_store.py           # Chunking + ChromaDB / in-memory vector storage
│
├── database/
│   └── sqlite_db.py              # PostgreSQL/Supabase persistence with SQLite fallback
│
├── templates/
│   └── index.html                # Single-page UI with difficulty controls & score display
│
├── static/                       # CSS, JS assets
├── api/
│   └── index.py                  # Vercel serverless entry point
│
├── requirements.txt              # Vercel-safe dependencies
├── optional-requirements.txt     # Full local Sentence Transformers + ChromaDB
├── render.yaml                   # Render deployment config
├── vercel.json                   # Vercel deployment config
├── runtime.txt                   # Pins Python 3.11
└── tests_question_count.py       # Basic test suite
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com/) (free tier available)
- *(Optional)* PostgreSQL / Supabase for production persistence
- *(Optional)* Google Cloud service account for Google Forms export

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Kamya1/Queryfyy.git
cd Queryfyy

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install core dependencies
pip install -r requirements.txt

# 4. (Optional) Install full local ML stack (Sentence Transformers + ChromaDB)
pip install -r optional-requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root:

```env
# ── LLM ──────────────────────────────────────────
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=8192
GROQ_TIMEOUT=60

# ── Database ──────────────────────────────────────
QUERYFY_DB_PATH=queryfy.db                          # SQLite path (local fallback)
DATABASE_URL=postgresql://user:password@host:5432/dbname  # Optional: PostgreSQL/Supabase

# ── Google Forms Export (Optional) ───────────────
SERVICE_ACCOUNT_JSON={"type":"service_account",...}
# OR
SERVICE_ACCOUNT_JSON_BASE64=<base64_encoded_json>
# OR
SERVICE_ACCOUNT_FILE=service-account.json

# ── RAG Tuning ────────────────────────────────────
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=80
RAG_TOP_K=6

# ── Server ────────────────────────────────────────
PORT=5000
```

> **Note:** If none of the `SERVICE_ACCOUNT_*` variables are set, the Google Forms export option is automatically hidden in the UI.

### Run Locally

```bash
python app.py
```

Open your browser at `http://localhost:5000`

---

## 🌐 Deployment

### Render

Render is supported out of the box via `render.yaml`.

```bash
# Production start command
gunicorn app:app
```

`runtime.txt` pins **Python 3.11** to ensure ChromaDB installs within its supported NumPy version range.

### Vercel

Vercel is supported via `vercel.json` and `api/index.py`.

- When `VERCEL=1` is set, all file writes (uploads, SQLite, Chroma data) go to the platform's temp directory.
- Set `CHROMA_PERSIST_DIR` to override the default Chroma persistence path.
- On Python 3.13 environments, ChromaDB is skipped via a dependency marker and the in-memory vector fallback is used automatically.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main application UI |
| `POST` | `/generate` | Generate questions from uploaded document |
| `GET` | `/health` | Health check |
| `GET` | `/analytics` | Session analytics & usage stats |
| `GET` | `/results` | Latest generation quality scores |

---

## 🔧 Configuration Notes

- `requirements.txt` is kept **Vercel-safe** (lightweight). Install `optional-requirements.txt` on local or Render environments to enable full Sentence Transformers and ChromaDB support.
- Without `DATABASE_URL` or `SUPABASE_DB_URL`, Queryfyy defaults to **SQLite** at the path specified by `QUERYFY_DB_PATH`.
- ChromaDB vectors persist under `vectorstore/chroma/` locally. On serverless environments, they live in the temp directory unless `CHROMA_PERSIST_DIR` is configured.
- `npm run build` is a no-op — Queryfyy serves its frontend through Flask templates with no Node build pipeline.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, Flask |
| **LLM** | Groq API (LLaMA-3.3-70B-Versatile) |
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Vector Store** | ChromaDB (with in-memory fallback) |
| **Database** | PostgreSQL / Supabase (with SQLite fallback) |
| **Export** | ReportLab (PDF), python-docx (DOCX), Google Forms API |
| **Frontend** | HTML, CSS, JavaScript (served via Jinja2 templates) |
| **Deployment** | Render, Vercel |

---

## 📊 Resume Highlight

> Built a **Retrieval-Augmented Generation (RAG)** platform for automated assessment creation — featuring semantic document chunking, vector embeddings, context-aware LLM prompting, Bloom's Taxonomy difficulty classification, duplicate question detection, and multi-format export (PDF, DOCX, Google Forms). Deployed on both Render and Vercel with PostgreSQL/Supabase persistence.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

