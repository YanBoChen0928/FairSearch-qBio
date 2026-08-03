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

Two runs of the same Step 6 candidate-labeling code produced different
labels for exactly one paper out of 3,086:

| | Earlier run (`data/candidate_labels.json`) | Later Kaggle run |
|---|---|---|
| `1505.06440` institution | Harvard University | University of Oslo |
| country | US | NO |
| `elite_label` | 1 | 0 |
| Total elite found | 320 | 319 |
| Candidate elite share | 0.1796 | 0.179 |

All other 3,085 records matched, and the `found` / `no_affiliation` /
`not_found` counts were identical in both runs.

### Cause

`_first_institution()` in the Step 6 notebook takes the first authorship
entry that carries a `display_name`. A paper with several authors has
several affiliations, so if OpenAlex returns authorships in a different
order, or updates its records between calls, a different institution is
selected. This is external API variability, not a code defect.

### How to use it

Report this as a limitation alongside the existing coverage caveat:
institution labeling has a small non-reproducible component, measured here
at roughly 0.03% of records (1 in 3,086), even with a fixed seed and an
unchanged method. It does not affect any conclusion at this magnitude, but
it means exact label counts should be quoted with the run they came from.

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
