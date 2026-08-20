"""
ai_explain.py
-------------
Optional AI explanation layer for the Bacterial Identification Assistant,
using the Groq API (free tier).

IMPORTANT: This module never identifies bacteria. It only takes a result
that utils/identification.py has already computed (deterministically) and
asks an LLM to explain it in plainer, more student-friendly language.

If the API call fails for any reason (no key, network issue, rate limit),
this fails gracefully — the app should keep working with the rule-based
result alone.
"""

import streamlit as st
from groq import Groq


def get_client():
    """Create a Groq client using the key from Streamlit secrets."""
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def explain_result(organism: str, comparisons: list, score: int, notes: str = ""):
    """
    Ask the AI to explain an already-computed identification result in
    simple language for an MLT student. Returns a string, or None if the
    explanation couldn't be generated (caller should handle this gracefully).
    """
    client = get_client()
    if client is None:
        return None

    comparison_lines = "\n".join(
        f"- {test}: student result = {user_val}, database profile = {db_val} ({status})"
        for test, user_val, db_val, status in comparisons
    )

    prompt = f"""You are helping a BS Medical Laboratory Technology (MLT) student
understand a bacterial identification result from an educational tool.

The result was already determined by a rule-based matching engine — do NOT
change the identification, do NOT introduce any characteristics that are
not listed below, and do NOT state anything as clinical or diagnostic fact.
Your only job is to explain, in simple student-friendly language, why these
characteristics point to this organism.

Identified organism: {organism}
Database Match Score: {score}%
Additional notes: {notes or "none"}

Characteristics compared:
{comparison_lines}

Write a short (3-5 sentence) explanation suitable for a student studying
for a Clinical Bacteriology exam. Keep it educational, not clinical."""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception:
        return None
