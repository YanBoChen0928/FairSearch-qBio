# Kaggle Datasets Index

Authoritative list of Kaggle datasets used across this project, with owner,
purpose, and which notebooks/steps reference each one. Kept here because
these paths were previously only findable by grepping notebook code.

All dataset URLs follow the pattern `https://www.kaggle.com/datasets/<owner>/<slug>`.

## Datasets

| Slug                                     | Owner                                                       | Purpose                                                                                      | Used by                                              |
| ---------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `fairsearch-qbio-processed-raj-jici-yb`  | yanbochen928                                                | Cleaned/deduplicated q-bio corpus, 55,300 papers (`qbio_papers.json`)                        | step3.md; Framework A and B generation notebooks; **Step 8 RAGAS notebook** |
| `fairsearch-qbio-embeddings-raj-jici-yb` | yanbochen928                                                | all-MiniLM-L6-v2 sentence embeddings of the corpus                                           | step3.md; step6_reranking.ipynb                      |
| `fairsearch-qbio-chromadb`               | **rajlucka (original)** and **yanbochen928 (working copy)** | Prebuilt ChromaDB vector store, collection `qbio_papers`                                     | See note below                                       |
| `fairsearch-qbio-1b-labels-raj-jici-yb`  | yanbochen928                                                | Option B institution labels: `sample_labels_1000.json`, `retrieval_labels.json`              | step6_reranking.ipynb; step7 Framework B notebook    |
| `fairsearch-qbio-queries-yb`             | yanbochen928                                                | 150 queries (`queries_all_150.json`), cached `retrieval_results.json`, `sides_q101_150.json` | step5/step6 notebooks; step7 Framework A/B notebooks |
| `frameworkb-manual-check`                | yanbochen928                                                | Human-filled red-flag check CSV for Framework B (5 queries, seed 42)                         | step7-rq2-generation-frameworkb-yb.ipynb             |
| `step7-frameworka-for-raj` (**display title**: `step7_frameworkAB_result_for_Raj`) | yanbochen928 | Raw per-query generation records for BOTH frameworks: `rq2_gen_checkpoint.jsonl` (Framework A, 100 neutral) and `rq2_frameworkB_generation_raw.jsonl` (Framework B, 50 contradictory). Originally created for Raj as Framework-A-only; the display title was renamed 2026-08-01 when Framework B's file was added as a new version. | Raj's Step 8 access; Step 8 RAGAS pilot notebook     |

## Full URLs currently referenced in code (owner: yanbochen928)

```
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-processed-raj-jici-yb
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-embeddings-raj-jici-yb
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-chromadb
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-1b-labels-raj-jici-yb
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-queries-yb
https://www.kaggle.com/datasets/yanbochen928/frameworkb-manual-check
https://www.kaggle.com/datasets/yanbochen928/step7-frameworka-for-raj
```

## Note: `queries_all_150.json` exists in TWO datasets (found 2026-08-01)

The table above lists `queries_all_150.json` under `fairsearch-qbio-queries-yb`,
which is where it was originally published. **A second copy also lives inside
`step7-frameworka-for-raj`**, having been bundled there when that dataset was
built for Raj.

This was discovered empirically while writing Cell 8 of the Step 8 notebook:
the expected path under `fairsearch-qbio-queries-yb` raised
`FileNotFoundError`, and an `os.walk` over `/kaggle/input` located the file at

```
/kaggle/input/datasets/yanbochen928/step7-frameworka-for-raj/queries_all_150.json
```

**Practical consequence.** Which path resolves depends on which datasets a
given notebook has attached, so hardcoding either one is fragile. Prefer the
`find_file()` pattern already used in Cell 1 of the Step 8 notebook
(`Path("/kaggle/input").rglob(filename)`), which locates the file by name
regardless of which dataset supplies it.

**Not verified:** whether the two copies are byte-identical, or whether they
could drift if one dataset is re-versioned without the other. Both are
currently assumed to be the same pre-registered 150-query set. If the two ever
disagree, `queries/queries_all_150.json` in this repository is the source of
truth.

**Note on the rename (corrected 2026-08-01):** only the dataset's **display
title** was changed, from `step7-frameworka-for-raj` to
`step7_frameworkAB_result_for_Raj`. Kaggle does not update the URL slug when
the title changes — that requires a separate, explicit slug edit in dataset
Settings, which was NOT done here. Confirmed empirically: the Step 8 pilot
notebook's `find_file()` output still resolves both files under
`/kaggle/input/datasets/yanbochen928/step7-frameworka-for-raj/`. So the slug
(and therefore the URL and the `/kaggle/input` path) is still
`step7-frameworka-for-raj`; only the title shown in the Kaggle UI is new.
Use the slug above for any code or URL; use the title only when describing
the dataset to a person.

## Note on `fairsearch-qbio-chromadb` (two versions exist)

Raj originally built and published this dataset (`step1.md`, `step3.md`: "Raj
will publish after Step 3"). Some early Step 5 notebooks pull from
`rajlucka/fairsearch-qbio-chromadb` via `kagglehub.dataset_download(...)` as a
fallback path.

Later, Yan-Bo downloaded Raj's version and re-uploaded it under his own
account (`yanbochen928/fairsearch-qbio-chromadb`), and subsequent notebooks
(the `-yb-kaggle-*` retrieval baseline notebooks) reference the working copy
at `/kaggle/input/datasets/yanbochen928/fairsearch-qbio-chromadb/chroma_db/`.

**Both copies exist.** Raj's is the original publish; Yan-Bo's is the working
copy actually used in the RQ1/RQ2/RQ3 notebooks from Step 5 onward. If
rebuilding the pipeline from scratch, use Yan-Bo's copy for consistency with
the rest of the notebooks, or confirm the two copies are identical in content
before treating them as interchangeable (not verified as byte-identical here).

## How to find the exact URL for any slug above

```
https://www.kaggle.com/datasets/<owner>/<slug>
```

e.g. `https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-queries-yb`

This file lists slugs and owners as confirmed from notebook code and step\*.md
files as of 2026-07-13; it does not independently verify that each URL
resolves (no network access from this session). If a link 404s, check the
owner's Kaggle profile for a renamed or re-uploaded version.
