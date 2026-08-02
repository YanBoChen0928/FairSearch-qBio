# Claude Todo Memo — last updated 2026-08-01

**Purpose:** reference this file when opening a new Claude conversation
window for this project, to pick up context without re-explaining
everything from scratch. THIS IS THE MASTER HANDOFF DOCUMENT. When it
disagrees with an older section below, the most recent dated section wins.

**Deadline: 2026-08-11, 20:59.** Per-team deliverables: ACM-style PDF report
(6-10 pages), GitHub repo link inside the report, and slides (12 max, 15-min
presentation).

---

## 000. Session 2026-08-01 (late) — rubric reconciliation, Step 8 closed by decision

**NEWEST SECTION. Read this first. Supersedes §00 and everything below it
wherever they disagree.**

### What this session produced

1. **Step 8 §2a is CLOSED by Yan-Bo's decision, not by asking anyone.**
   Written into `step8.md` §2b (new), §7 limitation 4, §7a, and into §00 of
   this file. Tier 1 delivered, Tier 2 closed as attempted-and-infeasible,
   Tier 3 Context Precision NOT RUN and carried as a disclosed limitation
   plus future work. **Any future session that proposes asking Prof.
   Sushmita about RAGAS scope is working from stale notes.**
2. **New file `deliverables_checklist.md`** at WD root. Transcribes the Week
   14 rubric and maps every line to a real artifact. §1 holds six verified
   gaps, §1a holds the G1 cost survey.

### Three findings worth carrying forward

**A. Peer reports cannot be cited.** Three other groups' final reports are
available, but they are classmates' unpublished coursework, not
peer-reviewed literature. Do not quote their numbers in the report or use
them as evidence. They may inform internal judgement only. An earlier draft
of the G1 argument leaned on one of them and had to be rewritten.

**B. `step5.md`'s "Fair MMR / Fair-Top-K" slash is NOT a valid defence.**
That slash is this project's own earlier plan; the Week 14 rubric came later
and names all three mitigation methods. A later course instruction outranks
an earlier internal plan. It may appear as background, never as
justification. This is why the G1 recommendation flipped to "implement it".

**C. RQ3's `n_queries: 100` is by design and already documented.** Not a
hole, and NOT caused by missing subcategory labels: all 150 queries carry a
`subcategory` field, contradictory ones included. The real reason is in
`handoff_status_rq1_for_step6.md`: q101-q150 are held out for RQ2 Experiment
B, main SPD computed on neutral only. Carried into `rq3_methodology.md` §1
as a locked convention.

### The three quantitative arguments against a hard quota

Derived this session from this project's own files. They belong in
`rq3_methodology.md` as a new section, and they are the entire defence for
G1 now that (B) removed the plan-level argument.

1. **Resolution.** A quota over K=10 can only express elite shares in 10
   percentage-point steps. Against a corpus baseline of 0.144, the reachable
   SPD grid is -0.044 (1 slot) or +0.056 (2 slots). The quantity being
   corrected is +0.029. The instrument's minimum step is more than three
   times the effect. Worse in practice, since SPD is computed over labeled
   slots only, roughly 5.9 of 10 per query.
2. **Groupability.** A quota requires every candidate to have a group.
   `data/retrieval_labels.json` meta: 1,366 unique retrieved papers, 798
   found (58.4%), 553 no_affiliation, 15 not_found. Over 40% cannot be
   assigned. MMR degrades gracefully here (zero penalty for unlabeled, per
   `rq3_methodology.md` §9 limitation 2); a quota cannot.
3. **Assumption replacing measurement.** A quota requires naming a target
   share in advance. RQ1's SPD is +0.029 with 95% CI [-0.005, +0.065], which
   contains zero and negative values. Fixing a target would convert the
   quantity under study into an assumption.

**Wording rule.** Say "we did not detect a significant disparity", never "we
have no statistical difference". The point estimate is positive; only its
distinguishability from zero is in question.

