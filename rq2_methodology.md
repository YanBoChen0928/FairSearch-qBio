# RQ2 Methodology: Generative Faithfulness

**Research question:** Does the LLM generation stage add or amplify bias that
retrieval alone (RQ1) did not show? Two complementary lenses are used.

**Source docs:** `rq2_plan.md` (v2, authoritative), `rq2_frameworkA_summary.md`,
`rq2_frameworkB_summary.md`, `rq2_frameworkb_draft.md`
**Result files:** `rq2_frameworkA_result.json`, `rq2_frameworkB_result.json`
**Owner:** Yan-Bo

---

## 1. Goal and the two-framework design

RQ1 measured bias at the **retrieval** stage (result: weak, not significant).
RQ2 asks whether the **generation** stage (the LLM) adds bias that retrieval
alone did not show, using two independent lenses on the same underlying
pipeline (10 retrieved papers fed to an LLM):

- **Framework A (institution / "who is cited")** — neutral queries
  (q001–q100). Does the LLM cite elite-institution papers more than it was
  given in context?
- **Framework B (viewpoint / "what is said")** — contradictory queries
  (q101–q150). On genuine two-sided debate questions, does the generated
  answer keep both sides that were present in the context, or flatten them
  into one?

A and B use the **same generation prompt skeleton** (evidence-grounded,
mark each claim with a source number, no balancing instruction) but are run
on disjoint, non-overlapping query sets, so no single generation call is
literally shared between them — they reuse the *pipeline*, not a *call*.
This split exists so each framework isolates one axis (institution vs.
viewpoint) cleanly, without one confounding the other.

RAGAS (answer quality: faithfulness, relevancy, context precision) is
deliberately **out of scope for RQ2** — it belongs to Step 8 alongside
NDCG@10/MRR. RQ2 measures only bias-related outcomes.

---

## 2. Framework A: institutional citation amplification

### 2.1 Method

1. For each of the 100 neutral queries, take its top-10 retrieved papers.
2. Number them [1]..[10] in retrieval rank order; keep a number → paper_id map.
3. Prompt the model to answer using ONLY these papers, marking each claim with
   its source number(s), e.g. "...as shown in [3], [7]". No balancing
   instruction (balancing is an RQ3 intervention, not baseline behavior).
4. Parse the [n] markers back to paper_ids (pure code, no manual labeling).
5. Look up each cited paper's elite label (reusing `retrieval_labels.json`
   from RQ1, QS Top-50 2026); only `coverage=="found"` papers count.
6. Per query, compute:
   - `context_elite_share` = elite fraction of the ~10 labeled context papers
   - `cited_elite_share` = elite fraction of the **unique** labeled cited papers
   - `amplification = cited_elite_share - context_elite_share`

**Headline metric = unique cited-paper set**, chosen for symmetry with the
~10 unique context papers. A frequency-weighted variant (citations counted
with repetition) is saved as a **secondary** diagnostic only — pre-registered
never to replace the headline, with a fixed interpretation rule set in
advance for how to read the two if they disagree (see `rq2_plan.md` Decision 1).

**Empty-denominator rule:** if a query has no labeled context papers or no
labeled cited papers, its amplification is set to `null` and the query is
**excluded** from aggregation — never filled with 0 (which would falsely
assert "no amplification").

Aggregated at the **query level** (not paper level, since citations within a
query are correlated), with a query-level bootstrap 95% CI (seed 42, 10,000
resamples) — same reasoning as RQ1 §5.

### 2.2 Measured result

| Metric | Value |
|---|---|
| Queries generated / failures | 100 / 0 |
| Queries used (empty-denominator excluded) | 99 (1 excluded) |
| **Mean amplification** | **+0.0041** |
| Median amplification | 0.0000 |
| Bootstrap 95% CI | **[-0.0254, +0.0342]** — crosses 0 |
| Cited elite share | 0.191 |
| Context elite share | 0.187 |
| Direction (amplifying / reducing / unchanged) | 31 / 17 / 51 |

**Conclusion:** the neutral, pre-registered outcome — no confirmed elite
citation amplification at generation. Cited share (0.191) essentially matches
context share (0.187); amplifying and reducing queries roughly offset. This
mirrors RQ1 (weak, non-significant retrieval-stage tilt) and the separate PCA
finding that the embedding encodes topic, not institution.

---

## 3. Framework B: viewpoint-diversity retention

### 3.1 Reframing before the judge run (pre-registered amendment)

