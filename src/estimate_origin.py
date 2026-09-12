from pathlib import Path
from math import asin, atan2, cos, degrees, radians, sin

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = PROJECT_DIR / "outputs" / "candidate_regions.csv"
OUTPUT_PATH = PROJECT_DIR / "outputs" / "estimated_spill_origins.csv"

# Initial demonstration assumptions.
# Replace these later with real wind and ocean-current data.
DRIFT_SPEED_KM_PER_HOUR = 0.6
HOURS_SINCE_RELEASE = 6
DRIFT_BEARING_DEGREES = 135  # toward south-east


def destination_point(latitude, longitude, bearing_degrees, distance_km):
    earth_radius_km = 6371.0
    bearing = radians(bearing_degrees)
    latitude_1 = radians(latitude)
    longitude_1 = radians(longitude)
    angular_distance = distance_km / earth_radius_km

    latitude_2 = asin(
        sin(latitude_1) * cos(angular_distance)
        + cos(latitude_1) * sin(angular_distance) * cos(bearing)
    )
    longitude_2 = longitude_1 + atan2(
        sin(bearing) * sin(angular_distance) * cos(latitude_1),
        cos(angular_distance) - sin(latitude_1) * sin(latitude_2),
    )

    return degrees(latitude_2), degrees(longitude_2)


def main():
    candidates = pd.read_csv(CANDIDATE_PATH)
    backtrack_distance = DRIFT_SPEED_KM_PER_HOUR * HOURS_SINCE_RELEASE
    reverse_bearing = (DRIFT_BEARING_DEGREES + 180) % 360

    records = []

    for candidate in candidates.itertuples(index=False):
        origin_latitude, origin_longitude = destination_point(
            candidate.latitude,
            candidate.longitude,
            reverse_bearing,
            backtrack_distance,
        )

        records.append(
            {
                "candidate_id": candidate.candidate_id,
                "observed_latitude": candidate.latitude,
                "observed_longitude": candidate.longitude,
                "estimated_origin_latitude": round(origin_latitude, 6),
                "estimated_origin_longitude": round(origin_longitude, 6),
                "backtrack_distance_km": backtrack_distance,
                "assumed_drift_bearing_degrees": DRIFT_BEARING_DEGREES,
                "assumed_hours_since_release": HOURS_SINCE_RELEASE,
            }
        )

    origins = pd.DataFrame(records)
    origins.to_csv(OUTPUT_PATH, index=False)

    print("Estimated spill-origin points:")
    print(origins.to_string(index=False))
    print(f"\nSaved file: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()