### Should contradictory queries be added to RQ3?

Discussed, not decided, priority LOW. Mechanically possible:
`data/retrieval_results.json` holds all 150 queries with Top-10 each. But it
would need a Kaggle re-run to rebuild 50-candidate pools for q101-q150.

The one real methodological objection is that NDCG@10 relies on
subcategory-match relevance, which is a reasonable proxy for neutral queries
and breaks for debate queries, where a good answer must cover a side of the
argument rather than merely share a subcategory. The same metric name would
measure a different thing.

If this is written up, frame the held-out split positively: a deliberate
separation so no query set is used both to discover and to verify. Do NOT
write engineering cost as a reason; that is internal only.

### Next session entry point

See §000a below.

---

## 000a. NEXT SESSION: exactly what to open and in what order

**Say this at the start of the next window.** Working directory is
`/Users/yanbochen/IdeaProjects/CS6200-Project`, desktop-commander is
available.

**Step 1, always.** Read `Claude_todo_memo.md` §000 and §000a (this
section). That is the current state. Do not read further down unless a
specific question needs it; §00 and below contain superseded text.

**Step 2, pick the track.**

*Track A, Step 9 build-out (the critical path).* Ask for these, in order:

1. `step9_plan.md` **§10** (bundle schema draft) and **§11** (the 9-0 /
   9-A / 9-B / 9-C / 9-D sequence with estimates). This is the master
   implementation doc.
2. `step9_query_subset.md` **§6** (tiered scope amendment) plus §2 for the
   sampling method. Needed to settle the Tier 1 vs Tier 2 scope call in 9-0.
3. `step9_plan.md` **§8a** for why the quota constraint on that scope call
   has dissolved.
4. Later, for deployment only: `step9_streamlit_deployment.md` **§3.2
   onward**. §3.1 local dry run is already done. Blocker 3 is still open and
   closes automatically once `app/data/step9_bundle.json` exists.

The first concrete action in Track A is **9-0: freeze the bundle schema and
make the scope call**. It is cheap and it unblocks 9-B and 9-C to run in
parallel; skipping it forces them serial and costs about a day.

*Track B, G1 Fair-Top-K contrast arm.* Ask for
`deliverables_checklist.md` §1a (cost survey with the exact cell numbers)
and `notebooks/step6-reranking-yb-optimized-basedon-jici.ipynb`. Roughly 20
lines of new code, zero API calls. Then write the new
`rq3_methodology.md` section using the three arguments in §000 above.

*Track C, G5 citation count.* Fully independent of A and B, no
prerequisites, purely mechanical. Count the report's reference list and
classify each entry by venue against the SIGIR / FAccT / ECIR / CIKM / WWW /
ACL requirement. Good filler work when energy is low.

**Priority, REVISED by Yan-Bo 2026-08-02: B first, then A, then C.** This
reverses the A-first ordering originally written here. Reason: Fair-Top-K is
named explicitly in the rubric, its scope is bounded (about 20 lines, zero
API calls, no unknown failure modes), and finishing it turns the README's
Fair-Top-K checkmark from an overclaim into a fact. Step 9's deployment is
the only step in the project with no known cost ceiling, so it gets the
remaining calendar slack.

**Condition attached: timebox Track B to one session.** If Fair-Top-K is not
finished in one sitting, park it and switch to Track A. It must not eat the
slack Step 9 needs.

**Track B pre-registration item, must be decided BEFORE the run.** A hard
quota needs a rule for the roughly 40% of candidates with no institution
label. Decide and write down whether unlabeled papers form a third group
used only as tiebreaker after both primary groups are exhausted, or are
excluded from the quota entirely. Deciding this after seeing results would
be a retroactive choice and must not happen.

### Do NOT create `step9_implementation_deploy.md`

Recommendation, for the same reason `step8_methodology.md` was cancelled:
one authoritative home per fact, no duplication. Three Step 9 documents
already exist and both already reserve the slots:

