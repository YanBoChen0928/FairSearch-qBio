# comparison_step8_with_step8_ragas.md

Comparison of the two independent Step 8 RAGAS runs: Yan-Bo's
(`results/ragas_faithfulness_result.json`) and Raj's
(`step8_ragas_summary.md` + three checkpoint JSONLs on `raj/step8-ragas`).

Written 2026-08-09, before merging `raj/step8-ragas`.
All findings below were verified against actual files, not from memory.

---

## 1. Why the two Faithfulness numbers differ

```
                          YAN-BO                    RAJ
                          ----------------------    ----------------------
  file                    results/ragas_            results/rq2_frameworkA_
                          faithfulness_result       ragas_cheap_checkpoint
                          .json                     .jsonl (+ B file)

  neutral / Framework A   0.9616   n=98             0.978    n=100
  contradictory / Fwk B   0.9613   n=50             0.966    n=50
  combined                0.9615   n=148            not reported combined
  failures                2  (q032, q068)           0

  judge model             gemini-3.1-flash-lite     gemini-3.1-flash-lite
  judge temperature       0                         0

  ragas version           0.4.3 + VertexAI stub     0.3.9 + VertexAI stub
  LLM object              native google.genai       LangchainLLMWrapper(
                          .Client                     ChatGoogleGenerativeAI)
  scoring call            evaluate(ds, metrics)     await m.single_turn_ascore
                          (sync wrapper)            (native async)

  CONTEXT FORMAT          "Title: {t}\n             "{t}\n{a}"
   *** the key diff ***    Abstract: {a}"
                          explicitly rebuilt to     labelled in his notebook
                          match what the            as mirroring step7
                          generator actually saw    build_context(), but the
                                                    labels are absent

  NaN handling            raise -> recorded as      only catches thrown
                          failure (fail-loud)       exceptions; NaN would be
                                                    written as a score
```

### Hypotheses tested and ruled out

| Hypothesis | Verdict | Evidence |
|---|---|---|
| Raj's checkpoint contains silent NaNs | RULED OUT | all 100 records numeric, 0 NaN |
| q032 / q068 got low-quality forced scores | RULED OUT | both scored 1.0; 82/100 queries score exactly 1.0, so these sit inside the normal distribution |
| Different judge model or temperature | RULED OUT | identical: gemini-3.1-flash-lite, temp 0 |
| **Context format differs** | **CONFIRMED** | see block above |

### What this means

The remaining explanation is that the two runs asked the judge a subtly
different question. Faithfulness decomposes the answer into atomic claims and
checks each against the supplied contexts. Yan-Bo's Step 8 notebook (Cell 3)
carries an explicit comment: rebuild contexts in the EXACT format shown to the
generator, because if the format diverges from what the model actually saw at
generation time, the score measures something subtly different from what was
generated. Raj's context builder drops the `Title:` / `Abstract:` labels.

This is a methodology difference, not a data-quality difference. Raj's run is
clean, reproducible, and complete. It is measured against a context string
that was not byte-identical to the generation-time prompt.

### Worked example (real paper, arXiv 1610.07213)

What Yan-Bo's judge saw for this context slot:

```
Title: Stochastic Modeling and Statistical Inference of Intrinsic Noise
       in Gene Regulation System via Chemical Master Equation
Abstract: Intrinsic noise, the stochastic cell-to-cell fluctuations in
       mRNAs and proteins, has been observed and proved to play important
       roles in cellular systems...
```

What Raj's judge saw for the same paper, same context slot:

```
Stochastic Modeling and Statistical Inference of Intrinsic Noise in Gene
Regulation System via Chemical Master Equation
Intrinsic noise, the stochastic cell-to-cell fluctuations in mRNAs and
proteins, has been observed and proved to play important roles in
cellular systems...
```

Same underlying text, but in Raj's version the title line reads like an
ordinary declarative sentence with no marker saying "this is a title, not a
claim you can verify against." A paper title phrased as an assertion (a
common style in this corpus) can be misread by the judge as itself a
verifiable statement, or can loosen the boundary of what counts as
supporting evidence for a claim. Yan-Bo's labelled version removes that
ambiguity. This is a small per-context effect, but it applies across all
100 (or 150) queries, and small systematic effects at that scale are enough
to move a corpus mean from 0.9615 to 0.978.

