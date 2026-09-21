# Final Deliverables Checklist (CS6200, Summer 2026)

**Created 2026-08-01. Deadline 2026-08-11, 20:59.**

**2026-08-10 sync.** Numbers updated after the three-way merge (Raj step8-ragas,
Jici power-analysis) and Step D. Two headline figures changed and one gap
closed: Faithfulness is now Raj's 150/150 run per decision D2, Answer Relevancy
is adopted per D1, and Framework B carries a second independent-judge number.
Superseded values are struck through rather than deleted, so the audit trail
survives.

Source of truth for what the course actually requires, checked against what
this project actually has. Rubric text is transcribed from Prof. Sushmita's
Week 14 brief. Status columns are evidence-based: every "have it" must name
a real file, not an intention.

All three deliverables are **per team**: ACM-style PDF report, GitHub
repository link inside the report, and presentation slides.

**Owners.** Report PDF: Jici. RQ1 / RQ2 / Step 8 / Step 9 sections and the
Streamlit app: Yan-Bo. Data pipeline and ChromaDB: Raj.

---

## 1. Gaps against the rubric, verified 2026-08-01

Read this section first. These are places where the rubric names something
this project does not currently have. Each needs either work or an explicit
disclosure sentence. Silence is not an option under this project's
disclosure standard.

| #   | Gap                                                                                                                                               | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Options                                                                                                                                                                                              |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| G1  | ~~**Fair-Top-K re-ranking not implemented.**~~ **RESOLVED 2026-08-03.** Rubric names it in Slide 8 and in Methodology/Mitigation.                 | Implemented in `notebooks/step6-reranking-yb-optimized-basedon-jici.ipynb` §7e; measured results in `results/rq3_results.json` (`fair_top_k`, `fair_top_k_spd_ci`) and written up in `rq3_methodology.md` §8a/§10 and `step6_fair-top-k_methodology.md` §7/§9. Headline: SPD -0.046, 95% CI [-0.049, -0.044], a statistically significant over-correction into reverse bias, distinct in kind from institution-aware MMR's non-significant SPD.                                                                                                                                                                                 | Done. No further action; §1a below is now a historical cost-survey record, not an open recommendation.                                                                                               |
| G2  | **Prompt engineering for perspective balancing not implemented.** Rubric names it in Slide 8 and Methodology/Mitigation.                          | `Claude_todo_memo.md` §3: planned in `rq2_plan.md`, never built, because Framework B retention was already 97.2% so there was no suppression to fix. Already documented in `rq2_methodology.md`.                                                                                                                                                                                                                                                                                                                                                                                                                                | Keep the decision, but surface the rationale explicitly on Slide 8 and in Methodology. As written it currently reads as an omission rather than a reasoned choice.                                   |
| G3  | **Model mismatch.** Rubric Slide 5 says "Gemini 1.5 Flash". This project used `gemini-3.1-flash-lite` throughout.                                 | Step 7a/7b generation, Step 8 judge, RQ2 Framework B judge.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | One line on Slide 5 and in Methodology naming the actual model and version. Do not silently print the rubric's model name.                                                                           |
| G4  | **"100-query audit" vs the pre-registered 150.** GitHub deliverable asks for "JSON file containing results of the 100-query audit".               | Pre-registered scope is 150 (100 neutral + 50 contradictory). RQ1 and RQ3 both run on **q001-q100 neutral only**; q101-q150 are deliberately held out for RQ2 Experiment B. Source: `handoff_status_rq1_for_step6.md` ("q101-q150 are contradictory and held out for RQ2. Compute the main SPD on neutral only"), carried into `rq3_methodology.md` §1 as a locked convention and §8 as "100 (neutral, q001-q100)". This is BY DESIGN and already documented. Note it is NOT caused by missing subcategory labels: every one of the 150 queries carries a `subcategory` field, contradictory ones included (q150 = `q-bio.SC`). | Low risk. State once in the README that "the 100-query audit" refers to the neutral Experiment A set, and that the other 50 are the Experiment B set. Make sure Raj and Jici use the same wording.   |
| G5  | **Background citation count and type.** Minimum 20 peer-reviewed conference papers from SIGIR, FAccT, ECIR, CIKM, WWW, or ACL. No blogs, no news. | Not yet counted. arXiv preprints that were never formally published may not count toward the 20.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Count the current reference list, classify each by venue, and fill any shortfall before Jici locks the PDF.                                                                                          |
| G6  | **Slide 7 wording: "Pro-Consensus vs. Dissenting token ratio analysis".**                                                                         | This project measured Framework B **viewpoint retention** (36/50 eligible, 35/36 retained, 97.2%), which is not literally a token ratio.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Verify against `rq2_methodology.md` whether a token-ratio quantity exists. If not, map the rubric term to what was actually measured and say so, rather than relabelling retention as a token ratio. |

