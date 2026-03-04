# ADR-XXXX: [Title]

**Status:** [Proposed | Accepted | Superseded | Deprecated]  
**Date:** YYYY-MM-DD  
**Decision Owner:** [Name/Role]  
**Affected Components:** [List of components]

## Context
[What is the issue we're seeing that is motivating this decision or change?]

## Decision
**Selected Option:** [A | B | C]

[What is the change that we're proposing and/or doing?]

## Options Considered

### Option A: [Title]
**Description:** [Brief description]

**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

**Implementation Effort:** [Low | Medium | High]  
**Operational Risk:** [Low | Medium | High]  
**PRD Alignment:** [Low | Medium | High]

### Option B: [Title]
[Same structure as Option A]

### Option C: [Title]
[Same structure as Option A]

## Decision Drivers
- [Driver 1: e.g., compliance requirements]
- [Driver 2: e.g., time to market]
- [Driver 3: e.g., cost optimization]

## Interfaces Impacted
- **APIs:** [List affected endpoints]
- **Database Schema:** [List affected tables]
- **Configuration:** [List affected config keys]
- **Dependencies:** [List affected external services]

## Refactor Points
[Single seam locations that enable switching options later]
- **Interface/Adapter:** [Path to file, function/class name]
- **Configuration Keys:** [Environment variables or config that control behavior]
- **Feature Flags:** [If applicable]

## Migration Plan

### Forward Migration (Implementing this decision)
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Backward Migration (Rolling back if needed)
1. [Step 1]
2. [Step 2]

### Switching to Alternative Option
**To switch from current to [Option X]:**
- [Specific changes needed]
- [Configuration updates]
- [Estimated effort]

## Consequences

### Positive
- [Positive consequence 1]
- [Positive consequence 2]

### Negative
- [Negative consequence 1]
- [Negative consequence 2]

### Neutral
- [Neutral consequence 1]

## Revisit Conditions
- [Condition 1 that would trigger reconsideration]
- [Condition 2 that would trigger reconsideration]

## Related Decisions
- [ADR-XXXX: Related decision title]

## References
- [Link to PRD section]
- [Link to technical documentation]
- [Link to discussion/issue]
