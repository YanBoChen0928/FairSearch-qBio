# Handoff Status: RQ1 -> Step 6 (Project Update 2)

Status snapshot for teammates (Raj, Jici) picking up Step 6 onward.
This is a PROGRESS file. The full delivery checklist (with final
SPD/SRR/CI numbers) comes after Step 5b runs, in
`handoff_for_step6-8_project_update2.md`.

Last updated: 2026-07-08
Owner of 1b->5b (RQ1): Yan-Bo

---

## TL;DR

- Step 1b labeling is DONE (Option B). Two clean label files exist.
- Step 5b (formal SPD/SRR + CI + significance) is NOT run yet.
- Do NOT start Step 6 evaluation against the OLD baseline (0.233) or the
  OLD kagglehub label set. Use the new Option B files below.
- Preview only: SPD = 0.177 - 0.144 = +0.033 (small; significance TBD in 5b).

---

## Where the pipeline stands (step by step)

| Step | What | Status |
|------|------|--------|
| 1  | Data prep (~55,300 q-bio papers) | done |
| 2  | Embeddings (all-MiniLM-L6-v2, 384-dim) | done |
| 3  | ChromaDB (`qbio_papers`) | done |
| 5a | Retrieval, 150 queries, top-10 | done |
| 1b | Institution labeling (Option B) | done |
| 5b | Formal fairness audit (SPD/SRR/CI) | NOT run yet |
| 6  | Fair MMR re-ranking (RQ3) | not started (your part) |
| 7  | Gemini + balanced prompt (RQ2) | not started (your part) |
| 8  | Evaluation (NDCG/MRR/SPD/RAGAS) | not started (your part) |
| 9  | Streamlit demo | not started |

Step 6-8 is the substantive work; Step 9 wraps it into a demo. All of the
above (1b -> 8) belongs to Project Update 2.

---

## The four data files you will need (in `data/`)

Full field-by-field docs are in `data/README_data.md`. Short version:

| File | What it gives you |
|------|-------------------|
| `retrieval_results.json` | 150 queries x top-10 papers + relevance. The candidates Step 6 re-ranks. |
| `retrieval_labels.json` | Elite label for each retrieved paper. Use this to measure post-rerank SPD. |
| `sample_labels_1000.json` | Baseline elite rate (0.144). The reference point for SPD. |
| `qs_top50_elite_2026.json` | Definition of "elite" (QS Top-50). Use if you label any new paper. |

For MMR diversity you also need the embeddings (in `data/processed/`):
`qbio_embeddings.npy` + `embedding_info.json`.

---

## Five things that WILL trip you up (read before Step 6)

1. Baseline is 0.144, NOT 0.233. The old v1 baseline (0.233) was biased
   (labeled subset over-represented elite schools). Option B replaces it with
   an unbiased random-sample rate of 0.144. If you compute post-rerank SPD
   against 0.233, it will not match RQ1.

2. Do NOT use Raj's old kagglehub dataset
   (`rajlucka/fairsearch-qbio-institution-labels`). That is the v1 whole-corpus
   table. Use the Option B files above instead.

3. Neutral only for the main metric. Queries q001-q100 are neutral (RQ1/RQ3);
   q101-q150 are contradictory and held out for RQ2. Compute the main SPD on
   neutral only.

4. Coverage is ~44-58%, not 100%. Only papers with a findable affiliation are
   labeled; the rest are excluded (not counted as elite or non-elite). Your
   post-rerank SPD is computed over labeled slots only. Expect smaller effective
   n than the raw slot count.

5. Elite threshold is QS Top-50, not Top-100. Exact display-name match against
   `qs_top50_elite_2026.json`.

---

## What is still pending on my side (RQ1)

- Run Step 5b to produce the authoritative SPD, SRR, 95% CI, and binomial
  p-value (neutral only). Preview SPD is +0.033; given how small it is, the CI
  may cross zero (i.e. direction present but possibly not significant). That is
  a valid, honest result and does not block Step 6.
- Upload the two label files as one Kaggle dataset (planned:
  `fairsearch-qbio-1b-labels`) so 5b and Step 6 notebooks can read them.
- After 5b: write the full delivery checklist with final numbers in
  `handoff_for_step6-8_project_update2.md`.

---

## Honesty note (please keep this intact)

Any SPD-reduction figure, optimal lambda, or Gemini citation share you may see
in older draft diagrams are HYPOTHETICAL/EXPECTED values, not measured results.
Do not present them as findings. Only report numbers your own run produces, or
label them clearly as expected.
