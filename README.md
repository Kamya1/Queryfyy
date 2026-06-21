# Queryfy: RAG-Powered AI Question Paper Generator

Queryfy turns uploaded study material into printable assessments using a Flask backend, Groq question generation, retrieval-aware context selection, duplicate detection, PDF/DOCX export, and optional Google Forms export.

## Features

- Upload PDF, DOCX, PPTX, or TXT files
- Extract, clean, chunk, embed, and retrieve document context
- Generate MCQ, True/False, Fill-Ups, Short Answer, Long Answer, and Numerical questions
- Enforce the exact requested question count before export
- Prevent near-duplicate questions across regeneration attempts
- Export clean student PDFs without per-question AI metadata
- Add Teacher Answer Sheet and final AI Assessment Summary pages in PDFs
- Export DOCX and optional Google Forms
- Store lightweight analytics in SQLite
- Health endpoint for deployment checks: `/health`

## Runtime

- Python 3.11+
- Flask
- Groq API
- SQLite
- Optional Google Forms/Drive API credentials
- Optional local RAG extras through `optional-requirements.txt`

## Local Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Optional local semantic stack:

```bash
pip install -r optional-requirements.txt
```

Create `.env.local` for local development only:

```bash
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=8192
GROQ_TIMEOUT=60
GROQ_MAX_RETRIES=3

PORT=5000
QUERYFY_DB_PATH=queryfy.db

RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=80
RAG_TOP_K=6
```

Run:

```bash
python app.py
```

## Render Deployment

`render.yaml` is included.

Set these environment variables in Render:

```bash
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=8192
GROQ_TIMEOUT=60
GROQ_MAX_RETRIES=3
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=80
RAG_TOP_K=6
```

Start command:

```bash
gunicorn app:app
```

## Vercel Deployment

Vercel support is included through:

- `api/index.py`
- `vercel.json`
- `requirements.txt`
- `.vercelignore`
- `package.json`

Set the same Groq variables in Vercel Project Settings. Do not rely on `.env.local` in production.

`npm run build` is intentionally a no-op because Queryfy serves the current UI from Flask templates.

## Google Forms

Google Forms is optional. If credentials are missing, the Google Form option is hidden and the app continues working.

Configure one of:

```bash
SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
SERVICE_ACCOUNT_JSON_BASE64=base64_encoded_service_account_json
SERVICE_ACCOUNT_FILE=service-account.json
```

For Vercel, prefer `SERVICE_ACCOUNT_JSON_BASE64` or `SERVICE_ACCOUNT_JSON` through Project Settings.

## Health Check

Visit:

```text
/health
```

It reports:

- Groq key status
- Groq model
- Google Forms status
- Vector store status
- SQLite database path

## Notes

- Upload temp files are written to `tempfile.gettempdir()` and deleted after processing.
- On Vercel, fallback SQLite and vector storage use the platform temp directory.
- `requirements.txt` contains deployment-critical packages only.
- `optional-requirements.txt` enables local Sentence Transformers and ChromaDB if desired.
