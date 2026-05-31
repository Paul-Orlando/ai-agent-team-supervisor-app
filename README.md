# AI Agent Team — Supervisor Pattern
### OpenAI Agents SDK · Next.js · FastAPI · ChromaDB

A production multi-agent supervisor pattern application that converts
a Flowise AgentFlows V2/V3 prototype into a full-stack Python deployment
using the OpenAI Agents SDK — featuring live agent status, RAG pipeline,
execution state tracking, and full delivery package export.

---

## 🔗 Live Demo

**[Try it live → ai-agent-team-supervisor-app.vercel.app](https://ai-agent-team-supervisor-app.vercel.app)**

---

## What It Does

Upload any PDF as a knowledge base then submit a software engineering
request. Six specialized agents collaborate autonomously to produce
a complete engineering delivery package — with live status updates,
quality review governance, and export in MD, PDF, or DOCX.

---

## Architecture

```
User Request
        ↓
┌─────────────────────────────────────────┐
│         1. PLANNER                      │
│  Decomposes request into execution plan │
│  Defines success criteria               │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│         2. SUPERVISOR (Orchestrator)    │
│  Routes tasks — maintains state         │
│  Enforces guardrails — handles retries  │
│  Decides: SOFTWARE / REVIEWER / FINISH  │
│  Max 5 loops per agent                  │
└──────────────┬──────────────────────────┘
               ↓
    ┌──────────────────────┐
    │   CONDITION ROUTER   │
    └──┬───────────┬───────┘
       │           │
       ▼           ▼
  SOFTWARE     REVIEWER
  ENGINEER     (QA Gate)
  Full Stack   Quality
  Developer    Assurance
       │           │
    Loop↑       Loop↑
   (max 5)    (max 5)
       └───────────┘
               ↓
      PENDING → CHANGES REQUIRED → APPROVED
               ↓
┌─────────────────────────────────────────┐
│      3. FALLBACK / ESCALATION           │
│  Triggered on max retries or errors     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│      4. FINAL SYNTHESIZER               │
│  Packages approved output               │
│  Formats delivery report                │
│  Provides next steps and artifacts      │
└─────────────────────────────────────────┘
```

## Workflow Diagram

![Supervisor Pattern Workflow](workflow.png)

---

## Key Features

- 6-agent pipeline — Planner, Supervisor, Engineer,
  Reviewer, Synthesizer, Fallback
- Live agent status panel — watch routing decisions in real time
- Review lifecycle — PENDING → CHANGES REQUIRED → APPROVED
- Execution state tracking — iterations, tokens, quality score
- RAG pipeline — upload any PDF as knowledge base
- ChromaDB vector store — semantic search across uploaded docs
- Streaming responses — SSE real-time output
- Export delivery packages — MD, PDF, DOCX
- Model selector — gpt-4o-mini / gpt-4o
- Max iterations slider — 1 to 10
- Session management — 30 minute session timeout

---
| Report | Query | Review Result |
|---|---|---|
| example_report_01.pdf | Microservices app | APPROVED |
| example_report_02.pdf | Food Chatbot Node.js | CHANGES REQUIRED → APPROVED |
| example_report_03.pdf | Food Chatbot Python | CHANGES REQUIRED → APPROVED |

---

## Agent System Prompts

All prompts preserved verbatim from the Flowise JSON:

| Agent | Source | Temperature |
|---|---|---|
| Supervisor | `llmAgentflow_0` | 0.9 |
| Software Engineer | `llmAgentflow_1` | 0.4 |
| Code Reviewer | `llmAgentflow_2` | 0.2 |
| Final Synthesizer | `llmAgentflow_3` | 0.9 |
| Planner | workflow.png spec | 0.7 |
| Fallback Handler | workflow.png spec | 0.3 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 + shadcn/ui + Tailwind CSS |
| Backend | Python FastAPI |
| Agent Framework | OpenAI Agents SDK |
| Vector Store | ChromaDB |
| Embeddings | text-embedding-3-small |
| PDF Extraction | pdfplumber |
| Streaming | SSE (Server-Sent Events) |
| Frontend Hosting | Vercel |
| Backend Hosting | Railway |
| Built With | Claude Code |

---

## RAG System

- Startup: seeds ChromaDB from uploaded PDF at launch
- User uploads: drag-drop PDFs in the UI — chunked and
  embedded immediately
- Chunk size: 1000 chars, 200 char overlap
- Embedding model: `text-embedding-3-small`
- Top 3 relevant chunks injected into each agent call
- Chunk count displayed live in the UI

---

## Execution State Tracking

The system maintains full runtime state throughout execution:

```json
{
  "execution_id": "",
  "user_input": "",
  "plan": "",
  "current_step": "",
  "retries": 0,
  "artifacts": [],
  "review_status": "PENDING",
  "quality_score": 0,
  "iteration_count": 0,
  "cost_tokens": 0,
  "timestamps": {}
}
```

All fields update in real time in the UI execution state panel.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Status + RAG chunk count |
| `POST` | `/upload-pdf` | Upload PDF to knowledge base |
| `POST` | `/run-agents` | Run pipeline (SSE stream) |
| `GET` | `/download-report/{session_id}/{format}` | Export: md, pdf, docx |
| `GET` | `/session/{session_id}/state` | Get execution state |

---

## Project Structure

```
ai-agent-team-supervisor-app/
│
├── backend/                    FastAPI + OpenAI Agents SDK
│   ├── main.py                 FastAPI app + CORS + endpoints
│   ├── agents/                 6 agent implementations
│   ├── rag/                    ChromaDB + embedder + store
│   ├── sessions/               Session state management
│   ├── requirements.txt        Python dependencies
│   └── Procfile                Railway deployment config
│
├── frontend/                   Next.js application
│   ├── app/                    App Router pages + API routes
│   ├── components/             UI components
│   └── lib/                    API client utilities
│
├── ai_agent_teams_agents.json  Original Flowise configuration
├── workflow.png                Architecture diagram
├── .gitignore
└── README.md
```

---

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

cp .env.example .env
# Add your OPENAI_API_KEY to .env

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

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key |
| `FRONTEND_URL` | optional | Default: `http://localhost:3000` |
| `CHROMA_PERSIST_DIR` | optional | Default: `./chroma_db` |
| `PDF_PATH` | optional | Path to startup PDF for RAG seeding |
| `PORT` | optional | Default: `8000` (Railway assigns automatically) |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | ✅ | Backend URL — do NOT mark as Sensitive in Vercel |

---

## Deployment

### Backend → Railway

1. Create new project → Deploy from GitHub repo
2. Set Root Directory: `backend`
3. Add environment variables in Railway dashboard
4. `Procfile` already configured:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```
5. Generate domain in Settings → Networking

### Frontend → Vercel

1. Import repo → set Root Directory: `frontend`
2. Add environment variable:
```
NEXT_PUBLIC_BACKEND_URL = https://your-railway-url.up.railway.app
```
⚠️ **Critical:** Do NOT mark `NEXT_PUBLIC_BACKEND_URL` as Sensitive —
this prevents Next.js from baking the value into the build bundle.

3. Deploy

---

## Deployment Notes

**CORS configuration**
The backend uses `allow_origin_regex` to whitelist all
`*.vercel.app` domains automatically — no manual updates
needed when Vercel generates new preview URLs.

**NEXT_PUBLIC_ variables**
These are baked into the JavaScript bundle at build time.
If the variable is marked Sensitive in Vercel it will not
be available during the build step and requests will fail.
Always leave Sensitive OFF for `NEXT_PUBLIC_*` variables.

---

## Related Repos

| Repo | Pattern | Framework |
|---|---|---|
| [ai-agent-team-supervisor-pattern](https://github.com/Paul-Orlando/ai-agent-team-supervisor-pattern) | Flowise Prototype | Flowise AgentFlows V2/V3 |
| [data-analysis-agent-app](https://github.com/Paul-Orlando/data-analysis-agent-app) | Interactive Data Agent | Next.js + FastAPI |
| [deep-research-agent](https://github.com/Paul-Orlando/deep-research-agent) | Research App | Claude Code + Next.js |
| [ai-food-chatbot-agent](https://github.com/Paul-Orlando/ai-food-chatbot-agent) | Agentic RAG | Flowise + Postgres |
| [ai-n8n-document-generator](https://github.com/Paul-Orlando/ai-n8n-document-generator) | LLM Chain + Quality Gate | n8n + OpenRouter |

---

## Author

Paul Orlando
Creative Technologist | AI Agent Developer | Data Analytics
🌐 [paulforlando.com](https://www.paulforlando.com)
💼 [LinkedIn](https://www.linkedin.com/in/paul-orlando-7841b5154)
🐙 [GitHub](https://github.com/Paul-Orlando)

---

## License

MIT License