- **Implementation record** goes into `step9_plan.md` as a new dated
  section, next after §12.
- **Deployment outcome** goes into `step9_streamlit_deployment.md` **§3.4
  "Record the result"**, which exists for precisely this and explicitly says
  a silent undocumented attempt is worse than not trying.

A fourth file would mean four places to check and would fragment the record
further. Only revisit this if `step9_plan.md` becomes unnavigable, in which
case the right move is to split the superseded sections out, not to add a
new document alongside them.

---

## 00. Session 2026-08-01 (evening) — Step 8 COMPLETE, docs reconciled

**Superseded in part by §000 above. Still authoritative for the Step 8
results and the Step 9 build-out plan.**

### Step 8 is finished

**Tier 1 Faithfulness: DONE.** 148/150 (98.7%) succeeded. Mean 0.9615,
median 1.0, neutral 0.9616 vs contradictory 0.9613 (a 0.0003 gap, i.e. query
type does not affect grounding). Results in
`results/ragas_faithfulness_result.json`, chart in
`results/step8_faithfulness_chart.png`, raw checkpoints in `data/`. This is
the rubric deliverable and it is met.

**Two queries failed permanently: q032, q068.** Identical upstream
`instructor` structured-output error on two separate runs, ~137s each vs a
normal 6-11s. Four content hypotheses tested and ruled out (answer length,
citation count, citation formatting, non-ASCII in context). Excluded, not
imputed. Full trail in `step8.md` §4a.7.

**Tier 2 Answer Relevancy: CLOSED as infeasible, not parked.** Five attempts.
The `embed_query` defect was actually solved (modern
`collections.AnswerRelevancy` + modern `GoogleEmbeddings`), but underneath it
sits a closed contradiction: a notebook event loop forces the async
`ascore()` path, `ascore()` needs an async LLM, an async LLM needs
`client.aio`, and ragas's instructor adapter rejects `AsyncClient` by type.
Attempt 4 ran the sync path inside a `ThreadPoolExecutor` thread, escaped the
event-loop check, and still hit the client-typing error, which proves the
deadlock is about client typing rather than the notebook. Report it as
attempted-and-infeasible, never as skipped. `step8.md` §4a.8.

**Tier 3 Context Precision: NOT RUN, closed by decision.** See the §2a
closure note below and `step8.md` §2b. It is a disclosed limitation, not an
open question.

**Decision: no `step8_methodology.md` will be written.** Cancelled as
duplication. `step8.md` §4a already holds the method; a new §7 consolidates
every reportable limitation in one citable list, and §7a holds the Step 8
next-to-do. See `step8.md` §7a for the rationale.

### The §2a rubric question is CLOSED. Do not raise it again.

**DECIDED by Yan-Bo, 2026-08-01, final. Recorded in `step8.md` §2b.**

No question will be asked of Prof. Sushmita or a TA about the RAGAS scope.
The decision was made on the project's own judgement and does not await
anyone's reply:

- **Tier 1 Faithfulness**: delivered, 148/150, mean 0.9615. This is the
  RAGAS deliverable.
- **Tier 2 Answer Relevancy**: closed as attempted-and-infeasible, reported
  as a documented note with the five-attempt evidence trail. Never worded as
  skipped.
- **Tier 3 Context Precision**: NOT RUN. Carried as a report limitation
  (`step8.md` §7 item 4) and as a future-work bullet. Off the schedule
  permanently, so its ~1,500 calls no longer compete with Step 9 for quota.

**Instruction to any future session:** Step 8 has zero blocking items. If a
stale section further down this file, or §0b item 2, or §2 item 1, still
frames the rubric question as open, that text is superseded by this
paragraph. Do not re-propose asking the professor about RAGAS scope.

### Kaggle notebook: a trap worth remembering

