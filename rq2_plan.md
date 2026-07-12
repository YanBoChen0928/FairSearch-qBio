# RQ2 Plan v2 (revised, authoritative)

Owner: Yan-Bo. Step 7 (generation) + RQ2 analysis. Run on Kaggle
(same pattern as 5b), then results feed Step 8 (quality) and Step 9 (demo).

This v2 block supersedes the v1 plan preserved below. Where they disagree,
v2 wins. v1 is kept only for traceability.

## What changed from v1 (six corrections)

1. A and B reuse the same PIPELINE (build_context -> generate -> parse
   functions and prompt skeleton), NOT the same generation call. A runs on
   neutral q001-q100; B runs on contradictory q101-q150; the two query sets do
   not overlap, so no generation call can literally be shared. v1's phrase
   "A's generation call is reused by B" was inaccurate and is corrected here.
2. Query count is 150, not 50 (neutral q001-q100 for A, contradictory
   q101-q150 for B). Cell 1 hard-asserts len(retrieval_results)==150 and
   neutral==100.
3. Elite shares EXCLUDE unknown labels. Only papers with coverage=="found"
   (having an elite_label) enter the denominator; no_affiliation / not_found
   are dropped, never counted as 0. Same "labeled slots only" rule as RQ1.
4. Unique citations vs citation frequency are distinguished explicitly
   (see Decision 1 below).
5. Framework B's metric is fixed in advance (see Decision 2 below).
6. RAGAS is moved out of RQ2 code and attached to Step 8 (see Decision 3).

## Decisions (confirmed, pre-registered)

Decision 1 - Framework A headline metric = UNIQUE cited-paper set.
The headline amplification metric uses the unique set of cited papers, giving
a symmetric comparison against the retrieved context (which is 10 unique
papers): context_elite_share (elite fraction of the up-to-10 labeled context
papers) vs cited_elite_share (elite fraction of the unique labeled papers the
answer actually cites). Frequency-weighted citation share is ALSO saved and
reported as a SECONDARY metric (it captures repeated reliance on elite papers
after selection) but is not the headline, because it is more sensitive to
answer length, repeated-citation style, and formatting noise.

