# Step 9 Plan: Diagnostic Interface (Streamlit)

**Status: Scope decided — representative subset (see §5).**
The design below reflects the team's interpretation of the "diagnostic
interface" requirement, described in Yan-Bo's email to Prof. Sushmita
(draft dated 2026-07-19). Nothing in this document has been implemented yet;
this is an architecture plan written before any code. The full-150 vs.
representative-subset question raised in §5 has been resolved: the team is
proceeding with a representative subset (~20 queries, see
`step9_query_subset.md`), not full-150 coverage.

---

## 1. What the professor's email describes (5-step requirement)

Per the email: the interface should let a user pick one query (of ~100
neutral + 50 contradictory), then for that query:

1. Generate an LLM response using the **baseline** retrieval results.
2. Show **RQ1 diagnostics** (elite vs. non-elite distribution among
   retrieved papers) and **RQ2 diagnostics** (institutional distribution of
   papers cited in the generated response), plus the fairness metrics /
   group differences.
3. Show representative retrieved papers (title, institution label, arXiv
   link).
4. Apply the **RQ3 intervention** (re-ranking) to the same query and
   generate a **second** LLM response from the adjusted context.
5. Present a **side-by-side comparison** of baseline vs. intervention:
   retrieval composition, LLM citations, institutional representation,
   response quality.

```
┌──────────────────────────────────────────────────────────────┐
│  User picks one query from the 150-query set                 │
│  (100 neutral + 50 contradictory)                             │
└───────────────────────────┬────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌───────────────────┐                 ┌───────────────────┐
│  BASELINE branch   │                 │  RQ3 INTERVENTION   │
├───────────────────┤                 │  branch             │
│ 1. Original Top-10 │                 ├───────────────────┤
│    retrieval        │                 │ 4. MMR re-ranking   │
│    → LLM answer #1  │                 │    same query        │
├───────────────────┤                 │    → LLM answer #2   │
│ 2. RQ1 diagnostics: │                 ├───────────────────┤
│    elite/non-elite  │                 │ RQ1 diagnostics      │
│    distribution      │                 │ (post-rerank,        │
│                      │                 │  should be more      │
│    RQ2 diagnostics:  │                 │  balanced)            │
│    cited-paper       │                 │                      │
│    institution mix    │                 │ RQ2 diagnostics      │
├───────────────────┤                 │ (post-rerank)         │
│ 3. Representative    │                 ├───────────────────┤
│    papers: title /   │                 │ Representative        │
│    institution /     │                 │ papers (post-rerank)   │
│    arXiv link         │                 │                      │
└─────────┬──────────┘                 └─────────┬──────────┘
          │                                       │
          └───────────────────┬───────────────────┘
                              ▼
              ┌───────────────────────────────┐
              │ 5. Side-by-side comparison      │
              │    baseline vs. intervention:   │
              │    - institution-mix change      │
              │    - LLM citation change         │
              │    - fairness-metric deltas       │
              │    - response-quality deltas      │
              └───────────────────────────────┘
```

---

## 2. Gap analysis against existing WD/ files

| Requirement | Existing file(s) | Status |
|---|---|---|
| 1. Baseline retrieval + generation | `retrieval_results.json`, Step 7a/7b generation outputs | ✅ Have it |
| 2. RQ1 diagnostics (per-query elite/non-elite split) | `retrieval_labels.json` | ✅ Have it (needs per-query assembly) |
| 2. RQ2 diagnostics (cited-paper institution mix) | Framework A citation-parsing results | ✅ Have it (needs per-query assembly) |
| 3. Paper title / institution / arXiv link | `retrieval_results.json` + `retrieval_labels.json` | ✅ Have it (needs assembly) |
| 4. RQ3 re-rank → second LLM generation, per query | `rq3_results.json` (aggregate stats only) | ❌ **Missing** — no per-query re-ranked paper list, no second Gemini call ever made on re-ranked context |
| 5. Streamlit UI itself | `app/streamlit_app.py` (listed in README, never written) | ❌ **Not started** |

**Key finding: most of the raw material already exists. The one clear gap
is step 4** — the RQ3 notebook (`step6-reranking-yb-optimized-basedon-jici.ipynb`)
only computed aggregate λ-sweep statistics (mean SPD, mean NDCG@10 across all
queries); it never saved the actual re-ranked Top-10 paper list per query,
and never called Gemini a second time on that re-ranked context. This is new
work, not a repackaging of existing output.

---

## 3. Architecture decision: precompute vs. live

Two fundamentally different technical routes were considered, given that
everything so far (ChromaDB, embeddings, Gemini calls) runs on Kaggle, not
in an environment Streamlit can reach live:

