# Data Dictionary — `data/`

This file explains the four JSON files in `data/` used by the RQ1 fairness
audit (Step 1b labeling + Step 5b audit). All shares are MEASURED
(2026-07-08), not hypothetical.

Quick map:

| File | Role | Key number |
|------|------|-----------|
| `qs_top50_elite_2026.json` | Elite institution list (ground truth for "elite") | 50 schools |
| `sample_labels_1000.json` | Option B baseline: random corpus sample, labeled | sample_elite_share = 0.144 |
| `retrieval_labels.json` | Option B retrieved set, labeled (same method) | retrieved_share = 0.177 |
| `retrieval_results.json` | Step 5a output: top-10 papers per query | 150 queries |

RQ1 headline: SPD = retrieved_share - sample_share = 0.177 - 0.144 = +0.033
(preview; CI + significance computed in Step 5b).

---

## 1. `qs_top50_elite_2026.json` — the elite list

What it is: the definition of "elite institution" for this project. A paper is
labeled elite if its first author's institution matches one of these names.

Source: QS World University Rankings 2026, Top 50.
Structure: a list of 50 objects.

```json
[
  {"rank": 1, "name": "Massachusetts Institute of Technology", "country": "US"},
  {"rank": 2, "name": "Imperial College London", "country": "GB"}
]
```

Fields: `rank` (1-50), `name` (exact display name, matched case-insensitively
against OpenAlex), `country` (ISO 2-letter code).

Note: threshold is Top-50 (not Top-100). Matching is exact on display name.

---

## 2. `sample_labels_1000.json` — Option B baseline (the "normal" rate)

What it is: a random sample of 1000 corpus papers, labeled for institution.
This answers "what does the bookshelf normally look like?" It is the reference
point (baseline) that the retrieved set is compared against.

Why it exists: you cannot label all ~55,300 papers (v1 tried and failed: ~82%
not found, and the labeled subset was biased toward elite institutions). A
random sample gives an UNBIASED estimate of the true elite base rate.

Structure: a dict with two keys, `meta` and `labels`.

`meta` (summary numbers, already computed):
```json
{
  "role": "option_b_baseline_sample",
  "sample_n": 1000,
  "random_seed": 42,
  "elite_list": "QS World University Rankings 2026 Top 50",
  "coverage": {"found": 438, "no_affiliation": 541, "not_found": 21},
  "elite_found": 63,
  "sample_elite_share": 0.1438
}
```

`labels` (list of 1000 per-paper records):
```json
{
  "coverage": "found",
  "institution": "Cold Spring Harbor Laboratory",
  "country": "US",
  "matched_by": "landing_page_url",
  "paper_id": "1301.7745",
  "id_format": "new",
  "elite_label": 0
}
```

Field meanings:
- `coverage`: `found` / `no_affiliation` / `not_found`. Only `found` papers have
  an `elite_label`. The other two are EXCLUDED from the share.
- `institution`, `country`: first author's affiliation (null if not found).
- `matched_by`: `landing_page_url` (primary) or `doi` (fallback).
- `paper_id`: arXiv id.
- `id_format`: `new` or `old` arXiv id style.
- `elite_label`: 1 = elite (in QS Top-50), 0 = not elite. Absent if not found.

Headline: elite share = 63 / 438 (found only) = 0.144.

---

## 3. `retrieval_labels.json` — Option B retrieved set (what the system did)

What it is: every unique paper the search system actually returned across all
150 queries (top-10 each, deduped to 1366 unique), labeled with the SAME method
as the baseline. This answers "what did the system actually pick?"

