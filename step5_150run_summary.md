# FairSearch-qBio — Status & Discussion (150-query RQ1 run)

Date: 2026-07-02
Prepared by: Yan-Bo (for discussion with Jici, Raj)

## TL;DR
- Ran the full RQ1 retrieval fairness audit on 150 queries (100 neutral + 50 contradictory).
- Retrieval favors elite institutions in the expected direction, but the result is underpowered and not statistically significant.
- The bottleneck is low institution-label coverage (about 17 percent), not too few queries. Going from 50 to 150 queries did not raise coverage.
- Recommendation: revisit Step 1b labeling (see step1b_v2.md, Option B) before the final run.

## Pipeline state
- Corpus: 55,300 q-bio papers (deduplicated).
- Step 1b labels (current, Raj): 7,061 labeled, 48,239 unlabeled. Elite = 1,643, Other = 5,418. Elite base rate within labeled = 0.233. Elite threshold = QS Top-50 (43 institutions).
- Queries: 150 total = q001-050 original neutral, q051-100 expanded neutral, q101-150 contradictory. Still draft (OT allocation and contradictory wording not finalized).
- 5a retrieval: dense only (all-MiniLM-L6-v2 + ChromaDB, K=10). Contradictory queries carry is_relevant = null and are excluded from precision.
- 5b fairness audit: run on the 150-query retrieval output; labels auto-joined by paper_id via kagglehub.

## RQ1 result (neutral queries only, n = 100)
- Retrieved elite share: 0.294 (50 / 170 labeled slots)
- Corpus elite base rate: 0.233
- SPD = +0.061 (positive means elite over-retrieved)
- SRR = 1.374
- SPD 95% CI [+0.010, +0.115] (excludes 0)
- SRR 95% CI [1.057, 1.759]
- Binomial p = 0.069 (not significant at alpha = 0.05)

Tension worth noting: the bootstrap CI excludes 0 (suggests a real effect), but the binomial test sits just above 0.05. This is a statistical power problem: only 170 labeled slots out of 1,000 neutral slots.

Comparison with the earlier 50-query run:
- 50 neutral: n_labeled = 95, elite share 0.274, SPD +0.041, binomial p = 0.333.
- 100 neutral: n_labeled = 170, elite share 0.294, SPD +0.061, CI now excludes 0, p = 0.069.
- The story moved toward a signal but did not cross significance. Direction has been consistent across both runs.

## Coverage (the crux)

| group | n_slots | n_labeled | coverage % | elite_share |
|---|---|---|---|---|
| all | 1500 | 264 | 17.6 | 0.322 |
| original neutral q001-050 | 500 | 95 | 19.0 | 0.274 |
| expanded neutral q051-100 | 500 | 75 | 15.0 | 0.320 |
| all neutral | 1000 | 170 | 17.0 | 0.294 |
| contradictory q101-150 | 500 | 94 | 18.8 | 0.372 |

- Coverage stayed at 15 to 19 percent across every group. More queries did not help.
- 82 percent of retrieved slots are unlabeled and excluded from SPD/SRR.
- Sanity check: the original-50 subset inside this run reproduces the standalone 50-query result (95 labeled, elite share 0.274). The pipeline is consistent.

## Why coverage is the bottleneck (and a confound to disclose)
- OpenAlex affiliation coverage is systematically lower for non-elite, non-English, and Global-South institutions.
- That gap runs in the SAME direction as RQ1 (it makes elite papers easier to label than non-elite ones), so it is a confound, not just random noise.
- Whatever we conclude about RQ1, this must be stated as a methodology limitation.

## Secondary observations
- Contradictory queries retrieved a higher elite share (0.372) than neutral queries (0.294). This is a lead to follow up in RQ2.
- Year bias: newer papers (2020-2026) are under-retrieved (about 0.6x), older papers over-retrieved. Worth one sentence in the report.

## Proposed decision: revisit Step 1b (per step1b_v2.md)
- Option A (v2a): keep whole-corpus labeling, fix the lookup (arXiv id to DOI via 10.48550/arXiv, title fallback). Same schema, so 5b is unchanged. Still inherits the OpenAlex directional bias.
- Option B (v2b, recommended): label a random sample of about 1,000 corpus papers as an unbiased baseline, plus the retrieved set, using the same method for both. SPD = retrieved_elite_share minus baseline_sample_share. This fixes both the coverage bottleneck and the biased baseline. Requires a small edit in 5b (how the baseline share is computed).

## Open items for the team
1. 1b redo: choose Option A or Option B. Threshold QS Top-50 is already in use; please confirm.
2. Raj: commit the actual Step 1b notebook and the elite-institution list to the repo. Right now only the output JSON is in the repo, not the code or the institution list.
3. Handling of unknown affiliations: label them explicitly and exclude, with a selection-bias note.
4. Queries: decide whether to finalize (OT allocation, contradictory wording) before the final run.

## What changes in code if we redo 1b
- 5a: no change (retrieval does not use labels).
- Queries: no change (unless finalized).
- 5b:
  - Option A: basically re-run after Raj republishes labels (same schema and dataset slug). No logic change.
  - Option B: edit the baseline computation so corpus_elite_share uses the random sample instead of the whole labeled corpus. SPD/SRR formula and the coverage table stay the same.

## Reference files
- step1b_v2.md: full 1b redo options and rationale.
- step4_v2.md: query expansion plan (50 to 150) and analysis grouping.
- notebooks/step5-retrieval-baseline-yb-kaggle-150.ipynb: 5a on 150 queries.
- notebooks/step5b_fairness_audit_kaggle.ipynb: 5b fairness audit.
