from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from optimizer import (
    METADATA,
    predict_risk,
    run_counterfactual_optimization,
)

app = FastAPI(
    title="EV Battery Health Simulator API",
    description="Microservice ML untuk prediksi kegagalan baterai EV dan optimasi kebiasaan pengemudi.",
    version="1.0.0"
)

# Izinkan request dari Nuxt frontend (default Nuxt: localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TelemetryPayload(BaseModel):
    # 5 Fitur Actionable Utama
    depth_of_discharge: Optional[float] = Field(None, example=68.0)
    state_of_charge: Optional[float] = Field(None, example=85.0)
    fast_charge_ratio: Optional[float] = Field(None, example=0.45)
    hard_braking_score: Optional[float] = Field(None, example=65.0)
    average_speed: Optional[float] = Field(None, example=82.0)
    
    # Payload fleksibel untuk fitur telemetri tambahan
    additional_features: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def to_flat_dict(self) -> dict:
        data = {
            "depth_of_discharge": self.depth_of_discharge,
            "state_of_charge": self.state_of_charge,
            "fast_charge_ratio": self.fast_charge_ratio,
            "hard_braking_score": self.hard_braking_score,
            "average_speed": self.average_speed,
        }
        if self.additional_features:
            data.update(self.additional_features)
        return data


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ev-battery-ml-api"}


@app.get("/api/metadata")
def get_metadata():
    """Mengirimkan metadata bounds dan default ke frontend Nuxt."""
    return {
        "actionable_features": METADATA["actionable_features"],
        "bounds": METADATA["bounds"],
        "defaults": {
            col: METADATA["medians"].get(col, 50.0) 
            for col in METADATA["actionable_features"]
        }
    }


@app.post("/api/predict")
def predict(telemetry: TelemetryPayload):
    try:
        data_dict = telemetry.to_flat_dict()
        risk = predict_risk(data_dict)
        return {
            "risk_probability": round(risk, 4),
            "risk_percentage": round(risk * 100, 2),
            "risk_level": "CRITICAL" if risk >= 0.65 else ("WARNING" if risk >= 0.35 else "HEALTHY")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize")
def optimize(telemetry: TelemetryPayload):
    try:
        data_dict = telemetry.to_flat_dict()
        result = run_counterfactual_optimization(data_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))