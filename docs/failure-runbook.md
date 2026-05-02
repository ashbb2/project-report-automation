# Failure Runbook

Use this table to quickly diagnose report generation issues after staged pipeline rollout.

| Error Signal | Likely Cause | First Check | Immediate Action | Severity |
|---|---|---|---|---|
| `baseline_immutability_violation` | Locked assumptions changed after baseline lock | Check `baseline_locks.baseline_hash` and latest stage checkpoint hash | Stop pipeline, restore approved baseline, rerun from financial stage | Hard stop |
| `Missing required financial inputs` | Computation-critical fields are missing | Validation events for stage `financial` | Request missing fields from user, then rerun report | Hard stop |
| `sourcing_validation` failed repeatedly | Quantitative claim has no citation or fallback phrase | Validation events for stage `financial` and latest generated section text | Retry generation; if retries exhausted, keep fallback phrase and continue | Soft fail |
| `stage status = failed` on `assembly` | Exception during final build or document write | `stage_checkpoints` for `assembly` and app logs | Regenerate report; if repeat failure, switch to legacy mode temporarily | Hard stop |
| Empty/very small output size | Incomplete output generation | `stage_checkpoints.output_size` and output hash | Force regenerate with `force=true` | Hard stop |
| Mode mismatch (`staged` vs `legacy`) | Submission executed with different generation path later | `submissions.execution_mode` | Keep same mode for that submission; do not mix modes | Hard stop |
| High duplication warning between chapters | Prompt overlap or missing bridge sentence control | Compare chapter outputs around repeated content | Regenerate affected chapter with chapter-specific prompt emphasis | Soft fail |
| Baseline exists but no checkpoints | Stage orchestration was bypassed | `/api/report/{id}/stage-status` output | Trigger staged report generation again | Hard stop |
| Financial stage keeps timing out | LLM/network transient issue | App logs + checkpoint attempt count | Retry once; if persistent, temporarily switch to legacy mode | Soft fail |

## Operator Notes
- Hard stop means do not proceed to final report delivery until fixed.
- Soft fail means report can proceed with warnings documented in caveats.
- Use these APIs during triage:
  - `GET /api/report/{submission_id}/stage-status`
  - `GET /api/report/{submission_id}/validation-report`
