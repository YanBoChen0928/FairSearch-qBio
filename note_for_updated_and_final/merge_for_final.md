# merge_for_final.md

Three-way branch integration plan for the CS6200 final submission.
Created 2026-08-09. Deadline 2026-08-11 20:59.

All git commands are for Yan-Bo to execute manually. Claude does not run git.

---

## 0. Branch topology (observed 2026-08-09)

| Branch                                                | Owner  | Behind main | Ahead of main | Notes                                |
| ----------------------------------------------------- | ------ | ----------- | ------------- | ------------------------------------ |
| `main`                                                | shared | -           | -             | last updated ~1 month ago, stale     |
| `20260801_step8_step9_after_update_work_for_final_yb` | Yan-Bo | 0           | 46            | integration target                   |
| `raj/step8-ragas`                                     | Raj    | 0           | 3             | branched off stale main              |
| `jici/power-analysis`                                 | Jici   | 0           | 3             | branched off stale main, open PR #17 |

**Critical implication.** Both teammate branches were cut from the stale `main`,
not from the 46-commit YB branch. Their copies of `step8.md` and any bundle
schema are therefore based on an older state of the project. Expect semantic
conflicts, not just line-number conflicts. Every conflicted file must be
reviewed by content, not auto-resolved. `report_overleaf.tex` is Jici's report
deliverable on Overleaf, not tracked in this repo, and out of scope for this
merge (see V3 below).

---

## 1. Pre-merge verification (do this before any merge)

Answer these four questions first. Do not start merging until all four are
resolved.

**V1. Does `jici/power-analysis` actually contain the independent judge work?
RESOLVED — yes, plus more than expected.**
Confirmed present: `rq2_frameworkB_independent_judge.py`,
`results/rq2_frameworkB_independent_judge_result.json`, and an additional file
not previously known, `results/rq2_frameworkB_judge_disagreements.json`
(per-query breakdown of the 7 disagreements). But the branch is **not scoped
to RQ2 only**. Its three commits are:

```
1. Add power/MDE analysis for RQ1 (both elite-list definitions) and RQ3
2. Add independent judge (gpt-oss-20b) validation for RQ2 Framework B
3. Add per-query breakdown of the 7 disagreements
```

Commit 1 touches `notebooks/power_analysis.ipynb`,
`notebooks/power_analysis_bio.ipynb`, `notebooks/power_analysis_rq3.ipynb`,
`results/rq1_power_analysis.json`, `results/rq1_power_analysis_bio.json`,
`results/rq3_power_analysis.json`. This is a power/minimum-detectable-effect
(MDE) analysis for **RQ1 and RQ3**, unrelated to Framework B. It answers a
different question than "is there bias" — it answers "how small an effect
could this sample size have detected even if it existed". This changes how
the RQ1/RQ3 "CI crosses zero" findings should be worded. See the new item
in section 6a below.

**V2. What is the target of PR #17? RESOLVED.**
Target is `main`, source `jici/power-analysis`, open, 3 commits, 14 files,
+2699/-0. The PR title ("Power/MDE analysis for RQ1 and RQ3") does not
mention the independent-judge commits it also contains — a reviewer going by
the title alone could approve it without realizing it changes the RQ2
Framework B narrative. Decision: **do not merge PR #17 on GitHub before this
integration completes.** Merge `jici/power-analysis` directly into the YB
branch instead (Step C below). Once the YB branch is later merged to `main`,
the same commits will already be present and PR #17 becomes a no-op to close,
not a duplicate to resolve.

**V3. `report_overleaf.tex` is out of scope for this merge — confirmed.**
Not tracked in this repo, on any branch, and not present locally. It lives on
Overleaf and is Jici's report deliverable; Yan-Bo does not verify its content.
This is not a git merge risk. It is a separate cross-document consistency
risk: after merging, `rq2_frameworkB_summary.md` in this repo must be updated
to match the independent-judge finding (97.2% to 77.8%), and Jici is
responsible for the tex saying the same thing. Updating the md file in this
repo is Yan-Bo's job; verifying the tex is not.

**V4. Does Raj's work change the Step 9 bundle schema? RESOLVED — no.**
Confirmed clean: neither branch touches `notebooks/step9b-bundle-assembly-yb.ipynb`
or anything under `app/`.

**V5. Does Raj's branch relate to RQ1/RQ2/RQ3, and does Jici's branch contain
Raj's work? Both resolved.**

