"""
FairSearch-qBio - Step 9 Diagnostic Interface (Streamlit)

Reads app/data/step9_bundle.json, produced by Step 9-B
(notebooks/step9b-bundle-assembly-yb.ipynb). Pure renderer: every number
displayed comes from the bundle, nothing is computed here, per the Route A
architecture decision in step9_plan.md section 3.

Implements the interface decisions in step9_plan.md section 10b:
  - three-tier conditional structure (shared / neutral-only / contradictory-only)
  - baseline and intervention side by side, not stacked
  - Framework A inside BOTH columns, since amplification is a before/after quantity
  - method toggle as buttons, not a dropdown, so both methods stay visible
  - all papers listed, never collapsed to "+N more"
  - contradictory queries get no intervention panel, stated as a design decision
  - Framework B shows the generated answer, not only the verdict
  - per-query NDCG@10 / MRR shown per arm and in the delta table, so the
    query-level fairness-utility tradeoff is visible (the corpus average
    hides it: MMR barely moves, Fair-Top-K swings in both directions)
  - institutional balance bar has THREE segments (elite / non-elite / unlabeled)
    plus an explicit labeled-only share line. A two-segment full-width bar
    misreads as "8 of 10 papers are elite" when it actually means "80% of the
    5 labeled papers". See the 2026-08-03 addition to section 10b.

Run locally (inside the clean venv, see step9_streamlit_deployment.md section 3.1):
    pip install -r app/requirements.txt
    streamlit run app/streamlit_app.py
"""

import json
import re
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="FairSearch-qBio · Diagnostic Interface",
    page_icon="⚖️",
    layout="wide",
)

