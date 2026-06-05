# Product Change Log

Use this log to record project progress in plain, non-technical language.

## Versioning Rule
- Start at `v1`
- Increase by 1 for each meaningful update (`v2`, `v3`, ...)
- Use one entry per update
- Keep newest entries at the top

## Change Entries

### v22 - 2026-06-05
**What We Changed**
- Three low-stakes report sections now use free open-source AI models instead of Claude, cutting Anthropic API costs by roughly 30–40%.
- Caveats and Appendices now use **Phi-4** (Microsoft's lightweight model, free via GitHub Models).
- Equipment Profiles now use **Llama 3.3 70B** (Meta's open-source model, free via GitHub Models).
- All other sections — Market Assessment, Financial Feasibility, Regulatory Framework, Risk Assessment, Business Model, Introduction, Executive Summary — still use Claude Sonnet where quality matters most.
- If no GitHub token is set, the app automatically falls back to Claude for those sections — nothing breaks.
- Each section's model can be overridden per-deployment using environment variables (e.g. `MODEL_caveats=claude` to force Claude for Caveats).

**Why**
- Caveats and Appendices are mostly standard disclaimer language and reference lists — any capable model can write these correctly. Using Claude for them is like hiring a senior consultant to write a terms-and-conditions page.
- Equipment Profiles are structured spec sheets — well-formatted structured output is something Llama 3.3 70B handles well without needing Claude's full capability.
- GitHub Models provides these models free of charge (within generous rate limits) using just a GitHub personal access token.

**How to Activate**
- Add `GITHUB_TOKEN=your_github_personal_access_token` to the `.env` file.
- A GitHub personal access token can be created at github.com → Settings → Developer settings → Personal access tokens.
- No other changes needed — the routing happens automatically.

**Model Routing Table**

| Section | Model Used | Provider | Cost |
|---|---|---|---|
| Caveats | Phi-4 | GitHub Models (Microsoft) | Free |
| Appendices | Phi-4 | GitHub Models (Microsoft) | Free |
| Equipment Profiles | Llama 3.3 70B Instruct | GitHub Models (Meta) | Free |
| Market Assessment | Claude Sonnet | Anthropic | Paid |
| Financial Feasibility | Claude Sonnet | Anthropic | Paid |
| Regulatory Framework | Claude Sonnet | Anthropic | Paid |
| Risk Assessment | Claude Sonnet | Anthropic | Paid |
| Business & Operating Model | Claude Sonnet | Anthropic | Paid |
| Introduction | Claude Sonnet | Anthropic | Paid |
| Executive Summary | Claude Sonnet | Anthropic | Paid |

**Key Decisions**
- Fallback to Claude if GitHub token is missing or the GitHub Models API fails — the report always completes, quality degrades gracefully rather than breaking.
- Each section's model is overridable via env var without touching code — useful for testing or if model quality needs tuning per deployment.

**Files Updated**
- `app/config.py` — added `SECTION_MODEL_MAP` defaults and `resolve_section_model()` method
- `app/llm_client.py` — added `_generate_github()` method and `model` parameter to `generate()`
- `app/report_builder.py` — section worker now resolves model per section and passes it through

**Risks or Follow-ups**
- GitHub Models free tier has rate limits — if many reports are generated simultaneously, GitHub Models calls may be throttled. The fallback to Claude handles this automatically.
- Phi-4 and Llama 3.3 may occasionally produce shorter or less consistently formatted output than Claude. If Caveats or Appendices quality is an issue, set `MODEL_caveats=claude` and `MODEL_appendices=claude` in `.env` to revert.
- GitHub Models availability depends on Microsoft's infrastructure — not under our control.

**Next Steps**
- Monitor output quality of Phi-4 sections in real reports and compare to Claude baseline.
- Consider routing Introduction to Llama 3.3 as well (currently kept on Claude out of caution).

---

### v21 - 2026-06-05
**What We Changed**
- Four report sections now receive real, sourced data before Claude starts writing — instead of Claude inventing everything from memory.
- The app automatically detects what type of business the submission is about (e.g. agro-processing, clean energy, textile) and pulls the right industry benchmarks for it.
- Live India macroeconomic data is fetched from the World Bank's free public API (GDP growth, inflation, industry contribution) and injected into the market assessment and risk sections.
- Current RBI (Reserve Bank of India) key interest rates are included in the financial feasibility section so Claude can reference real lending rates rather than guessing.
- Industry-specific government schemes, regulatory requirements, margins, and risks are injected into the regulatory, market, financial, and risk sections.
- Fetched data is cached for 24 hours so repeated report runs don't hit the same APIs twice.

**Why**
- Previously, all section content was generated purely from Claude's training memory — market sizes, interest rates, and regulatory details could be outdated or hallucinated. This change grounds those sections in real, citable facts.
- The `rag_context` field already existed as a placeholder in our prompt system but was hardcoded to "No reference documents available." — this update finally activates it.

**Which Sections Are Now Grounded**

| Section | What Real Data It Gets |
|---|---|
| Market Assessment | World Bank India macro indicators + industry benchmarks and growth drivers |
| Financial Feasibility | RBI policy rates and MCLR range + industry margin benchmarks |
| Regulatory Framework | Industry-specific licenses, government schemes, and regulatory highlights |
| Risk Assessment | Macro indicators + industry-specific risk factors |

**Key Decisions**
- No new API keys required — World Bank data is public and free, RBI rates are hardcoded from the official source and updated manually when rates change.
- Industry detection uses keyword matching on the business idea field — no ML model needed, no API call, instant.
- Fetch failures are handled silently — if the World Bank API is down, the section still generates normally using Claude's knowledge.
- Cached data lives in a `.data_cache/` folder (gitignored) — cleared automatically after 24 hours.

**Files Created**
- `app/data_fetchers/__init__.py` — main entry point: decides which context to fetch per section
- `app/data_fetchers/cache.py` — 24-hour file-based cache
- `app/data_fetchers/world_bank.py` — World Bank Open Data API (no key needed)
- `app/data_fetchers/rbi_rates.py` — RBI key rates (hardcoded, last verified June 2025)
- `app/data_fetchers/benchmarks.py` — static industry benchmark database covering 13 Indian industry types + keyword classifier

**Files Updated**
- `app/report_builder.py` — each section worker now fetches context before calling Claude
- `app/prompts/market_assessment.txt` — added `{rag_context}` injection point
- `app/prompts/financial_feasibility.txt` — added `{rag_context}` injection point
- `app/prompts/regulatory_framework.txt` — added `{rag_context}` injection point
- `app/prompts/risk_assessment.txt` — added `{rag_context}` injection point
- `.gitignore` — added `.data_cache/` so cached API responses are not committed

**Risks or Follow-ups**
- RBI rates are hardcoded and need a manual update when the Monetary Policy Committee changes rates (typically every 2 months). A comment in `rbi_rates.py` marks the last-verified date.
- World Bank data lags by 1-2 years — suitable for context-setting but not for citing current-year figures.
- The industry classifier uses keyword matching — unusual business ideas may fall back to "general manufacturing." Can be improved by adding more keywords to `benchmarks.py`.

**Next Steps**
- Phase 3: Route low-stakes sections (Caveats, Appendices) to free open-source models via GitHub Models API to cut Anthropic costs by ~40%.
- Extend the industry benchmark database with more niche Indian sectors as needed.

---

### v20 - 2026-06-05
**What We Changed**
- Report sections are now generated in parallel (up to 3 at a time) instead of one by one.
- The old "Round 1 / Round 2" split is removed — all 9 sections start at the same time, and the app collects them as each one finishes.
- Executive Summary still runs last so it can reference what the other sections said.
- A new setting (`PARALLEL_SECTION_WORKERS`, default 3) controls how many sections run simultaneously. This can be raised if we upgrade to a higher Anthropic API tier.

**Why**
- Sequential generation was the single biggest time cost. Running 3 sections in parallel cuts total generation time by roughly 3x — from around 2-3 minutes down to 40-60 seconds.
- The old round-split was a manual workaround for rate limits. The new parallel approach handles this automatically via a bounded worker pool — cleaner and easier to tune with one setting.

**Key Decisions**
- Max 3 workers at once (not all 9) — keeps us within Anthropic's token-per-minute limits. The limit is configurable, not hardcoded.
- Progress updates now show "X of Y sections done" since sections finish in different orders when running in parallel.

**Files Updated**
- `app/config.py` — added `PARALLEL_SECTION_WORKERS` setting
- `app/report_builder.py` — replaced sequential loop with a parallel worker block

**New Documents**
- `docs/subagent-rag-roadmap.md` — plain-language plan for the next two upgrade phases:
  - Phase 2: pull real data from World Bank, RBI, and data.gov.in so Claude writes from facts instead of memory
  - Phase 3: route low-stakes sections (Caveats, Appendices) to free open-source models via GitHub Models to cut Anthropic costs by ~40%

**Risks or Follow-ups**
- If the Anthropic API is under heavy load, parallel calls may still hit rate limits. The existing retry-with-backoff in `llm_client.py` handles this automatically.
- SQLite handles parallel writes safely because each database function opens its own connection.

**Next Steps**
- Build the Phase 2 data fetcher layer (`app/data_fetchers/`) so sections are grounded in real, current data.
- Add the Phase 3 model router so cheaper open-source models handle lower-stakes sections.
- Full plan is in `docs/subagent-rag-roadmap.md`.

---

### v19 - 2026-06-05
**What We Changed**
- Overhauled the client input form with smarter fields, better structure, and less manual work for users.

**Product Design Updates**
- Renamed "City" to "Proposed Project Site Location" with an improved autocomplete that suppresses browser address suggestions.
- Added real-time pin code validation — India uses postalpincode.in, all other countries use zippopotam.us. The system checks whether the pin code actually exists and matches the selected location, not just the format.
- Renamed "Target Customer" to "Target Customer Segment" with example-based placeholder text.
- Added 7 service-type options to the Business Model dropdown (Professional Services, Engineering Services, Education, Hospitals, Hospitality & Recreation, Government Services, R&D).
- Split the single "Target Production Capacity" text field into three structured fields — amount, unit (e.g. MT, Liters, kW), and time period (per Day, Month, Year). All three are validated and required together.
- Added a currency selector inside the budget section so users can set currency while entering budget amounts, synced with the main currency field across the form.
- Replaced the Product Mix open text field with a dynamic product list. Each product has a name, category (Base or By-Product), and ratio. By-product ratios auto-fill to reach 100% when base ratios are entered, and can be manually adjusted.
- Added a structured Material Yield / Conversion Ratio field — captures input material, quantity, and unit on one side, and output product, quantity, and unit on the other (e.g. 100 kg sugarcane → 30 L ethanol).
- Replaced the Raw Material Pricing Basis text field with a structured per-unit cost list (material name, cost, and unit per row).
- Removed Raw Material Consumption Norms, Utility Tariff Basis, Facility Type, Hazardous Materials, and Effluent Generation fields — these will be identified by AI during report generation.
- Added Allotted, Under Procurement, and Yet to be Identified options to the Land Status dropdown.
- Removed Manpower Approach, Repairs & Maintenance, Selling Overheads, Admin Overheads, Receivables Days, Inventory Days, and Payables Days fields.
- Reworked the Production Ramp-Up field — users select a preset (Conservative, Normal, Aggressive) which auto-fills Year 1, 2, 3 capacity percentages. Each year is editable, and Year 3 must reach 100%.
- Added validation for Operating Days (max 366), Shifts per Day (1–4), and Hours per Shift (1–24) with inline error messages.
- Renamed Loan Tenor to Loan Tenure. Renamed Upfront Fees to Upfront Loan Processing Charges.
- Added currency dropdowns to the Loan Amount and Upfront Charges fields, synced with the main currency selector.
- Equity percentage now auto-fills as 100% minus the Debt percentage when debt is entered.
- Removed Number of Key Equipment Items from the form — value is fixed at 14 for the backend and not shown to users.
- Removed Technology Exclusions and Preferred Manufacturer Geography.
- Added an equipment exclusion field with a dedicated toggle for "Exclude equipment sourced from China" and a free-text field for other exclusions.
- Removed the entire Non-Negotiables section (certifications, compliance constraints, ESG constraints, procurement constraints) — AI will identify these from the project context during generation.
- Promoter form redesigned: salutation and name now appear on the same row. Nature of Experience renamed to Industry of Experience with a 100-word description prompt. Loans Taken Earlier renamed to "Any loans taken earlier for any project?". "Have they been paid?" renamed to "Is any loan outstanding today?". "Any defaults?" renamed to "Any defaults so far?".
- Credit Score field now has a score type selector (CIBIL, FICO, Experian, Equifax, VantageScore) with range validation specific to each type and country.
- Phone number field now includes a country code dropdown with validation rules per country (e.g. India: 10 digits, Singapore: 8 digits).
- "Any Other Sources of Information" renamed to "Any Other Sources of Information about the Promoter" and replaced with a dynamic list — each entry is either a description or a validated URL link.
- Removed the "About the Promoter" open text field.
- Saved a product-service form split plan to docs/ for future implementation.

**Why**
- The form was collecting too many fields that users either don't know or that AI can determine automatically from the project context. The changes reduce friction, improve data quality through structured inputs, and make the form faster to complete.
- Pin code validation adds a layer of data accuracy that prevents location mismatches in the report.
- Structured fields for capacity, product mix, yield ratios, and raw material costs give the AI cleaner and more precise inputs, leading to better report quality.
- The promoter section was using confusing terminology that has now been made plain and unambiguous.

**Files/Areas Updated**
- `app/templates/form.html`
- `app/models.py`
- `docs/product-service-form-split-plan.md`

**Next Steps**
- Implement the product vs. service form split as documented in the plan (landing page → two separate forms).
- Review prompts and backend logic to take advantage of the new structured inputs (yield ratios, per-unit costs, ramp-up percentages).

---

### v18 - 2026-05-04
**What We Changed**
- Re-enabled live web research for sections marked as web.
- The report now uses web-enabled generation again for market assessment and regulatory framework, instead of silently falling back to plain generation.

**Why**
- The earlier token spike problem came from runaway multi-turn history growth, which has already been fixed. With that issue removed, live web research can be turned back on for the sections that benefit most from fresh source checking.

---

### v17 - 2026-05-04
**What We Fixed**
- Report generation was getting permanently stuck after writing all 10 sections. The "Validating source links" step was silently making hundreds of slow network requests to verify every URL in the report — taking 5–10+ minutes and sometimes never finishing.
- Removed the blocking network link-check entirely. Links are now kept as-is if they look syntactically valid (the AI-generated content already contains real URLs).
- Reduced the cooldown pause between writing batches from 90 seconds to 20 seconds (web search is disabled so the original reason for a 90s wait no longer applies).
- The cooldown now shows a live countdown ("Cooling down… 10s remaining") updating every 10 seconds so users can see it is making progress.

**Why**
- Report 17 was stuck because the link checker was blocking the entire generation thread, with no timeout guard, causing the report to appear permanently "generating" with no download ever arriving.

---

### v16 - 2026-05-04
**What We Improved**
- Fixed cases where users saw "Download failed" even though the report was generated.
- Improved progress responsiveness in the UI.

**Development Updates (Plain Language)**
- Updated report start behavior to launch generation in a detached async task instead of tying execution to the start request lifecycle.
- Added immediate queued/generating status write so status polling can see progress state right after start.
- Reduced front-end status polling interval from 6 seconds to 2 seconds so the progress bar updates faster as section status changes.

**Key Decisions and Why**
- Decision: decouple report generation from the start API response path.
- Why: avoids long-running start requests and reduces race conditions where download was attempted before backend completion state was visible.

**Files/Areas Updated**
- app/main.py
- app/templates/form.html

**Risks or Follow-ups**
- More frequent polling increases status endpoint traffic slightly.

**Next Steps**
- Add explicit front-end handling for 404 download with auto-retry and user-friendly "finalizing" state.

### v15 - 2026-05-04
**What We Improved**
- Fixed a remaining edge case where report start could still be blocked by a stuck lock with no visible progress.

**Development Updates (Plain Language)**
- Updated lock recovery logic to treat no-progress generating locks as stale fallback when lock timestamps cannot be parsed.
- This allows new report requests to proceed instead of returning repeated 409 conflicts.

**Files/Areas Updated**
- app/main.py

**Next Steps**
- Add explicit lock timestamp format normalization in database writes for stronger stale-lock detection.

### v14 - 2026-05-04
**What We Improved**
- Fixed stuck "Failed to start report generation" cases caused by stale generation locks.

**Product Design Updates**
- Kept single-active-report protection but added automatic stale-lock recovery so users are not blocked indefinitely.

**Development Updates (Plain Language)**
- Added lock metadata lookup for currently generating reports, including last update timestamp.
- Added stale lock timeout configuration (`REPORT_LOCK_STALE_SECONDS`).
- Updated start/generate APIs to auto-mark old inactive locks as failed and allow new report generation to proceed.

**Key Decisions and Why**
- Decision: auto-clear only stale locks, not active ones.
- Why: protects reliability while preventing deadlocks when jobs crash mid-run.

**Files/Areas Updated**
- app/config.py
- app/db.py
- app/main.py

**Risks or Follow-ups**
- Very long-running legitimate jobs could be marked stale if timeout is set too low.

**Next Steps**
- Surface a clear "queued / active lock" message in the front-end so users understand wait state.

### v13 - 2026-05-04
**What We Improved**
- Removed runaway multi-turn history buildup in Claude web-search generation.

**Product Design Updates**
- Changed web-search generation behavior to bounded execution so one section cannot balloon token usage through repeated conversation turns.

**Development Updates (Plain Language)**
- Replaced iterative tool loop in the Claude web path with a bounded two-call flow:
	1) one initial call,
	2) at most one follow-up call if tool use is requested.
