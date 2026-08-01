# Step 8 Plan: RAGAS Evaluation

**Status:** Planning (not yet implemented) — this document records the design
before any code is written, so the plan can be reviewed before committing to
an approach.

**AMENDED 2026-08-01.** Metric priority is now tiered (Faithfulness required,
Answer Relevancy opportunistic, Context Precision deferred) on the basis of
the Week 14 rubric wording. Read §2a and §5a before §4 and §5; where they
disagree, §2a wins. Query scope is unchanged at all 150. Actionable
checklist is in §6a.

**Goal:** measure pure RAG system quality (independent of fairness) on the
answers already generated in Step 7a/7b, using RAGAS. This complements RQ1
(retrieval fairness), RQ2 (generation fairness), and RQ3 (re-ranking
fairness-utility) with a system-quality benchmark: "regardless of fairness,
is the RAG system doing its basic job well — staying faithful to sources,
answering on-topic, retrieving relevant context?"

**Owner:** TBD
**Depends on:** Step 7a output (100 neutral-query generations), Step 7b
output (50 contradictory-query generations)

---

## 1. Background: what RAGAS measures

RAGAS (Retrieval-Augmented Generation Assessment) is a reference-free
evaluation framework for RAG systems — it does not require a human-written
"correct answer" to compare against. It scores the retrieval side and the
generation side of the pipeline separately:

- **Faithfulness** (generation): decomposes the generated answer into
  individual claims, then checks whether each claim can be inferred from the
  retrieved context. Score = (claims supported by context) / (total claims).
  This measures hallucination.
- **Answer Relevancy** (generation): works in reverse — an LLM generates
  several candidate questions that the given answer *could* be answering,
  then compares those to the actual question via embedding similarity. A
  low score means the answer is off-topic or evasive relative to what was
  asked.
- **Context Precision** (retrieval): scores whether the retrieved context
  chunks that are actually relevant to the question are ranked near the top
  of the retrieved set.

**Context Recall is deliberately excluded**, since it requires a
human-written ground-truth answer to measure against, which this project
does not have (see the relevance-proxy design in `rq1_methodology.md` §1–2
and `query_generation_methodology.md` — the project has never used
human-labeled ground truth answers, only a subcategory-match relevance
proxy for retrieval).

---

## 2. Data mapping — no new data collection needed

RAGAS expects, per sample: `question`, `contexts` (list of retrieved text
chunks), `answer`. All three already exist in this project's outputs; the
task is to assemble them, not collect new data:

| RAGAS field | Source in this project |
|---|---|
| `question` | `query_text` from `queries/queries_all_150.json` |
| `contexts` | The 10 retrieved paper abstracts for that query, from `retrieval_results.json` (`retrieved_paper_ids` → look up abstract text in the corpus) |
| `answer` | The Gemini-generated answer from Step 7a (neutral, 100) or Step 7b (contradictory, 50) output |

Scope: **all 150 queries** — Framework A's 100 neutral and Framework B's 50
contradictory generations both get evaluated, since RAGAS's three metrics
(faithfulness, relevancy, context precision) are agnostic to whether a query
is neutral or a two-sided debate; unlike RQ1/RQ3's relevance proxy, RAGAS
does not depend on the subcategory-match convention, so there is no reason
to exclude the contradictory set here.

### 2a. Metric-priority amendment (added 2026-08-01, BEFORE any Step 8 run)

This amendment changes the METRIC PRIORITY only. It does NOT change the
query scope decided above (all 150 queries remains the target for the
primary metric). Where this amendment and the original three-metric
framing in §4 disagree, this amendment wins.

**Basis.** The Week 14 Final Project rubric names RAGAS exactly twice, and
both mentions read "RAGAS Faithfulness scores" with no other metric named:

- Slide 7 (Experiment B: Generative Faithfulness): "Contradictory query
  design, Pro-Consensus vs. Dissenting token ratio analysis, RAGAS
  Faithfulness scores."
- Report Methodology, Experiment B: identical wording.

Answer Relevancy and Context Precision appear nowhere in the rubric. The
original three-metric plan in §4 was therefore this project's own added
scope, not a course requirement.

**Caveat on this reading.** The above is a literal reading of the rubric
text by Yan-Bo, not a confirmation from Prof. Sushmita or a TA. The rubric
wording may be illustrative rather than exhaustive. Confirm before relying
on it to justify a reduced deliverable.

**Amended priority (three tiers):**

| Tier | Metric | Scope | Status |
|---|---|---|---|
| 1 (required) | Faithfulness | all 150 queries | primary deliverable; maps directly to the rubric |
| 2 (opportunistic) | Answer Relevancy | all 150 queries | run in the same pass IF quota allows; ~1 sub-call/query, the cheapest of the three |
| 3 (deferred) | Context Precision | TBD | moved to the next-to-do list, NOT part of the committed Step 8 run |

