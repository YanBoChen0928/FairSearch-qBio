# Step 9 Query Subset: Sampling Method, Rationale, and Limitations

**Status:** Decided — a representative subset (not full-150 coverage) is the
team's confirmed approach for Step 9. This document specifies how the
subset is chosen.

**AMENDED 2026-08-01 (see §6).** The subset is now Tier 1 of a tiered
scope, not a fixed ceiling — full 150-query coverage (Tier 2) is pursued if
quota allows, per `step9_plan.md` §8. Read §6 before relying on §1/§5's
original framing.

**Owner:** Yan-Bo
**Depends on:** `queries/queries_all_150.json`, `queries/query_generation_methodology.md`

---

## 1. Why a subset at all

Step 9's diagnostic interface (per `step9_plan.md` §1) needs a **second**
Gemini generation per query in scope — one on the RQ3-intervention
(re-ranked) context, in addition to the baseline generation already done in
Step 7a/7b. Running this on all 150 queries is unnecessary for what the
interface is for:

- RQ3's headline fairness-utility conclusion is already established, on the
  full query set, in `results/rq3_results.json`. Step 9 exists to
  **demonstrate** that conclusion interactively, not to re-derive it or
  improve its statistical power.
- The concept demo (built on a single query, q033) that the team has already
  shown was well received on a "simple" demonstration of fairness results,
  not exhaustive per-query coverage.
- A smaller scope also reduces competition for the same free-tier Gemini
  quota that Step 8's RAGAS evaluation is already using (see §5 below).

## 2. Sampling method

**Target size: ~20 queries** (adjustable; not a hard constraint), sampled to
preserve the structure of the full 150-query set rather than picked by hand.

### 2.1 Preserve the neutral : contradictory ratio

The full set is 100 neutral : 50 contradictory (2:1). The subset follows the
same ratio, e.g. 14 neutral + 6 contradictory for a 20-query subset.

### 2.2 Neutral queries — stratified by subcategory

Per `query_generation_methodology.md` §1.3, the 100 neutral queries are
allocated across 10 q-bio subcategories (QM, PE, NC, BM, SC, MN, GN, TO, CB,
OT). The subset draws **at least 1 query per subcategory** first, then fills
remaining slots proportionally to each subcategory's original allocation
weight. This guarantees all 10 subcategories are represented and prevents a
subset that happens to concentrate on subcategories where the
baseline-vs-intervention shift looks most favorable.

### 2.3 Contradictory queries — spread across distinct debates

The 50 contradictory queries (q101-q150) cover several genuine two-sided
academic debates (e.g. junk DNA functionality, neutral drift vs. selection,
microbiome causality, deep-learning protein-structure prediction — per
`query_generation_methodology.md` §2.4). The subset's contradictory slice is
chosen to span **distinct debate topics** rather than clustering on one.

### 2.4 Fixed random seed

Sampling within each stratum uses **seed=42**, consistent with the seed
already used for bootstrap resampling throughout RQ1/RQ2/RQ3 (e.g.
`rq2_frameworkA_summary.md`, `rq1_methodology.md`). Anyone re-running the
sampling script reproduces the identical query list — this is the concrete,
checkable evidence that the subset was not hand-picked to favor a
particular narrative.

### 2.5 q033 retained as an anchor example

q033 is kept in the subset regardless of what the stratified draw would
otherwise select, since it already exists as a fully-built concept demo
(the HTML mockup Prof. Sushmita reviewed). This is disclosed explicitly as a
retained anchor, not folded silently into the "random" portion of the subset.

## 3. Benefits

- **Defensible against cherry-picking concerns.** A fixed seed plus a
  documented, mechanical selection rule means the subset can be
  regenerated and checked by anyone (teammate, professor, grader) —
  consistent with the project's broader pre-registration discipline.
- **Full subcategory and debate-topic coverage** despite the smaller size,
  so the interface still demonstrates the diagnostic across the breadth of
  the corpus, not just a narrow slice.
- **Materially lower API cost.** ~20 queries x 1 generation call each is
  roughly 20 additional Gemini calls, negligible next to Step 8's
  estimated 1,500-2,000 calls for RAGAS (see §5).
- **Faster to implement and demo-ready sooner**, since Step 9-A/B/C do not
  need to wait on 150-query-scale generation or assembly.