- Removed unbounded history accumulation across repeated turns.

**Key Decisions and Why**
- Decision: cap web-search conversation depth and stop iterative accumulation.
- Why: repeated re-sending of expanded history was a major contributor to token-per-minute spikes and 429 failures.

**Files/Areas Updated**
- app/llm_client.py

**Risks or Follow-ups**
- Web-search depth is intentionally limited, so some long research responses may be shorter.

**Next Steps**
- If web-search is re-enabled broadly later, add explicit per-request token telemetry and hard request-size guards.

### v12 - 2026-05-04
**What We Improved**
- Added stricter reliability controls to reduce repeated 429 failures during report generation.

**Product Design Updates**
- Temporarily turned off live web-search tool usage to prioritize completion reliability.
- Kept section mode policy structure so web-enabled sections can be re-enabled later without redesign.

**Development Updates (Plain Language)**
- Increased round cooldown between generation batches from 65 seconds to 90 seconds.
- Reduced default token budgets per section to lower token-per-minute pressure.
- Reduced web-designated sections further so only market assessment and regulatory framework remain marked as web-mode.
- Added a hard single-active-report guard so only one report can generate at a time across the app.
- Added database helper and API checks to block overlapping report jobs with a clear 409 response.

**Key Decisions and Why**
- Decision: disable web tool calls now while keeping architecture ready.
- Why: reliability is currently more important than incremental live-source richness.
- Decision: enforce single active report run.
- Why: overlapping runs were likely spiking org-level token-per-minute usage.

