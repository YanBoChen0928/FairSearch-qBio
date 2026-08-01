"""
FairSearch-qBio - Step 9 Diagnostic Interface (Streamlit)

Status: DEPLOYMENT DRY RUN. Data is still the hardcoded mock carried over
from step9_streamlit_demo_draft.py. Baseline panel uses real data for query
q033 (from retrieval_results.json / retrieval_labels.json / qbio_papers.json).
The RQ3-intervention panel is illustrative only: the real per-query MMR
re-rank output has not been generated yet (see step9_plan.md §2, the Step
9-A gap). Do NOT present the intervention numbers as real results.

Purpose of this file existing before real data: it lets the Streamlit
Community Cloud deployment path be tested end to end while Step 9-A/B are
still in progress. See step9_streamlit_deployment.md.

When the real bundle lands, only two things change (deployment §7):
  1. app/data/step9_bundle.json is added to the repo
  2. BASELINE_PAPERS / INTERVENTION_PAPERS_MOCK below are replaced by a
     JSON read, and the selectbox is populated from the bundle

Run locally (inside the clean venv, see deployment doc §3.1):
    pip install -r app/requirements.txt
    streamlit run app/streamlit_app.py
"""

import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="FairSearch-qBio · Diagnostic Interface",
    page_icon="⚖️",
    layout="wide",
)