Frequency positioning (anti-metric-switching rule, pre-registered). Frequency
is near-zero extra cost: both metrics come from the same parsed markers (unique
= deduped, frequency = not deduped). Unique stays the official headline; it is
never replaced by frequency. Interpretation is fixed IN ADVANCE by case:
(a) unique shows no clear amplification but frequency shows a pattern -> report
carefully as a secondary diagnostic ("no clear elite amplification in source
selection, but possible repeated reliance on elite papers once selected");
(b) both point the same way -> frequency strengthens the interpretation;
(c) frequency is noisy/inconsistent -> keep it in the per-query table or
appendix only. This rule exists so frequency can never be swapped in as the
primary result after seeing the numbers.

Decision 2 - Framework B headline metric = dissent retention rate (binary).
Eligibility: a query is eligible only if at least one retrieved top-10 context
paper is judged "dissenting". Among eligible queries, the answer counts as
retaining dissent if it is judged "balanced" or "dissenting-leaning". Each
eligible query is compressed to 0/1; the rate = retained / eligible. This
measures whether dissent is retained AT ALL, not HOW MUCH dissent is retained.
No separate dissent-quantity metric is added to the main analysis (it would
make B too large); answer stance distribution may still be reported
descriptively, not as a pre-registered metric.

Decision 2b - Framework B baseline prompt must NOT force balancing.
The B baseline generation prompt stays evidence-grounded (answer using ONLY
the given 10 papers, mark each claim with [n]) but does NOT explicitly instruct
the model to present multiple perspectives or balance viewpoints. Forcing
balance in the baseline would pre-apply the mitigation and destroy the
comparison. Perspective-balanced prompting is an RQ3 intervention, tested
AGAINST this baseline. Consequence: A and B share the SAME generation prompt
skeleton (evidence-grounded + [n], no balancing); they differ only in which
query set is fed. This keeps generation conditions identical across A and B.

Decision 3 - RAGAS is not part of RQ2 code.
RQ2 generates answers and measures bias-related outcomes only (A: institutional
citation amplification; B: dissent retention). RAGAS evaluates answer quality
(faithfulness, answer relevancy, context precision), which belongs to Step 8
alongside NDCG@10 / MRR. RQ2 outputs are saved in a Step-8-reusable schema
(query_id, query_text, retrieved context, paper_ids, generated_answer, parsed
citations, citation status) so Step 8 does not re-run generation.

Decision 4 - Models (updated 2026-07-11; supersedes all earlier model choices).

Model selection was forced to change several times by Google's deprecation
schedule during setup. Recorded in full for reproducibility and the report:
- Original plan: Gemini 1.5 Flash (gen) + 1.5 Pro (judge).
- 1.5 series: removed. "gemini-1.5-flash" -> 404 NOT_FOUND; not in the model
  list for our key.
- gemini-2.0-flash / -flash-001: shut down (Google lists 2026-06-01). Calling
  it returned 429 with "limit: 0" for the free tier (zero quota, i.e. not
  usable), not a temporary rate-limit.
- gemini-2.5-flash: listed by client.models.list() but NOT callable by our
  (new) project: the call returned "This model models/gemini-2.5-flash is no
  longer available to new users." KEY LESSON: appearing in models.list() does
  NOT mean the project may call it; only an actual generateContent call proves
  availability.
- gemini-3.5-flash: callable, but this project's free-tier DAILY quota for it
  was only 20 requests (429 with quotaId GenerateRequestsPerDayPerProjectPerModel,
  quotaValue 20). 20/day cannot finish A's 100 queries (let alone B). Not the
  RPM limit, the per-DAY limit. Enabling billing was rejected (course project).
- FINAL, ACTUALLY USED: gemini-3.1-flash-lite. A flash-lite model has a much
  higher free daily quota (order of 1000/day) and wider RPM, and the task
  (read 10 abstracts, write an answer with [n]) is well within its capability.
  Ran all 100 neutral queries with 0 failures, SLEEP=5.

Final choices:
- A generation + B baseline generation: gemini-3.1-flash-lite. SAME model for both,
  matching Decision 2b (A and B share one generation prompt skeleton, so they
  must share the model, or generation conditions would differ, confounding
  framework effects with model-capability effects). No pinned "-NNN" snapshot
  exists for it; we accept that (2.0-flash-001, the one pinned option, is
  dead). We avoid "-latest" and "-preview" aliases because those drift and
  hurt reproducibility.
- B judge: a stronger current model, decided when B starts. gemini-2.5-pro is
  not available to new projects (same "new users" restriction likely applies);
  the current stable Pro-tier option to check at that time is
  gemini-3.1-pro-preview (note: preview, so weaker reproducibility). Pick the
  strongest STABLE model callable by the project when B begins; do not assume a
  name from the list is callable until a real call succeeds.
- Temperature fixed at 0 for all calls. Key in Kaggle Secrets, label
  GEMINI_API_KEY. The new key format is NOT "AIza..."-prefixed, so code must
  not assert that prefix; only check the key is non-empty and stripped.

Known risk still open: if gemini-3.5-flash also returns 429 "limit: 0", the
problem is the PROJECT having no free-tier quota (not the model name). Fix by
creating a key in a fresh clean project, not by enabling billing (a course
project should not need paid tier).

Report note: state plainly that 1.5/2.0/2.5 were planned or attempted but were
unavailable at run time, and that gemini-3.5-flash was used. Never silently
swap models; record the actual model ID used.

Robustness across models (OPTIONAL, not main line). Re-running the whole audit
on a second model to check whether any amplification is model-specific is a
nice-to-have, NOT required to answer RQ2 (a single model answers "does
generation amplify institutional bias"). It roughly doubles the work (two
generation passes, two parses, two metric sets, a comparison). Defer it to
future work; only consider it IF the main run actually finds amplification
(no effect -> nothing to test for robustness) AND time remains. If done, name
it "model robustness check" with an explicit second model ID; do NOT call it
"Framework B" (that name is already the dissent/viewpoint framework and the two
must not be confused).

Decision 5 - The processed corpus dataset must be added to the notebook.
retrieval_results.json has NO title/abstract (only paper_id), so the prompt
context is built by joining paper_ids to data/processed/qbio_papers.json
(Kaggle: fairsearch-qbio-processed-Raj-Jici-YB). Verified locally: all 1000
neutral slots (953 unique ids) resolve in the corpus with 0 misses.

## Aggregation, CI, and how empty/invalid cases are handled

Both frameworks aggregate at the QUERY level (not paper level, because
citations within a query are correlated). CIs use query-level bootstrap
resampling with random_seed=42, same method as Step 5b.

Empty-denominator rule (Framework A). amplification = cited_elite_share -
context_elite_share is undefined if a query has no labeled context papers
(coverage=="found") OR no labeled cited papers. In that case its amplification
is set to null and the query is EXCLUDED from aggregate statistics. Never fill
0 (that would falsely assert "no amplification"). The count of excluded queries
is reported.

Frequency secondary metric (Framework A). Only valid citation markers [1]-[10]
that map to papers with coverage=="found" are counted. Invalid markers (out of
range, e.g. [0] or [13], or unparseable) and unknown-label papers are excluded
from the denominator. Invalid-marker counts are reported SEPARATELY (they also
serve as a parsing-health signal that cross-checks the manual sanity check).

Non-evaluable queries are excluded BEFORE resampling, not during. For A, the
resampling pool is the set of queries with a defined amplification. For B, the
resampling pool is the set of ELIGIBLE queries (at least one dissenting context
paper). Each pool's excluded count is reported alongside the CI.

## Citation-provenance limitation (must appear in the report)

Because current LLMs do not expose true token-level provenance, this analysis
does NOT claim to identify the actual source of every generated token. Each
retrieved paper is assigned a source number [1]-[10], and the model is
instructed to cite the supporting source number after each scientific claim.
We parse these markers back to paper_ids and institution labels. RQ2-A
therefore measures cited-source ATTRIBUTION BEHAVIOR under a controlled RAG
prompt (which papers the model chooses to cite as evidence), not true
token-level source tracing. Given 150 queries, exhaustive claim-level manual
verification is not feasible; the main analysis relies on automatic citation
parsing (A) and fixed LLM-judge labels (B), with a small manual sanity check.

## Manual sanity check (pre-registered)

Roles are asymmetric on purpose. A's check is the MORE IMPORTANT one: it
directly verifies the citation-parsing pipeline (a main pipeline). B's check
is a LIGHTWEIGHT RED-FLAG check only, NOT judge validation: 5 samples cannot
statistically validate an LLM judge, so we do not frame it that way. Its only
goal is to catch a judge that is broadly broken. Do not expand B's check into a
separate validation task (that would need large samples, statistics, and
inter-annotator agreement, which is out of scope). No long annotation, no
manual correction of metrics in either check.

Scope: NOT a full validation. Using random_seed=42, sample 5 Framework A
queries and 5 Framework B queries. A's check assesses citation faithfulness
(do the [n] markers generally point to context papers that support the cited
claims?), labeled citation_faithfulness in {ok, partial, not_ok, unclear}.
B's check assesses whether the judge's stance labels are broadly reasonable,
labeled context_stance_label_reasonable and answer_stance_label_reasonable,
each in {ok, partial, not_ok, unclear}. (partial = pipeline partly worked;
unclear = human cannot judge, a limit of the checker, not a pipeline failure.)

Data flow (human labels never touch the main metrics):

    RQ2 auto pipeline
        -> /kaggle/working/rq2_generation_raw.json   (clean, never hand-edited)
        -> sample 5 A + 5 B (seed 42)
        -> /kaggle/working/rq2_manual_check_todo.csv  (only check columns blank)
        -> human fills the check columns in the CSV
        -> program merges CSV back
        -> /kaggle/working/rq2_generation_raw_checked.json

The CSV carries only human EVALUATION labels, never metric values. Main metrics
(amplification, dissent retention) are always computed from the automatic
result files (rq2_frameworkA_result.json / rq2_frameworkB_result.json), never
recomputed from the _checked.json. The two data lines never cross, so neither
can contaminate the other. The _checked.json is used only for the report's
limitation section.

Systematic failure (qualitative, no fixed numeric threshold, because the check
is intentionally small): indicated if multiple sampled queries show not_ok, or
if the same TYPE of error recurs across sampled queries, e.g. citation numbers
consistently misaligned with the source mapping, citation markers frequently
pointing to unsupported papers, or judge stance labels repeatedly contradicting
the abstract/answer content. A single isolated error is treated as an expected
limitation of LLM-based citation/judging. Repeated same-type errors trigger a
prompt / parser / judge-prompt revision followed by RERUNNING the affected
pipeline. We never manually correct individual sampled results and treat them
as final metrics.

## Framework A - MEASURED RESULT (completed 2026-07-12)

Model: gemini-3.1-flash-lite, temperature 0. 100 neutral queries generated,
0 failures, 0 invalid citation markers, 0 zero-citation queries. 99 queries
used; 1 excluded by the empty-denominator rule (set null, not 0).

Headline (unique cited-paper set):
- mean amplification (cited_elite_share - context_elite_share) = +0.0041
- median amplification = 0.0000
- query-level bootstrap 95% CI (seed 42, 10,000 draws) = [-0.0254, +0.0342]
- CI crosses zero -> NOT statistically significant
- direction: 31 amplifying, 17 reducing, 51 unchanged
- cited elite share 0.191 vs context elite share 0.187 (essentially equal)

Conclusion: this is the NEUTRAL pre-registered outcome. No confirmed elite
citation amplification at the generation stage. Consistent with RQ1 (weak,
not significant) and the PCA topic-not-institution finding.

Output files (Kaggle /kaggle/working, also backed up locally):
rq2_gen_checkpoint.jsonl (raw), rq2_frameworkA_per_query.json,
rq2_frameworkA_result.json, rq2_frameworkA_scatter.png.

Caveats for report: "not significant" != proven zero; result is specific to
gemini-3.1-flash-lite (model switch disclosed); measures cited-source
attribution under a controlled RAG prompt, not token-level provenance; the
54.3% figure from other sources is not comparable.

## Research-question chain (final framing)

- RQ1: retrieval-stage institutional bias (done; weak, not significant).
- RQ2-main (Framework A): generation-stage institutional citation
  amplification (cited vs context).
- RQ2-extension (Framework B): generation-stage viewpoint flattening
  (dissent retention).
- RQ3: mitigation (MMR / balanced prompt) and utility tradeoff; Step 8 uses
  RAGAS / NDCG / MRR for quality.

---

# ============================================================
# DEPRECATED: DO NOT IMPLEMENT FROM THIS SECTION
# The authoritative plan is the v2 block ABOVE. Everything below
# is the old v1 draft, kept only for traceability. It contains at
# least one known-wrong statement (see inline WRONG markers).
# ============================================================

# RQ2 Plan v1 (superseded, kept for traceability)

Owner: Yan-Bo. Step 7 (generation) + RQ2 analysis. Run on Kaggle
(same pattern as 5b), then results feed Step 9 dashboard.

## Core question (one line)

RQ1 measured bias at the RETRIEVAL stage (result: weak, not significant).
RQ2 asks whether the GENERATION stage (the LLM) adds or amplifies bias that
retrieval alone did not show. Two complementary lenses, below.

## Why two frameworks

Our proposal's original hypothesis was a "rich-get-richer" loop: the LLM
treats a skewed retrieved context as consensus and amplifies it. That is
Framework A (institutional lens). Later we added 50 contradictory queries,
which enable Framework B (viewpoint lens). Both measure "bias added at
generation", from two angles:

- Framework A = does the LLM cite ELITE institutions more than it was given?
- Framework B = does the LLM favor MAINSTREAM consensus over dissenting views?

They do not conflict; A is about who (institution), B is about what (stance).

## The two frameworks at a glance

```
RQ2 = check whether the GENERATION stage adds bias. Two lenses:

                  same query's top-10 papers fed to the LLM
                                   |
             +---------------------+---------------------+
             |                                           |
      Framework A (institution)                Framework B (viewpoint)
      neutral queries q1-100                   contradictory queries q101-150
             |                                           |
      Q: does the LLM cite elite               Q: does the LLM favor the
         institutions more?                       mainstream and drop dissent?
             |                                           |
      compare: cited elite %                   compare: answer stance
               vs context elite %                       vs context stance mix
             |                                           |
      how: paper numbers [n]                   how: LLM-as-a-judge labels
           + look up elite label                    each paper / the answer
             |                                           |
      result > 0 = amplifies                   result = dissent dropped
               institutional bias                       = viewpoint flattened
             +---------------------+---------------------+
                                   |
                    both measure "bias added at generation"
                    A = who is cited, B = what is said
```

---

## Framework A - Institutional citation bias (MAIN)

**Query set:** neutral (q001-q100).

**Method:**
1. For each query, take its top-10 papers from retrieval_results.json.
2. Number them [1]..[10]; each number maps to a known paper_id.
3. Prompt the LLM to answer using ONLY these papers, and to mark every claim
   with the source number(s) it used, e.g. "... as shown in [3], [7]".
4. Parse the [n] markers back to paper_ids (pure code, no manual labeling).
5. Look up each cited paper's elite label in retrieval_labels.json (reused
   from RQ1).