**Files/Areas Updated**
- app/config.py
- app/llm_client.py
- app/db.py
- app/main.py

**Risks or Follow-ups**
- Market freshness may reduce temporarily while web-search tool usage is disabled.

**Next Steps**
- Re-enable web-search for selected sections after queue stability and TPM headroom are confirmed.
- Add explicit queued status UX in the form for better user messaging when another report is already running.

### v11 - 2026-05-03
**What We Improved**
- Reduced report generation failures caused by API token-per-minute limits.

**Product Design Updates**
- Kept live web research focused on the three freshest sections only: market assessment, regulatory framework, and equipment profiles.
- Kept other sections on standard generation to lower rate-limit pressure and improve completion reliability.

**Development Updates (Plain Language)**
- Updated section policy defaults so financial feasibility now runs in plain mode by default.
- Added automatic retry with exponential backoff for temporary rate-limit (429) errors from Claude.
- Reduced default web tool loop depth and added tighter token budgets per section mode.
- Added configurable runtime knobs for retries, token caps, and backoff timing.

**Key Decisions and Why**
- Decision: Prioritize reliable report completion over aggressive live web usage.
- Why: Fewer web-heavy calls reduces burst token usage and prevents generation from failing midway.

**Files/Areas Updated**
- app/config.py
- app/llm_client.py
- app/report_builder.py