---

## 1a. G1 Fair-Top-K: cost survey and recommendation (2026-08-01)

**Historical record as of 2026-08-03 — G1 is now resolved (see the table
above).** This section is kept because the cost survey and the "why
implementing beats defending" reasoning are still useful context for how
the report frames Fair-Top-K, but the recommendation itself has been acted
on; nothing below is still an open decision.

**Recommendation: implement it.** An earlier draft of this file offered
"argue it away" as an equal option. That has been downgraded, for two
reasons.

**Why the plan-level defence does not hold.** `step5.md` Next Steps wrote
Step 6 as "Fair MMR / Fair-Top-K", a slash, i.e. either/or. That was this
project's own earlier plan. The Week 14 rubric came later and lists MMR,
Fair-Top-K, and perspective-balanced prompting together under Mitigation.
A later instruction from the course outranks an earlier internal plan, so
"we only ever planned one" is not a defence. It may be mentioned as
background, never as justification.

**Why implementing is cheaper than defending.** WD survey:

| Item                                  | Location                                                                       |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| Step                                  | Step 6 (RQ3 re-ranking)                                                        |
| Main notebook                         | `notebooks/step6-reranking-yb-optimized-basedon-jici.ipynb`, 30 cells          |
| Older version                         | `notebooks/step6_reranking.ipynb`                                              |
| Generic eval harness                  | Cell 17 `evaluate(ranker)`, accepts any `ranker(pool) -> [paper_ids]`          |
| Existing rankers                      | Cell 15 `rerank_mmr(pool, lam)`, Cell 21 `rerank_labelaware(pool, lam, field)` |
| Candidate-pool labels, already cached | `data/candidate_labels.json`                                                   |
| Output assembly                       | Cell 29 `out` dict, written to `results/rq3_results.json`                      |
| Method doc to update                  | `rq3_methodology.md`                                                           |

The work is: one new function that splits the candidate pool by
`elite_label` and interleaves, one `evaluate()` call, one new key in the
Cell 29 dict. Roughly 20 lines. **Zero OpenAlex calls and zero LLM calls**,
because `data/candidate_labels.json` already holds the pool labels. The only
real cost is re-running the notebook's front sections on Kaggle to rebuild
embeddings, query encodings, and candidate pools.

**How to frame it in the report.** Fair-Top-K is a contrast arm, not the
recommended method. Running it converts the three quantitative arguments
against a hard quota (resolution, groupability, assumption-replacing-
measurement) from reasoning into measured numbers, which is the actual gain.
Those three arguments are written out in full, with this project's own
figures, in `Claude_todo_memo.md` §000. They belong in `rq3_methodology.md`
as a new section.

**Not a valid defence.** `step5.md` Next Steps wrote "Fair MMR /
Fair-Top-K", a slash. That is an internal plan predating the rubric, so it
cannot justify shipping only one method. Background at most.

**Also not usable.** Three other groups' final reports exist and one was
briefly used to source comparison numbers. They are classmates' unpublished
coursework, not peer-reviewed literature. Do not cite them.

---

## 1b. G2 prompt engineering: disclosure sentence (drafted 2026-08-03)

Recommendation unchanged: do not implement perspective-balanced prompting
retroactively just to fill the slot. The reasoning already in `rq2_plan.md`
and `rq2_methodology.md` is sound — Framework B's baseline retention was
already 97.2%, so there was no suppression problem for the mitigation to
fix. What was missing was an explicit sentence surfacing that reasoning on
Slide 8 and in Methodology, so it reads as a checked-and-not-needed decision
rather than an omission. Drafted sentence, ready to paste into both
locations:

> Perspective-balanced prompting was planned as a Framework B mitigation
> but was not triggered: baseline retention was already 97.2% (35/36
> eligible queries), leaving no dissent-suppression problem to correct.
> RQ3's mitigation results (this slide) therefore cover MMR and Fair-Top-K
> only.

