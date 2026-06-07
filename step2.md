# Step 2: Generate Embeddings with all-MiniLM-L6-v2

## Goal
Convert each paper's abstract into a 384-dimensional dense vector
using the `all-MiniLM-L6-v2` sentence embedding model.
These vectors will be used in Step 3 to build the ChromaDB index.

## Input
- `/kaggle/input/fairsearch-qbio-processed-raj-jici-yb/qbio_papers.json`
- 55,301 records from the current Kaggle arXiv snapshot,
  each containing `paper_id`, `abstract`, and other metadata

## Why all-MiniLM-L6-v2?
- A distilled version of BERT, optimized for semantic similarity tasks
- Output: 384-dimensional vector per sentence/paragraph
- Fast and lightweight — suitable for 55k abstracts on Kaggle GPU
- Used as the retrieval backbone for RQ1 and RQ3 evaluation

## Processing Steps

### 1. Install and load the model
Load `all-MiniLM-L6-v2` via the `sentence-transformers` library.
The model will automatically use GPU if available.

### 2. Extract abstracts in order
We iterate through `qbio_papers` in a fixed order and keep track of
`paper_id` for each position. This order must be preserved so that
`embeddings[i]` always corresponds to `qbio_papers[i]`.

### 3. Encode in batches
Encoding 55k abstracts one-by-one is slow.
We use `batch_size=64` to encode multiple abstracts at once,
which takes full advantage of GPU parallelism.
Progress is tracked with `tqdm`.

### 4. Output files

| File | Content | Shape |
|------|---------|-------|
| `qbio_embeddings.npy` | All paper embeddings | (num_records, 384) |
| `embedding_info.json` | Model metadata + ordered paper_ids | JSON object |

`embedding_info.json` structure:
```json
{
  "model": "all-MiniLM-L6-v2",
  "embedding_dim": 384,
  "num_records": 55301,
  "order": "same as qbio_papers.json",
  "paper_ids": ["0704.0021", "0704.0034", "..."]
}
```

This file is critical for Step 3: it tells Raj which `paper_id`
corresponds to which row in the embedding matrix.

```
embeddings[0]  →  paper_ids[0]  →  qbio_papers[0]
embeddings[1]  →  paper_ids[1]  →  qbio_papers[1]
...
```

## Output
- `/kaggle/working/qbio_embeddings.npy`
- `/kaggle/working/embedding_info.json`

## Validation
- Embedding matrix shape: should be `(num_records, 384)`
  (expected for this run: `(55301, 384)`)
- First 3 paper_ids from `embedding_info.json`
- Sample vector (first 5 dimensions of `embeddings[0]`)

## Next Step
Publish both output files as a new Kaggle Dataset:
`fairsearch-qbio-embeddings`
Then Raj proceeds to Step 3: loading these files into ChromaDB.