**Risks or Follow-ups**
- Some sections may include fewer live references due to reduced web usage.

**Next Steps**
- Add queue-level concurrency controls to reduce org-wide bursts during peak usage.
- Tune retry and token settings based on production telemetry.

### v10 - 2026-05-03
**What We Improved**
- Started a safer split-generation setup to reduce API rate-limit failures during report creation.

**Product Design Updates**
- Kept web-researched generation only for sections that need fresh public data.
- Kept standard generation for narrative sections that do not need live web research.

**Development Updates (Plain Language)**
- Added section-level generation policy controls.
- Added separate plain and web generation paths in the LLM client.
- Applied default policy:
	- Web: market assessment, regulatory framework, equipment profiles, financial feasibility
	- Plain: executive summary, introduction, business & operating model, risk assessment, caveats, appendices
- Added a safety cap for web-search tool loops to prevent runaway token usage.
- Updated progress text to show section mode while generating.

**Key Decisions and Why**
- Decision: Use web search only where freshness matters most.
- Why: This reduces token-per-minute pressure and lowers 429 failures while keeping critical sections grounded.

**Files/Areas Updated**
- app/config.py
- app/llm_client.py
- app/report_builder.py

**Risks or Follow-ups**
- Cached sections from earlier runs may still reflect old behavior unless force-regenerated.

