# Project Report Automation – AI Feasibility Report Agent

This project is an AI-orchestrated system that generates lender-grade project feasibility reports (90+ pages) based on structured client inputs and AI-driven research and financial modeling.

Consultants input comprehensive project details through a web form. The system generates a professionally formatted Microsoft Word (.docx) report using a six-module AI agent architecture with staged prompting, validation loops, and deterministic financial modeling.

This README documents the current implementation status, architecture, and roadmap toward full PRD compliance.

## Current Status

**Phase:** MVP → PRD Implementation (Sprint 1 in progress)

**Completed:**
- ✅ MVP web form + submission flow
- ✅ SQLite persistence
- ✅ Basic AI-generated sections (3 sections)
- ✅ Word (.docx) generation
- ✅ **Module 1 (Partial):** Expanded input schema with critical field classification
- ✅ **Policy C Implementation:** Critical input validation with blocking on missing fields
- ✅ Architecture Decision Records (ADRs) for key design choices

**In Progress (Sprint 1):**
- Module 2: Baseline & Assumption Lock Agent
- Enhanced validation and assumption tagging

**Planned:**
- Sprint 2: Module 3 - Financial Model Agent (13 schedules, 7 KPIs)
- Sprint 3: Module 4-5 - Section Drafting + Equipment Intelligence
- Sprint 4: Module 6 - Final Assembly & QA, Runtime migration to queue-based processing

## Documentation

- **[PRD: AI Project Feasibility Report Agent](ai-project-report-agent-prd.md)** - Full product requirements
- **[Architecture Decision Records (ADRs)](docs/adr/)** - Key technical decisions:
  - [ADR-0001: Critical Input Validation Policy](docs/adr/ADR-0001-critical-input-policy.md)
  - [ADR-0002: Financial Standard Selection](docs/adr/ADR-0002-financial-standard.md)
  - [ADR-0003: Runtime Execution Model](docs/adr/ADR-0003-runtime-execution-model.md)

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: Server-rendered HTML (Jinja)
- Database: SQLite (MVP), PostgreSQL (production planned)
- AI: LLM via abstraction layer (OpenAI GPT-4, configurable)
- Document Generation: python-docx
- Environment Config: .env
- Future: Celery + Redis (for async job queue in Sprint 4)

## Folder Structure

```
app/
├── main.py              # FastAPI app + routes + validation
├── models.py            # Pydantic schemas (expanded for PRD Module 1)
├── db.py                # SQLite connection & queries
├── report_builder.py    # Word document generation + section orchestration
├── llm_client.py        # AI abstraction layer
├── prompt_renderer.py   # Prompt template rendering
├── prompts/             # Prompt templates per section
│   ├── executive_summary.txt
│   ├── market_assessment.txt
│   └── risk_assessment.txt
├── templates/           # HTML templates
│   └── form.html        # Expanded with PRD Module 1 fields
├── static/              # CSS / assets
docs/
├── adr/                 # Architecture Decision Records
│   ├── README.md
│   ├── _template.md
│   ├── ADR-0001-critical-input-policy.md
│   ├── ADR-0002-financial-standard.md
│   └── ADR-0003-runtime-execution-model.md
ai-project-report-agent-prd.md
.env
README.md
```

## Application Flow (Current)

1. User fills out comprehensive web form (Module 1 inputs)
2. Data validated using Pydantic with critical field enforcement (Policy C)
3. Submission stored in SQLite with validation summary
4. Report sections generated using dedicated AI prompts (cached)
5. Sections assembled into Word (.docx) file
6. User downloads generated report

## Application Flow (Target - Post Sprint 4)

1. User submits comprehensive project data
2. **Module 2:** Baseline lock with assumption tagging (Client/AI Default/Public Source)
3. **Module 3:** Financial model generation (13 schedules, KPI calculations)
4. **Module 4:** Section drafting with coverage validation loops
5. **Module 5:** Equipment intelligence with OEM research and citations
6. **Module 6:** Final assembly with QA validation (90+ pages, lender-grade)
7. Background job processing with status polling
8. User downloads completed report

## Deployment

### Railway Deployment (Production)

This application is configured for Railway deployment:

**Quick Deploy:**
1. Fork/clone this repository
2. Sign up at [railway.app](https://railway.app)
3. Create new project → Deploy from GitHub repo
4. Set environment variables:
   - `LLM_PROVIDER=openai`
   - `OPENAI_API_KEY=your-key-here`
5. Railway auto-detects config and deploys

**Detailed Guide:** See [Railway Deployment Guide](docs/RAILWAY_DEPLOYMENT.md)

**Configuration Files:**
- `railway.toml` / `railway.json` - Railway configuration
- `Procfile` - Process definition
- `runtime.txt` - Python version
- `requirements.txt` - Dependencies with pinned versions

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repo-url>
   cd project-automation
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Access Application**
   - Web Form: http://localhost:8000
   - Health Check: http://localhost:8000/health
   - API Docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web form for submission |
| POST | `/api/submit` | Submit project data, returns ID + validation summary |
| GET | `/api/submission/{id}` | Retrieve stored submission |
| GET/POST | `/api/report/{id}` | Generate and download .docx report |
| GET | `/health` | Health check endpoint |

## Report Structure (MVP)

1. Executive Summary
2. Introduction
   - Background
   - Project Idea & Value Proposition
   - Promoters’ Background
3. Market Assessment
   - Industry Overview
   - Target Market
   - Competitive Landscape
4. Risk Assessment & Mitigation
5. Caveats
6. Appendices

## Prompting Strategy

- Each report section has its own prompt file
- Prompts receive structured input only
- Missing inputs are handled via assumptions
- Outputs are stored to allow regeneration without re-calling the LLM


## Local Setup

1. Create a virtual environment
2. Install dependencies
3. Add API keys to .env
4. Run FastAPI server

Example:
uvicorn app.main:app --reload

## Step-wise Development Plan

Step 0: Project setup & skeleton  
Step 1: Web form (minimal inputs)  
Step 2: SQLite persistence  
Step 3: Word document generation (no AI)  
Step 4: AI-powered section generation  
Step 5: Validation & quality checks  
Step 6: Expand report sections iteratively  
Step 7: Optional features (auth, templates, hosting)

