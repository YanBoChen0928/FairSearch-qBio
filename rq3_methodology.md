# RQ3 Methodology: Fairness-Utility Tradeoff

**Research question:** What is the fairness-utility tradeoff when applying
MMR-style re-ranking to the retrieved Top-10? Does re-ranking raise diversity
at an acceptable utility cost, and does it over-correct?

**Source notebook:** `step6-reranking-yb-optimized-basedon-jici.ipynb`
**Result file:** `results/rq3_results.json`
**Owner:** Jici (implementation), building on RQ1's Option B labels

---

## 1. Goal and framing decision (read this before the numbers)

RQ3 depends on RQ1: "Because RQ1 bias is small and non-significant, RQ3 is
**not** framed as 'push elite down'." Instead, the question studied is
narrower and more honest: *given a low-bias starting point, can re-ranking
raise diversity at a small utility cost, and does it over-correct?*

This framing matters for interpretation throughout this document — a
significant SPD improvement here should **not** be read as "correcting a
proven bias", since RQ1 found no such bias to correct (see §7 for why).

**Locked conventions** (from `handoff_status_rq1_for_step6.md`, reused here):
baseline elite share = **0.144** (Option B random-sample baseline), elite =
**QS Top-50** exact name match, neutral queries **q001–q100** only, SPD
computed over labeled slots only.

---

## 2. Baseline (Step 5a stored Top-10, i.e. "before" re-ranking)

| Metric | Value |
|---|---|
| NDCG@10 | 0.8092 |
| MRR | 0.7506 |
| Semantic diversity | 0.3797 |
| Unique institutions (avg per query) | 5.49 |
| Unique countries (avg per query) | 4.04 |
| Elite share | 0.1729 |
| SPD (vs. 0.144 baseline) | +0.0289 |
| Labeled slots | 590 |

This baseline is identical to RQ1's retrieval-stage measurement (SPD +0.029)
by construction — RQ3 starts from the same retrieved Top-10 that RQ1 audited.

---

## 3. Two MMR variants (the key methodological choice)

Both variants use the same greedy MMR selection loop, choosing one document
at a time to maximize `score = λ·rel(d) − (1−λ)·div(d)`, seeded with the
stored Top-10 pool so **λ=1.0 always reproduces the baseline exactly**. They
differ only in how `div(d)` (the diversity/penalty term) is computed:

### 3.1 Semantic MMR (Section 6) — diversifies in *topic* space

```
div(d) = max cosine similarity between d's embedding and already-selected docs
```

This is the classic Carbonell & Goldstein (1998) formulation. It diversifies
in **embedding = topic** space — it makes the Top-10 topically varied, but
has **no direct target on institution**.

### 3.2 Institution-aware MMR (Section 7b) — diversifies on the *label*

```
penalty(d) = count of already-selected docs sharing d's institution (graded)
           = 1 if any already-selected doc shares d's institution (binary, "graded=False")
score(d) = λ·rel(d) − (1−λ)·penalty(d)
```

Unlabeled candidates (no OpenAlex-found affiliation) get **zero penalty** —
they are neither rewarded nor punished for being unlabeled. This variant
directly targets **institutional diversity**, which is the actual RQ3 goal;
semantic MMR was tried first and found to barely move the institution metrics
(diversifying topic ≠ diversifying institution), motivating the label-aware
variant.

Two penalty modes were implemented: **graded** (penalty grows with each
repeat: 0, 1, 2, ...) and **binary** (penalty saturates at 1 after the first
repeat). The graded variant is used for the headline results below, since it
gives a smoother, less abrupt tradeoff curve.

---

## 4. Lambda sweep results

### 4.1 Semantic MMR (topic-space diversity)

| λ | NDCG@10 | MRR | SPD |
|---|---|---|---|
| 1.0 (baseline) | 0.8092 | 0.7506 | +0.029 |
| 0.9 | 0.8104 | 0.7523 | +0.029 |
| 0.8 | 0.8143 | 0.7591 | +0.026 |
| 0.7 | 0.8138 | 0.7561 | +0.024 |
| 0.6 | 0.8142 | 0.7609 | +0.017 |
| 0.5 | 0.8116 | 0.7576 | +0.023 |
| 0.4 | 0.8109 | 0.7569 | +0.011 |
| 0.3 | 0.8101 | 0.7584 | +0.030 |

**Reading:** NDCG@10 stays essentially flat or slightly *improves* across the
whole sweep (diversity-aware retrieval surfaces relevant documents pure
similarity search overlooks). SPD moves around but non-monotonically, and by
construction (topic-space diversity) never targets institution directly —
confirming the motivation for the institution-aware variant in §3.2.

