# Step 1b (Option B) — Summary

**What this documents:** how we rebuilt institution labeling the "Option B" way,
the final method, the measured results, and the traps we hit (so nobody repeats
them). All numbers here are MEASURED unless explicitly marked as preview.

Working notebook: `notebooks/step1b_institution_labels_full-yb.ipynb`
Date: 2026-07-08

---

## 1. Why Option B

The v1 approach tried to label the whole ~55,300-paper corpus via OpenAlex. It
failed two ways:

- **Coverage:** ~82% of papers came back not_found; only ~17% of the retrieved
  set was usable. The 150-query RQ1 result was underpowered (SPD +0.061,
  binomial p = 0.069).
- **Biased baseline:** the labeled subset over-represented elite institutions
  (they are easier for OpenAlex to match cleanly), so the corpus base rate
  (0.233) was inflated. Comparing the retrieved set against an inflated baseline
  understates the true gap.

**Option B** fixes both at once: do NOT label the whole corpus. Instead label
two small sets with ONE identical method:

1. a random ~1000-paper baseline sample of the corpus (unbiased base rate)
2. the retrieved set (deduped) from Step 5a

Then SPD = retrieved_share − sample_share. Same labeler on both sides is the
whole point.

---

## 2. Final method (same on both sides)

Institution labeling via OpenAlex, queried in BATCHES of 50 ids per request
(OpenAlex OR-syntax with the pipe `|`), authenticated with a personal API key:

1. **Primary lookup** — filter by `locations.landing_page_url` =
   `http://arxiv.org/abs/<id>` (note: http, not https).
2. **DOI fallback** — for ids not returned by the primary batch, retry by DOI
   `10.48550/arXiv.<id>`, also in batches of 50.
3. **Map result back to arXiv id** — OpenAlex does NOT expose `ids.arxiv`, so we
   parse `arxiv.org/abs/<id>` out of each work's landing_page_url list.
4. **Elite match** — first author's institution display name, exact
   case-insensitive match against the QS World University Rankings 2026 Top-50
   list (`data/qs_top50_elite_2026.json`).
5. **Coverage states** — found / no_affiliation / not_found. `null` (no
   affiliation) is excluded from SPD/SRR.

Batching drops ~1000 papers from ~2000 single requests to ~20-40 batch requests:
finishes in seconds and stays far inside the free daily API budget.

---

## 3. The two labeling runs (Cell 4 and Cell 8)

Cell 4 labels the random baseline sample. Cell 8 labels the retrieved set. They
run the SAME labeler; the only difference is the input set. This is what makes
SPD a fair comparison.

```
   CELL 4                                    CELL 8
   Random baseline sample                    Retrieval set
   1000 papers (seed=42)                     1500 slots -> dedup -> 1366 unique
        |                                          |
        |            === SAME METHOD ===           |
        |   OpenAlex batched (50 ids / request)    |
        |   1) primary: landing_page_url (http)    |
        |   2) DOI fallback: 10.48550/arXiv.<id>   |
        |   match: QS Top-50 2026, null excluded   |
        v                                          v
   coverage:                                  coverage:
     found  438 (44%)                           found  798 (58%)
     no_aff 541                                 no_aff 553
     not_fnd 21 (2%)                            not_fnd 15 (1%)
        |                                          |
        v                                          v
   sample_share (baseline)                    retrieved_share
     63 / 438 = 0.144                           141 / 798 = 0.177
        \                                         /
         \                                       /
          v                                     v
     SPD = retrieved_share - sample_share = 0.177 - 0.144 = +0.033
     (PREVIEW only; CI + binomial + SRR computed in Step 5b)
```

**Why the retrieved set has higher coverage (58% vs 44%):** retrieved papers
tend to be more mainstream / more cited, and such papers are more likely to have
affiliation data in OpenAlex. This is expected, not an error.

---

## 4. Measured results (all MEASURED, 2026-07-08)

**Baseline sample (Cell 4, n = 1000, seed 42):**
- coverage: found 438 (44%), no_affiliation 541 (54%), not_found 21 (2%)
- by id format: new 921 -> found 41%; old 79 -> found 75%
- sample_share (baseline elite rate) = 63 / 438 = **0.144**

**Retrieved set (Cell 8, 1366 unique papers):**
- 150 queries x 10 = 1500 slots -> deduped to 1366 unique
- coverage: found 798 (58%), no_affiliation 553, not_found 15 (1%)
- retrieved_share = 141 / 798 = **0.177**

