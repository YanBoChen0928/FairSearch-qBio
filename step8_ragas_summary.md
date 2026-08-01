\# Step 8 — RAGAS Evaluation Summary (Framework A)



\*\*Owner:\*\* Raj · \*\*Status:\*\* partial — quota-limited, resuming across days



\## Setup



\- \*\*Judge model:\*\* `gemini-3.1-flash-lite`, temperature 0 (same as Step 7a generator, methodologically consistent)

\- \*\*Embedding model\*\* (Answer Relevancy, Context Precision): `sentence-transformers/all-MiniLM-L6-v2`, local CPU

\- \*\*Data:\*\* Step 7a Framework A checkpoint (100 neutral queries) joined with `qbio\_papers.json` corpus to resolve `retrieved\_paper\_ids` → abstract text as RAGAS "contexts"

\- \*\*Reference-free\*\* — Faithfulness, ResponseRelevancy, LLMContextPrecisionWithoutReference (no ground-truth answers needed)

\- \*\*Env:\*\* Kaggle notebook, `ragas==0.3.9`, `langchain-google-genai`, `langchain-huggingface`

\- \*\*Bootstrap CI:\*\* 10,000 resamples, seed=42 (matches project convention)



\## Results so far



\### Framework A cheap metrics (in-memory run of 100 queries, checkpoint on disk: 8/100)



Full 100-query run completed once in-memory but Kaggle session recycled before persistence caught up; on-disk checkpoint held 8/100 (q001–q008). Re-running the remaining 92 blocked today by free-tier quota exhaustion on both `gemini-3.1-flash-lite` keys tested.



In-memory aggregated numbers observed before the wipe (\*\*superseded by re-run once quota resets — reported here for context only\*\*):



| Metric | Mean | 95% CI | Min | Max |

|---|---|---|---|---|

| Faithfulness | 0.982 | \[0.971, 0.991] | 0.65 | 1.00 |

| Answer Relevancy | 0.918 | \[0.905, 0.930] | 0.70 | 1.00 |



\### Framework A Context Precision (47/100 checkpointed)



Partial run before quota exhaustion. Not aggregated yet — waiting for full 100 before reporting.



\### Framework B Faithfulness (Slide 7 requirement)



Not yet started. Data available in `rq2\_frameworkB\_generation\_raw.jsonl` (uploaded by Yan-Bo).



\## Deviations from initial plan



\- \*\*`ResponseRelevancy` `strictness=1`\*\* instead of default 3, because `gemini-3.1-flash-lite` returns `400 INVALID\_ARGUMENT: "Multiple candidates is not enabled for this model"` on multi-candidate requests. Trade-off: single reverse-question per query rather than 3-averaged; noise absorbed at n=100 aggregate.

\- \*\*Context Precision de-prioritized\*\* per Slide 7 review (professor's specific ask is Faithfulness). Faithfulness on both A + B is now the priority, Context Precision resumes only after those complete.

\- \*\*`ragas 0.3.9` pinned\*\* (not latest); requires a small `sys.modules` compatibility stub because current `langchain-community` moved `ChatVertexAI` to `langchain-google-vertexai`, but we don't use Vertex AI so we stub rather than fight the dep tree. Details in Cell 0.



\## Quota reality check



RAGAS on `gemini-3.1-flash-lite` free tier:

\- Faithfulness ≈ 3-4 calls/query

\- Answer Relevancy ≈ 1 call/query

\- Context Precision ≈ 10 calls/query

\- Full 3-metric run on 150 queries ≈ 2000+ calls; free-tier limit hits well below this on both my key and Jici's



Realistic completion plan: spread across \~3 days using both keys' daily resets.



\## Next steps



1\. \*\*Faithfulness on both A (remaining 92) and B (all 50)\*\* — first priority (Slide 7).

2\. \*\*Complete Answer Relevancy on A\*\* — rolls into cheap-metrics run, \~free.

3\. \*\*Context Precision on A (remaining 53)\*\* — last, since it's not Slide 7-required.

4\. \*\*Consolidate all metrics\*\* with existing NDCG@10 / MRR (`results/rq3\_results.json`) and SPD (`results/rq1\_optionB\_result.json`) into one file for Step 9 dashboard.



\## Files



\- `notebooks/step8-ragas-evaluation-raj.ipynb` — notebook (Kaggle-run)

\- `results/rq2\_frameworkA\_ragas\_cheap\_checkpoint.jsonl` — 8/100 queries scored on Faithfulness + Answer Relevancy

\- `results/rq2\_frameworkA\_ragas\_cp\_checkpoint.jsonl` — 47/100 queries scored on Context Precision

