<img width="736" height="414" alt="Chasing Black Mass_ Inside the Electric Vehicle Battery Recycling Process" src="https://github.com/user-attachments/assets/0c9e9cb9-4b2b-48d0-96fc-09cfc212b294" />

# VoltIQ Telemetry ⚡
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
