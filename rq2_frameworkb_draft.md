# RQ2 Framework B - Draft (pre-registered execution details)

Owner: Yan-Bo. Step 7 generation + Framework B analysis. Runs on Kaggle,
same pattern as Framework A and Step 5b.

This file holds the Framework B execution details NOT covered by rq2_plan.md.
rq2_plan.md stays authoritative for high-level decisions; its "Decision 2
amendment" (added 2026-07-12, before the judge run) points here for the full
rules. Where this draft and the plan disagree, the plan wins; this draft only
fills in operational detail.

All decisions below are pre-registered: written down BEFORE the Framework B
judge run, so metrics cannot be changed after seeing results. Measured numbers
will be added later in a "MEASURED RESULT" section, same as Framework A.

## What Framework B measures (final framing)

Framework B measures viewpoint-diversity retention, NOT scientific-dissent
retention. The question: when the retrieved top-10 context contains BOTH sides
of a two-sided question, does the generated answer substantively keep both
sides, or does it flatten them into one side?

Reason for symmetric Side A / Side B (not consensus / dissent): q101-q150 pose
two contrasting positions, but most are complementary mechanisms or open
alternative theories, not a stable consensus-vs-dissent split. Naming one side
"consensus" would inject more researcher subjectivity than the judge would.
So both sides are treated symmetrically.

## The side-annotation file (sides_q101_150.json)

Role: a frozen derived annotation sidecar, NOT a new query dataset. The only
query dataset is still queries_all_150.json; q101-q150 text is unchanged, and
retrieval + generation still use the original query_text. sides_q101_150.json
is queried ONLY by the Framework B judge, to supply each query's fixed Side A /
Side B.

Data flow:

    queries_all_150.json (sole query dataset, unchanged)
        - retrieval / generation : uses original query_text
        - Framework B judge      : looks up Side A / Side B in sides_q101_150.json

Safe rule (prevents the sidecar from becoming researcher-defined data):
Side A / B may ONLY restate the two positions already in the original query.
No added evidence, background, consensus call, or value judgment. Example:
q150 Side A = "Organelle size is set by molecular rulers." is OK; adding
"the traditional deterministic explanation" would NOT be OK (adds prior).

Schema (one record per contradictory query):

    {
      "query_id": "q150",
      "side_a": "Organelle size is set by molecular rulers.",
      "side_b": "Organelle size is set by a dynamic balance of assembly and disassembly.",
      "source": "auto_split",     // auto_split | manual
      "reviewed": false           // flips to true only after human full-sweep
    }

Construction: a script auto-splits the 49 queries containing " or " into Side A
(before "or") and Side B (after), restating each as a full sentence by carrying
back the query subject (grammar only, no new words). Three special cases are
handled as source="manual":
- q108: no "or" ("...better than the classical polygenic model?"). Split by
  "better than".
- q129: two "or" ("...genuine, or artifacts of limited or poorly fit data?").
  The FIRST "or" is the position boundary; the second is inside Side B.
- q143: two "or" ("...sizer mechanism or by a timer or adder mechanism?").
  The FIRST "or" is the boundary; "timer or adder" is one side.

Freezing: all 50 records start reviewed=false. A human sweeps ALL 50
(Yan-Bo Chen), confirming each Side A/B is faithful to
the original query, adds no new scientific claim, and did not mis-split. Only
then reviewed is set true and the file is frozen. After the judge run starts,
Side A/B definitions are NOT changed because of unfavorable results.

The `source` field records HOW the initial Side A/B draft was derived
(auto_split = split on the query's "or"; manual = special sentence handled by
hand for q108/q129/q143). It does NOT indicate whether the final wording was
human-reviewed. Some auto_split records still received minor grammatical
completion (e.g. q130, q134 carry a shared clause into Side B; q106/q116/q122/
q137 were made symmetric; q108 was corrected so Side B does not overclaim).
Final human confirmation is indicated ONLY by reviewed=true, not by source.

## Context paper stance labels (three classes)

For each of the 10 retrieved papers per eligible query, the judge labels the
abstract relative to the fixed Side A / Side B:

- supports_side_a : the abstract's MAIN finding clearly supports Side A.
- supports_side_b : the abstract's MAIN finding clearly supports Side B.
- mixed_or_neutral: background/method only, does not address the axis, presents
  both sides with no main stance, highly conditional, insufficient info, or the
  judge is unsure.

Substantive support requires at least ONE of: a clear core claim, a mechanism/
explanation, or a research result related to the retrieved evidence. Just
"some researchers disagree" is not substantive.