# ---------- Theme (matches the HTML concept demo) ----------
ELITE = "#D6A24C"
NONELITE = "#4FB6AE"
CORAL = "#E2735F"
GOOD = "#6FBF8B"
DIM = "#8791A3"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #10141C; color: #EDEFF3; }}
    .badge {{
        font-family: monospace; font-size: 11px; padding: 3px 9px;
        border-radius: 100px; border: 1px solid {CORAL}; color: {CORAL};
        background: rgba(226,115,95,0.08); display:inline-block;
    }}
    .pill-real {{
        font-family: monospace; font-size: 10.5px; padding: 2px 8px;
        border-radius: 100px; border: 1px solid {GOOD}; color: {GOOD};
        background: rgba(111,191,139,0.08);
    }}
    .pill-illustrative {{
        font-family: monospace; font-size: 10.5px; padding: 2px 8px;
        border-radius: 100px; border: 1px solid {CORAL}; color: {CORAL};
        background: rgba(226,115,95,0.08);
    }}
    .paper-elite {{ border-left: 3px solid {ELITE}; padding: 6px 10px; margin-bottom:6px; background:#1D2330; border-radius:6px;}}
    .paper-nonelite {{ border-left: 3px solid {NONELITE}; padding: 6px 10px; margin-bottom:6px; background:#1D2330; border-radius:6px;}}
    .paper-unlabeled {{ border-left: 3px solid #2A3140; padding: 6px 10px; margin-bottom:6px; background:#1D2330; border-radius:6px;}}
    .paper-mock {{ border-left: 3px solid {CORAL}; padding: 6px 10px; margin-bottom:6px; background:#1D2330; border-radius:6px;}}
    a {{ color: {NONELITE}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown("## FairSearch-qBio · Diagnostic Interface")
with col_badge:
    st.markdown('<div class="badge">CONCEPT DEMO · NOT FINAL</div>', unsafe_allow_html=True)

# ---------- Query metadata (mock for now; Step 9-B will populate this
# from step9_bundle.json without changing the selection logic below) ----------
QUERY_META = {
    "q033": {"type": "neutral", "tier": 1,
             "short": "ML approaches for regulatory elements (worked example)"},
    "q001": {"type": "neutral", "tier": 1,
             "short": "SDE gene expression noise (pending Step 9-A)"},
    "q101": {"type": "contradictory", "tier": 2,
             "short": "junk DNA debate (pending Step 9-A)"},
}

show_all_tiers = st.checkbox(
    "Show all 150 queries (Tier 2)",
    value=False,
    help="Off = the ~20-query Tier 1 subset only (step9_plan.md §8). "
         "On = extends to full 150-query coverage if that tier has run.",
)
max_tier = 2 if show_all_tiers else 1
visible_ids = [k for k, v in QUERY_META.items() if v["tier"] <= max_tier]

st.caption(
    f"Showing {len(visible_ids)} of {len(QUERY_META)} queries "
    f"(tiered scope per step9_plan.md §8)"
)

selected = st.selectbox(
    "QUERY",
    options=visible_ids,
    format_func=lambda k: f"[{QUERY_META[k]['type']}] {k} — {QUERY_META[k]['short']}",
)

if selected != "q033":
    st.warning(
        "This query is not yet wired up — Step 9-A (per-query RQ3-intervention "
        "generation) has not been run. q033 is currently the only fully "
        "populated worked example in this concept demo."
    )
    st.stop()

st.markdown(
    "#### \"What machine learning approaches predict gene regulatory "
    "elements from DNA sequence?\""
)
st.caption(
    "Subcategory: **q-bio.GN** · Retrieved: **10 papers** · "
    "Elite list: **QS Top-50** · Baseline data: **real** "
    "(`retrieval_results.json`)"
)

# ---------- Key metrics summary (moved to top per Prof. Sushmita's
# feedback: "key metrics like NDCG@10 moved to the top of the interface") ----------
st.markdown("---")
d1, d2, d3, d4 = st.columns(4)
with d1:
    st.metric("ELITE SHARE (found)", "40%", "-40pp (mock)", delta_color="inverse")
with d2:
    st.metric("UNIQUE INSTITUTIONS", "4 (mock)", "+1")
with d3:
    st.metric("NDCG@10", "≈ flat", "per rq3_methodology.md §4.2")
with d4:
    st.markdown(
        f'<div style="font-family:monospace; font-size:11px; color:{DIM};">DATA STATUS</div>'
        f'<div style="color:{CORAL}; font-size:14px;">baseline real · intervention illustrative</div>',
        unsafe_allow_html=True,
    )

# ---------- Balance strip (signature element) ----------
st.markdown("---")
st.caption("INSTITUTIONAL BALANCE · SHARE OF LABELED (found) PAPERS")


def balance_bar(label, elite_pct, badge=None):
    nonelite_pct = 100 - elite_pct
    badge_html = f' <span style="color:{CORAL}">{badge}</span>' if badge else ""
    st.markdown(f"**{label}**{badge_html}", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="display:flex; height:24px; border-radius:6px; overflow:hidden; background:#1D2330;">
          <div style="width:{elite_pct}%; background:{ELITE}; display:flex; align-items:center; justify-content:flex-end; padding-right:6px;">
            <span style="font-family:monospace; font-size:10px; color:#10141C;">ELITE {elite_pct}%</span>
          </div>
          <div style="width:{nonelite_pct}%; background:{NONELITE}; display:flex; align-items:center; padding-left:6px;">
            <span style="font-family:monospace; font-size:10px; color:#10141C;">NON-ELITE {nonelite_pct}%</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


balance_bar("Baseline", 80)
balance_bar("RQ3 λ=0.8", 40, badge="(illustrative)")

# ---------- Comparison panel ----------
st.markdown("---")
col_base, col_inter = st.columns(2)


def donut(elite, nonelite, unlabeled, colors):
    fig, ax = plt.subplots(figsize=(2.2, 2.2))
    fig.patch.set_alpha(0)
    ax.pie(
        [elite, nonelite, unlabeled],
        colors=colors,
        wedgeprops=dict(width=0.42, edgecolor="#10141C"),
        startangle=90,
    )
    ax.set_aspect("equal")
    return fig


BASELINE_PAPERS = [
    ("unlabeled", True, "Advancing regulatory genomics with machine learning",
     "2304.12963", "unlabeled"),
    ("unlabeled", True, "Prediction of a Gene Regulatory Network from Gene Expression Profiles",
     "1805.01506", "unlabeled"),
    ("unlabeled", False, "Machine Learning Methods for Gene Regulatory Network Inference",
     "2504.12610", "unlabeled"),
    ("elite", False, "Predicting Genetic Regulatory Response using Classification: Yeast Stress Response",
     "q-bio/0406016", "Columbia University · US · elite"),
    ("elite", False, "Predicting Genetic Regulatory Response Using Classification",
     "q-bio/0411028", "Columbia University · US · elite"),
    ("elite", True, "Motif Discovery through Predictive Modeling of Gene Regulation",
     "q-bio/0701021", "Columbia University · US · elite"),
    ("unlabeled", True, "Prediction of Signal Sequences in Abiotic Stress Inducible Genes from Arabidopsis",
     "1811.07269", "unlabeled"),
    ("nonelite", False, "SIRENE: Supervised Inference of Regulatory Networks",
     "0802.3959", "Inserm · FR · non-elite"),
    ("unlabeled", True, "Learning to Discover Regulatory Elements for Gene Expression Prediction",
     "2502.13991", "unlabeled"),
    ("elite", True, "A multi-modal neural network for learning cis and trans regulation of stress response",
     "1908.09426", "Stanford University · US · elite"),
]

with col_base:
    st.markdown("#### ① Baseline retrieval → answer")
    st.markdown('<span class="pill-real">real data</span>', unsafe_allow_html=True)

    st.markdown("**Institution mix (Top-10)**")
    fig = donut(4, 1, 5, [ELITE, NONELITE, "#2A3140"])
    st.pyplot(fig, width="content")
    st.caption("Elite: 4 · Non-elite: 1 · Unlabeled: 5 · Elite share of found: **80%**")

    st.markdown("**Retrieved papers**")
    for group, rel, title, pid, label in BASELINE_PAPERS:
        css_class = f"paper-{group}"
        rel_marker = "🟢" if rel else "⚪"
        url = f"https://arxiv.org/abs/{pid}"
        st.markdown(
            f'<div class="{css_class}">{rel_marker} {title}<br>'
            f'<a href="{url}" target="_blank" style="font-family:monospace; font-size:11px;">arXiv:{pid}</a>'
            f' &nbsp; <span style="font-family:monospace; font-size:11px; color:{DIM};">{label}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("**Generated answer (Step 7a, illustrative wording)**")
    st.info(
        "Recent approaches combine sequence-based deep learning with classical "
        "motif discovery [1][2]. Supervised classification methods trained on "
        "expression profiles remain a strong baseline [4][5], while multi-modal "
        "neural networks jointly model cis- and trans-acting elements [10]. "
        "Motif-based predictive modeling continues to complement these methods [6].\n\n"
        "*(placeholder wording — not the stored Gemini output; see "
        "rq2_methodology.md §2.1 for the real prompt design)*"
    )

INTERVENTION_PAPERS_MOCK = [
    ("unlabeled", True, "Advancing regulatory genomics with machine learning",
     "2304.12963", "unlabeled · kept"),
    ("unlabeled", True, "Prediction of a Gene Regulatory Network from Gene Expression Profiles",
     "1805.01506", "unlabeled · kept"),
    ("elite", False, "Predicting Genetic Regulatory Response using Classification: Yeast Stress Response",
     "q-bio/0406016", "Columbia University · US · elite · kept (highest-relevance duplicate)"),
    ("elite", True, "Motif Discovery through Predictive Modeling of Gene Regulation",
     "q-bio/0701021", "Columbia University · US · elite · kept"),
    ("mock", False, "[mock swap-in — illustrative only] Regulatory network inference via graph neural networks",
     None, "mock non-elite institution · replaces 2nd Columbia duplicate"),
]

with col_inter:
    st.markdown("#### ② RQ3 re-rank (λ=0.8) → answer")
    st.markdown('<span class="pill-illustrative">illustrative — pending Step 9-A</span>',
                unsafe_allow_html=True)

    st.markdown("**Institution mix (Top-10, mocked)**")
    fig2 = donut(2, 3, 5, [ELITE, NONELITE, "#2A3140"])
    st.pyplot(fig2, width="content")
    st.caption("Elite: 2 · Non-elite: 3 · Unlabeled: 5 · Elite share of found: **40%**")

    st.markdown("**Re-ranked papers (mock — real MMR output not yet generated)**")
    for group, rel, title, pid, label in INTERVENTION_PAPERS_MOCK:
        css_class = f"paper-{group}"
        rel_marker = "🟢" if rel else "⚪"
        if pid:
            link = (f'<a href="https://arxiv.org/abs/{pid}" target="_blank" '
                    f'style="font-family:monospace; font-size:11px;">arXiv:{pid}</a>')
        else:
            link = ""
        st.markdown(
            f'<div class="{css_class}">{rel_marker} {title}<br>'
            f'{link} &nbsp; <span style="font-family:monospace; font-size:11px; color:{CORAL};">{label}</span></div>',
            unsafe_allow_html=True,
        )
    st.caption("+ 5 more papers (mock, not shown)")

st.markdown("---")
st.caption(
    "FairSearch-qBio · Step 9 deployment dry run · 1 of 150 queries populated "
    "(q033 worked example) · tiered scope per step9_plan.md §8: Tier 1 is the "
    "~20-query subset, Tier 2 extends to all 150 if quota allows"
)