**Next Steps**
- Add retry/backoff for temporary 429 errors.
- Tune per-section token limits after observing real traffic.

### v9 - 2026-05-03
**What We Improved**
- Upgraded report output quality so generated content now appears with proper document structure and styling instead of raw formatting symbols.
- Improved generation progress visibility so users can see real section-by-section progress.
- Updated report timing messaging to reflect longer research-based generation.

**Product Design Updates**
- Added clearer chapter flow with chapter breaks and a table of contents in the generated report.
- Improved progress feedback wording so users see which section is currently being generated.
- Removed dependence on a visible state selector in the form flow and kept location autofill behavior centered on city autocomplete.

**Development Updates (Plain Language)**
- Added markdown-aware rendering so headings, bullets, and bold text from model output are converted into proper Word formatting.
- Replaced placeholder financial table rows with computed 3-year projection values derived from input budget assumptions.
- Added backend progress fields for total sections, completed sections, and current section so progress can be shown from real status updates.
- Updated report status API responses and front-end progress handling to use real backend progress instead of a purely timer-based progress animation.
- Updated default generation estimate shown to users to around 12 minutes for research-heavy runs.
- Added Claude web-search usage flow for richer and more current report content generation.

**Key Decisions and Why**
- Decision: Use real backend section status for progress updates.
- Why: This avoids misleading progress behavior and improves trust during long generation runs.
- Decision: Convert model markdown into document-native formatting.
- Why: This preserves readability and report professionalism without changing the model prompts.
- Decision: Move to research-heavy generation defaults.
- Why: Better quality and grounding requires more generation time and should be communicated clearly.