**Route A — Precompute everything; Streamlit only displays.**
Kaggle runs baseline + RQ3-intervention for the queries in scope ahead of
time, bundles the results into JSON. Streamlit reads that JSON; picking a
query in the UI just switches which precomputed slice is shown — no live
Gemini/ChromaDB call happens during a demo session.

**Route B — Live computation.** Streamlit calls Gemini/ChromaDB/the
re-ranker in real time when a user picks a query. Requires moving ChromaDB,
the embedding model, and Gemini API credentials into wherever Streamlit runs.

**Decision: Route A (precompute-first).** Reasoning:
1. The professor's email explicitly says the user picks from **this
   project's existing query set** — not an arbitrary free-text question — so
   there is no requirement for live computation.
2. The team has no prior experience deploying ChromaDB + the embedding model
   outside Kaggle; Route B adds real deployment complexity (Streamlit
   Community Cloud's free tier is not sized for this) and a live-API-key
   exposure question.
3. Route A makes the Streamlit app itself much simpler — a pure JSON-reader
   and chart-renderer — which lowers demo-day risk (no live quota/network
   failure possible during presentation).

---

## 4. How Streamlit actually runs (since this was an open question)

Under Route A, the runtime picture is simple:

1. **Local development:** `pip install streamlit` in this project's
   environment; `app/streamlit_app.py` reads the precomputed JSON bundle
   from `data/`; running `streamlit run app/streamlit_app.py` opens a local
   browser tab (typically `localhost:8501`) for testing.
2. **Sharing / grading:** the simplest path is **Streamlit Community
   Cloud** (free) — connect the GitHub repo, it hosts a public URL
   automatically. No local machine needs to stay running for the professor
   or classmates to view it.

---

## 5. Scope decision — representative subset (resolved)

The professor's own email had raised this question, which directly
determines how much work Step 9-A (§6) requires:

> "Should the interface focus on demonstrating a few representative queries
> in depth, or are we expected to support and summarize the complete query
> set within the interface?"

This matters because Step 9-A requires **calling Gemini a second time**
(baseline generation already happened in Step 7a/7b, but the RQ3-intervention
generation on re-ranked context has never been run) — and per the Step 8
quota-risk analysis (`step8.md` §5), 150 queries × multiple calls each risks
hitting the same free-tier walls that broke Framework B's judge run. A
representative-queries scope is an order of magnitude cheaper than "all 150."

**Decision:** the team is proceeding with a representative subset, not full-
150 coverage. The approach is a ~20-query subset chosen by a documented,
seed-fixed sampling rule (stratified by subcategory for neutral queries,
spread across debate topics for contradictory queries, seed=42, q033
retained as a disclosed anchor) rather than hand-picked queries — see
`step9_query_subset.md` for the full method, rationale, and limitations.
This keeps the subset defensible against cherry-picking concerns and adds
negligible API cost on top of Step 8's RAGAS quota usage (~20 extra calls
vs. Step 8's ~1,500-2,000).

---

## 6. Proposed step sequence (scope decided, §5)

```
Step 9-A (Kaggle, new work): generate the RQ3-intervention's second LLM
    answer, per query in scope — needs: candidate pool + MMR re-ranking
    code (reused from Step 6) + a second Gemini call per query
    ↓ (requires: candidate pool size, MMR λ operating point per rq3_methodology.md,
       and a fresh Gemini quota budget — same risk class as step8.md §5)
Step 9-B (Kaggle, assembly): bundle baseline + intervention branches
    (retrieval / generation / RQ1 diagnostics / RQ2 diagnostics / paper
    metadata) into one per-query JSON, for every query in scope
    ↓
Step 9-C (local): download the bundle; write app/streamlit_app.py to read
    and render it
    ↓
Step 9-D (local test → deploy): `streamlit run` locally to verify, then
    deploy via Streamlit Community Cloud
```

---

## 7. Decisions still needed before implementation

- [x] Full-150 vs. representative-subset scope (§5) — **decided:**
      representative subset (~20 queries), sampling method in
      `step9_query_subset.md`.
- [ ] Finalize the actual ~20-query list by running the sampling script
      per `step9_query_subset.md` §2 (stratified by subcategory, seed=42).
- [ ] RQ3 operating point to use for the intervention branch — per
      `rq3_methodology.md` §4.2, λ=0.8 (institution-aware MMR) was the
      pre-registered operating point; confirm this is still the one to
      demo, rather than re-selecting per query.
- [ ] Whether Step 9-A's second Gemini call reuses the exact Step 7a/7b
      prompt skeleton (citation-marked, no balancing instruction) so the
      only variable that changes between baseline and intervention is the
      retrieved context, not the prompt itself.
- [ ] Data-bundle schema for the per-query JSON (field names, file
      location) — not yet drafted, depends on the scope decision above.

---

## 8. Scope tiering amendment (added 2026-08-01, supersedes §5 where they disagree)

§5 decided a fixed ~20-query subset. This amendment keeps that subset as the
guaranteed floor but removes the hard ceiling, because the cost analysis
behind §5 has changed.

**Why §5's justification weakened.** `step9_query_subset.md` §3 argued the
subset was justified because ~20 calls is negligible against Step 8's
estimated 1,500-2,000 calls. Step 8's `step8.md` §2a amendment (2026-08-01)
deferred Context Precision, cutting the committed Step 8 run to roughly 450
calls. The relative-cost argument no longer carries the same weight.

**Actual marginal cost of full coverage.** Step 9-A needs exactly one extra
Gemini generation per query (the second answer, on re-ranked context).
Re-ranking itself is local compute, no API. Citation parsing is pure code,
no API. So:

| Scope | Extra Gemini calls | Code difference |
|---|---|---|
| 20 queries | ~20 | a loop |
| all 150 queries | ~150 | the same loop |

The engineering effort is identical; only the loop count and the bundle
size differ. The decision is therefore a quota decision alone, not a design
decision, and it should not be frozen before the quota picture in
`step8.md` §5a is resolved.

**Amended scope rule (tiered, mirrors `step8.md` §2a):**

| Tier | Scope | Status |
|---|---|---|
| 1 (guaranteed) | ~20-query subset per `step9_query_subset.md` | run first; demo-ready floor |
| 2 (extend if quota allows) | remaining 130 queries, i.e. full 150 | removes the cherry-picking question entirely |

**Implementation requirement.** Step 9-A/B must be written scope-agnostic:
a single `QUERY_SCOPE` list variable drives the loop, and re-running with a
longer list must extend the bundle rather than require code changes. Do not
hard-code 20 anywhere.

**Two arguments in favour of reaching Tier 2 if quota permits:**

1. The rubric does not constrain interface coverage. Slide 9 asks only for
   "Screenshots or live demo of your diagnostic interface." The separate
   GitHub deliverable, "JSON file containing results of the 100-query
   audit," refers to the retrieval audit results, not to Step 9's scope.
2. Prof. Sushmita's email (§1) describes the user picking one query from
   the ~100 neutral + 50 contradictory set. Full coverage matches that
   description literally, and makes `step9_query_subset.md`'s
   anti-cherry-picking defence unnecessary rather than merely adequate.

**Disclosure requirement either way.** The interface must display its actual
coverage (e.g. "20 of 150 queries precomputed"), and the report must state
the coverage and, if Tier 1 only, cite the sampling rule in
`step9_query_subset.md`. Silent partial coverage is not acceptable.

### 8a. The quota premise has now dissolved (added 2026-08-01, later same day)

§8 above deliberately refused to freeze the scope "before the quota picture
in `step8.md` §5a is resolved". That picture has since resolved in practice,
and it removes the constraint rather than tightening it.

What actually happened in Step 8 (see `step8.md` §4a.7 and §4a.8):

| Step 8 tier | Planned cost | Actual outcome |
|---|---|---|
| Tier 1 Faithfulness | ~300 calls over 150 queries | COMPLETE. 148/150 succeeded, zero 429s. |
| Tier 2 Answer Relevancy | ~150 calls | CLOSED as technically infeasible. Consumes nothing further. |
| Tier 3 Context Precision | ~1,500 calls | Still deferred, pending the §2a rubric question. |

So the free-tier headroom that §8 was waiting on is now demonstrated, not
assumed: 150 sequential Gemini calls completed in one sitting without a
single rate-limit error. Step 9-A's full-coverage cost (~150 calls, one per
query) is the same order as a run that has already been shown to work.