The original plan called this "dissent retention" (consensus vs. dissent).
Before any judge call was made, it was renamed to **viewpoint-diversity
retention (Side A vs. Side B)**, because q101–q150 mostly encode two
contrasting but non-hierarchical positions (complementary mechanisms or open
alternative theories — e.g. neutral drift vs. selection — not a stable
consensus/dissent split). Forcing a consensus/dissent label would have
injected more researcher subjectivity than the symmetric Side A/B framing.

A frozen sidecar file (`queries/sides_q101_150.json`) maps each contradictory
query to its two stated positions, restating only what the query text already
contains (no added evidence or value judgment). The original query text is
unchanged; only this annotation file is new.

### 3.2 Method

1. **Generation** (baseline, no balancing instruction): same model, prompt
   skeleton, and citation-marking approach as Framework A, run on the 50
   contradictory queries. 50/50 generated, 0 failures.
2. **Context stance judge** (one LLM call per query, judges all 10 retrieved
   abstracts together): labels each paper `supports_side_a` /
   `supports_side_b` / `mixed_or_neutral`. Tie-break: when unsure, label
   `mixed_or_neutral` (never guess a side) — this reduces false-positive
   eligibility.
3. **Eligibility:** a query is eligible only if its context has **at least
   one** `supports_side_a` AND **at least one** `supports_side_b` paper.
4. **Answer judge** (one LLM call per query, two independent layers):
   - **Layer 1 — `retention_status`** (sole input to the headline metric):
     `both_sides_retained` / `side_a_only_or_token_b` /
     `side_b_only_or_token_a` / `neither_or_unclear`.
   - **Layer 2 — `conclusion_favor`** (descriptive only, never in the
     metric): `favors_side_a` / `favors_side_b` / `no_clear_favor`.
     Frequency or length alone never determines favor — an explicit
     evaluative/comparative statement is required.
5. **Retention** (binary, per eligible query): `retention = 1` iff
   `retention_status == both_sides_retained`; `0` for the other three
   statuses; `null` (excluded) for non-eligible queries.
6. Aggregate at query level; bootstrap 95% CI (resample eligible queries,
   seed 42, 10,000 draws).

### 3.3 Measured result

| Metric | Value |
|---|---|
| Total contradictory queries | 50 |
| Eligible (context has both sides) | 36 |
| Excluded (one side only / neither) | 14 |
| Retained (`both_sides_retained`) among eligible | 35 |
| **Retention rate** | **35/36 = 97.2%** |
| Bootstrap 95% CI | **[91.7%, 100.0%]** |

`conclusion_favor` distribution (descriptive only, eligible 36): favors_side_a
3, favors_side_b 3, no_clear_favor 30.

**How to read this:** the rate is high and the CI stays above 0.90, but **no
preservation threshold was pre-registered** and the judge is a **self-judge**
(see §3.4). This is reported as a descriptive measurement, not a formal
verdict that the model "preserves" viewpoint diversity.

### 3.4 Judge model fallback (self-judge disclosure)

The primary judge, `gemini-3-flash-preview`, passed an initial single-call
probe but hit a **429 quota error at q115** during the batch context-judge
run: `quotaId GenerateRequestsPerDayPerProjectPerModel-FreeTier, quotaValue
20` — this project's free tier allows only 20 preview requests/day, far short
of the ~100 judge calls needed.

**Fallback (pre-registered route):** `gemini-3.1-flash-lite` — the same model
used for generation — was used for the **entire** judge stage. This makes the
answer judge a **self-judge** (judge model == generation model). The 14
context-judge records already produced by the preview model before the 429
were **deleted** before the flash-lite rerun, so no query is judged by a mix
of two models.

### 3.5 Manual red-flag check (pre-registered, lightweight — not judge validation)

5 queries sampled (seed 42, from all 50): q102, q108, q118, q141, q148. This
is explicitly **not** a statistical validation (n=5 cannot validate an LLM
judge) — its only goal is to catch a broadly broken judge.

Results:
- `context_stance_label_reasonable`: 3/5 ok, 2/5 partial (q118, q148 — did
  not affect eligibility conclusions)
- `answer_retention_reasonable`: 4/5 ok, 1/5 **not_ok** (q141)
- `answer_favor_reasonable`: 3/5 ok, 2/5 **not_ok** (q118, q141)

**q141 finding:** the judge over-credited balance — an answer that
overwhelmingly supported one side with only a token acknowledgment of the
other was labeled `both_sides_retained`. This error direction (crediting the
judge's own generation model's output as more balanced than it is) is
consistent with the known self-judge risk.

