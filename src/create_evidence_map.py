from pathlib import Path

import folium
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = PROJECT_DIR / "outputs" / "candidate_regions.csv"
AIS_PATH = PROJECT_DIR / "data" / "demo" / "ais_demo_data.csv"
RANKING_PATH = PROJECT_DIR / "outputs" / "vessel_suspect_ranking.csv"
OUTPUT_PATH = PROJECT_DIR / "outputs" / "spill_attribution_map.html"


def main():
    candidates = pd.read_csv(CANDIDATE_PATH)
    ais = pd.read_csv(AIS_PATH)
    rankings = pd.read_csv(RANKING_PATH)

    center = [candidates["latitude"].mean(), candidates["longitude"].mean()]
    evidence_map = folium.Map(location=center, zoom_start=10)

    top_suspects = (
        rankings.sort_values("suspicion_score", ascending=False)
        .groupby("candidate_id")
        .head(1)
        .set_index("candidate_id")
    )

    for candidate in candidates.itertuples(index=False):
        suspect = top_suspects.loc[candidate.candidate_id]

        popup_text = (
            f"<b>Preliminary candidate: {candidate.candidate_id}</b><br>"
            f"Area: {candidate.area_pixels:.0f} pixels<br>"
            f"Top ranked vessel: {suspect['vessel_name']}<br>"
            f"Suspicion score: {suspect['suspicion_score']}/100<br>"
            f"Closest distance: {suspect['closest_distance_km']:.2f} km<br>"
            f"Evidence: {suspect['evidence']}"
        )

        folium.CircleMarker(
            location=[candidate.latitude, candidate.longitude],
            radius=8,
            color="red",
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(popup_text, max_width=320),
            tooltip=f"Candidate {candidate.candidate_id}",
        ).add_to(evidence_map)

    colours = {
        "DEMO-001": "blue",
        "DEMO-002": "green",
        "DEMO-003": "purple",
        "DEMO-004": "orange",
    }

    for vessel_id, track in ais.groupby("vessel_id"):
        track = track.sort_values("timestamp_utc")
        coordinates = list(zip(track["latitude"], track["longitude"]))
        vessel_name = track["vessel_name"].iloc[0]
        vessel_type = track["vessel_type"].iloc[0]
        colour = colours.get(vessel_id, "gray")

        folium.PolyLine(
            locations=coordinates,
            color=colour,
            weight=3,
            tooltip=f"{vessel_name} ({vessel_type})",
        ).add_to(evidence_map)

        latest = track.iloc[-1]
        folium.Marker(
            location=[latest["latitude"], latest["longitude"]],
            popup=f"{vessel_name} — demo AIS track",
            icon=folium.Icon(color=colour, icon="ship", prefix="fa"),
        ).add_to(evidence_map)

    evidence_map.save(OUTPUT_PATH)
    print(f"Saved interactive map: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()