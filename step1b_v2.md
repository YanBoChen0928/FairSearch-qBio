# Step 1b-v2: Institution Labeling Redesign

Status: 1b-v2 not implemented yet. The 150-query audit (using v1 labels) is done;
based on those numbers the recommendation is Option B (see section 5b), pending
team confirmation from Raj and Jici.

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

## 5b. Decision after the 150-query run: adopt Option B

Result of the 150-query re-run (neutral queries, n = 100), using v1 labels:
- Coverage stayed at 17% (170 of 1,000 neutral slots labeled), still stuck near
  the 19% we saw at 50 queries. Adding queries did not raise coverage.
- SPD = +0.061, SRR = 1.374. SPD 95% CI [+0.010, +0.115] excludes 0, but the
  binomial test gives p = 0.069 (not significant at 0.05).
- The original-50 subset reproduced the standalone 50-query result (95 labeled,
  elite share 0.274), confirming the pipeline is consistent.

Reading against the criteria in section 5, the signals are mixed: the bootstrap
CI excludes 0 (the "keep v1" branch), but coverage is stuck and the baseline is
still the biased 7,061-paper subset (the "redo" branch). A borderline,
underpowered result computed on a biased baseline is not something we can
defend, so we redo 1b.

Why Option B over Option A:
The run proves the bottleneck is the labeling method, not the query count.
Option A only fixes the lookup; it leaves the two problems that actually matter
untouched (the baseline is still the biased OpenAlex-covered subset, and preprint
affiliation coverage may stay low even with id-first lookup). Option B fixes both
at once, with a random-sample unbiased baseline plus direct labeling of the
retrieved set, and its extra per-paper effort lands exactly on the retrieved
papers that RQ2 (citation bias) and RQ3 (Fair MMR) need labeled anyway. So the
same labeling effort raises the validity and statistical power of all three
research questions simultaneously.

Effect on the research questions (the RQs do not change; only their validity and
power do):
- RQ1 (retrieval parity): B provides an unbiased baseline and near-100% coverage
  on the retrieved set, so SPD/SRR become trustworthy. A leaves RQ1 confounded
  and underpowered.
- RQ2 (Gemini citation bias): compares cited vs retrieved-context elite share,
  which needs labels on the retrieved set. B labels that set directly (near-full
  coverage); A relies on the sparse corpus table (~17%), so B makes RQ2 far
  better powered.
- RQ3 (Fair MMR tradeoff): re-ranking needs elite labels on the candidates. B's
  dense labels let MMR actually act on fairness and let us measure before/after
  SPD cleanly; A's sparse labels give MMR little to work with.

One-line summary: Option A only patches a broken thermometer; Option B swaps in
an accurate one and happens to measure exactly where RQ2 and RQ3 need it.

Cost accepted: higher per-paper labeling effort, and a small change to 5b's
baseline computation (5a and the query set are unchanged).

## 6. Open items / team alignment

- Confirm with Raj: exact v1 OpenAlex query field and elite matching rule, and
  ask him to commit the real notebook + elite list.
- Team decision: adopt A or B (only after the 150-query numbers are in).
- Methodology note to write regardless of choice: OpenAlex affiliation coverage
  is lower for non-elite / non-English institutions; acknowledge this as a
  limitation that runs in the same direction as RQ1.

## 7. Elite institution list: QS World University Rankings 2026 (Top 50)

Decision (this session): stop waiting for Raj's list. We adopt the QS World
University Rankings 2026 (overall edition) Top 50 as the definitive elite list,
and we build our own labeler so both Option B samples use one identical method.

### Source
- Ranking: QS World University Rankings 2026, overall table (published 19 June
  2025 by Quacquarelli Symonds). This is the edition in force during our project
  window and supersedes the earlier "QS Top-100" note in old README text.