### 4.2 Institution-aware MMR (label-space diversity, graded penalty)

| λ | NDCG@10 | MRR | Unique institutions | Unique countries | SPD |
|---|---|---|---|---|---|
| 1.0 (baseline) | 0.8092 | 0.7506 | 5.49 | 4.04 | +0.029 |
| 0.99 | 0.8092 | 0.7506 | 5.50 | 4.05 | +0.027 |
| 0.98 | 0.8093 | 0.7520 | 5.56 | 4.09 | +0.029 |
| 0.95 | 0.8091 | 0.7520 | 5.58 | 4.10 | +0.024 |
| 0.9 | 0.8087 | 0.7520 | 5.66 | 4.14 | +0.020 |
| **0.8** | 0.8090 | 0.7520 | **5.73** | **4.17** | **+0.016** |
| 0.6 | 0.8090 | 0.7520 | 5.73 | 4.17 | +0.017 |
| 0.4 | 0.8090 | 0.7520 | 5.73 | 4.17 | +0.017 |

**Reading:** unique institutions and countries per query rise as λ decreases,
**plateauing around λ=0.8** (no further gain at 0.6 or 0.4 — the penalty has
already exhausted the diversity available in a pool of 50 candidates). NDCG@10
stays flat across the entire sweep. SPD reaches its lowest point around λ=0.8.

**Operating point selection (pre-registered reasoning, not post-hoc):**
λ=0.8 was chosen based on the **diversity plateau + flat NDCG@10 + lowest
SPD** combination visible in this sweep — **not** based on the SPD
significance test in §6, which was run afterward at this fixed λ.

---

## 5. Diversity-gain significance check (unique institutions)

At λ=0.9 (the sweep point used to illustrate the trend in §4.2), bootstrap
95% CI on the gain in unique institutions per query (resampling queries,
seed 42, 10,000 draws — same method as RQ1):

| Metric | Value |
|---|---|
| λ | 0.9 |
| Mean gain (unique institutions) | +0.17 |
| 95% CI | [0.09, 0.26] |
| Significant (CI excludes 0) | **Yes** |

This confirms institution-aware MMR does measurably increase institutional
diversity per query, at negligible utility cost (§4.2).

---

## 6. SPD significance checks at the operating point (λ=0.8)