Use as-is on Slide 8 (short form) and in report §3.4 Mitigation (can expand
with the exact retention CI [91.7%, 100.0%] if space allows).

---

## 2. Slides (maximum 12, 15-minute presentation)

Current deck: `FairSearch_qBio_project_update3_slides_Jici_Raj_YanBo.pptx`
(12 slides, built 2026-08-10, speaker notes on every slide). Supersedes
`FairSearch_qBio_deck_v1_2_MODIFIED.pptx`. Confirm the deck
maps onto this structure and does not exceed 12 slides.

**Submission channel (decided 2026-08-10): this file is NOT tracked in the
git repository.** The rubric's GitHub requirements (section 4 below) do not
list the slide deck, so this is not a gap against that rubric. It is
submitted to the course separately from the repo. Every "Source artifact"
cell in the table below naming this `.pptx` refers to that separately
submitted file, not to anything findable by cloning this repository.

| #   | Rubric requirement                                                                                                                  | Have it?    | Source artifact                                                                                                 | Note                                                                                                                  |
| --- | ----------------------------------------------------------------------------------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 1   | **Title and Team.** Project title, member names.                                                                                    | yes         | Slide 1, `FairSearch_qBio_project_update3_slides_Jici_Raj_YanBo.pptx`                                                                                                 | Title, subtitle, three RQ labels, all three member names, instructor, repo URL.                                       |
| 2   | **Problem and Motivation.** Final refined research problem, why it matters.                                                         | yes         | Slide 2, `FairSearch_qBio_project_update3_slides_Jici_Raj_YanBo.pptx`; `README.md`                                                                                    | Opacity of the pipeline, why q-bio is the harder case, and the three commitments that make the audit trustworthy.     |
| 3   | **Research Questions and Hypotheses.** RQ1, RQ2, RQ3 plus initial hypotheses.                                                       | yes         | Slide 3, `FairSearch_qBio_project_update3_slides_Jici_Raj_YanBo.pptx`; `rq1/rq2/rq3_methodology.md`                                                                   | Each RQ carries its hypothesis and its metric. A footer states the hypotheses were fixed before any run, which is the required framing given several CIs cross zero. |
| 4   | **Dataset and Demographic Mapping.** arXiv sample, preprocessing, proxy labeling.                                                   | yes         | `step2.md`, `data/README_data.md`, `data/qs_top50_elite_2026.json`                                              | ~55,300 q-bio papers. Disclose the smapse.com provenance of the bio elite list.                                       |
| 5   | **System Architecture.** Embedding model, vector DB, LLM integration, Streamlit interface.                                          | yes         | Slide 5, `FairSearch_qBio_project_update3_slides_Jici_Raj_YanBo.pptx`; `app/streamlit_app.py`                                                                         | **G3 resolved.** Five-stage pipeline diagram plus an explicit model-disclosure card naming `gemini-3.1-flash-lite` and stating the brief said Gemini 1.5 Flash. |
| 6   | **Experiment A: Retrieval Bias Audit.** Institutional distribution, SPD, Equalized Odds. Tables or figures.                         | yes         | `results/rq1_optionB_result.json`, `results/equalized_odds_results.json`, `results/rq1_optionB_elite_share.png` | SPD +0.029, SRR 1.28, CI [-0.005, +0.065] crosses zero. Needs an honest framing that does not read as a null project. |
| 7   | **Experiment B: Generative Faithfulness.** Contradictory query design, Pro-Consensus vs Dissenting token ratio, RAGAS Faithfulness. | yes         | `rq2_frameworkB_summary.md`, `results/rq2_frameworkA_ragas_summary.json`, `results/rq2_frameworkB_ragas_summary.json`, `results/rq2_frameworkB_independent_judge_result.json` | **G6 still applies (wording only).** RAGAS is now 150/150, 0 failures: Faithfulness 0.978 neutral / 0.966 contradictory; Answer Relevancy 0.914 (n=100 neutral only, strictness=1). ~~148/150, mean 0.9615~~ superseded by D2. Framework B must show BOTH judges: self 97.2% and independent 77.8%. `step8_faithfulness_chart.png` is STALE (148/150) and must not be used. |
| 8   | **Mitigation Results.** MMR, Fair-Top-K, prompt engineering. NDCG@10 and MRR. Fairness-Utility tradeoff.                            | yes         | `results/rq3_results.json`, `results/rq3_three_way_comparison.png`, `results/rq3_lambda_ablation.png`, `results/rq3_institution_ablation.png` | **G1 resolved** (Fair-Top-K implemented and charted). **G2 remains a disclosure**, sentence drafted in §1b and now on the deck. ~~Only MMR exists today~~ no longer true. |
| 9   | **Streamlit Fairness Scorecard Demo.** Screenshots or live demo.                                                                    | yes         | `app/streamlit_app.py`, `app/data/step9_bundle.json`, **live at https://fairsearch-qbio-demo.streamlit.app/**   | Step D complete; bundle regenerated 2026-08-09 with all four items. Both screenshots (Update 3 deck) AND a public live demo are available. Demo precomputes 20 of 150 queries (Tier 1, seed 42) by design; state that whenever the demo is shown. Deployment date not recorded (see `Claude_todo_memo.md` post-deadline addendum). |
| 10  | **Key Takeaways.** 3 to 4 main findings.                                                                                            | yes         | Slide 10, `FairSearch_qBio_project_update3_slides_Jici_Raj_YanBo.pptx`                                                                                                | Four takeaways, including the independent-judge gap and an explicit "no confirmed bias is not the same as fair".      |
| 11  | **Future Directions.** 2 to 3 concrete directions.                                                                                  | yes         | Slide 11, `FairSearch_qBio_project_update3_slides_Jici_Raj_YanBo.pptx`                                                                                                | Three directions, each with a named first step. Context Precision is one of them, per `step8.md` §2b.                 |
| 12  | **Questions and Discussion.**                                                                                                       | yes         | Slide 12, `FairSearch_qBio_project_update3_slides_Jici_Raj_YanBo.pptx`                                                                                                | Closing slide with five prompt chips for likely questions.                                                            |

