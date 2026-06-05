# Subagent & RAG Upgrade Roadmap

This document explains the three-phase plan to make report generation faster, smarter, and more grounded in real data — in plain language.

---

## What We're Solving

Right now, every section of the report is written by Claude **from memory** — it uses general knowledge to invent market sizes, regulatory details, and equipment prices. This means:

- Numbers can be made up (hallucinated)
- Generation is slow because sections run one-by-one
- Every section costs the same, even "lightweight" ones like Caveats

The three phases below fix each problem in turn.

---

## Phase 1 — Parallel Section Generation ✅ Done (v20)

**What changed:** Instead of writing sections one at a time (like a person typing each chapter before starting the next), the app now starts up to 3 sections at the same time.

**Analogy:** Before, it was like having one chef cook each course in sequence. Now it's like having 3 chefs working simultaneously.

**Result:** Total generation time drops from ~2-3 minutes to ~40-60 seconds for a typical report.

**Why only 3 at a time (not all 9)?** The Anthropic API has a limit on how many tokens (words) can be processed per minute. Running all 9 at once would hit that limit and cause failures. 3 is the safe balance. This can be raised via the `PARALLEL_SECTION_WORKERS` environment variable if a higher API tier is in use.

**Executive Summary still runs last** — it needs to read what the other sections said so it can summarize them accurately.

---

## Phase 2 — RAG Data Layer (Planned)

**RAG** = Retrieval-Augmented Generation. Fancy term for: *look up real facts first, then ask Claude to write using those facts.*

### The Problem RAG Solves

Today, the `rag_context` field in every prompt template is set to:
> `"No reference documents available."`

That means Claude is writing about market sizes, interest rates, and regulatory requirements purely from its training data — which may be outdated or wrong for a specific industry and Indian state.

### What Gets Built

A new `app/data_fetchers/` folder with one module per data source:

| File | Data Source | What It Fetches |
|---|---|---|
| `world_bank.py` | World Bank Open Data API | GDP, sector growth rates, country economic indicators |
| `india_gov.py` | data.gov.in (India open data portal) | State-level statistics, census data, agricultural output |
| `rbi.py` | RBI DBIE (Reserve Bank of India) | Bank lending rates, industry financial benchmarks |
| `trade_india.py` | IndiaMART / TradeIndia public catalog | Real equipment price ranges for common machinery |

Each fetcher:
1. Makes a real API/web call to fetch current data
2. Caches the result locally for 24 hours (so the same query doesn't repeat across reports)
3. Returns a short plain-text summary (3-5 bullet points) that gets injected into the `rag_context` field of the prompt

### How It Changes the Flow

```
Before (Phase 1):
  Section Agent → Claude (writes from memory) → Section text

After (Phase 2):
  Section Agent → Data Fetcher (gets real facts) → Claude (writes using real facts) → Section text
```

### Which Sections Benefit Most

- **Market Assessment** — real market size numbers from World Bank / IBEF instead of invented figures
- **Regulatory Framework** — actual GST thresholds, MCA21 filing requirements by state
- **Financial Feasibility** — real RBI lending rates instead of assumed 12%
- **Equipment Profiles** — real price ranges from equipment marketplaces

---

## Phase 3 — Open-Source Model Integration (Planned)

### Part A: Industry Auto-Classifier (Hugging Face)

**What it does:** Reads the `business_idea` field from the form and automatically identifies the industry vertical — e.g., "dal mill" → agro-processing, "EV charging station" → clean energy infrastructure.

**Why it matters:** Once we know the industry, we can:
- Pull industry-specific benchmarks (IBEF has separate reports per sector)
- Use the right prompt variant (a dairy plant needs different regulatory context than a software company)
- Skip irrelevant sections (a service business doesn't need equipment profiles in the same depth)

**Model used:** `facebook/bart-large-mnli` — a free, open-source zero-shot text classifier from Meta, available on Hugging Face. No API key needed.

**Where it runs:** Before section agents start, in the orchestrator. One call, ~2 seconds. Output is a string like `"agro-processing"` that flows into all agents.

---

### Part B: Cheaper Models for Low-Stakes Sections (GitHub Models)

**What GitHub Models is:** Microsoft runs a free API (using your GitHub token) that gives access to open-source LLMs like Phi-4 (Microsoft), Llama 3.3 (Meta), and Mistral. The API works exactly like OpenAI's API.

**The idea:** Not every section needs Claude Sonnet (the most capable, most expensive model). Some sections are boilerplate.

| Section | Proposed Model | Reason |
|---|---|---|
| Caveats | Phi-4 via GitHub Models | Standard disclaimer language — any model can do this |
| Appendices | Phi-4 via GitHub Models | Reference lists, glossary — structured, low-creativity |
| Equipment Profiles | Llama 3.3 via GitHub Models | Spec-sheet style writing — works well with structured prompts |
| Market Assessment | Claude Sonnet | Needs nuanced synthesis of real data |
| Financial Feasibility | Claude Sonnet | High-stakes, accuracy matters |
| Executive Summary | Claude Sonnet | Narrative quality is important for first impression |

**How it gets wired in:** A new `SECTION_MODEL_MAP` config (like the existing `SECTION_GEN_POLICY`) maps each section to a `provider:model` string. The `LLMClient` routes to the right API based on that config. GitHub Models uses the same OpenAI SDK — just a different base URL and your GitHub token.

**Cost impact:** Phi-4 and Llama 3.3 on GitHub Models are free (within generous rate limits). If 4 out of 9 sections move to free models, the Anthropic bill drops by ~40%.

---

## Summary Table

| Phase | Status | Speed Impact | Quality Impact | Cost Impact |
|---|---|---|---|---|
| Phase 1 — Parallel Agents | ✅ Done | ~3x faster | No change | No change |
| Phase 2 — Real Data (RAG) | Planned | Slight slowdown (+5-10s for fetches) | Major improvement — grounded facts | No change |
| Phase 3A — Industry Classifier | Planned | No change | Medium — better prompt targeting | No change |
| Phase 3B — Cheaper Models | Planned | No change | Slight trade-off for low-stakes sections | ~40% cheaper |

---

## Files This Roadmap Will Create

```
app/
  data_fetchers/
    __init__.py
    base.py           ← shared cache + fetch logic
    world_bank.py
    india_gov.py
    rbi.py
    trade_india.py
  industry_classifier.py   ← Phase 3A
app/config.py             ← add SECTION_MODEL_MAP (Phase 3B)
app/llm_client.py         ← add GitHub Models routing (Phase 3B)
```
