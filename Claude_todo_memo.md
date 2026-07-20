# Claude Todo Memo — 2026-07-19

**Purpose:** reference this file when opening a new Claude conversation
window for this project, to pick up context without re-explaining
everything from scratch. Written at the end of the 2026-07-19 session.

---

## 1. What was decided / completed today

### RQ1 robustness check — COMPLETE
- Ran a full parallel Step 1b → Step 5b pipeline using QS World University
  Rankings by Subject 2026: Biological Sciences (instead of the original QS
  overall ranking) as a second, independent elite-institution definition.
- New files: `data/qs_top50_elite_2026_bio.json`,
  `data/sample_labels_1000_bio.json`, `data/retrieval_labels_bio.json`,
  `results/rq1_optionB_result_bio.json`, `results/equalized_odds_results_bio.json`,
  `results/equalized_odds_signed_direction_bio.json`.
- New notebooks (Kaggle): `step1b_institution_labels_full_bio_yb`,
  `step5b-fairness-audit-optionb-bio-yb`.
- **Result: SPD +0.031 (vs +0.029 original), CI still crosses zero.
  Conclusion unchanged and robust to elite-list choice.**
- Fully documented in `rq1_methodology.md` §10 (full comparison table),
  `README.md` (Key Findings), `data/README_data.md`.
- **Original QS-overall-ranking pipeline and results were NOT touched or
  overwritten** — this is purely additive.

### Methodology documentation — COMPLETE
- `query_generation_methodology.md`, `rq1_methodology.md`,
  `rq2_methodology.md`, `rq3_methodology.md` all written, cross-checked
  against each other and against the actual notebook code/output for
  consistency (numbers matched, one arithmetic-conflation error in
  `rq1_methodology.md` §6 was found and fixed).

### Step 8 (RAGAS evaluation) — PLANNED, NOT STARTED
- `step8.md` written: background on RAGAS, data mapping (existing files
  already have what's needed, no new data collection), judge model decided
  (`gemini-3.1-flash-lite`, self-judge, same free-tier reasoning as RQ2
  Framework B), technical code sketch, and a **quota risk estimate
  (~1,500–2,000 total API calls for all 150 queries)**.
- **Next action before any code runs: a 5–10 query pilot** to measure actual
  call count / latency / quota headroom.

### Step 9 (Streamlit diagnostic interface) — PLANNED, BLOCKED
- `step9_plan.md` written: ASCII flow of the professor's 5-step requirement,
  gap analysis against existing files (only real gap: RQ3-intervention's
  second Gemini call has never been run per-query, and the Streamlit app
  itself doesn't exist yet), architecture decision (**Route A: precompute
  everything on Kaggle, Streamlit only reads/displays** — chosen over live
  computation), and how Streamlit actually runs/deploys.
- **BLOCKED on Prof. Sushmita's answer** to: full 150-query coverage vs. a
  handful of representative queries. Do not start Step 9-A (the new
  RQ3-intervention generation work) until this is resolved — the scope
  decision changes the required work by an order of magnitude.

---

## 2. Immediate next steps (in priority order)

1. **Wait for Prof. Sushmita's reply** on the Step 9 scope question
   (full 150 vs. representative subset). This is the single biggest
   unblock — it determines both Step 9-A's workload and, indirectly,
   whether Step 8's RAGAS run should also be scoped down to match (running
   RAGAS only on the same representative subset that Step 9 will demo,
   rather than all 150, would reduce quota risk for both steps at once).
2. Once unblocked: run the **Step 8 pilot** (5–10 queries) to get real
   quota numbers before committing to the full RAGAS run.
3. Kaggle housekeeping: confirm `sample_labels_1000_bio.json`,
   `retrieval_labels_bio.json`, and `rq1_optionB_result_bio.json` (plus the
   two equalized_odds `_bio` files) are safely downloaded/backed up locally
   under `data/` and `results/` — they were produced via Kaggle notebooks
   this session and their local sync status was not explicitly confirmed.
4. GitHub: a PR description for the RQ1 robustness-check work was drafted
   in this session (not yet posted) — use it when opening the actual PR.

---

## 3. Known open items / caveats to remember

- **Bootstrap resample count differs across RQs**: RQ1 uses 5,000
  resamples; RQ2 and RQ3 use 10,000. Not an error, just an inconsistency
  flagged but not yet resolved with a footnote (Yan-Bo hasn't confirmed
  whether to add one).
- **RQ3 currently reports SPD only, not SRR** — flagged as a possible
  asymmetry vs. RQ1 (which reports both), not yet acted on.
- **RQ3's primary/secondary metric framing** (unique-institutions@10 as
  primary, SPD/SRR as secondary diagnostics) was discussed and agreed on
  2026-07-19 but **not yet written into `rq3_methodology.md`** — this edit
  is still pending along with the "statistically detectable but modest in
  magnitude" wording fix for the SPD-improvement significance discussion.
- **Perspective-balanced prompting** was planned in `rq2_plan.md` as an
  RQ3-adjacent intervention but was never implemented (Framework B's
  baseline retention was already 97.2%, so no suppression problem existed
  to fix). This is already correctly documented in `rq2_methodology.md`.
- Elite-list data provenance: `qs_top50_elite_2026_bio.json` was
  reconstructed from a third-party mirror (smapse.com), not an official QS
  download — cross-validated against facts on the official QS page but
  this indirect sourcing must stay disclosed in the report.

---

*Update this file at the end of each future session with what changed, so
the next fresh conversation window can pick up quickly.*
