# Step 6 — Fair-Top-K Re-ranking Methodology (RQ3 contrast arm)

**Created 2026-08-02.** Companion to `rq3_methodology.md`, which covers the
two MMR arms (`mmr_semantic_by_lambda`, `mmr_institution_by_lambda`). This
file is the single authoritative source for the Fair-Top-K algorithm
specifically. `rq3_methodology.md` should link here, not duplicate this
content, once this file exists.

**Status: design spec, not yet run.** Verified against the notebook cells
below on 2026-08-02, before writing a line of new code, per this project's
"verify before coding" rule.

---

## 0. Verified facts this design depends on

Read directly from
`notebooks/step6-reranking-yb-optimized-basedon-jici.ipynb` on 2026-08-02.
Nothing below is assumed.

| Fact | Source | Value |
|---|---|---|
| Candidate pool size | Cell 4 | `N_CANDIDATES = 50` |
| Final cutoff | Cell 4 | `K = 10` |
| Corpus baseline elite share | Cell 4 | `BASELINE_SHARE = 0.144` |
| Pool element shape | Cell 10 | tuple `(paper_id, rel, row)` |
| Pool ordering | Cell 10 | already sorted by `rel` **descending**; `rel = 1 - idx/n`, seeded with the stored Step 5a Top-10, then filled with embedding neighbours |
| Label lookup | Cell 8 | `label_of[pid] = {'coverage', 'institution', 'country', 'elite_label'}` |
| `coverage` domain | Cell 8, 12 | `'found'` / `'no_affiliation'` / `'not_found'` |
| `elite_label` domain | Cell 8, 12 | `1` / `0` / `None` (only meaningful when `coverage == 'found'`) |
| Generic eval harness | Cell 17 | `evaluate(ranker)` — accepts any `ranker(pool) -> [paper_ids]`, returns NDCG@10, MRR, SPD, uniq_institutions, uniq_countries, elite_share, labeled_slots |
| Existing rankers as templates | Cell 15, 21 | `rerank_mmr(pool, lam)`, `rerank_labelaware(pool, lam, field, graded)` |
| Output assembly | Cell 29 | single `out` dict written to `results/rq3_results.json` |
| Query scope | Cell 6 | neutral `q001`–`q100` only (contradictory queries held out, see `handoff_status_rq1_for_step6.md`) |

---

## 1. Why this arm exists despite RQ1's null result

Short version — full quantitative arguments live in `Claude_todo_memo.md`
§000 and should not be duplicated here.

```
+---------------------------+     +----------------------------+
|  RQ1: diagnosis           |     |  RQ3: what does a proposed |
|  "is there a disease?"    |     |   treatment cost?"         |
|                           |     |                             |
|  Result: not detected     |     |  A separate question from  |
|  (CI crosses zero)        |     |  "is there a disease".     |
+---------------------------+     +----------------------------+
```

The rubric names Fair-Top-K explicitly alongside MMR. This project's own
RQ1 result does not exempt it from being demonstrated -- it changes how the
result should be *framed* (a contrast arm showing the cost of a hard quota,
not a recommended fix for a confirmed problem).

---

## 2. What "Fair-Top-K" means here, vs. the existing Top-K

The project's stored Step 5a baseline is already "Top-K" -- plain
similarity ranking, no group awareness:

```
Candidate pool (sorted by rel, descending, group-blind)
+------------------------------------+
| 1. p_a  rel=1.00  elite            |
| 2. p_b  rel=0.98  non-elite        |
| 3. p_c  rel=0.96  elite            |
| 4. p_d  rel=0.94  unknown          |
| 5. p_e  rel=0.92  non-elite        |
| ...                                 |
+------------------------------------+
        v cut at K=10, no group logic
   This is the existing baseline / Cell 17's `baseline`.
```

Fair-Top-K keeps each group's *internal* ordering by `rel`, but overrides
*which slot* gets filled from which group:

```
elite (rel-sorted)      non_elite (rel-sorted)      unknown (rel-sorted)
+--------+               +--------+                  +--------+
| p_a    |               | p_b    |                  | p_d    |
| p_c    |               | p_e    |                  | p_g    |
| ...    |               | ...    |                  | ...    |
+--------+               +--------+                  +--------+
     strict alternation between these two, unknown fills only
     once BOTH of the above are exhausted (section 3).
```

---

## 3. Algorithm definition

### 3.1 Three buckets, order preserved

```python
def group(pid):
    lab = label_of.get(pid)
    if lab and lab['coverage'] == 'found':
        return 'elite' if lab['elite_label'] == 1 else 'non_elite'
    return 'unknown'
```

Filter the pool into three lists, preserving the pool's existing
descending-`rel` order (a stable filter, not a re-sort):

```python
elite_q     = [(pid, rel) for (pid, rel, row) in pool if group(pid) == 'elite']
non_elite_q = [(pid, rel) for (pid, rel, row) in pool if group(pid) == 'non_elite']
unknown_q   = [(pid, rel) for (pid, rel, row) in pool if group(pid) == 'unknown']
```

### 3.2 Pre-registered quota rule -- OPTION A, corpus-parity target (decided 2026-08-02)

**This section replaces an earlier draft of this rule** (strict 1:1
alternation between elite and non-elite). That draft is wrong for this
project and must not be implemented. Reasoning:

A strict 1:1 alternation targets a 50% elite share. This project's fairness
definition is **corpus parity**, not demographic parity -- the SPD metric
used everywhere else (RQ1, both MMR arms) is defined against
`BASELINE_SHARE = 0.144`, not against 0.5. Checked against the actual
candidate-pool composition (`data/candidate_labels.json` meta: elite share
0.1796 among found candidates), a strict 1:1 rule would force the realized
elite share toward 50%, which is **more than three times further from
0.144 than the current baseline (0.1729)** -- the quota would make SPD
worse, not better, and in the wrong direction. This was caught before any
code was run.

**Decided rule: the quota target is `BASELINE_SHARE` (0.144), the same
number every other RQ3 arm and RQ1 use.**

1. **Elite seat target**, computed from existing config, not hardcoded:
   ```python
   ELITE_QUOTA = round(K * BASELINE_SHARE)   # round(10 * 0.144) = 1
   ```
2. **Fill the elite quota first**, taking up to `ELITE_QUOTA` candidates
   from `elite_q` in its existing `rel` order (highest relevance first). If
   `elite_q` has fewer than `ELITE_QUOTA` candidates in a given pool, take
   however many exist -- no fabricated candidates, no borrowing from other
   queries.
3. **Fill all remaining slots from `non_elite_q`**, in its existing `rel`
   order, until `K` is reached or `non_elite_q` is exhausted.
4. **If `non_elite_q` runs out before `K` is reached, fall back to
   `elite_q`'s leftover candidates** (if any remain beyond the quota) before
   touching `unknown_q` -- a labeled candidate, of either group, carries
   more signal than an unlabeled one.
5. **Only once both `elite_q` and `non_elite_q` are exhausted**, fill any
   remaining slots from `unknown_q`, in its existing `rel` order.
6. Stop at `K = 10` regardless of which bucket is being drawn from.

No alternation step is needed under this design -- the quota is a **cap**
on elite seats, not a 50/50 turn-taking rule. This is closer to how
FA*IR-style hard quotas from the fairness-in-ranking literature are usually
framed (a minimum/maximum proportion constraint), and it is the design that
is actually consistent with this project's own SPD definition.

### 3.2a Honest caveat: the "resolution" argument needs re-checking at the pooled level

`evaluate()` computes SPD by **pooling** `elite` and `found` counts across
all 100 queries first, then taking one ratio (`pooled_elite / pooled_found`,
Cell 17) -- it does **not** average 100 separate per-query SPD values. This
matters for how strong the "quota resolution is too coarse" argument
actually is:

- **At the single-query level**, the argument is airtight: `ELITE_QUOTA` is
  forced to be an integer (1, under the current config), so no single query
  can realize the fractional target of 1.44. This part is not in question.
- **At the pooled level** (which is what the headline SPD number in
  `results/rq3_results.json` actually reports), pooling over 100 queries can
  average out per-query integer rounding, the same way averaging many
  discrete draws approximates a continuous number. Measured baseline data
  makes this concrete: baseline `labeled_slots` = 590 over 100 queries
  (5.9/query average), and baseline `elite_share` = 0.1729, implying
  **roughly 1.02 elite papers per query already occur under the unconstrained
  baseline** -- very close to the `ELITE_QUOTA = 1` this design would force.
  Whether the forced quota meaningfully changes the pooled SPD, worsens it,
  or barely moves it, is **an empirical question this design does not
  pre-answer**, and it must not be asserted with specific numbers before the
  run produces them.

**Do not write the earlier draft's illustrative grid values (-0.044 /
+0.056) into any report section as if measured.** Those were computed under
a simplifying assumption (a clean, fixed denominator of 10) that does not
match the actual measured baseline (a varying, averaging-5.9 denominator).
The per-query resolution argument survives; the specific pooled-level
numbers do not exist yet.

### 3.3 Trace, illustrative only -- NOT measured data

Toy example to show the mechanics under the Option A quota rule (section
3.2). Placeholder ids `p1`..`p9`, not real paper ids, not real relevance
values. `ELITE_QUOTA = 1` for the current config.

```
elite_q:     [p1(.95), p3(.80)]              (2 available, quota needs only 1)
non_elite_q: [p2(.90), p5(.70), p7(.60), p9(.55)]
unknown_q:   [p4(.85), p6(.65), p8(.58)]

ELITE_QUOTA = round(10 * 0.144) = 1

slot 1: elite     -> p1          (quota filled: 1 of 1; p3 stays unused)
slot 2: non_elite -> p2
slot 3: non_elite -> p5
slot 4: non_elite -> p7
slot 5: non_elite -> p9          (non_elite_q now empty)
slot 6: elite     -> p3          (non_elite exhausted -> fall back to leftover elite)
slot 7: unknown   -> p4          (both labeled groups now exhausted -> unknown fills)
slot 8: unknown   -> p6
slot 9: unknown   -> p8
slot 10: (pool exhausted at 9 in this toy example; real pools have 50 candidates)
```

Result composition in this toy trace: 2 elite, 4 non_elite, 3 unknown. Note
that even under the Option A design, if `non_elite_q` runs dry before
`elite_q` fully backs off, extra elite candidates can still enter beyond
the quota (slot 6 above) -- the quota is a *floor-priority cap on the first
pass*, not an absolute ceiling on the final composition, because rule 4
(section 3.2) prefers a labeled leftover candidate over an unlabeled one.
**This is a design property to disclose explicitly**, not an error: it
keeps unknown-group candidates from being favored simply because a quota
was hit, which would be a strange thing for the report to defend.

**This is also the important correction to the "clean 1:1" framing used
earlier in conversation**, before Option A was decided: the realized
composition depends on each pool's actual supply and will not be a clean
split by construction. The report must show the *actual* measured
distribution once this runs, not assume one.

---

## 4. Function to add (verified against real variable names, not pseudocode)

To be pasted into a new code cell after Cell 21 (`rerank_labelaware`), so it
sits next to its sibling rankers:

```python
ELITE_QUOTA = round(K * BASELINE_SHARE)   # round(10 * 0.144) = 1

def rerank_fair_top_k(pool):
    """Deterministic hard-quota re-ranking, Option A (corpus-parity target,
    NOT 1:1 demographic parity). Reserves up to ELITE_QUOTA seats for elite
    candidates (by the pool's existing rel order), fills the rest from
    non-elite, falls back to leftover elite before touching unlabeled
    candidates, and uses unlabeled only once both labeled groups are
    exhausted. No lambda -- this method has no hyperparameter to tune.
    Pre-registered rule, see step6_fair-top-k_methodology.md section 3.2."""
    def group(pid):
        lab = label_of.get(pid)
        if lab and lab['coverage'] == 'found':
            return 'elite' if lab['elite_label'] == 1 else 'non_elite'
        return 'unknown'

    elite_q     = [pid for (pid, rel, row) in pool if group(pid) == 'elite']
    non_elite_q = [pid for (pid, rel, row) in pool if group(pid) == 'non_elite']
    unknown_q   = [pid for (pid, rel, row) in pool if group(pid) == 'unknown']

    selected = []
    # Step 1: fill the elite quota (up to ELITE_QUOTA, capped by supply).
    n_elite_seats = min(ELITE_QUOTA, len(elite_q))
    selected.extend(elite_q[:n_elite_seats])
    elite_leftover = elite_q[n_elite_seats:]

    # Step 2: fill remaining slots from non-elite.
    remaining = K - len(selected)
    selected.extend(non_elite_q[:remaining])
    non_elite_used = min(remaining, len(non_elite_q))

    # Step 3: if still short, fall back to leftover elite before unknown.
    remaining = K - len(selected)
    if remaining > 0:
        selected.extend(elite_leftover[:remaining])
        remaining = K - len(selected)

    # Step 4: only once both labeled groups are exhausted, use unknown.
    if remaining > 0:
        selected.extend(unknown_q[:remaining])

    return selected[:K]
```

## 4a. Provenance of `N_CANDIDATES = 50` (retrospective note, not a design justification)

`N_CANDIDATES = 50` is inherited from Jici's original Step 6 implementation
(Cell 0 credits Jici as owner). It is byte-identical between
`step6_reranking.ipynb` and the current optimized notebook, and no project
document records why 50 was chosen. `rq3_methodology.md` §9 limitation 1
already names its known consequence: "diversity gains plateau at lambda<=0.8
partly because the pool itself has limited institutional variety."

**This paragraph is a retrospective observation, written after the fact,
and must be labeled as such wherever it is cited** -- it is not being
offered as the original reason 50 was chosen, per this project's standing
rule against post-hoc rationalization. Checked against
`data/candidate_labels.json`, the candidate-pool elite share is 0.1796
among found candidates; for the Option A quota (`ELITE_QUOTA = 1` per
query), a pool of 50 appears to give adequate elite supply in aggregate.
Whether every individual query's pool has at least one elite candidate is
not yet verified per-query and must be checked once the run completes,
per section 3.3's caveat.

## 5. How it plugs into the existing pipeline

No changes to `evaluate()` (Cell 17) -- it already accepts any
`ranker(pool) -> [paper_ids]`. Run it exactly like the existing baseline
call:

```python
fair_top_k = evaluate(rerank_fair_top_k)
print(json.dumps(fair_top_k, indent=2))
```

Add one key to Cell 29's `out` dict:

```python
out = {'baseline': baseline,
       'mmr_semantic_by_lambda': rows,
       'mmr_institution_by_lambda': rows_inst,
       'fair_top_k': fair_top_k,          # <-- new
       'diversity_gain_ci': diversity_ci,
       ...
```

No new file, no new schema -- `results/rq3_results.json` gains one key.

---

## 6. Important interpretation caveat: what `evaluate()` counts

`label_stats()` (Cell 15) only counts `coverage == 'found'` slots toward
`uniq_institutions`, `elite_share`, and `SPD`. This means:

- Unknown-group slots that Fair-Top-K places in the Top-10 **do not appear
  in the SPD calculation at all** -- they occupy real estate but are
  invisible to the fairness metric.
- If a query's pool is elite-thin or non-elite-thin (section 3.3), the
  *realized* elite:non-elite ratio among the `found` slots may not be 1:1,
  even though the algorithm alternated strictly while it could.
