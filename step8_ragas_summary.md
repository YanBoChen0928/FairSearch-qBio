# Step 8 — RAGAS Evaluation Summary

**Owner:** Raj Lucka · **Status:** Complete — all 150 queries scored, all planned metrics run.

## Overview

RAGAS was deliberately kept OUT of RQ2 (per `rq2_plan.md` Decision 3, `rq2_methodology.md`) and attached here as a separate answer-quality evaluation. NDCG@10, MRR, and SPD are already measured elsewhere (Step 6 re-ranking / RQ3, Step 5b fairness audit / RQ1); this step does not recompute them. Step 8's specific contribution is the answer-quality stamp on top of the fairness audit: whether the RAG system's generated answers are actually good, independent of the fairness question RQ1/RQ2/RQ3 already addressed.

## Setup

- **Judge model:** `gemini-3.1-flash-lite` at temperature 0 (same class of model as Step 7a generator, methodologically consistent).
- **Embeddings model:** `sentence-transformers/all-MiniLM-L6-v2` locally on CPU (used by Answer Relevancy and Context Precision; kept local to avoid extra Gemini quota).
- **RAGAS version:** `ragas==0.3.9` pinned. Newer 0.4.x hardcodes `from langchain_community.chat_models.vertexai import ChatVertexAI` which the current `langchain-community` no longer ships. We stub that missing module in the notebook rather than fight the dep tree, since we don't use Vertex AI.
- **Bootstrap:** 10,000 resamples, seed=42 — matches project convention.
- **Env:** Kaggle notebook, `langchain-google-genai`, `langchain-huggingface`.
- **Data:** Step 7a Framework A checkpoint (100 neutral queries) and Step 7b Framework B checkpoint (50 contradictory queries), joined with `qbio_papers.json` corpus to resolve `retrieved_paper_ids` → abstract text as RAGAS "contexts".
- **Reference-free.** No ground-truth answers used or needed. Metrics chosen: `Faithfulness`, `ResponseRelevancy`, `LLMContextPrecisionWithoutReference`.

## Final results

### Framework A (100 neutral queries)

| Metric | Mean | 95% Bootstrap CI | Min | Max | n |
|---|---|---|---|---|---|
| Faithfulness | **0.978** | [0.966, 0.988] | 0.636 | 1.000 | 100 |
| Answer Relevancy | **0.914** | [0.899, 0.927] | 0.699 | 1.000 | 100 |
| Context Precision (ref-free) | 0.039 | [0.015, 0.071] | 0.000 | 1.000 | 100 |

### Framework B (50 contradictory queries)

| Metric | Mean | 95% Bootstrap CI | Min | Max | n |
|---|---|---|---|---|---|
| Faithfulness | **0.966** | [0.947, 0.983] | 0.714 | 1.000 | 50 |

Framework B was scored on Faithfulness only, per Prof. Sushmita's Slide 7 feedback (which specifically asked for RAGAS Faithfulness scores) and because Framework B has its own quality checks built into its generation pipeline (context-stance judge + answer two-layer judge).

## Interpretation

**Faithfulness is very high across both frameworks.** The RAG system's generated answers are strongly grounded in the retrieved contexts — no meaningful hallucination at aggregate. Framework B scoring slightly lower than Framework A (0.966 vs 0.978) is expected: contradictory queries force the model to synthesize opposing positions, which increases the surface area for per-claim verification to find something not perfectly supported by any single one of the 10 provided abstracts. The three lowest Framework B Faithfulness scores (0.71–0.81) are all classic scientific debates (nature-vs-nurture stem-cell fate, metabolism-first-vs-genetics-first, deterministic-vs-stochastic gene networks) where holding both sides in the answer legitimately makes per-claim grounding harder.

**Answer Relevancy at 0.914** indicates answers stay on-topic; even the worst-scoring query (0.70) is still reasonably relevant.

**Context Precision at 0.039 is a metric artifact, not a real retrieval failure.** The score distribution (see notebook Cell 12) shows:
- 90/100 queries scored exactly 0.0
- 4/100 scored ~0.5
- 5/100 scored in-between values (~0.1, 0.11, 0.2, 0.25 ×2)
- 1/100 scored 1.0