6. Compare two shares:
   - context_elite_share  = elite fraction of the 10 papers given (per query)
   - cited_elite_share    = elite fraction of the papers actually cited

**Metric:** citation amplification = cited_elite_share - context_elite_share.
- > 0  -> generation amplifies elite bias (the "rich-get-richer" effect)
- ~ 0  -> generation is neutral (passes through what retrieval gave it)
- < 0  -> generation under-cites elite

Aggregate across queries; report with a bootstrap CI (resample queries, same
logic as 5b) because per-query citations are correlated.

**What we do NOT assume:** the old 54.3% figure is from another team's report
(different elite definition, baseline 58%). Our number will differ. Report
whatever we measure.

**Honest expectation:** RQ1 showed retrieval is nearly fair on our QS-Top-50
definition (baseline 14.4%). If A shows cited >> context, bias is added by the
LLM (a clean, strong finding). If A shows cited ~ context, the LLM is neutral
(also a valid finding). Either way, do not inflate.

---

## Framework B - Consensus vs dissent bias (EXTENSION)

**Query set:** contradictory (q101-q150). These are genuine two-sided debate
questions (e.g. "Is most non-coding DNA functional, or largely junk?").
Their `relevance` field is null by design (no subcategory proxy); stance must
be judged by an LLM.