Slide scripts: English roughly one minute per slide. Slides 3 to 10 English
scripts and Chinese drafts for slides 4 to 10 were still pending at the last
session.

---

## 2a. Disclosure obligations attached to the new numbers (added 2026-08-10)

These are not optional caveats. Each one must appear wherever its number is
printed, in the deck, the report, and the app.

| Number | Obligation |
| --- | --- |
| Faithfulness 0.978 / 0.966 | State that Faithfulness was measured twice with two different context construction methods, that the earlier run scored 0.9615 (148/150), and that the difference traces to context formatting rather than data quality. Exact required sentence: `comparison_step8_with_step8_ragas.md` section 4. Never print 0.978/0.966 bare. |
| Answer Relevancy 0.914 | State n=100, NEUTRAL ONLY (the contradictory checkpoint carries no answer_relevancy field), and `strictness=1`, which was required because `gemini-3.1-flash-lite` rejects the ragas default of 3. Never cite it as a 150-query figure. |
| Framework B retention | Never print 97.2% alone. The independent judge measured 77.8% on the same 36 queries. Both numbers, or neither. |
| Fair-Top-K SPD -0.046 | Report as a statistically significant over-correction into reverse bias, not as a successful fix. |
| Any RQ1/RQ2A headline | The bootstrap CI crosses zero. Report descriptively; no pass/fail language, since no threshold was pre-registered. |

---

## 3. ACM-style PDF report (6 to 10 pages, final cumulative version)

Owner: Jici. Yan-Bo contributes RQ1, RQ2, Step 8, Step 9 material.

### 3.1 Problem Description

Final refined version carried forward from prior submissions.
Status: **yes.** `README.md` was rewritten 2026-08-10 with the final problem
statement; Slide 2 of the Update 3 deck carries the same framing.

### 3.2 Background

Minimum **20 peer-reviewed conference papers** (SIGIR, FAccT, ECIR, CIKM,
WWW, ACL). No blogs, no news articles. Each paper written up in the
mandated three-part structure:

1. What is it about?
2. What did they do to solve the problem?
3. What were the limitations or conclusions?

Status: **G5 open.** Count not yet done, venue classification not yet done.
This is the single most mechanical remaining risk in the report, and it is
entirely front-loadable. Do it before prose polishing.

### 3.3 Dataset

Final version incorporating all preprocessing and enrichment across phases.
Status: have it. `step2.md`, `data/README_data.md`, `rq1_methodology.md`
§10 for the bio robustness check.

### 3.4 Methodology

Complete description of all experiments:

- **Experiment A, Retrieval Bias Audit:** query design, institutional
  distribution, SPD, Equalized Odds. Have it: `rq1_methodology.md`,
  `query_generation_methodology.md`.
