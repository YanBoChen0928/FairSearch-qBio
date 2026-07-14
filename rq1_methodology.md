# RQ1 Methodology: Retrieval Parity

**Research question:** Does semantic vector search over-represent papers from
elite institutions when retrieving papers relevant to a query?

**Source notebooks:** `step1b-institution-labels-full-yb.ipynb`,
`step5b-fairness-audit-optionb-yb.ipynb`
**Source docs:** `summary_step1b_OptionB.md`, `handoff_status_rq1_for_step6.md`
**Result file:** `results/rq1_optionB_result.json`
**Owner:** Yan-Bo

---

## 1. Goal

Measure whether the embedding-based retrieval pipeline (all-MiniLM-L6-v2 +
ChromaDB cosine similarity) systematically retrieves papers from elite
institutions (QS World University Rankings 2026 Top-50) at a higher rate than
their true prevalence in the corpus.

---

## 2. Why not label the whole corpus (the v1 problem)

An earlier attempt (v1) tried to label institution affiliation for the full
~55,300-paper corpus via OpenAlex. This failed in two ways:

- **Coverage collapse:** ~82% of papers came back `not_found` in OpenAlex;
  only ~17% of the corpus was usable.
- **Biased baseline:** the papers OpenAlex *could* match cleanly skewed toward
  elite institutions (better metadata, more citations), inflating the
  corpus-wide elite base rate to 0.233 — an overstated reference point.

This made any SPD computed against the v1 baseline unreliable in both
directions: understated statistical power, and an inflated baseline that
understates the true gap.

---

## 3. Option B design: same-method sample vs. retrieved set

Instead of labeling the whole corpus, Option B labels **two small sets with
the exact same method**, so measurement bias cancels out on both sides:

1. **Baseline sample** — a random 1,000-paper sample of the full corpus
   (`sample_labels_1000.json`), fixed seed = 42.
2. **Retrieved set** — the deduplicated Top-10 retrieval results across all
   150 queries (`retrieval_labels.json`): 1,500 slots → 1,366 unique papers.

**Labeling method (identical for both sets):**
1. Query OpenAlex in batches of 50 arXiv ids (OR-syntax), authenticated with
   an API key.
2. Primary lookup: match on `locations.landing_page_url` =
   `http://arxiv.org/abs/<id>` (note: http, not https — OpenAlex stores it
   this way; querying https returns nothing).
3. DOI fallback: for ids missed by the primary lookup, retry via DOI
   `10.48550/arXiv.<id>`.
