# Step 1 — Data Preparation & Team Collaboration Strategy

## Overall Idea

```text
Raw data (4GB)             Intermediate outputs              Team collaboration
────────────────           ──────────────                    ──────────────
arXiv snapshot      →      qbio_papers.json          →       Kaggle Dataset
(already available         (generated in Step 1)             (created by Yan-Bo, imported by all three members)
on Kaggle)

                    →      embeddings (ChromaDB)     →       Kaggle Dataset
                           (generated in Step 2)             (created by Yan-Bo, imported by all three members)
```

GitHub should only store the code. No data should be pushed to GitHub.

---

## Specific Workflow Plan

You (Yan-Bo) only need to do this once, and then the rest of the team can follow along.

**After finishing Step 1:**

- Save the output file `qbio_papers.json` as a private Kaggle Dataset.
- Name it something like `fairsearch-qbio-processed`.
- Invite Jici and Raj as collaborators.

**After finishing Step 2:**

- Save the ChromaDB index as another Kaggle Dataset.
- Name it something like `fairsearch-qbio-chromadb`.
- Invite the team members as collaborators as well.

**When team members use it:**

- They can import this Dataset into their own Notebook.
- The file path will become:

```text
/kaggle/input/fairsearch-qbio-processed/qbio_papers.json
```

---

## Corresponding `.gitignore` Rules

Based on this strategy, the files and folders that `.gitignore` should block are very clear:

```gitignore
# Raw data
data/raw/

# Processed data (shared through Kaggle Dataset instead)
data/processed/

# ChromaDB index
data/chroma/
*.sqlite3

# Python
__pycache__/
*.pyc
.env

# Jupyter
.ipynb_checkpoints/

# macOS
.DS_Store
```

The entire `data/processed/` folder should be ignored because the JSON file,
regardless of size, should be shared through Kaggle Dataset instead.
