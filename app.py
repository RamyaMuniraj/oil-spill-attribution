from pathlib import Path

import pandas as pd
import streamlit as st
import pydeck as pdk


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"



# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="OilSpill AI | Maritime Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(0, 170, 255, 0.10), transparent 30%),
            radial-gradient(circle at 90% 10%, rgba(0, 255, 190, 0.06), transparent 25%),
            #07111f;
        color: #e8f1f8;
    }

    [data-testid="stHeader"] {
        background: rgba(7, 17, 31, 0.85);
    }

    [data-testid="stSidebar"] {
        background: #081522;
        border-right: 1px solid rgba(120, 180, 220, 0.15);
    }

    [data-testid="stSidebar"] * {
        color: #dceaf5;
    }

    h1, h2, h3 {
        color: #f3f9ff !important;
    }

    p, label {
        color: #b7c9d8 !important;
    }


    /* ---------- HERO ---------- */

    .hero {
        padding: 28px 30px;
        border-radius: 20px;
        background:
            linear-gradient(
                135deg,
                rgba(0, 120, 190, 0.25),
                rgba(7, 17, 31, 0.85)
            );
        border: 1px solid rgba(90, 190, 255, 0.25);
        margin-bottom: 20px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        color: #f5fbff;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #9fb7c9;
    }

    .system-status {
        display: inline-block;
        margin-top: 15px;
        padding: 7px 14px;
        border-radius: 999px;
        background: rgba(0, 210, 150, 0.10);
        border: 1px solid rgba(0, 210, 150, 0.35);
        color: #5ff0c0;
        font-size: 13px;
        font-weight: 700;
    }


    /* ---------- METRIC CARDS ---------- */

    .metric-card {
        padding: 20px;
        min-height: 125px;
        border-radius: 16px;
        background: rgba(14, 31, 48, 0.85);
        border: 1px solid rgba(120, 180, 220, 0.16);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }

    .metric-icon {
        font-size: 25px;
    }

    .metric-label {
        color: #8faabd;
        font-size: 13px;
        margin-top: 8px;
    }

    .metric-value {
        color: #f5fbff;
        font-size: 30px;
        font-weight: 800;
        margin-top: 2px;
    }


    /* ---------- SECTION ---------- */

    .section-title {
        font-size: 23px;
        font-weight: 750;
        color: #eef8ff;
        margin-top: 28px;
        margin-bottom: 12px;
    }


    /* ---------- INVESTIGATION CARD ---------- */

    .investigation {
        padding: 25px;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            rgba(15, 38, 58, 0.95),
            rgba(9, 25, 40, 0.95)
        );
        border: 1px solid rgba(80, 190, 255, 0.20);
    }

    .candidate-title {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
    }

    .suspect-name {
        font-size: 21px;
        font-weight: 700;
        color: #65d8ff;
    }

    .origin {
        font-family: monospace;
        color: #7ee8c7;
        font-size: 16px;
    }


    /* ---------- SCORE ---------- */

    .score-box {
        text-align: center;
        padding: 20px;
        border-radius: 16px;
        background: rgba(0, 0, 0, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .score-number {
        font-size: 48px;
        font-weight: 900;
        color: #ffcc66;
    }

    .score-label {
        color: #a9bac7;
        font-size: 13px;
    }


    /* ---------- BADGES ---------- */

    .badge-critical {
        display: inline-block;
        padding: 6px 13px;
        border-radius: 999px;
        background: rgba(255, 70, 70, 0.14);
        border: 1px solid rgba(255, 90, 90, 0.35);
        color: #ff7777;
        font-weight: 800;
        font-size: 12px;
    }

    .badge-high {
        display: inline-block;
        padding: 6px 13px;
        border-radius: 999px;
        background: rgba(255, 175, 60, 0.14);
        border: 1px solid rgba(255, 175, 60, 0.35);
        color: #ffc66d;
        font-weight: 800;
        font-size: 12px;
    }


    /* ---------- INFO BOX ---------- */

    .info-box {
        padding: 18px;
        border-radius: 14px;
        background: rgba(18, 42, 62, 0.65);
        border-left: 4px solid #35bdf5;
        margin: 8px 0;
    }

    .info-title {
        font-weight: 750;
        color: #eefaff;
        margin-bottom: 4px;
    }

    .info-text {
        color: #a9bfce;
        font-size: 14px;
    }


    /* ---------- FOOTER ---------- */

    .footer {
        margin-top: 40px;
        padding: 20px;
        text-align: center;
        color: #718899;
        font-size: 12px;
        border-top: 1px solid rgba(120, 180, 220, 0.12);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    candidates = pd.read_csv(
        OUTPUT_DIR / "candidate_regions.csv"
    )

    origins = pd.read_csv(
        OUTPUT_DIR / "estimated_spill_origins.csv"
    )

    rankings = pd.read_csv(
        OUTPUT_DIR / "vessel_suspect_ranking.csv"
)
    confidence_df = pd.read_csv( 
        OUTPUT_DIR / "attribution_confidence.csv"
)

    ais = pd.read_csv(
        PROJECT_DIR / "data" / "demo" / "ais_demo_data.csv"
)

    return candidates, origins, rankings, confidence_df, ais

candidates, origins, rankings, confidence_df, ais = load_data()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🌊 OilSpill AI")

    st.caption("Maritime intelligence & attribution platform")

    st.divider()

    st.markdown("### 🧭 Investigation")

    selected_candidate = st.selectbox(
        "Select candidate",
        candidates["candidate_id"].tolist(),
    )
    st.caption(
        f"🔎 Currently investigating candidate **{selected_candidate}**"
)
    st.divider()

    st.markdown("### 🛰️ Data sources")

    st.write("✓ Sentinel-1 SAR")
    st.write("✓ AIS vessel records")
    st.write("✓ Spatial correlation")
    st.write("✓ Reverse-drift estimation")

    st.divider()

    st.caption(
        "Prototype research system"
    )


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="hero">
        <div class="hero-title">
            🌊 OilSpill AI
        </div>

        <div class="hero-subtitle">
            Maritime Oil Spill Detection & Source Attribution Intelligence
        </div>

        <div class="system-status">
            ● ANALYSIS PIPELINE ONLINE
        </div>
    </div>
    """
)


st.caption(
    "Sentinel-1 SAR candidate detection • AIS correlation • "
    "vessel attribution • estimated spill origin"
)


# ============================================================
# IMPORTANT DATA WARNING
# ============================================================

st.warning(
    "⚠️ Prototype notice: AIS records currently used by this "
    "dashboard are simulated demonstration data. Results must "
    "not be interpreted as real-world attribution until verified "
    "historical AIS data and independent validation are used."
)


# ============================================================
# TOP METRICS
# ============================================================

max_score = rankings["suspicion_score"].max()

high_risk_count = len(
    confidence_df[
        confidence_df["confidence_level"] == "HIGH"
    ]
)

metric_cols = st.columns(4)


with metric_cols[0]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🛰️</div>
            <div class="metric-label">SAR CANDIDATES</div>
            <div class="metric-value">{len(candidates)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metric_cols[1]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🚢</div>
            <div class="metric-label">AIS RECORDS</div>
            <div class="metric-value">{len(ais)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metric_cols[2]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🚨</div>
            <div class="metric-label">HIGH-RISK VESSELS</div>
            <div class="metric-value">{high_risk_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metric_cols[3]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-label">MAX ATTRIBUTION SCORE</div>
            <div class="metric-value">{max_score:.0f}/100</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SELECTED CANDIDATE DATA
# ============================================================

selected_ranking = rankings[
    rankings["candidate_id"] == selected_candidate
].sort_values(
    "suspicion_score",
    ascending=False,
)

selected_origin_df = origins[
    origins["candidate_id"] == selected_candidate
]

if selected_ranking.empty:

    st.error(
        "No vessel ranking is available for this candidate."
    )
    st.stop()

if selected_origin_df.empty:

    st.error(
        "No estimated origin is available for this candidate."
    )
    st.stop()


top_suspect = selected_ranking.iloc[0]
selected_origin = selected_origin_df.iloc[0]

score = float(top_suspect["suspicion_score"])


# ============================================================
# INVESTIGATION HEADER
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Active Investigation</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([2.3, 1])

with col1:
    st.html(
        f"""
        <div class="investigation">

            <div class="candidate-title">
                Candidate {selected_candidate}
            </div>

            <br>

            <div style="color:#91a9ba;font-size:13px;">
                TOP ATTRIBUTED VESSEL
            </div>

            <div class="suspect-name">
                🚢 {top_suspect['vessel_name']}
            </div>

            <div style="color:#a7bac8;margin-top:4px;">
                Vessel type: {top_suspect['vessel_type']}
            </div>

            <br>

            <div class="info-box">
                <div class="info-title">
                    Evidence summary
                </div>

                <div class="info-text">
                    {top_suspect['evidence']}
                </div>
            </div>

            <br>

            <div style="color:#91a9ba;font-size:13px;">
                ESTIMATED SPILL ORIGIN
            </div>

            <div class="origin">
                {selected_origin['estimated_origin_latitude']:.4f}°,
                {selected_origin['estimated_origin_longitude']:.4f}°
            </div>

        </div>
        """
    )

with col2:

    if score >= 80:
        badge = "CRITICAL"
        badge_class = "badge-critical"
    elif score >= 60:
        badge = "HIGH"
        badge_class = "badge-high"
    elif score >= 30:
        badge = "MEDIUM"
        badge_class = "badge-high"
    else:
        badge = "LOW"
        badge_class = "badge-high"

    st.html(
        f"""
        <div class="score-box">

            <div class="score-label">
                AI ATTRIBUTION SCORE
            </div>

            <div class="score-number">
                {score:.0f}
            </div>

            <div class="score-label">
                OUT OF 100
            </div>

            <br>

            <span class="{badge_class}">
                {badge} PRIORITY
            </span>

        </div>
        """
    )

    st.progress(min(score / 100, 1.0))


# ============================================================
# EXPLAINABLE ATTRIBUTION
# ============================================================

st.markdown(
    '<div class="section-title">🧠 Explainable Attribution</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Breakdown of the independent evidence factors used to rank "
    "the vessel associated with the selected candidate."
)

# ------------------------------------------------------------
# ATTRIBUTION FACTORS
# ------------------------------------------------------------

attribution_factors = [
    (
        "📍",
        "Spatial Proximity",
        float(top_suspect["spatial_score"]),
        35,
        f"{top_suspect['closest_distance_km']:.2f} km from candidate",
    ),
    (
        "⏱️",
        "Temporal Correlation",
        float(top_suspect["temporal_score"]),
        25,
        "AIS timing relative to SAR detection",
    ),
    (
        "📡",
        "AIS Anomaly",
        float(top_suspect["anomaly_score"]),
        15,
        "AIS gap / anomaly indicator",
    ),
    (
        "🚢",
        "Vessel Relevance",
        float(top_suspect["vessel_relevance_score"]),
        15,
        f"{top_suspect['vessel_type']} classification",
    ),
    (
        "🛳️",
        "Track Consistency",
        float(top_suspect["track_consistency_score"]),
        10,
        "Consistency of vessel movement",
    ),
    (
        "🧭",
        "Trajectory Consistency",
        float(top_suspect["trajectory_consistency_score"]),
        10,
        "Approach/departure trajectory compatibility",
    ),
    (
        "🌊",
        "Reverse-Drift Consistency",
        float(top_suspect["reverse_drift_score"]),
        100,
        "Backward trajectory compatibility",
    ),
]


# ------------------------------------------------------------
# DISPLAY FIRST FOUR CORE FACTORS
# ------------------------------------------------------------

core_cols = st.columns(4)

for col, (
    icon,
    title,
    value,
    maximum,
    description,
) in zip(core_cols, attribution_factors[:4]):

    with col:

        percentage = (
            min(value / maximum * 100, 100)
            if maximum > 0
            else 0
        )

        st.html(
            f"""
            <div style="
                padding:20px;
                border-radius:16px;
                background:rgba(14,31,48,0.88);
                border:1px solid rgba(56,189,248,0.18);
                min-height:205px;
            ">

                <div style="
                    font-size:27px;
                ">
                    {icon}
                </div>

                <div style="
                    font-size:15px;
                    font-weight:750;
                    margin-top:9px;
                    color:#eef8ff;
                ">
                    {title}
                </div>

                <div style="
                    font-size:26px;
                    font-weight:850;
                    margin-top:11px;
                    color:#65d8ff;
                ">
                    {value:.1f}/{maximum}
                </div>

                <div style="
                    height:5px;
                    margin-top:10px;
                    border-radius:10px;
                    background:rgba(255,255,255,0.08);
                ">
                    <div style="
                        width:{percentage:.1f}%;
                        height:5px;
                        border-radius:10px;
                        background:#38bdf8;
                    "></div>
                </div>

                <div style="
                    margin-top:11px;
                    font-size:11px;
                    color:#8199aa;
                    line-height:1.5;
                ">
                    {description}
                </div>

            </div>
            """
        )


# ------------------------------------------------------------
# ADVANCED FACTORS
# ------------------------------------------------------------

st.markdown("### 🧭 Advanced Evidence")

advanced_cols = st.columns(3)

for col, (
    icon,
    title,
    value,
    maximum,
    description,
) in zip(advanced_cols, attribution_factors[4:]):

    with col:

        percentage = (
            min(value / maximum * 100, 100)
            if maximum > 0
            else 0
        )

        st.html(
            f"""
            <div style="
                padding:20px;
                border-radius:16px;
                background:rgba(14,31,48,0.88);
                border:1px solid rgba(126,232,199,0.18);
                min-height:190px;
            ">

                <div style="
                    font-size:27px;
                ">
                    {icon}
                </div>

                <div style="
                    font-size:15px;
                    font-weight:750;
                    margin-top:9px;
                    color:#eef8ff;
                ">
                    {title}
                </div>

                <div style="
                    font-size:25px;
                    font-weight:850;
                    margin-top:11px;
                    color:#7ee8c7;
                ">
                    {value:.1f}/{maximum}
                </div>

                <div style="
                    height:5px;
                    margin-top:10px;
                    border-radius:10px;
                    background:rgba(255,255,255,0.08);
                ">
                    <div style="
                        width:{percentage:.1f}%;
                        height:5px;
                        border-radius:10px;
                        background:#7ee8c7;
                    "></div>
                </div>

                <div style="
                    margin-top:11px;
                    font-size:11px;
                    color:#8199aa;
                    line-height:1.5;
                ">
                    {description}
                </div>

            </div>
            """
        )


# ------------------------------------------------------------
# INTERPRETATION
# ------------------------------------------------------------

st.markdown("### 🔎 Evidence Interpretation")

st.html(
    f"""
    <div style="
        padding:20px 24px;
        border-radius:16px;
        background:linear-gradient(
            135deg,
            rgba(18,42,62,0.75),
            rgba(10,28,44,0.85)
        );
        border:1px solid rgba(56,189,248,0.18);
        line-height:1.7;
    ">

        <div style="
            font-size:15px;
            font-weight:750;
            color:#eef8ff;
        ">
            Computational evidence summary
        </div>

        <div style="
            margin-top:10px;
            color:#a9bfce;
            font-size:13px;
        ">

            <b style="color:#65d8ff;">
                {top_suspect['vessel_name']}
            </b>
            is ranked highest for
            <b>{selected_candidate}</b>
            based on combined spatial, temporal,
            vessel, AIS and trajectory evidence.

            <br><br>

            The strongest spatial match is
            <b>{top_suspect['closest_distance_km']:.2f} km</b>
            from the detected candidate region.

            The attribution system also evaluates
            AIS anomalies, vessel relevance, track consistency,
            trajectory consistency and reverse-drift compatibility.

            <br><br>

            <span style="color:#ffd166;">
                ⚠️ This is an explainable computational ranking,
                not proof of responsibility.
            </span>

        </div>

    </div>
    """
)

# ============================================================
# MARITIME INVESTIGATION MAP
# ============================================================

st.markdown("## 🗺️ Maritime Investigation Map")

st.caption(
    "Selected candidate, estimated spill origin and AIS trajectory "
    "of the highest-ranked vessel"
)

# ------------------------------------------------------------
# SELECTED CANDIDATE
# ------------------------------------------------------------

selected_candidate_row = candidates[
    candidates["candidate_id"] == selected_candidate
].iloc[0]

candidate_lat = float(
    selected_candidate_row["latitude"]
)

candidate_lon = float(
    selected_candidate_row["longitude"]
)


# ------------------------------------------------------------
# SELECTED ORIGIN
# ------------------------------------------------------------

origin_lat = float(
    selected_origin["estimated_origin_latitude"]
)

origin_lon = float(
    selected_origin["estimated_origin_longitude"]
)


# ------------------------------------------------------------
# SELECTED VESSEL AIS TRACK
# ------------------------------------------------------------

selected_vessel_id = top_suspect["vessel_id"]

vessel_track = ais[
    ais["vessel_id"] == selected_vessel_id
].copy()

vessel_track["timestamp_utc"] = pd.to_datetime(
    vessel_track["timestamp_utc"],
    errors="coerce",
    utc=True,
)

vessel_track = vessel_track.sort_values(
    "timestamp_utc"
)


# ------------------------------------------------------------
# TRAJECTORY PATH
# ------------------------------------------------------------

trajectory_data = []

for _, row in vessel_track.iterrows():

    trajectory_data.append(
        [
            float(row["longitude"]),
            float(row["latitude"]),
        ]
    )


trajectory_df = pd.DataFrame(
    {
        "path": [trajectory_data],
        "vessel": [top_suspect["vessel_name"]],
    }
)


# ------------------------------------------------------------
# CANDIDATE / ORIGIN POINTS
# ------------------------------------------------------------

candidate_map_df = pd.DataFrame(
    [
        {
            "latitude": candidate_lat,
            "longitude": candidate_lon,
            "label": f"Candidate {selected_candidate}",
        }
    ]
)

origin_map_df = pd.DataFrame(
    [
        {
            "latitude": origin_lat,
            "longitude": origin_lon,
            "label": "Estimated spill origin",
        }
    ]
)


# ------------------------------------------------------------
# VESSEL POSITIONS
# ------------------------------------------------------------

vessel_map_df = vessel_track[
    ["latitude", "longitude", "timestamp_utc"]
].copy()

vessel_map_df["label"] = (
    top_suspect["vessel_name"]
)


# ------------------------------------------------------------
# MAP VIEW
# ------------------------------------------------------------

view_state = pdk.ViewState(
    latitude=candidate_lat,
    longitude=candidate_lon,
    zoom=9,
    pitch=35,
    bearing=0,
)


# ------------------------------------------------------------
# LAYERS
# ------------------------------------------------------------

trajectory_layer = pdk.Layer(
    "PathLayer",
    data=trajectory_df,
    get_path="path",
    get_width=6,
    width_min_pixels=3,
    pickable=True,
)


vessel_layer = pdk.Layer(
    "ScatterplotLayer",
    data=vessel_map_df,
    get_position="[longitude, latitude]",
    get_radius=180,
    radius_min_pixels=5,
    radius_max_pixels=14,
    get_fill_color=[40, 140, 255, 220],
    pickable=True,
)


candidate_layer = pdk.Layer(
    "ScatterplotLayer",
    data=candidate_map_df,
    get_position="[longitude, latitude]",
    get_radius=450,
    radius_min_pixels=10,
    radius_max_pixels=22,
    get_fill_color=[255, 50, 80, 240],
    pickable=True,
)


origin_layer = pdk.Layer(
    "ScatterplotLayer",
    data=origin_map_df,
    get_position="[longitude, latitude]",
    get_radius=300,
    radius_min_pixels=8,
    radius_max_pixels=18,
    get_fill_color=[255, 150, 50, 240],
    pickable=True,
)


# ------------------------------------------------------------
# DECK MAP
# ------------------------------------------------------------

deck = pdk.Deck(
    map_style=None,
    initial_view_state=view_state,
    layers=[
        trajectory_layer,
        vessel_layer,
        origin_layer,
        candidate_layer,
    ],
    tooltip={
        "html": """
            <b>{label}</b>
        """,
        "style": {
            "backgroundColor": "#0d2033",
            "color": "white",
        },
    },
)


st.pydeck_chart(
    deck,
    width="stretch",
    height=520,
)


# ------------------------------------------------------------
# MAP LEGEND
# ------------------------------------------------------------

st.markdown(
    f"🔴 Candidate **{selected_candidate}**   &nbsp;&nbsp; "
    f"🟠 Estimated origin   &nbsp;&nbsp; "
    f"🔵 **{top_suspect['vessel_name']}** AIS track"
)


# ------------------------------------------------------------
# MAP INTERPRETATION
# ------------------------------------------------------------

st.html(
    f"""
    <div style="
        margin-top:14px;
        padding:18px 20px;
        border-radius:14px;
        background:rgba(18,42,62,0.60);
        border-left:4px solid #38bdf8;
    ">

        <div style="
            font-weight:750;
            color:#eef8ff;
        ">
            🧭 Trajectory interpretation
        </div>

        <div style="
            margin-top:7px;
            color:#9fb4c3;
            font-size:13px;
            line-height:1.6;
        ">
            The blue track represents the AIS positions of the
            highest-ranked vessel,
            <b style="color:#65d8ff;">
                {top_suspect['vessel_name']}
            </b>.

            The red marker identifies candidate
            <b>{selected_candidate}</b>, while the orange marker
            represents the computationally estimated spill origin.

            The displayed trajectory provides visual supporting
            evidence for the spatial and temporal attribution analysis.
            It should not be interpreted as proof of spill responsibility.
        </div>

    </div>
    """
)

# ============================================================
# AIS EVENT TIMELINE
# ============================================================

st.markdown("## 🕒 AIS Event Timeline")
st.caption(
    f"Movement history of the highest-ranked vessel for candidate {selected_candidate}"
)

timeline_source = pd.read_csv("data/demo/ais_demo_data.csv")

timeline_df = timeline_source[
    timeline_source["vessel_id"] == top_suspect["vessel_id"]
].copy()

timeline_df["timestamp_utc"] = pd.to_datetime(
    timeline_df["timestamp_utc"],
    utc=True
)

timeline_df = timeline_df.sort_values("timestamp_utc")

detection_time = pd.to_datetime(
    selected_candidate_row["detection_timestamp_utc"],
    utc=True
)

timeline_df["hours_from_detection"] = (
    (timeline_df["timestamp_utc"] - detection_time)
    .dt.total_seconds() / 3600
).round(1)

for _, event in timeline_df.iterrows():

    event_time = event["timestamp_utc"].strftime("%H:%M UTC")

    gap_status = (
        "⚠️ AIS GAP"
        if bool(event["ais_gap_flag"])
        else "✓ AIS received"
    )

    relative_time = event["hours_from_detection"]

    if relative_time < 0:
        timing_text = f"{abs(relative_time)} h before detection"
    elif relative_time == 0:
        timing_text = "At detection time"
    else:
        timing_text = f"{relative_time} h after detection"

    st.markdown(
        f"""
        <div style="
            padding:14px 18px;
            margin:8px 0;
            border-left:4px solid #35bdf6;
            border-radius:10px;
            background:rgba(14,31,48,0.75);
        ">
            <b>{event_time}</b>
            &nbsp;&nbsp; {timing_text}<br>
            📍 Position: {event['latitude']:.4f}, {event['longitude']:.4f}<br>
            🚢 Speed: {event['speed_knots']:.1f} knots
            &nbsp;&nbsp; | &nbsp;&nbsp;
            {gap_status}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# VESSEL INTELLIGENCE
# ============================================================

st.markdown("## 🚢 Vessel Intelligence")

st.caption(
    "AIS-based vessel correlation and computational suspicion ranking"
)

left, right = st.columns([1.2, 1])

with left:
    st.markdown("### 📊 Suspicion Ranking")
    st.caption(
        "Relative vessel suspicion score for the selected candidate"
    )

    chart_data = selected_ranking[
        ["vessel_name", "suspicion_score"]
    ].copy()

    chart_data = chart_data.set_index("vessel_name")

    st.bar_chart(
        chart_data,
        height=340,
        horizontal=True,
    )


with right:
    st.markdown("### 🚢 Ranked Vessels")
    st.caption(
        "Top vessels associated with the selected slick candidate"
    )

    display_data = selected_ranking[
        [
            "vessel_name",
            "vessel_type",
            "closest_distance_km",
            "suspicion_score",
            "temporal_score",
            "anomaly_score",
            "vessel_relevance_score",
            "track_consistency_score",
            "trajectory_consistency_score",
            "reverse_drift_score",
        ]
    ].copy()

    display_data.columns = [
        "Vessel",
        "Type",
        "Distance (km)",
        "Score",
        "Temporal",
        "AIS Anomaly",
        "Vessel Relevance",
        "Track",
        "Trajectory",
        "Reverse Drift",
    ]

    st.dataframe(
        display_data,
        hide_index=True,
        width="stretch",
        height=340,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Suspicion Score",
                help="Computational attribution score from 0 to 100",
                min_value=0,
                max_value=100,
                format="%d",
            ),
            "Distance (km)": st.column_config.NumberColumn(
                "Distance (km)",
                format="%.2f",
            ),
            "Temporal": st.column_config.NumberColumn(
                "Temporal",
                format="%.1f",
            ),
            "AIS Anomaly": st.column_config.NumberColumn(
                "AIS Anomaly",
                format="%.1f",
            ),
            "Vessel Relevance": st.column_config.NumberColumn(
                "Vessel Relevance",
                format="%.1f",
            ),
            "Track": st.column_config.NumberColumn(
                "Track",
                format="%.1f",
            ),
            "Trajectory": st.column_config.NumberColumn(
                "Trajectory",
                format="%.1f",
            ),
            "Reverse Drift": st.column_config.NumberColumn(
                "Reverse Drift",
                format="%.1f",
            ),
        },
    )
    # ============================================================
# WHY THIS VESSEL IS RANKED #1
# ============================================================

st.markdown("### 🔎 Why This Vessel Is Ranked #1")

distance = float(top_suspect["closest_distance_km"])
temporal = float(top_suspect["temporal_score"])
anomaly = float(top_suspect["anomaly_score"])
relevance = float(top_suspect["vessel_relevance_score"])
track = float(top_suspect["track_consistency_score"])
trajectory = float(top_suspect["trajectory_consistency_score"])
reverse_drift = float(top_suspect["reverse_drift_score"])


# ------------------------------------------------------------
# EVIDENCE STRENGTH CLASSIFICATION
# ------------------------------------------------------------

if distance <= 2:
    spatial_strength = "STRONG"
elif distance <= 5:
    spatial_strength = "MODERATE"
else:
    spatial_strength = "WEAK"


if temporal >= 20:
    temporal_strength = "STRONG"
elif temporal >= 10:
    temporal_strength = "MODERATE"
else:
    temporal_strength = "WEAK"


if trajectory >= 7 and reverse_drift >= 80:
    trajectory_strength = "STRONG"
elif trajectory >= 4 or reverse_drift >= 50:
    trajectory_strength = "MODERATE"
else:
    trajectory_strength = "WEAK"


# ------------------------------------------------------------
# DETAILED EVIDENCE POINTS
# ------------------------------------------------------------

evidence_points = []


if distance <= 2:
    evidence_points.append(
        f"📍 Very close spatial proximity — "
        f"{distance:.2f} km from the candidate"
    )
elif distance <= 5:
    evidence_points.append(
        f"📍 Moderate spatial proximity — "
        f"{distance:.2f} km from the candidate"
    )


if temporal >= 20:
    evidence_points.append(
        f"⏱️ Strong temporal correlation — "
        f"{temporal:.1f}/25"
    )
elif temporal >= 10:
    evidence_points.append(
        f"⏱️ Moderate temporal correlation — "
        f"{temporal:.1f}/25"
    )


if anomaly > 0:
    evidence_points.append(
        f"⚠️ AIS anomaly evidence — "
        f"{anomaly:.1f}/15"
    )


if relevance >= 10:
    evidence_points.append(
        f"🚢 High vessel relevance — "
        f"{relevance:.1f}/15"
    )
elif relevance > 0:
    evidence_points.append(
        f"🚢 Vessel relevance evidence — "
        f"{relevance:.1f}/15"
    )


if track >= 7:
    evidence_points.append(
        f"🛳️ Strong track consistency — "
        f"{track:.1f}/10"
    )
elif track >= 4:
    evidence_points.append(
        f"🛳️ Moderate track consistency — "
        f"{track:.1f}/10"
    )


if trajectory >= 7:
    evidence_points.append(
        f"🧭 Strong trajectory consistency — "
        f"{trajectory:.1f}/10"
    )
elif trajectory >= 4:
    evidence_points.append(
        f"🧭 Moderate trajectory consistency — "
        f"{trajectory:.1f}/10"
    )


if reverse_drift >= 80:
    evidence_points.append(
        f"🔄 Strong reverse-drift consistency — "
        f"{reverse_drift:.1f}/100"
    )
elif reverse_drift >= 50:
    evidence_points.append(
        f"🔄 Moderate reverse-drift consistency — "
        f"{reverse_drift:.1f}/100"
    )


# ------------------------------------------------------------
# DISPLAY DETAILED EVIDENCE
# ------------------------------------------------------------

if evidence_points:

    st.markdown(
        "\n".join(
            f"- {point}"
            for point in evidence_points
        )
    )

else:

    st.info(
        "No strong evidence factors exceeded the current "
        "interpretation thresholds."
    )


# ------------------------------------------------------------
# EVIDENCE STRENGTH
# ------------------------------------------------------------

st.markdown("### 📌 Evidence Strength")

strength_col1, strength_col2, strength_col3 = st.columns(3)


with strength_col1:

    st.metric(
        "📍 Spatial Evidence",
        spatial_strength
    )

    st.caption(
        f"Distance: {distance:.2f} km"
    )


with strength_col2:

    st.metric(
        "⏱️ Temporal Evidence",
        temporal_strength
    )

    st.caption(
        f"Temporal score: {temporal:.1f}/25"
    )


with strength_col3:

    st.metric(
        "🧭 Trajectory Evidence",
        trajectory_strength
    )

    st.caption(
        f"Trajectory: {trajectory:.1f}/10 • "
        f"Reverse drift: {reverse_drift:.1f}/100"
    )


st.caption(
    "Evidence is presented as computational support for "
    "investigation, not proof of spill responsibility."
)
# ============================================================
# INVESTIGATION CONFIDENCE & SAR RELIABILITY
# ============================================================

st.markdown("## 🧠 Investigation Confidence")

st.caption(
    "Attribution confidence and SAR candidate reliability are "
    "reported separately. Neither represents a probability of responsibility."
)

confidence_row = confidence_df[
    (confidence_df["candidate_id"] == selected_candidate)
    &
    (confidence_df["vessel_id"] == top_suspect["vessel_id"])
]

if not confidence_row.empty:

    confidence_row = confidence_row.iloc[0]

    confidence_level = str(
        confidence_row["confidence_level"]
    )

    evidence_count = int(
        confidence_row["evidence_count"]
    )

    false_positive_score = float(
        confidence_row["false_positive_score"]
    )

    false_positive_risk = str(
        confidence_row["false_positive_risk"]
    )

    candidate_status = str(
        confidence_row["candidate_status"]
    )

else:

    confidence_level = "UNKNOWN"
    evidence_count = 0
    false_positive_score = 0
    false_positive_risk = "UNKNOWN"
    candidate_status = "UNKNOWN"


confidence_cols = st.columns(2)


# ------------------------------------------------------------
# VESSEL ATTRIBUTION CONFIDENCE
# ------------------------------------------------------------

with confidence_cols[0]:

    st.html(
        f"""
        <div class="glass-card"
             style="
                padding:25px;
                border-radius:18px;
                background:rgba(14,31,48,0.90);
                border:1px solid rgba(56,189,248,0.22);
                min-height:230px;
             ">

            <div style="
                color:#65d8ff;
                font-size:13px;
                font-weight:700;
                letter-spacing:1px;
            ">
                VESSEL ATTRIBUTION CONFIDENCE
            </div>

            <div style="
                font-size:42px;
                font-weight:850;
                margin-top:10px;
                color:#f5fbff;
            ">
                {score:.0f}/100
            </div>

            <div style="
                font-size:20px;
                font-weight:750;
                margin-top:5px;
                color:#7ee8c7;
            ">
                {confidence_level}
            </div>

            <div style="
                margin-top:14px;
                color:#a9bfce;
                font-size:13px;
            ">
                {evidence_count}/7 supporting evidence indicators
            </div>

            <div style="
                margin-top:15px;
                color:#8199aa;
                font-size:12px;
                line-height:1.6;
            ">
                Computational vessel-attribution confidence based on
                spatial, temporal, AIS anomaly, vessel relevance,
                track, trajectory and reverse-drift consistency.
            </div>

        </div>
        """
    )


# ------------------------------------------------------------
# SAR CANDIDATE RELIABILITY
# ------------------------------------------------------------

with confidence_cols[1]:

    risk_display = false_positive_risk.replace(
        "_", " "
    )

    status_display = candidate_status.replace(
        "_", " "
    )

    st.html(
        f"""
        <div class="glass-card"
             style="
                padding:25px;
                border-radius:18px;
                background:rgba(14,31,48,0.90);
                border:1px solid rgba(126,232,199,0.22);
                min-height:230px;
             ">

            <div style="
                color:#7ee8c7;
                font-size:13px;
                font-weight:700;
                letter-spacing:1px;
            ">
                SAR CANDIDATE RELIABILITY
            </div>

            <div style="
                font-size:42px;
                font-weight:850;
                margin-top:10px;
                color:#f5fbff;
            ">
                {false_positive_score:.0f}/100
            </div>

            <div style="
                font-size:18px;
                font-weight:750;
                margin-top:5px;
                color:#7ee8c7;
            ">
                {risk_display}
            </div>

            <div style="
                margin-top:14px;
                color:#a9bfce;
                font-size:13px;
            ">
                Candidate status:
                <b style="color:#f5fbff;">
                    {status_display}
                </b>
            </div>

            <div style="
                margin-top:15px;
                color:#8199aa;
                font-size:12px;
                line-height:1.6;
            ">
                Geometry-based heuristic assessment of potential
                SAR false-positive characteristics. This does not
                confirm or reject the presence of oil.
            </div>

        </div>
        """
    )
# ============================================================
# SYSTEM EVALUATION
# ============================================================

st.markdown("## 📈 System Evaluation")

st.caption(
    "Prototype-level evaluation statistics generated from the current "
    "SAR, AIS correlation, filtering, and trajectory-analysis pipeline"
)

evaluation_file = PROJECT_DIR / "outputs" / "evaluation_summary.csv"

if evaluation_file.exists():

    evaluation_df = pd.read_csv(evaluation_file)

    evaluation = evaluation_df.iloc[0]

    eval_col1, eval_col2, eval_col3, eval_col4 = st.columns(4)

    with eval_col1:
        st.metric(
            "🛰️ SAR Candidates",
            int(evaluation["sar_candidates_detected"])
        )

    with eval_col2:
        st.metric(
            "✅ Retention Rate",
            f"{evaluation['retention_rate_percent']:.1f}%"
        )

    with eval_col3:
        st.metric(
            "🚢 Avg Top-Vessel Score",
            f"{evaluation['average_top_vessel_score']:.1f}/100"
        )

    with eval_col4:
        st.metric(
            "🎯 High-Confidence Cases",
            int(evaluation["high_confidence_cases"])
        )

    st.markdown("### 🔬 Evaluation Breakdown")

    breakdown_col1, breakdown_col2 = st.columns(2)

    with breakdown_col1:

        st.markdown("**SAR Candidate Screening**")

        st.write(
            f"Candidates detected: "
            f"**{int(evaluation['sar_candidates_detected'])}**"
        )

        st.write(
            f"Candidates retained: "
            f"**{int(evaluation['candidates_retained'])}**"
        )

        st.write(
            f"Review required: "
            f"**{int(evaluation['candidates_review_required'])}**"
        )

        st.write(
            f"Retention rate: "
            f"**{evaluation['retention_rate_percent']:.1f}%**"
        )

    with breakdown_col2:

        st.markdown("**Trajectory Consistency**")

        st.write(
            f"Strong cases: "
            f"**{int(evaluation['strong_trajectory_cases'])}**"
        )

        st.write(
            f"Good cases: "
            f"**{int(evaluation['good_trajectory_cases'])}**"
        )

        st.write(
            f"Moderate cases: "
            f"**{int(evaluation['moderate_trajectory_cases'])}**"
        )

        st.write(
            f"Weak/low cases: "
            f"**{int(evaluation['weak_or_low_trajectory_cases'])}**"
        )

        st.write(
            f"Average reverse-drift score: "
            f"**{evaluation['average_reverse_drift_score']:.1f}/100**"
        )

    st.info(
        "These values represent prototype/system evaluation statistics. "
        "They are not accuracy, precision, recall, or probability-of-"
        "responsibility metrics because independently labeled ground-truth "
        "data are not currently available."
    )

else:

    st.warning(
        "Evaluation results are not available. "
        "Run `python src\\evaluate.py` first."
    )    

# ============================================================
# RESEARCH PIPELINE
# ============================================================

st.markdown(
    '<div class="section-title">⚙️ Research Pipeline</div>',
    unsafe_allow_html=True,
)

pipeline_cols = st.columns(6)

pipeline = [
    ("🛰️", "SAR", "Satellite imagery"),
    ("🔬", "Detection", "Low-backscatter analysis"),
    ("🎯", "Candidates", "Slick region extraction"),
    ("🚢", "AIS", "Spatial + temporal correlation"),
    ("🧭", "Trajectory", "Track + reverse drift"),
    ("🤖", "Attribution", "Explainable evidence ranking"),
]

for col, (icon, title, description) in zip(
    pipeline_cols,
    pipeline,
):

    with col:

        st.html(
            f"""
            <div class="metric-card">

                <div style="font-size:25px;">
                    {icon}
                </div>

                <div style="
                    font-weight:750;
                    color:#eef8ff;
                    margin-top:8px;
                ">
                    {title}
                </div>

                <div style="
                    color:#8199aa;
                    font-size:11px;
                    margin-top:5px;
                ">
                    {description}
                </div>

            </div>
            """
        )


# ============================================================
# SAR ANALYSIS
# ============================================================

st.markdown(
    "## 🛰️ SAR Detection Analysis"
)
st.caption(
    "Sentinel-1 SAR imagery is analysed to identify low-backscatter "
    "ocean-surface regions that may indicate potential oil slicks."
)
sar_steps = st.columns(3)

sar_process = [
    ("🛰️", "SAR Input", "Sentinel-1 imagery"),
    ("🌊", "Backscatter Analysis", "Detect dark ocean regions"),
    ("🎯", "Candidate Extraction", "Generate potential slicks"),
]

for col, (icon, title, description) in zip(sar_steps, sar_process):
    with col:
        st.html(
            f"""
            <div class="metric-card" style="text-align:center;">
                <div style="font-size:28px;">{icon}</div>
                <div style="font-weight:750; margin-top:8px;">
                    {title}
                </div>
                <div style="color:#8199aa; font-size:11px; margin-top:5px;">
                    {description}
                </div>
            </div>
            """
        )
with st.expander(
    "Open Sentinel-1 candidate detection visualization",
    expanded=True,
):

    sar_col1, sar_col2 = st.columns([1.7, 1])

    with sar_col1:
        st.image(
            OUTPUT_DIR / "candidate_regions.png",
            caption="Sentinel-1 SAR candidate detection — preliminary low-backscatter regions",
            width="stretch",
        )

    with sar_col2:
        st.html(
            """
            <div style="
                background:#0d2033;
                border:1px solid #214a65;
                border-radius:16px;
                padding:22px;
                min-height:300px;
            ">

                <div style="
                    color:#45c7ff;
                    font-size:13px;
                    font-weight:700;
                    letter-spacing:1px;
                ">
                    DETECTION INTERPRETATION
                </div>

                <div style="
                    color:#f1f6fa;
                    font-size:22px;
                    font-weight:700;
                    margin-top:10px;
                ">
                    Low-backscatter candidates
                </div>

                <div style="
                    color:#9fb4c3;
                    line-height:1.7;
                    margin-top:15px;
                ">
                    The SAR processing stage identifies ocean-surface
                    regions exhibiting reduced radar backscatter.
                    These regions may be consistent with surface oil
                    slicks and are therefore treated as candidate
                    detections.
                </div>

                <div style="
                    margin-top:20px;
                    padding:12px;
                    border-radius:10px;
                    background:#132c40;
                    color:#ffd166;
                ">
                    ⚠️ Candidate detection ≠ confirmed oil spill
                </div>

            </div>
            """
        )
        # ============================================================
# RESEARCH LIMITATIONS
# ============================================================

st.markdown("## ⚠️ Research Limitations")

st.html("""
<div class="glass-card" style="padding:24px;">

    <div style="font-size:18px; font-weight:750;">
        Important interpretation notes
    </div>

    <div style="
        margin-top:14px;
        color:#9fb4c3;
        line-height:1.7;
    ">
        <b>1. SAR candidates:</b>
        Low-backscatter regions are potential slick detections,
        not confirmed oil spills.
        <br><br>

        <b>2. AIS correlation:</b>
        Vessel proximity and movement provide supporting evidence,
        not definitive proof of responsibility.
        <br><br>

        <b>3. AIS data:</b>
        The current prototype uses simulated AIS records for
        pipeline testing.
        <br><br>

        <b>4. Origin estimation:</b>
        Reverse-drift results are computational estimates and
        depend on environmental and oceanographic conditions.
        <br><br>

        <b>5. Real-world deployment:</b>
        Verified historical AIS, validated environmental data
        and independent expert or authority review are required.
    </div>

</div>
""")
# ============================================================
# FOOTER
# ============================================================

st.html("""
<div style="
    margin-top:40px;
    padding:25px;
    text-align:center;
    border-top:1px solid rgba(120,180,220,0.15);
    color:#8199aa;
    font-size:12px;
    line-height:1.7;
">

    <div style="
        font-size:16px;
        font-weight:750;
        color:#dcecf7;
        margin-bottom:8px;
    ">
        🌊 OilSpill AI — Research Prototype
    </div>

    <div>
        Sentinel-1 SAR • AIS Correlation • Vessel Attribution
        • Reverse Drift Origin Estimation
    </div>

    <div style="margin-top:10px; opacity:0.65;">
        For research and demonstration purposes only.
    </div>

</div>
""")