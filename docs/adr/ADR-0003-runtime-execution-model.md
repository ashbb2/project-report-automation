# ADR-0003: Runtime Execution Model

**Status:** Accepted  
**Date:** 2026-03-04  
**Decision Owner:** Engineering  
**Affected Components:** API endpoints, Report generation, Database, Worker processes

## Context
The PRD requires generating 90+ page reports with multiple AI-driven sections, financial modeling, and equipment research. Current MVP uses synchronous request-response model. As report complexity grows (6 modules, staged prompts, validation loops), we need to decide on the execution model to handle long-running operations reliably.

## Decision
**Selected Option:** A Now, B Soon

Start with synchronous execution (Option A) for immediate delivery and controlled rollout. Migrate to queued background jobs (Option B) in next release when latency becomes problematic.

**Current (Sprint 1-2):** Synchronous API (Option A)  
**Next (Sprint 4):** Queued Background Jobs (Option B)

## Options Considered

### Option A: Synchronous API Now (SELECTED - PHASE 1)
**Description:** Keep current synchronous request-response model where `/api/report/{id}` blocks until report is generated and returns document.

**Pros:**
- Minimal code changes
- No infrastructure additions
- Simple debugging
- Fastest immediate delivery
- Easier testing

**Cons:**
- Request timeout risk (Heroku ~30s, may need increase)
- Poor UX for long operations (>2 min)
- No retry mechanism
- Single failure point
- Doesn't scale to 90+ page reports with full modules

**Implementation Effort:** Low (already implemented)  
**Operational Risk:** Medium-High  
**PRD Alignment:** Medium

### Option B: Queued Background Jobs Soon (SELECTED - PHASE 2)
**Description:** Accept report generation requests immediately, queue for background processing, provide status polling endpoint. User gets job ID instantly, polls for completion, downloads when ready.

**Pros:**
- Handles arbitrarily long operations
- Better user experience (no hanging)
- Retry/idempotency support
- Status visibility
- Scales horizontally
- Matches PRD complexity requirements

**Cons:**
- Requires queue infrastructure (Redis/PostgreSQL LISTEN)
- Worker process management
- More complex error handling
- Status polling UI needed

**Implementation Effort:** Medium  
**Operational Risk:** Low-Medium  
**PRD Alignment:** High

### Option C: Immediate Async Migration
**Description:** Full async/await refactor of all generation logic with concurrent execution of independent modules.

**Pros:**
- Modern architecture
- Better resource utilization
- Concurrent module execution

**Cons:**
- Large refactor now
- Doesn't solve long-running problem (still need queue)
- Premature optimization
- Higher immediate risk

**Implementation Effort:** High  
**Operational Risk:** Medium-High  
**PRD Alignment:** Medium

## Decision Drivers
1. **Immediate Delivery:** Need working solution quickly (Option A)
2. **Future Scalability:** Will need long-running support (Option B)
3. **Pragmatism:** Don't refactor until necessary (defer Option C)
4. **User Experience:** Acceptable now, must improve later
5. **PRD Requirements:** Full 6-module generation requires async (Option B)

## Interfaces Impacted

### Phase 1 (Option A - Current)
- **APIs:**
  - `GET /api/report/{id}` - synchronous, blocks until complete
  - No changes needed
- **Database:**
  - Current `submissions` and `report_sections` tables sufficient
- **Configuration:**
  - `REQUEST_TIMEOUT` - may need to increase

### Phase 2 (Option B - Sprint 4)
- **APIs (New/Modified):**
  - `POST /api/report/{id}` - accepts request, returns job_id immediately
  - `GET /api/report/status/{job_id}` - polls generation status
  - `GET /api/report/download/{job_id}` - downloads completed report
- **Database (New Tables):**
  - `generation_jobs` (job_id, submission_id, status, started_at, completed_at, error)
  - `job_events` (job_id, stage, status, timestamp) - for progress tracking
- **Configuration:**
  - `CELERY_BROKER_URL` or `QUEUE_TYPE=postgres`
  - `WORKER_CONCURRENCY=2`
- **Infrastructure:**
  - Worker dyno in Procfile: `worker: celery -A app.tasks worker`
  - Redis addon (or use PostgreSQL LISTEN/NOTIFY)

## Refactor Points

