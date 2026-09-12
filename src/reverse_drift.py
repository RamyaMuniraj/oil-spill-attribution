from pathlib import Path
import math
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

CANDIDATE_FILE = PROJECT_DIR / "outputs" / "candidate_regions.csv"

AIS_FILE = (
    PROJECT_DIR
    / "data"
    / "demo"
    / "ais_demo_data.csv"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "outputs"
    / "reverse_drift_consistency.csv"
)


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_km(lat1, lon1, lat2, lon2):

    earth_radius_km = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


# ============================================================
# BEARING
# ============================================================

def calculate_bearing(lat1, lon1, lat2, lon2):

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlon = math.radians(lon2 - lon1)

    x = (
        math.sin(dlon)
        * math.cos(lat2)
    )

    y = (
        math.cos(lat1)
        * math.sin(lat2)
        -
        math.sin(lat1)
        * math.cos(lat2)
        * math.cos(dlon)
    )

    bearing = math.degrees(
        math.atan2(x, y)
    )

    return (bearing + 360) % 360


# ============================================================
# DESTINATION POINT
# ============================================================

def destination_point(
    latitude,
    longitude,
    bearing,
    distance_km
):

    earth_radius_km = 6371.0

    lat1 = math.radians(latitude)
    lon1 = math.radians(longitude)

    bearing_rad = math.radians(bearing)

    angular_distance = (
        distance_km / earth_radius_km
    )

    lat2 = math.asin(
        math.sin(lat1)
        * math.cos(angular_distance)
        +
        math.cos(lat1)
        * math.sin(angular_distance)
        * math.cos(bearing_rad)
    )

    lon2 = (
        lon1
        +
        math.atan2(
            math.sin(bearing_rad)
            * math.sin(angular_distance)
            * math.cos(lat1),
            math.cos(angular_distance)
            -
            math.sin(lat1)
            * math.sin(lat2)
        )
    )

    return (
        math.degrees(lat2),
        math.degrees(lon2)
    )


# ============================================================
# OBSERVED AIS MOVEMENT
# ============================================================

def calculate_observed_movement(
    vessel_track,
    closest_index
):

    track = vessel_track.sort_values(
        "timestamp_utc"
    ).reset_index(drop=True)

    current_row = track.loc[closest_index]

    current_time = current_row["timestamp_utc"]

    previous_rows = track[
        track["timestamp_utc"] < current_time
    ]

    next_rows = track[
        track["timestamp_utc"] > current_time
    ]

    previous_row = None
    next_row = None

    if not previous_rows.empty:
        previous_row = previous_rows.iloc[-1]

    if not next_rows.empty:
        next_row = next_rows.iloc[0]

    # --------------------------------------------------------
    # Prefer movement segment before detection
    # --------------------------------------------------------

    if previous_row is not None:

        distance_km = haversine_km(
            previous_row["latitude"],
            previous_row["longitude"],
            current_row["latitude"],
            current_row["longitude"]
        )

        time_hours = (
            current_time
            - previous_row["timestamp_utc"]
        ).total_seconds() / 3600

        if time_hours > 0:

            observed_speed_kmh = (
                distance_km / time_hours
            )

            bearing = calculate_bearing(
                previous_row["latitude"],
                previous_row["longitude"],
                current_row["latitude"],
                current_row["longitude"]
            )

            return (
                bearing,
                observed_speed_kmh
            )

    # --------------------------------------------------------
    # Otherwise use segment after detection
    # --------------------------------------------------------

    if next_row is not None:

        distance_km = haversine_km(
            current_row["latitude"],
            current_row["longitude"],
            next_row["latitude"],
            next_row["longitude"]
        )

        time_hours = (
            next_row["timestamp_utc"]
            - current_time
        ).total_seconds() / 3600

        if time_hours > 0:

            observed_speed_kmh = (
                distance_km / time_hours
            )

            bearing = calculate_bearing(
                current_row["latitude"],
                current_row["longitude"],
                next_row["latitude"],
                next_row["longitude"]
            )

            return (
                bearing,
                observed_speed_kmh
            )

    return None, None


# ============================================================
# TRAJECTORY CONSISTENCY
# ============================================================

