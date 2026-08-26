<div align="center">

# ⛰️ GeoShield Enterprise
### *AI-Powered Landslide Intelligence & Geotechnical Command Center*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost-159957?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)](https://github.com/helloAi0/landslide-monitoring)

<p align="center">
  An enterprise-grade, highly precise geospatial command center combining <b>Hybrid Machine Learning</b> and a <b>Geotechnical Physics Engine</b> (Limit Equilibrium Method) to forecast real-time landslide risk.
</p>

[🎥 Live Video Demo](#-live-video-demonstration) • [📊 Dashboard](#-command-center-dashboard) • [🌟 Features](#-key-features) • [🏗️ Architecture](#%EF%B8%8F-system-architecture) • [🚀 Quickstart](#-quick-start-guide) • [🔌 API Reference](#-core-api-endpoints)

</div>

---

<h2 align="center">🎥 Live Video Demonstration</h2>

<p align="center">
  <i>Continuous live platform walkthrough demonstrating real-time telemetry processing, slope dynamics, and instantaneous risk computation.</i>
</p>

<div align="center">
  <img src="https://raw.githubusercontent.com/helloAi0/landslide-monitoring/main/frontend/src/assets/video.gif" alt="GeoShield Live Platform Walkthrough" width="100%" />
</div>

<p align="center">
  <sub>🎬 <i>If the GIF does not render immediately, <a href="https://github.com/helloAi0/landslide-monitoring/blob/main/frontend/src/assets/video.mp4">click here to open the raw MP4 video file</a>.</i></sub>
</p>

---

<h2 align="center">📊 Command Center Dashboard</h2>

<p align="center">
  <i>High-resolution geospatial command interface displaying regional hazard radar, safety thresholds, and telemetry analytics.</i>
</p>

<div align="center">
  <img src="https://raw.githubusercontent.com/helloAi0/landslide-monitoring/main/frontend/src/assets/dashboard.png" alt="GeoShield Command Center Dashboard" width="100%" />
</div>

---

<h2 align="center">🌟 Key Features</h2>

<div align="center">

| Feature | Description |
| :--- | :--- |
| 🧠 **Hybrid ML & Physics Engine** | Fuses an XGBoost classification model with a Geotechnical Factor of Safety (FoS) equation to guarantee dynamic readings on all terrain types. |
| 📡 **Live Automated Telemetry** | Fetches real-time 3D/7D precipitation from Open-Meteo and deep soil composition data (clay, sand, bulk density) via ISRIC SoilGrids. |
| 🚨 **Automated Telegram Alerts** | Deploys instant, formatted markdown warnings to registered Telegram channels when catastrophic failure probability exceeds safety thresholds. |
| 🗺️ **Evacuation Routing (OSRM)** | Generates instantaneous, safe geospatial escape routes away from high-risk sectors using the OpenSRM routing API. |
| 🛡️ **Fail-Safe Fallbacks** | Intelligent API timeout handling ensures the system degrades gracefully, maintaining realistic baseline calculations without crashing. |

</div>

---

<h2 align="center">🏗️ System Architecture</h2>

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