4. Map results back to arXiv id by parsing the `landing_page_url` list
   (OpenAlex's `ids.arxiv` field is always null — do not rely on it).
5. Elite match: first author's institution, exact case-insensitive match
   against `data/qs_top50_elite_2026.json`.
6. Coverage states: `found` / `no_affiliation` / `not_found`. Only `found`
   papers have a usable `elite_label`; `no_affiliation` and `not_found` are
   excluded from SPD/SRR (they carry no signal either way).

**Measured coverage and elite share:**

| Set | n found (usable) | n elite | elite share |
|---|---|---|---|
| Baseline sample (n=1000) | 438 (44%) | 63 | **0.1438** |
| Retrieved set (1,366 unique) | 798 (58%) | 141 | **0.1767** |

Retrieved-set coverage is higher (58% vs 44%) because retrieved papers tend
to be more mainstream/cited, and such papers are more likely to have
affiliation data in OpenAlex — expected, not an error.

---

## 4. Core fairness metrics: SPD and SRR

**Statistical Parity Difference (SPD):**

```
SPD = retrieved_elite_share - baseline_elite_share
```

- `0` = parity (no difference between retrieved and baseline elite rate).
- `> 0` = elite institutions over-represented in retrieval.
- `< 0` = elite institutions under-represented.

**Selection Rate Ratio (SRR):**

```
SRR = (retrieved_elite_share / baseline_elite_share)
      / (retrieved_other_share / baseline_other_share)
```

- `1.0` = parity.
- `> 1.0` = elite institutions favored (retrieved relatively more often than
  their baseline share would predict).
- `< 1.0` = elite institutions disfavored.

**Scope:** analysis restricted to **neutral queries only (q001–q100)**;
contradictory queries (q101–q150) are held out for RQ2 and excluded here,
since their relevance proxy is undefined (see `label_source` /
`is_relevant = null` convention in the query expansion methodology).

---

## 5. Why bootstrap, not a plain formula or binomial test

The retrieved-set data is **grouped**: 150 queries × 10 papers each. Papers
from the same query are correlated (they answer the same question, often
drawing from similar research circles), so they are **not independent
samples**. Formula-based approaches (normal-approximation CI, a plain
binomial test) assume independent draws — an assumption violated here — and
so they **understate the true uncertainty** (too-narrow CI, artificially
small p-value).

**Bootstrap procedure:** resample the neutral queries (not the papers) with
replacement, 5,000 times; recompute SPD each time using the same baseline
reference (0.144); take the middle 95% of the resulting distribution as the CI.
Resampling queries (not papers) preserves the within-query correlation and
gives an honest interval.

**Binomial test:** kept only as a cross-check, since it assumes independent
papers. Where it disagrees with the bootstrap, **the bootstrap is
authoritative**.

---

## 6. Measured SPD/SRR result (authoritative)

From `results/rq1_optionB_result.json`:

| Metric | Value |
|---|---|
| Baseline elite share | 0.1438 (438 found, seed=42) |
| Retrieved elite share | 0.1767 (798 found) |
| Neutral labeled slots | 590 (102 elite) |
| **SPD (point estimate)** | **+0.0290** |
| **SRR** | **1.2775** |
| SPD bootstrap 95% CI | **[-0.0054, +0.0648]** — crosses 0 |
| Binomial p-value | 0.0462 (nominally "significant", but see §5) |
| **Conclusion** | **Not statistically significant** |

**Reading:** elite institutions are retrieved at a slightly higher rate than
their corpus baseline (17.7% vs 14.4%), but the gap is small and the
bootstrap CI crosses zero — the direction is present but not statistically
distinguishable from no effect at α=0.05. This is consistent with a separate
PCA finding that the embedding model encodes topic, not institutional origin.

---

## 7. Equalized Odds (approximate, within Top-K only)

### 7.1 What true Equalized Odds requires vs. what we can compute

Textbook Equalized Odds requires, per group (elite vs. other): the
**True Positive Rate (TPR)** — the fraction of *all truly relevant papers in
the full candidate pool* that get retrieved — and the **False Positive Rate
(FPR)** on the same basis. Our retrieval log only records relevance labels
for papers that were actually retrieved (the Top-10 slots per query), not for
the full candidate pool. **We cannot compute a textbook TPR/FPR.**

What we compute instead is an **approximation**: within each query's Top-10,
the relevant-share rate per group (a precision-style, within-Top-K rate, not
a corpus-level recall). This is reported explicitly as an approximation with
a stated limitation, not a strict Equalized Odds compliance test.

### 7.2 Calculation

For each neutral query, using only papers with a usable elite/other label:

```
for each of the 10 retrieved papers:
    group = elite | other          (skip if unlabeled)
    is_relevant = (subcategory match == 1)
    tally into: elite_rel, elite_irr, other_rel, other_irr

rate_elite_relevant = elite_rel / (elite_rel + elite_irr)
rate_other_relevant = other_rel / (other_rel + other_irr)

delta_tpr_approx = | rate_elite_relevant - rate_other_relevant |
```

A query is only included if **both groups appear** in its Top-10 (otherwise
there is nothing to compare within that query). Of 100 neutral queries,
**62** met this condition; the mean and 95% CI are computed by bootstrap
(5,000 resamples) over these 62 queries.

### 7.3 Result

| Metric | Value |
|---|---|
| Queries used | 62 / 100 |
| Delta_TPR (approx) mean / median | 0.2817 / 0.2500 |
| Delta_TPR 95% CI | [0.2169, 0.3491] |
| Delta_FPR (approx) mean / median | 0.2817 / 0.2500 (identical by construction*) |

*Delta_FPR mirrors Delta_TPR here because, within a single query's Top-10,
the irrelevant-rate is just `1 - relevant-rate` per group, so the absolute
gap is the same value.

Taken at face value, a ~0.28 average gap looks like a meaningful disparity.
**This number needs the signed-direction check in §7.4 before drawing any
conclusion from it.**

### 7.4 Signed-direction check (critical caveat)

`delta_tpr_approx` uses `abs()`, so a large mean is consistent with two very
different situations: (a) a consistent tilt toward one group across most
queries, or (b) queries swinging in both directions that cancel out in sign
but not in magnitude. To distinguish these, we compute the **signed**
difference instead:

```
signed_diff = rate_elite_relevant - rate_other_relevant
```

**Result (same 62 queries):**

| | Count |
|---|---|
| Elite-favored (signed_diff > 0) | 26 queries |
| Other-favored (signed_diff < 0) | 16 queries |
| Tied (signed_diff = 0) | 20 queries |

| Metric | Value |
|---|---|
| Signed mean | +0.0851 |
| Signed median | 0.0000 |
| Signed mean 95% CI (bootstrap) | **[-0.0100, +0.1759]** — crosses 0 |

**Conclusion:** the CI crosses zero, so there is **no statistically
consistent directional bias**. The large `abs()`-based mean (0.28) is driven
mainly by query-to-query variance swinging in both directions, not a
systematic tilt toward either group. This is consistent with the main
SPD/SRR finding in §6: a weak, non-significant elite tilt overall.

---

## 8. Locked conventions (do not deviate without updating downstream steps)

Per `handoff_status_rq1_for_step6.md`, these are fixed reference values used
by Step 6 (RQ3) and must not be silently changed:

- **Baseline elite share = 0.144** (Option B random-sample baseline, NOT the
  v1 corpus-wide 0.233).
- **Elite definition = QS World University Rankings 2026 Top-50**, exact
  name match.
- **Query scope for RQ1/RQ3 = neutral queries q001–q100 only.**
- **SPD computed over labeled slots only** (unlabeled/no-affiliation papers
  excluded, not treated as "other").

---

## 9. Key limitations (for the report's limitations section)

1. **Equalized Odds is an approximation**, not a textbook computation — no
   full-candidate-pool relevance labels are available, only Top-10 slots.
2. **Coverage is partial** even in the "found" sets (44% baseline, 58%
   retrieved) — papers with no OpenAlex affiliation match are excluded
   entirely rather than imputed.
3. **Binomial test and bootstrap disagree** on significance (p=0.046 vs. CI
   crossing 0) precisely because of within-query correlation; this
   disagreement is itself informative and is reported rather than hidden.
4. **Signed-direction analysis is exploratory**, computed on a sub-sample of
   62/100 queries (those with both groups present in Top-10).

---

*This document consolidates the RQ1 methodology recorded across
`summary_step1b_OptionB.md`, `handoff_status_rq1_for_step6.md`, and the
`step5b-fairness-audit-optionb-yb.ipynb` notebook, for reuse in the Final
Report's Methodology and Results sections.*
