# OilSpill AI

### Explainable Multi-Modal Framework for Potential Oil-Spill Detection and Vessel Attribution

OilSpill AI is a research prototype for investigating potential marine oil-spill events by combining **Sentinel-1 SAR imagery**, **AIS vessel trajectories**, geometric analysis, trajectory consistency, and explainable evidence scoring.

The system is designed as an **investigative decision-support framework**, helping analysts identify potential spill candidates and rank vessels based on multiple supporting evidence factors.

> **Important:** This prototype does not establish legal responsibility or claim that a vessel caused an oil spill. Attribution scores represent computational evidence for investigation.

---

## 🚨 Problem Statement

Detecting an oil spill from satellite imagery is only the first step.

A potential dark region in SAR imagery may also be caused by several non-oil phenomena. Therefore, an investigation requires:

- Reliable candidate detection
- False-positive screening
- Vessel movement analysis
- Temporal correlation
- Spatial correlation
- Behavioural evidence
- Trajectory consistency
- Uncertainty-aware interpretation

Traditional approaches based only on satellite detection or nearest-vessel matching can provide insufficient evidence for source attribution.

---

## 🎯 Objectives

1. Detect potential oil-spill regions from Sentinel-1 SAR imagery.
2. Analyse candidate geometry to identify possible SAR false positives.
3. Correlate potential spill candidates with AIS vessel trajectories.
4. Develop an explainable multi-factor vessel attribution score.
5. Evaluate vessel trajectory and reverse-drift consistency.
6. Separate SAR candidate reliability from vessel attribution confidence.
7. Provide an interactive investigation dashboard.

---

## 🧠 Proposed Framework

```text
Sentinel-1 SAR Imagery
        │
        ▼
SAR Preprocessing
        │
        ▼
Low-Backscatter Candidate Detection
        │
        ▼
Candidate Geometry Analysis
        │
        ▼
False-Positive Screening
        │
        ▼
AIS Spatial & Temporal Correlation
        │
        ▼
Explainable Multi-Factor Attribution
        │
        ├── Spatial Proximity
        ├── Temporal Correlation
        ├── AIS Anomaly
        ├── Vessel Relevance
        ├── Track Consistency
        ├── Trajectory Consistency
        └── Reverse-Drift Consistency
        │
        ▼
Evidence Confidence Assessment
        │
        ▼
Investigation Dashboard