Tie-break: when unsure, label mixed_or_neutral, NOT a side. Reason: mislabeling
one paper as a side can flip a whole query to eligible; the conservative rule
reduces false-positive eligibility.

## Answer judging - TWO INDEPENDENT LAYERS

The judge labels the generated answer on two separate layers. Layer 1 is the
ONLY input to the headline metric. Layer 2 is descriptive only.

Layer 1 - retention_status (presentation: are both sides substantively there?)
- both_sides_retained    : both Side A and Side B each get >=1 substantive,
                           evidence-related point.
- side_a_only_or_token_b : Side A substantive; Side B absent or token only.
- side_b_only_or_token_a : Side B substantive; Side A absent or token only.
- neither_or_unclear     : neither side substantive, or cannot judge.
Token = a decorative one-liner ("some researchers disagree", "there are other
views") with no mechanism/claim/evidence.

Layer 2 - conclusion_favor (evaluation: does the answer judge one side better?)
- favors_side_a / favors_side_b / no_clear_favor
A favor label needs an explicit evaluative/comparative signal, one of:
- explicit_conclusion      : answer states a side is better supported/correct.
- evidence_superiority     : one side's evidence called stronger/more consistent.
- explanatory_primacy      : one side framed as primary, the other secondary.
- opposing_side_downgraded : other side called limited/overextended/speculative.
- none                     : no such signal.

Frequency/length NEVER decides favor. More sentences, more citations, a longer
paragraph, or appearing first are NOT favor signals; they are at most a
diagnostic. Example: 3 sentences on A, 1 on B, but the answer explicitly says
B's evidence is stronger -> retention_status=both_sides_retained,
conclusion_favor=favors_side_b. Reverse: only A content, no claim that A is
correct -> side_a_only_or_token_b, no_clear_favor (presentation flattened B,
but no explicit favor stated).

## Headline metric (uses Layer 1 only)

Eligibility: a query is eligible only if the top-10 context has >=1
supports_side_a AND >=1 supports_side_b. mixed_or_neutral never helps satisfy
eligibility. Non-eligible queries are excluded BEFORE bootstrap, and the
excluded count is reported.

Retention (per eligible query, binary):
- retention = 1 iff retention_status == both_sides_retained
- retention = 0 for side_a_only_or_token_b / side_b_only_or_token_a /
  neither_or_unclear

viewpoint_diversity_retention_rate = retained / eligible.
Equal coverage is not required; the answer may still conclude one side is
stronger (that is Layer 2, does not affect Layer 1).

conclusion_favor distribution is reported descriptively only, never in the rate.

## Aggregation and CI (same method as Framework A / Step 5b)

Query-level bootstrap, random_seed=42, N_BOOT=10000. Resampling pool = the
eligible queries only. Report point estimate (rate), 95% CI, and whether it is
informative given the eligible n (with only up to 50 contradictory queries and
eligibility filtering, n may be small; a wide CI is expected and is itself a
finding, not a failure).

## Judge JSON schema (what the judge must return)

Implementation note (added 2026-07-12, BEFORE the judge run). The RAW judge
response for context judging does NOT include paper_id. The judge is shown only
the numbered papers [1]..[10] (title + abstract) and returns, per paper, the
number n (1..10), stance, and a short evidence string. The code then joins
paper_id deterministically via num2pid (the same [n] -> paper_id map used for
generation). Rationale: stance and evidence require semantic judgment, but
paper_id is a fixed mapping; letting the code fill it removes any risk of the
LLM mis-copying, mis-aligning, dropping, or reformatting an id. The FINAL saved
output still matches the schema below (paper_id present); only the raw judge
response omits it, and paper_id is added by code before saving. The context
shown to the judge is the full build_context output (complete title + abstract),
identical to what the generator saw, so the judge evaluates exactly the evidence
available at generation time.

Context judging (one call per query, judges all 10 abstracts at once):

    {
      "query_id": "q101",
      "labels": [
        {"n": 1, "paper_id": "...", "stance": "supports_side_a", "evidence": "..."},
        ... 10 items ...
      ]
    }

Answer judging (one call per query):

    {
      "query_id": "q101",
      "retention_status": "both_sides_retained",
      "conclusion_favor": "favors_side_a",
      "favor_basis": "explicit_conclusion",
      "evidence": "The answer states Side A is better supported by the evidence."
    }

The short "evidence" string lets the manual red-flag check confirm the judge is
pointing at real text, not guessing. favor_basis is fixed to one of:
explicit_conclusion / evidence_superiority / explanatory_primacy /
opposing_side_downgraded / none.

Implementation note for answer judging (added 2026-07-12, BEFORE the judge run).
Unlike context judging, the answer judge returns the COMPLETE JSON with all
fields (query_id, retention_status, conclusion_favor, favor_basis, evidence) and
the code saves it as-is. There is NO code-filled field here: the answer judge
evaluates one whole generated answer, not per-paper items, so no paper_id and no
num2pid join is involved. The code only validates the JSON (allowed enum values
for retention_status, conclusion_favor, favor_basis) and stores it; it does not
add, join, or rewrite any field. So context judging has a raw-vs-final
distinction (paper_id added by code), while answer judging does not (raw == final).

Difference between the two judges (ASCII):

    CONTEXT stance judge                 ANSWER two-layer judge
    --------------------------           --------------------------
    input : 10 papers [1..10]            input : 1 generated answer
            (title + abstract)                   + Side A / Side B
    judges: each paper's stance          judges: the whole answer
    output: n + stance + evidence        output: retention_status
            (per paper, x10)                     + conclusion_favor
                                                 + favor_basis + evidence
    code  : fills paper_id via num2pid    code  : nothing added (raw == final)
    calls : 1 per query (batched 10)     calls : 1 per query
    feeds : ELIGIBILITY                   feeds : RETENTION (Layer 1 only)
            (>=1 side_a AND >=1 side_b            Layer 2 favor = descriptive
             among the 10)                        only, never in the rate

    Context judge runs on all 50 (its output DEFINES eligibility);
    answer judge's retention counts only on eligible queries.
    Both use JUDGE_MODEL, temp 0, JSON-only output parsed by _extract_json.

## Models (Framework B)

Generation (B baseline): gemini-3.1-flash-lite, temperature 0. Same model,
same PROMPT_TEMPLATE, same build_context / generate_answer / parse_citations
as Framework A (verified verbatim from step7-rq2-generation-frameworka-yb.ipynb).
The A prompt has no balancing language, so it satisfies Decision 2b directly.
parse_citations is still run and stored in the raw output for Step 8 reuse, but
it does NOT feed the Framework B retention metric.

Judge model decision tree (route A, decided 2026-07-12):
1. PRIMARY: gemini-3-flash-preview. Cell 4 must PROVE it callable with an
   actual generate_content call (listing is not proof) AND check the daily
   quota is enough (~120 judge calls needed, see below). If OK, use it.
2. FALLBACK: gemini-3.1-flash-lite (same as generation -> self-judge). Only if
   primary is not callable or quota too low. If used, disclose the same-model
   (self-judge) limitation in the report.
3. If neither works (project has no free quota), consider a fresh clean-project
   key (plan Decision 4 known risk), not enabling billing.

Preview caution: gemini-3-flash-preview is a PREVIEW model (may drift, weaker
reproducibility). Record exact model ID, run date, temperature 0, and the judge
prompt version in the output and report; note it is preview.

Models MEASURED / fallback note (recorded 2026-07-12, AFTER the batch judge run
started, but the fallback decision itself did not change any pre-registered
metric definition; it only changed WHICH judge model executed the frozen rubric).

What happened: the primary judge gemini-3-flash-preview passed the Cell 4 probe
(a single generate_content call proved it callable), but the batch context judge
hit 429 at q115. The full error reported quotaId
GenerateRequestsPerDayPerProjectPerModel-FreeTier, quotaValue 20, model
gemini-3-flash. So this project's free tier allows only 20 preview requests per
day, which cannot cover the ~100 judge calls Framework B needs. This is the same
lesson as plan Decision 4: listing / single-call callability does NOT prove the
daily quota is sufficient; only the actual batch run reveals the per-day cap.

Action taken (route A step 2, fallback): the entire judge stage was switched to
gemini-3.1-flash-lite, the same model used for generation. This makes the answer
judge a SELF-JUDGE, disclosed as a limitation (see the self-judge section). The
14 context-judge records produced by preview before the 429 were DELETED from
the checkpoint before the flash-lite rerun, so no query is judged by a mix of
two models; all 50 context judgements and all answer judgements come from a
single model (gemini-3.1-flash-lite, temperature 0).

Recorded for the run: JUDGE_MODEL = gemini-3.1-flash-lite, JUDGE_IS_SELF = True,
and JUDGE_META captures the fallback reason (preview daily quota 20). The exact
model ID, run date, temperature, and judge prompt version are saved in
rq2_frameworkB_result.json.

Impact on the metric: none by definition. The rubric, eligibility rule, and
retention definition were frozen before any judge ran. Only the executing model
changed. The self-judge risk affects mainly the answer layer (retention); the
context layer judges other authors' abstracts, so self-preference is less
applicable there.

Judge prompt version = "frameworkb-judge-v1" (named 2026-07-12, retroactive
label). This single version string identifies the two judge prompts actually
used in the batch run: the context stance judge (three-class supports_side_a /
supports_side_b / mixed_or_neutral, per-paper n + stance + evidence, batched 10
abstracts per call) and the answer two-layer judge (retention_status +
conclusion_favor + favor_basis + evidence), both at temperature 0. The name is
assigned after the run for record-keeping; it does NOT imply the string existed
before the run. The prompt TEXT itself was fixed before the batch judge run (in
the context-judge and answer-judge cells) and was not changed after seeing
results. This version string is written into rq2_frameworkB_result.json so the
reported metric is traceable to the exact prompt pair that produced it.

Cross-model spot check (OPTIONAL, small consistency check, NOT judge validation):
- Model: use a model DIFFERENT from whichever primary was used (if primary =
  3-flash-preview, cross = gemini-3.5-flash; if primary fell back to flash-lite,
  cross = gemini-3-flash-preview or gemini-3.5-flash).
- Sample: 5 queries, seed=42, SAME 5 as the manual check.
- Calls: ~5 context + ~5 answer = ~10 core, budget ~15 with probe/retry.
- If the cross model hits 429 within a few calls, SKIP it; it is optional and
  must never block the main line.
- Result saved separately (rq2_frameworkB_crossmodel_check.json), NOT merged
  into the human-check CSV, and NEVER changes the headline metric. It can only
  be labeled a "small cross-model consistency check".

## Quota budget

From scratch (generation + judge):
- 50 baseline generation (flash-lite)
- 50 context judge (1 call per query, batched 10 abstracts)
- 50 answer judge (1 call per query)
- probe + schema/JSON retry + 429/503 retry buffer: ~15-20
- total ~165-170 calls

Judge-only (if generation already done): ~50 + ~50 + buffer = ~115-120 calls.
Cell 4 threshold: confirm the primary judge quota covers ~120 calls + buffer
(check ~130), NOT 550. Batching context (10 abstracts in one call) is what
brings 500 context calls down to 50. Rate limits are per-project per-model and
must be read from the actual 429 error / AI Studio, not from a public table.

## Manual red-flag check (pre-registered, lightweight)

Scope: NOT validation. 5 Framework B queries, seed=42. Goal is only to catch a
broadly broken judge, not to statistically validate it (5 samples cannot).

Data flow (human labels never touch the main metric):

    B auto pipeline
        -> rq2_frameworkB_generation_raw.json  (clean, never hand-edited)
        -> sample 5 queries (seed 42)
        -> rq2_frameworkB_manual_check_todo.csv  (only check columns blank)
        -> human fills the check columns
        -> program merges back -> rq2_frameworkB_generation_raw_checked.json

CSV, one row per query. Auto-filled:
    query_id, query_text, side_a, side_b, context_items_json,
    primary_context_labels_json, generated_answer, primary_retention_status,
    primary_conclusion_favor, eligible
Human fills only:
    context_labels_reasonable, retention_status_reasonable,
    conclusion_favor_reasonable, check_notes
Each reasonable-column value in {ok, partial, not_ok, unclear}.
(context_items_json may include the 10 papers' paper_id, title, abstract, and
primary stance label; with only 5 rows, long cells are fine.)

Order (keeps human check and cross-model check independent):
    primary judge done
        -> sample 5 (seed 42)
        -> build human-check CSV
        -> human fills
        -> THEN run cross-model check
        -> compare side by side at the end

Systematic failure (qualitative, no fixed numeric threshold): multiple sampled
queries not_ok, or the same TYPE of error recurring (e.g. stance labels
consistently contradicting the abstract, retention_status repeatedly ignoring a
clearly-present second side). A single isolated error is an expected LLM-judge
limitation. Repeated same-type errors -> revise the judge prompt and RERUN the
affected pipeline; never hand-correct individual results into the final metric.

## Output files (Kaggle /kaggle/working, also backed up locally)

- rq2_frameworkB_generation_raw.json  : per query - query_text, context
  paper_ids, generated answer, parsed citations, citation status (Step-8 schema,
  same shape as A) + side_a/side_b used.
- rq2_frameworkB_judge_raw.json       : context labels + answer two-layer labels
  + evidence strings, per query.
- rq2_frameworkB_per_query.json       : eligibility, retention_status, retention
  0/1, conclusion_favor, per query.
- rq2_frameworkB_result.json          : eligible n, excluded n, retention rate,
  bootstrap CI, favor distribution, model IDs, run date, judge prompt version.
- rq2_frameworkB_crossmodel_check.json: optional, separate.
- one figure (retention bar / stacked stance), neutral colors, honest framing.

## Report-ready lines (fill with REAL numbers after the run)

- "The original 150-query dataset was unchanged. For Framework B we created a
  frozen side-annotation file mapping each contradictory query to its two
  explicitly stated positions for consistent stance judging."
- "A query was eligible when at least one retrieved abstract substantively
  supported Side A and at least one supported Side B. Viewpoint diversity was
  retained when the generated answer substantively represented both sides;
  equal coverage was not required, and the answer could still conclude that one
  side had stronger evidence."
- "Across N eligible debate queries, viewpoint diversity was retained in X%
  (CI [...]) -> [flattens / preserves]."

## Self-judge / limitations to disclose in the report

- If judge = generation model (fallback), disclose self-preference risk; note
  it only affects the answer layer, since context stance judges other people's
  abstracts.
- Side A/B are researcher-frozen operational definitions restated from the
  query, not objective truth; disclosed as a known limitation.
- Stance rubric scope (noted 2026-07-12, BEFORE the batch judge run). The
  context stance labels supports_side_a / supports_side_b require only that a
  paper's MAIN position clearly aligns with one side via a core claim,
  mechanism, theoretical argument, or methodological position. They do NOT
  require the paper to empirically establish the full "most / majority" claim in
  Side A / Side B. Consequence: a methodological stance (e.g. "treat RNA of
  unknown function as junk by default") and an empirical majority result are
  both counted as supports for the same side; the rubric does not distinguish
  their evidential strength, and no stance_strength dimension is recorded. This
  keeps one consistent operational definition across all 50 queries, but it
  means "supports" denotes directional alignment, not proven majority. Disclosed
  as a known limitation. Decision made after a development-stage sanity check of
  q101 (not a substitute for the pre-registered 5-query red-flag review).
- LLM judge has its own biases; fixed prompt + temperature 0 + small manual
  red-flag check + optional cross-model check are the mitigations, not proof.
- Preview judge model may drift; exact ID + date + prompt version recorded.
- Dev-stage targeted sanity check of the single eligible retention==0 query
  (q133), recorded 2026-07-12 AFTER the batch judge run. NOT part of the
  pre-registered pipeline and NOT a substitute for the pre-registered 5-query
  red-flag review; it did not change the 36-query retention result or the
  bootstrap CI. Context: q133 asks whether cellular decision-making is governed
  more by network topology (Side A) or reaction kinetics (Side B). The generated
  answer cited papers from BOTH sides, but it reframed the two supports_side_b
  papers ([7] 0811.2834 and [10] 1104.2845) to argue FOR Side A (e.g. it
  used a bistability-depends-on-rate-constants result as evidence that function
  is rooted in network structure). The answer judge labelled it
  side_a_only_or_token_b (retention=0), consistent with its own evidence string
  and with the retention definition: citing a paper is not the same as retaining
  its viewpoint, and a paper repurposed to argue the opposite side is not a
  substantive representation of that side. Judged reasonable, not a bug; the result was NOT
  hand-edited to 1. Two takeaways: (a) this query illustrates why retention is
  defined on substantive viewpoint representation, not citation presence, which
  is the intended strength of the metric; (b) because this is a self-judge
  (flash-lite judging flash-lite output), the direction here is against
  self-preference: a purely self-protective judge would more likely have labelled
  this both_sides_retained, so the judge did not merely rubber-stamp its own
  answer here. This is a single-query observation and is not generalized.

## Notebook plan (12 cells)

Cell 0 setup (install google-genai, imports, rglob path auto-detect, load key).
Cell 1 load + assertions (contradictory==50, q101-150, 500 ids in corpus),
       load sides_q101_150.json and assert 50 reviewed==true records.
Cell 2 build_context (verbatim from A).
Cell 3 generate_answer + PROMPT_TEMPLATE (verbatim from A) + parse_citations.
Cell 4 judge probe: prove primary callable + quota >=~130; else fallback.
Cell 5 context stance judge function (batched 10 abstracts, JSON out).
Cell 6 answer two-layer judge function (retention_status + conclusion_favor).
Cell 7 batch generation over q101-150 (checkpoint/resume, 429/503 backoff).
Cell 8 batch judge: context then answer (checkpoint/resume).
Cell 9 eligibility + retention (Layer 1 only) + favor distribution (Layer 2).
Cell 10 query-level bootstrap CI (seed 42, eligible pool).
Cell 11 save outputs + figure + report line; then manual-check CSV + optional
        cross-model check.

Notebook filename: step7-rq2-frameworkB-dissent-yb.ipynb
