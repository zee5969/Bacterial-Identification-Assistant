"""
identification.py
------------------
Core matching/scoring engine for the Bacterial Identification Assistant.

This module contains NO Streamlit code and NO AI calls. It is plain,
testable Python: load a CSV of known organism profiles, compare a
user's entered characteristics against every organism, and return a
ranked list of matches with a transparent score.

app.py imports four things from this file:
    - load_database()
    - identify(user_input, db)
    - TEST_COLUMNS
    - NOT_TESTED
"""

import pandas as pd

# Value shown in dropdowns meaning "the student did not enter this test."
# Rows with this value are simply skipped during comparison (not counted
# as a mismatch), so a partially-filled-in form still produces useful
# partial matches instead of failing outright.
NOT_TESTED = "Not tested"

# The full list of biochemical/morphological test columns used for
# scoring. Kept in one place so app.py can reference it too (e.g. when
# suggesting which additional tests would help differentiate organisms).
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

DATABASE_PATH = "data/bacteria.csv"


def load_database(path: str = DATABASE_PATH) -> pd.DataFrame:
    """Load the organism reference table from CSV."""
    df = pd.read_csv(path)
    return df


def identify(user_input: dict, db: pd.DataFrame) -> list:
    """
    Compare the student's entered characteristics against every organism
    in the database and return a ranked list of match results.
    """
    results = []

    for _, row in db.iterrows():
        comparisons = []
        match_count = 0
        applicable_count = 0

        for test in TEST_COLUMNS:
            user_val = user_input.get(test, NOT_TESTED)
            db_val = row[test]

            if user_val == NOT_TESTED:
                continue

            if pd.isna(db_val) or db_val == "NA":
                continue

            applicable_count += 1

            if db_val == "Variable":
                match_count += 1
                comparisons.append((test, user_val, db_val, "Consistent (variable)"))
            elif user_val == db_val:
                match_count += 1
                comparisons.append((test, user_val, db_val, "Match"))
            else:
                comparisons.append((test, user_val, db_val, "Mismatch"))

        if applicable_count == 0:
            continue

        score = round((match_count / applicable_count) * 100)

        results.append({
            "organism": row["Organism"],
            "score": score,
            "match_count": match_count,
            "applicable_count": applicable_count,
            "comparisons": comparisons,
            "notes": row.get("Notes", ""),
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results