**q118 finding:** the judge under-detected favor — the answer's opening claim
gave one side clear explanatory primacy but was labeled `no_clear_favor`.

**Decision:** these two answer-layer errors are of **different types** (one
over-credits retention, one under-detects favor), not the same rule repeated.
Per the pre-registered qualitative standard (systematic failure = multiple
*same-type* errors), this was judged **not** to require a prompt revision or
rerun — it is instead recorded as a disclosed limitation.

### 3.6 Development-stage sanity check (q133, not pre-registered)

The single eligible query with `retention=0` was manually inspected. The
generated answer cited papers from both sides but reframed the two
Side-B-supporting papers to argue *for* Side A. Judged reasonable, not a bug:
citing a paper is not the same as retaining its viewpoint. Notably, being a
self-judge, the direction here is *against* self-preference — a purely
self-protective judge would more likely have labeled this
`both_sides_retained`.

---

## 4. Model selection history (both frameworks; report transparently)

The original plan specified Gemini 1.5 Flash. Google's deprecation schedule
forced several changes during setup, all disclosed rather than silently
swapped:

| Model attempted | Outcome |
|---|---|
| gemini-1.5-flash | 404 NOT_FOUND — removed, not in model list |
| gemini-2.0-flash / -flash-001 | Shut down; free tier returned 429 "limit: 0" |
| gemini-2.5-flash | Listed by `models.list()` but call failed: "no longer available to new users" |
| gemini-3.5-flash | Callable, but free-tier **daily** quota = 20 requests — cannot finish 100+ queries |
| **gemini-3.1-flash-lite (final)** | Higher daily quota, wide RPM; ran all queries with 0 failures |

**Key lesson (recorded for reproducibility):** appearing in
`client.models.list()` does **not** mean a project can call a model — only an
actual `generateContent` call proves availability and quota.

Temperature fixed at 0 for all generation and judge calls. Both Framework A
generation and Framework B baseline generation use gemini-3.1-flash-lite,
satisfying the requirement that A and B share one generation model (so
framework differences aren't confounded with model-capability differences).

---

## 5. Aggregation and empty-case handling (shared convention)

Both frameworks:
- Aggregate at the **query level**, never the paper level (citations within
  a query are correlated).
- Use **query-level bootstrap** (not per-paper), seed 42, 10,000 resamples —
  same reasoning as RQ1's bootstrap-over-binomial choice.
- Exclude non-evaluable queries **before** resampling (not during), and
  report the excluded count alongside the CI.
- Never fill an undefined ratio with 0 — always `null` + exclude.

---

## 6. Key limitations (for the report)

1. **Framework A:** measures cited-source *attribution behavior* under a
   controlled RAG prompt (which papers the model chooses to cite), not true
   token-level provenance, which current LLMs do not expose.
2. **Framework A:** results are specific to gemini-3.1-flash-lite; a
   different generator could behave differently (disclosed model-switch
   limitation, not a design choice).
3. **Framework B:** the answer judge is a **self-judge** (same model as
   generation) due to a quota-forced fallback — a known potential bias
   direction, not a corrected estimate. Given the q141 red-flag finding, the
   true retention rate could plausibly be somewhat lower under an independent
   judge.
4. **Framework B:** small eligible n (36) with an extreme proportion (35/36)
   — the CI upper bound touching 1.000 is a small-sample artifact; the entire
   lower bound rests on the single q133 case.
5. **Framework B:** retention is defined on *substantive viewpoint
   representation*, not citation presence (q133 is the clearest illustration
   of this distinction).
6. **Both frameworks:** the 54.3% citation-amplification figure seen in
   earlier drafts / other groups' reports uses a different elite definition
   and pipeline and is **not comparable** to these measured results.

---

## 7. Relation to RQ1 and RQ3

Framework A's neutral result (no amplification) combined with RQ1's neutral
result (no significant retrieval-stage bias) led to the decision that the
optional "Framework A × RQ3" linkage (re-running Framework A on RQ3's
MMR-reranked context) was **not necessary** — there is no confirmed
generation-stage amplification to correct for. See `rq2_rq3_linkage_plan.md`.

Framework B's viewpoint-retention lens connects to RQ3's perspective-balanced
prompting as a potential mitigation target, though since B's baseline result
is already high (97.2%), this was not pursued as a required follow-up.

---

*This document consolidates the RQ2 methodology recorded across `rq2_plan.md`
(v2), `rq2_frameworkA_summary.md`, and `rq2_frameworkB_summary.md`, for reuse
in the Final Report's Methodology and Results sections.*