---

## 2. Can Raj's data go straight into `streamlit_app.py`?

**No. Not without a converter.** The app is a pure renderer, but the bundle
notebook (`step9b-bundle-assembly-yb.ipynb`) reads a specific schema.

### What the bundle notebook requires

```
results/ragas_faithfulness_result.json
  |
  +-- per_query            [ list ]      Cell 1
  |     +-- query_id                     Cell 1  (keyed by this)
  |     +-- faithfulness_score           Cell 2  faithfulness_block()
  |
  +-- failed_queries       [ list ]      Cell 1
  |     +-- query_id                     -> status 'failed' in the app
  |
  +-- faithfulness_overall [ dict ]      Cell 6  'faithfulness_corpus_mean'
  +-- faithfulness_by_type [ dict ]      Cell 6  'faithfulness_by_type'
```

### What Raj's files actually contain

```
results/rq2_frameworkA_ragas_cheap_checkpoint.jsonl   (100 lines, neutral)
results/rq2_frameworkB_ragas_faithfulness_checkpoint.jsonl (50 lines, contra)
results/rq2_frameworkA_ragas_cp_checkpoint.jsonl      (100 lines, CP only)

  one JSON object per line:
    { "query_id": "q032",
      "faithfulness": 1.0,
      "answer_relevancy": 0.946 }
```

### Gap list

| Needed | Raj has | Action |
|---|---|---|
| single JSON file | three JSONL files | merge |
| `faithfulness_score` | `faithfulness` | rename |
| `type` (neutral / contradictory) | absent | derive from qid (q001-q100 neutral, q101-q150 contradictory) |
| `failed_queries` | absent | emit `[]` |
| `faithfulness_overall` | absent (only in his .md prose) | compute |
| `faithfulness_by_type` | absent | compute |

So switching to Raj's numbers is not a drop-in. It needs a small conversion
cell that reads his three JSONLs and writes a file in the schema above. The
Streamlit app itself needs no code change for Faithfulness, because it only
ever sees the bundle.

**Note on the two "missing" summary JSONs.** Raj's `step8_ragas_summary.md`
mentions `results/rq2_frameworkA_ragas_summary.json` and
`results/rq2_frameworkB_ragas_summary.json` as not committed. Verified: the
Step 9-B notebook never reads either filename. Their absence blocks nothing.

---

## 3. How did Raj get Answer Relevancy when we closed it as infeasible?

Short answer: **he used a different stack, and our "infeasible" claim was
always scoped to ours.** Neither party is wrong, and `step8.md` does not need
to be retracted. It needs a scope qualifier.

### What blocked us (step8.md 4a.8)

Four constraints on **ragas 0.4.3 + native `google.genai.Client`** formed a
closed contradiction:

```
  1. notebook already runs an event loop  -> ragas refuses sync score()
  2. so ascore() must be used             -> requires async-capable LLM
  3. async-capable means client.aio       -> AsyncClient
  4. instructor adapter type-checks for   -> rejects AsyncClient
     exactly google.genai.Client
```

No arrangement satisfies all four. A ThreadPoolExecutor escape was also tried
and failed the same way. We stopped there per the pre-registered stopping
rule, and recorded the conclusion as infeasible **on this stack**.

### What Raj did differently

```
                        OURS                      RAJ'S
                        ---------------------     ---------------------
  ragas                 0.4.3                     0.3.9
  LLM object            google.genai.Client       LangchainLLMWrapper(
                        (native)                    ChatGoogleGenerativeAI)
  embeddings            GoogleEmbeddings          LangchainEmbeddingsWrapper(
                        (Gemini API)                HuggingFaceEmbeddings
                                                    all-MiniLM-L6-v2, local CPU)
  strictness            n/a (never ran)           1  (flash-lite rejects
                                                     multi-candidate requests)
```

Two of these independently dissolve the deadlock:

1. **LangChain wrapper instead of the native client.** `ChatGoogleGenerativeAI`
   is async-native and ragas wraps it with `LangchainLLMWrapper`, so the
   instructor adapter that type-checks `google.genai.Client` is never on the
   path. Constraints 3 and 4 above simply do not arise.
2. **Local HuggingFace embeddings instead of Google embeddings.** Sidesteps
   the whole `embed_query` / legacy-vs-modern interface problem, and costs
   zero Gemini quota.