Two separate bootstrap checks (query-resampling, seed=42, n_boot=10,000 —
identical logic to RQ1's bootstrap, reused directly), both computed at the
chosen operating point λ=0.8:

### 6.1 (A) Absolute — is the post-rerank SPD itself different from 0?

| Metric | Value |
|---|---|
| Institution-aware SPD at λ=0.8 | **+0.0162** |
| 95% CI | **[-0.0139, +0.0484]** — crosses 0 |
| Significant | **No** |

### 6.2 (B) Improvement — is the drop from baseline SPD significant?

Paired bootstrap: the *same* resampled query indices are applied to both the
baseline and institution-aware arms in each draw, so the comparison is
apples-to-apples per resample.

| Metric | Value |
|---|---|
| SPD improvement (baseline − institution-aware) | **+0.0126** |
| 95% CI | **[0.0013, 0.0254]** — excludes 0 |
| Significant | **Yes** |

**Reading:** the post-rerank SPD is not itself distinguishable from zero, but
the *improvement* over baseline is statistically significant. These two
results are not contradictory — SPD dropped from a already-small +0.029 to a
smaller-still +0.016, and the paired bootstrap detects that consistent
per-query drop even though the post-rerank value alone isn't far enough from
zero to clear significance on its own.

### 6.3 Statistical power (added 2026-08-09) — read before citing §6.2

Source: `results/rq3_power_analysis.json` and
`notebooks/power_analysis_rq3.ipynb` (Jici, merged 2026-08-09), simulated at
the λ=0.8 operating point, 3000 bootstrap replicates per target, 2000
replicates per point.

| Test | MDE at 80% power | Power at observed |
|---|---|---|
| Absolute SPD (§6.1) | 0.0459 | **0.229** |
| Paired improvement (§6.2) | 0.0577 | **0.091** |

**Two caveats follow, and both must travel with the §6.2 result.**

**(1) The significant improvement in §6.2 was found at 9% power.** The
paired test could only reliably detect an improvement of about 0.058; the
observed improvement is 0.0126, roughly a fifth of that. Obtaining
significance under such low power is not evidence of a large effect — if
anything it warrants more caution, because in low-power designs the subset of
effects that do reach significance is biased upward in magnitude (the
"winner's curse" / Type M error). The §6.2 result should therefore be
reported as **borderline and exploratory**, not as a robust demonstration,
and the point estimate 0.0126 should not be treated as a reliable estimate of
the true improvement size. This reinforces, rather than weakens, the §7
argument that the improvement is a de-duplication side effect rather than a
corrected bias.

**(2) The power analysis input is a local reconstruction, not the official
run.** Jici's notebook reconstructs the per-query institution-aware data
locally. Per `results/rq3_power_analysis.json`, the baseline arm reproduces
RQ1 exactly, but the institution-aware arm is close without being
bit-identical to the officially reported run:

| Quantity | Reconstructed | Official (§6) |
|---|---|---|
| Absolute SPD at λ=0.8 | 0.0187 | 0.0162 |
| Paired improvement | 0.0104 | 0.0126 |

The power figures are therefore approximate. The gap is small enough that the
qualitative conclusion (this design is badly underpowered for the improvement
test) is unaffected, but the MDE and power numbers should be cited as
approximate and attributed to the reconstruction, not presented as exact
properties of the official run.

---

## 7. Why the significant SPD improvement is a de-duplication side effect, not a corrected bias

This is the most important interpretive point in RQ3, and it follows directly
from the mechanism in §3.2: the institution-aware MMR penalty fires whenever a
candidate shares an institution with an **already-selected** document — it
penalizes **institutional duplication**, not "eliteness" specifically. An
elite-institution paper is only penalized if another paper from the *same*
institution was already selected; a non-elite paper repeating its institution
is penalized identically.

Because elite institutions (e.g. large, prolific universities) are more likely
to have **multiple** papers competing for the same Top-10 slots in the
original candidate pool, de-duplicating by institution disproportionately
removes *some* elite repeats — producing a measurable SPD drop as a **side
effect** of diversification, not because the re-ranker was told to target
elite status.

**Practical consequence for how this result should be read and reported:**
the significant SPD improvement in §6.2 should **not** be presented as
"RQ3 corrects the institutional bias found in RQ1" — RQ1 found no
statistically significant bias to correct. The more accurate framing,
consistent with §1's framing decision, is: *institution-aware re-ranking, when
applied for its own sake (raising institutional diversity), incidentally also
produces a small, measurable reduction in elite over-representation, as a
by-product of de-duplication rather than a targeted correction.*

---

## 8. Configuration (for reproducibility)

From `results/rq3_results.json`:

| Setting | Value |
|---|---|
| Baseline elite share (reference) | 0.144 |
| Elite definition | QS Top-50 |
| Candidate pool size per query | 50 |
| Top-K | 10 |
| Number of queries | 100 (neutral, q001–q100) |
| Baseline source | Stored Step 5a Top-10 (`retrieval_results.json`) |
| Bootstrap | Seed 42, 10,000 resamples, query-level (not paper-level) |

---

## 8a. Third mitigation arm: Fair-Top-K (contrast arm, rubric-named method)

The rubric names Fair-Top-K alongside MMR under Mitigation. This project's
own RQ1 result (SPD not significant) reframes it from a bias correction to
a **contrast arm**: what does a hard quota cost, and how does it compare to
MMR's soft penalty, at this project's own corpus-parity target (0.144, not
50/50 demographic parity)? Full algorithm and pre-registration log live in
`step6_fair-top-k_methodology.md` -- that file is the authoritative source
for the design decisions; this section reports the measured result.

**Measured result (2026-08-03 Kaggle run):**

| Metric | Value |
|---|---|
| NDCG@10 | 0.8108 |
| MRR | 0.7819 |
| Unique institutions (avg per query) | 9.35 |
| Unique countries (avg per query) | 5.98 |
| Elite share | 0.098 |
| SPD (vs. 0.144 baseline) | **-0.046** |
| Labeled slots | 1000 (of 1000 possible -- see caveat below) |

**Bootstrap checks (same query-resampling method as §6, 10,000 resamples,
seed 42):**

| Check | Value | Significant? |
|---|---|---|
| Absolute SPD | -0.0460, 95% CI [-0.0490, -0.0440] | **Yes** -- entirely negative, excludes zero |
| SPD change vs. baseline (`share_base - share_ftk`) | +0.0748, 95% CI [0.0409, 0.1108] | **Yes** -- excludes zero |

**This is a confirmed statistically significant over-correction, not a
clean fix.** Unlike institution-aware MMR (§6.1, SPD not itself
distinguishable from zero), Fair-Top-K's post-rerank SPD is itself
significant -- and negative, meaning the hard quota pushed representation
past parity into favoring non-elite institutions, with the direction
confirmed by bootstrap rather than assumed from the point estimate alone.

**Two caveats that must accompany this result wherever it is cited:**

1. **NDCG@10/MRR are not degraded relative to baseline** (both are
   marginally higher). This is NOT evidence that hard quotas carry no
   relevance cost in general -- `relevance()` (§5) is a coarse binary
   subcategory-string-match proxy, not a graded relevance judgment, so the
   quota's reordering can coincidentally help this specific proxy metric
   without implying the swapped-in candidates are more relevant in any
   richer sense.
2. **`uniq_institutions = 9.35` is partly a rule artifact.**
   `labeled_slots` rose from 590 (baseline) to 1000 (= 100 queries x 10
   slots, i.e. every slot labeled), because the quota rule only falls back
   to unlabeled ("unknown") candidates once both elite and non-elite are
   exhausted -- which this run essentially never needed to do. Part of the
   apparent diversity gain is this near-elimination of unlabeled slots
   rather than a pure increase in genuine institutional variety.

---

## 9. Key limitations (for the report)

1. **Candidate pool is capped at 50 per query** — diversity gains plateau at
   λ≤0.8 partly because the pool itself has limited institutional variety;
   a larger candidate pool might allow further diversification.
2. **Unlabeled candidates get zero penalty** in the institution-aware
   re-ranker — they are treated as institutionally "free," which could
   under- or over-state the true diversity effect depending on who is
   actually unlabeled.
3. **The SPD improvement is a side effect of de-duplication**, not a
   targeted correction (§7) — this must be stated explicitly whenever the
   λ=0.8 result is cited, to avoid overclaiming.
4. **Operating point (λ=0.8) was chosen from the diversity/utility tradeoff
   curve**, not from the significance test — this ordering is intentional
   (avoids picking λ post-hoc to maximize significance) and should be stated
   as such.
5. **RQ1's null result constrains how RQ3 can be framed** — since no
   significant retrieval-stage bias was found, RQ3 cannot be presented as
   "fixing a proven problem"; see §1.

---

## 10. Relation to RQ1 and RQ2, and the two mitigation arms compared

- **RQ1** provides the baseline (SPD +0.029, not significant) that RQ3's
  "before" state is identical to by construction (§2).
- **RQ2** (Framework A) found no generation-stage citation amplification to
  correct for, which is why the optional "Framework A × RQ3" linkage
  (re-running Framework A's citation-parsing on RQ3's re-ranked context) was
  decided **not necessary** — see `rq2_rq3_linkage_plan.md`. RQ2's
  perspective-balanced-prompting mitigation was similarly never triggered,
  since Framework B's baseline viewpoint retention was already 97.2%.
- **RQ3's two mitigation arms are not interchangeable, even starting from
  the same low-bias baseline.** Institution-aware MMR (§4.2, §6) raises
  unique institutions per query significantly (+0.170, CI [0.090, 0.260])
  while its own SPD stays statistically indistinguishable from zero (CI
  crosses zero) — a clean diversity gain with no detectable directional
  bias. Fair-Top-K (§8a) significantly overcorrects into reverse bias (SPD
  -0.046, CI entirely negative) at the same Top-10 depth and the same
  0.144 fairness target. The two methods answer "does re-ranking raise
  diversity at an acceptable cost" differently: a soft, relevance-weighted
  penalty stayed inside the non-significant zone; a hard quota calibrated
  to a modest, corpus-derived target did not.
- Together, RQ1 + RQ2 + RQ3 tell a consistent story: **weak, non-significant
  institutional bias at both retrieval and generation**, and — new as of
  the Fair-Top-K arm — **not every fairness-aware re-ranking method carries
  the same risk profile even when the underlying bias to correct is small**.
  A soft penalty (institution-aware MMR) raised diversity safely; a hard
  quota (Fair-Top-K), while raising nominal diversity further, did so with
  a statistically confirmed swing past parity in the opposite direction.

---

*This document consolidates the RQ3 methodology recorded in
`step6-reranking-yb-optimized-basedon-jici.ipynb` (Sections 5–9, including
the Fair-Top-K contrast arm added 2026-08-03) and
`handoff_status_rq1_for_step6.md`, for reuse in the Final Report's
Methodology and Results sections.*