# ---------- Theme ----------
ELITE = "#D6A24C"
NONELITE = "#4FB6AE"
UNLABELED = "#5A6478"
CORAL = "#E2735F"
GOOD = "#6FBF8B"
DIM = "#8791A3"
SIDE_A = "#C084D8"
SIDE_B = "#5FA8E0"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #10141C; color: #EDEFF3; }}
    .pill-real {{
        font-family: monospace; font-size: 10.5px; padding: 2px 8px;
        border-radius: 100px; border: 1px solid {GOOD}; color: {GOOD};
        background: rgba(111,191,139,0.08);
    }}
    .pill-na {{
        font-family: monospace; font-size: 10.5px; padding: 2px 8px;
        border-radius: 100px; border: 1px solid {DIM}; color: {DIM};
        background: rgba(135,145,163,0.08);
    }}
    .paper-elite {{ border-left: 3px solid {ELITE}; padding: 6px 10px; margin-bottom:5px; background:#1D2330; border-radius:6px; font-size:13px;}}
    .paper-nonelite {{ border-left: 3px solid {NONELITE}; padding: 6px 10px; margin-bottom:5px; background:#1D2330; border-radius:6px; font-size:13px;}}
    .paper-unlabeled {{ border-left: 3px solid {UNLABELED}; padding: 6px 10px; margin-bottom:5px; background:#1D2330; border-radius:6px; font-size:13px;}}
    .paper-sa {{ border-left: 3px solid {SIDE_A}; padding: 6px 10px; margin-bottom:5px; background:#1D2330; border-radius:6px; font-size:13px;}}
    .paper-sb {{ border-left: 3px solid {SIDE_B}; padding: 6px 10px; margin-bottom:5px; background:#1D2330; border-radius:6px; font-size:13px;}}
    .answerbox {{ background:#171C27; border:1px solid #2A3140; border-radius:7px;
                  padding:11px 13px; font-size:13px; color:#D5DAE3; }}
    .notebox {{ border-left:3px solid {DIM}; background:#171C27; padding:10px 13px;
                border-radius:0 6px 6px 0; font-size:13px; color:#C6CCD6; }}
    a {{ color: {NONELITE}; }}
    div[data-testid="stButton"] button p {{
        white-space: nowrap; font-size: 13px;
    }}
    /* Anchor jump targets: Streamlit's toolbar is fixed at the top of the
       viewport, so a plain #anchor scroll lands the card underneath it and
       the NEXT card is what the reader sees. Offset the scroll position. */
    div[id^="cite-"] {{ scroll-margin-top: 90px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Load bundle ----------
BUNDLE_PATH = Path(__file__).parent / "data" / "step9_bundle.json"


@st.cache_data
def load_bundle():
    with open(BUNDLE_PATH) as f:
        return json.load(f)


try:
    bundle = load_bundle()
except FileNotFoundError:
    st.error(
        f"Bundle not found at `{BUNDLE_PATH}`. Run Step 9-B "
        "(`notebooks/step9b-bundle-assembly-yb.ipynb`) to generate it."
    )
    st.stop()

META = bundle["meta"]
QUERIES = {q["query_id"]: q for q in bundle["queries"]}
METHOD_LABEL = {m["id"]: m["label"] for m in META["rerank_methods"]}
METHOD_META = {m["id"]: m for m in META["rerank_methods"]}

# ---------- Header ----------
st.markdown("## FairSearch-qBio · Diagnostic Interface")
st.caption(
    f"Institutional bias audit over ~55,300 arXiv q-bio papers · "
    f"Tier {META['tier']} · {META['n_queries_in_bundle']} queries precomputed "
    f"({META['n_queries_neutral_total']} neutral + "
    f"{META['n_queries_contradictory_total']} contradictory in the full study)"
)

# ---------- Query selector ----------
ordered_ids = [q["query_id"] for q in bundle["queries"]]


def query_label(qid):
    rec = QUERIES[qid]
    anchor = " ★" if rec.get("is_anchor") else ""
    text = rec["query_text"]
    short = text if len(text) <= 70 else text[:67] + "..."
    return f"[{rec['type']}] {qid}{anchor} — {short}"


selected_id = st.selectbox("QUERY", options=ordered_ids, format_func=query_label)
rec = QUERIES[selected_id]
is_neutral = rec["type"] == "neutral"

st.markdown(f"#### \"{rec['query_text']}\"")
st.caption(
    f"Subcategory: **{rec['subcategory']}** · Type: **{rec['type']}** · "
    f"Elite list: **{META['elite_list']}** · "
    f"Generation: **{META['generation_model']}** (temperature "
    f"{META['generation_temperature']})"
    + ("  ·  ★ disclosed sampling anchor" if rec.get("is_anchor") else "")
)


# ---------- Shared helpers ----------
def paper_group(p):
    if p.get("coverage") == "found":
        return "elite" if p.get("elite_label") == 1 else "nonelite"
    return "unlabeled"


def composition(papers):
    """Return (n_elite, n_nonelite, n_unlabeled, n_total)."""
    e = sum(1 for p in papers if paper_group(p) == "elite")
    n = sum(1 for p in papers if paper_group(p) == "nonelite")
    u = sum(1 for p in papers if paper_group(p) == "unlabeled")
    return e, n, u, len(papers)


def balance_bar(papers):
    """Three-segment bar over ALL papers + an explicit labeled-only share line.

    Per step9_plan.md section 10b (2026-08-03): a two-segment full-width bar
    showing only the labeled ratio is misleading. Unlabeled papers must be
    visible, never hidden and never counted as 0.
    """
    e, n, u, total = composition(papers)
    if total == 0:
        st.caption("no papers")
        return
    pe, pn, pu = 100 * e / total, 100 * n / total, 100 * u / total

    def seg(pct, color, text):
        if pct <= 0:
            return ""
        label = (
            f'<span style="font-family:monospace; font-size:10px; color:#10141C;">{text}</span>'
            if pct >= 14
            else ""
        )
        return (
            f'<div style="width:{pct}%; background:{color}; display:flex; '
            f'align-items:center; justify-content:center;">{label}</div>'
        )

    st.markdown(
        '<div style="display:flex; height:22px; border-radius:6px; overflow:hidden; '
        'background:#1D2330;">'
        + seg(pe, ELITE, f"ELITE {pe:.0f}%")
        + seg(pn, NONELITE, f"NON-ELITE {pn:.0f}%")
        + seg(pu, UNLABELED, f"UNLABELED {pu:.0f}%")
        + "</div>",
        unsafe_allow_html=True,
    )
    labeled = e + n
    if labeled:
        st.caption(
            f"Top-{total} composition: **{e} elite · {n} non-elite · {u} unlabeled**  \n"
            f"Elite share among labeled papers: **{100 * e / labeled:.0f}%** "
            f"({e} of {labeled}) — this is the quantity RQ1/RQ2 fairness metrics use"
        )
    else:
        st.caption(
            f"Top-{total} composition: **0 elite · 0 non-elite · {u} unlabeled**  \n"
            "Elite share among labeled papers: **not evaluable** (no labeled papers)"
        )


def render_papers(papers, cited_ids, context_key, baseline_ids=None):
    """List every paper. Never collapse to '+N more' (section 10b).

    context_key namespaces the anchor ids (e.g. 'base-q018' vs
    'fair_top_k-q018') so citation links in render_answer() jump to the
    right card even when baseline and an intervention are both on screen
    for the same query with different papers at the same rank number."""
    cited = set(cited_ids or [])
    base = set(baseline_ids) if baseline_ids is not None else None
    for p in papers:
        grp = paper_group(p)
        css = {"elite": "paper-elite", "nonelite": "paper-nonelite",
               "unlabeled": "paper-unlabeled"}[grp]
        pid = p["paper_id"]
        title = p.get("title") or "(title unavailable)"
        anchor_id = f"cite-{context_key}-{p['rank']}"

        if grp == "unlabeled":
            meta = f"{p.get('coverage', 'not_found')} · unlabeled"
        else:
            meta = (
                f"{p.get('institution') or '(no institution)'} · "
                f"{p.get('country') or '??'} · "
                f"{'elite' if grp == 'elite' else 'non-elite'}"
            )

        tags = ""
        if pid in cited:
            tags += f' <span style="color:{NONELITE}; font-family:monospace; font-size:11px;">· cited</span>'
        if base is not None and pid not in base:
            tags += f' <span style="color:{CORAL}; font-family:monospace; font-size:11px;">· swapped in</span>'

        st.markdown(
            f'<div class="{css}" id="{anchor_id}">'
            f'<span style="font-family:monospace; color:{DIM}; font-size:11px;">{p["rank"]}</span> '
            f"{title}{tags}<br>"
            f'<a href="https://arxiv.org/abs/{pid}" target="_blank" '
            f'style="font-family:monospace; font-size:11px;">arXiv:{pid}</a> '
            f'<span style="font-family:monospace; font-size:11px; color:{DIM};"> · {meta}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )


def fmt(v, pct=False, signed=False):
    """Format a number that may legitimately be None ('not evaluable')."""
    if v is None:
        return "not evaluable"
    if pct:
        return f"{100 * v:+.1f}pp" if signed else f"{100 * v:.1f}%"
    return f"{v:+.4f}" if signed else f"{v:.4f}"


def framework_a_table(diag):
    """Framework A block. Empty denominators render as 'not evaluable', never 0."""
    st.markdown("**RQ2 Framework A — citation amplification**")
    st.markdown(
        f"""
        | Quantity | Value |
        |---|---|
        | context_elite_share | {fmt(diag.get('context_elite_share'))} |
        | cited_elite_share | {fmt(diag.get('cited_elite_share'))} |
        | **amplification** | **{fmt(diag.get('amplification'), signed=True)}** |
        """
    )


def ir_quality_line(diag):
    """Compact per-query IR quality line. n_relevant=0 is shown explicitly so a
    0.000 score reads as 'nothing matched the proxy', not as a missing value."""
    n = diag.get("ndcg_at_10")
    m = diag.get("mrr")
    nrel = diag.get("n_relevant")
    if n is None:
        return
    if nrel == 0:
        st.caption(
            f"NDCG@10 **{n:.3f}** · MRR **{m:.3f}** — "
            "no paper matched the subcategory proxy, so both are 0 by "
            "definition, not missing"
        )
    else:
        st.caption(
            f"NDCG@10 **{n:.3f}** · MRR **{m:.3f}** · "
            f"{nrel} of {10} papers relevant under the subcategory proxy"
        )


def render_answer(text, cited_ids, context_key):
    """Turn every [n] marker into a clickable link to that paper's card
    (anchor ids set in render_papers with the same context_key), so a
    citation can be checked in one click instead of counting rank numbers
    by eye."""
    def linkify(match):
        n = match.group(1)
        return (f'<a href="#cite-{context_key}-{n}" '
                f'style="color:{NONELITE}; text-decoration:none; font-weight:600;">[{n}]</a>')
    linked_text = re.sub(r"\[(\d+)\]", linkify, text)
    st.markdown(
        f'<div class="answerbox">{linked_text}</div>', unsafe_allow_html=True
    )
    st.caption(f"cited papers: {len(cited_ids)} unique · [n] markers link to the paper card below")


# ---------- Shared metric strip ----------
st.markdown("---")
base_papers = rec["baseline"]["papers"]
be, bn, bu, btot = composition(base_papers)
b_labeled = be + bn

bdg = rec["baseline"]["diagnostics"]
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric(
        "ELITE SHARE (labeled only)",
        f"{100 * be / b_labeled:.0f}%" if b_labeled else "n/a",
        help="Elite papers as a fraction of LABELED papers only. Unlabeled "
             "papers are excluded from the denominator, never counted as 0. "
             "0% is common and expected: the corpus-wide retrieved elite share "
             "is only about 17%, so with roughly 6 labeled slots per query, "
             "many queries legitimately retrieve no elite paper at all.",
    )
with m2:
    st.metric("UNIQUE INSTITUTIONS", bdg.get("uniq_institutions", "n/a"))
with m3:
    st.metric(
        "NDCG@10 (baseline)",
        f"{bdg['ndcg_at_10']:.3f}" if bdg.get("ndcg_at_10") is not None else "n/a",
        help="Per-query NDCG@10 under the binary subcategory-match relevance "
             "proxy (the same proxy RQ3 uses). Coarse by construction: it asks "
             "only whether a paper's arXiv categories string contains the "
             "query's target subcategory, not whether it is semantically "
             "relevant. Illustrative per query; the aggregate figure lives in "
             "rq3_methodology.md.",
    )
with m4:
    fa = rec["faithfulness"]
    st.metric(
        "FAITHFULNESS (this query)",
        f"{fa['score']:.3f}" if fa.get("score") is not None else fa.get("status", "n/a"),
        help="RAGAS Faithfulness, Step 8. Self-judge design (same model as "
             "generation), disclosed in step8.md section 3.",
    )
with m5:
    st.metric(
        "COVERAGE",
        f"{META['n_queries_in_bundle']} queries",
        help="Tier 1 precomputed scope. The interface shows its real coverage "
             "rather than implying full-corpus coverage.",
    )

st.caption(
    "Per-query numbers are diagnostic illustrations. Aggregate statistical "
    "claims (SPD, NDCG@10, MRR, bootstrap CIs) live in "
    "`results/rq3_results.json` and `rq3_methodology.md`, computed over the "
    "full 100-query neutral set, not over this subset."
)

# ---------- Side-by-side comparison ----------
st.markdown("---")
col_base, col_inter = st.columns(2)

with col_base:
    hl, hr = st.columns([4, 6])
    with hl:
        st.markdown("#### ① Baseline retrieval")
    with hr:
        # Disabled button, not decoration: it occupies the same slot as the
        # method toggle opposite, so both "Institution mix" bars start at the
        # same vertical position instead of the right one sitting lower.
        st.button("No re-ranking", disabled=True, use_container_width=True,
                  key="btn_baseline_placeholder")
    st.markdown('<span class="pill-real">real data</span>', unsafe_allow_html=True)

    st.markdown("**Institution mix**")
    balance_bar(base_papers)
    ir_quality_line(rec["baseline"]["diagnostics"])

    st.markdown(f"**Retrieved papers (all {btot} shown)**")
    render_papers(base_papers, rec["baseline"]["cited_paper_ids"], context_key=f"base-{selected_id}")

    st.markdown("**Generated answer**")
    render_answer(rec["baseline"]["answer_text"], rec["baseline"]["cited_paper_ids"],
                  context_key=f"base-{selected_id}")

    if is_neutral:
        framework_a_table(rec["baseline"]["diagnostics"])

with col_inter:
    if not is_neutral:
        hl, hr = st.columns([4, 6])
        with hl:
            st.markdown("#### ② RQ3 intervention")
        with hr:
            st.button("Not applicable", disabled=True, use_container_width=True,
                      key="btn_contra_placeholder")
        st.markdown('<span class="pill-na">not applicable by design</span>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="notebox"><strong>By design, not missing.</strong> '
            "q101\u2013q150 were pre-registered as the Experiment B set and held out "
            "of RQ1 and RQ3, so the institution axis and the viewpoint axis stay "
            "separable (<code>rq2_methodology.md</code> \u00a71). No re-ranking output "
            "exists for these queries, and Framework A is not computed for them "
            "either.</div>",
            unsafe_allow_html=True,
        )
    else:
        method_ids = [m["id"] for m in META["rerank_methods"]]
        if "method" not in st.session_state or st.session_state.method not in method_ids:
            st.session_state.method = method_ids[0]

        # Toggle sits in the header row, opposite the "No re-ranking" placeholder
        # in the baseline column, so both institution-mix bars line up.
        hl, *hbtns = st.columns([4] + [3] * len(method_ids))
        with hl:
            st.markdown("#### ② RQ3 intervention")
        for c, mid in zip(hbtns, method_ids):
            mm_ = METHOD_META[mid]
            tip = (
                f"Soft penalty, lambda={mm_['lambda']}. Adjusts scores, fixes no "
                "seat. Penalises repeated institutions, so it moves "
                "uniq_institutions most."
                if mm_["family"] == "soft_penalty"
                else
                f"Hard quota: elite seats capped at {mm_['elite_quota']}, target "
                f"share {mm_['target_share']}. Targets elite share directly. "
                "Measured corpus-wide as a statistically significant "
                "over-correction into reverse bias (rq3_methodology.md 8a)."
            )
            with c:
                if st.button(
                    METHOD_LABEL[mid],
                    key=f"btn_{mid}",
                    use_container_width=True,
                    help=tip,
                    type="primary" if st.session_state.method == mid else "secondary",
                ):
                    st.session_state.method = mid
                    st.rerun()

        method = st.session_state.method
        mm = METHOD_META[method]
        iv = rec["interventions"][method]

        st.markdown('<span class="pill-real">real data</span>', unsafe_allow_html=True)

        st.markdown("**Institution mix**")
        balance_bar(iv["papers"])
        ir_quality_line(iv["diagnostics"])

        st.markdown(f"**Re-ranked papers (all {len(iv['papers'])} shown)**")
        render_papers(
            iv["papers"],
            iv["cited_paper_ids"],
            context_key=f"{method}-{selected_id}",
            baseline_ids=[p["paper_id"] for p in base_papers],
        )

        st.markdown("**Generated answer from re-ranked context**")
        render_answer(iv["answer_text"], iv["cited_paper_ids"], context_key=f"{method}-{selected_id}")

        framework_a_table(iv["diagnostics"])

        if mm["family"] == "soft_penalty":
            st.caption(
                f"**Soft penalty** (\u03bb={mm['lambda']}) \u2014 scores adjusted, no seat "
                "fixed; penalises repeated institutions."
            )
        else:
            st.caption(
                f"**Hard quota** \u2014 elite seats capped at {mm['elite_quota']}, "
                f"target share {mm['target_share']}; measured corpus-wide as a "
                "significant over-correction into reverse bias."
            )
        st.markdown(
            f'<div style="font-size:12px; color:{DIM};">'
            f'<span style="font-family:monospace; color:{NONELITE};">cited</span> = appears '
            "in the generated answer above &nbsp;\u00b7&nbsp; "
            f'<span style="font-family:monospace; color:{CORAL}; font-weight:600;">swapped in</span> '
            "= not in the baseline Top-10, added by this re-ranking method</div>",
            unsafe_allow_html=True,
        )

# ---------- Delta block, neutral only ----------
if is_neutral:
    st.markdown("---")
    method = st.session_state.method
    iv = rec["interventions"][method]
    d = iv["delta_vs_baseline"]
    bd = rec["baseline"]["diagnostics"]
    idg = iv["diagnostics"]

    with st.expander(f"Baseline → {METHOD_LABEL[method]} delta", expanded=True):
        st.markdown(
            f"""
            | Metric | Baseline | Intervention | Δ |
            |---|---|---|---|
            | **NDCG@10** | {bd.get('ndcg_at_10'):.4f} | {idg.get('ndcg_at_10'):.4f} | {d.get('ndcg_at_10'):+.4f} |
            | **MRR** | {bd.get('mrr'):.4f} | {idg.get('mrr'):.4f} | {d.get('mrr'):+.4f} |
            | context_elite_share | {fmt(bd.get('context_elite_share'))} | {fmt(idg.get('context_elite_share'))} | {fmt(d.get('context_elite_share'), signed=True)} |
            | cited_elite_share | {fmt(bd.get('cited_elite_share'))} | {fmt(idg.get('cited_elite_share'))} | — |
            | amplification | {fmt(bd.get('amplification'), signed=True)} | {fmt(idg.get('amplification'), signed=True)} | — |
            | uniq_institutions | {bd.get('uniq_institutions')} | {idg.get('uniq_institutions')} | {d.get('uniq_institutions'):+d} |
            | uniq_countries | {bd.get('uniq_countries')} | {idg.get('uniq_countries')} | {d.get('uniq_countries'):+d} |
            | papers changed | — | — | {d.get('n_papers_changed')} of {len(base_papers)} |
            """
        )
        st.caption(
            "Deltas are precomputed in the bundle by Step 9-B, not derived here, "
            "so the UI stays a pure renderer (step9_plan.md §10a). NDCG@10 and MRR "
            "use the binary subcategory-match proxy; a per-query change here is "
            "illustrative of how the two methods behave differently, not a "
            "statistical claim — the corpus-level figures over all 100 neutral "
            "queries are in rq3_methodology.md §4.2 and §8a."
        )

# ---------- Framework B block, contradictory only ----------
if not is_neutral:
    st.markdown("---")
    fb = rec["framework_b"]
    with st.expander("RQ2 Framework B — viewpoint retention", expanded=True):
        st.markdown("**The two stated positions**")
        st.markdown(
            f'<div style="color:{SIDE_A}; font-size:13px;">side_a — {fb["side_a"]}</div>'
            f'<div style="color:{SIDE_B}; font-size:13px;">side_b — {fb["side_b"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Retrieved context, coloured by stance**")
        stance_css = {"supports_side_a": "paper-sa", "supports_side_b": "paper-sb"}
        pid_to_paper = {p["paper_id"]: p for p in rec["baseline"]["papers"]}
        for s in fb["context_stances"]:
            pid = s["paper_id"]
            p = pid_to_paper.get(pid, {})
            css = stance_css.get(s["stance"], "paper-unlabeled")
            title = p.get("title") or "(title unavailable)"
            st.markdown(
                f'<div class="{css}">'
                f'<span style="font-family:monospace; color:{DIM}; font-size:11px;">{s["n"]}</span> '
                f"{title}<br>"
                f'<a href="https://arxiv.org/abs/{pid}" target="_blank" '
                f'style="font-family:monospace; font-size:11px;">arXiv:{pid}</a> '
                f'<span style="font-family:monospace; font-size:11px; color:{DIM};"> · {s["stance"]}</span>'
                f'<div style="font-size:12px; color:#AEB6C4; font-style:italic; margin-top:3px;">'
                f'"{s["evidence"]}"</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("**Answer-layer judgment**")
        st.markdown(
            f"""
            | Field | Value |
            |---|---|
            | retention_status | **{fb['retention_status']}** |
            | conclusion_favor | {fb['conclusion_favor']} |
            | favor_basis | {fb['favor_basis']} |
            """
        )
        st.markdown(
            f'<div class="notebox">{fb["judge_evidence"]}</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Corpus level: 36 of 50 contradictory queries were eligible (context "
            "contained both sides), 35 of those retained both sides — retention "
            "97.2%, 95% CI [91.7%, 100.0%]. Favouring one side is not a failure: "
            "retention asks whether both sides survived into the answer, not "
            "whether the answer stayed undecided. Judge is a self-judge (same "
            "model as generation), disclosed in rq2_methodology.md §3.4."
        )

# ---------- Shared RAGAS footer ----------
st.markdown("---")
with st.expander("RAG answer quality — RAGAS Faithfulness (Step 8)", expanded=False):
    st.markdown('<span class="pill-real">real data</span>', unsafe_allow_html=True)
    fmean = META["faithfulness_corpus_mean"]
    fbytype = META["faithfulness_by_type"]

    f1, f2, f3 = st.columns(3)
    with f1:
        fa = rec["faithfulness"]
        st.metric(
            f"THIS QUERY · {selected_id}",
            f"{fa['score']:.3f}" if fa.get("score") is not None else fa.get("status"),
        )
    with f2:
        st.metric("CORPUS MEAN", f"{fmean['mean']:.4f}")
        st.caption(f"{fmean['n']} of 150 queries scored")
    with f3:
        parts = []
        for k, v in fbytype.items():
            mval = v.get("mean") if isinstance(v, dict) else v
            parts.append(f"{k} {mval:.4f}" if isinstance(mval, float) else f"{k} {mval}")
        st.metric("BY QUERY TYPE", " / ".join(parts) if parts else "n/a")

    st.caption(
        "Faithfulness measures whether claims in the generated answer are "
        "supported by the retrieved abstracts. Judge model "
        f"{META['generation_model']}, the same model used for generation, so "
        "this is a self-judge design (step8.md §3). Two queries (q032, q068) "
        "failed reproducibly on an upstream structured-output error and are "
        "excluded rather than imputed. RAGAS Answer Relevancy was attempted "
        "and found infeasible on this stack; Context Precision was not run and "
        "is carried as a disclosed limitation (step8.md §2b, §4a.8)."
    )

st.markdown("---")
st.caption(
    f"FairSearch-qBio · Step 9 diagnostic interface · Tier "
    f"{META['tier']}: {META['n_queries_in_bundle']} of "
    f"{META['n_queries_neutral_total'] + META['n_queries_contradictory_total']} "
    f"queries precomputed (sampling seed {META['sampling_seed']}, method in "
    "step9_query_subset.md §2) · bundle generated "
    f"{META['generated_at']}"
)
