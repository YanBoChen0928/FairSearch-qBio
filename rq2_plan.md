# RQ2 Plan: Does the generation stage amplify bias?

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