**Consequence.** Tier 2 (all 150 queries) is no longer gated on quota. What
remains is engineering time before the 2026-08-11 deadline, plus the
unresolved Tier 3 question, which would compete for the same daily quota if
Prof. Sushmita's answer to §2a makes Context Precision mandatory.

**This is not a decision, only a removed constraint.** The scope rule in §8
stands as written: Tier 1 is still the guaranteed floor and the
implementation must still be scope-agnostic. Choosing Tier 2 remains a
judgement about available working time, and the disclosure requirement above
applies unchanged.

---

## 9. Data architecture: additive, not a rewrite

**Answer to "do we need to change the data architecture?" — No.** Nothing
existing is modified or overwritten. Step 9 adds one new derived artifact
layer on top of files that already exist, the same purely-additive pattern
used for the RQ1 bio robustness check (`Claude_todo_memo.md` §1).

**Existing inputs (verified against the actual files 2026-08-01):**

| File | Verified fields used by Step 9 |
|---|---|
| `data/retrieval_results.json` | `query_id`, `query_text`, `subcategory`, `type`, `retrieved_paper_ids` (10 per query), `relevance`, `precision_at_10` |
| `data/retrieval_labels.json` | `labels[]` with `paper_id`, `coverage`, `institution`, `country`, and `elite_label` (present ONLY when `coverage == "found"`) |
| `data/processed/qbio_papers.json` | `paper_id`, `title`, `abstract`, `authors`, `categories`, `year` |
| Step 7a/7b generation output | baseline answer text + parsed `[n]` citation markers per query |
| `results/rq3_results.json` | aggregate only: `baseline` and `mmr_semantic_by_lambda[]` (`lambda`, `NDCG@10`, `MRR`, `uniq_institutions`, `uniq_countries`, `elite_share`, `SPD`, `labeled_slots`). Confirmed: contains NO per-query re-ranked lists. |