Raj's branch is RAGAS answer-quality evaluation (Faithfulness, Answer
Relevancy, Context Precision). It is explicitly out-of-scope for RQ1/RQ2/RQ3
per `rq2_plan.md` Decision 3 — RAGAS was deliberately kept separate from the
fairness questions. It consumes RQ2's generated answers as input but does not
answer RQ1, RQ2, or RQ3. It is a fourth, independent axis: "is the system
fair" (RQ1-RQ3) versus "are the answers any good" (RAGAS). No RQ1/RQ3 files
are touched by Raj's branch.

Jici's branch does **not** contain Raj's commits. Verified via
`git merge-base origin/raj/step8-ragas origin/jici/power-analysis`, which
returns the same commit as `main` — the two branches share no history beyond
the common stale-main ancestor. `git ls-tree` on Jici's branch shows zero
files matching `ragas` or `step8`. The two branches are fully independent and
must each be merged separately; neither subsumes the other.

---

## 2. Open decision that must be recorded before merging

### D1. Answer Relevancy: keep as disclosed limitation, or adopt?

**Conflict.** `step8.md` records Tier 2 Answer Relevancy as
"attempted-and-infeasible" and closed. Jici reports that Raj's Answer Relevancy
(0.914) reproduces from raw data under two independent bootstrap methods and is
usable. The document says infeasible; the data says otherwise. Both cannot
stand in the final deliverables.

**DECIDED (2026-08-09): Adopt.** Raj's Answer Relevancy (0.914, 95% CI
[0.899, 0.927], n=100, `strictness=1`) reproduces under two independent
bootstrap methods per Jici's verification. Update `step8.md` §4a.8 with a
scope qualifier — Answer Relevancy was infeasible on the specific stack used
in this repo (ragas 0.4.3 + native `google.genai.Client`), not infeasible as
a metric. Raj used a different stack (ragas 0.3.9 +
`LangchainLLMWrapper(ChatGoogleGenerativeAI)` + local HuggingFace embeddings)
that does not hit the same async/sync deadlock. Disclose `strictness=1`
wherever 0.914 is cited; it is noisier than the ragas default of 3. Full
technical comparison: `comparison_step8_with_step8_ragas.md` section 3.

### D2. Faithfulness: which run is the headline number?

**Conflict, now resolved with a disclosure obligation.** Yan-Bo and Raj each
independently ran RAGAS Faithfulness over the same 150 queries with the same
judge (`gemini-3.1-flash-lite`, temperature 0) and got different numbers:

```
                    Yan-Bo               Raj
  neutral           0.9616 (n=98)        0.978  (n=100)
  contradictory      0.9613 (n=50)        0.966  (n=50)
  failures            2 (q032, q068)       0
```

Three explanations were tested and ruled out (silent NaN in Raj's checkpoint,
forced low-quality scores on the two originally-failing queries, judge model
or temperature mismatch). The confirmed explanation is a **context format
difference**: Yan-Bo's contexts were rebuilt to exactly match what the
generator saw at generation time
(`"Title: {t}\nAbstract: {a}"`); Raj's contexts drop the field labels
(`"{t}\n{a}"`). Full worked example with a real paper:
`comparison_step8_with_step8_ragas.md` section 1.

**DECIDED (2026-08-09): use Raj's numbers (0.978 / 0.966, 150/150) as the
headline in Streamlit, the deck, and the report.**

This decision carries a **mandatory disclosure requirement**, not optional:
wherever 0.978/0.966 is shown, state that a second, differently-constructed
run measured 0.9615 (148/150) and that the difference traces to context
formatting, not data quality. See
`comparison_step8_with_step8_ragas.md` section 4 for the exact required
sentence. Do not present 0.978/0.966 as a bare number.

Required follow-up work, tracked as a Step D task:
1. Write a converter: Raj's three checkpoint JSONLs -> the schema
   `step9b-bundle-assembly-yb.ipynb` expects (`per_query`,
   `failed_queries`, `faithfulness_overall`, `faithfulness_by_type`). Detail
   in `comparison_step8_with_step8_ragas.md` section 2.
2. Regenerate `data/step9_bundle.json`.
3. Update `step8.md`, `deliverables_checklist.md`, and the deck wherever
   0.9615/148 currently appears.

### D3. Context Precision

