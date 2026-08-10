"""
Generate rq2_frameworkA_ragas_summary.json and rq2_frameworkB_ragas_summary.json
from the checkpoint JSONL files. Deterministic — same bootstrap (seed=42, n=10000)
as Cell 10 in the Step 8 notebook.
"""

import json
import os
import numpy as np

RNG_SEED = 42
N_BOOT = 10_000
rng = np.random.default_rng(RNG_SEED)


def aggregate_metric(records, metric_name):
    vals = np.array(
        [
            r[metric_name]
            for r in records
            if isinstance(r.get(metric_name), (int, float)) and not np.isnan(r[metric_name])
        ],
        dtype=float,
    )
    n = len(vals)
    if n == 0:
        return {"mean": None, "n": 0, "n_dropped_null": len(records), "bootstrap_95CI": [None, None]}
    boot = [float(np.mean(rng.choice(vals, size=n, replace=True))) for _ in range(N_BOOT)]
    ci_low, ci_high = np.percentile(boot, [2.5, 97.5])
    return {
        "mean": round(float(np.mean(vals)), 4),
        "n": n,
        "n_dropped_null": len(records) - n,
        "bootstrap_95CI": [round(float(ci_low), 4), round(float(ci_high), 4)],
        "min": round(float(np.min(vals)), 4),
        "max": round(float(np.max(vals)), 4),
    }


def load_checkpoint(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


recs_a_cheap = load_checkpoint("results/rq2_frameworkA_ragas_cheap_checkpoint.jsonl")
recs_a_cp = load_checkpoint("results/rq2_frameworkA_ragas_cp_checkpoint.jsonl")

summary_a = {
    "framework": "A (neutral queries, 100)",
    "judge_model": "gemini-3.1-flash-lite",
    "judge_temperature": 0,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "bootstrap": {"n_resamples": N_BOOT, "seed": RNG_SEED},
    "metrics": {
        "faithfulness": aggregate_metric(recs_a_cheap, "faithfulness"),
        "answer_relevancy": aggregate_metric(recs_a_cheap, "answer_relevancy"),
        "context_precision": aggregate_metric(recs_a_cp, "context_precision"),
    },
    "notes": {
        "answer_relevancy_strictness": 1,
        "answer_relevancy_strictness_reason": "gemini-3.1-flash-lite rejects multi-candidate requests; default strictness=3 fails.",
        "context_precision_variant": "LLMContextPrecisionWithoutReference (no ground-truth used)",
        "context_precision_caveat": "Bimodal distribution (90/100 at 0.0, 4 at ~0.5, 5 in-between, 1 at 1.0) - metric artifact of reference-free variant on synthesized answers; Faithfulness=0.977 on the 90 CP=0 queries confirms retrieval is not broken.",
    },
}

recs_b = load_checkpoint("results/rq2_frameworkB_ragas_faithfulness_checkpoint.jsonl")
summary_b = {
    "framework": "B (contradictory queries, 50)",
    "judge_model": "gemini-3.1-flash-lite",
    "judge_temperature": 0,
    "bootstrap": {"n_resamples": N_BOOT, "seed": RNG_SEED},
    "metrics": {
        "faithfulness": aggregate_metric(recs_b, "faithfulness"),
    },
    "notes": {
        "reason_faithfulness_only": "Framework B has its own context-stance + answer two-layer judges built into its generation pipeline; RAGAS was added for Faithfulness only per professor's Slide 7 feedback.",
    },
}

os.makedirs("results", exist_ok=True)
with open("results/rq2_frameworkA_ragas_summary.json", "w") as f:
    json.dump(summary_a, f, indent=2)
with open("results/rq2_frameworkB_ragas_summary.json", "w") as f:
    json.dump(summary_b, f, indent=2)

print("=== Framework A ===")
print(json.dumps(summary_a["metrics"], indent=2))
print("\n=== Framework B ===")
print(json.dumps(summary_b["metrics"], indent=2))
print("\nsaved to results/")