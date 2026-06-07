# Step 3: Build ChromaDB Vector Index

**Owner:** Raj  
**Depends on:** Step 1a (Yan-Bo) and Step 2 (Yan-Bo) must be completed first.

---

## Goal

Load the pre-computed embeddings and paper metadata produced in Steps 1a and 2,
and store them into a local ChromaDB vector database.
The resulting ChromaDB index will be used in Step 5 for Top-K semantic retrieval.

---

## What is ChromaDB?

ChromaDB is a local vector database. It is not an external server —
it runs entirely inside the Kaggle notebook and stores data as files
in a local folder (e.g., `/kaggle/working/chroma_db/`).

Its main job is to store paper embeddings so that later steps can run
semantic search queries like:

```
User query → embed query → find Top-K most similar paper vectors → return papers
```

Each record stored in ChromaDB has three parts:

| Part | What it is | Example |
|------|-----------|---------|
| `id` | Unique identifier | `"0704.0021"` |
| `embedding` | 384-dim vector | `[0.12, -0.34, ...]` |
| `metadata` | Paper info (title, year, categories) | `{"title": "...", "year": "2007"}` |

---

## Inputs

You need to import two Kaggle Datasets into your notebook before running this step.

### Dataset 1: Processed paper metadata
- **Kaggle Dataset URL:** https://www.kaggle.com/datasets/yanbochen928/fairsearch-qbio-processed-raj-jici-yb
- **File:** `qbio_papers.json`
- **Kaggle path:** `/kaggle/input/fairsearch-qbio-processed-raj-jici-yb/qbio_papers.json`
- **Content:** 55,301 q-bio papers with `paper_id`, `title`, `abstract`, `authors`, `categories`, `year`

### Dataset 2: Pre-computed embeddings
- **Kaggle Dataset URL:** (Yan-Bo will share this after Step 2 is complete)
- **Files:**
  - `qbio_embeddings.npy` — embedding matrix, shape `(55301, 384)`
  - `embedding_info.json` — metadata file confirming model name, dimension, record count, and `paper_id` order
- **Kaggle path (once added):**
  - `/kaggle/input/fairsearch-qbio-embeddings/qbio_embeddings.npy`
  - `/kaggle/input/fairsearch-qbio-embeddings/embedding_info.json`

> **Important:** The row order in `qbio_embeddings.npy` matches the order of
> `paper_ids` in `embedding_info.json`, which matches the order of records
> in `qbio_papers.json`. Do NOT shuffle or re-sort either file.

---

## How to Add the Datasets in Kaggle

1. Open your Kaggle notebook
2. Right panel → **Input** → **+ Add Input**
3. Search for `fairsearch-qbio-processed-raj-jici-yb` → Add
4. Repeat for the embeddings dataset once Yan-Bo publishes it

---

## Processing Steps

### Step 3.1 — Install dependencies

```python
!pip install chromadb -q
```

### Step 3.2 — Load inputs

Load `qbio_papers.json` to get paper metadata.
Load `qbio_embeddings.npy` to get the pre-computed vectors.
Load `embedding_info.json` to verify alignment.

Key alignment check:
```
embedding_info["paper_ids"][i] == qbio_papers[i]["paper_id"]
```
If this check fails, do NOT proceed — the data is misaligned.

### Step 3.3 — Initialize ChromaDB

Create a persistent ChromaDB client pointing to `/kaggle/working/chroma_db/`.
Create a collection named `qbio_papers`.

### Step 3.4 — Insert records in batches

Insert records in batches of 500 to avoid memory issues.
Each record must include:
- `id` = `paper_id` (string)
- `embedding` = row from `qbio_embeddings.npy` (list of 384 floats)
- `metadata` = `{"title": ..., "year": ..., "categories": ...}`

> **Do NOT store `abstract` or `authors` in ChromaDB metadata.**
> These fields are large and will slow down retrieval.
> Step 5 will join back to `qbio_papers.json` using `paper_id` to get full details.

### Step 3.5 — Validate

After inserting all records, verify:
- Total count in ChromaDB collection should equal `55,301`
- Run one test query to confirm retrieval works

---

## Output

After the notebook finishes, the ChromaDB index will be saved at:
```
/kaggle/working/chroma_db/
```

---

## Publishing the ChromaDB Index as a Kaggle Dataset

1. Run the notebook with **Save Version → Save and Run All**
2. After the run completes, go to the **Output** panel
3. Download the `chroma_db/` folder
4. Go to https://www.kaggle.com/datasets/new
5. Upload the folder
6. Dataset name: `fairsearch-qbio-chromadb`
7. Visibility: **Public**
8. Click **Create**
9. Share the Dataset URL with Yan-Bo and Jici

---

## Notebook Name

Please name your notebook:
```
step3_chromadb.ipynb
```

---

## What Comes Next (Step 4 and 5)

Step 4 query generation can be done independently and does not require ChromaDB.

After Step 3 is complete, the ChromaDB index will be used by Step 5 for Top-K semantic retrieval and Precision/Recall evaluation.

Jici will import your `fairsearch-qbio-chromadb` Dataset to run Step 5.
Make sure the collection name is exactly `qbio_papers` so Jici's code can connect to it.
