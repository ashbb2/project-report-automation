# AI Project Feasibility Report Agent

## Product Requirements Document (PRD)

## 1. Product Overview

### 1.1 Purpose
The AI Project Feasibility Report Agent is an AI-orchestrated system that generates a lender-grade project feasibility report ($\geq 90$ pages) based solely on structured client inputs and AI-driven research and financial modelling.

The system will automatically generate:
- A minimum 90-page A4 report
- Font: Arial 12
- Single spacing
- Paragraph spacing: 6 pt
- 15 pages of financial tables
- 5–6 illustrated equipment pages within Section 5
- Source-backed regulatory and market intelligence

The system must:
- Use staged prompting
- Prevent AI hallucinations
- Produce complete financial projections
- Ensure coverage validation of all sections

## 2. Core Objectives
- Convert structured client inputs into a complete feasibility report.
- Generate a comprehensive AI-based financial model.
- Validate completeness against section-level requirements.
- Produce consistent lender-grade documentation.
- Ensure no silent assumptions or invented facts.
- Provide equipment manufacturer intelligence with citations.

## 3. System Architecture
The system consists of six sequential AI agents:

1. Client Inputs
2. Baseline Lock Agent
3. Financial Model Agent
4. Section Drafting Agent
5. Equipment Intelligence Agent
6. Final Assembly & QA Agent

## 4. AI Agent Modules

### Module 1 — Client Input Capture Agent
#### Purpose
Collect structured project inputs required to generate the feasibility report and financial model.

#### Required Inputs
**Project Identity**
- Client name
- Project title
- Product/service
- Project location
- Business model (B2B / B2C / B2G)

**Project Sizing Mode**
- User must choose one:
  - Capacity-driven
  - Budget-driven

**Commercial Assumptions**
- Selling price
- Product mix
- Production ramp-up
- Market geography

**Operating Assumptions**
- Operating days
- Shift structure
- Utilization assumptions
- Utilities consumption

**Financing Inputs**
- Total investment
- Debt/equity mix
- Loan tenor
- Interest rate
- Moratorium period

**Equipment Preferences**
- Preferred manufacturer geography
- Brand preferences
- Technology exclusions

#### Output
- `CLIENT_INPUTS_LOCKED`
- Structured JSON object

---

### Module 2 — Baseline & Assumption Lock Agent
#### Purpose
Create a single source of truth for the report.

#### Responsibilities
Generate:

**Project Definition**
- Project description
- Capacity explanation
- Location justification

**Tagged Assumption Table**
Each assumption must be labelled as:

| Source | Meaning |
|---|---|
| Client | Provided by user |
| AI Default | System-generated |
| Public Source | Market/regulatory data |

**Missing Inputs Detection**
- Critical missing inputs must stop the process.

#### Output
- `BASELINE_LOCKED_OBJECT`

---

### Module 3 — Financial Model Agent
#### Purpose
Generate complete financial projections without external spreadsheets.

#### Mandatory Financial Schedules
The agent must produce the following 13 schedules:
1. Capex schedule
2. Means of finance
3. Revenue build-up
4. Operating cost schedule
5. Working capital schedule
6. Depreciation schedule
7. Debt repayment schedule
8. Tax calculation schedule
9. Proforma Profit & Loss
10. Proforma Balance Sheet
11. Cash Flow Statement
12. KPI summary
13. Sensitivity tables

#### KPI Calculations
Must include:
- Project IRR
- Equity IRR
- DSCR
- Payback Period
- Break-even year
- Average gross margin
- Average PAT margin

#### Output
- `FINANCIAL_MODEL_OBJECT`

---

### Module 4 — Section Drafting Agent
#### Purpose
Generate the report chapters.

#### Process
For each section:
1. Draft Section
2. Generate Coverage Checklist
3. Check Missing Requirements
4. Repair Draft

The loop continues until one of the following is true:
- All requirements covered
- Missing inputs flagged
- Public data unavailable

#### Output per Section
- `SECTION_OUTPUT`
- `COVERAGE_CHECKLIST`
- `SOURCE_REFERENCES`

---

### Module 5 — Equipment Intelligence Agent
#### Purpose
Generate 5–6 illustrated pages describing key equipment.

#### Submodules
**Equipment Identification**
- AI identifies 12–18 key equipment items required for the production process.

**OEM Research**
For each equipment item:
- Manufacturer name
- Model or product line
- Official product page
- Technical specifications
- Output capacity
- Performance parameters

**Source Policy**
Preferred sources:
- OEM websites
- Manufacturer catalogues
- Engineering suppliers

The agent must never invent manufacturers.

#### Output
5–6 page Equipment Compendium including:
- Images
- Manufacturer links
- Technical specifications
- Performance metrics

---

### Module 6 — Final Assembly & QA Agent
#### Purpose
Assemble and validate the full feasibility report.

#### Page Allocation
| Section | Pages |
|---|---:|
| Executive Summary | 2 |
| Introduction | 6 |
| Regulatory Framework | 10 |
| Market Assessment | 16 |
| Business & Operating Model | 23 |
| Financial Feasibility | 24 |
| Risk Assessment | 6 |
| Caveats | 3 |

Total = 90 pages minimum (appendices excluded).

#### Financial Tables Allocation
Within Chapter 6:

| Table | Pages |
|---|---:|
| Assumptions | 1 |
| Capex | 1 |
| Means of Finance | 1 |
| Revenue Forecast | 2 |
| Opex | 2 |
| Debt Schedule | 2 |
| Tax | 1 |
| Depreciation | 1 |
| P&L | 1 |
| Balance Sheet | 1 |
| Cash Flow | 1 |
| KPIs | 1 |

Total = 15 pages.

#### Validation Framework
Each section must return:
- Section narrative
- Coverage checklist
- Source references

Financial model must:
- Contain all schedules
- Reconcile internally

Equipment module must:
- Include manufacturer sources
- Include valid links

Baseline module must:
- Tag assumptions
- Identify missing inputs

## 5. Non-Functional Requirements

### Report Format
- A4
- Arial 12
- Single spacing
- Paragraph spacing: 6 pt

### Quality Requirements
- Lender-grade language
- Structured headings
- Table-heavy financial section
- Deterministic financial outputs

## 6. Risks & Mitigation

| Risk | Mitigation |
|---|---|
| Incomplete sections | Checklist validation loop |
| Model inconsistency | Mandatory financial schedule schema |
| Hallucinated equipment brands | OEM source requirement |
| Missing client inputs | Baseline validation stage |
| Section duplication | Section boundary enforcement |

## 7. Success Criteria
The system succeeds when:
- A 90+ page feasibility report is generated automatically.
- All section requirements are covered or flagged.
- Financial schedules reconcile.
- Equipment specifications include real OEM references.
- No invented numeric assumptions appear.
- Bankers can evaluate the project using Chapter 6 alone.

## 8. Future Enhancements
Not included in Version 1:
- Commodity price APIs
- Regulatory license database
- Industry benchmark database
- Scenario modelling dashboard
- Investor pitch deck generator