# Governance Integration Roadmap

This file tracks which governance steps are completed, what must be done now, what is planned for later, and what is intentionally deferred.

## Already Implemented
- Added assumptions review APIs so clients can inspect AI defaults and source notes before final generation.
- Added client approval + override endpoint to lock baseline values.
- Added staged pipeline gate: final staged report generation now requires approved client review when enabled.
- Added a lightweight review screen template for approval workflow.
- Added material-number provenance logging for key financial and operating fields.
- Added validation report summary for provenance and unable-to-source count.

## Must-have Now (In Progress)
- Stage 1 baseline artifact hardening:
  - save a structured baseline artifact with project summary, sizing basis, assumptions table, and exact missing-input questions.
- Stage 2 readiness controls:
  - hard-stop when required financial inputs are missing, with exact questions returned.
  - persist a lightweight financial model snapshot for traceability.
- Stage 3 Chapter 6 consistency guardrail:
  - run model-to-chapter mapping checks and log mismatches as validation events.
- Stage 4 equipment governance minimum:
  - enforce required profile elements (OEM/product link, image link, technical/performance cues, brand/manufacturer cues).
- Stage 5 lightweight quality checks:
  - add warnings for repetition, citation gaps for quantitative claims, and page-intent low content.

## Later (After Must-have Stabilizes)
- Deterministic financial model engine with canonical schedules and KPIs:
  - capex, drawdown, revenue, opex split, working capital, depreciation, debt, tax,
  - proforma P&L, balance sheet, cash flow, IRR/DSCR/payback/breakeven,
  - sensitivity tables from client-selected toggles.
- Explicit equipment sub-stage orchestration:
  - 4A shortlist, 4B web profile enrichment, 4C final non-duplicative write-up.
- Final-format expansion:
  - add PDF output with DOCX/PDF parity checks.

## Deferred Steps (Intentional)
- Full semantic attribution for every numeric token across all chapters.
- Hard-fail policy for all uncited numbers, including low-impact narrative numbers.
- Deep frontend redesign of the entire form flow around review state.
- Cross-version migration framework for historical assumptions-review schemas.

## Why Deferred
- These items add complexity and brittleness early.
- Current focus is trust-critical controls first (review gate, lock, traceability, and lightweight quality checks).
- Deferred items can be added after observing real failure patterns in production.