**Method (LLM-as-a-judge, two stages):**
1. Stance-label the CONTEXT: for each retrieved paper, an LLM judge classifies
   its abstract as pro-consensus / dissenting / neutral on that query's debate.
   This gives the stance mix of what the LLM was given.
2. Generate the answer from the top-10 (same generation call as A, reused).
3. Stance-label the ANSWER: judge whether the generated answer leans
   consensus, balanced, or dissenting.
4. Compare: does the answer suppress dissent relative to the context? e.g. if
   context is 50/50 but the answer only reflects the consensus side, the LLM
   is collapsing viewpoint diversity.

**Metric ideas:**
- pro-consensus vs dissenting token/claim ratio in the answer
- answer stance vs context stance distribution (does dissent get dropped?)

**Independence from RQ1:** Framework B does NOT depend on institutional bias.
Even if institutions are perfectly fair, the LLM can still flatten dissent.
So B stands on its own regardless of RQ1's null result.

**Caveat:** LLM-as-a-judge is itself a model with its own biases; disclose
this. Use a fixed judge prompt and temperature; consider spot-checking a few
by hand for sanity.

---

## Mapping to pipeline steps

| Framework | Step | Query set | Labels used | Judge needed? |
|-----------|------|-----------|-------------|---------------|
| A (institution) | 7 (generation) | neutral q001-100 | retrieval_labels.json (RQ1) | no (parse [n]) |
| B (viewpoint)   | 7 (generation) | contradictory q101-150 | none (stance by LLM) | yes (LLM judge) |

