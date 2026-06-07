# Step 5: Baseline Retrieval and Evaluation

**Owner:** Jici  
**Depends on:**
- Step 3 (Raj): `fairsearch-qbio-chromadb` Kaggle Dataset must be published
- Step 4 (Yan-Bo): `queries/queries.json` must be committed to GitHub

---

## Goal

Run Top-K semantic retrieval for all 50 research queries against the ChromaDB index,
and compute baseline retrieval metrics (Precision@10, Recall@10, HitRate@10).

These results will be reported in **Slide 6** of the Project Update 1 presentation.

---

## Relevance Definition

Because no manual ground-truth relevance labels are available, we use
**target subcategory match** as a proxy relevance definition.

A retrieved paper is considered **relevant** if its `categories` field includes
the query's target q-bio subcategory.

**Example:**
```
Query subcategory : q-bio.NC
Retrieved paper categories : "q-bio.NC cs.LG"
→ relevant ✅

Retrieved paper categories : "q-bio.PE q-bio.QM"
→ not relevant ❌
```

---

## Inputs

### From GitHub repo
- `queries/queries.json` — 50 research queries with `query_id`, `query_text`, `subcategory`

### From Kaggle Datasets (add to your notebook)
- `fairsearch-qbio-processed-raj-jici-yb` → `qbio_papers.json`
  - Path: `/kaggle/input/fairsearch-qbio-processed-raj-jici-yb/qbio_papers.json`
- `fairsearch-qbio-chromadb` (Raj will publish after Step 3)
  - Path: `/kaggle/input/fairsearch-qbio-chromadb/chroma_db/`

---

## Retrieval Setting

```
K = 10  (primary baseline)
```

We use Top-K retrieval with K=10 as the main baseline setting.
If time permits, K=5 and K=20 may also be reported as a sensitivity check.

---

## Processing Steps

### Step 5.1 — Install dependencies
```python
!pip install chromadb sentence-transformers -q
```

### Step 5.2 — Load inputs
Load `queries.json` from the GitHub repo (committed file).
Load `qbio_papers.json` to retrieve full paper metadata by `paper_id`.
Connect to the ChromaDB collection `qbio_papers`.

### Step 5.3 — Embed each query and retrieve Top-K
For each of the 50 queries:
1. Encode `query_text` using `all-MiniLM-L6-v2` (same model as Step 2)
2. Query ChromaDB collection for Top-10 most similar papers
3. Record the retrieved `paper_id` list

**Important:** Use the same embedding model as Step 2 (`all-MiniLM-L6-v2`).
Using a different model will produce incompatible vectors and incorrect results.

### Step 5.4 — Compute baseline metrics

For each query, compute:

**Precision@10**
```
Precision@10 = number of relevant papers in Top-10 / 10
```

**Recall@10**
```
Recall@10 = number of relevant papers in Top-10 / total papers in target subcategory
```

Note: Recall@10 will be very small because the relevant pool is large
(e.g., q-bio.NC has 12,131 category assignments). Report it but emphasize Precision@10.

**HitRate@10**
```
HitRate@10 = 1 if at least one relevant paper appears in Top-10, else 0
```

Then compute the **average** of each metric across all 50 queries:
- Mean Precision@10
- Mean Recall@10
- Mean HitRate@10

Also report **per-subcategory** averages to show which subcategories retrieve better.

### Step 5.5 — Save results
Save per-query results as `retrieval_results.json`:

```json
[
  {
    "query_id": "q001",
    "query_text": "...",
    "subcategory": "q-bio.QM",
    "retrieved_paper_ids": ["paper_id_1", "paper_id_2", "..."],
    "precision_at_10": 0.7,
    "recall_at_10": 0.0005,
    "hit_rate_at_10": 1
  }
]
```

---

## Evaluation Metrics Summary

| Metric | Formula | Primary? |
|--------|---------|----------|
| Precision@10 | relevant in Top-10 / 10 | ✅ Primary |
| Recall@10 | relevant in Top-10 / subcategory size | Secondary |
| HitRate@10 | ≥1 relevant in Top-10 | ✅ Primary |

---

## Output

- `/kaggle/working/retrieval_results.json` — per-query retrieval results and metrics
- Summary table: Mean Precision@10, Mean Recall@10, Mean HitRate@10 (overall and per subcategory)

---

## For Slide 6 (Project Update 1)

Report the following in the presentation:
- Mean Precision@10 (overall)
- Mean HitRate@10 (overall)
- Per-subcategory Precision@10 table or bar chart
- Note that Recall@10 is low due to large relevant pool size

## For Slide 7 (Project Update 1)

At this stage, fairness auditing is preliminary because institution and region labels
are planned for the next phase (Step 1b via OpenAlex API).

Preliminary observations to report:
- Are retrieval results concentrated in certain years or q-bio subcategories?
- Do any queries consistently retrieve papers from a narrow set of authors or venues?

Formal SPD and SRR measurement will be completed after OpenAlex enrichment in Project Update 2.

---

## Notebook Name

Please name your notebook:
```
step5_retrieval_baseline.ipynb
```

---

## Next Steps (Project Update 2)

After Step 5a is complete:
- **Step 1b** (Yan-Bo): Enrich `qbio_papers.json` with institution and region labels via OpenAlex API
- **Step 5b** (Jici): Join retrieval results with institution labels → compute SPD and SRR
- **Step 6**: Apply fairness-aware re-ranking (Fair MMR / Fair-Top-K)
