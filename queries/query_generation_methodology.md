# Query Generation Methodology

**Source documents:** `step4.md`, `step4_v2.md`
**Scope:** How the 150 evaluation queries (100 neutral + 50 contradictory)
used across RQ1, RQ2, and RQ3 were designed and generated.
**Owner:** Yan-Bo (drafting with AI assistance), reviewed by the team.

---

## Part 1 — Original 50 Neutral Queries (from `step4.md`)

### 1.1 Goal

Generate 50 diverse research queries covering all q-bio subcategories, to be
used for Top-K semantic retrieval (Step 5) and later fairness auditing
(RQ1, RQ2, RQ3). Query diversity is critical: if queries concentrate in only
a few subcategories, retrieval results become unrepresentative and fairness
metrics (SPD, SRR) become unreliable.

### 1.2 Step 1 — Determine subcategory distribution

Before designing any query, the full q-bio corpus was scanned to count papers
per subcategory across all ten q-bio categories, ranging from 1,586 papers in
q-bio.OT to 13,181 in q-bio.QM. A legacy `q-bio` tag with no subcategory
(1,356 papers) was excluded from query design, since it cannot be mapped to a
specific subcategory.

### 1.3 Step 2 — Hybrid allocation of query counts

Rather than strict proportional allocation, a hybrid strategy was used:
larger subcategories received more queries, while smaller subcategories
retained a minimum representation, preventing the evaluation from
over-concentrating on the largest areas while ensuring every subcategory has
enough samples for later per-subcategory fairness analysis.

| Subcategory | Paper Count | Allocated Queries |
|-------------|-------------|--------------------|
| q-bio.QM | 13,181 | 7 |
| q-bio.PE | 12,999 | 7 |
| q-bio.NC | 12,131 | 6 |
| q-bio.BM | 6,745 | 5 |
| q-bio.SC | 1,808 | 5 |
| q-bio.MN | 4,157 | 4 |
| q-bio.GN | 3,835 | 4 |
| q-bio.TO | 2,618 | 4 |
| q-bio.CB | 2,451 | 4 |
| q-bio.OT | 1,586 | 4 |
| **Total** | **61,511** | **50** |

Note: category counts represent category *assignments*, not unique papers,
since one paper can carry multiple q-bio tags.

### 1.4 Step 3 — Draft each query under three principles

Each query was required to satisfy three principles:
(i) a natural-language research question, not a keyword search;
(ii) specific enough to retrieve relevant papers;
(iii) covering a distinct aspect within its subcategory, to avoid redundancy
against other queries in the same subcategory.

Drafts were produced in one pass with AI assistance, following the `step4.md`
specification (subcategory distribution, allocation, and the three principles
above) rather than a standalone, freeform prompt. In other words, the
generation process was spec-driven: the distribution table and allocation
counts constrained what the AI assistant produced, rather than the AI being
asked to invent queries unconstrained.

### 1.5 Step 4 — Manual review and refinement

After drafting, each query was reviewed one by one by a team member, focusing
on whether its target subcategory label was accurate. Three queries were
revised for category alignment:

- **q025** — changed from a chromatin-structure question to a protein-DNA
  interaction question (more canonical for q-bio.BM)
- **q047** — rephrased into a cross-domain question integrating molecular,
  cellular, and environmental factors (better fitting q-bio.OT)
- **q049** — rephrased into a cross-system comparative question (more
  appropriate for q-bio.OT)

### 1.6 Step 5 — Storage format

Each query was stored as a JSON object with three fields:

| Field | Type | Description |
|-------|------|-------------|
| `query_id` | str | Unique identifier, e.g. `"q001"` |
| `query_text` | str | Natural language research question |
| `subcategory` | str | Target q-bio subcategory, e.g. `"q-bio.NC"` |

The final set of 50 was written to `queries/queries.json`.

---

## Part 2 — Expansion to 150 Queries (from `step4_v2.md`)

### 2.1 Goal and motivation

The original 50 neutral queries were expanded to 150 total: the original 50
neutral queries were kept unchanged, 50 new neutral queries were added, and
50 new contradictory queries were added. This expansion served two distinct
purposes, which were deliberately kept separate:

- **Neutral queries (100 total)** — raise statistical power for RQ1 (retrieval
  parity) and RQ3 (fairness-utility tradeoff) by increasing the number of
  labeled retrieval slots available for SPD/SRR estimation.
- **Contradictory queries (50 total)** — enable RQ2's dissent-suppression and
  citation-bias audit on genuine two-sided academic debates, which the
  neutral queries cannot support.