Both share ONE generation pass over the top-10 contexts; A and B differ in
which queries and which post-analysis.
<!-- WRONG (v1): A and B do NOT share one generation pass. A = neutral
q001-100, B = contradictory q101-150; disjoint query sets. They reuse the
same PIPELINE/prompt skeleton, run separately. See v2 Correction 1 above. -->

## Expected outputs (deliverables)

Files (Kaggle notebook output, then reused by Step 9 and the report):
- `rq2_generation_raw.json` - per query: the prompt, the LLM answer, parsed
  citation numbers -> paper_ids (for A), stance labels (for B).
- `rq2_frameworkA_result.json` - context_elite_share, cited_elite_share,
  amplification, bootstrap CI, per-query table.
- `rq2_frameworkB_result.json` - context stance mix, answer stance,
  consensus-vs-dissent metric, per-query table.
- one figure per framework (bar/scatter), neutral colors, honest framing.

Report-ready one-liners (to be filled with REAL numbers after the run):
- A: "The LLM cited elite papers at X% vs a context share of Y%
  (amplification +Z, CI [...]) -> [amplifies / neutral]."
- B: "Across 50 debate queries, the answer reflected the dissenting side in
  X% of cases where dissent was present in context -> [suppresses / balanced]."

## Relation to RQ3