**New artifacts Step 9 creates (none of these exist yet):**

1. `data/step9_query_scope.json` - the resolved query list for the current
   tier, produced by the sampling script (seed=42) per
   `step9_query_subset.json` rules.
2. `data/step9_rerank_per_query.json` - the per-query re-ranked Top-10
   paper_id list at the chosen operating point. This is the artifact whose
   absence is the core gap identified in §2.
3. `data/step9_bundle.json` - the single display bundle Streamlit reads
   (schema in §10).

**Labeling rule inherited unchanged.** Elite shares count only papers with
`coverage == "found"`. Papers with `no_affiliation` or `not_found` are
excluded from the denominator and are NEVER counted as 0, matching the
RQ1/RQ2 rule. The interface must show the unknown count rather than hiding
it, otherwise a query with 8 unknown papers would display a misleadingly
confident elite share.

---

## 10. Bundle schema (draft, resolves the open item in §7)

One JSON file, one record per query in scope. Field names below are chosen
to match the existing files' conventions.

```jsonc
{
  "meta": {
    "generated_at": "2026-08-__",
    "tier": 1,                          // 1 = subset, 2 = full 150
    "n_queries_in_bundle": 20,
    "n_queries_total": 150,             // for honest coverage display
    "rerank_operating_point": {         // confirm against rq3_methodology.md
      "method": "institution_aware_mmr",
      "lambda": 0.8
    },
    "generation_model": "gemini-3.1-flash-lite",
    "generation_temperature": 0,
    "prompt_skeleton": "step7a_evidence_grounded_no_balancing",
    "elite_list": "QS World University Rankings 2026 Top 50",
    "sampling_seed": 42
  },
  "queries": [
    {
      "query_id": "q033",
      "query_text": "...",
      "subcategory": "q-bio.QM",
      "type": "neutral",
      "is_anchor": true,                // q033 disclosed anchor, per subset doc

      "baseline": {
        "papers": [
          {
            "rank": 1,
            "paper_id": "1610.07213",
            "title": "...",
            "institution": "University of Freiburg",
            "country": "DE",
            "coverage": "found",        // found | no_affiliation | not_found
            "elite_label": 0,           // absent when coverage != "found"
            "arxiv_url": "https://arxiv.org/abs/1610.07213",
            "was_cited": true
          }
        ],
        "answer_text": "...",
        "cited_paper_ids": ["1610.07213"],   // unique, parsed from [n]
        "diagnostics": {
          "n_labeled": 7,               // coverage == "found" only
          "n_unknown": 3,               // shown, never folded into 0
          "context_elite_share": 0.1429,
          "cited_elite_share": 0.2000,
          "amplification": 0.0571,      // null if either denominator empty
          "uniq_institutions": 6,
          "uniq_countries": 4
        }
      },

      "intervention": {
        // identical structure to "baseline", built from the re-ranked Top-10
        "papers": [],
        "answer_text": "...",
        "cited_paper_ids": [],
        "diagnostics": {}
      },

      "delta": {
        "context_elite_share": -0.0429,
        "cited_elite_share": -0.0500,
        "uniq_institutions": 1,
        "uniq_countries": 0,
        "n_papers_changed": 4           // how many of the Top-10 differ
      }
    }
  ]
}
```

**Schema notes.**

- `delta` is precomputed rather than derived in Streamlit, so the UI stays a
  pure renderer (the whole point of Route A) and so the numbers shown in the
  demo are reproducible from the bundle alone.