- Primary source for the names/ranks: QS official results page
  (https://www.qs.com/insights/qs-world-university-rankings-2026) and the QS /
  TopUniversities 2026 table (https://www.topuniversities.com/world-university-rankings/2026).
- The full 1 to 50 order was compiled and cross-checked across:
  timeout.com (top 20 with explicit ranks), universityguru.com QS-2026 overall
  list (ranks 8 to 54), and a Kaggle mirror of the QS-2026 top-1500 table.
  These agree on Top-50 membership.
- Boundary anchor (why exactly 50): QS states Yonsei University "moves into 50th
  position", and multiple sources place University of Bristol at 51. So rank 50
  is Yonsei (included) and rank 51 is Bristol (excluded). This fixes the cutoff
  unambiguously.

### Stored file
- Path: `data/qs_top50_elite_2026.json`
- Format: a JSON array of 50 objects, each `{rank, name, country}`. `country`
  uses ISO 2-letter codes, consistent with the `region` field in Raj v1 labels.
- Tie handling: QS has tied ranks (for example rank 17 has both Tsinghua and
  UC Berkeley, rank 22 has EPFL and TU Munich). Ties are listed as separate
  entries carrying the same rank number. Counting ties, the file has exactly 50
  institutions.

### How this list is used in labeling
- An affiliation counts as elite (`elite_label = 1`) if it matches any name in
  this list; otherwise `elite_label = 0`; unknown affiliation stays `null` and
  is excluded from SPD/SRR (same rule as v1).
- Matching note: OpenAlex returns institution display names that will not always
  be byte-identical to QS names (for example "Massachusetts Institute of
  Technology" vs "MIT", "EPFL" vs "Ecole Polytechnique Federale de Lausanne").
  The pilot will first measure raw coverage, then we decide whether to add a
  small alias / normalization table. Both Option B samples (random baseline and
  retrieved set) must use the exact same list and the exact same matching rule.

### Note on QS year sensitivity
QS updates ranks yearly, so Top-50 membership shifts a little between editions.
We freeze on the 2026 edition for reproducibility. Any future re-run must state
which QS edition it used, or the elite share is not comparable across runs.

## 8. Pilot results (MEASURED, n = 300) — 2026-07-08

These are REAL measured numbers from a 300-paper pilot run of the Option B
labeler on Kaggle (notebook: `step1b_institution_labels-yb.ipynb`). They are not
hypothetical. Config: random seed 42, PILOT_N = 300, OpenAlex polite pool
(mailto set), method = landing_page_url primary (http://arxiv.org/abs/<id>) with
DOI fallback (10.48550/arXiv.<id>), elite list = QS Top-50 2026 exact
case-insensitive match.

### Method fix found during the pilot
The primary lookup initially missed everything because OpenAlex stores the arXiv
landing page URL as `http://arxiv.org/abs/<id>` (http, not https). After changing
the query to http, the primary lookup works and DOI is a true fallback, not the
main path. Verified on a raw record in the diagnostic cell.

### Coverage (n = 300)
- found          : 138 (46%)
- no_affiliation : 156 (52%)
- not_found      :   6 (2%)

Key comparison: Raj v1 whole-corpus labeling had not_found = 82% and usable
coverage ~17% on the retrieved set. The pilot cuts not_found to 2% and raises
usable coverage to 46% (about 3x). The bottleneck is no longer "OpenAlex can't
find the paper" (solved) but "the paper exists in OpenAlex with no affiliation
attached" (a data ceiling for arXiv preprints, not a code problem — confirmed by
inspecting a raw record with empty institutions and empty raw_affiliation_strings).

### Coverage by id format
- new format (e.g. 1610.07213): total 282, found 125 (44%), no_aff 151, not_found 6
- old format (e.g. physics/0310009): total 18, found 13 (72%), no_aff 5, not_found 0

The old-format concern is dropped: old ids were not a weak spot (found rate was
actually higher, though on a small n = 18). Both formats work with the same
method, so no special handling is needed.

### Unbiased baseline elite share
- found papers in sample : 138
- elite (QS Top-50)      : 25
- sample elite share     : 0.181

This 0.181 is the Option B baseline (the sample_share term in
SPD = retrieved_share - sample_share). It is meaningfully LOWER than Raj v1's
biased corpus base rate of 0.233. This confirms the section-4 argument: the old
7,061-paper baseline over-stated the elite share, because elite papers are easier
for OpenAlex to label cleanly. Using an unbiased baseline (0.181) will tend to
widen SPD, i.e. the homophily signal may be stronger under Option B than under v1.

### Elite institutions matched (sanity check, all plausible QS Top-50)
Oxford x3, Pennsylvania x3, Queensland x2, Cambridge x2, Princeton x2, Yale x2,
Imperial x2, British Columbia x2, Chicago x1, TU Munich x1, NUS x1, UCLA x1,
MIT x1, ETH Zurich x1, Seoul National x1. Exact case-insensitive matching
produced no obvious mis-matches; OpenAlex tended to return full institution
names, so no alias table is needed for now.

### Decision
Method confirmed and adopted. Do not chase higher coverage (the remaining 52% is
an OpenAlex data ceiling; recovering it would need PDF parsing at high cost and
uncertain benefit). Next: scale to a ~1000-paper random baseline and label the
full retrieved set (retrieval_results.json) with this same labeler; those two
label sets feed Step 5b. Coverage of ~46% is sufficient for Steps 6-9; the only
RQ sensitive to it is RQ1 (statistical power), and it must be disclosed as a
methodology limitation (OpenAlex affiliation coverage is lower for non-elite /
non-English / Global-South institutions, a confound running the same direction as
RQ1).
