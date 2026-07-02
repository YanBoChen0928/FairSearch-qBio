# Step 1b-v2: Institution Labeling Redesign

Status: design draft for team review. No code is run yet. We choose between
Option A and Option B after the 150-query re-run (see "Decision criteria").

## 1. Why a v2 is needed

Step 1b-v1 (Raj) faithfully implemented the original design: enrich the whole
q-bio corpus with author affiliations via OpenAlex, assign an elite label, and
join to retrieval results by `paper_id`. The execution is correct; the design
has three weaknesses we discovered while auditing:

1. Low coverage. Only 7,061 of 55,300 papers (12.8%) received an affiliation.
   In the Step 5b audit, only 95 of 500 retrieval slots (19%) were labeled, so
   the fairness test had very little statistical power (SPD +0.041, SRR 1.243,
   p = 0.333, not significant).
2. Biased baseline. The corpus elite base rate (23.3%) was computed over the
   7,061 papers OpenAlex happened to cover. That subset is not random: it skews
   toward well-indexed, larger, English-language institutions.
3. Directional source bias. OpenAlex affiliation coverage is known to be lower
   for less-visible / Global South / non-English institutions. This gap runs in
   the same direction as the elite vs non-elite axis we are trying to measure,
   so it can distort the elite share itself, not just shrink the sample.

## 2. Confirmed facts from v1 (do not re-derive)

Label file: Kaggle `rajlucka/fairsearch-qbio-institution-labels`
(`qbio_institution_labels.json`), a local copy is in `data/raj_step1b/`.

- Schema: `paper_id`, `elite_label` (1 = elite, 0 = other, NaN = unlabeled),
  `institution` (OpenAlex display name), `region` (ISO country code), `coverage`.
- `coverage` has three states: `found` (7,061), `no_affiliation` (2,870),
  `not_found` (45,369). Labeled = 7,061; unlabeled = 48,239.
- Label counts: elite 1,643, other 5,418, unlabeled 48,239.
- Elite threshold: QS Top-50. Verified from the data: exactly 43 distinct
  institutions carry `elite_label = 1`, all top-50 caliber (Harvard, MIT,
  Cambridge, ETH Zurich, NUS, Tsinghua, etc.), with no rank 70-100 schools
  present. This is consistent with a ~50-university list, not Top-100.
- The v1 lookup method used title-based search (inferred from the shape of the
  coverage split: not_found >> no_affiliation). The exact query and matching
  rule live only in Raj's Kaggle notebook, which was committed empty to the repo.

## 3. Option A (1b-v2a): ID-first enrichment of the full corpus

Goal: keep the same "label the whole corpus" paradigm, but raise coverage by
fixing the lookup, so Step 5b stays unchanged.

Lookup strategy (in priority order):
1. Primary: arXiv id -> DOI form `10.48550/arXiv.{paper_id}`, then
   `GET /works/https://doi.org/10.48550/arXiv.{paper_id}` on OpenAlex. This is a
   precise key and should reduce `not_found` sharply versus title search.
2. Fallback 1: for works still not found, title search (this reproduces v1).
3. Fallback 2 (optional): Semantic Scholar, which accepts arXiv ids directly and
   returns author affiliations, to fill records OpenAlex lacks.

Mandatory pilot before any full run:
- Run the lookup on a random 500-paper sample.
- Report the new `found / no_affiliation / not_found` split.
- Decision gate: proceed to full run only if the "has affiliation" rate improves
  meaningfully over 12.8%. If it only reaches ~20%, a full re-run is not worth it.

Output and schema: identical to v1 (`paper_id, elite_label, institution, region,
coverage`), so Jici's Step 5b code does not change. Reuse the same QS Top-50 list.

Deliverables (all committed to the repo, unlike v1):
- `notebooks/step1b_institution_labels.ipynb` with the real code.
- `data/raj_step1b/qs_top50_elite.json` (the elite list itself).
- New labels + a v1-vs-v2 coverage comparison table.

Pros: smallest change; 5b untouched; low risk.
Cons: still inherits OpenAlex's directional affiliation bias; the biased-baseline
problem (weakness 2) is not fixed; affiliation ceiling for preprints may stay low
even with id-first lookup, because arXiv preprints often carry no structured
affiliation in OpenAlex at all.

## 4. Option B (1b-v2b): two-sample clean design

Goal: stop trying to label all 55,300 papers. Label only what the fairness
metrics actually need, with one consistent method, to remove both the coverage
bottleneck and the biased baseline.

Two separate samples, two purposes:
1. Baseline sample (query-independent): draw a random sample of the corpus
   (target ~1,000 papers), label each. This gives an unbiased estimate of the
   corpus elite share, with a confidence interval. This replaces the biased
   7,061-paper baseline. It can be built now, before any query run.
2. Retrieved set (query-dependent): after Step 5a runs the (expanded) queries,
   take every retrieved paper across all top-K lists and label each. This gives
   the retrieved elite share. Because we label the full retrieved set, coverage
   on the numerator approaches 100%.

Labeling method (must be identical for both samples):
- Preferred: extract the affiliation from the paper's own first page (arXiv PDF
  or LaTeX source), which partly escapes third-party database bias, then apply
  the same QS Top-50 matching. Spot-check a subset by hand.
- Consistency rule: both samples use the same method and the same elite list.
  Never mix (e.g. OpenAlex for one, manual for the other), or the numerator and
  denominator would be measured on different rulers.

Metric computation (Step 5b):
- SPD = retrieved_elite_share - baseline_elite_share.
- SRR = (retrieved elite rate / retrieved other rate) normalized by the baseline
  rates. Report bootstrap CIs and a significance test, as in v1.

Design changes this implies (needs team alignment):
- Step 1b becomes "label a random baseline sample," not "label the full corpus."
- Step 5b changes its baseline source (random sample, not the 7,061 subset) and
  its numerator source (label the retrieved set directly, not a join to a sparse
  corpus-wide table).

Pros: removes the coverage bottleneck; baseline is unbiased; smallest possible
directional bias; fully reproducible; matches the "no fabricated numbers" rule.
Cons: higher effort per paper (careful extraction), and it changes 1b/5b, so Raj
and Jici must agree before we adopt it.

## 5. Decision criteria (decide after the 150-query re-run)

Run the expanded query set through Step 5a/5b using v1 labels first, then read
three numbers before choosing A or B:
1. SPD direction and size: is it clearly > 0, or hugging 0?
2. CI: does the confidence interval still cross 0 (still inconclusive)?
3. Coverage: is the labeled-slot rate still stuck near 19%?

- If SPD is clearly > 0 with a CI that excludes 0 -> query expansion was enough;
  keep v1 labels, no 1b redo needed.
- If SPD hugs 0, the CI still crosses 0, and coverage is still ~19% -> the
  bottleneck is coverage, not query count -> redo 1b. Prefer Option B if time
  allows (it also fixes the baseline); use Option A if we need the smallest change.

## 6. Open items / team alignment

- Confirm with Raj: exact v1 OpenAlex query field and elite matching rule, and
  ask him to commit the real notebook + elite list.
- Team decision: adopt A or B (only after the 150-query numbers are in).
- Methodology note to write regardless of choice: OpenAlex affiliation coverage
  is lower for non-elite / non-English institutions; acknowledge this as a
  limitation that runs in the same direction as RQ1.
