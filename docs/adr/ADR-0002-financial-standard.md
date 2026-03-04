# ADR-0002: Financial Standard Selection

**Status:** Accepted  
**Date:** 2026-03-04  
**Decision Owner:** Product/Engineering  
**Affected Components:** Financial Model Agent (Module 3), Report Builder, Financial schedules generation

## Context
The PRD requires generating 13 mandatory financial schedules with KPI calculations (IRR, DSCR, payback, etc.) for lender-grade feasibility reports. We need to decide the modeling approach: conservative banker-standard formulas vs industry-specific models vs user-selectable templates.

## Decision
**Selected Option:** A - Conservative Banker Model (Now)

Implement a single, deterministic financial model using conservative banking industry standards. This provides a stable, auditable baseline for all reports. Industry-specific enhancements deferred to later phase.

## Options Considered

### Option A: Conservative Banker Model (SELECTED)
**Description:** Single standardized financial model using conservative assumptions and banking industry conventions. Deterministic formulas for all 13 schedules and 7 KPIs.

**Pros:**
- Simpler implementation and testing
- Auditable and explainable
- Lender-friendly (matches banker expectations)
- Lower risk of errors
- Deterministic outputs
- Fastest time to market

**Cons:**
- Less accurate for sector-specific nuances
- May underestimate revenue in optimistic scenarios
- One-size-fits-all approach
- Limited flexibility

**Implementation Effort:** Medium  
**Operational Risk:** Low  
**PRD Alignment:** High

### Option B: Industry-Specific Formulas
**Description:** Multiple financial models tailored to different industries (manufacturing, services, retail, etc.) with sector-specific assumptions and benchmarks.

**Pros:**
- Higher realism and accuracy
- Better credibility with sector experts
- More competitive reports
- Captures industry dynamics

**Cons:**
- Complex data dependencies
- Heavy validation burden
- Model drift risk
- Requires industry expertise
- Higher maintenance cost
- Longer development time

**Implementation Effort:** High  
**Operational Risk:** High  
**PRD Alignment:** High

### Option C: User-Selectable Templates
**Description:** Multiple template options (conservative, moderate, aggressive) that users can select based on their risk appetite and industry.

**Pros:**
- Maximum flexibility
- Supports multiple use cases
- Better GTM positioning
- User empowerment

**Cons:**
- Template proliferation
- Risk of user misuse (selecting wrong template)
- Complex testing matrix
- Heavier support burden
- Inconsistent outputs

**Implementation Effort:** Medium-High  
**Operational Risk:** Medium  
**PRD Alignment:** Medium-High

## Decision Drivers
1. **Time to Market:** Need functional financial engine quickly
2. **Auditability:** Lenders need consistent, explainable calculations
3. **Quality:** Conservative approach reduces risk of overstatement
4. **Simplicity:** Current MVP has no financial engine; start simple
5. **PRD Compliance:** Must produce all 13 schedules deterministically

## Interfaces Impacted
- **APIs:**
  - Financial calculations encapsulated in `FinancialModelEngine` class
  - Input: submission data dict
  - Output: `FinancialModelObject` with all 13 schedules
- **Database Schema:**
  - New table: `financial_models` (to be created in Sprint 2)
  - Stores JSON output of each schedule
  - Version field for future model evolution
- **Configuration:**
  - `FINANCIAL_MODEL_VERSION = "banker_v1"`
  - Conservative assumptions (e.g., tax rate, depreciation method)
- **Dependencies:**
  - May add `numpy-financial` for IRR calculations

## Refactor Points
**Single financial engine interface:**
```python
class FinancialModelEngine:
    def __init__(self, standard: str = "banker_v1"):
        self.standard = standard
    
    def generate_model(self, inputs: dict) -> FinancialModelObject:
        # Load standard-specific calculator
        calculator = self._get_calculator(self.standard)
        return calculator.compute_all_schedules(inputs)
```

**Location:** `app/financial_model.py` (to be created)

**Switching mechanism:**
- Standard selection via config: `FINANCIAL_STANDARD=banker_v1|industry_manufacturing|industry_services`
- Factory pattern returns appropriate calculator class
- All calculators implement common interface

## Migration Plan

### Forward Migration (Implementing Option A)
1. Create `app/financial_model.py` module
2. Implement banker-standard formulas for all 13 schedules:
   - Capex, Means of Finance, Revenue, Opex, Working Capital
   - Depreciation, Debt Repayment, Tax, P&L, Balance Sheet
   - Cash Flow, KPIs, Sensitivity
3. Add reconciliation checks (balance sheet balance, cash flow tie-out)
4. Create `financial_models` database table
5. Integrate into report builder for Chapter 6
6. Add unit tests with golden fixtures

### Backward Migration (Reverting)
- Not applicable (no financial engine exists currently)
- To disable: skip financial chapter generation

### Switching to Alternative Option

**To add Option B (Industry-Specific) later:**
1. Create `app/financial_model_manufacturing.py`, etc.
2. Add `industry` field to submission form
3. Update engine factory to select calculator by industry
4. Maintain banker model as fallback
5. Estimated effort: 3-4 weeks per industry

**To add Option C (User Templates) later:**
1. Add `financial_template` field to submission form
2. Create template-specific calculators (conservative/moderate/aggressive)
3. Update engine factory
4. Add template selection UI
5. Estimated effort: 2-3 weeks

## Consequences

### Positive
- Fast delivery of working financial engine
- Consistent outputs across all projects
- Easy to audit and validate
- Reduces risk of financial errors
- Meets PRD requirements fully

### Negative
- May not capture industry-specific dynamics optimally
- Less competitive in specialized sectors
- Users cannot adjust risk profile
- Single point of failure if formulas are wrong

### Neutral
- Sets baseline for future enhancements
- Establishes testing and validation framework
- Creates architecture for multiple models later

## Revisit Conditions
- **After 50 reports generated:** Analyze lender feedback on financial assumptions
- **If >20% of users request industry models:** Prioritize Option B development
- **If financial errors found:** Immediate fix in banker model + consider external audit
- **Q3 2026:** Evaluate adding top 2-3 industry-specific models based on usage data

## Related Decisions
- ADR-0001: Critical Input Policy (provides inputs to financial model)
- ADR-0003: Runtime Execution Model (impacts calculation performance)
- Future: ADR for financial model versioning strategy

## References
- [PRD Module 3: Financial Model Agent](../ai-project-report-agent-prd.md#module-3--financial-model-agent)
- Banking industry standard IRR/DSCR calculation methods
- Indian banking norms for project financing (if applicable)
- Future implementation: `app/financial_model.py` (Sprint 2)