- RQ3 (Jici, Step 6, MMR re-ranking) changes WHICH papers reach the LLM.
- If Framework A finds the LLM amplifies elite citation, then RQ3's fairer
  context could reduce downstream citation bias too -> a nice A x RQ3 link
  (re-run A on the MMR-reranked contexts and compare).
- Framework B connects to RQ3's perspective-balanced prompt (Step 7 mitigation):
  if B finds dissent suppression, the balanced prompt is the intervention to
  test against it.
- Because RQ1 bias is small, the RQ3 story is "behavior under a low-bias start"
  (can MMR nudge without hurting utility / does it over-correct?), not
  "removing a large bias". RQ2 gives RQ3 a second place to look for effects
  (generation), even if retrieval-stage room is small.

## Expected outcomes and how to read them (pre-registered)

We write down what each result would mean BEFORE running, so we do not chase a
"significant" result or massage numbers afterward. Every outcome below is a
valid, reportable finding. Significance does NOT decide whether we do RQ3;
RQ2 and RQ3 are both committed deliverables regardless of results.

### Framework A - two outcomes

- If cited_elite_share >> context_elite_share (amplification clearly > 0,
  CI excludes 0): the LLM adds institutional bias at generation. This is the
  strongest version of our proposal's "rich-get-richer" hypothesis, and it is
  especially clean given RQ1 showed retrieval is nearly fair -> the bias is
  located at the LLM, not retrieval.
- If cited_elite_share ~ context_elite_share (amplification ~ 0, CI crosses 0):
  the LLM passes through what it was given; it does not add institutional bias.
  Combined with a near-fair RQ1, the honest conclusion is "this pipeline shows
  little institutional bias at either stage on a QS-Top-50 definition" -
  consistent with prior work (Avery et al.) and still a real finding.

### Framework B - two outcomes

- If the answer drops the dissenting side when it was present in context: the
  LLM flattens viewpoint diversity (consensus prioritization). This motivates
  the perspective-balanced prompt as the RQ3/Step-7 intervention.
- If the answer reflects both sides roughly in proportion to the context: the
  LLM preserves dissent; no consensus bias at synthesis. Also a valid finding
  (matches the "no systematic consensus prioritization" result some prior
  teams reported).

### Why "not significant" is not failure

RQ1 was not significant, and that was a clean result. The same applies here:
our contribution is a transparent, correctly-measured audit, not a large
number. Do not substitute the other team's 54.3% or any expected figure.

## Decisions (confirmed)

1. Generation model: Gemini 1.5 Flash, run on Kaggle (free tier is enough for
   100-150 queries; key stored in Kaggle Secrets, same pattern as OpenAlex).
2. Do BOTH A and B (they use up all 150 queries: A = neutral q1-100,
   B = contradictory q101-150, nothing wasted). Order: A first, then B.
   A's generation call is reused by B, so A first is the least-effort path.
3. Judge model (for B only): prefer Gemini 1.5 Pro (stronger than Flash,
   same API key, avoids "judging itself"). Fallback: Flash judging Flash,
   disclosed as a limitation. Decide when B starts; A does not need a judge.
4. Query facts verified: q1-100 are neutral (informational), q101-150 are
   genuine two-sided debates. Framework A uses ONLY neutral to avoid
   confounding institution bias with stance bias.
