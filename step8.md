# Step 8 Plan: RAGAS Evaluation

**Status:** Planning (not yet implemented) — this document records the design
before any code is written, so the plan can be reviewed before committing to
an approach.

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

```python
import os
from google import genai
from ragas.llms import llm_factory
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
evaluator_llm = llm_factory(
    "gemini-3.1-flash-lite",
    provider="google",
    client=client,
)

# dataset: HuggingFace Dataset with columns question / contexts / answer
result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision],
    llm=evaluator_llm,
)
```

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

---

*This is a planning document. Implementation has not started; this file
will be updated (or superseded by a `step8_methodology.md`, mirroring the
RQ1/RQ2/RQ3 pattern) once results exist.*
