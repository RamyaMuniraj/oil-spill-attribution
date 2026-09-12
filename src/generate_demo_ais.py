from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_DIR / "data" / "demo" / "ais_demo_data.csv"


def main():
    # Simulated AIS records for pipeline testing only.
    # They are not real vessel identities or real AIS transmissions.
    records = [
        {
            "vessel_id": "DEMO-001",
            "vessel_name": "MV Ocean Guardian",
            "vessel_type": "Tanker",
            "timestamp_utc": "2026-09-06T06:00:00Z",
            "latitude": 18.430000,
            "longitude": 72.350000,
            "speed_knots": 11.2,
            "ais_gap_flag": False,
        },
        {
            "vessel_id": "DEMO-001",
            "vessel_name": "MV Ocean Guardian",
            "vessel_type": "Tanker",
            "timestamp_utc": "2026-09-06T08:00:00Z",
            "latitude": 18.416000,
            "longitude": 72.344500,
            "speed_knots": 4.1,
            "ais_gap_flag": True,
        },
        {
            "vessel_id": "DEMO-001",
            "vessel_name": "MV Ocean Guardian",
            "vessel_type": "Tanker",
            "timestamp_utc": "2026-09-06T12:00:00Z",
            "latitude": 18.395000,
            "longitude": 72.330000,
            "speed_knots": 10.8,
            "ais_gap_flag": False,
        },
        {
            "vessel_id": "DEMO-002",
            "vessel_name": "MV Blue Horizon",
            "vessel_type": "Cargo",
            "timestamp_utc": "2026-09-06T06:00:00Z",
            "latitude": 18.670000,
            "longitude": 72.480000,
            "speed_knots": 12.5,
            "ais_gap_flag": False,
        },
        {
            "vessel_id": "DEMO-002",
            "vessel_name": "MV Blue Horizon",
            "vessel_type": "Cargo",
            "timestamp_utc": "2026-09-06T12:00:00Z",
            "latitude": 18.620000,
            "longitude": 72.440000,
            "speed_knots": 12.1,
            "ais_gap_flag": False,
        },
        {
            "vessel_id": "DEMO-003",
            "vessel_name": "Sea Pearl",
            "vessel_type": "Fishing",
            "timestamp_utc": "2026-09-06T06:00:00Z",
            "latitude": 18.535000,
            "longitude": 72.150000,
            "speed_knots": 7.4,
            "ais_gap_flag": False,
        },
        {
            "vessel_id": "DEMO-003",
            "vessel_name": "Sea Pearl",
            "vessel_type": "Fishing",
            "timestamp_utc": "2026-09-06T12:00:00Z",
            "latitude": 18.500000,
            "longitude": 72.120000,
            "speed_knots": 6.8,
            "ais_gap_flag": False,
        },
        {
            "vessel_id": "DEMO-004",
            "vessel_name": "Coastal Trader",
            "vessel_type": "Cargo",
            "timestamp_utc": "2026-09-06T06:00:00Z",
            "latitude": 18.570000,
            "longitude": 72.360000,
            "speed_knots": 10.0,
            "ais_gap_flag": False,
        },
        {
            "vessel_id": "DEMO-004",
            "vessel_name": "Coastal Trader",
            "vessel_type": "Cargo",
            "timestamp_utc": "2026-09-06T12:00:00Z",
            "latitude": 18.590000,
            "longitude": 72.390000,
            "speed_knots": 9.8,
            "ais_gap_flag": False,
        },
    ]

    ais_data = pd.DataFrame(records)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ais_data.to_csv(OUTPUT_PATH, index=False)

    print(f"Demo AIS records created: {len(ais_data)}")
    print(f"Saved file: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()