**Files/Areas Updated**
- app/report_builder.py
- app/llm_client.py
- app/db.py
- app/main.py
- app/templates/form.html

**Risks or Follow-ups**
- Real-time progress currently updates per section, not per paragraph or token.
- Financial projections are computed from assumptions and should still be validated against final client and lender inputs.

**Next Steps**
- Add lightweight tests for markdown rendering behavior and section progress API values.
- Extend progress milestones to include final assembly and file packaging steps.

### v8 - 2026-04-06
**What We Improved**
- Started implementation of the must-have governance controls and reorganized the roadmap into clear Must-have, Later, and Deferred buckets.

**Product Design Updates**
- Strengthened staged generation quality controls so important gaps are surfaced before final report output.
- Kept strict heavy controls deferred to avoid slowing down delivery.

**Development Updates (Plain Language)**
- Added a structured baseline artifact event that includes project summary, mode logic, assumptions table, and exact questions for missing inputs.
- Expanded financial readiness checks to stop generation when key financial inputs are missing and return client-ready questions.
- Added a lightweight Stage 2 model snapshot and a Chapter 6 mapping check event to catch number mismatches.
- Added equipment profile validation checks for required content signals like links, specs, and performance cues.
- Added lightweight assembly quality checks for repetition, citation gaps, and page-intent low-content warnings.
- Updated governance roadmap to separate what is implemented now, what must be done now, what comes later, and what is deferred.

**Key Decisions and Why**
- Decision: Implement lightweight validation events first instead of building a heavy deterministic engine immediately.
- Why: This gives faster trust improvements with lower rollout risk.
- Decision: Keep full semantic attribution and strict global hard-fail policy deferred.
- Why: These controls are valuable but too brittle for early rollout.

**Files/Areas Updated**
- `app/staged_pipeline.py`
- `docs/governance-integration-roadmap.md`

**Risks or Follow-ups**
- Some checks are heuristic warning checks and should be upgraded later with deterministic models.
- Chapter 6 consistency is currently monitored via mapping checks, not full table-bound computation yet.

**Next Steps**
- Add tests for baseline artifact generation, readiness blocking, Chapter 6 mapping events, and quality warnings.
- Implement deterministic financial schedules and KPI tables in the Later phase.

### v7 - 2026-04-06
**What We Improved**
- Added a practical number-provenance snapshot so key assumptions are easier to audit during staged report generation.

**Product Design Updates**
- Extended validation reporting to show how many important values are marked as unable to source.
- Added material-number provenance records to improve trust and simplify client-facing troubleshooting.

**Development Updates (Plain Language)**
- Added logic in the staged financial step to record provenance for core numeric inputs like selling price, interest rate, moratorium, operating assumptions, and financing ratios.
- Stored this provenance as validation events so it appears in existing diagnostics without adding heavy new infrastructure.
- Updated the validation report API to include a compact provenance summary and the latest unable-to-source count.

