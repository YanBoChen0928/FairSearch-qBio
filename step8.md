# Step 8 Plan: RAGAS Evaluation

**Status:** Tier 1 full 150-query run COMPLETE (148/150 succeeded,
2026-08-01). See §4a.7 for the full results and the q032/q068 failure
investigation. Tier 2 CLOSED as infeasible on this stack (async/sync
deadlock, §4a.8), not merely parked. Tier 3 deferred by plan.

**AMENDED 2026-08-01 (twice).** First amendment: metric priority is now
tiered (Faithfulness required, Answer Relevancy opportunistic, Context
Precision deferred) on the basis of the Week 14 rubric wording. Second
amendment: §4a added after the pilot actually ran, recording what the
planning sections got wrong.

**Reading order, since parts of this file are now superseded by evidence:**
§2a (scope) and §5a (quota) before §4 and §5. Then **§4a, which overrides
§4 wherever they conflict**: §4 is an unexecuted draft, §4a is what happened
on the machine. Actionable checklist is in §6a. Query scope is unchanged at
all 150.

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

### 4a. Implementation findings (added 2026-08-01, after the Tier 1 pilot)

Everything in §4 above was written at planning time and had never been
executed. This section records what actually happened when it was, in the
Kaggle notebook `step8-ragas-faithfulness-pilot-yb`. Where §4 and this
section disagree, this section wins: it is empirical, §4 was not.

**Summary: Tier 1 (Faithfulness) works and is cheap. Tier 2 (Answer
Relevancy) is blocked by a ragas-internal defect and is parked.**

#### 4a.1 Three environment problems, none predicted by §4

All three surfaced before or during the pilot. They are recorded here
because each one invalidates an assumption that §4 stated as fact.

