# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) documenting key technical and architectural decisions for the AI Project Feasibility Report Agent.

## Active Decisions

| ADR | Title | Status | Date | Components |
|-----|-------|--------|------|------------|
| [ADR-0001](ADR-0001-critical-input-policy.md) | Critical Input Validation Policy | ✅ Accepted | 2026-03-04 | Input validation, Form, API |
| [ADR-0002](ADR-0002-financial-standard.md) | Financial Standard Selection | ✅ Accepted | 2026-03-04 | Financial Model Agent, Report Builder |
| [ADR-0003](ADR-0003-runtime-execution-model.md) | Runtime Execution Model | ✅ Accepted | 2026-03-04 | API, Workers, Database |

## Decision Summary

### ADR-0001: Critical Input Validation Policy
**Selected:** Option C - Configurable Threshold with Strict Default

Critical fields block generation; optional fields proceed with explicit AI assumptions. This balances PRD compliance ("critical missing inputs must stop") with reasonable UX.

**Key Interfaces:**
- `validate_critical_inputs()` in `app/main.py`
- `ValidationSummary` model in `app/models.py`

**Switch Points:**
- To strict (Option A): Expand critical field list
- To permissive (Option B): Remove blocking logic, add caveats to report

### ADR-0002: Financial Standard Selection
**Selected:** Option A - Conservative Banker Model (now), Option B (later)

Single deterministic financial model using banking industry standards for all 13 schedules and 7 KPIs. Industry-specific models deferred until after baseline validation.

**Key Interfaces:**
- `FinancialModelEngine` in `app/financial_model.py` (Sprint 2)
- Config: `FINANCIAL_STANDARD=banker_v1`

**Switch Points:**
- To industry-specific (Option B): Add industry field, implement factory pattern
- To templates (Option C): Add template selector UI + multiple calculators

### ADR-0003: Runtime Execution Model
**Selected:** Option A (now) → Option B (Sprint 4)

Start synchronous for fast delivery. Migrate to queued background jobs when report generation exceeds reasonable request timeouts (~90s).

**Key Interfaces:**
- Phase 1: Current synchronous `GET /api/report/{id}`
- Phase 2: Queue-based `POST /api/report/{id}`, `GET /api/report/status/{job_id}`, `GET /api/report/download/{job_id}`
- Abstraction: `ExecutionBackend` adapter pattern

**Switch Points:**
- Config: `EXECUTION_MODE=sync|queue`
- Trigger: When avg generation time >90s or timeout rate >5%

## Using This Directory

### Creating a New ADR
1. Copy `_template.md` to `ADR-XXXX-title.md`
2. Fill in all sections
3. Update this index
4. Link from README.md if user-facing

### Reviewing Decisions
- **Revisit conditions** in each ADR specify when to reconsider
- Quarterly review of all "Accepted" ADRs
- Update status to "Superseded" when replaced

### Switching Options
Each ADR includes:
- **Refactor Points:** Single locations to change
- **Migration Plan:** Forward and backward steps
- **Switching guide:** How to move to alternative options

## Related Documentation
- [PRD: AI Project Feasibility Report Agent](../../ai-project-report-agent-prd.md)
- [README: Project Overview](../../README.md)
- [Sprint Plan](../sprint-plan.md) (to be created)
