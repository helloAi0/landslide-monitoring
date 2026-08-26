# 🌍 GeoShield Enterprise - Landslide Intelligence API & Command Center

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103.0-009688)
![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success)

An industry-grade, highly precise geospatial command center utilizing a **Hybrid Machine Learning and Geotechnical Physics Engine** to predict landslide probabilities in real-time. Built to ingest live telemetry, compute safety factors, and trigger automated evacuation protocols.

[Key Features](#-key-features) • [Architecture](#-system-architecture) • [Quickstart](#-quick-start-guide) • [API Reference](#-core-api-endpoints)

---

## 🎥 System Demonstration

*Watch the GeoShield Command Center in action:*
<div align="center">
  <video src="frontend/assets/video.mp4" controls="controls" width="100%">
    Your browser does not support the video tag.
  </video>
</div>

## 🖥️ Live Command Dashboard

<div align="center">
  <img src="frontend/assets/dashboard.png" alt="GeoShield Dashboard" width="100%">
  <p><em>Real-time visualization of hybrid risk assessments, telemetry, and safety thresholds.</em></p>
</div>

---

## 🌟 Key Features

| Feature | Description |
| :--- | :--- |
| 🧠 **Hybrid ML & Physics Engine** | Fuses an XGBoost classification model with a Geotechnical Factor of Safety (FoS) equation to guarantee dynamic readings on all terrain types. |
| 📡 **Live Automated Telemetry** | Fetches real-time 3D/7D precipitation from Open-Meteo and deep soil composition data (clay, sand, bulk density) via ISRIC SoilGrids. |
| 🚨 **Automated Telegram Alerts** | Deploys instant, formatted markdown warnings to registered Telegram channels when catastrophic failure probability exceeds safety thresholds. |
| 🗺️ **Evacuation Routing (OSRM)** | Generates instantaneous, safe geospatial escape routes away from high-risk sectors using the OpenSRM routing API. |
| 🛡️ **Fail-Safe Fallbacks** | Intelligent API timeout handling ensures the system degrades gracefully, maintaining realistic baseline calculations without crashing. |

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Raw Geospatial Coordinates] --> B(External APIs: Nominatim, Open-Meteo, SoilGrids)
    B --> C{Data Validation & Fallbacks}
    C --> D[Geotechnical Physics Engine]
    C --> E[XGBoost ML Predictor]
    D --> F{Hybrid Merge Logic}
    E --> F
    F --> G[FastAPI REST Backend]
    G --> H(React/Vite Web Dashboard)
    G --> I(Telegram Alert Dispatcher)
    G --> J(OSRM Evacuation Router)