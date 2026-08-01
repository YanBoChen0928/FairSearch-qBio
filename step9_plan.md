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

*This is a planning document. §5's scope question is resolved (representative
subset, ~20 queries). Step 9-A/B/C/D work can begin once the query list is
finalized (see remaining items in §7). Update this file (or supersede it
with a finalized `step9_methodology.md`) as implementation proceeds.*
