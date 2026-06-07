# FairSearch-qBio

Evaluating and Mitigating Institutional Bias in Academic RAG
for Quantitative Biology (q-bio) papers on arXiv.

# FairSearch-qBio

Evaluating and Mitigating Institutional Bias in Academic RAG
for Quantitative Biology (q-bio) papers on arXiv.

# FairSearch-qBio

## Evaluating and Mitigating Institutional Bias in Academic RAG Systems

**Course:** CS 6200 Information Retrieval — Northeastern University (Summer 2026)  
**Instructor:** Prof. Shanu Sushmita  
**Team:** Jici Jiang · Raj Lucka · Yan-Bo Chen
**GitHub:** [github.com/YanBoChen0928/FairSearch-qBio](https://github.com/YanBoChen0928/FairSearch-qBio)

---

## Project Overview

This project audits a Retrieval-Augmented Generation (RAG) system built on the arXiv **q-bio** corpus (~54,971 papers) for **institutional homophily** — the tendency to systematically rank or cite papers from elite universities higher than equally relevant work from non-elite institutions.

We investigate three research questions across the full RAG pipeline:

| RQ      | Stage               | Question                                                                         |
| ------- | ------------------- | -------------------------------------------------------------------------------- |
| **RQ1** | Retrieval (Step 5)  | Does semantic vector search exhibit institutional homophily?                     |
| **RQ2** | Generation (Step 7) | Does the LLM disproportionately cite elite institutions when generating answers? |
| **RQ3** | Re-ranking (Step 6) | What is the fairness–utility tradeoff when applying MMR re-ranking?              |

---

## Pipeline Architecture

```
Step 1  →  Prepare dataset (54,971 q-bio arXiv abstracts)
Step 2  →  Embed text with all-MiniLM-L6-v2
Step 3  →  Store vectors in ChromaDB
Step 4  →  Generate research queries
Step 5  →  Retrieve Top-K papers  ← RQ1 (SPD, SRR)
Step 6  →  Fair MMR re-ranking    ← RQ3 (NDCG@10, MRR)
Step 7  →  Gemini 1.5 Flash generation ← RQ2 (citation bias)
Step 8  →  Evaluate (NDCG@10, MRR, SPD, RAGAS)
Step 9  →  Streamlit diagnostic dashboard
```

---

## Technical Stack

| Component            | Tool                                                            |
| -------------------- | --------------------------------------------------------------- |
| Dataset              | arXiv metadata (Cornell University / Kaggle)                    |
| Embedding model      | `all-MiniLM-L6-v2` (sentence-transformers)                      |
| Vector database      | ChromaDB                                                        |
| Generative LLM       | Google Gemini 1.5 Flash                                         |
| Institution metadata | OpenAlex API                                                    |
| IR evaluation        | NDCG@10, MRR, Precision@K, Recall@K                             |
| Fairness metrics     | SPD (Statistical Parity Difference), SRR (Selection Rate Ratio) |
| RAG evaluation       | RAGAS (Faithfulness, Answer Relevancy, Context Precision)       |
| Dashboard            | Streamlit                                                       |
| Compute              | Kaggle Notebooks                                                |

---

## Repository Structure

```
FairSearch-qBio/
│
├── data/
│   ├── raw/                    # Raw arXiv JSON/CSV metadata (not committed, ~4GB)
│   ├── processed/              # Preprocessed metadata (filtered, enriched)
│   │   └── qbio_papers.json    # 54,971 q-bio abstracts (clean, no institution yet)
│   └── queries.json            # 50 starter queries for audit
│
├── src/                        # Core modules
│   ├── data_loader.py          # Load, preprocess, enrich arXiv metadata
│   ├── index_builder.py        # Build vector embeddings & index in ChromaDB
│   ├── retriever.py            # Query → vector search (Top-K)
│   ├── rerank.py               # Fairness-aware re-ranking (MMR, Fair-Top-K)
│   ├── audit.py                # Bias audit and evaluation scripts (SPD, SRR)
│   ├── metrics.py              # IR metrics (NDCG, MRR) & fairness metrics
│   └── prompt_utils.py         # Helpers for LLM synthesis / prompt engineering
│
├── notebooks/                  # Step-by-step development notebooks
│   ├── step1_data_prep.ipynb       # Yan-Bo: filter & clean 54k q-bio papers
│   ├── step2_embedding.ipynb       # Yan-Bo: embed abstracts with all-MiniLM-L6-v2
│   ├── step3_chromadb.ipynb        # Jici: store vectors in ChromaDB
│   ├── step4_query_generation.ipynb # Yan-Bo: generate 50 research queries
│   ├── step5_retrieval_baseline.ipynb # Jici: Top-K search + Precision/Recall
│   ├── step6_reranking.ipynb       # Jici: Fair MMR / Fair-Top-K
│   ├── step7_generation.ipynb      # Jici: Gemini generation + citation audit
│   └── step8_evaluation.ipynb      # Both: NDCG, MRR, SPD, RAGAS
│
├── app/                        # Phase IV: Dashboard
│   └── streamlit_app.py        # Streamlit interface: standard vs FairSearch
│
├── run_experiments.py          # Orchestration: run queries, audit, rerank, reports
├── README.md                   # Repo overview, quick start
├── requirements.txt            # Dependencies
└── LICENSE
```

---

## Work Division

| Step                                           | Owner  | Status         |
| ---------------------------------------------- | ------ | -------------- |
| Step 1 — Data preparation                      | Yan-Bo | ✅ Complete    |
| Step 2 — Embedding (all-MiniLM-L6-v2)          | Yan-Bo | 🔄 In progress |
| Step 3 — ChromaDB ingestion                    | Jici   | 🔄 In progress |
| Step 4 — Query generation                      | Yan-Bo | 🔄 In progress |
| Step 5 — Baseline retrieval + Precision/Recall | Jici   | ⏳ Upcoming    |
| Step 6 — Fair MMR re-ranking                   | Jici   | ⏳ Upcoming    |
| Step 7 — Gemini generation                     | Jici   | ⏳ Upcoming    |
| Step 8 — Full evaluation                       | Both   | ⏳ Upcoming    |
| Step 9 — Streamlit dashboard                   | Both   | ⏳ Upcoming    |

---

## Key Findings (Preliminary)

> Results will be updated as experiments complete.

- **RQ2 early signal:** Elite institutions account for ~11.7% of retrieved results but appear in ~54.3% of Gemini-generated citations.
- **RQ3 early signal:** Fair MMR at λ=0.7 reduces SPD by 67% while NDCG@10 actually improves vs. Fair-Top-K.

---

## Evaluation Metrics

**IR Utility**

- `Precision@K` — fraction of top-K results that are relevant
- `Recall@K` — fraction of all relevant results captured in top-K
- `NDCG@10` — ranking quality weighted by position
- `MRR` — how high the first relevant result ranks

**Fairness**

- `SPD` (Statistical Parity Difference) — gap in retrieval rates between elite and non-elite institutions
- `SRR` (Selection Rate Ratio) — ratio of elite-to-non-elite selection rate; ideal = 1.0

**RAG Quality**

- RAGAS: Faithfulness, Answer Relevancy, Context Precision

---

## Dataset Note

The raw arXiv snapshot (~4GB) is too large to commit to GitHub. To reproduce:

1. Download from [Kaggle — Cornell University arXiv](https://www.kaggle.com/datasets/Cornell-University/arxiv)
2. Place at `data/raw/arxiv-metadata-oai-snapshot.json`
3. Run `notebooks/step1_data_prep.ipynb` to extract the 54,971 q-bio papers

Institution labels are enriched via the [OpenAlex API](https://openalex.org/) and cached in `data/processed/`.

---

## Local Development

**Working directory (local machine):**

```
/Users/yanbochen/IdeaProjects/CS6200-Project
```

**Quick start (local):**

```bash
# 1. Clone the repo
git clone https://github.com/YanBoChen0928/FairSearch-qBio.git
cd CS6200-Project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add arXiv raw data (download separately from Kaggle)
# Place at: data/raw/arxiv-metadata-oai-snapshot.json

# 4. Run notebooks in order under notebooks/
```

**Kaggle environment (primary compute):**
All Step 1–2 notebooks are developed and executed on Kaggle Notebooks, where the arXiv dataset is directly mounted at:

```
/kaggle/input/datasets/organizations/Cornell-University/arxiv/arxiv-metadata-oai-snapshot.json
```

---

## Milestones (14-Week Schedule)

| Phase           | Week  | Milestone                                       | Status |
| --------------- | ----- | ----------------------------------------------- | ------ |
| I: Foundations  | 1–2   | Environment setup, data loading, ChromaDB index | ✅     |
| I: Foundations  | 3–4   | Naive RAG baseline, Precision & Recall          | 🔄     |
| II: Audit       | 5–6   | Institution labeling via OpenAlex               | ⏳     |
| II: Audit       | 7–8   | SPD & SRR measurement across 50 queries         | ⏳     |
| III: Mitigation | 9–10  | MMR & Fair-Top-K re-ranking                     | ⏳     |
| III: Mitigation | 11–12 | Perspective-Balanced Prompt + RAGAS eval        | ⏳     |
| IV: Conclusion  | 13    | Streamlit dashboard                             | ⏳     |
| IV: Conclusion  | 14    | Final presentation                              | ⏳     |

---

## References

Key papers informing this work:

- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. _NeurIPS_.
- Zehlike et al. (2017). FA\*IR: A Fair Top-k Ranking Algorithm. _CIKM_.
- Patro et al. (2022). Fair ranking: a critical review. _FAccT_.
- Balagopalan et al. (2023). The Role of Relevance in Fair Ranking. _SIGIR_.
- Wu et al. (2025). Does RAG Introduce Unfairness in LLMs? _COLING_.
