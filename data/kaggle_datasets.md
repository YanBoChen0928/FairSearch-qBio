# Kaggle Datasets Index

Authoritative list of Kaggle datasets used across this project, with owner,
purpose, and which notebooks/steps reference each one. Kept here because
these paths were previously only findable by grepping notebook code.

All dataset URLs follow the pattern `https://www.kaggle.com/datasets/<owner>/<slug>`.

## Datasets

| Slug                                     | Owner                                                       | Purpose                                                                                      | Used by                                              |
| ---------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `fairsearch-qbio-processed-raj-jici-yb`  | yanbochen928                                                | Cleaned/deduplicated q-bio corpus, 55,300 papers (`qbio_papers.json`)                        | step3.md; Framework A and B generation notebooks     |
| `fairsearch-qbio-embeddings-raj-jici-yb` | yanbochen928                                                | all-MiniLM-L6-v2 sentence embeddings of the corpus                                           | step3.md; step6_reranking.ipynb                      |
| `fairsearch-qbio-chromadb`               | **rajlucka (original)** and **yanbochen928 (working copy)** | Prebuilt ChromaDB vector store, collection `qbio_papers`                                     | See note below                                       |
| `fairsearch-qbio-1b-labels-raj-jici-yb`  | yanbochen928                                                | Option B institution labels: `sample_labels_1000.json`, `retrieval_labels.json`              | step6_reranking.ipynb; step7 Framework B notebook    |
| `fairsearch-qbio-queries-yb`             | yanbochen928                                                | 150 queries (`queries_all_150.json`), cached `retrieval_results.json`, `sides_q101_150.json` | step5/step6 notebooks; step7 Framework A/B notebooks |
| `frameworkb-manual-check`                | yanbochen928                                                | Human-filled red-flag check CSV for Framework B (5 queries, seed 42)                         | step7-rq2-generation-frameworkb-yb.ipynb             |

## Full URLs currently referenced in code (owner: yanbochen928)

```
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-processed-raj-jici-yb
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-embeddings-raj-jici-yb
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-chromadb
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-1b-labels-raj-jici-yb
https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-queries-yb
https://www.kaggle.com/datasets/yanbochen928/frameworkb-manual-check
```

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
