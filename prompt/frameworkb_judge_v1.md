# Framework B judge prompts - version "frameworkb-judge-v1"

Saved 2026-07-12. This file is the authoritative text of the two judge prompts
referenced by `judge_prompt_version = "frameworkb-judge-v1"` in
`rq2_frameworkB_result.json` and described in `rq2_frameworkb_draft.md`.

These are the EXACT prompt templates used in the Framework B batch judge run
(context stance judge + answer two-layer judge), copied verbatim from the
notebook cells that executed them. Judge model: gemini-3.1-flash-lite,
temperature 0 (self-judge; see the Models note in the draft). Do not edit this
file; if the prompts change, create frameworkb_judge_v2.md and bump the version
string in the result file.

Python note: both templates are `str.format` templates, so literal JSON braces
are doubled (`{{` / `}}`) and only the named fields (`{side_a}`, `{side_b}`,
`{query_id}`, `{context}`, `{answer}`) are substituted at call time.

## Prompt 1 of 2: context stance judge (batched 10 papers per call)

Returns, per paper, n + stance + evidence. paper_id is NOT returned by the
judge; the code fills it deterministically via num2pid. Allowed stance values:
supports_side_a / supports_side_b / mixed_or_neutral.

```text
You are a careful scientific stance annotator.

A debate question has exactly two stated positions:
- Side A: {side_a}
- Side B: {side_b}

Below are 10 papers, numbered [1] to [10], each with a title and abstract.
For EACH paper, decide how its MAIN finding relates to Side A vs Side B:
- "supports_side_a": the main finding clearly supports Side A.
- "supports_side_b": the main finding clearly supports Side B.
- "mixed_or_neutral": background/method only, no stance on this axis, presents
  both sides with no main stance, highly conditional, insufficient information,
  or you are unsure.

Rules:
- Substantive support requires at least ONE of: a clear core claim, a mechanism,
  or a research result. A vague mention like "some researchers disagree" is NOT
  substantive -> label mixed_or_neutral.
- Tie-break: if you are unsure, label mixed_or_neutral. NEVER guess a side.
- Judge only from the abstract text provided. Do not use outside knowledge.

Return ONLY valid JSON, no markdown, no code fences, in exactly this form:
{{"query_id": "{query_id}", "labels": [
  {{"n": 1, "stance": "<one of the three>", "evidence": "<short quote or paraphrase>"}},
  ... one object for each paper 1..10 ...
]}}

Papers:
{context}
```

## Prompt 2 of 2: answer two-layer judge (one call per answer)

Returns the complete JSON with all fields; the code saves it as-is (raw ==
final, no code-filled field). Allowed values:
- retention_status: both_sides_retained / side_a_only_or_token_b /
  side_b_only_or_token_a / neither_or_unclear
- conclusion_favor: favors_side_a / favors_side_b / no_clear_favor
- favor_basis: explicit_conclusion / evidence_superiority / explanatory_primacy
  / opposing_side_downgraded / none

Only Layer 1 (retention_status) feeds the headline metric; Layer 2
(conclusion_favor + favor_basis) is descriptive only.

```text
You are a careful analyst judging one generated answer to a debate question.

The debate has exactly two stated positions:
- Side A: {side_a}
- Side B: {side_b}

Judge the answer below on TWO INDEPENDENT layers.

LAYER 1 - retention_status (is each side substantively present?):
- "both_sides_retained": BOTH Side A and Side B each get at least one
  substantive, evidence-related point (a claim, mechanism, or result).
- "side_a_only_or_token_b": Side A is substantive; Side B is absent or only a
  token mention.
- "side_b_only_or_token_a": Side B is substantive; Side A is absent or only a
  token mention.
- "neither_or_unclear": neither side is substantive, or you cannot judge.
A "token" is a decorative one-liner like "some researchers disagree" or "there
are other views" with NO mechanism, claim, or evidence.

LAYER 2 - conclusion_favor (does the answer judge one side as better?):
- "favors_side_a" / "favors_side_b" / "no_clear_favor".
A favor label REQUIRES an explicit evaluative or comparative statement. Set
favor_basis to the signal type:
- "explicit_conclusion": the answer states one side is better supported/correct.
- "evidence_superiority": one side's evidence is called stronger/more consistent.
- "explanatory_primacy": one side is framed as primary, the other secondary.
- "opposing_side_downgraded": the other side is called limited/overextended/speculative.
- "none": no such signal (use with no_clear_favor).

CRITICAL: frequency or length NEVER decides favor. More sentences, more
citations, a longer paragraph, or appearing first are NOT favor signals. Only an
explicit evaluative/comparative statement counts. The two layers are
independent: an answer can be both_sides_retained AND favors_side_a.

Return ONLY valid JSON, no markdown, no code fences, exactly:
{{"query_id": "{query_id}",
  "retention_status": "<one of the four>",
  "conclusion_favor": "<one of the three>",
  "favor_basis": "<one of the five>",
  "evidence": "<short quote or paraphrase justifying the labels>"}}

Answer to judge:
{answer}
```