**SPD preview = 0.177 - 0.144 = +0.033** (preview only)

Comparison to v1:
- v1 biased baseline was 0.233; the unbiased Option B baseline is 0.144. This
  confirms v1 over-stated the elite base rate.
- not_found dropped from ~82% (v1) to ~2% (http fix + DOI fallback).

---

## 5. How to read +0.033 (do NOT overstate)

The clean Option B SPD preview (+0.033) is SMALLER than v1's +0.061 and much
smaller than any earlier hypothetical figure. This is not a problem; it is the
honest answer.

Why smaller: v1's larger gap was partly an artifact of measuring the two sides
with different / biased labeling. When both sides are measured with the SAME
clean ruler, the real gap is smaller (retrieved 0.177 vs baseline 0.144).

Important limits:
- +0.033 is a point estimate with NO significance test yet. Given how small it
  is, the 95% CI may well cross zero (i.e. not significant).
- The authoritative SPD (with CI and binomial test) and SRR are computed in
  Step 5b, not here. Do NOT cite +0.033 as a finding, and do NOT substitute the
  older 0.061 or any hypothetical number to make it look larger.
- A fair-audit result of "direction present but small / possibly not
  significant" is a valid, publishable finding. The value is the clean method,
  not a large gap.

---

## 6. Traps we hit (so nobody repeats them)

**http vs https.** OpenAlex stores the arXiv landing page as
`http://arxiv.org/abs/<id>` (http). Querying https matched nothing. Fixing to
http made the primary lookup work.

**Rate limiting (429).** Per-paper looping (~2000 requests) hit 429 Too Many
Requests near the end of a 1000-run, silently turning real papers into
not_found. Two root causes:
- OpenAlex changed to credit-based limits; without an API key you share a tiny
  pool (and on Kaggle that pool is shared across the whole Kaggle IP).
- Switching email (mailto) did NOT help, because the limit was tied to the
  shared IP, not the email.

**Fix = API key + batching (both).**
- API key: OpenAlex now recommends/expects a key. Free key gives $1/day budget
  (~10,000 credits; a filtered list = 1 credit). Enough for our whole 1b.
- Batching (50 ids/request via OR-syntax) cuts requests ~50x, so we stay far
  inside budget and never trip the per-second limit.

**ids.arxiv is null.** Do not map batch results back by `ids.arxiv` (always
None). Parse the arXiv id out of the landing_page_url list instead.

**Wrong retrieval_results.json (50 vs 150).** The local
`data/processed/retrieval_results.json` was an OLD 50-query file. The real
150-query output lived only in the Kaggle output of
`step5-retrieval-baseline-yb-kaggle-150`. Always verify query count
(`len(...) == 150`) before labeling the retrieved set.

**Kaggle dataset versions don't auto-update.** After uploading a new dataset
version, the notebook keeps using the old version until you re-add / update the
input. Re-add the input, then confirm the loaded data (e.g. queries: 150).

---

## 7. How to set up the OpenAlex API key (for reproducibility)

1. Create a free account at openalex.org (Sign in / Sign up, ~30 sec).
2. Go to `openalex.org/settings/api` and copy your API key.
3. On Kaggle, store it as a Secret (do NOT paste it into code):
   Add-ons -> Secrets -> Add secret, Label = `OPENALEX_API_KEY`, Value = the key.
   Make sure the secret is attached/authorized for the notebook.
4. In the notebook, read it and pass it as a request param:
   ```python
   from kaggle_secrets import UserSecretsClient
   OPENALEX_API_KEY = UserSecretsClient().get_secret("OPENALEX_API_KEY")
   # ... then in each request: params={"api_key": OPENALEX_API_KEY, ...}
   ```
Free budget resets daily (UTC midnight). Our full 1b run costs only a few
credits, so it stays free.

---

## 8. Outputs and next step

Two label files (the deliverables of 1b), consumed by Step 5b:
- `sample_labels_1000.json` — baseline sample, sample_share 0.144
- `retrieval_labels.json` — retrieved set, retrieved_share 0.177

**Next:** upload both as one Kaggle dataset (e.g. `fairsearch-qbio-1b-labels`),
then Step 5b reads them to compute the authoritative SPD (with CI + binomial)
and SRR. Step 5b is where RQ1 is actually answered; 1b only produced the labels.
