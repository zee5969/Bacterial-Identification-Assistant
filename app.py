"""
app.py
------
Streamlit front end for the Bacterial Identification Assistant.

This file only handles UI: drawing inputs, calling into
utils/identification.py, and displaying results. All identification
logic lives in that module on purpose.
"""

import random
import pandas as pd
import streamlit as st

from utils.identification import load_database, identify, TEST_COLUMNS, NOT_TESTED

st.set_page_config(page_title="Bacterial Identification Assistant", page_icon="🧫", layout="centered")

DB = load_database()

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

st.title("🧫 Bacterial Identification Assistant")
st.caption("An educational decision-support tool for learning bacterial identification.")
st.warning(
    "**Educational use only.** This tool is not intended to replace laboratory "
    "procedures, validated identification systems, antimicrobial susceptibility "
    "testing, professional interpretation, or clinical diagnosis."
)

tab_identify, tab_practice = st.tabs(["🔬 Identify", "🎓 Practice Mode"])

# ----------------------------------------------------------------------
# TAB 1 — Identify
# ----------------------------------------------------------------------
with tab_identify:
    st.subheader("Section 1 — Basic Characteristics")
    col1, col2, col3 = st.columns(3)
    with col1:
        gram = st.selectbox("Gram stain", OPTIONS["Gram"])
    with col2:
        shape = st.selectbox("Shape", OPTIONS["Shape"])
    with col3:
        arrangement = st.selectbox("Arrangement", OPTIONS["Arrangement"])

    st.subheader("Section 2 — Biochemical Tests")
    biochem_cols = st.columns(3)
    biochem_tests = ["Catalase", "Coagulase", "Oxidase", "Indole", "Urease", "Citrate", "Motility"]
    biochem_values = {}
    for i, test in enumerate(biochem_tests):
        with biochem_cols[i % 3]:
            biochem_values[test] = st.selectbox(test, OPTIONS[test], key=f"id_{test}")

    user_input = {"Gram": gram, "Shape": shape, "Arrangement": arrangement, **biochem_values}

    st.subheader("Section 3 — Identify")
    if st.button("🔬 Identify Bacterium", type="primary"):
        results = identify(user_input, DB)

        st.subheader("Section 4 — Results")
        if not results:
            st.error(
                "**No exact match found.**\n\n"
                "The selected characteristics do not correspond to an organism in the "
                "current educational database. Please review the laboratory results or "
                "try additional tests."
            )
        else:
            top = results[0]
            close_matches = [r for r in results if r["score"] >= 60]

            if len(close_matches) > 1:
                st.subheader("Possible identifications")
                for r in close_matches:
                    st.markdown(f"**{r['organism']}** — Database Match Score: **{r['score']}%**")
            else:
                st.markdown(f"### Likely identification: **{top['organism']}**")
                st.metric("Database Match Score", f"{top['score']}%")

            st.markdown("#### Matching characteristics")
            for r in ([top] if len(close_matches) <= 1 else close_matches):
                st.markdown(f"**{r['organism']}**")
                table_rows = [
                    {"Test": t, "User Result": u, "Database Profile": d, "Status": s}
                    for (t, u, d, s) in r["comparisons"]
                ]
                st.table(pd.DataFrame(table_rows))
                if r["notes"]:
                    st.caption(f"Note: {r['notes']}")

            if len(close_matches) > 1:
                st.info(
                    "Multiple organisms remain possible with the tests provided. "
                    "Consider testing additional characteristics (e.g. any of: "
                    + ", ".join(TEST_COLUMNS) + ") to further differentiate them."
                )

            st.markdown("#### Why?")
            st.write(
                f"The entered characteristics matched {top['match_count']} of "
                f"{top['applicable_count']} applicable database tests for "
                f"**{top['organism']}**, giving a Database Match Score of "
                f"{top['score']}%. This score reflects agreement with the "
                "educational database only — it is not a validated diagnostic "
                "confidence level."
            )

# ----------------------------------------------------------------------
# TAB 2 — Practice Mode
# ----------------------------------------------------------------------
with tab_practice:
    st.subheader("Unknown Organism Case")

    if "practice_case" not in st.session_state:
        st.session_state.practice_case = None
        st.session_state.practice_answered = False

    if st.button("🎲 New Case"):
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

        if st.button("Submit Answer") and choice is not None:
            st.session_state.practice_answered = True
            if choice == case["Organism"]:
                st.success(f"✅ Correct! This is **{case['Organism']}**.")
            else:
                st.error(f"❌ Not quite. The correct answer was **{case['Organism']}**.")
            if case["Notes"] and not pd.isna(case["Notes"]):
                st.caption(f"Note: {case['Notes']}")
    else:
        st.write("Click **New Case** to generate an unknown organism to identify.")