def calculate_trajectory_consistency(
    candidate,
    vessel_track,
    candidate_time
):

    vessel_track = (
        vessel_track
        .sort_values("timestamp_utc")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Find AIS point closest to candidate detection
    # --------------------------------------------------------

    time_difference = (
        vessel_track["timestamp_utc"]
        - candidate_time
    ).abs()

    closest_index = time_difference.idxmin()

    closest_row = vessel_track.loc[
        closest_index
    ]

    ais_time = closest_row[
        "timestamp_utc"
    ]

    time_difference_hours = abs(
        (
            ais_time
            - candidate_time
        ).total_seconds()
    ) / 3600

    vessel_lat = float(
        closest_row["latitude"]
    )

    vessel_lon = float(
        closest_row["longitude"]
    )

    reported_speed_knots = float(
        closest_row["speed_knots"]
    )

    reported_speed_kmh = (
        reported_speed_knots * 1.852
    )

    # --------------------------------------------------------
    # Calculate actual movement from coordinates
    # --------------------------------------------------------

    bearing, observed_speed_kmh = (
        calculate_observed_movement(
            vessel_track,
            closest_index
        )
    )

    # --------------------------------------------------------
    # Speed discrepancy
    # --------------------------------------------------------

    if (
        observed_speed_kmh is not None
        and reported_speed_kmh > 0
    ):

        speed_difference_percent = (
            abs(
                observed_speed_kmh
                - reported_speed_kmh
            )
            / reported_speed_kmh
        ) * 100

    else:

        speed_difference_percent = None

    # --------------------------------------------------------
    # Estimate movement distance
    #
    # Use observed coordinate-derived speed.
    # This avoids blindly trusting inconsistent demo AIS speed.
    # --------------------------------------------------------

    if observed_speed_kmh is not None:

        movement_distance_km = (
            observed_speed_kmh
            * time_difference_hours
        )

    else:

        movement_distance_km = (
            reported_speed_kmh
            * time_difference_hours
        )

    # --------------------------------------------------------
    # Backtrack/project trajectory
    # --------------------------------------------------------

    if bearing is not None:

        if ais_time < candidate_time:

            projected_bearing = bearing

        else:

            projected_bearing = (
                bearing + 180
            ) % 360

        estimated_lat, estimated_lon = (
            destination_point(
                vessel_lat,
                vessel_lon,
                projected_bearing,
                movement_distance_km
            )
        )

    else:

        estimated_lat = vessel_lat
        estimated_lon = vessel_lon

    trajectory_distance_km = haversine_km(
        estimated_lat,
        estimated_lon,
        candidate["latitude"],
        candidate["longitude"]
    )

    # --------------------------------------------------------
    # Trajectory score
    # --------------------------------------------------------

    if trajectory_distance_km <= 2:

        trajectory_score = 100
        interpretation = (
            "strong trajectory consistency"
        )

    elif trajectory_distance_km <= 5:

        trajectory_score = 80
        interpretation = (
            "good trajectory consistency"
        )

    elif trajectory_distance_km <= 10:

        trajectory_score = 60
        interpretation = (
            "moderate trajectory consistency"
        )

    elif trajectory_distance_km <= 20:

        trajectory_score = 35
        interpretation = (
            "weak trajectory consistency"
        )

    else:

        trajectory_score = 10
        interpretation = (
            "low trajectory consistency"
        )

    # --------------------------------------------------------
    # Temporal reliability
    # --------------------------------------------------------

    if time_difference_hours <= 1:

        temporal_factor = 1.0

    elif time_difference_hours <= 3:

        temporal_factor = 0.9

    elif time_difference_hours <= 6:

        temporal_factor = 0.7

    elif time_difference_hours <= 12:

        temporal_factor = 0.4

    else:

        temporal_factor = 0.1

    final_score = (
        trajectory_score
        * temporal_factor
    )

    return {
        "candidate_id": candidate["candidate_id"],
        "vessel_id": closest_row["vessel_id"],
        "vessel_name": closest_row["vessel_name"],

        "distance_to_candidate_km": round(
            haversine_km(
                vessel_lat,
                vessel_lon,
                candidate["latitude"],
                candidate["longitude"]
            ),
            2
        ),

        "time_difference_hours": round(
            time_difference_hours,
            2
        ),

        "reported_speed_knots": round(
            reported_speed_knots,
            2
        ),

        "observed_speed_kmh": (
            round(
                observed_speed_kmh,
                2
            )
            if observed_speed_kmh is not None
            else None
        ),

        "speed_difference_percent": (
            round(
                speed_difference_percent,
                2
            )
            if speed_difference_percent is not None
            else None
        ),

        "estimated_bearing_degrees": (
            round(bearing, 2)
            if bearing is not None
            else None
        ),

        "estimated_movement_distance_km": round(
            movement_distance_km,
            2
        ),

        "estimated_position_latitude": round(
            estimated_lat,
            6
        ),

        "estimated_position_longitude": round(
            estimated_lon,
            6
        ),

        "trajectory_distance_to_candidate_km": round(
            trajectory_distance_km,
            2
        ),

        "reverse_drift_score": round(
            final_score,
            2
        ),

        "interpretation": interpretation,
    }


# ============================================================
# MAIN
# ============================================================

def run_reverse_drift():

    candidates = pd.read_csv(
        CANDIDATE_FILE
    )

    ais = pd.read_csv(
        AIS_FILE
    )

    candidates[
        "detection_timestamp_utc"
    ] = pd.to_datetime(
        candidates[
            "detection_timestamp_utc"
        ],
        utc=True
    )

    ais["timestamp_utc"] = pd.to_datetime(
        ais["timestamp_utc"],
        utc=True
    )

    results = []

    for _, candidate in candidates.iterrows():

        candidate_time = candidate[
            "detection_timestamp_utc"
        ]

        for vessel_id, vessel_track in (
            ais.groupby("vessel_id")
        ):

            result = (
                calculate_trajectory_consistency(
                    candidate,
                    vessel_track,
                    candidate_time
                )
            )

            results.append(result)

    results_df = pd.DataFrame(
        results
    )

    results_df = results_df.sort_values(
        [
            "candidate_id",
            "reverse_drift_score"
        ],
        ascending=[
            True,
            False
        ]
    )

    results_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\nTrajectory-based reverse-drift "
        "consistency results:\n"
    )

    print(
        results_df.to_string(
            index=False
        )
    )

    print(
        f"\nSaved: {OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    run_reverse_drift()