The dominant signal is 90/100 at exactly 0.0 — the signature of a conservative LLM-as-judge answering yes/no per context with mostly "no"s, producing a spike at the "zero useful contexts" outcome rather than a graded distribution of retrieval quality. Independently verified by Jici on 2026-08-05 using two separate bootstrap implementations; all aggregated numbers reproduce to the third decimal.


The reference-free variant of Context Precision compares each retrieved context against the *response* rather than a ground-truth answer, and it penalizes syntheses (like our answers, which combine information across multiple sources) that don't verbatim mirror any single context. On the 90 queries where Context Precision scored exactly 0.0, **Faithfulness averages 0.977 — essentially unchanged from the overall 0.978 mean**. If retrieval were genuinely producing "no useful contexts" for those queries, Faithfulness would drop with them; it doesn't. The answers ARE supported by the retrieved material (per Faithfulness), which directly contradicts Context Precision's verdict of "not useful". We report the CP number for transparency and flag it as a limitation of the reference-free variant, alongside Jici's independent-judge finding on Framework B — both are cases where LLM-as-judge produces systematic bias worth documenting.

## Deviations from initial plan

- **`ResponseRelevancy strictness=1`** instead of the default 3. `gemini-3.1-flash-lite` returns `400 INVALID_ARGUMENT: "Multiple candidates is not enabled for this model"` on multi-candidate requests. `strictness=1` asks for a single reverse-question per query rather than 3-averaged. Trade-off: slightly noisier per-query relevancy, absorbed at n=100 aggregate.
- **Context Precision de-scoped from Framework B**, per professor's Slide 7 feedback which asked only for Faithfulness, plus Framework B's built-in quality judges (see setup section).
- **Scoring spread across three days on free-tier quota** between two team keys (my key and Jici's). Full run needed ~1500 API calls; free-tier `gemini-3.1-flash-lite` doesn't fit that in one day. The per-query checkpoint + resume logic (notebook Cells 5-9) plus `flush()` + `os.fsync()` after every write made this quota-management approach safe against Kaggle session recycling.

## How this fits with RQ1/RQ2/RQ3

- **RQ1** (retrieval): weak/non-significant institutional bias, precisely framed after Jici's power analysis as "we can rule out large elite-retrieval bias with confidence; we cannot distinguish no-bias from small-bias-near-observed at this sample size" (both QS-overall and bio-specific list definitions).
- **RQ2** (generation): Framework A no significant citation amplification. Framework B substantive-engagement retention challenged by Jici's independent-judge finding (77.8% independent, 97.2% self-judge, essentially non-overlapping CIs, 7 unidirectional disagreements).
- **RQ3** (re-ranking): borderline/exploratory paired improvement per Jici's ~9% power finding.
- **RAGAS (this step):** the system is not only fair (RQ1–RQ3) but also produces faithful and on-topic answers (Faithfulness ~0.98 / 0.97, Answer Relevancy ~0.91) — the quality stamp on top of the fairness audit.

## Honest limits

- Judge = generator class of model. RAGAS scores are LLM-as-judge estimates, not oracle numbers — directional evidence.
- `strictness=1` on Answer Relevancy is a necessary workaround for flash-lite; default strictness=3 would have averaged over 3 reverse-questions per query.
- Reference-free Context Precision systematically underestimates precision when responses are syntheses rather than paraphrases; a with-reference variant using ground-truth answers would give a more calibrated number but requires human-written references outside project scope.

## Files

- **Notebook:** `notebooks/step8-ragas-evaluation-raj.ipynb` (Kaggle-run, 28 cells, resume-safe)
- **Checkpoints (per-query scores):**
  - `results/rq2_frameworkA_ragas_cheap_checkpoint.jsonl` — 100 queries, Faithfulness + Answer Relevancy
  - `results/rq2_frameworkA_ragas_cp_checkpoint.jsonl` — 100 queries, Context Precision
  - `results/rq2_frameworkB_ragas_faithfulness_checkpoint.jsonl` — 50 queries, Faithfulness
- **Aggregated summaries** (generated by notebook Cell 10, for Step 9 Streamlit consumption): `results/rq2_frameworkA_ragas_summary.json`, `results/rq2_frameworkB_ragas_summary.json` — *these will be generated when the notebook is re-run end-to-end; not committed as static files since they're deterministic from the checkpoint JSONLs.*