### Phase 1 (No Refactor Needed)
Current endpoint stays as-is:
```python
@app.get("/api/report/{submission_id}")
async def generate_report(submission_id: int):
    doc_bytes = build_doc(submission_data, submission_id)
    return StreamingResponse(...)
```

### Phase 2 (Queue Integration)
**Abstraction point:** Execution backend adapter

```python
# app/execution_backend.py
class ExecutionBackend:
    def submit_job(self, submission_id: int) -> str:
        """Submit report generation job, return job_id"""
        pass
    
    def get_status(self, job_id: str) -> JobStatus:
        """Get job status"""
        pass

class SyncBackend(ExecutionBackend):
    """Option A: Execute immediately"""
    def submit_job(self, submission_id):
        doc_bytes = build_doc(...)
        # Store in temp location, return id
        
class QueueBackend(ExecutionBackend):
    """Option B: Submit to queue"""
    def submit_job(self, submission_id):
        task = generate_report_task.delay(submission_id)
        return task.id
```

**Configuration switch:**
```python
# app/config.py
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "sync")  # sync | queue

def get_backend():
    if EXECUTION_MODE == "queue":
        return QueueBackend()
    return SyncBackend()
```

## Migration Plan

### Phase 1: Implement Option A (Current - Sprint 1-2)
1. ✅ Keep synchronous endpoint
2. Monitor average report generation time
3. Set alert if >90s average
4. Document timeout limitations in README

### Phase 2: Migrate to Option B (Sprint 4)
1. Add `generation_jobs` and `job_events` tables
2. Install Celery + Redis (or use PostgreSQL queue)
3. Create `app/tasks.py` with `generate_report_task()`
4. Add new status/download endpoints
5. Update frontend for polling UI
6. Deploy worker dyno
7. Feature flag: `USE_QUEUE=true` to enable
8. Parallel run old+new for 1 week
9. Deprecate synchronous endpoint

### Backward Migration (B→A if needed)
1. Set `USE_QUEUE=false`
2. Route requests to sync backend
3. Keep queue infrastructure for rollback
4. Remove after 30 days if stable

### Switching Between Options

**A → B (Sync to Queue):**
- Effort: 1 week (3-4 days dev, 2-3 days testing)
- Changes: API layer, worker setup, frontend polling
- Trigger: When avg generation time >90s or timeout rate >5%

**B → C (Queue to Async):**
- Effort: 2-3 weeks
- Changes: Internal concurrency within worker tasks
- Trigger: When processing multiple sections sequentially is bottleneck
- Note: Option C complements Option B, not replacement

## Consequences

### Phase 1 (Option A)
**Positive:**
- Fast delivery
- Simple deployment
- Easy debugging

**Negative:**
- Will timeout on full PRD reports
- Poor UX for long operations
- Cannot support 90+ page reports reliably

**Neutral:**
- Known temporary solution
- Clear migration path

### Phase 2 (Option B)
**Positive:**
- Handles any report length
- Better UX (instant response)
- Retry support
- Status visibility
- PRD-compliant

**Negative:**
- More moving parts
- Queue infrastructure needed
- Slightly more complex debugging

**Neutral:**
- Industry-standard pattern
- Well-understood trade-offs

## Revisit Conditions

### Trigger Migration to Phase 2 (A → B) if:
- Average report generation time >90 seconds
- Timeout error rate >5%
- User complaints about hanging requests
- Full Module 4-6 implementation underway
- **Target: Sprint 4 (~ weeks from now)**

### Consider Option C if:
- Queue worker CPU utilization <50% (indicates parallelism opportunity)
- Multiple independent modules wait sequentially
- After Phase 2 stable for 2+ months

### Rollback to Phase 1 if:
- Queue infrastructure failures >10% rate
- Worker deployment issues
- Within first 2 weeks of Phase 2 deployment

## Related Decisions
- ADR-0001: Critical Input Policy (validation must be fast, stays sync)
- ADR-0002: Financial Standard (calculations may be slow, needs queue)
- Future: ADR for job prioritization and rate limiting

## References
- [PRD Section: Non-Functional Requirements](../ai-project-report-agent-prd.md#5-non-functional-requirements)
- Heroku request timeout docs: https://devcenter.heroku.com/articles/request-timeout
- Celery best practices: https://docs.celeryq.dev/
- Implementation plan: Sprint 4 tasks
