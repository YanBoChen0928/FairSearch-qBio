# FairSearch-qBio

## Evaluating and Mitigating Institutional Bias in Academic RAG for Quantitative Biology (q-bio) papers on arXiv.

**Course:** CS 6200 Information Retrieval — Northeastern University (Summer 2026)  
**Instructor:** Prof. Shanu Sushmita  
**Team:** Jici Jiang · Raj Lucka · Yan-Bo Chen  
**GitHub:** [github.com/YanBoChen0928/FairSearch-qBio](https://github.com/YanBoChen0928/FairSearch-qBio)

---

## Project Overview

This project audits a Retrieval-Augmented Generation (RAG) system built on the arXiv **q-bio** corpus (~55,300 papers) for **institutional homophily** — the tendency to systematically rank or cite papers from elite universities higher than equally relevant work from non-elite institutions.

We investigate three research questions across the full RAG pipeline:

| RQ                     | Stage               | Question                                                                                                           |
| ---------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **RQ1**                | Retrieval (Step 5b)  | Does semantic vector search exhibit institutional homophily?                                                      |
| **RQ2 (Framework A)**  | Generation (Step 7)  | Does the LLM disproportionately cite elite institutions when generating answers?                                  |
| **RQ2 (Framework B)**  | Generation (Step 7)  | On two-sided debate queries, does the LLM flatten viewpoint diversity present in the retrieved context?           |
| **RQ3**                | Re-ranking (Step 6)  | What is the fairness–utility tradeoff when applying MMR re-ranking?                                               |

---

## Pipeline Architecture

```
Step 1   →  Prepare dataset (55,301 q-bio abstracts; 55,300 after dedup)
Step 1b  →  Enrich institution/region labels via OpenAlex   [Done]
Step 2   →  Embed text with all-MiniLM-L6-v2
Step 3   →  Store vectors in ChromaDB (55,300 records)
Step 4   →  Generate 150 research queries (100 neutral + 50 contradictory)   [Done]
Step 5a  →  Retrieve Top-K + Precision/Recall   ← baseline   [Done]
Step 5b  →  Join labels → SPD, SRR   ← RQ1   [Done]
Step 6   →  Fair MMR re-ranking   ← RQ3 (NDCG@10, MRR, SPD)   [Done]
Step 7a  →  Gemini generation, neutral queries   ← RQ2 Framework A (citation bias)   [Done]
Step 7b  →  Gemini generation, contradictory queries   ← RQ2 Framework B (viewpoint retention)   [Done]
Step 8   →  Evaluate (NDCG@10, MRR, SPD, RAGAS)   [Not started]
Step 9   →  Streamlit diagnostic dashboard   [Not started]
```

---

## Technical Stack

| Component            | Tool                                                            |
| -------------------- | --------------------------------------------------------------- |
| Dataset              | arXiv metadata (Cornell University / Kaggle)                    |
| Embedding model      | `all-MiniLM-L6-v2` (sentence-transformers)                      |
| Vector database      | ChromaDB                                                        |
| Generative LLM       | Google Gemini (`gemini-3.1-flash-lite`; see notes below)         |
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
│   ├── processed/              # Preprocessed metadata (not committed)
│   │   └── qbio_papers.json    # NOT in GitHub — import from Kaggle Dataset
│   └── chroma/                 # ChromaDB index files (not committed)
│
├── queries/
│   └── queries.json            # 50 research queries for the audit
│
├── src/                        # Core modules — PLANNED (current work is notebook-first; see notebooks/)
│   ├── data_loader.py          # Load, preprocess, enrich arXiv metadata
│   ├── index_builder.py        # Build vector embeddings & index in ChromaDB
│   ├── retriever.py            # Query → vector search (Top-K)
│   ├── rerank.py               # Fairness-aware re-ranking (MMR, Fair-Top-K)
│   ├── audit.py                # Bias audit and evaluation scripts (SPD, SRR)
│   ├── metrics.py              # IR metrics (NDCG, MRR) & fairness metrics
│   └── prompt_utils.py         # Helpers for LLM synthesis / prompt engineering
│
├── notebooks/                  # Step-by-step development notebooks (actual filenames)
│   ├── step1-data-prep.ipynb                      # Yan-Bo: filter & clean q-bio papers (55,301)
│   ├── step1b-institution-labels-full-yb.ipynb     # Yan-Bo: OpenAlex institution labeling
│   ├── step2-embedding.ipynb                       # Yan-Bo: embed abstracts with all-MiniLM-L6-v2
│   ├── step3_chromadb.ipynb                        # Raj: store vectors in ChromaDB
│   ├── step5-retrieval-baseline-yb-kaggle-150.ipynb # Jici: Top-K search + Precision/Recall (150 queries)
│   ├── step5b_fairness_audit_optionB-yb.ipynb      # Yan-Bo: SPD/SRR ← RQ1 (authoritative Option B run)
│   ├── step6_reranking.ipynb                       # Jici: Fair MMR / Fair-Top-K ← RQ3
│   ├── step7-rq2-generation-frameworka-yb.ipynb    # Yan-Bo: Gemini generation + citation audit ← RQ2 Framework A
│   └── (step7 Framework B notebook runs on Kaggle as step7_rq2_generation_frameworkb-yb;
│        not yet downloaded into this local folder)
│   # Step 8/9 notebooks not started yet.
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

| Step                                           | Owner  | Status      |
| ---------------------------------------------- | ------ | ----------- |
| Step 1 — Data preparation                      | Yan-Bo | ✅ Done     |
| Step 2 — Embedding (all-MiniLM-L6-v2)          | Yan-Bo | ✅ Done     |
| Step 3 — ChromaDB ingestion                    | Raj    | ✅ Done     |
| Step 4 — Query generation (150: 100 neutral + 50 contradictory) | Yan-Bo | ✅ Done     |
| Step 5 — Baseline retrieval + Precision/Recall | Jici   | ✅ Done     |
| Step 5b — Fairness audit (SPD/SRR) ← RQ1       | Yan-Bo | ✅ Done     |
| Step 6 — Fair MMR re-ranking ← RQ3             | Jici   | ✅ Done     |
| Step 7a — Gemini generation, Framework A ← RQ2 | Yan-Bo | ✅ Done     |
| Step 7b — Gemini generation, Framework B ← RQ2 | Yan-Bo | ✅ Done     |
| Step 8 — Full evaluation (NDCG, MRR, SPD, RAGAS) | TBD    | ⏳ Upcoming |
| Step 9 — Streamlit dashboard                   | TBD    | ⏳ Upcoming |
| Slides (Project Update 1)                      | Yan-Bo | ✅ Done     |
| Report PDF (Project Update 1)                  | Jici   | ✅ Done     |

---

## Key Findings

RQ1, RQ2 (both frameworks), and RQ3 have measured results as of 2026-07-12.
Step 8 (RAGAS + full evaluation) and Step 9 (dashboard) have not started.

**RQ1 — Retrieval-stage institutional bias (Step 5b).** Elite defined as QS
World University Rankings 2026 Top-50. SPD +0.029, SRR 1.28, bootstrap 95% CI
[-0.005, +0.065] crossing zero: a weak elite tilt that is NOT statistically
significant. Consistent with a PCA finding that the embedding model encodes
topic, not institutional origin. See `handoff_status_rq1_for_step6.md` and
`results/rq1_optionB_result.json`.

**RQ2, Framework A — Generation-stage institutional citation bias (Step 7a).**
Neutral queries (q001-q100). Mean amplification (cited elite share minus
context elite share) = +0.0041, bootstrap 95% CI [-0.0254, +0.0342] crossing
zero: NEUTRAL, no confirmed elite citation amplification at generation. Model:
`gemini-3.1-flash-lite` (see model-history note below). See
`rq2_frameworkA_summary.md`.

**RQ2, Framework B — Generation-stage viewpoint-diversity retention (Step 7b).**
Contradictory two-sided debate queries (q101-q150). Among 36/50 queries whose
retrieved context contained evidence for both sides, 35 retained both
viewpoints in the generated answer: retention rate 97.2%, bootstrap 95% CI
[91.7%, 100.0%]. Judge fell back to a self-judge design
(`gemini-3.1-flash-lite`, same model as generation) after the primary judge's
free-tier daily quota was exhausted mid-run; disclosed as a limitation. A
pre-registered 5-query human red-flag check found 2/5 answer-layer judgments
questionable (judged non-systematic, not corrected). This result is reported
descriptively, not as a formal "preserves diversity" verdict. See
`rq2_frameworkB_summary.md`.

**RQ3 — Fairness/utility tradeoff under MMR re-ranking (Step 6, owner: Jici).**
Per `results/rq3_results.json`: institution-aware MMR at λ≈0.9-0.95 reduces SPD
from a baseline 0.0278 to about 0.015-0.02 while NDCG@10 stays essentially flat
(0.8092 → ~0.8096) and MRR is unchanged or slightly higher. Semantic-diversity
MMR trades more NDCG for diversity as λ decreases. Because RQ2 Framework A
found no generation-stage amplification to correct for, the optional "A x RQ3
linkage" (re-running Framework A on RQ3's re-ranked context) was decided
NOT necessary; see `rq2_rq3_linkage_plan.md`.

**Model history note.** The original plan specified Gemini 1.5 Flash. Over the
course of the project, 1.5-series and 2.0/2.5-series models were retired or
became uncallable for this project (404s, zero daily quota, or "no longer
available to new users") before any call was made; `gemini-3.1-flash-lite` was
the model that actually completed all generation runs. Framework B's primary
judge (`gemini-3-flash-preview`) was similarly blocked mid-run by a 20/day free
quota and fell back to the same flash-lite model. Full details in
`rq2_plan.md` (Decision 4) and `rq2_frameworkb_draft.md` (Models section).

- **Baseline retrieval (Update 1):** Mean Precision@10 = 0.654 and HitRate@10 = 0.96 across 50 queries; per-subcategory Precision@10 ranges from 0.97 (q-bio.NC) down to 0.08 (q-bio.OT).

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
3. Run `notebooks/step1_data_prep.ipynb` to extract the 55,301 q-bio papers

Institution labels are enriched via the OpenAlex API where available and cached locally in `data/processed/`, but these generated data files are not committed to GitHub. If needed, they should be shared through Kaggle Datasets.

---

## Local Development

**Working directory (local machine):**

```
/Users/yanbochen/IdeaProjects/CS6200-Project
```

**Quick start (local):**

```bash
# 1. Clone the repo
git clone https://github.com/YanBoChen0928/FairSearch-qBio.git CS6200-Project
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
| I: Foundations  | 3–4   | Naive RAG baseline, Precision & Recall          | ✅     |
| II: Audit       | 5–6   | Institution labeling via OpenAlex               | ✅     |
| II: Audit       | 7–8   | SPD & SRR measurement ← RQ1                     | ✅     |
| III: Mitigation | 9–10  | MMR & Fair-Top-K re-ranking ← RQ3               | ✅     |
| III: Mitigation | 11–12 | Generation-stage bias audit ← RQ2 (A + B) / RAGAS eval | 🔄 RQ2 done; RAGAS (Step 8) not started |
| IV: Conclusion  | 13    | Streamlit dashboard                             | ⏳     |
| IV: Conclusion  | 14    | Final presentation                              | ⏳     |

---

## Possible Future Extensions (not started, not pre-registered)

**Institutional skew within Framework B's Side A / Side B papers.** Framework A
(institution) and Framework B (viewpoint) were deliberately split across two
non-overlapping query sets (100 neutral queries for A, 50 contradictory
queries for B) so that each Framework isolates one axis cleanly. Mixing both
questions on the same debate queries would risk a confound: if Side A's papers
happen to skew more elite than Side B's papers in the underlying corpus (quite
plausible), then an observed "answer favors Side A" result becomes impossible
to attribute cleanly to a substantive-position preference versus an
elite-institution preference. This is why B's design note in `rq2_plan.md`
states B's retention metric "does NOT depend on institutional bias" and stands
on its own regardless of RQ1/A's results.

A possible follow-up: after Framework B's retention/favor results are already
final (as they are now), separately compute the elite share of Side A's cited
papers vs Side B's cited papers within the 36 eligible debate queries, purely
as a descriptive check of whether one side's literature happens to be more
institutionally elite than the other's. This would be reported ALONGSIDE the
existing retention_rate finding, never merged into it or used to revise it,
to avoid retroactively contaminating an already pre-registered, completed
metric. Not started; would need its own pre-registration if pursued.

---

## References

Key papers informing this work:

- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. _NeurIPS_.
- Zehlike et al. (2017). FA\*IR: A Fair Top-k Ranking Algorithm. _CIKM_.
- Patro et al. (2022). Fair ranking: a critical review. _FAccT_.
- Balagopalan et al. (2023). The Role of Relevance in Fair Ranking. _SIGIR_.
- Wu et al. (2025). Does RAG Introduce Unfairness in LLMs? _COLING_.
