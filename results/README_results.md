# Results Dictionary — `results/`

Aggregated, reportable outputs. Everything here is MEASURED, never
hypothetical or projected. Raw per-query checkpoints live in `data/` instead
(see `data/README_data.md`); this folder holds only the aggregated result
files and the charts built from them.

**Rule of thumb for which folder a file belongs in:** if it has one row per
query and was written incrementally during a run, it goes in `data/`. If it
is the single summarised artifact a section of the report would cite, it
goes here.

## Quick map

| File | Research question | Headline |
|---|---|---|
| `rq1_optionB_result.json` | RQ1 retrieval parity | SPD +0.029, SRR 1.28, 95% CI [-0.005, +0.065] (crosses zero) |
| `rq1_optionB_result_bio.json` | RQ1 robustness check | SPD +0.031, same conclusion under the bio-specific elite list |
| `equalized_odds_results_bio.json` | RQ1 equalized odds | signed CI crosses zero, no systematic directional bias |
| `equalized_odds_signed_direction_bio.json` | RQ1 equalized odds | signed-direction breakdown |
| `rq2_frameworkA_result.json` | RQ2 citation amplification | mean amplification +0.0041, bootstrap CI crosses zero |
| `rq2_frameworkB_result.json` | RQ2 viewpoint retention | 35/36 retained both viewpoints, 97.2%, CI [91.7%, 100.0%] |
| `rq3_results.json` | RQ3 fairness-utility tradeoff | NDCG@10 / MRR vs lambda sweep; institution-aware re-rank at lambda=0.8 |
| `ragas_faithfulness_result.json` | Step 8 system quality | 148/150 scored, mean faithfulness 0.9615 |

Charts, each paired with the JSON above it:
`rq1_optionB_elite_share.png`, `rq1_optionB_elite_share_bio.png`,
`equalized_odds_distribution_bio.png`,
`equalized_odds_signed_distribution_bio.png`,
`rq2_frameworkA_scatter.png`, `rq2_frameworkB_retention.png`,
`rq3_lambda_ablation.png`, `rq3_institution_ablation.png`,
`rq3_spd_significance.png`, `step8_faithfulness_chart.png`.

---

## `ragas_faithfulness_result.json` (Step 8, added 2026-08-01)

The Step 8 deliverable: RAGAS Faithfulness over the pre-registered 150-query
set. Faithfulness decomposes each generated answer into individual claims and
checks whether each is supported by the retrieved abstracts, so it measures
hallucination independently of fairness.

Produced by Cell 8 of `notebooks/step8-ragas-faithfulness-pilot-yb.ipynb`,
which dedupes the raw checkpoint `data/step8_faithfulness_full150.jsonl` by
`query_id`. Full method and caveats in `step8.md` §4a.7.

### Headline numbers

| Measure | Overall (n=148) | Neutral / Framework A (n=98) | Contradictory / Framework B (n=50) |
|---|---|---|---|
| Mean | 0.9615 | 0.9616 | 0.9613 |
| Median | 1.0 | 1.0 | 1.0 |
| Min | 0.5 | 0.7059 | 0.5 |
| Max | 1.0 | 1.0 | 1.0 |
| Stdev | 0.0777 | 0.0699 | 0.0918 |

Neutral and contradictory means differ by 0.0003, so there is no evidence
that answer type affects grounding quality. No confidence interval is
computed and none is needed: unlike RQ1/RQ2/RQ3, this is a descriptive
system-quality metric, not a test of whether a quantity differs from zero.

### Structure

Top-level keys: `metric`, `judge_model`, `self_judge_disclosure`,
`query_scope`, `failed_queries`, `faithfulness_overall`,
`faithfulness_by_type`, `per_query`.

`per_query` holds the 148 successful rows only. The 2 failures are in
`failed_queries` with a populated `disclosed_limitation` string, deliberately
kept separate so a mean can never be computed over imputed values.

### Three things to state whenever this file is cited

1. **Self-judge design.** The judge is `gemini-3.1-flash-lite`, the same
   model that generated the answers in Step 7a/7b. Disclose exactly as
   Framework B's self-judge limitation is disclosed (`step8.md` §3).
2. **148 of 150, not 150.** q032 and q068 failed reproducibly across two
   separate runs on an upstream `instructor` structured-output error. Four
   content-based explanations were checked and ruled out. They are excluded,
   not imputed (`step8.md` §4a.7).
3. **Faithfulness is the only RAGAS metric here.** Answer Relevancy was
   attempted and found infeasible on this stack after five documented
   attempts (`step8.md` §4a.8). Context Precision is deferred pending the
   rubric-scope question in `step8.md` §2a. Presenting Faithfulness alone
   without saying why is not acceptable under this project's disclosure
   standard.