The "same method" rule is the whole point of Option B: baseline and retrieved
set are measured with one identical ruler, so any gap is a real gap, not an
artifact of two different labeling methods (that was v1's mistake).

Structure: identical to `sample_labels_1000.json` (a `meta` + `labels` dict).

`meta`:
```json
{
  "role": "option_b_retrieved_set",
  "unique_retrieved": 1366,
  "elite_list": "QS World University Rankings 2026 Top 50",
  "coverage": {"found": 798, "no_affiliation": 553, "not_found": 15},
  "elite_found": 141,
  "retrieved_share": 0.1767
}
```

`labels`: same per-paper record shape as file #2.

Headline: elite share = 141 / 798 (found only) = 0.177.

Why coverage is higher here (798/1366 = 58%) than in the baseline (438/1000 =
44%): retrieved papers tend to be more mainstream / more cited, and such papers
are more likely to have affiliation data in OpenAlex. This is expected, not an
error.

---

## 4. `retrieval_results.json` — Step 5a output (raw retrieval)

What it is: the raw output of the retrieval step. For each of the 150 queries,
it stores the top-10 papers the system returned plus per-query quality metrics.
This is the SOURCE that `retrieval_labels.json` was built from (its unique paper
ids were sent to the labeler). Step 5b also reads this to group results per
query for the bootstrap confidence interval.

Structure: a list of 150 objects, one per query.

```json
{
  "query_id": "q001",
  "query_text": "...",
  "subcategory": "q-bio.NC",
  "type": "neutral",
  "retrieved_paper_ids": ["...", "..."],
  "relevance": [1, 0, ...],
  "precision_at_10": 0.4,
  "recall_at_10": null,
  "hit_rate_at_10": 1
}
```

Field meanings:
- `query_id`: q001-q150.
- `type`: `neutral` (q001-q100) or `contradictory` (q101-q150). The MAIN RQ1
  audit uses neutral only; contradictory is held out for RQ2.
- `retrieved_paper_ids`: the 10 returned arXiv ids (rank order).
- `relevance`: 0/1 per rank (subcategory-match proxy). Null for contradictory.
- `precision_at_10` etc.: per-query quality; null for contradictory queries.

Important: this is the corrected 150-query file. An earlier 50-query file with
the same name once lived in `data/processed/` and caused confusion; it has been
removed. Always verify `len(...) == 150` before using.

---

## Why we design it this way (plain-language)

The question we ask:
"When the system picks the top-10, does it favor elite schools MORE than the
bookshelf normally has?"

To answer that, we need TWO numbers to compare.

```
  [ How much elite is NORMAL? ]      [ How much elite did the SYSTEM pick? ]
   we can't label all 55k              we label everything the system
   (too big, and labeling all          returned across 150 queries
    of it turned out biased)                     |
            |                                     |
   so we scoop a random 1000            1366 unique papers
   = a fair "taste" of the pot                   |
            |                                     |
   sample_labels_1000.json             retrieval_labels.json
   normal rate = 14.4%                 system rate = 17.7%
            \                                    /
             \                                  /
              the GAP = 17.7% - 14.4% = +3.3%
              = how much the system leans elite
              (small, honest; is it real? -> Step 5b tests it)
```

Two design choices, in plain words:

1. We taste, not drink the whole pot. 1000 random papers represent 55k, the
   same way a national poll of ~1000 people represents millions. Accuracy comes
   from the SAMPLE size, not the corpus size. (Caveat: only 438 of the 1000 had
   a findable affiliation, so the real basis is 438 papers with a 95% margin of
   about +/-3%. The honest limitation to disclose is not "too few papers" but
   "only 44% were findable, and those 44% may not perfectly represent all.")
2. We use ONE ruler on both sides. Same labeling method for the sample and the
   retrieved set, so the gap is a real gap, not a measuring trick. (Using two
   different rulers was v1's mistake, which produced a fake larger gap.)

---

## How the four files connect (RQ1 in one line)

```
qs_top50_elite_2026.json  ---defines "elite"--->  used by the labeler
                                                        |
retrieval_results.json  ---unique ids--->  retrieval_labels.json (0.177)
                                                        |
random sample of corpus  ------------->  sample_labels_1000.json (0.144)
                                                        |
                          SPD = 0.177 - 0.144 = +0.033 (preview)
                          CI + significance -> computed in Step 5b
```

Reminder: +0.033 is a small, honest gap. Do not substitute the older v1 figure
(0.061) or any hypothetical number to make it look larger. The value of this
project is the clean method, not a large gap.
