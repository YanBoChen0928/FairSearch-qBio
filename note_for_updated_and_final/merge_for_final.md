# merge_for_final.md

Three-way branch integration plan for the CS6200 final submission.
Created 2026-08-09. Deadline 2026-08-11 20:59.

All git commands are for Yan-Bo to execute manually. Claude does not run git.

---

## 0. Branch topology (observed 2026-08-09)

| Branch | Owner | Behind main | Ahead of main | Notes |
|---|---|---|---|---|
| `main` | shared | - | - | last updated ~1 month ago, stale |
| `20260801_step8_step9_after_update_work_for_final_yb` | Yan-Bo | 0 | 46 | integration target |
| `raj/step8-ragas` | Raj | 0 | 3 | branched off stale main |
| `jici/power-analysis` | Jici | 0 | 3 | branched off stale main, open PR #17 |

**Critical implication.** Both teammate branches were cut from the stale `main`,
not from the 46-commit YB branch. Their copies of `step8.md`,
`report_overleaf.tex`, and any bundle schema are therefore based on an older
state of the project. Expect semantic conflicts, not just line-number conflicts.
Every conflicted file must be reviewed by content, not auto-resolved.

---

## 1. Pre-merge verification (do this before any merge)

Answer these four questions first. Do not start merging until all four are
resolved.

**V1. Does `jici/power-analysis` actually contain the independent judge work?**
The branch name suggests power analysis, not the Framework B independent judge.
Jici's message referenced `rq2_frameworkB_independent_judge.py` and
`results/rq2_frameworkB_independent_judge_result.json`. Confirm these files
exist on this branch. If not, there is a fourth branch that has not been
identified yet.

**V2. What is the target of PR #17?**
If PR #17 targets `main`, merging it will move `main` forward and the YB branch
will become "behind". Decide whether PR #17 should be held until after the
three-way integration, to keep a single merge direction.

**V3. Which version of `report_overleaf.tex` is authoritative?**
Jici edited the tex on a branch cut from stale main. If the YB branch also
touched the tex in its 46 commits, the two edits are on divergent bases.
Determine which file is the base of truth before merging, not during.

**V4. Does Raj's work change the Step 9 bundle schema?**
The Streamlit app is a pure renderer. Any change to bundle keys or nesting
breaks the app silently. Diff the bundle-producing notebook and any schema
definition before merging.

---

## 2. Open decision that must be recorded before merging

### D1. Answer Relevancy: keep as disclosed limitation, or adopt?

**Conflict.** `step8.md` records Tier 2 Answer Relevancy as
"attempted-and-infeasible" and closed. Jici reports that Raj's Answer Relevancy
(0.914) reproduces from raw data under two independent bootstrap methods and is
usable. The document says infeasible; the data says otherwise. Both cannot
stand in the final deliverables.

Two admissible options:

- **Adopt.** Update `step8.md`, the report limitation section, and the Streamlit
  RAGAS block. State plainly that the metric was previously judged infeasible
  and was subsequently obtained through Raj's pipeline. Do not present this as a
  smooth path.
- **Do not adopt.** Permitted, but the stated reason must change. "Infeasible"
  is no longer true. The only honest remaining reasons are: not required by the
  rubric, insufficient time, or not independently re-verified by us.

Record the choice and the date here before touching any deliverable:

```
D1 decision: __________
Decided on:  __________
Rationale:   __________
```

### D2. Context Precision

No change. Remains out of scope as a disclosed limitation per `step8.md`.
This decision was not overturned by new data and is not reopened.

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

| File | Why | Owner of truth |
|---|---|---|
| `step8.md` | D1 decision lives here | Yan-Bo |
| `report_overleaf.tex` | edited by Jici on a stale base | see V3 |
| `rq2_frameworkB_summary.md` | 97.2% figure now contested | Yan-Bo |
| Step 9 bundle notebook | schema drives the whole app | Yan-Bo |
| `Claude_todo_memo.md` | append-at-top convention | Yan-Bo |

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
- Answer Relevancy field, only if D1 resolves to adopt
- A null placeholder field for the manual adjudication verdict of the 7
  disagreements, so the bundle does not need regenerating later

### Judge comparison panel constraints

1. The comparison exists **only** for Framework B, q101 to q150. RAGAS and
   Faithfulness have a single judge and no second opinion. Do not imply
   otherwise anywhere in the UI.
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

| Quantity | Self-judge | Independent judge |
|---|---|---|
| Retained | 35 / 36 | 28 / 36 |
| Rate | 97.2% | 77.8% |
| 95% CI | [91.7%, 100.0%] | [63.9%, 91.7%] |
| Agreement | 29 / 36 (80.6%) | |

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

## 8. Rollback

If any merge goes wrong:

```bash
git merge --abort                                   # during a conflicted merge
git reset --hard backup/pre-merge-20260809          # after a bad completed merge
```

The backup branch is not deleted until the final submission is confirmed.

---

## 9. Status log

| Date | Item | Status |
|---|---|---|
| 2026-08-09 | Plan created | done |
| | V1 jici branch contents | pending |
| | V2 PR #17 target | pending |
| | V3 tex base of truth | pending |
| | V4 bundle schema diff | pending |
| | D1 Answer Relevancy decision | pending |
| | Step B merge Raj | pending |
| | Step C merge Jici | pending |
| | Step D Streamlit | pending |
