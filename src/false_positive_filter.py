from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "outputs"

CANDIDATE_FILE = OUTPUT_DIR / "candidate_regions.csv"
GEOMETRY_FILE = OUTPUT_DIR / "candidate_geometry.csv"
OUTPUT_FILE = OUTPUT_DIR / "filtered_candidate_regions.csv"


# ---------------------------------------------------------
# Calculate false-positive risk
# ---------------------------------------------------------

def calculate_false_positive_score(row):
    """
    Estimate SAR false-positive risk using multiple
    candidate-level indicators.

    This is a heuristic research prototype, not a trained
    machine-learning classifier.
    """

    score = 0

    area = row["area_pixels"]
    backscatter = row["low_backscatter_threshold"]
    aspect_ratio = row["aspect_ratio"]
    compactness = row["compactness"]
    solidity = row["solidity"]

    # -----------------------------------------------------
    # 1. Candidate size
    # -----------------------------------------------------

    if area < 30:
        score += 25
    elif area < 50:
        score += 15

    # -----------------------------------------------------
    # 2. Very low backscatter
    # -----------------------------------------------------

    if backscatter < 0.03:
        score += 20
    elif backscatter < 0.05:
        score += 10

    # -----------------------------------------------------
    # 3. Aspect ratio
    #
    # Extremely elongated regions can be associated with
    # non-oil SAR structures such as wakes or linear
    # backscatter patterns.
    # -----------------------------------------------------

    if aspect_ratio > 5:
        score += 20
    elif aspect_ratio > 3:
        score += 10

    # -----------------------------------------------------
    # 4. Compactness
    #
    # Low compactness indicates an irregular/elongated
    # region and increases review priority.
    # -----------------------------------------------------

    if compactness < 0.20:
        score += 15
    elif compactness < 0.35:
        score += 8

    # -----------------------------------------------------
    # 5. Solidity
    #
    # Lower solidity means the region has a more irregular
    # or fragmented shape.
    # -----------------------------------------------------

    if solidity < 0.70:
        score += 15
    elif solidity < 0.85:
        score += 8

    return min(score, 100)


# ---------------------------------------------------------
# Risk classification
# ---------------------------------------------------------

def classify_candidate(score):
    if score >= 60:
        return "HIGH_FALSE_POSITIVE_RISK"

    elif score >= 30:
        return "MEDIUM_FALSE_POSITIVE_RISK"

    else:
        return "LOW_FALSE_POSITIVE_RISK"


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    if not CANDIDATE_FILE.exists():
        print(f"Candidate file not found: {CANDIDATE_FILE}")
        return

    if not GEOMETRY_FILE.exists():
        print(f"Geometry file not found: {GEOMETRY_FILE}")
        return

    # -----------------------------------------------------
    # Load candidate detection data
    # -----------------------------------------------------

    candidates = pd.read_csv(CANDIDATE_FILE)

    # -----------------------------------------------------
    # Load geometry features
    # -----------------------------------------------------

    geometry = pd.read_csv(GEOMETRY_FILE)

    # -----------------------------------------------------
    # Merge candidate and geometry information
    #
    # candidate_regions.csv uses candidate_id.
    # candidate_geometry.csv uses label.
    #
    # Candidate IDs are assigned according to the detected
    # region ordering, so align them using row order.
    # -----------------------------------------------------

    geometry = geometry.copy()

    if len(candidates) != len(geometry):
        print(
            "Warning: Candidate and geometry row counts do not match."
        )
        print(
            f"Candidates: {len(candidates)} | "
            f"Geometry: {len(geometry)}"
        )
        return

    geometry["candidate_id"] = candidates["candidate_id"].values

    df = candidates.merge(
        geometry,
        on="candidate_id",
        how="left",
        suffixes=("", "_geometry")
    )

    # -----------------------------------------------------
    # Calculate false-positive score
    # -----------------------------------------------------

    df["false_positive_score"] = df.apply(
        calculate_false_positive_score,
        axis=1
    )

    # -----------------------------------------------------
    # Classify risk
    # -----------------------------------------------------

    df["false_positive_risk"] = df[
        "false_positive_score"
    ].apply(classify_candidate)

    # -----------------------------------------------------
    # Candidate decision
    # -----------------------------------------------------

    df["candidate_status"] = df[
        "false_positive_risk"
    ].apply(
        lambda x:
        "REVIEW_REQUIRED"
        if x == "HIGH_FALSE_POSITIVE_RISK"
        else "RETAINED"
    )

    # -----------------------------------------------------
    # Save results
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # -----------------------------------------------------
    # Display results
    # -----------------------------------------------------

    print("\nSAR False-Positive Filtering Results:\n")

    print(
        df[
            [
                "candidate_id",
                "area_pixels",
                "aspect_ratio",
                "compactness",
                "solidity",
                "low_backscatter_threshold",
                "false_positive_score",
                "false_positive_risk",
                "candidate_status",
            ]
        ].to_string(index=False)
    )

    print(
        f"\nFiltered candidate data saved to:\n"
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()