# Supervisor Pattern Multi-Agent System

Full-stack production application converting a Flowise supervisor-pattern workflow
into Python using the OpenAI Agents SDK + Next.js frontend.

## Architecture

```
User Request
    ↓
Planner  →  creates execution plan
    ↓
Supervisor (loop, max iterations)
    ├── SOFTWARE → Software Engineer (streams implementation)
    ├── REVIEWER → Code Reviewer (streams review)
    └── FINISH   → breaks loop
    ↓
Final Synthesizer  →  streams delivery report
```

## Project Structure

```
supervisor-pattern-multi-agent/
├── backend/          FastAPI + OpenAI Agents SDK
└── frontend/         Next.js + shadcn/ui
```

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Create .env
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### 2. Frontend

```bash
cd frontend
cp .env.example .env.local
# .env.local already points to http://localhost:8000

npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key |
| `FRONTEND_URL` | optional | Default: `http://localhost:3000` |
| `CHROMA_PERSIST_DIR` | optional | Default: `./chroma_db` |
| `PDF_PATH` | optional | Path to startup PDF for RAG seeding |
| `PORT` | optional | Default: `8000` (Railway uses this) |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | ✅ | Backend URL |

## Agent System Prompts

All prompts are preserved verbatim from the Flowise JSON:

| Agent | Source | Temperature |
|---|---|---|
| Supervisor | `llmAgentflow_0` | 0.9 |
| Software Engineer | `llmAgentflow_1` | 0.4 |
| Code Reviewer | `llmAgentflow_2` | 0.2 |
| Final Synthesizer | `llmAgentflow_3` | 0.9 |
| Planner | workflow.png spec | 0.7 |
| Fallback | workflow.png spec | 0.3 |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Status + RAG chunk count |
| `POST` | `/upload-pdf` | Upload PDF to knowledge base |
| `POST` | `/run-agents` | Run pipeline (SSE stream) |
| `GET` | `/download-report/{session_id}/{format}` | Export: `md`, `pdf`, `docx` |
| `GET` | `/session/{session_id}/state` | Get execution state |

## Deployment

### Backend → Railway

1. Set environment variables in Railway dashboard
2. `Procfile` already configured: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel

1. Import the `frontend/` directory
2. Set `NEXT_PUBLIC_BACKEND_URL` to your Railway backend URL

## RAG System

- Startup: seeds ChromaDB from `course_advanced_prompt_engineering.pdf`
- User uploads: drag-drop PDFs in the UI, they are chunked and embedded immediately
- Chunk size: 1000 chars, 200 char overlap
- Embedding model: `text-embedding-3-small`
- Top 3 relevant chunks injected into each agent call