**Never use "Save & Run All" on `step8-ragas-faithfulness-pilot-yb`.**
`/kaggle/working/` is session-scoped, so a fresh container starts with an
empty checkpoint, Cell 7's resume logic concludes 0/150 are done, and the
full 150-query pass re-runs at roughly 300 API calls. Quick Save is always
safe. A warning markdown cell now sits at the very top of the notebook. If
Save & Run All is ever genuinely needed, first publish
`step8_faithfulness_full150.jsonl` as its own Kaggle Dataset and repoint
Cell 7's `CKPT_PATH_FULL` at that input path.

### Step 9: the quota premise has dissolved

`step9_plan.md` §8 made Step 9's scope tiered (Tier 1 = ~20 queries, Tier 2 =
all 150) and deliberately refused to freeze it until the Step 8 quota picture
resolved. It has now resolved, in the permissive direction: 150 sequential
Gemini calls completed in one sitting with zero 429s. Step 9-A's full
coverage costs ~150 calls, the same order.

**So Tier 2 is no longer quota-gated.** What is left is engineering time
before 08-11, plus the risk that Tier 3 competes for the same daily quota if
the professor's answer makes Context Precision mandatory. Recorded as
`step9_plan.md` §8a. This removes a constraint; it does not make the
decision.

### Documentation reconciled this session

| File                                                | Change                                                                                                                                                                                                |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `step8.md`                                          | §4a.7 Tier 1 results + q032/q068 investigation; §4a.8 Tier 2 closure with all 5 attempts; §7 consolidated limitations; §7a next-to-do and the no-methodology-file decision; §6a items 4 and 5 updated |
| `notebooks/step8-ragas-faithfulness-pilot-yb.ipynb` | Save & Run All warning at top; Cell 10 visualisation; Tier 2 summary table. Now 46 cells including the full 9b-9f investigation trail                                                                 |
| `step9_plan.md`                                     | §8a added: the quota premise behind the tiered scope has dissolved                                                                                                                                    |
| `step9_streamlit_deployment.md`                     | §0 status update: blockers 1, 2, 4 FIXED; blocker 3 still open; venv is `.venv-cs5340-app` not `.venv-app`; §3.1 done, §3.2 onward untouched                                                          |
| `step9_streamlit_demo_draft.py`                     | Marked SUPERSEDED, points to `app/streamlit_app.py`, self-referencing filename fixed                                                                                                                  |
| `app/streamlit_app.py`                              | Faithfulness metrics added to the footer (q033 1.000, corpus mean 0.9615, by-type split)                                                                                                              |
| `data/README_data.md`                               | Step 8 raw checkpoints documented; RQ1 preview SPD +0.033 corrected to the reportable +0.029                                                                                                          |
| `results/README_results.md`                         | NEW. Results dictionary for the whole folder, with a full section on the Step 8 output                                                                                                                |
| `data/kaggle_datasets.md`                           | Step 8 usage added; `queries_all_150.json` documented as existing in two datasets                                                                                                                     |

### Next step: Step 9-A/B build-out and deployment (supersedes §0b's critical path below)

**This is now the critical path.** §0b below is stale — items 1 and 2 there
(the quota discrepancy and the rubric confirmation) are the old Step 8
blockers, already resolved or downgraded per §00 above. The ordered plan
from here:

1. **Step 9-0: freeze the bundle schema** (`step9_plan.md` §10) and decide
   the scope call now that §8a removed the quota constraint — Tier 1
   (~20 queries) as a guaranteed floor, or go straight for Tier 2 (all 150)
   since the marginal cost is engineering time only, not API risk.
2. **Step 9-A: generate the RQ3-intervention data.** For each query in
   scope: re-rank with institution-aware MMR (λ=0.8, fixed operating
   point per §0b item 6 below), then one extra Gemini generation call per
   query on the re-ranked context. This is the actual gap — everything in
   `app/streamlit_app.py` right now for the intervention panel
   (`INTERVENTION_PAPERS_MOCK`) is illustrative, not this output.
