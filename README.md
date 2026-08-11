# FairSearch-qBio

## Evaluating and Mitigating Institutional Bias in Academic RAG for Quantitative Biology (q-bio) papers on arXiv

**Course:** CS 6200 Information Retrieval — Northeastern University (Summer 2026)
**Instructor:** Prof. Shanu Sushmita
**Team:** Jici Jiang · Raj Lucka · Yan-Bo Chen
**GitHub:** [github.com/YanBoChen0928/FairSearch-qBio](https://github.com/YanBoChen0928/FairSearch-qBio)

**Status:** all experiments complete. Last updated 2026-08-10.

---

## Headline results, with their caveats

Every number below is measured and traceable to a file in this repository. Most
headline confidence intervals cross zero. That is reported as the finding, not
smoothed into a positive claim.

| Question | Result | Verdict |
| --- | --- | --- |
| **RQ1** Does retrieval over-select elite institutions? | SPD **+0.029**, SRR 1.28, bootstrap 95% CI **[−0.005, +0.065]** | Crosses zero — not significant |
| **RQ2-A** Does the LLM over-cite elite institutions? | Mean amplification **+0.0041**, 95% CI **[−0.0254, +0.0342]** | Crosses zero — not significant |
| **RQ2-B** Does the LLM keep both sides of a debate? | Self-judge **97.2%** (35/36) vs independent judge **77.8%** (28/36) | Judge-dependent — see caveat below |
| **RQ3** What does fairness-aware re-ranking cost? | MMR λ=0.8: diversity 5.49→5.73 at flat NDCG@10. Fair-Top-K: diversity 9.35 but SPD **−0.046**, CI excludes zero | Cheap, but the hard quota over-corrects |
| **Step 8** Are generated answers grounded? | RAGAS Faithfulness **0.978** neutral / **0.966** contradictory, 150/150, 0 failures | See disclosure below |

**The single most important caveat.** RQ2 Framework B's retention rate depends
on which model judges it. Our original self-judge (same model that generated the
answers) reported 97.2%. An independent judge (`openai/gpt-oss-20b`) scoring the
same 36 queries reported 77.8%. Agreement is 80.6%; all 7 disagreements run one
direction, with the independent judge always rating retention lower. These 7
cases are **not adjudicated** — no blinded third review was run before the
deadline. Comparing the two confidence intervals by eye is also the wrong test,
because both judges scored the same queries: McNemar's test is correct and was
not run. Full account in `rq2_frameworkB_summary.md`.

**Required Faithfulness disclosure.** Faithfulness was independently measured
twice with two different context construction methods. The headline run built
contexts as `"{title}\n{abstract}"` without field labels, differing from the
`"Title: ...\nAbstract: ..."` format used at generation time and in an earlier
internal run, which scored 0.9615 over 148/150. The two runs converge in
direction but not exact value. Never cite 0.978/0.966 without this sentence.
Details: `comparison_step8_with_step8_ragas.md` §1 and §4.

**Answer Relevancy scope.** 0.914, 95% CI [0.899, 0.927], **n=100 neutral
queries only** (the contradictory checkpoint carries no `answer_relevancy`
field), at `strictness=1` — required because `gemini-3.1-flash-lite` rejects the
ragas default of 3. Never cite it as a 150-query figure.

---

## Where the graded deliverables live

| Required item | File |
| --- | --- |
| Data preprocessing scripts | `notebooks/step1-data-prep.ipynb`, `notebooks/step1b-institution-labels-full-yb.ipynb`, `notebooks/step2-embedding.ipynb`, `notebooks/step3_chromadb.ipynb` |
| RAG pipeline code | `notebooks/step5-retrieval-baseline-yb-kaggle-150.ipynb` (retrieval), `notebooks/step7-rq2-generation-frameworka-yb.ipynb` and `notebooks/step7-rq2-generation-frameworkb-yb.ipynb` (generation) |
| Re-ranking implementations | `notebooks/step6-reranking-yb-optimized-basedon-jici.ipynb` — institution-aware MMR **and** Fair-Top-K |
| Streamlit fairness scorecard app | `app/streamlit_app.py`, reading `app/data/step9_bundle.json` |
| **JSON results of the 100-query audit** | **`results/rq1_optionB_result.json`** — see the scope note directly below |
| README with setup and reproduction | this file, section "Setup and reproduction" |

### Scope note: "the 100-query audit"

The pre-registered query set is **150** queries, split by design into two
non-overlapping halves that answer different questions:

- **q001–q100, neutral.** The Experiment A / retrieval-audit set. **RQ1, RQ3,
  and RQ2 Framework A all run on these 100 queries.** This is the set the
  rubric's "100-query audit" refers to.
- **q101–q150, contradictory.** The Experiment B set, held out so that the
  institution axis and the viewpoint axis stay separable. RQ2 Framework B runs
  on these 50.

So the primary audit JSON is `results/rq1_optionB_result.json` (aggregate SPD,
SRR, bootstrap CI over the 100 neutral queries). Supporting per-query files:

| File | Contents |
| --- | --- |
| `results/rq1_optionB_result.json` | RQ1 headline: SPD, SRR, bootstrap CI, slot counts |
| `results/rq1_optionB_result_bio.json` | Same, under the bio-specific elite list (robustness check) |
| `results/rq3_results.json` | Baseline, MMR λ sweep, Fair-Top-K, all bootstrap CIs |
| `results/rq2_frameworkA_result.json` | Citation amplification, per-query distribution |
| `results/rq2_frameworkB_result.json` | Self-judge retention |
| `results/rq2_frameworkB_independent_judge_result.json` | Independent-judge retention |
| `results/rq2_frameworkA_ragas_summary.json` | Faithfulness, Answer Relevancy, Context Precision (neutral) |
| `results/rq2_frameworkB_ragas_summary.json` | Faithfulness (contradictory) |
| `data/retrieval_results.json` | Raw Top-10 retrieval for all 150 queries |

---

## Setup and reproduction

There are **two separate environments**. Do not merge them.

### 1. Streamlit app only (fast, no API keys, no GPU)

The deployed app is a pure JSON reader: it never embeds text, never queries
ChromaDB, and never calls an LLM. Everything it displays is precomputed in
`app/data/step9_bundle.json`.

```bash
git clone https://github.com/YanBoChen0928/FairSearch-qBio.git
cd FairSearch-qBio
python3 -m venv .venv && source .venv/bin/activate
pip install -r app/requirements.txt      # streamlit only
streamlit run app/streamlit_app.py
```

`app/requirements.txt` is deliberately minimal. Do **not** install the root
`requirements.txt` for the app: `sentence-transformers` pulls in PyTorch (~2GB)
and exhausts Streamlit Community Cloud's free-tier build budget.

### 2. Research pipeline (notebooks)

**Read this before trying to reproduce anything.** This pipeline was built and
run on **Kaggle Notebooks**, not locally. 18 of the 24 notebooks contain
hardcoded `/kaggle/input/...` or `/kaggle/working/...` paths, and 8 of them read
the Gemini API key from Kaggle Secrets (`UserSecretsClient`). Cloning this repo
and running `jupyter lab` locally will **not** work without editing those paths
first. No end-to-end local run of the full pipeline has ever been performed, so
this README does not claim one is reproducible.

What this means in practice:

| You want to | Do this |
| --- | --- |
| See the interface and the results | Run the Streamlit app (section 1 above). No keys, no Kaggle, works locally. |
| Inspect how a result was computed | Open the notebook and read it; most have saved cell outputs from the actual run. |
| Actually re-run a stage | Upload the notebook to Kaggle, attach the datasets listed in `data/kaggle_datasets.md`, and add `GEMINI_API_KEY` to Kaggle Secrets. |
| Re-run only the local, API-free parts | `notebooks/step9b-bundle-assembly-yb.ipynb` and `notebooks/power_analysis*.ipynb` have no `/kaggle/` paths and run locally against files in this repo. |

The dependency list below is the research environment, provided for reference
and for the locally-runnable notebooks:

```bash
pip install -r requirements.txt
```

Raw data is **not** committed:

1. Download the arXiv snapshot from
   [Kaggle — Cornell University arXiv](https://www.kaggle.com/datasets/Cornell-University/arxiv)
   and place it at `data/raw/arxiv-metadata-oai-snapshot.json` (~4GB).
2. Run `notebooks/step1-data-prep.ipynb` to extract the q-bio subset
   (55,301 papers; 55,300 after dedup).
3. Intermediate artifacts (`data/processed/`, `data/chroma/`) are gitignored and
   shared through Kaggle Datasets instead. See `data/kaggle_datasets.md` for the
   dataset slugs.

No API key is stored anywhere in this repository.

### RAGAS environment caveat

`requirements.txt` alone does **not** reproduce the Step 8 environment. RAGAS
version conflicts and the async/sync workarounds are documented in `step8.md`
§4a.6. The two runs in this project used different stacks on purpose:

| Run | Stack | Produced |
| --- | --- | --- |
| Yan-Bo | ragas 0.4.3 + native google-genai | Faithfulness 0.9615 (148/150), superseded |
| Raj | ragas 0.3.9 + `LangchainLLMWrapper` + local HuggingFace embeddings | Faithfulness 0.978/0.966 (150/150), Answer Relevancy 0.914 — **headline** |

`generate_summary_jsons.py` regenerates the two official summary JSONs from the
raw checkpoints without any API calls.

---

## Pipeline architecture

```
Step 1   →  Prepare dataset (55,301 q-bio abstracts; 55,300 after dedup)      [Done]
Step 1b  →  Enrich institution/region labels via OpenAlex                     [Done]
Step 2   →  Embed with all-MiniLM-L6-v2 (384-dim)                             [Done]
Step 3   →  Store vectors in ChromaDB                                         [Done]
Step 4   →  Generate 150 queries (100 neutral + 50 contradictory)             [Done]
Step 5a  →  Retrieve Top-10, Precision/Recall                                 [Done]
Step 5b  →  Join labels → SPD, SRR, Equalized Odds       ← RQ1                [Done]
Step 6   →  Institution-aware MMR + Fair-Top-K re-ranking ← RQ3               [Done]
Step 7a  →  Generation on neutral queries    ← RQ2 Framework A                [Done]
Step 7b  →  Generation on contradictory queries ← RQ2 Framework B             [Done]
Step 8   →  RAGAS evaluation + independent judge validation                   [Done]
Step 9   →  Streamlit diagnostic interface                                    [Done]
```

---

## Technical stack

| Component | Tool |
| --- | --- |
| Dataset | arXiv metadata (Cornell University / Kaggle), q-bio subset |
| Embedding model | `all-MiniLM-L6-v2` (sentence-transformers, 384-dim) |
| Vector database | ChromaDB |
| Generative LLM | `gemini-3.1-flash-lite`, temperature 0 (see model-history note) |
| LLM-as-judge | `gemini-3.1-flash-lite` (self-judge); `openai/gpt-oss-20b` via OpenRouter (independent judge, Framework B) |
| Institution metadata | OpenAlex API, matched against QS World University Rankings 2026 Top-50 |
| IR evaluation | NDCG@10, MRR, Precision@K, Recall@K |
| Fairness metrics | SPD, SRR, approximate Equalized Odds |
| RAG evaluation | RAGAS (Faithfulness, Answer Relevancy; Context Precision out of scope) |
| Dashboard | Streamlit |
| Compute | Kaggle Notebooks |

**Model history note.** The original plan specified Gemini 1.5 Flash. Over the
course of the project, 1.5-series and 2.0/2.5-series models were retired or
became uncallable for this project (404s, zero daily quota, or "no longer
available to new users") before any call was made. `gemini-3.1-flash-lite` is
the model that actually completed every generation run, and this repository
names the model it actually used rather than the one originally planned.
Framework B's primary judge (`gemini-3-flash-preview`) was similarly blocked
mid-run by a 20/day free quota and fell back to the same flash-lite model,
which is what makes it a self-judge. Details in `rq2_plan.md` (Decision 4) and
`rq2_frameworkb_draft.md` (Models section).

---

## Repository map

The project is notebook-first. Method decisions live in Markdown files at the
repository root, one per step, and each is the authoritative source for its
stage. This table is the entry point.

```
FairSearch-qBio/
├── app/                     Streamlit interface (deployable on its own)
│   ├── streamlit_app.py
│   ├── data/step9_bundle.json   precomputed diagnostics, 20 of 150 queries
│   └── requirements.txt         streamlit only, intentionally minimal
├── notebooks/               all pipeline code, step-numbered
├── results/                 measured outputs, JSON + figures
├── data/                    labels, checkpoints, query scope (large inputs gitignored)
├── queries/                 the 150 audit queries and their side annotations
├── prompt/                  frozen judge prompt, versioned
├── prototype/               early HTML layout prototypes for the interface
└── *.md                     methodology and decision records (see below)
```

### Methodology documents

| File | Covers |
| --- | --- |
| `rq1_methodology.md` | RQ1 design, Option B labeling, bio robustness check (§10), power analysis (§6a) |
| `rq2_methodology.md` | RQ2 overall design, Framework A and B scope separation |
| `rq2_frameworkA_summary.md` | Citation amplification results |
| `rq2_frameworkB_summary.md` | Viewpoint retention, **including the independent-judge validation** |
| `rq3_methodology.md` | Re-ranking design, λ sweep, power analysis (§6.3) |
| `step6_fair-top-k_methodology.md` | Fair-Top-K design and why corpus-parity beats strict alternation |
| `step8.md`, `step8_ragas_summary.md` | RAGAS setup, environment workarounds, D1/D2/D3 decisions |
| `comparison_step8_with_step8_ragas.md` | Why the two Faithfulness runs differ, with a worked example |
| `step9_plan.md`, `step9_query_subset.md` | Interface architecture and the 20-query sampling method |
| `queries/query_generation_methodology.md` | How the 150 queries were built |
| `note_for_updated_and_final/` | Merge plan, deliverables checklist, session handoff notes |

`src/` exists but is **empty** apart from a `.gitkeep`. An earlier plan proposed
extracting reusable modules from the notebooks; that refactor was never done,
and this README does not pretend otherwise.

---

## Work division

| Step | Owner | Status |
| --- | --- | --- |
| Step 1 — Data preparation | Yan-Bo | Done |
| Step 1b — Institution labeling | Yan-Bo, Raj | Done |
| Step 2 — Embedding | Yan-Bo | Done |
| Step 3 — ChromaDB ingestion | Raj | Done |
| Step 4 — Query generation (150) | Yan-Bo | Done |
| Step 5 — Baseline retrieval | Jici | Done |
| Step 5b — Fairness audit ← RQ1 | Yan-Bo | Done |
| Step 6 — MMR + Fair-Top-K ← RQ3 | Jici, Yan-Bo | Done |
| Step 7a/7b — Generation ← RQ2 A and B | Yan-Bo | Done |
| Step 8 — RAGAS evaluation | Raj | Done |
| Step 8 — Independent judge validation, power analysis | Jici | Done |
| Step 9 — Streamlit interface | Yan-Bo | Done |
| Final report PDF | Jici | In progress |
| Final slide deck | Yan-Bo | Done |

---

## Detailed findings

**RQ1 — retrieval-stage institutional bias.** Elite defined as QS World
University Rankings 2026 Top-50. Baseline elite share 14.4% (438 found of 1,000
sampled, seed 42); retrieved elite share 17.3% across 590 labeled Top-10 slots
for the 100 neutral queries. SPD +0.029, SRR 1.28, bootstrap 95% CI
[−0.005, +0.065] crossing zero: a weak elite tilt that is not statistically
significant. A binomial test returns p = 0.046 but assumes independent papers,
an assumption violated by within-query correlation; the query-level bootstrap is
the authoritative test. See `results/rq1_optionB_result.json`.

**Step 1b — why labeling is "Option B" and not a full-corpus label.** The first
attempt tried to label the entire ~55,300-paper corpus via OpenAlex title
lookup. 82% of papers came back `not_found`, and the 18% that did match skewed
toward better-indexed, more mainstream institutions — inflating the apparent
baseline elite share to 0.233. Comparing a retrieved set against that inflated
baseline would understate the real gap. The fix ("Option B") does not attempt
full-corpus coverage at all: it labels two SMALL sets — a random 1,000-paper
corpus sample and the deduplicated retrieved set — with the identical method
(OpenAlex batched lookup, 50 ids/request, primary match on
`landing_page_url` with DOI fallback, matched against QS Top-50). Applying one
identical procedure to both sides removes *asymmetric measurement* as an
explanation for the gap. It does **not** prove the gap is free of all labeling
effects: coverage still differs between the two sets (44% baseline vs 58%
retrieved), so conclusions remain conditional on resolved records, and
differential missingness cannot be ruled out from this design alone.

**Which elite-share number goes with which denominator.** Three figures appear
in this project and they are not interchangeable:

| Figure | Denominator | Used for |
| --- | --- | --- |
| 14.4% | 63 elite of 438 resolved baseline papers | the parity reference |
| 17.7% | 141 of 798 resolved unique retrieved papers, all 150 queries | an all-queries cross-check |
| **17.3%** | **102 of 590 resolved Top-10 slots, q001–q100 neutral only** | **the RQ1 test** |

The headline SPD is `17.29% − 14.38% = +0.029`, so it pairs 17.3% with 14.4%.
The 17.7% figure is a wider cross-check and is never the input to the test. See
`rq1_methodology.md` §3 and `summary_step1b_OptionB.md`.

**RQ1 robustness — subject-specific elite definition.** Following a suggestion
from Prof. Sushmita, a second elite list drawn from QS World University Rankings
by Subject 2026: Biological Sciences was run in full parallel. Baseline elite
share 0.158 (vs 0.144), SPD +0.031 (vs +0.029), bootstrap 95% CI [−0.005,
+0.069] still crossing zero. The conclusion is robust to the choice of elite
definition. See `rq1_methodology.md` §10.

**RQ1 — approximate Equalized Odds.** Textbook TPR/FPR requires relevance
judgments over the full candidate pool per group; this project only has
relevance for retrieved Top-10, so a Top-K-conditional approximation is reported
instead. Signed-direction mean +0.048, 95% CI [−0.051, +0.142], crossing zero
(25 queries favour elite, 19 favour non-elite, 21 tied, n=65, bio elite list).
The large absolute gap reflects query-to-query variance in both directions, not
a systematic tilt.

**RQ2 Framework A — citation amplification.** Neutral queries. Mean
amplification (cited elite share minus context elite share) = +0.0041, median
0.0000, bootstrap 95% CI [−0.0254, +0.0342] crossing zero. n = 99 usable
queries: 31 amplifying, 17 reducing, 51 unchanged. No confirmed elite citation
amplification at the generation stage.

**RQ2 Framework B — viewpoint retention.** Contradictory queries. Of 50, 36 were
eligible (retrieved context contained evidence for both stated sides). The
self-judge found 35 of 36 retained both sides (97.2%, CI [91.7%, 100.0%]); the
independent judge found 28 of 36 (77.8%, CI [63.9%, 91.7%]). See the caveat at
the top of this README — this gap is a headline limitation, not a footnote.

**RQ3 — fairness/utility tradeoff.** Institution-aware MMR at λ=0.8 raises
unique institutions per query from 5.49 to 5.73 with NDCG@10 flat at 0.809 and
MRR unchanged. Its own SPD (+0.0163) has a CI crossing zero, but the improvement
versus baseline is significant: **+0.0126**, defined as baseline SPD minus MMR
SPD (0.0289 − 0.0163), so a positive value means SPD moved toward parity;
95% CI [+0.0013, +0.0254].

Fair-Top-K is the hard-quota contrast arm. Note what the quota actually resolves
to: `round(10 × 0.144) = 1`, so in a Top-10 list the operating target is **one
elite slot, i.e. 10%**, not 14.4%. Measured elite share lands at 0.098 and SPD
at −0.046, CI [−0.049, −0.044] excluding zero: a statistically significant
over-correction into reverse bias, largely a consequence of that integer
resolution. Unique institutions rise to 9.35, but this is **not a pure
diversity gain**: Fair-Top-K fills all 1,000 output slots from the labeled
elite/non-elite pools, versus 590 labeled slots at baseline and 574 under MMR,
so part of the 9.35 is a mechanical coverage effect
(`step6_fair-top-k_methodology.md` §7). Neither arm costs NDCG@10 **under this
project's binary subcategory-match relevance proxy**; that must not be
generalized into a claim that hard quotas are relevance-free in general. The two
arms are parallel contrasts, not a hierarchy.

**Power.** RQ1 operates at roughly 49% power (MDE 0.0434 against an observed SPD
of 0.029); the RQ3 paired improvement test is lower still. Several null results
are therefore under-powered rather than conclusively null. See
`rq1_methodology.md` §6a and `rq3_methodology.md` §6.3.

**Mitigation not run.** Perspective-balanced prompting was planned as a
Framework B mitigation but was not triggered: baseline retention was already
97.2% (35/36 eligible queries), leaving no dissent-suppression problem to
correct. RQ3's mitigation results therefore cover MMR and Fair-Top-K only.

---

## Known limitations

- **Binary elite framing.** QS Top-50 is a fixed, reproducible threshold, not a
  claim that institutional prestige is binary.
- **Label coverage.** 44% of the baseline sample and 58% of the retrieved set
  resolved to an institution. Unlabeled papers are excluded from every share,
  never counted as zero.
- **Self-judge on RAGAS Faithfulness.** One judge, and it is the same model that
  generated the answers. Only Framework B has a genuine two-judge comparison;
  the two must not be conflated.
- **Judge disagreements unadjudicated.** 7 of 36, all one-directional.
- **Context Precision out of scope.** Measured at 0.039 with a bimodal
  distribution (90 of 100 at zero), while Faithfulness on those same queries
  stayed at 0.977 — evidence of a metric artifact of the reference-free variant
  rather than a retrieval failure. Carried as a disclosed limitation, not
  promoted to a headline metric.
- **Demo coverage.** The Streamlit bundle precomputes 20 of 150 queries (Tier 1,
  seed 42). All statistical claims come from the full query sets, not this
  subset. None of the 6 sampled contradictory queries is one of the 7 judge
  disagreements, so the disagreement branch of the interface is not reachable in
  the shipped demo.
- **Eligibility inference in the interface.** The bundle carries no explicit
  `eligibility` field; the app infers it from whether an independent-judge record
  exists. Verified consistent against `results/rq2_frameworkB_result.json`'s
  `excluded_ids`, but a future bundle should carry the field explicitly.

---

## Possible future extensions (not started, not pre-registered)

**Institutional skew within Framework B's Side A / Side B papers.** Framework A
(institution) and Framework B (viewpoint) were deliberately split across two
non-overlapping query sets so that each isolates one axis cleanly. Mixing both
questions on the same debate queries would risk a confound: if Side A's papers
happen to skew more elite than Side B's in the underlying corpus, an observed
"answer favors Side A" result becomes impossible to attribute cleanly to a
substantive-position preference versus an elite-institution preference.

A possible follow-up: after Framework B's results are final, as they are now,
separately compute the elite share of Side A's cited papers versus Side B's
within the 36 eligible queries, purely as a descriptive check. It would be
reported alongside the existing retention finding, never merged into it, to
avoid retroactively contaminating a completed pre-registered metric. This would
need its own pre-registration if pursued.

**Adjudicating the judge disagreements.** A blinded review of the 7 cases with a
frozen rubric, plus McNemar's test on the paired data.

**More statistical power for RQ1.** Expanding institution-label coverage beyond
44–58%, or widening the query set, would narrow the CI enough to distinguish a
small real effect from no effect.

---

## References

Key papers informing this work:

- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS*.
- Zehlike et al. (2017). FA\*IR: A Fair Top-k Ranking Algorithm. *CIKM*.
- Patro et al. (2022). Fair ranking: a critical review. *FAccT*.
- Balagopalan et al. (2023). The Role of Relevance in Fair Ranking. *SIGIR*.
- Wu et al. (2025). Does RAG Introduce Unfairness in LLMs? *COLING*.
- Es et al. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation. *arXiv:2309.15217*.