- **Experiment B, Generative Faithfulness:** contradictory query design,
  Pro-Consensus vs Dissenting token ratio, LLM-as-a-judge, RAGAS
  Faithfulness. Mostly have it: `rq2_methodology.md`, `step8.md` §4a.
  **G6 applies** to the token-ratio wording.
- **Mitigation:** MMR, Fair-Top-K, prompt engineering for perspective
  balancing. **G1 and G2 apply.** `rq3_methodology.md` covers MMR only.

### 3.5 Result Analysis

Full analysis across all experiments, answering all three RQs with
empirical evidence, using tables and figures throughout.

Measured results available for citation, do not restate from memory:

| Result                                | Value                                                                | File                                     |
| ------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------- |
| RQ1 SPD                               | +0.029, SRR 1.28, 95% CI [-0.005, +0.065], crosses zero              | `results/rq1_optionB_result.json`        |
| RQ1 bio robustness                    | SPD +0.031, CI still crosses zero                                    | `results/rq1_optionB_result_bio.json`    |
| RQ1 Equalized Odds                    | signed CI crosses zero, no systematic direction                      | `results/equalized_odds_results.json`    |
| RQ2 Framework A                       | mean amplification +0.0041, CI crosses zero                          | `rq2_frameworkA_summary.md`              |
| RQ2 Framework B, self-judge           | 35/36 retained, 97.2%, CI [91.7%, 100.0%]                            | `results/rq2_frameworkB_result.json`     |
| RQ2 Framework B, independent judge    | 28/36 retained, 77.8%, CI [63.9%, 91.7%]; agreement 80.6%, 7 disagreements, all one-directional (6:1), unadjudicated | `results/rq2_frameworkB_independent_judge_result.json` |
| RQ3 institution-aware MMR, lambda=0.8 | SPD +0.0163, CI crosses zero; improvement vs baseline is significant | `results/rq3_results.json`               |
| RQ3 diversity gain, lambda=0.9        | +0.17 unique institutions, CI [0.09, 0.26], significant              | `results/rq3_results.json`               |
| Step 8 Faithfulness (D2, headline)    | 150/150, 0 failures. Neutral 0.978 (n=100), contradictory 0.966 (n=50) | `results/rq2_frameworkA_ragas_summary.json`, `results/rq2_frameworkB_ragas_summary.json` |
| Step 8 Faithfulness (superseded)      | ~~148/150, mean 0.9615, neutral 0.9616 vs contradictory 0.9613~~ retained only as the second run cited in the D2 disclosure | `results/ragas_faithfulness_result.json` |
| Step 8 Answer Relevancy (D1)          | 0.914, 95% CI [0.899, 0.927], n=100 NEUTRAL ONLY, strictness=1        | `results/rq2_frameworkA_ragas_summary.json` |
| Step 8 Context Precision (D3)         | 0.039, out of scope, supporting evidence only for the limitation paragraph | `results/rq2_frameworkA_ragas_summary.json` |

Framing note. Most headline CIs cross zero. The report must present this
descriptively, per the project's standing "no post-hoc verdicts" rule, and
must not be written as though the project failed to find anything. The
finding is that institutional bias in this corpus is not detectable at this
sample size, which is a result, stated with its CI.

### 3.6 Conclusion and Discussion

3 to 4 key takeaways. For each, what it reveals about fairness in RAG and
in academic IR more broadly.

### 3.7 Future Directions

2 to 3 concrete directions. Candidates already documented: Tier 3 Context
Precision (`step8.md` §2b), Framework B elite-share extension which would
need its own pre-registration, larger sample for RQ1 power.

### 3.8 References

ACM format. Cross-check against G5.

---

## 4. GitHub repository

The link must appear inside the report.