3. **Step 9-B: build `app/data/step9_bundle.json`** from 9-A's output,
   schema per `step9_plan.md` §10, and confirm it is NOT gitignored
   (`git check-ignore -v app/data/step9_bundle.json` must print nothing —
   Blocker 3 in `step9_streamlit_deployment.md` is still open exactly
   because this file doesn't exist yet).
4. **Wire `app/streamlit_app.py` to read the bundle** instead of the
   hardcoded `BASELINE_PAPERS` / `INTERVENTION_PAPERS_MOCK` lists, and
   populate the query selectbox from the bundle's query list. Remove the
   "illustrative — pending Step 9-A" pill once this lands, since it will no
   longer be true.
5. **Attempt the actual Streamlit Community Cloud deployment**
   (`step9_streamlit_deployment.md` §3.2 onward — §3.1's local dry run is
   already done). This has never been attempted end to end; treat it as
   having unknown failure modes and budget time accordingly, per the
   document's own reasoning for doing this early.
6. Record the outcome (public URL, or the exact error) back into this memo,
   per the deployment doc's §3.4 instruction — a silent, undocumented
   attempt is explicitly called out there as worse than not trying.

### NEW 2026-08-01: `deliverables_checklist.md`

Created at WD(working directory) root. Transcribes Prof. Sushmita's Week 14 rubric (12 slides,
report sections, GitHub contents) and maps every line to a real artifact or
marks it open. §1 of that file lists six verified gaps between the rubric
and what exists. Three matter:

- **G1 Fair-Top-K is not implemented.** The rubric names it under Mitigation
  on Slide 8 and in Methodology. `results/rq3_results.json` contains only
  `mmr_semantic_by_lambda` and `mmr_institution_by_lambda`.
- **G2 Perspective-balanced prompting is not implemented.** Known and
  reasoned (§3 below), but currently reads as an omission rather than a
  choice. Needs an explicit sentence on Slide 8 and in Methodology.
- **G5 Background needs 20+ peer-reviewed conference papers**, venue-checked.
  Never counted. Most mechanical remaining risk, fully front-loadable.

Also recorded there: `results/rq3_results.json` `config.n_queries` is **100,
not 150**. RQ3 was run on the neutral set only. This interacts with the
"100-query audit" GitHub deliverable wording and with Step 9's scope call.

### Two judgement calls worth preserving

**Why Faithfulness went in the app footer, not the baseline panel.** The
answer text displayed in panel 1 is placeholder wording, but the Faithfulness
score was computed against the real stored Gemini output. Putting the score
beside the placeholder would imply it describes the visible text. Footer
placement keeps it honest as a system-level indicator.

**Why no confidence interval on Faithfulness.** RQ1/RQ2/RQ3 need CIs because
they test whether a quantity differs from zero. Faithfulness is descriptive
system quality with no pre-registered null, so a CI would imply a hypothesis
test that was never registered. Reported as means and stdevs only.

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
2. **[CLOSED 2026-08-01, STALE TEXT BELOW]** ~~Confirm the rubric reading
   with Prof. Sushmita or a TA: is "RAGAS Faithfulness scores" the whole
   requirement, or shorthand for the RAGAS suite?~~ Superseded by §00's
   closure note and `step8.md` §2b. Decided internally, no one is being
   asked, Tier 3 is out of scope as a disclosed limitation.
3. **[DONE 2026-08-01]** `rq2_frameworkB_generation_raw.jsonl` uploaded to
   the Kaggle dataset `step7-frameworka-for-raj` (display title renamed to
   `step7_frameworkAB_result_for_Raj`; URL slug unchanged — see
   `data/kaggle_datasets.md`). Confirmed working: the Step 8 pilot
   notebook's Cell 1 resolves both `rq2_gen_checkpoint.jsonl` (100 records)
   and `rq2_frameworkB_generation_raw.jsonl` (50 records) from it, 150/150
   total. That file being Framework-A-only
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