Rationale for the tiering. Faithfulness (~2 sub-calls/query) plus Answer
Relevancy (~1) is roughly 450 calls across 150 queries; Context Precision
alone (up to 10 per query) is roughly 1,500, i.e. it accounts for the large
majority of the original estimate in §5. Dropping it from the committed run
removes most of the quota risk while still satisfying the rubric.

**Deferral condition for Tier 3.** Context Precision is revisited only
after (a) the quota discrepancy in §5a is resolved, AND (b) Tiers 1 and 2
have completed successfully. If it is ultimately run on a subset rather
than all 150 queries, the subset size and selection rule must be stated
explicitly in the report, in the same manner as Framework B's self-judge
disclosure.

**Reporting requirement (no silent scope reduction).** The report must state
plainly which RAGAS metrics were run, over how many queries, and that
Context Precision was deferred on free-tier quota grounds. Omitting the two
unrun metrics without explanation is not acceptable under this project's
disclosure standard.

### 5a. Quota discrepancy (open, blocking the schedule)

Two contradictory observations of the same free-tier daily limit on
`gemini-3.1-flash-lite` exist as of 2026-08-01:

- Yan-Bo, during Step 7a: order of 1,000 requests/day.
- Raj, attempting Step 8: blocked at approximately 50/day.

This 20x gap is the single largest schedule risk in Step 8, because it
decides whether the Tier 1 + Tier 2 run is a two-hour job or a nine-day job:

| Assumed daily quota | Calls needed (Tiers 1+2, 150 queries) | Elapsed |
|---|---|---|
| ~1,000/day | ~450 | one sitting, roughly 1.5-2.5 hours wall clock at SLEEP=5 |
| ~50/day | ~450 | ~9 days, which does not fit before the 2026-08-11 deadline |

**Agreed diagnosis path (Solution 1 + Solution 2, confirmed with Raj):**

1. Solution 1: obtain the `quotaId` and `quotaValue` from Raj's 429 error
   response, to establish whether both keys draw on the same quota pool or
   whether Raj's project has a different (or zero) free-tier allocation.
   This is the critical-path item; resolve it before scheduling the run.
2. Solution 2: keep all 150 pre-registered queries; run the cheap metrics
   (Tier 1, then Tier 2) first with per-query checkpointing, and defer the
   expensive metric (Tier 3) per §2a.

**Solution 3 (added 2026-08-01):** Jici supplied Raj with a separate Gemini
API key for Step 8 use only, to be deleted after the run. If this key sits
in the ~1,000/day tier, Tiers 1 and 2 can complete in a single session and
no scope reduction is needed. Record which key/project actually produced
the reported numbers, consistent with the "never silently swap models"
rule in `rq2_plan.md` Decision 4.

---

## 3. Judge model

**Decision: `gemini-3.1-flash-lite`**, the same model used for all Step
7a/7b generation, chosen specifically to stay on the free tier.

**Known limitation (same pattern as RQ2 Framework B):** using the same model
as both generator and judge is a **self-judge** design — a known potential
bias direction (the model may rate its own output more favorably than an
independent judge would). This must be disclosed identically to how
Framework B's self-judge limitation is disclosed in `rq2_methodology.md`
§3.4. No mitigation is planned for Step 8 (no independent second model), on
the same free-tier-quota grounds that drove Framework B's fallback.

---

## 4. Technical approach (Gemini integration, current as of RAGAS docs Jan 2026)

**Terminology note (to avoid a naming collision):** the `dataset` in the code
below refers to a `datasets.Dataset` object — an in-memory table format from
HuggingFace's `datasets` Python library (`pip install datasets`), unrelated
to "Kaggle Dataset." No data leaves Kaggle and no HuggingFace account is
needed; this is purely a Python-library data structure that Ragas requires
as input, built from the same JSON files already stored as Kaggle Datasets
(`retrieval_results.json`, Step 7a/7b outputs, etc.) by loading them with
`json.load(...)` and converting to a `pandas.DataFrame` /
`Dataset.from_pandas(...)` inside the same Kaggle notebook — all in one
runtime, no platform change.

```python
import os
from google import genai
from ragas.llms import llm_factory
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset  # HuggingFace `datasets` library, pip install only

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
evaluator_llm = llm_factory(
    "gemini-3.1-flash-lite",
    provider="google",
    client=client,
)

# dataset: an in-memory Dataset object (question / contexts / answer columns),
# built from the project's own Kaggle-hosted JSON — see terminology note above
result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision],
    llm=evaluator_llm,
)
```

**AMENDED 2026-08-01 (see §2a).** The metric list above is the original
three-metric plan and is now superseded for the committed run. The actual
run uses the tiered list below, so that a quota failure on the expensive
metric cannot destroy the required one:

```python
# Tier 1 (required by rubric) - run first, checkpoint per query
metrics_tier1 = [faithfulness]

# Tier 2 (opportunistic) - add only if Tier 1 completed with quota to spare
metrics_tier2 = [faithfulness, answer_relevancy]

# Tier 3 (deferred, NOT in the committed run) - see §2a deferral condition
# metrics_tier3 = [context_precision]
```