**Key Decisions and Why**
- Decision: Use existing validation-event storage for provenance snapshots first.
- Why: This delivers immediate visibility while keeping implementation light and low-risk.
- Decision: Track a focused set of material numbers instead of every numeric token.
- Why: This keeps the workflow useful now and avoids overengineering.

**Files/Areas Updated**
- `app/staged_pipeline.py`
- `app/main.py`

**Risks or Follow-ups**
- Provenance is currently captured for selected material numeric fields, not full chapter-wide numeric extraction.
- Legacy mode does not generate this staged provenance snapshot.

**Next Steps**
- Add tests for provenance event creation and validation-report aggregation.
- Expand tracked fields to include selected market and equipment quantitative claims.

### v6 - 2026-04-06
**What We Improved**
- Added a focused client review and baseline approval workflow before staged report generation.

**Product Design Updates**
- Added a dedicated assumptions review screen so clients can inspect AI defaults, source notes, and apply overrides.
- Kept the workflow simple: review -> approve -> lock baseline -> generate report.

**Development Updates (Plain Language)**
- Added backend APIs to fetch assumptions review data and confirm assumptions with overrides.
- Added database storage for assumptions review state, approvals, overrides, and locked baseline hash.
- Added a staged pipeline gate that blocks staged generation unless client review is approved.
- Added a roadmap file to track what is done now, what is useful but lighter next, and what is deferred.

**Key Decisions and Why**
- Decision: Implement a focused governance slice first instead of full heavy provenance automation.
- Why: This protects trust-critical behavior quickly while avoiding early overengineering.
- Decision: Keep deferred items explicitly documented for traceability.
- Why: This prevents scope drift and makes future upgrades deliberate.

**Files/Areas Updated**
- `app/models.py`
- `app/db.py`
- `app/main.py`
- `app/staged_pipeline.py`
- `app/config.py`
- `app/templates/assumptions_review.html`
- `docs/governance-integration-roadmap.md`

**Risks or Follow-ups**
- Number-by-number provenance logging is not fully automated yet across all chapters.
- Review screen is currently lightweight and can be linked more tightly into post-submit UX.

**Next Steps**
- Add material-number provenance logging for Chapter 6 and key market/equipment figures.
- Add tests for review-gate enforcement and override propagation.
- Expand diagnostics to report counts of unable-to-source values.

### v5 - 2026-04-06
**What We Improved**
- Started implementation of a safer staged report generation flow so failures are easier to identify and fix.

**Product Design Updates**
- Added stage-level tracking for report generation (baseline, financial, assembly).
- Added new diagnostics endpoints so you can inspect stage progress and validation events.
- Added a practical failure runbook for faster troubleshooting.

**Development Updates (Plain Language)**
- Introduced a feature-flag controlled staged pipeline that can run without removing the current legacy flow.
- Added baseline lock storage and stage checkpoint storage in the database.
- Added validation event logging for sourcing checks and financial input checks.
- Added mode consistency support to avoid mixed legacy/staged behavior for the same submission.

**Key Decisions and Why**
- Decision: Keep staged rollout behind flags with optional legacy fallback.
- Why: This reduces risk while implementation is still evolving.
- Decision: Use hard stops only for integrity-critical failures and soft warnings for recoverable quality issues.
- Why: This protects output quality without making generation too brittle.

**Files/Areas Updated**
- `app/config.py`
- `app/staged_pipeline.py`
- `app/execution_backend.py`
- `app/sourcing_validator.py`
- `app/db.py`
- `app/main.py`
- `docs/failure-runbook.md`

**Risks or Follow-ups**
- Stage-level telemetry is in place, but deeper structured logging and metric dashboards are still pending.
- Sourcing checks are currently focused on the financial section first; broader chapter checks can be added next.

**Next Steps**
- Add structured request/stage correlation IDs in logs.
- Add tests for baseline lock integrity, stage transitions, and sourcing retry behavior.
- Expand sourcing validation to additional quantitative chapters.

### v4 - 2026-04-06
**What We Improved**
- Made the report output rules editable from one markdown file and applied them throughout report generation.

**Product Design Updates**
- Locked the report structure to Chapters 1 to 8 with clear page targets.
- Added explicit handling for the Chapter 5 equipment-profile requirement and Chapter 6 financial-table requirement.
- Kept appendices separate from the main 90-page target.

**Development Updates (Plain Language)**
- Added a central output specification file so future changes can be made quickly without digging through code.
- Updated report generation to always create all required chapters in order.
- Applied the required document style defaults (A4-compatible layout intent, Arial 12, single spacing, 6 pt paragraph spacing).
- Added a built-in financial table pack to ensure Chapter 6 includes 15 tables for the required table-heavy section.

