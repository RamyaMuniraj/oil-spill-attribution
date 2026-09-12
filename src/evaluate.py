import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "outputs"

CANDIDATE_FILE = OUTPUT_DIR / "candidate_regions.csv"
FILTERED_FILE = OUTPUT_DIR / "filtered_candidate_regions.csv"
RANKING_FILE = OUTPUT_DIR / "vessel_suspect_ranking.csv"
CONFIDENCE_FILE = OUTPUT_DIR / "attribution_confidence.csv"
REVERSE_DRIFT_FILE = OUTPUT_DIR / "reverse_drift_consistency.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    candidates = pd.read_csv(CANDIDATE_FILE)

    filtered = pd.read_csv(FILTERED_FILE)

    ranking = pd.read_csv(RANKING_FILE)

    confidence = pd.read_csv(CONFIDENCE_FILE)

    reverse_drift = pd.read_csv(REVERSE_DRIFT_FILE)

    return (
        candidates,
        filtered,
        ranking,
        confidence,
        reverse_drift,
    )


# ============================================================
# EVALUATE SAR CANDIDATE DETECTION
# ============================================================

def evaluate_candidates(candidates):

    total_candidates = len(candidates)

    if "area_pixels" in candidates.columns:
        average_area = candidates["area_pixels"].mean()
    else:
        average_area = 0

    return {
        "sar_candidates_detected": total_candidates,
        "average_candidate_area_pixels": round(
            average_area,
            2
        ),
    }


# ============================================================
# EVALUATE FALSE-POSITIVE FILTERING
# ============================================================

def evaluate_false_positive_filter(filtered):

    total = len(filtered)

    retained = 0
    review_required = 0

    if "candidate_status" in filtered.columns:

        status = (
            filtered["candidate_status"]
            .astype(str)
            .str.upper()
        )

        retained = status.eq("RETAINED").sum()

        review_required = status.eq(
            "REVIEW_REQUIRED"
        ).sum()

    retention_rate = (
        retained / total * 100
        if total > 0
        else 0
    )

    return {
        "candidates_after_filtering": total,
        "candidates_retained": int(retained),
        "candidates_review_required": int(
            review_required
        ),
        "retention_rate_percent": round(
            retention_rate,
            2
        ),
    }


# ============================================================
# EVALUATE AIS ATTRIBUTION
# ============================================================

def evaluate_attribution(ranking):

    top_ranked = (
        ranking
        .sort_values(
            ["candidate_id", "suspicion_score"],
            ascending=[True, False]
        )
        .groupby("candidate_id")
        .first()
        .reset_index()
    )

    average_score = top_ranked[
        "suspicion_score"
    ].mean()

    highest_score = top_ranked[
        "suspicion_score"
    ].max()

    return {
        "candidates_with_vessel_ranking": len(
            top_ranked
        ),
        "average_top_vessel_score": round(
            average_score,
            2
        ),
        "highest_vessel_score": round(
            highest_score,
            2
        ),
    }, top_ranked


# ============================================================
# EVALUATE CONFIDENCE
# ============================================================

def evaluate_confidence(confidence, ranking):

    # Select the highest-ranked vessel for
    # each SAR candidate.
    top_ranked = (
        ranking
        .sort_values(
            ["candidate_id", "suspicion_score"],
            ascending=[True, False]
        )
        .groupby("candidate_id")
        .first()
        .reset_index()
    )

    # Match the confidence record belonging
    # to each top-ranked vessel.
    top_confidence = confidence.merge(
        top_ranked[
            [
                "candidate_id",
                "vessel_id",
            ]
        ],
        on=[
            "candidate_id",
            "vessel_id",
        ],
        how="inner",
    )

    confidence_level = (
        top_confidence["confidence_level"]
        .astype(str)
        .str.upper()
    )

    high = confidence_level.eq(
        "HIGH"
    ).sum()

    medium = confidence_level.eq(
        "MEDIUM"
    ).sum()

    low = confidence_level.eq(
        "LOW"
    ).sum()

    insufficient = confidence_level.eq(
        "INSUFFICIENT"
    ).sum()

    return {
        "high_confidence_cases": int(high),
        "medium_confidence_cases": int(
            medium
        ),
        "low_confidence_cases": int(low),
        "insufficient_evidence_cases": int(
            insufficient
        ),
    }


