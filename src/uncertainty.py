import pandas as pd


def calculate_confidence(row):
    """
    Estimate evidence confidence from multiple independent
    attribution factors.

    This is NOT a probability of responsibility.

    SAR false-positive risk is treated separately from
    vessel-attribution evidence.
    """

    score = float(row["suspicion_score"])

    evidence_count = 0

    # -----------------------------
    # Vessel attribution evidence
    # -----------------------------

    # Spatial evidence
    if row["closest_distance_km"] <= 2:
        evidence_count += 1

    # Temporal evidence
    if row["temporal_score"] >= 20:
        evidence_count += 1

    # AIS anomaly evidence
    if row["anomaly_score"] > 0:
        evidence_count += 1

    # Vessel relevance
    if row["vessel_relevance_score"] >= 10:
        evidence_count += 1

    # Track consistency
    if row["track_consistency_score"] >= 7:
        evidence_count += 1

    # Trajectory consistency
    if row["trajectory_consistency_score"] >= 7:
        evidence_count += 1

    # Reverse drift consistency
    if row["reverse_drift_score"] >= 80:
        evidence_count += 1

    # -----------------------------
    # SAR candidate reliability
    # -----------------------------

    false_positive_score = float(
        row.get("false_positive_score", 0)
    )

    false_positive_risk = str(
        row.get(
            "false_positive_risk",
            "UNKNOWN"
        )
    )

    candidate_status = str(
        row.get(
            "candidate_status",
            "UNKNOWN"
        )
    )

    # -----------------------------
    # Confidence classification
    # -----------------------------

    if score >= 80 and evidence_count >= 5:
        confidence = "HIGH"

    elif score >= 60 and evidence_count >= 3:
        confidence = "MEDIUM"

    elif score >= 40:
        confidence = "LOW"

    else:
        confidence = "INSUFFICIENT"

    return pd.Series(
        {
            "evidence_count": evidence_count,
            "confidence_level": confidence,
            "false_positive_score": false_positive_score,
            "false_positive_risk": false_positive_risk,
            "candidate_status": candidate_status,
        }
    )


def add_confidence_analysis(input_file, output_file):

    df = pd.read_csv(input_file)

    confidence_data = df.apply(
        calculate_confidence,
        axis=1
    )

    # Remove existing columns before
    # adding the updated analysis.
    columns_to_replace = [
        "evidence_count",
        "confidence_level",
        "false_positive_score",
        "false_positive_risk",
        "candidate_status",
    ]

    df = df.drop(
        columns=[
            col
            for col in columns_to_replace
            if col in df.columns
        ]
    )

    df = pd.concat(
        [df, confidence_data],
        axis=1
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Confidence analysis saved: {output_file}"
    )

    print("\nConfidence summary:")

    print(
        df[
            [
                "candidate_id",
                "vessel_id",
                "suspicion_score",
                "evidence_count",
                "confidence_level",
                "false_positive_score",
                "false_positive_risk",
                "candidate_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":

    input_file = (
        "outputs/vessel_suspect_ranking.csv"
    )

    output_file = (
        "outputs/attribution_confidence.csv"
    )

    add_confidence_analysis(
        input_file,
        output_file
    )