# RQ2 Framework B - Summary

Viewpoint-diversity retention at the generation stage (contradictory queries).
Completed 2026-07-12. Owner: Yan-Bo. Notebook: step7_rq2_generation_frameworkb-yb.

This file summarizes Framework B for the report and for teammates. Authoritative
methodology lives in `rq2_frameworkb_draft.md` and `rq2_plan.md` (Decision 2
amendment); measured numbers here match the output files listed at the bottom.

**2026-08-09 addendum:** an independent-judge validation was added below (new
section, after "Measured result"). This is an ADDITION, not a revision of the
original 2026-07-12 content; nothing above that date was altered except two
places explicitly marked below, per this project's rule that post-hoc changes
must be dated and labeled rather than silently edited into the original text.

## Pre-registered question

When the retrieved top-10 context for a genuinely two-sided debate question
contains evidence for BOTH stated positions, does the generated answer
substantively keep both sides, or does it flatten them into one side?

This is the "what is said" lens (viewpoint). It is distinct from Framework A,
which is the "who is cited" lens (institution). A single model answers A on
neutral queries (q001-q100); B is a separate, later notebook on contradictory
queries (q101-q150).

Framework B was reframed once, before any judge run: the original plan named
this "dissent retention" (consensus vs dissent). Because q101-q150 mostly
encode two contrasting but non-hierarchical positions (complementary
mechanisms or open alternative theories, not a stable consensus/dissent
split), it was operationalized symmetrically as Side A vs Side B instead.
This amendment is dated before the judge run (rq2_plan.md, "Decision 2
amendment").

## Method (short)

1. A frozen side-annotation sidecar (`queries/sides_q101_150.json`) maps each
   of the 50 contradictory queries to its two stated positions (Side A / Side
   B), restating only what the original query already contains. The original
   query dataset and query_text are unchanged; retrieval and generation still
   use the original query_text.
2. Generation (baseline, no balancing instruction): gemini-3.1-flash-lite,
   temperature 0, same build_context / generate_answer / PROMPT_TEMPLATE /
   parse_citations as Framework A (verbatim reuse). 50/50 queries generated,
   0 failures.
3. Context stance judge (one call per query, judges all 10 retrieved abstracts
   at once): labels each paper supports_side_a / supports_side_b /
   mixed_or_neutral relative to the query's Side A / Side B. Tie-break rule:
   when unsure, label mixed_or_neutral (never guess a side). This defines
   ELIGIBILITY: a query is eligible only if its top-10 context has >=1
   supports_side_a AND >=1 supports_side_b.
4. Answer judge (one call per query, two independent layers):
   - Layer 1 retention_status (sole input to the headline metric):
     both_sides_retained / side_a_only_or_token_b / side_b_only_or_token_a /
     neither_or_unclear.
   - Layer 2 conclusion_favor (descriptive only, never in the metric):
     favors_side_a / favors_side_b / no_clear_favor, with a favor_basis
     category. Frequency or length never decides favor; an explicit
     evaluative/comparative statement is required.
5. Retention (per eligible query, binary): retention = 1 iff
   retention_status == both_sides_retained; retention = 0 for the other three
   statuses; retention = null (excluded from the denominator) for non-eligible
   queries.
6. Aggregate at query level; bootstrap 95% CI (resample the eligible queries,
   seed 42, 10,000 draws).

Both judge prompts are saved verbatim, version "frameworkb-judge-v1", in
`prompt/frameworkb_judge_v1.md`.

## Models

Generation: gemini-3.1-flash-lite, temperature 0 (same model and prompt
skeleton as Framework A, satisfying the no-balancing requirement directly).

Judge: primary judge gemini-3-flash-preview passed the single-call probe, but
the batch context judge hit a 429 at q115. The error reported quotaId
GenerateRequestsPerDayPerProjectPerModel-FreeTier, quotaValue 20 - this
project's free tier allows only 20 preview requests per day, far short of the
~100 judge calls needed. Fallback (pre-registered route A step 2):
gemini-3.1-flash-lite, temperature 0, for the entire judge stage. This makes
the answer judge a SELF-JUDGE (judge model == generation model), disclosed
below. The 14 context-judge records produced by preview before the 429 were
deleted before the flash-lite rerun, so no query is judged by a mix of two
models. Full account in `rq2_frameworkb_draft.md`, Models section.

## Measured result (completed 2026-07-12)

- Total contradictory queries: 50
- Eligible (context has both sides): 36
- Excluded (context has only one side or neither): 14
  (q106, q108, q109, q113, q114, q120, q125, q130, q138, q141, q142, q146,
  q147, q150)
- Retained (both_sides_retained) among eligible: 35
- **Retention rate = 35/36 = 97.2%**
- Query-level bootstrap 95% CI (seed 42, 10,000 resamples): [91.7%, 100.0%]

conclusion_favor distribution (Layer 2, descriptive only, never in the metric):
- All 50 queries: favors_side_a 4, favors_side_b 3, no_clear_favor 43
- Eligible 36 queries only: favors_side_a 3, favors_side_b 3, no_clear_favor 30

Output files (Kaggle /kaggle/working):
`rq2_frameworkB_generation_raw.jsonl`, `rq2_frameworkB_context_judge.jsonl`,
`rq2_frameworkB_answer_judge.jsonl`, `rq2_frameworkB_per_query.json`,
`rq2_frameworkB_result.json`, `rq2_frameworkB_retention.png`.

## Independent judge validation (2026-08-09)

Motivation: the self-judge design (Models section above) means the 97.2%
figure could not, on its own, rule out self-preference bias. An independent
judge run closes part of that gap.

**Setup.** Jici ran the same 36 eligible queries and the same generated
answer text through a second, genuinely different judge model
(`openai/gpt-oss-20b:free`, via OpenRouter), using the same answer-judge
prompt file and the same bootstrap method (seed 42, 10,000 resamples).
Source files: `results/rq2_frameworkB_independent_judge_result.json`,
`results/rq2_frameworkB_judge_disagreements.json`.

**Result.**
- Independent judge retention: 28/36 = **77.8%**, 95% CI [63.9%, 91.7%]
- Self-judge retention (measured above): 35/36 = 97.2%, 95% CI [91.7%, 100.0%]
- Agreement between the two judges: 80.6% (29 of 36 queries)
- Disagreements: 7 of 36 queries, **all in the same direction** — in every
  one, the self-judge said `both_sides_retained` and the independent judge
  said the answer was one-sided. 6 of the 7 were rated as retaining only
  Side B (`side_b_only_or_token_a`); 1 (q133 — the same query flagged in the
  development-stage sanity check above) was rated as retaining only Side A.

**This is a substantive finding, not a minor footnote.** A 19.4
percentage-point drop when swapping judges is large enough to weaken the
headline 97.2% figure and must be reported alongside it, never in its place
and never omitted.

**What this does and does not establish.**
- It does not, by itself, prove the self-judge was wrong. At least three
  explanations are consistent with a unidirectional 6:1 disagreement pattern,
  and this data cannot separate them: self-preference bias (the leading
  candidate, and consistent with the self-judge design disclosed above),
  a plain capability difference between the two judge models, and
  ambiguity in the retention criterion itself.
- Comparing the two 95% CIs by eye is not the right statistical test here,
  because both judges scored the *same* 36 queries — this is paired data.
  McNemar's test is the correct test for paired binary disagreement and
  **has not been run**.
- "Independent" covers only the retention judgment. Eligibility (which 36
  of 50 queries qualify) was determined once, upstream, by the original
  context-stance judge. Both retention numbers share that same denominator;
  the eligibility step itself was not independently re-derived.
- Both confidence intervals are wide at n=36. Neither 97.2% nor 77.8%
  should be treated as a settled point estimate.

**Not done before the deadline:** a blinded, pre-registered manual
adjudication of the 7 disagreement cases. The Streamlit demo displays them
as unadjudicated rather than resolved (`app/streamlit_app.py`, Framework B
panel).

## How to read this result

The measured retention rate is high and the bootstrap CI stays above 0.90.
However, no preservation threshold was pre-registered (there is no defined
"passing" retention rate), and the evaluation used a self-judge design. For
both reasons, this is reported as a descriptive measurement, NOT as a formal
verdict that the model "preserves" viewpoint diversity. Report language should
state the number and CI, then discuss interpretation separately, rather than
asserting preserves/flattens as a conclusion.

**2026-08-09 addendum, does not alter the paragraph above:** an independent
judge run (see "Independent judge validation" above) found a materially
lower retention rate, 77.8%, confirming that the self-judge risk named here
was not merely theoretical. Report language must present both numbers
together — 97.2% (self-judge) and 77.8% (independent judge) — never the
self-judge figure alone.

## Development-stage sanity check: the single retention==0 eligible query (q133)

NOT part of the pre-registered pipeline; did not change the metric or the CI.
q133 asks whether cellular decision-making is governed more by network
topology (Side A) or reaction kinetics (Side B). The generated answer cited
papers from both sides, but reframed the two supports_side_b papers ([7]
0811.2834 and [10] 1104.2845) to argue FOR Side A. The judge labelled it
side_a_only_or_token_b (retention=0), consistent with its own evidence string
and with the retention definition: citing a paper is not the same as retaining
its viewpoint. Judged reasonable, not a bug; the result was not hand-edited.
Because this is a self-judge, the direction here is against self-preference (a
purely self-protective judge would more likely have labelled this
both_sides_retained). Single-query observation, not generalized.

## Pre-registered red-flag check (5 queries, seed 42): completed

Sampled from all 50 queries (not only eligible ones), so the check also covers
context-stance judgements underlying non-eligible queries. Sample: q102, q108,
q118, q141, q148. This is a lightweight red-flag screen, NOT a statistical
validation of the judge (n=5 cannot validate); its only goal is to catch a
broadly broken judge.

Human review results:
- context_stance_label_reasonable: 3/5 ok, 2/5 partial (q118, q148; neither
  affects the eligibility conclusion for those queries)
- answer_retention_reasonable: 4/5 ok, 1/5 not_ok (q141)
- answer_favor_reasonable: 3/5 ok, 2/5 not_ok (q118, q141)

Findings from not_ok / partial cases:
- q141: the judge over-credited balance. The generated answer overwhelmingly
  supported one side with only a token acknowledgment of the other, but was
  labeled both_sides_retained. Reviewer assessment: this should likely have
  been classified as one-sided with a token mention, favoring that side. This
  error direction (crediting the judge's own generation model's output as more
  balanced than it is) is consistent with the known self-judge risk.
- q118: the judge under-detected favor. The answer's opening claim and
  explanatory detail gave one side clear explanatory primacy, but was labeled
  no_clear_favor.
- q148 / q118 (context, partial): a small number of context stance labels
  conflated adjacent evidence types (e.g. protein folding vs protein function
  evidence); eligibility conclusions were unaffected in both cases.

Decision: these two answer-layer errors are of different types (one
over-credits retention, one under-detects favor), not the same rule repeated.
Per the pre-registered qualitative standard (systematic failure = multiple
same-type errors), this was judged NOT to constitute a systematic judge
failure requiring a prompt revision and rerun. It is instead recorded as a
disclosed limitation (see below). Saved to
`rq2_frameworkB_generation_raw_checked.json`; the main metric was never
recomputed from this file.

## Key caveats (must appear in the report)

- **Self-judge.** Same model (gemini-3.1-flash-lite) generates and judges,
  which can bias toward approving its own phrasing. The q141 red-flag finding
  is a concrete instance of this risk. Mainly affects the answer
  (retention/favor) layer; the context stance layer judges other authors'
  abstracts, so self-preference is less applicable there.
- **Small eligible n (36) with an extreme proportion.** The CI upper bound
  touching 1.000 is a small-sample artifact; the entire lower bound rests on
  the single q133 case.
- **Retention is binary and defined on substantive viewpoint representation,
  not citation presence.** q133 is the clearest illustration: citing a paper
  is not the same as representing its side.
- **Judge model fallback.** Primary judge (gemini-3-flash-preview) was
  replaced by flash-lite because its free-tier daily quota (20) could not
  cover the ~100 judge calls needed.
- **Direction of residual bias — speculative when written, confirmed by
  later data (2026-08-09).** Given the q141 red-flag finding and the
  self-judge design generally, the true retention rate could plausibly be
  somewhat lower than 97.2% if judged by an independent model. This is a
  known DIRECTION of possible bias, not a corrected estimate. Addendum:
  an independent judge has since measured 77.8% (see "Independent judge
  validation" above). The direction named here was correct; this bullet's
  original wording is left as written rather than rewritten, per this
  project's rule that post-hoc findings are dated and added, not folded
  silently into earlier text.
- **Two-judge disagreement is unidirectional and unadjudicated (added
  2026-08-09).** 7 of the 36 eligible queries get a different verdict
  depending on which judge is used, and all 7 run the same direction (the
  independent judge always rates retention lower, never higher). None of
  the 7 has been manually adjudicated. See "Independent judge validation"
  above for the full account and the reasons this cannot yet be resolved
  to a single number.
- **Stance rubric scope.** supports_side_a / supports_side_b require only
  directional alignment (a core claim, mechanism, or methodological position),
  not proof of a "majority" empirical claim. One consistent operational
  definition across all 50 queries; no stance_strength dimension recorded.
- Judge prompt version "frameworkb-judge-v1"; full text in
  `prompt/frameworkb_judge_v1.md`.

## Relation to Framework A

Framework A (institutional citation amplification, neutral queries) measured
mean amplification +0.0041, bootstrap 95% CI [-0.0254, +0.0342], crossing
zero: neutral (no confirmed elite citation amplification at generation).
Framework B measures a different axis (viewpoint retention, contradictory
queries) with a different method (two LLM judges vs citation parsing). The two
frameworks are reported side by side, each answering its own pre-registered
question; they are not combined into a single score.

## Pre-registered follow-ups not run

The optional cross-model spot check (a model different from the judge,
sampling the same 5 red-flag queries) was NOT run. This is explicitly optional
per `rq2_frameworkb_draft.md`; skipping it does not violate pre-registration.

## Actual notebook cell map (differs from the draft's 12-cell plan)

`rq2_frameworkb_draft.md` pre-registered a 12-cell plan (Cell 0-11) before any
code was written. The notebook that was actually built and run,
`step7_rq2_generation_frameworkb-yb`, diverged from that numbering for two
reasons: (1) the draft's single "build_context / generate_answer /
PROMPT_TEMPLATE / parse_citations" cell was split into three separate cells to
match how Framework A's notebook was structured, and (2) an unplanned judge
model switch cell was inserted mid-run when the primary judge's daily quota
was exhausted (see Models section above). This shifted every later cell's
number relative to the draft plan. This section records what was ACTUALLY run,
cell by cell, so the two numbering schemes are never confused later.

Draft plan (as pre-registered, for reference):
```
Cell 0  setup
Cell 1  load + assertions
Cell 2  build_context (verbatim from A)
Cell 3  generate_answer + PROMPT_TEMPLATE (verbatim from A) + parse_citations
Cell 4  judge probe
Cell 5  context stance judge function
Cell 6  answer two-layer judge function
Cell 7  batch generation
Cell 8  batch judge (context then answer)
Cell 9  eligibility + retention + favor distribution
Cell 10 query-level bootstrap CI
Cell 11 save outputs + figure + report line
```

Actual notebook (as executed):
```
Cell 0  SDK check (google-genai 1.68.0)
Cell 1  load + assertions (contradictory==50, 500 slots, 484 unique ids all in
        corpus, sides sidecar 50/50 reviewed==true, query_id sets match).
        Built pmap / lmap / smap lookup dicts.
Cell 2  read GEMINI_API_KEY (non-empty check only, no "AIza" prefix assert) +
        smoke test. GEN_MODEL = gemini-3.1-flash-lite, GEN_TEMPERATURE = 0.
Cell 3  build_context(query) -> (context_text, num2pid). Verbatim from A.
Cell 4  generate_answer(query) -> (resp.text, num2pid, prompt) + PROMPT_TEMPLATE.
        Verbatim from A; no balancing language (Decision 2b).
Cell 5  parse_citations(answer_text, num2pid) -> dict with cited_pids_unique
        etc. Verbatim from A.
Cell 6  judge probe: retry logic distinguishing transient (429/503) vs
        permanent errors; used to test primary judge callability + quota.
Cell 7  context stance judge function (CONTEXT_JUDGE_TEMPLATE, batched 10
        abstracts per call). Judge returns n + stance + evidence only;
        paper_id filled by code via num2pid (dated amendment, raw != final
        for this judge).
Cell 8  answer two-layer judge function (ANSWER_JUDGE_TEMPLATE). Judge returns
        the complete JSON (retention_status, conclusion_favor, favor_basis,
        evidence); code saves as-is (raw == final, no code-filled field).
[switch] Judge model fallback switch (NOT in the original 12-cell plan).
        Inserted after the primary judge (gemini-3-flash-preview) hit its
        daily quota (20/day) mid-batch at q115. Switches JUDGE_MODEL to
        gemini-3.1-flash-lite, sets JUDGE_IS_SELF = True, records JUDGE_META
        with the fallback reason. Deletes the 14 preview-judged context
        records so no query is judged by a mix of two models.
Cell 9  batch generation over all 50 contradictory queries. Checkpoint/resume,
        429/503 exponential backoff. Result: 50/50, 0 failures. Saved to
        rq2_frameworkB_generation_raw.jsonl.
Cell 10 batch judge, two stages with tqdm progress and checkpoint/resume:
        Stage 1 context stance judge (all 50, defines eligibility), then
        Stage 2 answer two-layer judge (all 50). Saved to
        rq2_frameworkB_context_judge.jsonl and rq2_frameworkB_answer_judge.jsonl.
Cell 11 eligibility + retention (Layer 1) + favor distribution (Layer 2). Pure
        post-processing, no API calls. Fail-loud validation against the
        pre-registered enum whitelists (unknown retention_status /
        conclusion_favor values raise, never silently coerced to 0 or
        dropped). Saved to rq2_frameworkB_per_query.json.
Cell 12 query-level bootstrap CI (seed 42, N_BOOT=10000, pool = eligible
        queries only). Self-contained: reads only rq2_frameworkB_per_query.json.
Cell 13 save rq2_frameworkB_result.json (eligible/excluded/retained counts,
        retention rate, CI, favor distributions, model IDs, run date, judge
        prompt version, self-judge flag) + two-panel figure
        (rq2_frameworkB_retention.png: left = retention rate with CI error
        bar, right = denominator decomposition excluded/not-retained/retained)
        + descriptive report line (no preserves/flattens verdict).
[dev-check] Development-stage targeted sanity check (NOT in the 12-cell plan,
        NOT pre-registered): inspects the single eligible retention==0 query
        (q133) in full (query, sides, generated answer, judge evidence,
        context stance mix). Read-only; did not change any result.
[red-flag] Pre-registered red-flag check, part 1: sample 5 query_ids from all
        50 (seed 42: q102, q108, q118, q141, q148), build
        rq2_frameworkB_manual_check_todo.csv with auto-filled columns and
        blank human columns.
[merge]   Pre-registered red-flag check, part 2: after human review, merge the
        filled CSV into rq2_frameworkB_generation_raw_checked.json. Fail-loud
        validation on the 4 human columns (blank or off-whitelist values
        raise). Does not recompute or touch the headline metric.
```

Net effect on numbering: the draft's Cell 2 (one combined cell) became actual
Cells 3-5 (split into three), and the unplanned judge-switch cell added one
more shift, so everything from the draft's Cell 4 onward is offset by +2 (judge
probe: draft Cell 4 -> actual Cell 6) or +3 (batch generation onward: draft
Cell 7 -> actual Cell 9, ..., draft Cell 11 -> actual Cell 13). The three
final cells (dev-check, red-flag sample, merge) were not part of the original
12-cell plan at all; the red-flag check was pre-registered as a REQUIRED step
but not originally broken into notebook cells in the plan, and the dev-check
was an unplanned addition after seeing the retention==0 result.
