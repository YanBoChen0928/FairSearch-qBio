# Step 1 — Data Preparation & Team Collaboration Strategy

## Overall Idea

```text
Raw data (4GB)             Intermediate outputs              Team collaboration
────────────────           ──────────────                    ──────────────
arXiv snapshot      →      qbio_papers.json          →       Kaggle Dataset
(already available         (generated in Step 1)             (created by the step owner, imported by all three members)
on Kaggle)

                    →      embeddings                →       Kaggle Dataset
                           (generated in Step 2)             (created by the step owner, imported by all three members)

                    →      ChromaDB index            →       Kaggle Dataset
                           (generated in Step 3)             (created by the step owner, imported by all three members)
```

GitHub should only store the code. No data should be pushed to GitHub.

---

## Specific Workflow Plan

For Step 1, Yan-Bo only needs to generate and publish `qbio_papers.json` once, and then the rest of the team can import it from Kaggle.

**After finishing Step 1:**

- Save the output file `qbio_papers.json` as a private Kaggle Dataset.
- Name it something like `fairsearch-qbio-processed`.
- Invite Jici and Raj as collaborators.

**After finishing Step 2:**

- Save the embedding output as a Kaggle Dataset if needed.
- Name it something like `fairsearch-qbio-embeddings`.
- Invite the team members as collaborators.

**After finishing Step 3:**

- Save the ChromaDB index as a Kaggle Dataset.
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
data/raw/*
!data/raw/.gitkeep

# Processed data (shared through Kaggle Dataset instead)
data/processed/*
!data/processed/.gitkeep

# ChromaDB index
data/chroma/*
!data/chroma/.gitkeep

# ChromaDB / SQLite files
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

All real data files inside `data/processed/` should be ignored, except for `.gitkeep`, because the JSON file should be shared through Kaggle Dataset instead.

---

## Repository Folder Structure & `.gitkeep`

Git does not track empty folders. To make sure all team members get the correct
folder structure after `git clone`, each folder contains an empty placeholder file
called `.gitkeep`.

**What `.gitkeep` is:**
- A completely empty file with no content.
- Its only purpose is to make Git "see" the folder so it gets committed.
- The name is a community convention — Git has no built-in knowledge of it.

**Current folder structure committed to the repo:**

```
data/
├── raw/           ← .gitkeep (actual raw data is NOT committed)
├── processed/     ← .gitkeep (actual JSON data is NOT committed)
└── chroma/        ← .gitkeep (ChromaDB index is NOT committed)
src/               ← .gitkeep (Python modules go here)
notebooks/         ← .gitkeep (Kaggle notebooks go here)
app/               ← .gitkeep (Streamlit dashboard goes here)
```

**For team members after `git clone`:**

You do not need to do anything special. All folders will already exist on your machine.
Just place the correct data files inside them as described in the workflow plan above.
Do NOT delete or commit the `.gitkeep` files — they are harmless and necessary.
