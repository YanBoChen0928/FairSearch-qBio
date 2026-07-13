# RQ2 Framework A - Summary

Institutional citation amplification at the generation stage.
Completed 2026-07-12. Owner: Yan-Bo. Notebook: step7-rq2-generation-frameworka-yb.

This file summarizes Framework A for the report and for teammates. Authoritative
methodology lives in `rq2_plan.md` (v2); measured numbers here match the output
files listed at the bottom.

## Pre-registered question

Does the generation stage amplify elite institutional representation? That is,
does the model cite elite-institution papers at a higher rate than they appear
in the retrieved context it was given?

This is the "who is cited" lens (institution). It is distinct from Framework B,
which is the "what is said" lens (viewpoint / dissent). A single model answers A;
B is a separate, later notebook.

## Method (short)

1. For each of the 100 neutral queries (q001-q100), take its top-10 retrieved
   papers from retrieval_results.json.
2. Number them [1]..[10] (retrieval rank order); keep a number -> paper_id map.
3. Prompt the model to answer using ONLY those 10 papers and mark each claim
   with its source number(s), e.g. [3] or [2][5]. Evidence-grounded prompt,
   NO balancing instruction (balancing belongs to RQ3).
4. Parse the [n] markers back to paper_ids (pure code).
5. Look up each paper's elite_label (retrieval_labels.json, QS Top-50 2026),
   counting only papers with coverage=="found" (unknown labels excluded, same
   rule as RQ1).
6. Per query compute:
   - context_elite_share = elite fraction of the labeled context papers
   - cited_elite_share   = elite fraction of the UNIQUE labeled cited papers
   - amplification = cited_elite_share - context_elite_share
7. Aggregate at query level; bootstrap 95% CI (resample queries, seed 42,
   10,000 draws). Empty-denominator queries set to null and excluded (never 0).

Headline metric = unique cited-paper set (symmetric with the 10 unique context
papers). Frequency-weighted share is a secondary diagnostic only, never swapped
in as the headline.

## Model used (and why it changed)

FINAL model: gemini-3.1-flash-lite, temperature 0.

The plan originally named Gemini 1.5 Flash. Google's deprecation schedule forced
several changes during setup (full trail in rq2_plan.md Decision 4):

- 1.5 series: removed (404 NOT_FOUND).
- 2.0-flash / -flash-001: shut down; free tier quota "limit: 0".
- 2.5-flash: listed by models.list() but "no longer available to new users"
  when actually called.
- 3.5-flash: callable, but this new project's free DAILY quota for it was only
  20 requests/day, which cannot finish 100 queries. Billing was declined
  (course project).
- 3.1-flash-lite: flash-lite has a much higher free daily quota and wider RPM,
  and the task is well within its capability. Ran all 100 queries, 0 failures.

KEY LESSON: appearing in client.models.list() does NOT mean the project may call
a model; only an actual generate_content call proves availability and quota.

## Measured result

- Model: gemini-3.1-flash-lite, temperature 0
- 100 neutral queries generated, 0 failures, 0 invalid citation markers,
  0 zero-citation queries
- 99 queries used; 1 excluded by the empty-denominator rule (set null, not 0)

Headline (unique cited-paper set):

| quantity | value |
|---|---|
| mean amplification (cited - context) | +0.0041 |
| median amplification | 0.0000 |
| bootstrap 95% CI (query-level, seed 42) | [-0.0254, +0.0342] |
| CI crosses zero | yes -> not statistically significant |
| cited elite share | 0.191 |
| context elite share | 0.187 |

Per-query direction (99 queries):

| direction | count |
|---|---|
| amplifying (>0) | 31 |
| reducing (<0) | 17 |
| unchanged (=0) | 51 |

## Conclusion

This is the NEUTRAL pre-registered outcome. No confirmed elite citation
amplification at the generation stage: the model's cited elite share (0.191)
essentially matches the context elite share (0.187) it was given, more than half
the queries show no change, and amplifying vs reducing queries roughly offset.

This mirrors RQ1 at the retrieval stage (SPD +0.029, 95% CI crossing zero, weak
and not significant) and the PCA finding that the embedding encodes topic rather
than institution. Retrieval, generation, and representation all point the same
way: this pipeline shows no clear institutional bias on a QS-Top-50 definition.

## Challenges encountered (for the report's method/limitations section)

- Model availability churn: four planned/attempted models were unavailable or
  quota-restricted before a usable one (3.1-flash-lite) was found. External
  constraint, not a design choice, and is disclosed.
- Free-tier quota: the working model's daily/minute limits required sequential
  calls with SLEEP and a retry-with-backoff loop; a per-query checkpoint (JSONL)
  with resume was used so an interrupted run could continue without re-calling
  the API for completed queries.
- Kaggle /kaggle/working is not durable across full session recycling; outputs
  must be saved (Save Version with output enabled) and backed up locally.

## Caveats (must appear in the report)

- "Not significant" means the difference is not confirmed by this data; it does
  NOT prove the bias is zero.
- The result is specific to gemini-3.1-flash-lite. A different generator could
  behave differently; the model switch is a disclosed limitation.
- Under a controlled RAG prompt this measures cited-source ATTRIBUTION behavior
  (which papers the model chooses to cite), not true token-level provenance,
  which LLMs do not expose.
- The 54.3% figure from earlier drafts / other groups uses a different elite
  definition and pipeline and is NOT comparable to this measured result.
- Retrieval rank is a possible confounder (the model may favor higher-ranked
  papers regardless of institution). Reported as a limitation; a descriptive
  check of cited-paper average rank can be added if needed.

## Output files

Kaggle /kaggle/working (backed up locally in the project WD):

- rq2_gen_checkpoint.jsonl - raw per-query generation (prompt inputs, answer,
  parsed citations); the immutable raw record
- rq2_frameworkA_per_query.json - per-query shares, amplification, diagnostics
- rq2_frameworkA_result.json - headline numbers, CI, direction counts, settings
- rq2_frameworkA_scatter.png - cited vs context elite share, per query + mean

## Next

Framework B (viewpoint flattening / dissent retention) on contradictory queries
q101-q150, in a separate notebook, reusing the same generation pipeline and the
same model (gemini-3.1-flash-lite). Judge model chosen at B start by testing
which stable model the project can actually call. See rq2_plan.md Decision 2/2b.
