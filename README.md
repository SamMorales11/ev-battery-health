<img width="736" height="414" alt="Chasing Black Mass_ Inside the Electric Vehicle Battery Recycling Process" src="https://github.com/user-attachments/assets/0c9e9cb9-4b2b-48d0-96fc-09cfc212b294" />

# VoltIQ Telemetry ⚡
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82?logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LightGBM](https://img.shields.io/badge/Model-LightGBM-brightgreen?logo=scikitlearn&logoColor=white)](https://lightgbm.readthedocs.io/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.x-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Predictive EV Battery Degradation & Telemetry Intelligence
VoltIQ is a machine-learning-powered battery telemetry simulator designed to analyze electric vehicle (EV) driver habits, predict electrochemical cell degradation risk, and provide actionable counterfactual optimization to extend battery pack lifespan.

## Key Features
- Interactive Behavioral Telemetry Controls: 5 actionable driver inputs (Depth of Discharge, Target State of Charge, DC Fast Charge Share, Hard Braking Intensity, and Cruising Speed) equipped with an adaptive risk heatmap that dynamically alters track and thumb glows based on stress thresholds.
- LightGBM Inference Engine: Sub-15ms electrochemical stress and failure risk index computation served via a high-performance FastAPI asynchronous backend.
- Real-World Lifespan & Mileage Projections: Translates abstract failure risk percentages into concrete vehicle metrics (estimated pack lifespan in years before reaching 70% State of Health / SOH threshold and cumulative operational mileage).
- Counterfactual Optimization Engine: Coordinate search recommendation algorithm that identifies minimal habit changes necessary to transition from high-risk degradation to optimal cell preservation.
- SVG Radar Parameter Comparison: Native responsive polygon radar chart comparing baseline driver telemetry against recommended parameters.
- Reactive Bento Architecture Card: Simulates battery hardware telemetry including real-time thermal operating windows, dynamic energy consumption (kWh/100km), and Battery Management System (BMS) mitigation states.
- Behavior Presets: Instant scenario switching between Eco-Safe, Commuter, and Abusive driving profiles.

## System Architecture
```bash
┌────────────────────────────────────────────────────────┐
│             Nuxt 3 Client (Vue 3 + Tailwind)           │
│  - HabitControls (Adaptive Range Sliders)              │
│  - RiskGauge (Animated Number Ticker + Lifespan)       │
│  - OptimizationResult (Native SVG Radar Chart)         │
│  - BatterySpecs (Dynamic Thermal & Power Bento Grid)   │
└───────────────────────────▲────────────────────────────┘
                            │ JSON over HTTP (REST API)
┌───────────────────────────▼────────────────────────────┐
│               FastAPI ML Inference Service             │
│  - /api/predict   -> LightGBM Risk Scoring Model       │
│  - /api/optimize  -> Coordinate Search Optimization    │
└────────────────────────────────────────────────────────┘
```

## Project Structure
```bash
ev-battery-health/
├── service-ml/
│   ├── main.py                  # FastAPI server & inference endpoints
│   ├── model.joblib             # Trained LightGBM battery risk model
│   ├── requirements.txt         # Python dependencies
│   └── README.md
│
├── web-nuxt/
│   ├── app/
│   │   ├── components/
│   │   │   ├── BatterySpecs.vue         # Hardware specs & thermal telemetry
│   │   │   ├── DashboardHeader.vue      # Branding, presets & optimize trigger
│   │   │   ├── HabitControls.vue        # 5-slider adaptive heatmap controls
│   │   │   ├── OptimizationResult.vue   # Counterfactual results & radar chart
│   │   │   └── RiskGauge.vue            # Risk index, ticker & lifespan projection
│   │   └── app.vue                      # Orchestrator & state management
│   ├── nuxt.config.ts           # Nuxt configuration & runtime env
│   ├── package.json             # Frontend dependencies
│   └── tailwind.config.ts       # Design tokens & color palettes
│
└── README.md
```

## Machine Learning & Degradation Formulation
- VoltIQ models battery capacity loss and stress acceleration driven by the primary mechanisms of lithium-ion (NMC 811) degradation:
- Cycle Aging (DoD & SoC Stress): Elevated average State of Charge (SoC > 80%) promotes electrolyte oxidation and transition metal dissolution, while deep Depth of Discharge (DoD > 80%) accelerates mechanical stress on anode particles.
- Kinetic & Thermal Degradation (Fast Charge & Cruising Speed): High DC fast charge ratios (> 0.50) induce localized lithium plating during high-rate intercalation, driving irreversible cell capacity loss.
- Regenerative Current Surges (Hard Braking): Severe deceleration events generate sudden, high-C-rate regenerative current spikes into the BMS.

## ⚡ Quick Start & Local Setup 
Prerequisites
- Node.js: v18.x or higher
- Python: v3.10 or higher
- Package Managers: npm / pnpm & pip

## 1. Backend Service (service-ml)
```bash
# Navigate to the backend directory
cd service-ml

# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Start the FastAPI development server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- The ML service will be accessible at http://127.0.0.1:8000.
- Interactive API docs are available at http://127.0.0.1:8000/docs.

## 2. Frontend Client (web-nuxt)
```bash
# Navigate to the frontend directory
cd web-nuxt

# Install dependencies
npm install

# Run the Nuxt development server
npm run dev
```
- Open http://localhost:3000 in your browser.

## 📡 API Specification
1. Predict Risk Index
- Endpoint: POST /api/predict
- Description: Calculates failure probability based on operational parameters.
Request Payload:
```bash
{
  "depth_of_discharge": 70.0,
  "state_of_charge": 90.0,
  "fast_charge_ratio": 0.55,
  "hard_braking_score": 65.0,
  "average_speed": 85.0
}
```
- Response:
```bash
{
  "risk_percentage": 1.07,
  "risk_level": "HEALTHY",
  "confidence": 0.989
}
```

2. Counterfactual Habit Optimization
- Endpoint: POST /api/optimize
- Description: Computes minimal feature deltas to achieve the lowest safe risk state.
Response:
```bash
{
  "optimized_risk": 0.0035,
  "risk_reduced_percent": 67.2,
  "latency_ms": 12,
  "recommendations": [
    {
      "feature": "depth_of_discharge",
      "current_value": 70,
      "recommended_value": 30,
      "delta": -40,
      "action": "Turunkan 40.0"
    },
    {
      "feature": "fast_charge_ratio",
      "current_value": 0.55,
      "recommended_value": 0.05,
      "delta": -0.5,
      "action": "Turunkan 0.5"
    }
  ]
}
```

## 🧪 Environmental Variables
```bash
NUXT_PUBLIC_API_BASE_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)
```

## 📄 License
Distributed under the MIT License. See LICENSE for more information.
