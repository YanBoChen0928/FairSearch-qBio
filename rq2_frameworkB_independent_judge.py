"""
Independent judge for RQ2 Framework B (viewpoint-diversity retention).

Re-judges the answer-retention question with an INDEPENDENT model
(openai/gpt-oss-20b:free via OpenRouter) instead of the original self-judge
(gemini-3.1-flash-lite == the generation model). Only the 36 eligible queries
are re-judged, using the exact "answer two-layer judge" prompt from
prompt/frameworkb_judge_v1.md, so the only variable that changes vs. the
original run is the judge model.

Usage:
    export OPENROUTER_API_KEY=sk-or-v1-...
    python rq2_frameworkB_independent_judge.py

Inputs (already pulled into data/):
    data/rq2_frameworkB_generation_raw.jsonl   -- per-query: side_a, side_b, answer_text
    data/rq2_frameworkB_per_query.json          -- per-query: eligibility, original retention_status

Output:
    results/rq2_frameworkB_independent_judge_result.json
"""

import json
import os
import re
import time

import numpy as np
import requests

MODEL = "openai/gpt-oss-20b:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
SEED = 42
N_BOOT = 10000
SLEEP_SECONDS = 3.5  # free tier: 20 req/min -> stay well under it

# Verbatim "Prompt 2 of 2: answer two-layer judge" from prompt/frameworkb_judge_v1.md
JUDGE_PROMPT = """You are a careful analyst judging one generated answer to a debate question.

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
"""


def load_inputs():
    raw = {}
    with open("data/rq2_frameworkB_generation_raw.jsonl") as f:
        for line in f:
            r = json.loads(line)
            raw[r["query_id"]] = r
    with open("data/rq2_frameworkB_per_query.json") as f:
        per_query = {r["query_id"]: r for r in json.load(f)}
    eligible_ids = sorted(qid for qid, r in per_query.items() if r["eligibility"])
    return raw, per_query, eligible_ids


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.DOTALL).strip()
    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
    return json.loads(text)


def call_judge(api_key, side_a, side_b, query_id, answer_text):
    prompt = JUDGE_PROMPT.format(
        side_a=side_a, side_b=side_b, query_id=query_id, answer=answer_text
    )
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": MODEL,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(API_URL, headers=headers, json=body, timeout=90)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    return extract_json(content)


OUT_PATH = "results/rq2_frameworkB_independent_judge_result.json"


def load_previous_results():
    """Resume support: load any already-successful judgments from a prior run,
    so re-running only retries missing/ERROR queries instead of burning
    free-tier quota re-judging everything from scratch."""
    if not os.path.exists(OUT_PATH):
        return {}
    with open(OUT_PATH) as f:
        prev = json.load(f)
    return {
        q["query_id"]: q
        for q in prev.get("per_query", [])
        if q["retention_status"] != "ERROR"
    }


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    assert api_key, "Set OPENROUTER_API_KEY first (export OPENROUTER_API_KEY=sk-or-v1-...)"

    raw, per_query, eligible_ids = load_inputs()
    done = load_previous_results()
    todo = [qid for qid in eligible_ids if qid not in done]
    print(f"eligible queries: {len(eligible_ids)} | already judged: {len(done)} | to (re)run: {len(todo)}")

    results = list(done.values())
    for qid in todo:
        r = raw[qid]
        try:
            out = call_judge(api_key, r["side_a"], r["side_b"], qid, r["answer_text"])
        except Exception as e:
            print(f"  [warn] {qid} failed: {e}")
            out = {
                "query_id": qid,
                "retention_status": "ERROR",
                "conclusion_favor": None,
                "favor_basis": None,
                "evidence": str(e),
            }
        out["original_self_judge_retention_status"] = per_query[qid]["retention_status"]
        results.append(out)
        print(
            f"  {qid}: independent={out['retention_status']:<28} "
            f"self-judge={out['original_self_judge_retention_status']}"
        )
        time.sleep(SLEEP_SECONDS)

    results.sort(key=lambda r: r["query_id"])
    valid = [r for r in results if r["retention_status"] != "ERROR"]
    if len(valid) < len(results):
        print(f"\nWARNING: {len(results) - len(valid)} queries still errored; re-run again to retry them.")

    retained = np.array(
        [1 if r["retention_status"] == "both_sides_retained" else 0 for r in valid]
    )
    agree = np.array(
        [
            1 if r["retention_status"] == r["original_self_judge_retention_status"] else 0
            for r in valid
        ]
    )

    rng = np.random.default_rng(SEED)
    idx = np.arange(len(retained))
    boot = np.array(
        [retained[rng.choice(idx, size=len(idx), replace=True)].mean() for _ in range(N_BOOT)]
    )
    ci = np.percentile(boot, [2.5, 97.5])

    summary = {
        "framework": "B",
        "metric": "viewpoint_diversity_retention_rate",
        "judge_model": MODEL,
        "judge_is_self": False,
        "compared_against": "gemini-3.1-flash-lite self-judge (results/rq2_frameworkB_result.json)",
        "n_eligible": len(valid),
        "n_retained": int(retained.sum()),
        "retention_rate": float(retained.mean()),
        "ci_low": float(ci[0]),
        "ci_high": float(ci[1]),
        "n_boot": N_BOOT,
        "random_seed": SEED,
        "agreement_rate_vs_self_judge": float(agree.mean()),
        "n_disagreements": int(len(valid) - agree.sum()),
        "per_query": results,
    }

    os.makedirs("results", exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== SUMMARY ===")
    print(
        f"Independent judge ({MODEL}) retention: "
        f"{retained.mean():.4f} ({int(retained.sum())}/{len(valid)})  "
        f"95% CI [{ci[0]:.4f}, {ci[1]:.4f}]"
    )
    print("Original self-judge retention: 0.9722 (35/36), CI [0.9167, 1.0]")
    print(f"Agreement rate vs. self-judge: {agree.mean():.4f}  ({len(valid) - int(agree.sum())} disagreements)")
    print(f"saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