- **Report the actual measured distribution once this runs.** Do not assume
  or state a clean 1:1 split without checking `labeled_slots` and the
  per-arm elite/non-elite counts in the output.

---

## 7. Comparison table (headline presentation)

**Compares against `mmr_institution_by_lambda` (institution-aware MMR),
NOT `mmr_semantic_by_lambda`.** Reason: only the institution-aware arm
targets the same axis as Fair-Top-K (institutional/elite-share fairness).
Semantic MMR targets embedding-space topical diversity, which
`rq3_methodology.md` §3 already shows barely moves institution metrics --
it is the reason the institution-aware variant was built in the first
place. Semantic MMR may still be mentioned as background context (how weak
topic-only diversification is on this axis), but it does not belong in the
same head-to-head comparison as a peer arm.

The operating point for institution-aware MMR is lambda=0.8, the value
already selected in `rq3_methodology.md` §7c/§8 on independent
diversity/utility-plateau grounds (not chosen via this comparison).

| Ranker | NDCG@10 | MRR | uniq_institutions | uniq_countries | elite_share | SPD |
|---|---|---|---|---|---|---|
| Baseline | 0.8092 | 0.7506 | 5.49 | 4.04 | 0.1729 | +0.0289 |
| Institution-aware MMR (lambda=0.8) | 0.8090 | 0.7520 | 5.73 | 4.17 | -- | +0.016 |
| Fair-Top-K (Option A) | -- | -- | -- | -- | -- | -- |

Baseline and MMR rows are the only measured values that exist as of
2026-08-02 (from `results/rq3_results.json`); the MMR row's `elite_share` is
not separately stored in that file (only SPD is), and the Fair-Top-K row is
entirely pending the Kaggle run. **Do not fill in placeholder numbers before
the run.** A one-paragraph interpretation should sit under this table once
real numbers exist, addressing: which method moves `uniq_institutions` more,
which moves `SPD` more, and what each costs in `NDCG@10`.

---

## 8. Pre-registration log

| Decision | Made | Rationale |
|---|---|---|
| Quota target = `BASELINE_SHARE` (0.144), NOT 1:1 demographic parity | 2026-08-02, before running (revised from an earlier 1:1 draft) | Aligns with this project's own SPD definition; 1:1 would push SPD further from 0.144, not closer |
| `ELITE_QUOTA = round(K * BASELINE_SHARE)` computed from config, not hardcoded | 2026-08-02, before running | Deterministic, ties the quota to the exact same baseline number RQ1/MMR use |
| Unknown fills only after BOTH primary groups exhausted (not either) | 2026-08-02, before running | Unknown carries no elite/non-elite signal; exhaust labeled supply first |
| Elite leftovers (beyond quota) still eligible if non-elite runs dry, before unknown | 2026-08-02, before running | A labeled candidate carries more signal than an unlabeled one, even if it is elite |
| No lambda / no ablation grid for this method | 2026-08-02 | Fair-Top-K is parameter-free by construction; this is a property to report, not a limitation |
| Reuses `label_of`, `elite_label`, `coverage` exactly as RQ1/RQ3 do | 2026-08-02 | Same-ruler discipline -- no new labeling method introduced |
| Compared against institution-aware MMR, not semantic MMR | 2026-08-02 | Only the institution-aware arm targets the same fairness axis |

---

## 9. Open items, not yet decided

- Whether to also report a per-query composition table (elite / non_elite /
  unknown counts actually realized), given section 6's caveat. Recommended:
  yes, at least as a summary distribution, since the realized composition
  is not guaranteed by construction (section 3.3).
- Whether Fair-Top-K needs its own bootstrap CI (mirroring Cell 25's
  `bootstrap_spd`) for comparability with the two MMR arms. Not yet
  decided; cheap to add once the base run exists, since `bootstrap_spd()`
  is already generic over any `(elites, founds)` arrays.
- Whether the pooled-level resolution effect (section 3.2a) turns out to be
  material once the run completes -- flagged as an open empirical question,
  not something this document can resolve in advance.