# ============================================================
# EVALUATE REVERSE-DRIFT CONSISTENCY
# ============================================================

def evaluate_reverse_drift(reverse_drift):

    average_score = reverse_drift[
        "reverse_drift_score"
    ].mean()

    interpretation = (
        reverse_drift["interpretation"]
        .astype(str)
        .str.lower()
    )

    strong = interpretation.str.contains(
        "strong",
        na=False
    ).sum()

    good = interpretation.str.contains(
        "good",
        na=False
    ).sum()

    moderate = interpretation.str.contains(
        "moderate",
        na=False
    ).sum()

    weak = interpretation.str.contains(
        "weak|low",
        na=False,
        regex=True
    ).sum()

    return {
        "reverse_drift_cases": len(
            reverse_drift
        ),

        "average_reverse_drift_score": round(
            average_score,
            2
        ),

        "strong_trajectory_cases": int(
            strong
        ),

        "good_trajectory_cases": int(
            good
        ),

        "moderate_trajectory_cases": int(
            moderate
        ),

        "weak_or_low_trajectory_cases": int(
            weak
        ),
    }


# ============================================================
# CREATE EVALUATION SUMMARY
# ============================================================

def create_evaluation_summary():

    print("\nLoading project outputs...")

    (
        candidates,
        filtered,
        ranking,
        confidence,
        reverse_drift,
    ) = load_data()

    print(
        "All required output files loaded successfully."
    )

    # --------------------------------------------------------
    # SAR CANDIDATE EVALUATION
    # --------------------------------------------------------

    candidate_results = evaluate_candidates(
        candidates
    )

    # --------------------------------------------------------
    # FALSE-POSITIVE EVALUATION
    # --------------------------------------------------------

    filter_results = (
        evaluate_false_positive_filter(
            filtered
        )
    )

    # --------------------------------------------------------
    # AIS ATTRIBUTION EVALUATION
    # --------------------------------------------------------

    attribution_results, top_ranked = (
        evaluate_attribution(
            ranking
        )
    )

    # --------------------------------------------------------
    # CONFIDENCE EVALUATION
    # --------------------------------------------------------

    confidence_results = evaluate_confidence(
        confidence,
        ranking
    )

    # --------------------------------------------------------
    # REVERSE-DRIFT EVALUATION
    # --------------------------------------------------------

    reverse_results = evaluate_reverse_drift(
        reverse_drift
    )

    # --------------------------------------------------------
    # COMBINE RESULTS
    # --------------------------------------------------------

    summary = {

        # SAR
        "sar_candidates_detected":
            candidate_results[
                "sar_candidates_detected"
            ],

        "average_candidate_area_pixels":
            candidate_results[
                "average_candidate_area_pixels"
            ],

        # False-positive filtering
        "candidates_after_filtering":
            filter_results[
                "candidates_after_filtering"
            ],

        "candidates_retained":
            filter_results[
                "candidates_retained"
            ],

        "candidates_review_required":
            filter_results[
                "candidates_review_required"
            ],

        "retention_rate_percent":
            filter_results[
                "retention_rate_percent"
            ],

        # AIS attribution
        "candidates_with_vessel_ranking":
            attribution_results[
                "candidates_with_vessel_ranking"
            ],

        "average_top_vessel_score":
            attribution_results[
                "average_top_vessel_score"
            ],

        "highest_vessel_score":
            attribution_results[
                "highest_vessel_score"
            ],

        # Confidence
        "high_confidence_cases":
            confidence_results[
                "high_confidence_cases"
            ],

        "medium_confidence_cases":
            confidence_results[
                "medium_confidence_cases"
            ],

        "low_confidence_cases":
            confidence_results[
                "low_confidence_cases"
            ],

        "insufficient_evidence_cases":
            confidence_results[
                "insufficient_evidence_cases"
            ],

        # Reverse drift
        "reverse_drift_cases":
            reverse_results[
                "reverse_drift_cases"
            ],

        "average_reverse_drift_score":
            reverse_results[
                "average_reverse_drift_score"
            ],

        "strong_trajectory_cases":
            reverse_results[
                "strong_trajectory_cases"
            ],

        "good_trajectory_cases":
            reverse_results[
                "good_trajectory_cases"
            ],

        "moderate_trajectory_cases":
            reverse_results[
                "moderate_trajectory_cases"
            ],

        "weak_or_low_trajectory_cases":
            reverse_results[
                "weak_or_low_trajectory_cases"
            ],
    }

    summary_df = pd.DataFrame(
        [summary]
    )

    # ========================================================
    # SAVE EVALUATION SUMMARY
    # ========================================================

    output_file = (
        OUTPUT_DIR /
        "evaluation_summary.csv"
    )

    summary_df.to_csv(
        output_file,
        index=False
    )

    # ========================================================
    # SAVE TOP-RANKED VESSELS
    # ========================================================

    top_vessel_file = (
        OUTPUT_DIR /
        "evaluation_top_ranked_vessels.csv"
    )

    top_ranked[
        [
            "candidate_id",
            "vessel_id",
            "vessel_name",
            "suspicion_score",
        ]
    ].to_csv(
        top_vessel_file,
        index=False
    )

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print("\n" + "=" * 65)
    print("RESEARCH PROTOTYPE EVALUATION")
    print("=" * 65)

    # SAR
    print(
        f"\nSAR candidates detected: "
        f"{summary['sar_candidates_detected']}"
    )

    print(
        f"Average candidate area: "
        f"{summary['average_candidate_area_pixels']:.2f} pixels"
    )

    # Filtering
    print(
        f"\nCandidates after filtering: "
        f"{summary['candidates_after_filtering']}"
    )

    print(
        f"Candidates retained: "
        f"{summary['candidates_retained']}"
    )

    print(
        f"Candidates requiring review: "
        f"{summary['candidates_review_required']}"
    )

    print(
        f"Retention rate: "
        f"{summary['retention_rate_percent']:.2f}%"
    )

    # Attribution
    print(
        f"\nCandidates with vessel ranking: "
        f"{summary['candidates_with_vessel_ranking']}"
    )

    print(
        f"Average top-vessel score: "
        f"{summary['average_top_vessel_score']:.2f}"
    )

    print(
        f"Highest vessel score: "
        f"{summary['highest_vessel_score']:.2f}"
    )

    # Confidence
    print(
        f"\nHigh-confidence cases: "
        f"{summary['high_confidence_cases']}"
    )

    print(
        f"Medium-confidence cases: "
        f"{summary['medium_confidence_cases']}"
    )

    print(
        f"Low-confidence cases: "
        f"{summary['low_confidence_cases']}"
    )

    print(
        f"Insufficient-evidence cases: "
        f"{summary['insufficient_evidence_cases']}"
    )

    # Reverse drift
    print(
        f"\nReverse-drift cases: "
        f"{summary['reverse_drift_cases']}"
    )

    print(
        f"Average reverse-drift score: "
        f"{summary['average_reverse_drift_score']:.2f}"
    )

    print(
        f"Strong trajectory cases: "
        f"{summary['strong_trajectory_cases']}"
    )

    print(
        f"Good trajectory cases: "
        f"{summary['good_trajectory_cases']}"
    )

    print(
        f"Moderate trajectory cases: "
        f"{summary['moderate_trajectory_cases']}"
    )

    print(
        f"Weak/low trajectory cases: "
        f"{summary['weak_or_low_trajectory_cases']}"
    )

    # ========================================================
    # CONSISTENCY CHECK
    # ========================================================

    trajectory_total = (
        summary["strong_trajectory_cases"]
        + summary["good_trajectory_cases"]
        + summary["moderate_trajectory_cases"]
        + summary["weak_or_low_trajectory_cases"]
    )

    print(
        f"\nTrajectory classification total: "
        f"{trajectory_total}"
    )

    if trajectory_total == summary[
        "reverse_drift_cases"
    ]:
        print(
            "Trajectory classification check: PASSED"
        )
    else:
        print(
            "Trajectory classification check: "
            "WARNING - counts do not match"
        )

    print("\n" + "=" * 65)

    # ========================================================
    # OUTPUT FILES
    # ========================================================

    print(
        f"\nEvaluation summary saved to:\n"
        f"{output_file}"
    )

    print(
        f"\nTop-ranked vessel summary saved to:\n"
        f"{top_vessel_file}"
    )

    # ========================================================
    # SCIENTIFIC DISCLAIMER
    # ========================================================

    print(
        "\nNote: These are prototype/system evaluation "
        "statistics. They are not accuracy, precision, "
        "recall, or probability-of-responsibility metrics "
        "because independently labeled ground-truth data "
        "are not available."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_evaluation_summary()