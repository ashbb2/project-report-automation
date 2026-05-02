# Product Change Log

Use this log to record project progress in plain, non-technical language.

## Versioning Rule
- Start at `v1`
- Increase by 1 for each meaningful update (`v2`, `v3`, ...)
- Use one entry per update
- Keep newest entries at the top

## Change Entries

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