**Key Decisions and Why**
- Decision: Use one editable markdown file as the source of truth for output requirements.
- Why: This makes updates faster and reduces mismatch between prompts and generated report structure.
- Decision: Generate missing chapters through dedicated prompts rather than fixed boilerplate.
- Why: This improves consistency while keeping report content adaptable to each submission.

**Files/Areas Updated**
- `docs/report-output-specification.md`
- `app/prompt_renderer.py`
- `app/report_builder.py`
- `app/prompts/executive_summary.txt`
- `app/prompts/market_assessment.txt`
- `app/prompts/risk_assessment.txt`
- `app/prompts/introduction.txt`
- `app/prompts/regulatory_framework.txt`
- `app/prompts/business_operating_model.txt`
- `app/prompts/equipment_profiles.txt`
- `app/prompts/financial_feasibility.txt`
- `app/prompts/caveats.txt`
- `app/prompts/appendices.txt`

**Risks or Follow-ups**
- Actual page count still depends on final model output length and may need one content expansion pass for strict page-level compliance in every run.
- Equipment illustrations are currently link-based references and may later be upgraded to embedded images.

**Next Steps**
- Run one full sample report generation and verify chapter length balance against the 90-page target.
- If needed, tune chapter prompts further to tighten per-section page adherence.

### v3 - 2026-03-25
**What We Improved**
- Changed two-choice dropdown questions to radio buttons so users can answer faster with fewer clicks.

**Product Design Updates**
- Replaced binary dropdowns with clear Yes/No or Option A/Option B radio choices in the client form.
- Kept all existing logic and required checks intact after the UI change.

**Development Updates (Plain Language)**
- Updated the form behavior code to read and set radio values correctly.
- Adjusted autofill logic so example data still works with the new input style.

**Key Decisions and Why**
- Decision: Use radio buttons for all two-option selections.
- Why: It improves speed, clarity, and reduces input friction for users.

**Files/Areas Updated**
- `app/templates/form.html`

**Risks or Follow-ups**
- Frontend-only lint warnings may still appear for server template expressions in HTML editors, but runtime behavior is unchanged.

**Next Steps**
- Do one quick UI pass in the browser to confirm all converted fields behave correctly on submit and autofill.

### v2 - 2026-03-25
**What We Improved**
- Expanded the client input form so key project details can be captured up front without guesswork.

**Product Design Updates**
- Added structured inputs for project profile, budget method, commercial assumptions, financing details, compliance flags, and equipment preferences.
- Kept optional fields where flexibility is needed and used clear dropdowns for critical yes/no and mode choices.

**Development Updates (Plain Language)**
- Connected all new form fields to the data sent to the backend.
- Added server-side checks so required combinations are enforced, especially for budget mode and DSRA inputs.
- Updated defaults and conditional form behavior so users can provide complete data with fewer mistakes.

**Key Decisions and Why**
- Decision: Use dropdowns and typed numeric fields for mandatory decision points.
- Why: This improves consistency and gives cleaner inputs for AI report generation.
- Decision: Allow default-driven assumptions while still enabling manual overrides.
- Why: This balances speed with user control and supports better report quality.

**Files/Areas Updated**
- `app/templates/form.html`
- `app/models.py`

**Risks or Follow-ups**
- Existing saved submissions may not include newly added fields, so older records should be handled carefully if reused.

**Next Steps**
- Validate the full submit and report flow with one capacity-driven case and one budget-driven case.

### v1 - 2026-03-25
**What We Improved**
- Created a repeatable way to capture product progress in simple language.

**Product Design Updates**
- Added a clear structure so updates are easy for non-technical stakeholders to read.

**Development Updates (Plain Language)**
- Set up a reusable workflow that adds one versioned entry each time this process is run.

**Key Decisions and Why**
- Decision: Keep one shared markdown file for all updates.
- Why: This makes project history easy to find and review in one place.
- Decision: Use simple headings for each entry.
- Why: Readers can quickly scan what changed and why.

**Files/Areas Updated**
- `.github/skills/product-change-journal/SKILL.md`
- `.github/skills/product-change-journal/assets/log-template.md`
- `docs/product-change-log.md`

**Risks or Follow-ups**
- Future entries may drift into technical wording if not reviewed for clarity.

**Next Steps**
- Use this skill after each meaningful design or development change.