- `amplification` follows the RQ2 Framework A empty-denominator rule: `null`
  when a query has no labeled context papers or no labeled cited papers.
  Streamlit must render `null` as "not evaluable", never as 0.
- Per-query diagnostics are illustrative. Per `step9_query_subset.md` §4,
  aggregate statistical claims stay grounded in `results/rq3_results.json`,
  and the interface should not present per-query numbers as evidence for
  the headline RQ3 conclusion.

---

## 11. Step-by-step implementation sequence

Ordered so that the schema is frozen early, which is what lets 9-B and 9-C
proceed in parallel instead of serially.

**9-0. Freeze the schema and the operating point (do this first, ~1 hour)**
- Confirm the §10 field names with whoever writes 9-B and 9-C.
- Confirm the re-rank operating point against `rq3_methodology.md` §4.2
  (λ=0.8, institution-aware MMR was the pre-registered point). Decide
  explicitly that it is fixed across all queries, not re-selected per query
  (re-selecting per query would be a post-hoc choice and would break the
  pre-registration discipline).
- Confirm 9-A's second generation reuses the exact Step 7a/7b prompt
  skeleton, so the only variable changing between branches is the retrieved
  context, not the prompt.

**9-A. Kaggle: re-rank + second generation (~0.5 to 1 day)**
- Run the sampling script (seed=42) to produce `step9_query_scope.json`.
- Re-run the Step 6 MMR code with per-query output enabled, saving
  `step9_rerank_per_query.json`. This is the genuinely new work.
- For each query in scope, call Gemini once on the re-ranked context.
  Checkpoint per query to JSONL, same pattern as `rq2_gen_checkpoint.jsonl`.
- Parse `[n]` markers on the new answers with the existing Framework A
  parser. Do not write a second parser.

**9-B. Kaggle: assemble the bundle (~0.5 day)**
- Join baseline + intervention + labels + paper metadata into
  `data/step9_bundle.json` per the §10 schema.
- Assert `len(queries) == len(QUERY_SCOPE)` and fail loud on any missing
  join, consistent with the project's fail-loud validation rule.

**9-C. Local: write the Streamlit app (~1 to 2 days, parallel with 9-B)**
- `app/streamlit_app.py` reads the bundle and renders it. Reuse the layout
  already prototyped in `step9_streamlit_demo_draft.py` and the concept HTML
  Prof. Sushmita reviewed.
- Per her feedback, put the fairness results and key metrics at the top.
- Can be developed against a hand-written 1-query mock bundle before 9-B
  finishes, which is why 9-0 matters.

**9-D. Deploy and test (~0.5 day, but start early)**
- `streamlit run` locally, then deploy to Streamlit Community Cloud.
- Do NOT leave the first deployment attempt to the final days.

---

## 12. Known risks and gaps not yet closed

1. **9-A is new code, not repackaging.** Confirmed 2026-08-01 by inspecting
   `results/rq3_results.json`: it holds only aggregate λ-sweep statistics.
   No per-query re-ranked list has ever been saved, and no second Gemini
   call has ever been made on re-ranked context.
2. **`step9_methodology.md` does not exist.** RQ1/RQ2/RQ3 each have one; the
   report will need a citable methodology source for Step 9. Write it once
   implementation stabilises, mirroring the existing pattern.
3. **The 20-query list has not been generated.** `step9_query_subset.md`
   specifies the method but the sampling script has not been run, so the
   actual query list does not exist yet. This blocks 9-A.
4. **Streamlit Community Cloud deployment is untried by this team.** Expect
   friction on `requirements.txt` resolution, relative file paths, and
   repository file-size limits. Budget buffer; do not first attempt it near
   the deadline.
5. **Contradictory-query branch needs a decision.** For q101-q150 the
   baseline answers come from Step 7b and the relevance field is null by
   design. Decide whether the interface shows the Framework B
   viewpoint-retention diagnostic for those queries, or only the
   institutional diagnostics. Currently unspecified.
6. **Bundle size.** 150 queries x 20 papers x (title + institution) plus two
   answer texts per query is likely a few MB. Fine for Streamlit, but
   confirm it does not trip GitHub file-size warnings; if it does, store
   answers separately or compress.

---

*This is a planning document. §5's original fixed-subset decision is
amended by §8 into a tiered scope (subset guaranteed, full 150 if quota
allows). The bundle schema in §10 resolves §7's last open item in draft
form and needs sign-off before 9-B and 9-C start. Update this file, or
supersede it with `step9_methodology.md`, as implementation proceeds.*
