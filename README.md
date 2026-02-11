# Project Report Automation – MVP

This project is a local-first web application that automates the creation of structured project feasibility reports.

Consultants input basic project details through a web form.  
The system generates a professionally formatted Microsoft Word (.docx) report using AI-driven section prompts.

This README documents the MVP scope, architecture, and step-wise development approach.

## MVP Scope

The MVP supports:
- Single form submission (no authentication)
- SQLite-based local storage
- AI-generated narrative sections
- Word (.docx) report generation
- Fixed report structure

Out of scope for MVP:
- User login / roles
- Client portals
- Advanced financial modeling (IRR, DSCR)
- Template customization UI
- Cloud deployment

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: Server-rendered HTML (Jinja)
- Database: SQLite
- AI: LLM via abstraction layer
- Document Generation: python-docx
- Environment Config: .env

## Folder Structure

app/
├── main.py              # FastAPI app + routes
├── models.py            # Pydantic schemas
├── db.py                # SQLite connection & queries
├── report_builder.py    # Word document generation
├── llm_client.py        # AI abstraction layer
├── prompts/             # One prompt file per report section
│   ├── executive_summary.txt
│   ├── market_assessment.txt
│   └── risk_assessment.txt
├── templates/           # HTML templates
│   └── form.html
├── static/              # CSS / assets
.env
README.md

## Application Flow

1. User fills out the web form
2. Data is validated using Pydantic
3. Submission is stored in SQLite
4. Each report section is generated using a dedicated AI prompt
5. Sections are assembled into a Word (.docx) file
6. User downloads the generated report

## API Endpoints

POST /api/submit
- Saves a new submission
- Returns submission_id

GET /api/submission/{id}
- Fetches stored submission data

POST /api/report/{id}
- Generates and returns a .docx report

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

