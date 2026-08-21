"""
app.py
------
Streamlit front end for the Bacterial Identification Assistant.

This file only handles UI: drawing inputs, calling into
utils/identification.py, and displaying results. All identification
logic lives in that module on purpose. The optional AI explanation
layer (utils/ai_explain.py) is called only after a result has already
been computed deterministically — it never identifies anything itself.
"""

import random
import pandas as pd
import streamlit as st

from utils.identification import load_database, identify, TEST_COLUMNS, NOT_TESTED

try:
    from utils.ai_explain import explain_result
except Exception:
    explain_result = None  # AI layer is optional; app must work without it

st.set_page_config(page_title="Bacterial Identification Assistant", page_icon="🧫", layout="centered")

DB = load_database()

# ----------------------------------------------------------------------
# VISUAL IDENTITY
#
# The color coding is not decorative: violet/lavender marks Gram-positive
# organisms (they retain crystal violet stain) and rose/red marks
# Gram-negative organisms (they take up the safranin counterstain) — the
# same convention students already use at the bench.
# ----------------------------------------------------------------------

def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

        :root {
            --ink: #24242b;
            --ink-soft: #5b5b66;
            --paper: #faf9f5;
            --card: #ffffff;
            --line: #e6e3da;
            --gram-pos: #6b3fa0;
            --gram-pos-bg: #f2ecf9;
            --gram-neg: #c1445a;
            --gram-neg-bg: #fbecef;
            --match: #2f7d55;
            --match-bg: #eaf5ee;
            --mismatch: #b3492f;
            --mismatch-bg: #fbeee9;
            --variable: #b8862c;
            --variable-bg: #fbf3e3;
            --accent: #1f6f6b;
        }

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
            color: var(--ink);
        }

        .stApp {
            background: var(--paper);
        }

        /* ---------- Hero header ---------- */
        .bia-hero {
            padding: 2.1rem 1.8rem 1.8rem 1.8rem;
            background: linear-gradient(155deg, #1f6f6b 0%, #164f4c 100%);
            border-radius: 18px;
            margin-bottom: 1.4rem;
            box-shadow: 0 8px 24px rgba(22, 79, 76, 0.18);
        }
        .bia-hero .eyebrow {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #bfe3d9;
            margin-bottom: 0.5rem;
        }
        .bia-hero h1 {
            font-family: 'Fraunces', serif;
            font-weight: 600;
            font-size: 2.05rem;
            color: #ffffff;
            margin: 0 0 0.35rem 0;
            line-height: 1.15;
        }
        .bia-hero p {
            color: #d9ece7;
            font-size: 0.98rem;
            margin: 0;
            max-width: 46ch;
        }

        .bia-notice {
            background: #fff8ec;
            border: 1px solid #f0dfb3;
            border-left: 4px solid #b8862c;
            border-radius: 10px;
            padding: 0.85rem 1.05rem;
            font-size: 0.88rem;
            color: #6b5427;
            margin-bottom: 1.6rem;
        }

        /* ---------- Section labels ---------- */
        .bia-section-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--accent);
            margin: 1.6rem 0 0.35rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .bia-section-label::after {
            content: "";
            flex: 1;
            height: 1px;
            background: var(--line);
        }
        .bia-section-title {
            font-family: 'Fraunces', serif;
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--ink);
            margin: 0 0 0.9rem 0;
        }

        /* ---------- Buttons ---------- */
        .stButton > button {
            background: var(--accent);
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            font-size: 0.95rem;
            transition: transform 0.08s ease, box-shadow 0.15s ease;
            box-shadow: 0 2px 6px rgba(31, 111, 107, 0.25);
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(31, 111, 107, 0.32);
            color: #ffffff;
        }

        /* ---------- Result card ---------- */
        .bia-result-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 1.3rem 1.4rem;
            margin-bottom: 1.1rem;
            display: flex;
            gap: 1.3rem;
            align-items: center;
        }
        .bia-ring {
            width: 84px;
            height: 84px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            position: relative;
        }
        .bia-ring::before {
            content: "";
            position: absolute;
            inset: 8px;
            background: var(--card);
            border-radius: 50%;
        }
        .bia-ring-score {
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 600;
            font-size: 1.05rem;
            z-index: 1;
            color: var(--ink);
        }
        .bia-result-name {
            font-family: 'Fraunces', serif;
            font-size: 1.18rem;
            font-weight: 600;
            margin: 0 0 0.3rem 0;
            color: var(--ink);
        }
        .bia-tag {
            display: inline-block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            font-weight: 600;
        }
        .bia-tag-pos { background: var(--gram-pos-bg); color: var(--gram-pos); }
        .bia-tag-neg { background: var(--gram-neg-bg); color: var(--gram-neg); }

        /* ---------- Comparison table ---------- */
        .bia-comp-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.6rem;
            font-size: 0.87rem;
        }
        .bia-comp-table td {
            padding: 0.5rem 0.6rem;
            border-bottom: 1px solid var(--line);
        }
        .bia-comp-table tr:last-child td { border-bottom: none; }
        .bia-comp-test { color: var(--ink-soft); width: 30%; }
        .bia-comp-vals { font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; }
        .bia-status-pill {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            white-space: nowrap;
        }
        .bia-status-match { background: var(--match-bg); color: var(--match); }
        .bia-status-mismatch { background: var(--mismatch-bg); color: var(--mismatch); }
        .bia-status-variable { background: var(--variable-bg); color: var(--variable); }

        .bia-note {
            font-size: 0.83rem;
            color: var(--ink-soft);
            font-style: italic;
            margin-top: 0.5rem;
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--line);
            border-radius: 12px;
            background: var(--card);
        }

        /* ---------- Footer ---------- */
        .bia-footer {
            margin-top: 2.4rem;
            padding-top: 1.2rem;
            border-top: 1px solid var(--line);
            text-align: center;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            color: var(--ink-soft);
            letter-spacing: 0.02em;
        }
        .bia-footer strong {
            color: var(--accent);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def score_ring_html(score: int, gram: str) -> str:
    color = "#6b3fa0" if gram == "Positive" else "#c1445a"
    return f"""
    <div class="bia-ring" style="background: conic-gradient({color} {score * 3.6}deg, #eee2 0deg);">
        <span class="bia-ring-score">{score}%</span>
    </div>
    """


def gram_tag_html(gram: str) -> str:
    if gram == "Positive":
        return '<span class="bia-tag bia-tag-pos">GRAM POSITIVE</span>'
    if gram == "Negative":
        return '<span class="bia-tag bia-tag-neg">GRAM NEGATIVE</span>'
    return ""


def comparison_table_html(comparisons) -> str:
    status_class = {
        "Match": "bia-status-match",
        "Mismatch": "bia-status-mismatch",
        "Consistent (variable)": "bia-status-variable",
    }
    rows = ""
    for test, user_val, db_val, status in comparisons:
        cls = status_class.get(status, "bia-status-match")
        rows += f"""
        <tr>
            <td class="bia-comp-test">{test}</td>
            <td class="bia-comp-vals">{user_val} → {db_val}</td>
            <td><span class="bia-status-pill {cls}">{status}</span></td>
        </tr>
        """
    return f'<table class="bia-comp-table">{rows}</table>'


inject_css()

# ----------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class="bia-hero">
        <div class="eyebrow">Clinical Bacteriology · Decision Support Tool</div>
        <h1>🧫 Bacterial Identification Assistant</h1>
        <p>Enter Gram stain, morphology, and biochemical test results to see a
        transparent, database-driven match — built for MLT students learning
        the identification workflow.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="bia-notice">
        <strong>Educational use only.</strong> This tool is not intended to replace
        laboratory procedures, validated identification systems, antimicrobial
        susceptibility testing, professional interpretation, or clinical diagnosis.
    </div>
    """,
    unsafe_allow_html=True,
)

# Options for each test, in the order we want them shown.
OPTIONS = {
    "Gram": [NOT_TESTED, "Positive", "Negative"],
    "Shape": [NOT_TESTED, "Cocci", "Rod"],
    "Arrangement": [NOT_TESTED, "Clusters", "Chains", "Pairs (diplococci)", "Single/short chains", "Single/pairs"],
    "Catalase": [NOT_TESTED, "Positive", "Negative"],
    "Coagulase": [NOT_TESTED, "Positive", "Negative"],
    "Oxidase": [NOT_TESTED, "Positive", "Negative"],
    "Indole": [NOT_TESTED, "Positive", "Negative"],
    "Urease": [NOT_TESTED, "Positive", "Negative"],
    "Citrate": [NOT_TESTED, "Positive", "Negative"],
    "Motility": [NOT_TESTED, "Positive", "Negative"],
}

tab_identify, tab_practice = st.tabs(["🔬 Identify", "🎓 Practice Mode"])

# ----------------------------------------------------------------------
# TAB 1 — Identify
# ----------------------------------------------------------------------
with tab_identify:
    st.markdown('<div class="bia-section-label">Step 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="bia-section-title">Basic characteristics</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        gram = st.selectbox("Gram stain", OPTIONS["Gram"])
    with col2:
        shape = st.selectbox("Shape", OPTIONS["Shape"])
    with col3:
        arrangement = st.selectbox("Arrangement", OPTIONS["Arrangement"])

    st.markdown('<div class="bia-section-label">Step 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="bia-section-title">Biochemical tests</div>', unsafe_allow_html=True)
    st.caption("Leave any test as “Not tested” if you haven't run it — it won't count against the score.")

    biochem_cols = st.columns(3)
    biochem_tests = ["Catalase", "Coagulase", "Oxidase", "Indole", "Urease", "Citrate", "Motility"]
    biochem_values = {}
    for i, test in enumerate(biochem_tests):
        with biochem_cols[i % 3]:
            biochem_values[test] = st.selectbox(test, OPTIONS[test], key=f"id_{test}")

    user_input = {"Gram": gram, "Shape": shape, "Arrangement": arrangement, **biochem_values}

    st.markdown('<div class="bia-section-label">Step 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="bia-section-title">Run identification</div>', unsafe_allow_html=True)

    if st.button("🔬 Identify bacterium", type="primary"):
        results = identify(user_input, DB)

        st.markdown('<div class="bia-section-label">Results</div>', unsafe_allow_html=True)

        if not results:
            st.error(
                "**No exact match found.**\n\n"
                "The selected characteristics don't correspond to an organism in the "
                "current educational database. Try reviewing your entries or testing "
                "additional characteristics."
            )
        else:
            top = results[0]
            close_matches = [r for r in results if r["score"] >= 60]
            shown = close_matches if len(close_matches) > 1 else [top]

            if len(close_matches) > 1:
                st.markdown('<div class="bia-section-title">Possible identifications</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="bia-section-title">Likely identification</div>', unsafe_allow_html=True)

            for r in shown:
                organism_gram = DB.loc[DB["Organism"] == r["organism"], "Gram"].iloc[0]
                st.markdown(
                    f"""
                    <div class="bia-result-card">
                        {score_ring_html(r['score'], organism_gram)}
                        <div>
                            <div class="bia-result-name">{r['organism']}</div>
                            {gram_tag_html(organism_gram)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander(f"View matching characteristics — {r['organism']}"):
                    st.markdown(comparison_table_html(r["comparisons"]), unsafe_allow_html=True)
                    if r["notes"]:
                        st.markdown(f'<div class="bia-note">Note: {r["notes"]}</div>', unsafe_allow_html=True)

                    st.write(
                        f"Matched **{r['match_count']} of {r['applicable_count']}** applicable "
                        f"database tests, giving a Database Match Score of **{r['score']}%**. "
                        "This score reflects agreement with the educational database only — "
                        "it is not a validated diagnostic confidence level."
                    )

                    if explain_result is not None:
                        with st.spinner("Generating a plain-language explanation..."):
                            explanation = explain_result(
                                organism=r["organism"],
                                comparisons=r["comparisons"],
                                score=r["score"],
                                notes=r["notes"],
                            )
                        if explanation:
                            st.markdown("**🤖 AI explanation**")
                            st.write(explanation)
                        else:
                            st.caption("AI explanation unavailable right now — the rule-based result above is unaffected.")

            if len(close_matches) > 1:
                st.info(
                    "Multiple organisms remain possible with the tests provided. "
                    "Consider testing additional characteristics (e.g. any of: "
                    + ", ".join(TEST_COLUMNS) + ") to further differentiate them."
                )

# ----------------------------------------------------------------------
# TAB 2 — Practice Mode
# ----------------------------------------------------------------------
with tab_practice:
    st.markdown('<div class="bia-section-label">Self-test</div>', unsafe_allow_html=True)
    st.markdown('<div class="bia-section-title">Unknown organism case</div>', unsafe_allow_html=True)

    if "practice_case" not in st.session_state:
        st.session_state.practice_case = None
        st.session_state.practice_answered = False

    if st.button("🎲 New case"):
        row = DB.sample(1).iloc[0]
        st.session_state.practice_case = row
        st.session_state.practice_answered = False

    case = st.session_state.practice_case
    if case is not None:
        st.markdown("**Given laboratory results:**")
        shown_tests = ["Gram", "Shape", "Arrangement", "Catalase", "Coagulase"]
        for t in shown_tests:
            if case[t] != "NA":
                st.write(f"- **{t}:** {case[t]}")

        options = [case["Organism"]]
        other_organisms = DB[DB["Organism"] != case["Organism"]]["Organism"].tolist()
        options += random.sample(other_organisms, k=min(3, len(other_organisms)))
        random.shuffle(options)

        choice = st.radio("What is the most likely organism?", options, index=None, key=f"choice_{id(case)}")

        if st.button("Submit answer") and choice is not None:
            st.session_state.practice_answered = True
            if choice == case["Organism"]:
                st.success(f"✅ Correct! This is **{case['Organism']}**.")
            else:
                st.error(f"❌ Not quite. The correct answer was **{case['Organism']}**.")
            if case["Notes"] and not pd.isna(case["Notes"]):
                st.caption(f"Note: {case['Notes']}")
    else:
        st.write("Click **New case** to generate an unknown organism to identify.")

# ----------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class="bia-footer">
        Built by <strong>Zeeshan Ali</strong> · BS Medical Laboratory Technology ·
        Riphah International University
    </div>
    """,
    unsafe_allow_html=True,
)