Run Tier 1 to completion and save its results BEFORE starting Tier 2. Do
not launch a single combined call over all three metrics: RAGAS aborts the
whole `evaluate()` batch on an unhandled quota error, which would lose the
Faithfulness results alongside the Context Precision ones. Per-query
checkpointing to JSONL (same pattern as `rq2_gen_checkpoint.jsonl`) is
required, not optional.

Ragas auto-detects the Google provider and routes through its LiteLLM
adapter; Answer Relevancy's embedding-similarity step is automatically
matched to a Google embedding model when the LLM is Gemini, so no separate
OpenAI key or embedding setup is needed.

---

## 5. Quota risk (flagged before implementation, given prior free-tier failures)

RAGAS does not make one API call per metric per query — each metric
internally issues **several sub-calls**:

| Metric | Approx. sub-calls per query |
|---|---|
| Faithfulness | ~2 (claim extraction, then per-claim verification) |
| Answer Relevancy | ~1 (generate ~3 candidate reverse-questions) |
| Context Precision | up to 10 (one relevance judgment per retrieved context chunk) |

**Rough estimate: ~10–13 LLM calls per query.** Across all 150 queries
(Framework A's 100 + Framework B's 50):

```
150 queries × ~10–13 calls/query ≈ 1,500–2,000 total API calls
```

This is the same category of risk that caused Framework B's primary judge
(`gemini-3-flash-preview`, 20 requests/day free tier) to fail mid-run at
q115 (see `rq2_methodology.md` §3.4). Before running the full 150-query
batch, this plan calls for:

1. **A small pilot** (5–10 queries) to measure actual call count, latency,
   and whether the free tier is hit, before committing to the full run.
2. **A decision point after the pilot**: if quota is a binding constraint,
   options include running in batches across multiple days (saving
   intermediate results, as recommended for the Step 1b/5b Kaggle re-runs),
   or narrowing the metric set (e.g. Context Precision alone first, since it
   scales with context length, being the most expensive of the three).

No commitment is made yet on which fallback to use — that decision is
deferred until the pilot's actual numbers are in hand.

---

## 6. Open items before implementation begins

- [ ] Run the 5–10 query pilot; record actual call count and elapsed time.
- [ ] Confirm `gemini-3.1-flash-lite`'s current free-tier RPM/RPD limits.
- [ ] Decide whether Framework A and Framework B results are reported
      separately or pooled (leaning toward separately, mirroring RQ2's
      split, since the two query types differ in what "faithfulness" means
      for a two-sided debate answer vs a factual neutral-query answer).
- [ ] Decide output file naming (proposed: `ragas_frameworkA_result.json`,
      `ragas_frameworkB_result.json`, consistent with the RQ2 naming
      convention).

### 6a. Next-to-do list (amended 2026-08-01, in priority order)

Critical path first. Items 1 and 2 gate everything else.

1. **[BLOCKING] Resolve the quota discrepancy (§5a).** Ask Raj for the
   `quotaId` and `quotaValue` from his 429 response. Until this is known,
   the Step 8 schedule cannot be committed to, because the same run is
   either a 2-hour job or a 9-day job.
2. **[BLOCKING] Confirm the rubric reading in §2a** with Prof. Sushmita or
   a TA: is "RAGAS Faithfulness scores" the full requirement, or
   illustrative shorthand for the RAGAS suite? A one-line answer here
   determines whether Tier 3 is optional or mandatory.
3. Run the 5-10 query pilot on Tier 1 only; record actual call count,
   latency, and whether the free tier is hit.
4. Run Tier 1 (Faithfulness) over all 150 queries with per-query JSONL
   checkpointing.
5. Run Tier 2 (Answer Relevancy) if quota headroom remains after item 4.
6. **DEFERRED: Tier 3 (Context Precision).** Revisit only under the §2a
   deferral condition. If run on a subset, document the subset size and
   selection rule.
7. Upload `rq2_frameworkB_generation_raw.jsonl` to the Kaggle dataset
   `step7-frameworka-for-raj`. Raj currently has only the Framework A
   checkpoint (`rq2_gen_checkpoint.jsonl`, 100 records), which is
   Framework-A-only by design and NOT evidence of data loss; the
   Framework B generations live in a separate file that has not been
   shared yet. Step 8's 150-query scope cannot be run without it.
8. **[SECURITY, unrelated to quota] Rotate or revoke Yan-Bo's older Gemini
   API key.** It was previously pasted in plaintext into a team chat
   message. Confirm in Google Cloud Console whether it has been revoked;
   if not, revoke it and reissue. Track separately from the Step 8 run.

---

*This is a planning document. Implementation has not started; this file
will be updated (or superseded by a `step8_methodology.md`, mirroring the
RQ1/RQ2/RQ3 pattern) once results exist.*
