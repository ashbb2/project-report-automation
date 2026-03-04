# ADR-0001: Critical Input Validation Policy

**Status:** Accepted  
**Date:** 2026-03-04  
**Decision Owner:** Product/Engineering  
**Affected Components:** Frontend form, Backend API, Database schema, Validation logic

## Context
The PRD requires a systematic approach to handling missing inputs to prevent silent assumptions and ensure lender-grade report quality. Module 2 specifies that "critical missing inputs must stop the process." We need to decide how strictly to enforce input requirements while balancing user experience and report quality.

## Decision
**Selected Option:** C - Configurable Threshold with Strict Default

We will classify all inputs as either **critical** or **optional**. Critical fields block report generation if missing. Optional fields allow generation with explicit caveats and AI-default assumptions that are clearly tagged.

## Options Considered

### Option A: Strict Blocking
**Description:** All PRD-required fields must be provided. Report generation is blocked if any required field is missing.

**Pros:**
- Highest data quality and compliance
- No silent assumptions
- Matches PRD requirement: "critical missing inputs must stop the process"
- Simplest validation logic

**Cons:**
- Higher user friction
- More form abandonment
- Slower time to first value
- May block users who want partial/draft reports

**Implementation Effort:** Low-Medium  
**Operational Risk:** Low  
**PRD Alignment:** High

### Option B: Partial Generation with Caveats
**Description:** Allow report generation even with missing critical fields, but include prominent warnings and caveats throughout the document.

**Pros:**
- Better completion rate
- Faster user feedback
- Lower abandonment
- Allows iterative refinement

**Cons:**
- Conflicts with PRD "no silent assumptions" requirement
- Risk of incomplete reports being used for actual financing
- Harder to distinguish draft vs final quality
- Lower lender trust

**Implementation Effort:** Low  
**Operational Risk:** Medium-High  
**PRD Alignment:** Low-Medium

### Option C: Configurable Threshold (SELECTED)
**Description:** Maintain a classification map of critical vs optional fields. Block generation only when critical fields are missing. For optional fields, proceed with AI-default assumptions that are explicitly documented.

**Pros:**
- Balances quality and UX
- Aligns with PRD staged approach
- Supports phased rollout (start strict, relax for non-criticals)
- Clear separation of concerns
- Explicit assumption tracking

**Cons:**
- Requires policy configuration
- More complex validation logic
- Need to maintain field classification

**Implementation Effort:** Medium  
**Operational Risk:** Medium  
**PRD Alignment:** High

## Decision Drivers
1. **Compliance:** PRD explicitly requires blocking on critical missing inputs
2. **User Experience:** Need reasonable completion rates
3. **Transparency:** All assumptions must be tagged and traceable
4. **Flexibility:** Support future relaxation of constraints without code changes

## Interfaces Impacted
- **APIs:** 
  - `POST /api/submit` - returns validation summary
  - Response includes `ValidationSummary` with critical_missing, optional_missing, assumptions_used
- **Database Schema:**
  - Submissions table stores all inputs including null optionals
  - No schema changes needed (JSON flexible)
- **Configuration:**
  - `CRITICAL_FIELDS` list in validation module
  - `OPTIONAL_FIELDS` list in validation module
- **Frontend:**
  - Field labels marked with `class="critical"` or `class="optional"`
  - Client-side validation before submit

## Refactor Points
**Single validation interface:** `app/main.py:validate_critical_inputs()`
- Input: `SubmissionCreate` object
- Output: `ValidationSummary` object
- To switch policies: modify logic in this single function

**Field classification:**
- Location: `app/main.py:validate_critical_inputs()` 
- To reclassify fields: update conditionals in validation function
- Future: extract to config file `config/field_policy.yaml`

**Policy enforcement point:** `app/main.py:submit_form()`
- Currently raises 400 if `critical_missing` is non-empty
- To switch to Option B: remove the HTTPException raise
- To switch to Option A: add all PRD fields to critical list

## Migration Plan

### Forward Migration (Implementing Option C)
1. ✅ Define `ValidationSummary` model in `app/models.py`
2. ✅ Implement `validate_critical_inputs()` in `app/main.py`
3. ✅ Update `submit_form()` to call validation and block on critical missing
4. ✅ Update frontend to display validation summary
5. ✅ Mark form fields with critical/optional indicators

### Backward Migration (Reverting to no validation)
1. Remove validation call from `submit_form()`
2. Remove `ValidationSummary` from response model
3. Remove critical/optional CSS classes from form

### Switching to Alternative Option

**To switch to Option A (Strict Blocking):**
- Change: Add all PRD Module 1 fields to critical check in `validate_critical_inputs()`
- Config: Set `STRICT_MODE=true` environment variable
- Effort: 1-2 hours

**To switch to Option B (Permissive with Caveats):**
- Change: Remove `if validation_summary.critical_missing: raise HTTPException` in `submit_form()`
- Change: Pass `validation_summary` to report builder to include caveats in document
- Config: Set `PERMISSIVE_MODE=true` environment variable
- Effort: 4-6 hours (includes report builder changes)

## Consequences

### Positive
- Clear user feedback on what's missing before generation
- Explicit tracking of all AI assumptions
- Maintains report quality for lender-grade use
- Flexible for future policy changes

### Negative
- Some legitimate use cases may be blocked (e.g., early-stage feasibility checks)
- Requires maintaining field classification list
- More complex validation logic than all-or-nothing

### Neutral
- Validation logic is centralized in one function
- Classification can be externalized to config later

## Revisit Conditions
- If form abandonment rate exceeds 40% → consider relaxing critical field list
- If reports with missing optionals are flagged by lenders → tighten assumptions
- If users request "draft mode" → implement Option B as secondary mode
- After 3 months: review which optional fields are rarely provided → consider removing from form

## Related Decisions
- ADR-0002: Financial Standard Selection
- ADR-0003: Runtime Execution Model
- Future: ADR for user roles and permissions (admin override for validation)

## References
- [PRD Module 2: Baseline & Assumption Lock Agent](../ai-project-report-agent-prd.md#module-2--baseline--assumption-lock-agent)
- [Implementation: app/main.py validate_critical_inputs()](../../app/main.py)
- [Implementation: app/models.py ValidationSummary](../../app/models.py)
