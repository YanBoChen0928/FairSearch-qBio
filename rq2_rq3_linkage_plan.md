# RQ2 x RQ3 Linkage Plan

How Framework A (RQ2, generation-stage citation bias, mine) can connect to
Jici's RQ3 re-ranking to form one causal story. This is an OPTIONAL extension,
not a required deliverable. Decide whether to run it after RQ2 lands.

## What the linkage is (plain language)

"A x RQ3 linkage" = run RQ2's Framework A a SECOND time, but on the re-ranked
context from RQ3 instead of the original retrieval. It asks: does improving the
context (re-ranking) also reduce the LLM's citation bias downstream?

## Why this idea exists

It answers a question we raised earlier: "if RQ2 finds bias at generation, can
RQ3 be used to intervene on it?" RQ3 re-ranking changes WHICH papers are fed to
the LLM. If the LLM's citation bias comes from the context it is given, then a
fairer/more diverse context could lower that bias. This linkage tests exactly
that.

---

## The flow (two passes, compared)

Pass 1 (the original RQ2 Framework A):
1. retrieval gives the original top-10 (elite ~18% in context)
2. feed to the LLM -> LLM cites elite at some rate, e.g. 40%
3. amplification = cited_elite_share - context_elite_share

Pass 2 (the linkage):
1. apply Jici's institution-aware re-ranking to get a MORE DIVERSE top-10
2. feed THIS re-ranked top-10 to the LLM
3. run Framework A again -> is the cited elite share now lower, e.g. 30%?

If Pass 2 < Pass 1: improving the retrieval context (RQ3) also reduced the
generation-stage citation bias (RQ2). That is the payoff.

## How it ties the three RQs into one causal chain

- RQ1: is there bias at retrieval?            (measure)
- RQ2: does generation amplify bias?          (measure)
- RQ3: can re-ranking fix retrieval?          (intervene)
- A x RQ3: does fixing retrieval also fix generation?   (downstream effect)

This is the original proposal vision: intervene on fairness at BOTH the
retrieval and generation stages, and show the effect propagates.

---

## Preconditions (when to actually do this)

1. RQ2 Framework A must FIRST find generation-stage bias (cited >> context).
   If RQ2 finds the LLM is neutral (cited ~ context), there is nothing to
   "fix downstream", so skip the linkage and just report RQ2 as neutral.
2. This is an add-on / bonus that deepens the story. Core deliverables are
   RQ1, RQ2, RQ3 each on their own. Only do the linkage if time allows AND
   precondition 1 holds.

## Data dependency (why "reuse candidate_labels" matters here)

The re-ranked top-10 (Pass 2) may include papers that were NOT in my original
retrieval_labels.json but ARE in Jici's candidate_labels.json (the top-50
pool). So Pass 2's Framework A needs Jici's candidate_labels.json to look up
elite labels for those newly-surfaced papers. This is the ONE scenario where my
RQ2 work would consume her candidate labels — reuse them, do not re-label
(same Option B method, already verified consistent: QS Top-50, OpenAlex
landing_page_url + DOI fallback, share 0.179 vs my 0.177).

## Decision checkpoint

To be decided together on the Sunday sync, AFTER RQ2 results:
- If RQ2 shows generation bias -> consider running the linkage; frame RQ3 as an
  intervention that also reduces downstream citation bias.
- If RQ2 shows no generation bias -> skip the linkage; frame RQ3 purely as
  "raise diversity at low utility cost" (Avery-style).

## Files involved (when/if run)

- inputs: retrieval_results.json, Jici's re-ranked top-10 output (from
  step6_reranking), retrieval_labels.json + candidate_labels.json (elite labels)
- reuse the same Framework A citation-parsing + bootstrap code from RQ2
- output: rq2_linkage_result.json (Pass 1 vs Pass 2 cited elite share + CI)
