# Claude Todo Memo — last updated 2026-08-01

**Purpose:** reference this file when opening a new Claude conversation
window for this project, to pick up context without re-explaining
everything from scratch. THIS IS THE MASTER HANDOFF DOCUMENT. When it
disagrees with an older section below, the most recent dated section wins.

**Deadline: 2026-08-11, 20:59.** Per-team deliverables: ACM-style PDF report
(6-10 pages), GitHub repo link inside the report, and slides (12 max, 15-min
presentation).

---

## 0. Session 2026-08-01 — Step 8 and Step 9 scoping

### What changed today

**Rubric was read against our internal plans for the first time.** The Week
14 rubric names RAGAS exactly twice, and both times reads "RAGAS
Faithfulness scores" with no other metric named. Answer Relevancy and
Context Precision appear nowhere in it. Our three-metric plan was our own
added scope, not a course requirement. NOTE: this is a literal reading, not
confirmed with Prof. Sushmita or a TA.

**`step8.md` amended (§2a, §5a, §6a added; §4 and header updated).**
- Metrics are now tiered: Tier 1 Faithfulness (required, all 150 queries),
  Tier 2 Answer Relevancy (opportunistic, cheapest of the three), Tier 3
  Context Precision (DEFERRED, not part of the committed run).
- Query scope unchanged at all 150. Only the metric priority changed.
- Committed run drops from ~1,500-2,000 calls to roughly 450.
- §4 now warns against a single combined `evaluate()` over all three
  metrics: RAGAS aborts the whole batch on an unhandled quota error, which
  would lose Faithfulness alongside Context Precision. Per-query JSONL
  checkpointing is required, not optional.

**`step9_plan.md` amended (§8-§12 added).**
- §5's fixed ~20-query subset became a tiered scope: Tier 1 the ~20-query
  subset (guaranteed floor), Tier 2 all 150 if quota allows.
- Reason: Step 9-A costs exactly one Gemini call per query, so 20 vs 150 is
  ~20 vs ~150 calls with IDENTICAL code. It is a quota decision, not a
  design decision. Also, the subset's original justification leaned on Step
  8 being 1,500-2,000 calls, which is no longer true.
- Code must be scope-agnostic: one `QUERY_SCOPE` list drives the loop. Do
  not hard-code 20 anywhere.
- §9 answers "must we change the data architecture?" — No. Purely additive,
  same pattern as the bio robustness check. Three new artifacts:
  `step9_query_scope.json`, `step9_rerank_per_query.json`,
  `step9_bundle.json`.
- §10 drafts the bundle schema (was §7's last unresolved open item).
  Field names verified against the actual files, not guessed.
- §11 gives the 9-0 / 9-A / 9-B / 9-C / 9-D sequence with estimates.
  Total roughly 3-4 focused working days.
- §12 lists six known risks.

### Time estimates produced today

**Step 8, Tier 1 + Tier 2 over 150 queries = ~450 API calls.** Wall clock
depends entirely on the unresolved quota question:
- at ~1,000/day (Yan-Bo's Step 7a observation): one sitting, ~1.5-2.5 hours
- at ~50/day (Raj's observation): ~9 days, which does not fit before 08-11

**Step 9, all four stages: ~3-4 focused working days.** API cost is
negligible either way (20-150 calls). The bottleneck is engineering, not
quota. Freezing the schema first (9-0) is what allows 9-B and 9-C to run in
parallel; skipping it forces them to be serial and adds roughly a day.

### CORRECTION to the 2026-07-19 section below

That section says Step 9 is "**BLOCKED on Prof. Sushmita's answer**". That
is now STALE. `step9_plan.md` §5 recorded the scope decision (representative
subset), and §8 has since made it tiered. Step 9 is NOT blocked on the
professor. It is blocked only on internal work: the 20-query list has not
been generated and the schema needs sign-off.

---

## 0b. Current critical path (supersedes §2 below)

Ordered. Items 1 and 2 gate the schedule; items 3 onward can start now.

1. **[BLOCKING, Step 8] Get the `quotaId` and `quotaValue` from Raj's 429
   error.** This single answer decides whether Step 8 is a 2-hour job or a
   9-day job. Jici has since given Raj a separate key (Solution 3); if that
   key is in the ~1,000/day tier the problem dissolves. Record which
   key/project produced the reported numbers.
2. **[BLOCKING, both steps] Confirm the rubric reading with Prof. Sushmita
   or a TA:** is "RAGAS Faithfulness scores" the whole requirement, or
   shorthand for the RAGAS suite? Determines whether Tier 3 is optional.
3. **Upload `rq2_frameworkB_generation_raw.jsonl`** to the Kaggle dataset
   `step7-frameworka-for-raj`. Raj currently has only
   `rq2_gen_checkpoint.jsonl` (100 records). That file being Framework-A-only
   is BY DESIGN and is NOT data loss; the Framework B generations live in a
   separate file that has not been shared. Step 8's 150-query scope cannot
   run without it.
4. **[SECURITY] Rotate or revoke Yan-Bo's older Gemini API key.** It was
   previously pasted in plaintext into a team chat message. Verify in Google
   Cloud Console whether it is revoked; if not, revoke and reissue.
5. **Run the Step 8 pilot** (5-10 queries, Tier 1 only) to get real call
   counts before committing to the full run.
6. **Step 9-0: freeze the bundle schema** (`step9_plan.md` §10) and confirm
   the re-rank operating point (λ=0.8 institution-aware MMR, fixed across
   all queries, not re-selected per query). Cheap, unblocks parallel work.
7. **Run the Step 9 sampling script** (seed=42) to produce the actual
   20-query list. Blocks 9-A.
8. **Attempt a throwaway Streamlit Community Cloud deployment early**, with
   a mock bundle. The team has never deployed there; find the friction now,
   not on 08-10.
9. Slides: confirm the deck maps to the rubric's 12-slide structure and does
   not exceed 12. Slides 6 and 8 need a narrative for "CI crosses zero"
   results that is honest without reading as a null project.
10. Report: check the Background section has 20+ peer-reviewed conference
    papers from SIGIR / FAccT / ECIR / CIKM / WWW / ACL. arXiv preprints
    that were never formally published may not count.

### Ambiguity to resolve with the professor

The GitHub deliverable says "JSON file containing results of the
**100-query** audit", but our pre-registered scope is 150. Likely the 100
refers to the neutral Framework A audit only, but confirm rather than
assume, and make sure Raj and Jici are not working to different numbers.

---

## 1. What was decided / completed on 2026-07-19

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
  **[STALE as of 2026-08-01 — see §0. Step 9 is NOT blocked on the
  professor. The scope was resolved in `step9_plan.md` §5 and then made
  tiered in §8. Remaining blockers are internal: the 20-query list has not
  been generated, and the bundle schema needs sign-off.]**

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

_Update this file at the end of each future session with what changed, so
the next fresh conversation window can pick up quickly._