| Required item                                   | Have it?    | Note                                                                                                                                     |
| ----------------------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Data preprocessing scripts                      | yes         | Exported into the repo, not only on Kaggle: `notebooks/step1-data-prep.ipynb`, `step1b-institution-labels-full-yb.ipynb`, `step2-embedding.ipynb`, `step3_chromadb.ipynb`. Named in README. |
| RAG pipeline code                               | yes         | `notebooks/step5-retrieval-baseline-yb-kaggle-150.ipynb` (retrieval), `step7-rq2-generation-frameworka-yb.ipynb` and `step7-rq2-generation-frameworkb-yb.ipynb` (generation). All committed. |
| Re-ranking implementations                      | yes         | `notebooks/step6-reranking-yb-optimized-basedon-jici.ipynb` contains institution-aware MMR **and** Fair-Top-K. **G1 resolved.**          |
| Streamlit fairness scorecard app                | yes         | `app/streamlit_app.py` reads `app/data/step9_bundle.json`; the mock lists are gone. Confirm the bundle is not gitignored before submitting. |
| JSON file with results of the 100-query audit   | yes         | **G4 resolved.** `results/rq1_optionB_result.json` is named explicitly in README under "Where the graded deliverables live", with a scope note explaining the 100-neutral / 50-contradictory split and a table of supporting per-stage result files. |
| README with setup and reproduction instructions | yes         | Rewritten 2026-08-10. Two separate setup paths (app-only vs research), the RAGAS stack table per `step8.md` §4a.6, and an explicit statement that 18 of 24 notebooks hardcode `/kaggle/` paths so no local end-to-end run is claimed. |

~~Also confirm `app/data/step9_bundle.json` is not gitignored once it exists.~~
**Verified 2026-08-10:** `git check-ignore -v app/data/step9_bundle.json` prints
nothing and the file is tracked by git. Blocker 3 in
`step9_streamlit_deployment.md` is cleared.

---

## 4a. FINAL PASS 2026-08-10 — what is still genuinely open

Every "verify" and "partial" above has been resolved to "yes" with a named
file, except the items below. These are real, not bookkeeping.

| # | Open item | Owner | Why it is still open |
| --- | --- | --- | --- |
| G5 | **20 peer-reviewed citations, counted and venue-classified.** | Jici | Never counted. arXiv preprints that were never formally published may not qualify. This is the single most mechanical remaining risk and is entirely front-loadable. |
| G6 | **Slide 7 wording vs the rubric's "Pro-Consensus vs Dissenting token ratio".** | Yan-Bo | This project measured viewpoint *retention*, not a token ratio. The deck reports retention honestly and does not relabel it, but no sentence yet explicitly maps the rubric term onto what was measured. One sentence fixes it, in the report and optionally on Slide 7. |
| — | **McNemar's test on the paired judge data.** | Jici | Flagged in `merge_for_final.md` §6 and disclosed in `rq2_frameworkB_summary.md` and on the deck as not run. Acceptable to ship disclosed; better to run. |
| — | **Blinded adjudication of the 7 judge disagreements.** | — | Pre-registered as out of scope before the deadline. Displayed as unadjudicated everywhere. **Do not confuse this with the work Jici completed:** running the independent judge and identifying the 7 cases plus their 6:1 direction split is DONE; deciding which judge was right is NOT. The bundle keeps `adjudicated: false` / `adjudication_verdict: null` so a later review needs no bundle regeneration. Correct phrasing: "two judges disagree on 7 of 36 and we do not know which is correct." |
| — | **Keep the two "two-number" situations apart.** | Yan-Bo | Framework B has two *judges*; RAGAS Faithfulness has one judge and two *runs* differing only in context construction. Raised by Jici 2026-08-10. Already enforced in the app and the bundle (`single_judge_disclosure`), and stated in `rq2_frameworkB_summary.md`. Listed here so a report writer does not merge them into one "we validated with a second model" claim. |
| — | **Report PDF assembly.** | Jici | In progress in Overleaf, out of git scope. |

Repository housekeeping deliberately NOT done, recorded so it is a decision
rather than an oversight: several superseded files remain in the repo
(`step9_streamlit_demo_draft.py`, `results/step8_faithfulness_chart.png` which
holds the superseded 148/150 figure, `results/rq3_three_way_comparison copy.png`,
`notebook-q-bio.ipynb` which is a pre-Step-1 scratch notebook). They are
harmless to grading but can mislead a reader into citing a stale number. The
stale chart is the one that actually matters.

---

## 5. How to use this file

At final assembly, walk sections 2, 3, and 4 top to bottom and change every
"verify" and "partial" to either "yes" with a named file, or to a written
disclosure sentence in the report. A row left as "verify" on 08-11 means
nobody checked it.

Section 1 is the priority list. G1, G2, and G5 are the three that can still
change the grade; G3, G4, and G6 are one-sentence disclosure fixes.

_Update this file as items close. Keep it in sync with
`Claude_todo_memo.md`._