## 4. Limitations (must be disclosed in the report / demo)

- **Not a statistical claim.** The subset exists to demonstrate the
  interface and the already-established RQ3 conclusion, not to provide an
  independent statistical estimate at n=20. All statistical claims about
  RQ3's fairness-utility tradeoff remain grounded in the full-150-query
  result in `results/rq3_results.json`; the subset is illustrative only.
- **q033's retention as a fixed anchor is a deliberate, disclosed
  deviation** from pure random sampling for that one query; it does not
  apply to any other query in the subset.
- **Subcategory floor (>=1 query each) is not proportional** to the
  original allocation weights at this small a sample size, so per-subcategory
  representation in the subset is not intended to mirror the full set's
  exact distribution — only to guarantee no subcategory is entirely absent.
- **Debate-topic spread for contradictory queries is a qualitative
  judgment**, not an algorithmic stratification (unlike the neutral
  subcategory draw), since debate-topic groupings are not currently encoded
  as a field in `queries_all_150.json` / `sides_q101_150.json`. If pursued,
  this should be documented as a manual categorization step before sampling.

## 5. Interaction with Step 8 (quota)

Step 9-A's ~20 extra generation calls and Step 8's RAGAS evaluation (~1,500-
2,000 calls across the full 150 queries) draw from the same free-tier
`gemini-3.1-flash-lite` quota pool, but the two are not in serious
competition: Step 9-A's share is roughly 1% of Step 8's estimated volume.
Step 9-A can proceed independently of however Step 8's quota situation
resolves (see `step8.md` §5 and the Solution 1+2 approach already agreed
with Raj).

## 6. Amendment (added 2026-08-01): tiered scope, not a fixed ceiling

This section amends §1 and §5 above. It does NOT replace the sampling
method in §2 — the ~20-query subset described there is still exactly how
Tier 1 is chosen. What changes is that Tier 1 is no longer the ceiling.

**Why.** §5's original argument was: ~20 extra Gemini calls is negligible
next to Step 8's estimated 1,500-2,000 calls, so a small subset was
justified purely on relative cost. `step8.md` §2a (2026-08-01) deferred
Context Precision, cutting Step 8's committed run to roughly 450 calls.
The relative-cost comparison this section relied on no longer holds at the
same magnitude, so the fixed-20 decision is reopened — see full reasoning
in `step9_plan.md` §8.

**Amended rule (tiered, mirrors `step8.md`'s Faithfulness/Answer-Relevancy/
Context-Precision tiering):**

- **Tier 1 (do this first, unconditionally):** the ~20-query subset, chosen
  exactly per §2's method (stratified, seed=42, q033 retained as anchor).
  This is the guaranteed demo-ready floor regardless of how quota resolves.
- **Tier 2 (extend if quota allows):** the remaining ~130 queries, i.e. full
  150-query coverage.

**Tier 2 is itself run in layers, not as one uninterrupted 130-query batch.**
This mirrors the checkpointing discipline in `step8.md` §4/§6a and the
project's general rule against a single all-or-nothing run:

1. Run Tier 2 in fixed-size batches (e.g. 25-30 queries per batch), writing
   each batch's per-query JSONL checkpoint before starting the next, same
   pattern as `rq2_gen_checkpoint.jsonl`.
2. After each batch, confirm quota headroom remains before starting the
   next batch. If a 429 occurs mid-batch, stop, keep everything already
   checkpointed, and do NOT delete/retry the whole 130-query run — only the
   unfinished batch is at risk, consistent with the project's "delete
   affected records and restart that stage" rule (not the entire run).
3. Tier 2 shares the same free-tier `gemini-3.1-flash-lite` quota pool as
   Step 8's Tier 1/Tier 2 run. Coordinate scheduling so the two do not
   compete for the same daily allowance on the same day if quota turns out
   to be tight (see `step8.md` §5a).
4. Bundle assembly (`step9_plan.md` §10) must record actual coverage
   achieved (e.g. "83 of 150 queries completed") rather than assuming all
   batches finished. The interface displays this number; it is not
   hard-coded to 150.

**What does NOT change:** the sampling method in §2, the disclosure
requirements in §4, and Tier 1 always running to completion before any
Tier 2 batch starts.
