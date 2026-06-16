# Step 4: Generate Research Queries

**Owner:** Yan-Bo  
**Depends on:** Step 1a must be complete (`qbio_papers.json` must exist)

---

## Goal

Generate 50 diverse research queries covering all q-bio subcategories.
These queries will be used in Step 5 for Top-K semantic retrieval and baseline evaluation,
and later for fairness auditing (RQ1, RQ2, RQ3).

Query diversity is critical: if queries are concentrated in only a few subcategories,
the retrieval results will be unrepresentative and the fairness metrics (SPD, SRR) will be unreliable.

---

## Step 4.0: Understand the q-bio Subcategory Distribution

Before designing queries, we first identify which q-bio category tags exist in our dataset
and how many records are assigned to each tag.

### How to run the distribution check (local machine)

```bash
cd /path/to/CS6200-Project
python3 -c "

import json
from collections import Counter

with open('data/processed/qbio_papers.json', 'r') as f:
    papers = json.load(f)

qbio_cats = []
for paper in papers:
    for cat in paper['categories'].split():
        if cat.startswith('q-bio'):
            qbio_cats.append(cat)

counter = Counter(qbio_cats)
for cat, count in sorted(counter.items()):
    print(f'{cat}: {count:,}')
"
```

### Results (current Kaggle snapshot)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| q-bio | 1,356 | Legacy format — no subcategory tag (older records) |
| q-bio.BM | 6,745 | **Biomolecules** — structure and function of biological molecules (proteins, DNA, RNA) |
| q-bio.CB | 2,451 | **Cell Behavior** — cellular processes, motility, signaling, and development |
| q-bio.GN | 3,835 | **Genomics** — gene expression, genome structure, sequencing, and annotation |
| q-bio.MN | 4,157 | **Molecular Networks** — gene regulatory networks, protein interaction networks, metabolic pathways |
| q-bio.NC | 12,131 | **Neurons and Cognition** — neural computation, brain modeling, sensory systems, learning |
| q-bio.OT | 1,586 | **Other Quantitative Biology** — topics not fitting other subcategories |
| q-bio.PE | 12,999 | **Populations and Evolution** — evolutionary dynamics, population genetics, ecology |
| q-bio.QM | 13,180 | **Quantitative Methods** — mathematical and computational methods applied to biology |
| q-bio.SC | 1,808 | **Subcellular Processes** — organelle function, intracellular transport, cytoskeleton |
| q-bio.TO | 2,618 | **Tissues and Organs** — physiology, organ modeling, morphogenesis |

**Note:** The `q-bio` category uses a legacy format without a specific subcategory tag.
These papers are included in our corpus but excluded from query design because
they cannot be mapped to a specific subcategory.

---

## Query Design Strategy

We use a hybrid allocation strategy for the 50 queries. Larger q-bio subcategories receive
more queries, while smaller subcategories still receive enough queries to ensure meaningful coverage.
This avoids over-concentrating the evaluation on only the largest q-bio areas and helps make
the retrieval results more representative across the full q-bio corpus.

| Subcategory | Category Count | Allocated Queries |
|-------------|----------------|-------------------|
| q-bio.QM | 13,180 | 7 |
| q-bio.PE | 12,999 | 7 |
| q-bio.NC | 12,131 | 6 |
| q-bio.BM | 6,745 | 5 |
| q-bio.MN | 4,157 | 4 |
| q-bio.GN | 3,835 | 4 |
| q-bio.TO | 2,618 | 4 |
| q-bio.CB | 2,451 | 4 |
| q-bio.SC | 1,808 | 5 |
| q-bio.OT | 1,586 | 4 |
| **Total** | **61,511** | **50** |

**Note:** The category counts represent q-bio category assignments, not unique papers.
Since one paper can have multiple q-bio category tags, the total category count (61,511)
can exceed the number of unique papers in the corpus (55,301).

The 50 queries are allocated only across the 10 specific q-bio subcategories,
excluding the legacy `q-bio` tag.

Each query should:
- Be a natural language research question (not a keyword search)
- Be specific enough to retrieve relevant papers
- Cover different aspects within the subcategory

**Example queries:**
- q-bio.NC: "How do neural oscillations contribute to memory consolidation during sleep?"
- q-bio.PE: "What mathematical models describe the spread of antibiotic resistance in bacterial populations?"
- q-bio.QM: "How can stochastic differential equations model gene expression noise?"

---

## Query Generation Methodology

This five-step methodology documents how the 50 queries were produced. It is
written for reuse in the final report's Methodology section.

**1. Determine subcategory distribution.**
We first scanned the full q-bio corpus to count papers per subcategory across
all ten q-bio categories (ranging from 1,586 in q-bio.OT to 13,180 in q-bio.QM).
The 1,356 papers carrying only the legacy `q-bio` tag — which cannot be mapped
to a specific subcategory — were excluded from query design.

**2. Hybrid allocation of query counts.**
We adopted a hybrid allocation strategy rather than strict proportional
allocation. Larger subcategories received more queries (7 each for q-bio.QM and
q-bio.PE, 6 for q-bio.NC), while smaller subcategories retained a minimum
representation (at least 4 queries each). This prevents the evaluation from
over-concentrating on the largest areas while ensuring every subcategory has
enough samples to support later per-subcategory fairness analysis. Final
allocation: QM 7, PE 7, NC 6, BM 5, SC 5, MN 4, GN 4, TO 4, CB 4, OT 4 —
50 queries total.

**3. Draft each query under three principles.**
Each query follows three principles: (i) it is a natural-language research
question, not a keyword search; (ii) it is specific enough to retrieve relevant
papers; and (iii) it covers a distinct aspect within its subcategory to avoid
redundancy. Drafts were produced in one pass with AI assistance, following this
step4.md specification (the distribution, allocation, and principles above)
rather than a standalone prompt.

**4. Manual review and refinement.**
After drafting, each query was reviewed query-by-query by a team member,
focusing on the accuracy of its target subcategory label. Three queries were
refined for category alignment:
- q025: changed from a chromatin-structure question to a protein-DNA
  interaction question (more canonical for q-bio.BM)
- q047: rephrased into a cross-domain version integrating molecular, cellular,
  and environmental factors (better fitting q-bio.OT)
- q049: rephrased into a cross-system comparative question (more appropriate
  for q-bio.OT)

**5. Store in standard JSON format.**
Each query is stored with three fields: `query_id` (e.g., q001), `query_text`
(the natural-language question), and `subcategory` (the target category). The
final set was written to `queries/queries.json` and committed to GitHub for
team use.

---

## Output Schema

Each query is stored as a JSON object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| query_id | str | Unique identifier, e.g. `"q001"` |
| query_text | str | Natural language research question |
| subcategory | str | Target q-bio subcategory, e.g. `"q-bio.NC"` |

### Output file structure

```json
[
  {
    "query_id": "q001",
    "query_text": "How do neural oscillations contribute to memory consolidation during sleep?",
    "subcategory": "q-bio.NC"
  },
  {
    "query_id": "q002",
    "query_text": "What mathematical models describe the spread of antibiotic resistance?",
    "subcategory": "q-bio.PE"
  }
]
```

## Output

- `queries/queries.json` (committed to GitHub — Jici can use this directly after cloning)
- `/kaggle/working/queries.json` (optional Kaggle notebook output)

---

## Next Step

After `queries.json` is complete, Jici proceeds to Step 5:
load the queries, run Top-K retrieval against ChromaDB, and compute baseline retrieval metrics
once the relevance criteria are finalized.
