# FairSearch-qBio: Project Takeaways and Open Leads

**Created 2026-08-02.** Observations that are worth carrying into the report
but that do not belong to any single methodology document. Each entry states
what was measured, under which pipeline, and how much weight it can bear.

**Rule for this file:** every claim names its source file and its coverage.
An observation from a superseded pipeline is labeled as such and is never
promoted to a finding.

---

## 1. Contradictory queries may retrieve more elite papers than neutral ones (LEAD, not a finding)

### What was observed

`step5_150run_summary.md`, "Coverage (the crux)" table:

| Group | Slots | Labeled | Coverage | Elite share |
|---|---|---|---|---|
| All 150 queries | 1500 | 264 | 17.6% | 0.322 |
| Neutral q001-q100 | 1000 | 170 | 17.0% | 0.294 |
| **Contradictory q101-q150** | 500 | 94 | 18.8% | **0.372** |

The same document files this under "Secondary observations" and describes it
in its own words as a lead to follow up in RQ2, not as a result.

### Why it matters conceptually

If debate-style queries really do surface a higher elite share, then
contradictory queries would be exactly where institutional bias is
strongest, and therefore where a mitigation like re-ranking would matter
most. That would be a substantive argument for extending RQ3 beyond the
neutral set.

It also gives an independent, empirical reason why the Framework A /
Framework B split was a sound design: if Side A's supporting papers skew
more elite than Side B's, then an observed "the answer favours Side A"
result cannot be cleanly attributed to a viewpoint preference rather than an
elite-institution preference. `rq2_methodology.md` §1 states this confound
as the reason for the disjoint query sets. This observation suggests the
confound is a live risk in this corpus, not just a theoretical one.

### Why it cannot be reported as a finding

Three limits, all verified 2026-08-02:

1. **Superseded pipeline.** These numbers come from the pre-Option-B
   labeling pass. That pass was replaced precisely because its baseline was
   biased and its coverage too low. `step5_150run_summary.md` itself proposes
   the Option B redo in the same document.
2. **Low coverage.** 18.8% for the contradictory group: 94 labeled slots out
   of 500. 82% of slots were unlabeled and excluded.
3. **Never recomputed under Option B.** `results/rq1_optionB_result.json`
   has `analysis_scope: "neutral queries only (q001-q100)"`. No Option B
   elite share exists for contradictory queries. The magnitudes are not
   transferable between pipelines: the old all-query elite share was 0.322,
   while Option B's retrieved-set share is 0.1767.

### How to use it

- **Report:** Future Directions. Frame it as an untested lead with its
  provenance stated, e.g. that an earlier labeling pass suggested debate
  queries surface a higher elite share, that this was never re-verified
  under the final labeling method, and that testing it would require
  extending the Option B labeling and the RQ3 re-ranking to q101-q150.
- **Do NOT** cite 0.372 or 0.294 as current results, and do not use them to
  justify scope decisions.
- **Related decision:** `step9_plan.md` — contradictory queries get no RQ3
  intervention panel in the Streamlit interface. This lead is the strongest
  argument *against* that decision, which is why it is recorded here rather
  than quietly dropped.

---

## 2. A small fraction of institution labels is not reproducible across runs

### What was observed

Three runs of the same Step 6 candidate-labeling code, run 1 and run 2 on
2026-08-02 and run 3 on 2026-08-03 (during the Fair-Top-K contrast-arm
work), produced different aggregate counts each time:

| | Run 1 (`data/candidate_labels.json`) | Run 2 (Kaggle, 2026-08-02) | Run 3 (Kaggle, 2026-08-03) |
|---|---|---|---|
| Total elite found | 320 | 319 | 311 |
| Papers found (labeled) | -- (not recorded) | -- (not recorded) | 1,787 |
| Candidate elite share | 0.1796 | 0.179 | 0.174 |

Run 1 vs run 2 differed by exactly one paper out of 3,086
(`1505.06440`: Harvard University / elite=1 in run 1, vs University of Oslo
/ elite=0 in run 2 -- traced at the time). Run 3's drop (319 to 311, 8
papers) is larger and the specific paper-level cause was not traced this
time, since by run 3 the drift itself was already an understood, expected
property of the pipeline rather than something requiring per-paper
investigation. All three runs used the identical `n_candidates_new = 3086`
input set and the identical Option B method.

### Cause

`_first_institution()` in the Step 6 notebook takes the first authorship
entry that carries a `display_name`. A paper with several authors has
several affiliations, so if OpenAlex returns authorships in a different
order, or updates its records between calls, a different institution is
selected. This is external API variability, not a code defect.

### How to use it

Report this as a limitation alongside the existing coverage caveat:
institution labeling has a small non-reproducible component. Across the
three observed runs, the elite-count drift ranges from 1 paper (run 1 to
run 2, 0.03% of the 3,086 candidate set) to 8 papers (run 2 to run 3,
0.26%), even with a fixed seed and an unchanged method. It does not affect
any downstream conclusion at this magnitude -- e.g. the Fair-Top-K contrast
arm computed in the same run 3 session used the run 3 labels consistently
throughout, so internal consistency within a single run is preserved -- but
it means exact label counts should always be quoted with the run they came
from, and that the drift trends slightly larger with more runs rather than
staying fixed at "1 in 3,086."

