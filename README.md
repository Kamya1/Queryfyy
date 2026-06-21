# Queryfy: RAG-Powered AI Question Paper Generator

Queryfy transforms study material into professional assessments. The existing upload, generation, export, and Google Forms workflows are preserved, and the backend now uses a Retrieval-Augmented Generation pipeline so questions are generated from semantically retrieved document chunks instead of sending whole documents directly to the LLM.

## Features

- Upload PDF, DOCX, PPTX, or TXT files
- Extract and clean document text
- Chunk documents with configurable chunk size and overlap
- Generate embeddings with Sentence Transformers `all-MiniLM-L6-v2`
- Store chunks, embeddings, metadata, and document references in ChromaDB with an in-memory fallback
- Retrieve top-k relevant chunks before generation
- Generate MCQ, True/False, Fill-Ups, Short Answer, Long Answer, and Numerical questions
- Choose Easy, Medium, or Hard difficulty using Bloom's Taxonomy guidance
- Generate correct answers, explanations, and source chunk references
- Detect near-duplicate questions with embedding similarity
- Calculate relevance, context coverage, difficulty, and confidence scores
- Export as PDF, DOCX, or Google Form
- Store documents, generated questions, metadata, and analytics in PostgreSQL/Supabase with SQLite fallback
- Expose analytics through `/analytics` and latest quality scores through `/results`

## Architecture

```text
Document Upload
  -> Text Extraction
  -> Text Cleaning
  -> Semantic Chunking
  -> EmbeddingService (all-MiniLM-L6-v2)
  -> VectorStore (ChromaDB preferred, in-memory fallback)
  -> RetrievalService (top-k similarity search)
  -> QuestionGenerator (Groq with retrieved context only)
  -> EvaluationService (quality scores + duplicate detection)
  -> Exports + DatabaseManager analytics
```

## Folder Structure

```text
app.py                    Flask routes, existing exports, RAG orchestration
templates/index.html      Existing single-page UI with added difficulty, RAG controls, and score display
services/
  embeddingService.py     Lazy-loaded Sentence Transformer embeddings with cache
  retrievalService.py     Semantic retrieval helpers
  questionGenerator.py    Context-aware JSON question generation and duplicate filtering
  evaluationService.py    Relevance, coverage, difficulty, and confidence scoring
vectorstore/
  vector_store.py         Chunking plus ChromaDB/in-memory vector storage
database/
  sqlite_db.py            PostgreSQL/Supabase persistence with SQLite fallback
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r optional-requirements.txt  # optional: full local Sentence Transformers + ChromaDB
```

Create a `.env` file:

```bash
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=8192
GROQ_TIMEOUT=60
SERVICE_ACCOUNT_JSON={"type":"service_account", "...":"..."}
SERVICE_ACCOUNT_FILE=service-account.json
SERVICE_ACCOUNT_JSON_BASE64=base64_encoded_service_account_json
QUERYFY_DB_PATH=queryfy.db
DATABASE_URL=postgresql://user:password@host:5432/dbname
PORT=5000
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=80
RAG_TOP_K=6
```

Run locally:

```bash
python app.py
```

Production start command:

```bash
gunicorn app:app
```

## Deployment Notes

- Render is supported through `render.yaml`.
- `runtime.txt` pins Python 3.11 so ChromaDB installs with its supported NumPy range.
- Backend APIs remain Flask routes: `/`, `/generate`, `/health`, `/analytics`, and `/results`.
- Vercel is supported through `vercel.json` and `api/index.py`. The app writes temporary uploads, fallback SQLite, and fallback Chroma data under the platform temp directory when `VERCEL=1`.
- `npm run build` is a no-op check because Queryfy serves the existing frontend through Flask templates and has no Node build pipeline.
- ChromaDB persists vectors under `vectorstore/chroma` locally and under the serverless temp directory on Vercel unless `CHROMA_PERSIST_DIR` is set.
- `requirements.txt` is kept Vercel-safe. Install `optional-requirements.txt` locally or on Render when you want full Sentence Transformers and ChromaDB instead of the lightweight fallback embedding/vector path.
- Set `DATABASE_URL` or `SUPABASE_DB_URL` to use PostgreSQL/Supabase. Without it, Queryfy uses local SQLite at `QUERYFY_DB_PATH`.
- On Python 3.13 local environments, ChromaDB is skipped by the dependency marker and Queryfy uses the in-memory vector fallback.
- Google Forms export requires a Google Cloud service account with Forms and Drive APIs enabled. Configure one of `SERVICE_ACCOUNT_JSON`, `SERVICE_ACCOUNT_JSON_BASE64`, or `SERVICE_ACCOUNT_FILE`. If none is set, the Google Form option is hidden.

## Resume Summary

Built a Retrieval-Augmented Generation (RAG) platform for automated assessment generation using semantic search, vector embeddings, context-aware question generation, Bloom's Taxonomy difficulty classification, duplicate detection, and quality evaluation.
