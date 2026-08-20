"""
identification.py
------------------
The "brain" of the Bacterial Identification Assistant.

This module contains plain, testable Python functions that:
1. Load the bacterial knowledge base (data/bacteria.csv)
2. Compare a user's entered lab characteristics against every organism
3. Calculate a transparent "Database Match Score" for each organism
4. Return ranked results with an explanation of what matched

No Streamlit code lives here on purpose — this logic can be tested
and reused independently of the web interface.
"""

import pandas as pd

# The characteristic columns we compare on.
# ("Organism" and "Notes" are metadata, not test results.)
TEST_COLUMNS = [
    "Gram",
    "Shape",
    "Arrangement",
    "Catalase",
    "Coagulase",
    "Oxidase",
    "Indole",
    "Urease",
    "Citrate",
    "Motility",
]

# What we accept as "the user didn't provide/test this characteristic".
NOT_TESTED = "Not tested"


def load_database(csv_path="data/bacteria.csv"):
    """Load the bacterial knowledge base from CSV into a DataFrame."""
    return pd.read_csv(csv_path)


def score_organism(user_input: dict, organism_row: pd.Series):
    """
    Compare one organism's known profile against the user's input.

    Returns a dict with:
        - matches: list of (test, user_value, db_value, status) for tests
          that were actually compared
        - applicable_count: how many tests counted toward the score
        - match_count: how many of those the organism matched on
        - score: percentage match (0-100), or None if nothing was
          applicable/comparable (e.g. user tested nothing relevant)

    Scoring rules (deliberately simple and explainable):
      - If the user marked a test "Not tested", we skip it entirely —
        it doesn't help or hurt any organism's score.
      - If the organism's database value for that test is "NA"
        (not applicable to that organism, e.g. Coagulase for a
        Gram-negative rod), we also skip it — a "NA" is not a
        disagreement, so it must never be scored as a mismatch.
      - If the database value is "Variable", we count it as a match
        but flag it, since some strains legitimately go either way.
      - Otherwise, it's a straightforward match or mismatch.
    """
    comparisons = []
    applicable = 0
    matched = 0

    for test in TEST_COLUMNS:
        user_value = user_input.get(test, NOT_TESTED)
        db_value = organism_row[test]

        if user_value == NOT_TESTED:
            continue  # user didn't test this — never penalize or reward
        if db_value == "NA":
            continue  # not applicable to this organism — never a mismatch

        applicable += 1

        if db_value == "Variable":
            matched += 1
            comparisons.append((test, user_value, db_value, "possible (variable)"))
        elif user_value == db_value:
            matched += 1
            comparisons.append((test, user_value, db_value, "match"))
        else:
            comparisons.append((test, user_value, db_value, "mismatch"))

    score = round((matched / applicable) * 100) if applicable > 0 else None

    return {
        "organism": organism_row["Organism"],
        "notes": organism_row.get("Notes", ""),
        "comparisons": comparisons,
        "applicable_count": applicable,
        "match_count": matched,
        "score": score,
    }


def identify(user_input: dict, df: pd.DataFrame):
    """
    Run the user's input against every organism in the database.

    Returns a list of result dicts (see score_organism), sorted by
    score descending. Organisms with score None (nothing applicable
    was compared) or 0 mismatched-everything are still included so
    the caller can decide how to present "no match" — filtering is
    a UI decision, not something this function should hide.
    """
    results = [score_organism(user_input, row) for _, row in df.iterrows()]
    results = [r for r in results if r["score"] is not None]
    results.sort(key=lambda r: r["score"], reverse=True)
    return results
