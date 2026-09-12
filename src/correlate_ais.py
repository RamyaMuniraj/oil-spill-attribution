from pathlib import Path
from math import asin, cos, radians, sin, sqrt

import pandas as pd


# =================================================
# PROJECT PATHS
# =================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

CANDIDATE_PATH = (
    PROJECT_DIR
    / "outputs"
    / "candidate_regions.csv"
)

FILTERED_CANDIDATE_PATH = (
    PROJECT_DIR
    / "outputs"
    / "filtered_candidate_regions.csv"
)

AIS_PATH = (
    PROJECT_DIR
    / "data"
    / "demo"
    / "ais_demo_data.csv"
)

OUTPUT_PATH = (
    PROJECT_DIR
    / "outputs"
    / "vessel_suspect_ranking.csv"
)

REVERSE_DRIFT_PATH = (
    PROJECT_DIR
    / "outputs"
    / "reverse_drift_consistency.csv"
)


# =================================================
# HAVERSINE DISTANCE
# =================================================

def haversine_km(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371.0

    latitude_difference = radians(lat2 - lat1)
    longitude_difference = radians(lon2 - lon1)

    a = (
        sin(latitude_difference / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(longitude_difference / 2) ** 2
    )

    return 2 * earth_radius_km * asin(sqrt(a))


# =================================================
# VESSEL TYPE RELEVANCE SCORE
# =================================================

def vessel_type_score(vessel_type):

    scores = {
        "Tanker": 15,
        "Cargo": 8,
        "Fishing": 2,
    }

    return scores.get(vessel_type, 0)


# =================================================
# MAIN
# =================================================

def main():

    # ------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------

    candidates = pd.read_csv(
        CANDIDATE_PATH
    )

    # Use the false-positive filtered file when
    # available. Fall back to the original candidate
    # file if the filtered file does not exist.

    if FILTERED_CANDIDATE_PATH.exists():

        candidates = pd.read_csv(
            FILTERED_CANDIDATE_PATH
        )

        print(
            "Using geometry-based false-positive "
            "candidate assessment."
        )

    else:

        print(
            "Filtered candidate file not found. "
            "Using original candidate regions."
        )

        candidates = pd.read_csv(
            CANDIDATE_PATH
        )

        # Add default values so the downstream
        # attribution pipeline remains consistent.

        candidates["false_positive_score"] = 0
        candidates["false_positive_risk"] = (
            "NOT_ASSESSED"
        )
        candidates["candidate_status"] = (
            "NOT_ASSESSED"
        )

    ais = pd.read_csv(
        AIS_PATH
    )

    reverse_drift = pd.read_csv(
        REVERSE_DRIFT_PATH
    )

    rankings = []

    # =================================================
    # IDENTIFY TIME COLUMNS
    # =================================================

    candidate_time_col = next(
        (
            col
            for col in [
                "detection_timestamp_utc",
                "timestamp",
                "datetime",
                "date",
                "detection_time",
                "candidate_date",
            ]
            if col in candidates.columns
        ),
        None,
    )

    ais_time_col = next(
        (
            col
            for col in [
                "timestamp_utc",
                "timestamp",
                "datetime",
                "date",
                "time",
            ]
            if col in ais.columns
        ),
        None,
    )

    # =================================================
    # CONVERT TIME COLUMNS
    # =================================================

    if candidate_time_col:

        candidates[candidate_time_col] = pd.to_datetime(
            candidates[candidate_time_col],
            errors="coerce",
        )

    if ais_time_col:

        ais[ais_time_col] = pd.to_datetime(
            ais[ais_time_col],
            errors="coerce",
        )

    # =================================================
    # CANDIDATE LOOP
    # =================================================

    for candidate in candidates.itertuples(index=False):

        candidate_dict = candidate._asdict()

        # ------------------------------------------------
        # SAR FALSE-POSITIVE INFORMATION
        # ------------------------------------------------

        false_positive_score = float(
            candidate_dict.get(
                "false_positive_score",
                0
            )
        )

        false_positive_risk = candidate_dict.get(
            "false_positive_risk",
            "NOT_ASSESSED"
        )

        candidate_status = candidate_dict.get(
            "candidate_status",
            "NOT_ASSESSED"
        )

        # =================================================
        # VESSEL LOOP
        # =================================================

        for vessel_id, track in ais.groupby("vessel_id"):

            # =================================================
            # CALCULATE DISTANCE FROM EVERY AIS POINT
            # =================================================

            distances = track.apply(
                lambda record: haversine_km(
                    candidate.latitude,
                    candidate.longitude,
                    record.latitude,
                    record.longitude,
                ),
                axis=1,
            )

            closest_index = distances.idxmin()

            closest_record = track.loc[
                closest_index
            ]

            closest_distance = float(
                distances.loc[closest_index]
            )

            # =================================================
            # 1. SPATIAL PROXIMITY SCORE — 35 POINTS
            # =================================================

            proximity_score = max(
                0,
                35 * (
                    1 - closest_distance / 30
                ),
            )

            proximity_score = round(
                proximity_score,
                1,
            )

            # =================================================
            # 2. TEMPORAL CORRELATION SCORE — 25 POINTS
            # =================================================

            temporal_score = 12.5

            temporal_reason = (
                "temporal correlation unavailable"
            )

            if (
                candidate_time_col
                and ais_time_col
            ):

                candidate_time = candidate_dict.get(
                    candidate_time_col
                )

                vessel_time = closest_record.get(
                    ais_time_col
                )

                if (
                    pd.notna(candidate_time)
                    and pd.notna(vessel_time)
                ):

                    time_difference_hours = abs(
                        (
                            candidate_time
                            - vessel_time
                        ).total_seconds()
                    ) / 3600

                    if time_difference_hours <= 1:

                        temporal_score = 25

                    elif time_difference_hours <= 3:

                        temporal_score = 20

                    elif time_difference_hours <= 6:

                        temporal_score = 15

                    elif time_difference_hours <= 12:

                        temporal_score = 8

                    else:

                        temporal_score = 0

                    temporal_reason = (
                        f"temporal difference "
                        f"{time_difference_hours:.1f} hours"
                    )

            # =================================================
            # 3. AIS ANOMALY SCORE — 15 POINTS
            # =================================================

            anomaly_score = 0

            anomaly_reason = (
                "no relevant AIS anomaly"
            )

            if (
                "ais_gap_flag" in track.columns
                and ais_time_col
                and candidate_time_col
            ):

                candidate_time = candidate_dict.get(
                    candidate_time_col
                )

                if pd.notna(candidate_time):

                    track_time_difference = (
                        track[ais_time_col]
                        - candidate_time
                    ).abs()

                    # AIS observations within ±3 hours

                    relevant_window = track[
                        track_time_difference
                        <= pd.Timedelta(hours=3)
                    ]

                    if (
                        not relevant_window.empty
                        and relevant_window[
                            "ais_gap_flag"
                        ]
                        .fillna(False)
                        .astype(bool)
                        .any()
                    ):

                        anomaly_score = 15

                        anomaly_reason = (
                            "AIS gap detected near "
                            "candidate detection time"
                        )

                    else:

                        anomaly_score = 0

                        anomaly_reason = (
                            "no AIS gap near candidate "
                            "detection time"
                        )

            # =================================================
            # 4. VESSEL RELEVANCE SCORE — 15 POINTS
            # =================================================

            type_score = vessel_type_score(
                closest_record["vessel_type"]
            )

            type_score = round(
                type_score,
                1,
            )

            # =================================================
            # 5. TRACK CONSISTENCY SCORE — 10 POINTS
            # =================================================

            nearby_distances = distances[
                distances <= 30
            ]

            if len(nearby_distances) >= 3:

                mean_distance = (
                    nearby_distances.mean()
                )

                track_consistency_score = max(
                    0,
                    10 * (
                        1 - mean_distance / 30
                    ),
                )

            elif len(nearby_distances) == 2:

                mean_distance = (
                    nearby_distances.mean()
                )

                track_consistency_score = max(
                    0,
                    8 * (
                        1 - mean_distance / 30
                    ),
                )

            else:

                track_consistency_score = 0

            track_consistency_score = round(
                track_consistency_score,
                1,
            )

            # =================================================
            # 6. TRAJECTORY CONSISTENCY SCORE — 10 POINTS
            # =================================================

            trajectory_consistency_score = 0

            trajectory_reason = (
                "insufficient trajectory data"
            )

            if (
                len(track) >= 3
                and ais_time_col
            ):

                track_sorted = (
                    track
                    .sort_values(
                        ais_time_col
                    )
                    .reset_index(drop=True)
                )

                track_distances = (
                    track_sorted.apply(
                        lambda record: haversine_km(
                            candidate.latitude,
                            candidate.longitude,
                            record.latitude,
                            record.longitude,
                        ),
                        axis=1,
                    )
                    .reset_index(drop=True)
                )

                closest_position = int(
                    track_distances.idxmin()
                )

                # Need a point before AND after
                # the closest point.

                if (
                    closest_position > 0
                    and closest_position
                    < len(track_sorted) - 1
                ):

                    previous_distance = float(
                        track_distances.iloc[
                            closest_position - 1
                        ]
                    )

                    closest_track_distance = float(
                        track_distances.iloc[
                            closest_position
                        ]
                    )

                    next_distance = float(
                        track_distances.iloc[
                            closest_position + 1
                        ]
                    )

                    approaching = (
                        previous_distance
                        > closest_track_distance
                    )

                    departing = (
                        next_distance
                        > closest_track_distance
                    )

                    if (
                        approaching
                        and departing
                    ):

                        trajectory_consistency_score = 10

                        trajectory_reason = (
                            "vessel approaches and departs "
                            "candidate region"
                        )

                    elif (
                        approaching
                        or departing
                    ):

                        trajectory_consistency_score = 5

                        trajectory_reason = (
                            "partial trajectory consistency"
                        )

                    else:

                        trajectory_consistency_score = 0

                        trajectory_reason = (
                            "no clear approach/departure "
                            "pattern"
                        )

            # =================================================
            # 7. REVERSE-DRIFT CONSISTENCY — 10 POINTS
            # =================================================

            reverse_drift_match = reverse_drift[
                (
                    reverse_drift["candidate_id"]
                    == candidate.candidate_id
                )
                &
                (
                    reverse_drift["vessel_id"]
                    == vessel_id
                )
            ]

            if not reverse_drift_match.empty:

                reverse_drift_score = float(
                    reverse_drift_match.iloc[0][
                        "reverse_drift_score"
                    ]
                )

            else:

                reverse_drift_score = 0.0

            # =================================================
            # FINAL EXPLAINABLE SCORE — 120 POINTS
            # =================================================

            raw_score = (
                proximity_score
                + temporal_score
                + anomaly_score
                + type_score
                + track_consistency_score
                + trajectory_consistency_score
                + (
                    reverse_drift_score
                    * 0.10
                )
            )

            # Normalize 120 → 100

            total_score = round(
                (
                    raw_score
                    / 120
                ) * 100
            )

            # =================================================
            # EXPLAINABLE EVIDENCE
            # =================================================

            reasons = [

                (
                    f"closest AIS point is "
                    f"{closest_distance:.2f} km away"
                ),

                temporal_reason,

                (
                    f"vessel type: "
                    f"{closest_record['vessel_type']}"
                ),

                (
                    f"track consistency score "
                    f"{track_consistency_score:.1f}/10"
                ),

                (
                    f"trajectory: "
                    f"{trajectory_reason}"
                ),

                (
                    f"reverse-drift consistency score "
                    f"{reverse_drift_score:.0f}/100"
                ),

                anomaly_reason,

                (
                    f"SAR candidate false-positive risk: "
                    f"{false_positive_risk}"
                ),
            ]

            # =================================================
            # SAVE THIS VESSEL-CANDIDATE RESULT
            # =================================================

            rankings.append(
                {
                    "candidate_id":
                        candidate.candidate_id,

                    "vessel_id":
                        vessel_id,

                    "vessel_name":
                        closest_record[
                            "vessel_name"
                        ],

                    "vessel_type":
                        closest_record[
                            "vessel_type"
                        ],

                    "closest_distance_km":
                        round(
                            closest_distance,
                            2,
                        ),

                    "spatial_score":
                        proximity_score,

                    "temporal_score":
                        round(
                            temporal_score,
                            1,
                        ),

                    "anomaly_score":
                        anomaly_score,

                    "vessel_relevance_score":
                        type_score,

                    "track_consistency_score":
                        track_consistency_score,

                    "trajectory_consistency_score":
                        trajectory_consistency_score,

                    "reverse_drift_score":
                        round(
                            reverse_drift_score,
                            1,
                        ),

                    "false_positive_score":
                        false_positive_score,

                    "false_positive_risk":
                        false_positive_risk,

                    "candidate_status":
                        candidate_status,

                    "suspicion_score":
                        total_score,

                    "evidence":
                        "; ".join(
                            reasons
                        ),
                }
            )

    # =================================================
    # SAVE FINAL RANKING
    # =================================================

    result = pd.DataFrame(
        rankings
    )

    result = result.sort_values(
        [
            "candidate_id",
            "suspicion_score",
        ],
        ascending=[
            True,
            False,
        ],
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # =================================================
    # PRINT TOP SUSPECT FOR EACH CANDIDATE
    # =================================================

    print(
        "\nTop-ranked vessel for each candidate:\n"
    )

    top_suspects = (
        result
        .groupby(
            "candidate_id"
        )
        .head(1)
    )

    print(
        top_suspects[
            [
                "candidate_id",
                "vessel_id",
                "vessel_name",
                "false_positive_risk",
                "suspicion_score",
            ]
        ].to_string(
            index=False
        )
    )

    print(
        f"\nSaved ranking: {OUTPUT_PATH}"
    )


# =================================================
# RUN PROGRAM
# =================================================

if __name__ == "__main__":
    main()