### 2.2 Query set structure

| ID range | Type | Description |
|----------|------|--------------|
| q001–q050 | neutral | original 50 |
| q051–q100 | neutral | expanded 50 |
| q101–q150 | contradictory | new 50 |

A `type` field (`"neutral"` or `"contradictory"`) was added to the schema.
Drafts were kept in `queries_v2_draft.json`, leaving the original
`queries.json` untouched; the two sets were merged only after a sanity check
into a single file, `queries_all_150.json`, which is what Step 5a loads.

### 2.3 Design rules — expanded neutral queries (q051–q100)

- Fill subcategory angles **not already covered** by q001–q050.
- Keep the same how/what, method-oriented style used in the original 50, so
  that each new query still maps cleanly to a single q-bio subcategory. This
  keeps the subcategory-match relevance proxy valid and keeps the new queries
  comparable to the original set.

### 2.4 Design rules — contradictory queries (q101–q150)

- Must reflect a **genuine, live academic debate** with published opposing
  sides — for example: whether "junk DNA" has functional significance,
  neutral drift versus selection as the dominant evolutionary force,
  causality claims around the microbiome, neural criticality, and whether
  deep-learning structure prediction "solves" protein folding.
- Use an explicit "X or Y?" framing that forces the generated answer to take,
  or at least visibly present, a side.
- Avoid pseudo-debates — topics that are already scientifically settled but
  merely packaged as controversial.
- Avoid dependence on a single proper/product name where possible (e.g. q105
  replaced "AlphaFold" with "deep-learning-based protein structure
  prediction") so that retrieval stays inside the general q-bio corpus rather
  than keying on one branded method.

### 2.5 Workflow (same loop as the original 50)

Claude drafted queries by subcategory and by "angles to avoid" (reconstructed
from the existing q001–q050 to prevent overlap), and Yan-Bo reviewed and
revised each draft. This mirrors the same draft-then-review loop used for the
original 50 queries in Part 1.

### 2.6 Downstream schema additions tied to the expansion

Two fields were added to the Step 5a retrieval-output schema specifically
because of the expansion, and are relevant to how relevance/labels are
interpreted downstream:

- **`label_source`** — records which Step 1b institution-label version
  (v1 / v2a / v2b) was joined for a given row. This decouples the labeling
  decision from Step 5b, so that switching label versions and recomputing
  SPD/SRR later does not get mixed up with earlier runs.
- **`is_relevant = null` for contradictory queries** (not `0`). The
  subcategory-match relevance proxy used for neutral queries does not apply
  to debate queries, so writing `0` would falsely read as a retrieval
  failure — the same lesson learned from the earlier q047/q050 zero-hit case,
  which was a proxy mismatch, not an actual retrieval failure.

### 2.7 Analysis grouping (queries are never all averaged together)

The expanded query set is analyzed in four separate groups, never pooled
into one blanket average:

1. **Original 50 only** — regression check against the Update 1 baseline
   (Mean Precision@10 = 0.654, HitRate@10 = 0.96) to confirm nothing broke.
2. **Expanded neutral 50 only** — sanity check on the new queries themselves.
3. **All neutral 100** — the main RQ1 / RQ3 analysis.
4. **Contradictory 50** — RQ2 generation-bias audit only; excluded from the
   main Precision@10 / NDCG@10 / MRR computation, which is neutral-queries-only.

---

## Summary Table

| | Original 50 (Part 1) | Expansion to 150 (Part 2) |
|---|---|---|
| Source doc | `step4.md` | `step4_v2.md` |
| IDs | q001–q050 | q051–q100 (neutral), q101–q150 (contradictory) |
| Purpose | Baseline coverage across all 10 q-bio subcategories | Raise RQ1/RQ3 statistical power (neutral) + enable RQ2 debate audit (contradictory) |
| Allocation method | Hybrid (size-weighted, min. floor per subcategory) | Fill gaps not covered by q001–q050 (neutral); genuine two-sided debates (contradictory) |
| Relevance proxy | Subcategory match | Subcategory match (neutral only); `null` for contradictory |
| Drafting process | AI-drafted per step4.md spec, then manually reviewed | Claude-drafted per subcategory/avoid-angles, then Yan-Bo reviewed |
| Output file | `queries/queries.json` | `queries/queries_all_150.json` (merged) |

---

*This document consolidates the query-generation methodology recorded in
`step4.md` (original 50) and `step4_v2.md` (expansion to 150) for reuse in
the Final Report's Methodology section.*
