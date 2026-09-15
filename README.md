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