1. **`ragas` will not import at all on this Kaggle image.**
   `ragas/llms/base.py` line 12 imports `ChatVertexAI` from
   `langchain_community.chat_models.vertexai`. That path no longer exists
   in this image's `langchain_community` (0.4.2, which upstream has
   declared sunset in favour of standalone integration packages). The
   import failure breaks the entire ragas import chain even though this
   project never uses VertexAI. Confirmed as an upstream ragas defect, not
   a local misconfiguration: GitHub issues #2745 and #2741 report the same
   trace. Pinning `ragas==0.3.9` was attempted on the strength of those
   issues and did NOT help, because 0.3.9 carries the identical import.
   **Resolution:** stay on 0.4.3 (its `llm_factory` API matches §4's draft)
   and stub the missing submodule with a class that raises
   `NotImplementedError` if instantiated. The stub exists only to satisfy
   an import-time reference and is never called. Line 13's
   `langchain_community.llms.VertexAI` turned out to be present already and
   needed no stub.

2. **`instructor` needs an extras install for Gemini structured output.**
   The first real pilot attempt failed on all 8 queries with
   `ConfigurationError: The 'jsonref' package is required for Gemini
   structured output`. Elapsed time (about 2s per query, far too fast for a
   real API round trip) confirmed no Gemini calls were made, so no quota
   was consumed. **Resolution:** `pip install instructor[google-genai]`,
   which pulls in `jsonref`.

3. **§4's last paragraph is wrong about embeddings.** It states that
   Answer Relevancy's embedding step "is automatically matched to a Google
   embedding model when the LLM is Gemini, so no separate embedding setup
   is needed." In practice the auto-selected embeddings object fails with
   `AttributeError: 'GoogleEmbeddings' object has no attribute
   'embed_query'`. Note the shape of this: ragas's own `GoogleEmbeddings`
   class exposes `embed_text`/`aembed_text` per its documentation, while
   ragas's Answer Relevancy code calls `embed_query`. This is an internal
   inconsistency in ragas, not a configuration error on our side.
   **Resolution: none attempted. Tier 2 is parked, see §4a.4.**

#### 4a.2 What §4's draft got right

`inspect.signature(llm_factory)` confirms `provider` and `client` are real
parameters, so §4's planned call
`llm_factory("gemini-3.1-flash-lite", provider="google", client=client)`
is valid as written on 0.4.3. This is the reason 0.4.3 was chosen over
0.3.9 once it was established that downgrading did not avoid the VertexAI
defect.

#### 4a.3 Tier 1 pilot results (8 queries, seed 42)

Sample: 8 of the 150 queries, stratified 4 neutral (Framework A) and 4
contradictory (Framework B), `random.Random(42)` over id-sorted pools.
Selected ids: q004, q015, q082, q095, q109, q115, q116, q118.

Contexts were rebuilt in the exact `[i] Title: ...\nAbstract: ...` format
used by step7a/7b's `build_context()`, so Faithfulness scores claims
against what the generator actually saw rather than a reconstructed
approximation.

| Measure | Value |
|---|---|
| Queries attempted | 8 |
| Succeeded | 8 |
| Failed | 0 |
| Faithfulness range | 0.7778 to 1.0000 |
| Mean faithfulness | 0.9653 |
| Mean wall time per query | 11.75s (neutral 12.49s, contradictory 11.02s) |
| Extrapolated to 150 queries | about 29.4 min of API latency, excluding any added sleep |

**Bearing on the §5a quota discrepancy: zero 429s were observed.** This does
not explain why Raj saw approximately 50 requests/day, and it does not
resolve §5a, but it does establish that Tier 1 over all 150 queries is
feasible on Yan-Bo's key without waiting for that answer. The §5a
diagnosis item stays open; it is no longer a schedule blocker for Tier 1.

**Pilot scores are a feasibility signal, not a result.** The mean of 0.9653
is computed over 8 queries chosen to test the pipeline, not to estimate a
population value. Nothing from the pilot should be reported as the
project's Faithfulness finding; only the full 150-query run produces that.

#### 4a.4 Tier 2 (Answer Relevancy): parked, not abandoned

Parked on the `embed_query` defect in §4a.1 item 3, for three reasons:

1. Answer Relevancy is not in the rubric. Per §2a, the rubric names only
   "RAGAS Faithfulness scores", so Tier 2 was always this project's own
   added scope.
2. It exercises a different API surface (embeddings, not generation) whose
   quota behaviour and permissions on this key are entirely unverified. It
   is not simply "more of the same calls".
3. It would be the third consecutive environment defect to debug in this
   layer, with no evidence it is the last.

The parked Tier 2 cells stay at the bottom of the notebook, marked
do-not-run, rather than being deleted. **If Tier 2 is revisited, it should
be a bounded test, not open-ended debugging:** one query, with an explicit
`embeddings=embedding_factory(provider="google", client=client)` passed to
`evaluate()`. If the same `embed_query` error recurs, stop and record it as
a disclosed limitation rather than continuing to patch.

**RESOLVED 2026-08-01: the bounded test was run and Tier 2 is now CLOSED as
infeasible on this stack. See §4a.8.**

#### 4a.8 Tier 2 closed: an async/sync deadlock, not the embed_query bug

The bounded one-query test from §4a.4 was carried out on q004 (a query whose
Faithfulness score had already succeeded, so any failure would isolate the
metric rather than the query). The outcome upgrades the Tier 2 diagnosis
from "there is an embeddings bug" to "this metric cannot be constructed at
all on this stack".

**The original `embed_query` defect was actually solved.** Zero-quota
inspection established the root cause: ragas 0.4.3 ships two parallel
interfaces, a legacy one (`BaseRagasEmbeddings`, plural, exposing
`embed_query`) and a modern one (`BaseRagasEmbedding`, singular, exposing
`embed_text`/`embed_texts`). `GoogleEmbeddings` implements only the modern
interface (`hasattr(GoogleEmbeddings, "embed_query")` is False), while the
legacy `ragas.metrics.answer_relevancy` calls the legacy method. The fix is
to pair modern with modern: `ragas.metrics.collections.AnswerRelevancy` is
typed against `BaseRagasEmbedding`, and with that pairing the embeddings
layer passed without error.

**A deeper incompatibility then surfaced.** Four successive attempts, each
responding to the specific error raised by the previous one:

| Attempt | Call | Error |
|---|---|---|
| 1 | `metric.ascore()` with sync `genai.Client` | `TypeError: Cannot use agenerate() with a synchronous client. Use generate() instead.` |
| 2 | `metric.score()` (sync) with the same objects | `RuntimeError: Cannot call sync score() from an async context. Use ascore() instead.` |
| 3 | `ascore()` with the LLM rebuilt on `client.aio` | `ValueError: Client must be an instance of google.genai.Client. Got: AsyncClient` |
| 4 | Sync `score()` run inside a `ThreadPoolExecutor` worker thread (a different mechanism: escaping the notebook's event loop rather than reconfiguring the client) | Same `TypeError` as attempt 1. The thread had no event loop of its own, so the async-context check in attempt 2 was bypassed — but the LLM object itself still required an async-capable client. This confirms the deadlock is about client typing, not the notebook's event loop. |

These four constraints form a closed contradiction, and every one of them is
imposed by the libraries rather than by our configuration:

1. A Jupyter/Kaggle notebook already runs inside an event loop, so ragas
   refuses the synchronous `score()` path (attempt 2).
2. The asynchronous `ascore()` path therefore has to be used, and it
   requires an async-capable LLM (attempt 1).
3. An async-capable LLM would require passing the async client namespace,
   `client.aio` (confirmed to exist on the google-genai client).
4. But ragas's instructor adapter type-checks the client and rejects
   anything that is not exactly `google.genai.Client`, which `AsyncClient`
   is not (attempt 3).

No arrangement of these components satisfies all four simultaneously on
ragas 0.4.3 with google-genai, including the thread-based escape in attempt
4. **Tier 2 is therefore closed as infeasible on this stack, not merely
parked**, and no fifth workaround was attempted, per the stopping rule in
§4a.4. Note this is an upstream compatibility gap of the
same character as the three defects in §4a.1, not a quota issue and not a
configuration error on our side.

**Reporting.** Answer Relevancy is absent from the rubric (§2a), so this
closes an optional item rather than a required one. The report should state
that Answer Relevancy was attempted and found infeasible on this stack, with
the async/sync deadlock named as the reason, in the same spirit as Framework
B's self-judge disclosure. Do not imply it was skipped for convenience.

Path not taken, recorded for completeness: `LangchainEmbeddingsWrapper` does
expose `embed_query` and would satisfy the legacy interface, and the project
already has all-MiniLM-L6-v2 embeddings of the corpus that could have served
as the similarity backend at zero Gemini cost. This was not pursued because
the blocking constraint turned out to be on the LLM side, not the embeddings
side, so a different embeddings object would not have resolved it.

#### 4a.5 A defect in this project's own pilot code (fixed)

Worth recording separately, because it was our error rather than an
upstream one. Ragas catches a per-query job exception internally and
returns `faithfulness = NaN` instead of raising. The first version of the
pilot loop did not check for this, so all 8 queries from the `jsonref`
failure were written to the checkpoint as `error: None` with a `NaN` score,
i.e. recorded as successes. That is a silent failure of exactly the kind
this project's fail-loud rule exists to prevent (compare the "never
silently map unknown enum values" rule in Framework B).

Fixed before any further queries were run: the runner now rejects
`NaN`/non-finite scores as failures, and the resume logic counts a query as
done only when `error is None AND score is not None`, so a recorded failure
is never skipped on a rerun. The 8-row checkpoint from the first attempt
was deleted rather than kept, since every row in it was invalid.

#### 4a.6 Notebook cell structure

`step8-ragas-faithfulness-pilot-yb`, attached datasets:
`fairsearch-qbio-processed-raj-jici-yb` (for `qbio_papers.json`) and
`step7-frameworka-for-raj` (for both frameworks' generation records; note
the display title is `step7_frameworkAB_result_for_Raj` but the URL slug is
unchanged, see `data/kaggle_datasets.md`).

| Cell | Purpose | Calls API |
|---|---|---|
| 0 | Install `ragas==0.4.3` (install only, no import) | no |
| 0b | Stub the VertexAI submodule, import ragas, print `llm_factory` signature | no |
| 0c | Install `instructor[google-genai]` for `jsonref` | no |
| 1 | Load corpus + both frameworks' generation records, build `pmap` | no |
| 2 | Stratified pilot sample, seed 42 | no |
| 3 | Rebuild contexts in the generator's exact format | no |
| 4 | Build Gemini client and `evaluator_llm` | no |
| 5 | Tier 1 pilot: per-query Faithfulness, JSONL checkpoint, NaN rejection | yes |
| 6 | Pilot summary and extrapolation to 150 | no |
| 7 | Tier 1 full run: all 150 queries, same checkpoint pattern | yes |
| 8 | Aggregate the full run, write `ragas_faithfulness_result.json` | no |
| (parked) | Tier 2 Answer Relevancy, blocked per §4a.4, marked do-not-run | n/a |

A kernel restart is needed after cells 0 and 0c, since Kaggle keeps
pip-installed packages across a restart but clears Python import state,
which is what a stale partial ragas import requires.

#### 4a.7 Tier 1 full run results (all 150 queries, 2026-08-01)

Cell 7 ran to completion twice: once attempting all 150 queries fresh (148
succeeded, 2 failed), and once as a resume pass over just the 2 recorded
failures (both failed again, identically). The checkpoint file therefore
contains 152 rows for 150 unique `query_id`s; Cell 8 dedupes by
`query_id`, preferring a successful record over a failed one when both
exist for the same id.

**Final scope: 148/150 (98.7%) succeeded.**

| Measure | Overall (n=148) | Neutral / Framework A (n=98) | Contradictory / Framework B (n=50) |
|---|---|---|---|
| Mean faithfulness | 0.9615 | 0.9616 | 0.9613 |
| Median | 1.0 | 1.0 | 1.0 |
| Min | 0.5 | 0.7059 | 0.5 |
| Max | 1.0 | 1.0 | 1.0 |
| Stdev | 0.0777 | 0.0699 | 0.0918 |

Neutral and contradictory queries score within 0.0003 of each other on
mean faithfulness — no evidence that answer type (factual vs. two-sided
debate) affects grounding quality. Output written to
`ragas_faithfulness_result.json` on Kaggle (local sync into `results/`
deferred until Step 8 is fully closed out).

**q032 and q068: persistent, unexplained failure.** Both failed identically
on two separate Cell 7 executions — same error
(`InstructorRetryException: "Please return your response as a function
call"`), same ~136-138s elapsed both times, versus the normal 6-11s for a
successful query. This rules out a one-off API blip: a transient failure
would not reproduce with this precision twice.

Four content-based hypotheses were checked and each was ruled out:

1. **Answer length.** q032 (1027 chars) and q068 (991 chars) are both
   below the Framework A median (1238 chars, range 505-1738). Not
   outliers, and shorter than typical if anything.
2. **Citation count.** q032 has 5 `valid_numbers`, q068 has 7; corpus
   median is 9 (range 4-16). Below median, not distinctive.
3. **Citation formatting.** Adjacent-bracket citations (e.g. `[4][10]`)
   and two-digit citation numbers appear in 81/100 and 75/100 neutral
   answers respectively — extremely common corpus-wide. q032 does not
   even exhibit this pattern, so it cannot be the shared cause with q068.
4. **Context content.** All 20 retrieved-paper abstracts across both
   queries' contexts were inspected: lengths range 564-1894 characters
   (unremarkable), and zero non-ASCII characters were found in any of
   them.

**No content-based cause was identified.** Per the same principle used for
Tier 2 in §4a.4 ("if the same error recurs, stop and record it as a
disclosed limitation rather than continuing to patch"), a third retry was
not attempted. Disclosed limitation for the report: 148/150 (98.7%) of
queries received a Faithfulness score; q032 and q068 failed reproducibly
on an `instructor`/Gemini structured-output error whose root cause could
not be determined from available signals, and are excluded from the
aggregate statistics above rather than assigned a fabricated score.

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

1. **[NO LONGER BLOCKING for Tier 1, still open] Resolve the quota
   discrepancy (§5a).** Ask Raj for the `quotaId` and `quotaValue` from his
   429 response. Downgraded from BLOCKING on 2026-08-01: the Tier 1 pilot
   hit zero 429s and extrapolates to about 29 min for all 150 queries on
   Yan-Bo's key (§4a.3), so Tier 1 can proceed without this answer. The
   question itself is still unresolved and still matters for anything Raj
   runs on his own key.
2. **[BLOCKING] Confirm the rubric reading in §2a** with Prof. Sushmita or
   a TA: is "RAGAS Faithfulness scores" the full requirement, or
   illustrative shorthand for the RAGAS suite? A one-line answer here
   determines whether Tier 3 is optional or mandatory.
3. **[DONE 2026-08-01]** 8-query Tier 1 pilot: 8/8 succeeded, 11.75s mean
   per query, zero 429s. Full numbers and the three environment defects it
   surfaced are in §4a.
4. **[DONE 2026-08-01]** Run Tier 1 (Faithfulness) over all 150 queries
   with per-query JSONL checkpointing. Result: 148/150 (98.7%) succeeded,
   mean faithfulness 0.9615 (neutral 0.9616, contradictory 0.9613). See
   §4a.7 for the full breakdown and the q032/q068 failure investigation.
   This satisfies the rubric deliverable.
5. **[CLOSED 2026-08-01, infeasible on this stack]** Tier 2 (Answer
   Relevancy): the bounded one-query test from §4a.4 was run. The original
   `embed_query` defect was solved (modern `collections.AnswerRelevancy` +
   `GoogleEmbeddings`), but a deeper async/sync deadlock in ragas 0.4.3 +
   google-genai makes the metric impossible to construct in a notebook
   event loop. Three attempts, full error trail in §4a.8. No fourth
   workaround attempted, per the §4a.4 stopping rule. Not a quota issue.
   Report as an attempted-and-infeasible optional metric, not as skipped.
6. **DEFERRED: Tier 3 (Context Precision).** Revisit only under the §2a
   deferral condition. If run on a subset, document the subset size and
   selection rule.
7. **[DONE 2026-08-01]** `rq2_frameworkB_generation_raw.jsonl` uploaded to
   the Kaggle dataset `step7-frameworka-for-raj` (display title renamed to
   `step7_frameworkAB_result_for_Raj`; URL slug unchanged — see
   `data/kaggle_datasets.md`). Confirmed working via the Step 8 pilot
   notebook's Cell 1: both `rq2_gen_checkpoint.jsonl` (Framework A, 100
   records) and `rq2_frameworkB_generation_raw.jsonl` (Framework B, 50
   records) resolve correctly, 150/150 total, 0 missing corpus paper_ids.
8. **[SECURITY, unrelated to quota] Rotate or revoke Yan-Bo's older Gemini
   API key.** It was previously pasted in plaintext into a team chat
   message. Confirm in Google Cloud Console whether it has been revoked;
   if not, revoke it and reissue. Track separately from the Step 8 run.

---

## 7. Limitations (consolidated for the report, added 2026-08-01)

Everything a report or slide citing Step 8 must disclose, in one place.
Each item links to the section holding the underlying evidence.

1. **Self-judge design.** The judge model is `gemini-3.1-flash-lite`, the
   same model that generated every answer in Step 7a/7b. A model scoring its
   own output may be more lenient than an independent judge. No mitigation
   was attempted, on the same free-tier grounds that drove RQ2 Framework B's
   judge fallback. Disclose identically to that case. (§3)

2. **148 of 150 queries, not 150.** q032 and q068 failed reproducibly across
   two separate executions with an identical upstream `instructor`
   structured-output error, at ~137s each versus a normal 6-11s. Four
   content-based explanations were tested and ruled out: answer length,
   citation count, citation formatting, and non-ASCII characters in the
   retrieved context. No cause was identified. Both are excluded from all
   aggregates rather than imputed. (§4a.7)

3. **Answer Relevancy could not be produced.** Five attempts are documented.
   The originally reported `embed_query` defect was genuinely solved by
   pairing the modern `collections.AnswerRelevancy` with the modern
   `GoogleEmbeddings`, but a closed async/sync contradiction in
   ragas 0.4.3 with google-genai makes the metric impossible to construct in
   this environment, including from inside a worker thread. This is an
   upstream compatibility gap, not a quota limit and not a configuration
   error. It must be reported as attempted-and-infeasible, never as skipped.
   (§4a.8)

4. **Context Precision was never run.** Deferred by plan, and still open.
   The deferral is contingent on the unresolved rubric question in §2a, not
   on a technical finding. If the answer to §2a makes it mandatory, this
   becomes work rather than a limitation. See the next-to-do note below.

5. **Environment workarounds are load-bearing.** Getting ragas to import at
   all required stubbing a `langchain_community` submodule that this project
   never uses, plus an extras install for `jsonref`. The results are valid,
   but the environment is not reproducible from `requirements.txt` alone.
   Anyone rerunning this must follow the cell order in §4a.6. (§4a.1)

6. **Faithfulness measures grounding, not correctness.** A claim fully
   supported by a retrieved abstract scores 1.0 even if that abstract is
   itself wrong. Faithfulness says the system is not hallucinating beyond its
   sources; it says nothing about whether the sources are right, and nothing
   about fairness, which is what RQ1 to RQ3 measure. (§1)

7. **Scores are descriptive, with no significance test.** Means and standard
   deviations are reported without confidence intervals, deliberately. Unlike
   SPD, SRR, or citation amplification, Faithfulness here is not being tested
   against a null value, so a CI would imply a hypothesis test that was never
   pre-registered. The 0.0003 gap between neutral and contradictory means is
   reported as "no material difference", not as a tested null result.

### 7a. Next to do (Step 8 specific)

Everything else Step 8 owns is closed. Two items remain, both external:

1. **[BLOCKING] The §2a rubric question.** Ask Prof. Sushmita or a TA
   whether "RAGAS Faithfulness scores" is the complete requirement or
   shorthand for the RAGAS suite. This single answer decides whether Tier 3
   Context Precision moves from limitation 4 above into required work. Ask
   now: the answer costs one line, and the work it might trigger is roughly
   1,500 API calls.
2. **[NON-BLOCKING] The §5a quota discrepancy with Raj.** Downgraded, not
   resolved. Tier 1 completed on Yan-Bo's key with zero 429s, so it no longer
   blocks anything in Step 8, but it still matters for anything Raj runs on
   his own key.

**Decision recorded 2026-08-01: no `step8_methodology.md` will be written.**
The earlier closing note below planned one, mirroring RQ1/RQ2/RQ3. That is
now cancelled as unnecessary duplication: Tier 1 is complete and Tier 2 is
closed, so §4a already contains everything a methodology file would restate,
and §7 above gives the report a single citable limitations list. Tier 3 is
carried as limitation 4 plus next-to-do item 1 rather than as a placeholder
section in a new document.

---

*Originally a planning document. Implementation started 2026-08-01; §4a
records what the plan got wrong and is authoritative over §4. §7 consolidates
the reportable limitations. The earlier plan to supersede this file with a
`step8_methodology.md` was cancelled on 2026-08-01, see §7a. Treat §§1-3, 5, 6
as plan and §§2a, 4a, 5a, 6a, 7, 7a as record.*
