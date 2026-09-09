import json
import time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

# Load model dan metadata dari folder models/
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "ev_battery_ops_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

with open(METADATA_PATH, "r") as f:
    METADATA = json.load(f)

MODEL = joblib.load(MODEL_PATH)

ALL_FEATURES = METADATA["all_features"]
ACTIONABLE_FEATURES = METADATA["actionable_features"]
BOUNDS = METADATA["bounds"]
MEDIANS = METADATA["medians"]
CAT_DEFAULTS = METADATA["categorical_defaults"]
CAT_FEATURES = METADATA["categorical_features"]


def build_dataframe(input_data: dict) -> pd.DataFrame:
    """Membangun single-row DataFrame lengkap berdasarkan skema model."""
    row = {}
    for col in ALL_FEATURES:
        if col in input_data and input_data[col] is not None:
            row[col] = input_data[col]
        elif col in CAT_FEATURES:
            row[col] = CAT_DEFAULTS.get(col, "Unknown")
        else:
            row[col] = MEDIANS.get(col, 0.0)

    df_row = pd.DataFrame([row])
    for col in CAT_FEATURES:
        df_row[col] = df_row[col].astype("category")

    return df_row[ALL_FEATURES]


def predict_risk(input_data: dict) -> float:
    """Menghitung probabilitas kegagalan baterai."""
    df_row = build_dataframe(input_data)
    prob = MODEL.predict_proba(df_row)[0, 1]
    return float(prob)


def run_counterfactual_optimization(input_data: dict, steps: int = 10) -> dict:
    """Mencari kombinasi kebiasaan terbaik untuk meredam risiko."""
    start_time = time.perf_counter()
    
    base_df = build_dataframe(input_data)
    initial_risk = float(MODEL.predict_proba(base_df)[0, 1])
    
    best_df = base_df.copy()
    current_values = {col: float(base_df[col].iloc[0]) for col in ACTIONABLE_FEATURES}
    optimized_values = current_values.copy()
    best_risk = initial_risk

    # Grid diskrit untuk 5 fitur actionable
    grids = {
        col: np.linspace(BOUNDS[col][0], BOUNDS[col][1], steps)
        for col in ACTIONABLE_FEATURES
    }

    # Optimasi koordinat 2 putaran (vectorized batch evaluation)
    for _ in range(2):
        for col in ACTIONABLE_FEATURES:
            candidates = grids[col]
            batch = pd.concat([best_df] * len(candidates), ignore_index=True)
            batch[col] = candidates
            
            probs = MODEL.predict_proba(batch)[:, 1]
            min_idx = int(np.argmin(probs))
            
            if probs[min_idx] < best_risk:
                best_risk = float(probs[min_idx])
                optimized_values[col] = float(candidates[min_idx])
                best_df[col] = candidates[min_idx]

    duration_ms = (time.perf_counter() - start_time) * 1000

    # Susun payload rekomendasi perubahan
    recommendations = []
    for col in ACTIONABLE_FEATURES:
        old_val = round(current_values[col], 2)
        new_val = round(optimized_values[col], 2)
        delta = round(new_val - old_val, 2)
        
        if abs(delta) < 0.5:
            action = "Pertahankan"
        elif delta < 0:
            action = f"Turunkan {abs(delta)}"
        else:
            action = f"Naikkan {abs(delta)}"

        recommendations.append({
            "feature": col,
            "current_value": old_val,
            "recommended_value": new_val,
            "delta": delta,
            "action": action
        })

    return {
        "initial_risk": round(initial_risk, 4),
        "optimized_risk": round(best_risk, 4),
        "risk_reduced_percent": round((initial_risk - best_risk) * 100, 2),
        "latency_ms": round(duration_ms, 2),
        "recommendations": recommendations
    }