---

## 3. OpenAlex coverage bias runs in the same direction as the hypothesis

### What was observed

`step5_150run_summary.md`, "Why coverage is the bottleneck (and a confound
to disclose)": OpenAlex affiliation coverage is systematically lower for
non-elite, non-English, and Global-South institutions.

### Why it matters

The missing labels are not missing at random. They are more likely to be
non-elite papers, which makes elite papers easier to label than non-elite
ones. That gap points in the **same direction** as the RQ1 hypothesis, so it
inflates the apparent elite share rather than adding neutral noise.

This is a confound, not sampling error, and it applies to every SPD and SRR
number in the project, including the Option B numbers, since Option B
improved coverage (44-58%) without eliminating the directional gap.

### How to use it

Report as a first-order methodology limitation wherever SPD or SRR is
cited. It strengthens rather than weakens the project's headline result: the
measured tilt is small and non-significant **despite** a confound that
should have exaggerated it.

---

## 4. Year bias in retrieval (minor, one line in the report)

`step5_150run_summary.md`, "Secondary observations": newer papers
(2020-2026) are under-retrieved at roughly 0.6x, older papers
over-retrieved. Same provenance caveat as entry 1 (pre-Option-B pass), and
never re-verified. Worth one sentence, not a section.

---

## 5. Key Takeaways for Slide 10 / Report Conclusion (drafted 2026-08-03)

**Scope note, so this section is not confused with 1-4 above.** Entries 1-4
in this file are leads, caveats, and confounds that do not belong to any
single methodology document and are explicitly NOT findings. This section
is different in kind: it is a draft of the confirmed, CI-backed findings
already written up in full in `rq1_methodology.md`, `rq2_methodology.md`,
and `rq3_methodology.md`, condensed here into the exact "3-4 main findings
+ what they reveal about fairness in RAG" shape Prof. Sushmita's rubric
asks for on Slide 10. It is a convenience draft for slide/report assembly,
not a new claim, and every number below is already fully sourced in the
methodology doc named. If the underlying numbers in those documents change,
this section must be updated to match, not the other way around.

**1. Retrieval-stage institutional bias is present in the point estimate
but not statistically significant.** RQ1: SPD +0.029, 95% CI
[-0.005, +0.065], crosses zero; robust to using a biology-specific elite
list instead of the general QS ranking (SPD +0.031, CI still crosses zero);
Equalized Odds shows no systematic directional bias either. *Reveals:*
institutional homophily in academic RAG retrieval is not automatic or
universal -- whether it is detectable depends heavily on corpus size and
composition, and this ~55,300-paper q-bio corpus does not show a
statistically detectable retrieval-stage tilt.

**2. Generation-stage synthesis neither amplifies nor suppresses fairly
across the two axes tested.** RQ2 Framework A: citation amplification
+0.0041, CI crosses zero (LLM does not preferentially cite elite papers
beyond what retrieval already surfaced). RQ2 Framework B: 35/36 eligible
contradictory queries retained both viewpoints (97.2%, CI [91.7%, 100.0%]).
Step 8 RAGAS Faithfulness: 148/150 queries scored, mean 0.9615, with no
meaningful gap between neutral (0.9616) and contradictory (0.9613) queries.
*Reveals:* even where retrieval carries a small tilt, this pipeline's LLM
synthesis stage was not an additional source of unfairness -- it neither
amplified the retrieval-stage skew nor systematically flattened dissenting
viewpoints into consensus.

**3. Fairness-aware re-ranking methods are not interchangeable, even
starting from the same low-bias baseline.** RQ3: institution-aware MMR
(lambda=0.8) significantly raises institutional diversity (+0.17 unique
institutions per query, CI [0.09, 0.26], excludes zero) with no detectable
directional bias of its own (SPD +0.016, CI crosses zero). Fair-Top-K, a
hard quota calibrated to the corpus-parity target (0.144, not 50/50),
significantly overcorrects into reverse bias (SPD -0.046, CI
[-0.049, -0.044], entirely negative). *Reveals:* a soft, relevance-weighted
penalty and a hard quota are not two flavors of the same fix -- at the same
Top-10 depth and the same fairness target, one produces a clean diversity
gain and the other produces a statistically confirmed overcorrection in the
opposite direction.

**4. Not every mitigation named in the fairness-in-RAG literature needs to
be deployed, and disclosing that is itself part of responsible reporting.**
Perspective-balanced prompting was planned as a third RQ3-adjacent
mitigation but was never triggered, because Framework B's baseline already
retained both viewpoints in 97.2% of eligible queries -- there was no
dissent-suppression problem for it to fix. *Reveals:* a fairness pipeline
should apply mitigations conditionally on a measured problem existing, not
apply every technique named in prior work by default; stating "checked, not
needed" is a defensible finding in its own right, not an implementation
gap.
