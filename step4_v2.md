# Step 4-v2: Query Expansion Plan (neutral + contradictory)

Status: plan for review. Does not modify `queries.json`. Query generation is the
next step, after this plan is signed off. This document also specifies the
retrieval-output fields (Step 5a) and reporting rules (Step 5b / final report)
that the expansion requires, and it doubles as evidence-gathering for the
Step 1b go/no-go decision (see `step1b_v2.md`).

## 1. Goal

- Expand 50 -> 150 queries: keep the 50 original neutral, add 50 neutral,
  add 50 contradictory.
- Two purposes, kept separate:
  - neutral -> raise RQ1 / RQ3 statistical power (more labeled retrieval slots).
  - contradictory -> enable the RQ2 dissent-suppression and citation audit.

## 2. Query set structure

- ID ranges:
  - q001-q050  original neutral
  - q051-q100  expanded neutral
  - q101-q150  contradictory
- Schema adds a `type` field: `"neutral"` or `"contradictory"`.
- Draft lives in `queries_v2_draft.json`. `queries.json` stays untouched.
  Merge into `queries_all_150.json` only after a sanity check (approach A: a
  single merged file is what Step 5a loads).

## 3. Design rules

Neutral queries:
- Fill subcategory angles NOT already covered by q001-q050.
- Keep the same how/what, method-oriented style, each mapping cleanly to a single
  q-bio subcategory, so the subcategory-match relevance proxy stays valid and the
  new queries remain comparable to the original 50.

Contradictory queries:
- Must be genuine, live debates with published opposing sides (e.g. junk DNA
  functionality, neutral drift vs selection, microbiome causality, neural
  criticality, whether structure prediction "solves" folding).
- Use an "X or Y?" framing that forces the answer to take or show sides.
- Avoid pseudo-debates (already settled, only packaged as controversy).
- Avoid dependence on a proper name (prefer general phrasing over a product name)
  so retrieval stays inside the q-bio corpus.

Sample-level wording already agreed (apply at generation): q053 add "gene
expression profiles"; q054 add "biomolecular simulations"; q105 replace
"AlphaFold" with "deep-learning-based protein structure prediction".

## 4. Retrieval output fields (Step 5a)

Keep at least:
`query_id, query_text, subcategory, type, rank, paper_id, score/distance,
paper_categories, is_relevant`.

Two additions decided with the team:
- `label_source`: which Step 1b label version was joined (v1 / v2a / v2b). This
  decouples the 1b decision from 5b, so switching label versions and recomputing
  SPD/SRR does not get mixed up.
- For contradictory queries, `is_relevant = null` (NOT 0). The subcategory-match
  proxy does not apply to debate queries; writing 0 would falsely read as a
  retrieval failure, the same lesson as the q047/q050 zero-hit case (proxy
  mismatch, not retrieval failure).

## 5. Analysis grouping (do NOT average everything together)

1. Original 50 only -> regression check against the Update 1 baseline
   (Mean Precision@10 = 0.654, HitRate@10 = 0.96); confirm nothing broke.
2. Expanded neutral 50 only -> sanity check the new queries themselves.
3. All neutral 100 -> main RQ1 / RQ3 analysis.
4. Contradictory 50 -> RQ2 generation audit only; excluded from main Precision@10.

Precision@10 / HitRate@10 / NDCG@10 / MRR are computed on neutral queries only.

## 6. Coverage column (ties the expansion to the 1b decision)

Every group in the analysis table reports, ALONGSIDE SPD / SRR:
- number of labeled retrieval slots, and
- label coverage % (labeled slots / total slots).

Why: expanding to 150 neutral raises the query count, but effective sample size
is still `queries x top-K x coverage`. If coverage stays near 19%, 100 neutral
queries give only ~190 labeled slots, which may still be too few for a small SPD
to reach significance.

Decision hook: after the 150-run, read effective n and coverage to choose:
- SPD clearly > 0 with a CI excluding 0 -> queries were enough, keep v1 labels.
- SPD hugs 0, CI still crosses 0, coverage still ~19% -> coverage-bound,
  redo Step 1b (choose Option A or B in `step1b_v2.md`).

So the query expansion also collects the go/no-go evidence for Step 1b, in one
shared table.

## 7. RQ2 observations for contradictory queries

A. Does the generated answer present both sides of the debate?
B. Which side's papers does the answer cite?
C. Is the citation elite rate higher than the retrieved-context elite rate?

## 8. Workflow and sequencing

- Claude drafts queries by subcategory + angles-to-avoid (reconstructed from the
  existing q001-q050), Yan-Bo reviews and revises. Same loop as the original 50.
- Do not modify `queries.json` yet. This document is the plan; query generation
  is the next step after sign-off.

## 9. Open items / team alignment

- Share with Jici: the two field additions (`label_source`, `is_relevant = null`
  for contradictory) and the coverage column.
- Confirm the merge step (approach A: single merged `queries_all_150.json`) with
  whoever runs Step 5a.