No change. Remains out of scope as a disclosed limitation per `step8.md`.
This decision was not overturned by new data and is not reopened. Raj's
0.039 (90/4/5/1 distribution, corrected per Jici's review) is usable as
supporting evidence for the limitation paragraph — his Faithfulness
cross-check on the 90 zero-scoring queries (0.977, versus 0.978 overall)
argues the low CP is a metric artifact, not a retrieval failure — but CP
itself is not promoted to a headline metric.

---

## 3. Merge sequence

One merge at a time. Verify the stated checkpoint before starting the next.
Do not merge both teammate branches in a single step.

### Step A. Safety net

```bash
cd /Users/yanbochen/IdeaProjects/CS6200-Project
git fetch --all --prune
git status                      # must be clean before proceeding
git checkout 20260801_step8_step9_after_update_work_for_final_yb
git branch backup/pre-merge-20260809
```

Inspect what is actually coming in, before merging anything:

```bash
git log --oneline main..origin/raj/step8-ragas
git log --oneline main..origin/jici/power-analysis
git diff --stat HEAD...origin/raj/step8-ragas
git diff --stat HEAD...origin/jici/power-analysis
```

The `--stat` output answers V4 and V3. Read it before continuing.

### Step B. Merge Raj (data layer first)

```bash
git merge --no-ff origin/raj/step8-ragas
```

Checkpoint before proceeding to Step C:

- [ ] Bundle schema unchanged, or changes explicitly catalogued
- [ ] Streamlit app still loads and renders one neutral and one contradictory query
- [ ] RAGAS numbers reproduce: Faithfulness 0.978 / 0.966, Answer Relevancy 0.914,
      Context Precision 0.039
- [ ] `step8.md` conflict resolved per D1

### Step C. Merge Jici (report and independent judge)

```bash
git merge --no-ff origin/jici/power-analysis
```

Checkpoint before proceeding to Step D:

- [ ] `rq2_frameworkB_independent_judge.py` and its result JSON are present
- [ ] The independent judge finding is reflected consistently in the abstract,
      the RQ2 results section, and the conclusion, not only in Methodology
- [ ] Framework B claims in `rq2_frameworkB_summary.md` updated to match
- [ ] Slide deck Framework B slide flagged for revision

### Step D. Streamlit

Do not start until B and C checkpoints are clear. See section 5.

---

## 4. Files with high conflict risk

Review these by content. Never accept an auto-resolution.

| File                        | Why                                                                                                 | Owner of truth |
| --------------------------- | --------------------------------------------------------------------------------------------------- | -------------- |
| `step8.md`                  | D1 decision lives here; Raj's new `step8_ragas_summary.md` may contradict it without a git conflict | Yan-Bo         |
| `rq2_frameworkB_summary.md` | 97.2% figure now contested by independent judge (77.8%)                                             | Yan-Bo         |
| Step 9 bundle notebook      | schema drives the whole app                                                                         | Yan-Bo         |
| `Claude_todo_memo.md`       | append-at-top convention                                                                            | Yan-Bo         |

---

## 5. Streamlit changes: generate the bundle once

Do not regenerate the bundle twice. Combine all pending schema work into a
single pass.

Pending items already queued (source data exists, no API quota needed):

- B1 / B2: `elite_share`, `n_labeled`
- C1 / C2: `cited_elite_share`, `amplification`
  in `delta_vs_baseline` and intervention diagnostics

New items from this integration:

- Judge comparison fields for Framework B (see constraints below)
- Answer Relevancy field (D1 decided: adopt) — 0.914, disclose `strictness=1`
- Faithfulness field switches source from `results/ragas_faithfulness_result.json`
  to a new converter output built from Raj's checkpoints (D2 decided: use
  Raj's numbers) — see section 7a for the single-run-with-disclosure decision
- A null placeholder field for the manual adjudication verdict of the 7
  disagreements, so the bundle does not need regenerating later

### Judge comparison panel constraints

1. The Framework B panel (self-judge vs. `gpt-oss-20b`) is a genuine
   **two-judge** comparison — different model, different vendor. It exists
   **only** for Framework B, q101 to q150. Do not confuse this with the
   Faithfulness situation below, which is a different kind of duplication:
   same judge model, two different context-construction methods, not two
   judges. See section 7a for how to display Faithfulness so this
   distinction is not blurred in the UI.
2. q101 to q150 have no RQ3 intervention by design. The panel therefore belongs
   under the contradictory branch, alongside the existing "not applicable"
   notice, and must never appear on the neutral branch.
3. The 7 disagreements must be displayed as **unadjudicated**. No verdict, no
   implied winner between the two judges.
4. Display the direction breakdown, not just the count: 6 queries judged
   "only B retained", 1 judged "only A retained", 0 in the reverse direction.
   The 6:1 split is evidence about the failure mode, and it is more informative
   than the word "unidirectional".

### Corpus-level numbers to show side by side

| Quantity  | Self-judge      | Independent judge |
| --------- | --------------- | ----------------- |
| Retained  | 35 / 36         | 28 / 36           |
| Rate      | 97.2%           | 77.8%             |
| 95% CI    | [91.7%, 100.0%] | [63.9%, 91.7%]    |
| Agreement | 29 / 36 (80.6%) |                   |

Both intervals are wide at n = 36. Neither point estimate may be presented as
a settled value in UI captions or in the report.

---

## 6. Statistical points to raise with Jici

These affect the report text, not the merge itself, but should be settled
before the tex is frozen.

1. **Comparing two independent CIs is not the right test for paired data.**
   The same 36 queries and the same answers were judged twice. Use McNemar on
   the 7 discordant pairs, or bootstrap the paired difference. With 7:0
   discordance, McNemar exact two-sided is approximately p = 0.016, which is a
   stronger and cleaner statement than "the intervals barely touch".
2. **Unidirectionality does not establish self-preference.**
   `gpt-oss-20b` is far smaller than the Gemini judge. A weaker or more
   conservative judge produces the same one-directional pattern on borderline
   cases. Judge capability difference must be listed as a third explanation
   alongside self-preference risk and criterion ambiguity.
3. **Independence covers only the retention step.**
   If eligibility for the 36 queries was determined by the original pipeline,
   the independent judge inherits that upstream filter. State this explicitly,
   or the phrase "independent judge" reads stronger than it is.
4. **Report the 6:1 direction split**, not just "unidirectional".

---

## 6a. RQ1 / RQ3 wording check after merging Jici's power analysis

Jici's branch is not scoped to Framework B alone — it also adds
`notebooks/power_analysis.ipynb`, `notebooks/power_analysis_bio.ipynb`,
`notebooks/power_analysis_rq3.ipynb`, and their result JSONs. This is a
power / minimum-detectable-effect (MDE) analysis for **RQ1 and RQ3**.

**Action after merging Step C:** review the "CI crosses zero" wording in
`rq1_methodology.md` and `rq3_methodology.md`. There are two different
statements a non-significant CI can support, and they are not
interchangeable:

1. "We have enough data to be confident there is no meaningful effect."
2. "Our sample size cannot distinguish no-effect from a small effect near
   what we observed."

Without a power analysis, the report cannot honestly make statement 1. Raj's
own `step8_ragas_summary.md` already uses framing consistent with statement 2
("we can rule out large elite-retrieval bias with confidence; we cannot
distinguish no-bias from small-bias-near-observed at this sample size") —
meaning this framing has already started propagating into other people's
documents before the source methodology files are updated. Update
`rq1_methodology.md` and `rq3_methodology.md` to match, citing the specific
MDE figures once the notebooks are reviewed, rather than leaving the
methodology files saying less than what other documents already claim.

---

## 7. Scope call on the 7 disagreements

Roughly two days remain. Manual blind adjudication of the 7 disagreements
requires a pre-registered, dated procedure: who judges, how many judges,
whether consensus is required, blinding of which judge produced which label,
and an operationalised definition of "substantive engagement".

Recommended: **do not attempt adjudication before the deadline.** Present the 7
disagreements in Streamlit as unadjudicated, document the procedure in the
report as future work, and state the ambiguity in the criterion as a limitation.
A half-completed adjudication is worse than none, because it invites post-hoc
rationalisation of exactly the criterion that is under question.

---

## 7a. Single judge or dual judge in Step 9 — decide before building the panel

To do, flagged for the Step D rebuild. There are now **two separate
"two-versions-of-a-metric" situations** in this project, and the Step 9 UI
must not present them the same way, because they are not the same kind of
disagreement.

**Framework B (already planned): genuinely two judges.**
Self-judge (same model as generation) vs. `gpt-oss-20b` (different vendor,
different architecture). This is the comparison covered in section 5's
"Judge comparison panel constraints" above. Two judges, two opinions, shown
side by side with the corpus-level table and the unadjudicated 7 flagged.

**Faithfulness (new, from this integration): one judge, two runs.**
Same judge model (`gemini-3.1-flash-lite`) scored the same 150 queries twice,
but the two runs built the context text differently (see D2 above and
`comparison_step8_with_step8_ragas.md`). This is not "two judges disagreeing"
— it is "the same judge answering two subtly different questions because the
input was assembled differently." Displaying this with the same dual-column
UI pattern as Framework B would misrepresent it as a second opinion, when it
is closer to a data-preparation difference.

**Decision needed before Step D:** how should the Faithfulness metric render
in Streamlit?

- **Option 1 (matches the current D2 decision).** Show one number (Raj's
  0.978/0.966) with the required disclosure sentence from
  `comparison_step8_with_step8_ragas.md` section 4, e.g. as a caption or an
  info tooltip. Simplest, and consistent with "the app is a pure renderer of
  one bundle value."
- **Option 2.** Show both numbers side by side, similar in spirit to the
  Framework B panel, but visually distinguished (e.g. a plain two-row table,
  not the same colored dual-column layout) so it is not mistaken for a
  second judge. More transparent, more work: needs both numbers in the
  bundle and a second small UI block.

Recommendation: **Option 1** for this deadline, given the two-day window and
that Option 2 would require carrying Yan-Bo's original per-query data into
the bundle alongside Raj's converted data, doubling the Faithfulness-related
bundle work in section 5. Option 2 is a reasonable future-work item, not a
requirement for this submission.

---

## 8. Rollback

If any merge goes wrong:

```bash
git merge --abort                                   # during a conflicted merge
git reset --hard backup/pre-merge-20260809          # after a bad completed merge
```

The backup branch is not deleted until the final submission is confirmed.

---

## 9. Status log

| Date       | Item                         | Status                                                                                                                                 |
| ---------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-08-09 | Plan created                     | done                                                                                                                                    |
| 2026-08-09 | V1 jici branch contents          | done — present, plus judge_disagreements.json; branch also covers RQ1/RQ3 power analysis, not RQ2-only                                |
| 2026-08-09 | V2 PR #17 target                 | done — main; decided not to merge on GitHub before this integration, merge branch directly instead                                    |
| 2026-08-09 | V3 tex scope                     | done — not tracked in repo, out of scope, Jici's responsibility                                                                        |
| 2026-08-09 | V4 bundle schema diff            | done — clean, neither branch touches step9b or app/                                                                                    |
| 2026-08-09 | V5 Raj scope + branch overlap    | done — Raj's work is out-of-scope for RQ1-3 by design; Jici's branch confirmed NOT to contain Raj's commits (independent ancestry)     |
| 2026-08-09 | Risk found                       | Raj added `step8_ragas_summary.md` instead of editing `step8.md`; no git conflict but content contradicted D1/D2 — resolved, see below |
| 2026-08-09 | Check done                       | Jici's two `data/rq2_frameworkB_*` files are byte-identical to YB's current versions — zero risk                                       |
| 2026-08-09 | Faithfulness discrepancy diagnosed | done — root cause is context format (`Title:`/`Abstract:` labels vs none), NaN-masking and forced-low-score hypotheses ruled out; full detail in `comparison_step8_with_step8_ragas.md` |
| 2026-08-09 | D1 Answer Relevancy decision     | **decided: adopt** (0.914, strictness=1 disclosed)                                                                                     |
| 2026-08-09 | D2 Faithfulness headline         | **decided: use Raj's (0.978/0.966, 150/150), mandatory disclosure sentence required**                                                  |
| 2026-08-09 | D3 Context Precision             | unchanged, out of scope                                                                                                                |
| 2026-08-09 | 6a RQ1/RQ3 wording check         | flagged — to do after Step C merge                                                                                                     |
| 2026-08-09 | 7a Step 9 single/dual display    | flagged — recommend Option 1 (single number + disclosure), Option 2 deferred to future work                                           |
|            | Step B merge Raj                 | pending                                                                                                                                 |
|            | Step C merge Jici                | pending                                                                                                                                 |
|            | Step D Streamlit                 | pending — includes Faithfulness converter (section 2 of comparison doc) and 7a display decision                                       |