He also hit the same `ChatVertexAI` import defect we did, and resolved it the
same way (stub the missing submodule) but on 0.3.9 rather than 0.4.3.

### Worth noting: we recorded this exact path and did not take it

`step8.md` 4a.8, "Path not taken, recorded for completeness":

> `LangchainEmbeddingsWrapper` does expose `embed_query` and would satisfy the
> legacy interface, and the project already has all-MiniLM-L6-v2 embeddings of
> the corpus that could have served as the similarity backend at zero Gemini
> cost. This was not pursued because the blocking constraint turned out to be
> on the LLM side, not the embeddings side.

That reasoning was correct about the embeddings alone. What was not tried was
changing the **LLM** object at the same time. Raj changed both, and the
combination works. This is a good outcome for the disclosure discipline: the
alternative was written down at the time, which is why we can now say exactly
what the difference is instead of guessing.

### Is it legitimate?

Yes. Same judge model, same temperature, same source data, local embeddings
for the similarity step. The one caveat Raj discloses himself: `strictness=1`
instead of the default 3, because flash-lite returns
`400 INVALID_ARGUMENT: Multiple candidates is not enabled for this model`.
That makes each per-query relevancy score noisier (one reverse-question
instead of three averaged), absorbed at n=100 aggregate. Disclose it; do not
present 0.914 as if it were a default-strictness number.

### Context Precision

Unchanged: stays out of scope as a disclosed limitation per `step8.md` 2b.
Raj's 0.039 with the 90/4/5/1 distribution is a useful supporting artifact for
the limitation paragraph, and his Faithfulness cross-check (0.977 on the 90
queries scoring CP = 0.0, versus 0.978 overall) is a good argument that the
low CP is a metric artifact rather than a retrieval failure. Report it as
evidence for the limitation, not as a fourth headline metric.

---

## 4. Decision and disclosure requirement

**DECIDED (2026-08-09): Faithfulness headline switches to Raj's numbers**
(0.978 neutral / 0.966 contradictory, 150/150). This overrides the earlier
recommendation in this document to keep Yan-Bo's 0.9615. Recorded here so the
reasoning trail stays intact rather than silently disappearing.

**This decision carries a mandatory disclosure obligation.** The context
format difference documented in Section 1 (the worked example) is not
optional background reading — it must appear, in substance, wherever the
0.978/0.966 figure is presented: the report's Methodology or Limitations
section, the Streamlit caption next to the Faithfulness metric, and the
slide notes if the number appears on a slide. Minimum required sentence:

> Faithfulness was independently measured twice with two different context
> construction methods; this run's contexts were built as `"{title}\n
> {abstract}"` without field labels, differing from the
> `"Title: ...\nAbstract: ..."` format used at generation time and in an
> earlier internal run (which scored 0.9615, 148/150, see
> `results/ragas_faithfulness_result.json`). The two runs converge in
> direction but not in exact value.

Do not present 0.978/0.966 as a bare number with no caveat. Doing so
misrepresents what was measured against what the model actually saw at
generation time.

This requires: the converter in Section 2 (Raj's three JSONLs into the
bundle schema), a regenerated bundle, and updates to the deck, the
checklist, and the report wherever 0.9615/148 currently appears.

Either way, **Answer Relevancy 0.914 is adopted** and `step8.md` 4a.8 gets a
scope qualifier rather than a retraction. Suggested wording:

> Answer Relevancy was closed as infeasible on the ragas 0.4.3 +
> native-google-genai stack used here. It was subsequently obtained by Raj on
> a ragas 0.3.9 + LangChain-wrapper stack with local HuggingFace embeddings
> (mean 0.914, 95% CI [0.899, 0.927], n=100, strictness=1). The original
> finding stands as a statement about this stack; it was not a statement
> about the metric.

---

## 5. Decisions to record

```
D1  Answer Relevancy       adopt (0.914, strictness=1 disclosed)
    decided on:  __________

D2  Faithfulness headline  [x] Raj 0.978/0.966   decided 2026-08-09
    disclosure sentence (Section 4) required everywhere the number appears
    converter written?  [ ] yes  [ ] no  -- next action, see Section 2

D3  Context Precision      unchanged, out of scope, Raj's 0.039 cited as
                           supporting evidence in the limitation paragraph
```
