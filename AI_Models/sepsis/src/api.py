"""
FastAPI endpoint for Sepsis Prediction Model.
Best Model: MyRF (Random Forest) - Highest Recall for clinical safety.

Run with:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import joblib
import numpy as np
from pathlib import Path
from typing import List
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ============================================================
# Configuration
# ============================================================
MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_NAME = "MyRF"
MODEL_PATH = MODEL_DIR / f"{MODEL_NAME}.pkl"

FEATURE_NAMES = [
    "heartrate", "sysbp", "diasbp", "meanbp", "resprate",
    "tempc", "spo2", "glucose", "age", "gender"
]

# ============================================================
# Load Model
# ============================================================
try:
    model = joblib.load(MODEL_PATH)
    MODEL_LOADED = True
    print(f"✅ Model loaded: {MODEL_PATH}")
except Exception as e:
    print(f"⚠️ Could not load model: {e}")
    model = None
    MODEL_LOADED = False

# ============================================================
# Pydantic Models
# ============================================================
class Observation(BaseModel):
    """Single observation of patient vitals."""
    heartrate: float = Field(..., ge=0, le=300, description="Heart rate (bpm)")
    sysbp: float = Field(..., ge=0, le=300, description="Systolic BP (mmHg)")
    diasbp: float = Field(..., ge=0, le=200, description="Diastolic BP (mmHg)")
    meanbp: float = Field(..., ge=0, le=250, description="Mean BP (mmHg)")
    resprate: float = Field(..., ge=0, le=100, description="Respiratory rate")
    tempc: float = Field(..., ge=30, le=45, description="Temperature (°C)")
    spo2: float = Field(..., ge=0, le=100, description="SpO2 (%)")
    glucose: float = Field(..., ge=0, le=1000, description="Glucose (mg/dL)")
    age: float = Field(..., ge=0, le=150, description="Age (years)")
    gender: int = Field(..., ge=0, le=1, description="Gender (0=F, 1=M)")


class PredictionRequest(BaseModel):
    """Request body for prediction."""
    patient_id: str = Field(..., description="Patient identifier")
    observations: List[Observation] = Field(..., min_length=1)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "P001",
                "observations": [{
                    "heartrate": 95, "sysbp": 110, "diasbp": 70, "meanbp": 83,
                    "resprate": 24, "tempc": 38.5, "spo2": 94, "glucose": 140,
                    "age": 72, "gender": 1
                }]
            }
        }
    }


class PredictionResponse(BaseModel):
    """Response body for prediction."""
    patient_id: str
    prediction: int = Field(..., description="0=No Sepsis, 1=Sepsis")
    probability: float
    risk_level: str
    interpretation: str
    timestamp: str
    model_used: str


class BatchRequest(BaseModel):
    """Batch prediction request."""
    patients: List[PredictionRequest]


class ModelInfo(BaseModel):
    """Model metadata."""
    name: str
    version: str
    features: List[str]
    metrics: dict
    loaded: bool


# ============================================================
# Helper Functions
# ============================================================
def construct_features(observations: List[Observation]) -> np.ndarray:
    """Convert observations to feature vector (mean aggregation)."""
    arr = np.array([
        [obs.heartrate, obs.sysbp, obs.diasbp, obs.meanbp, obs.resprate,
         obs.tempc, obs.spo2, obs.glucose, obs.age, obs.gender]
        for obs in observations
    ])
    return np.nanmean(arr, axis=0).reshape(1, -1)


def get_risk_level(probability: float) -> tuple[str, str]:
    """Determine risk level and interpretation."""
    if probability < 0.3:
        return "LOW", "Low risk of sepsis. Continue routine monitoring."
    elif probability < 0.6:
        return "MODERATE", "Moderate risk. Consider increased monitoring and labs."
    else:
        return "HIGH", "High risk of sepsis. Immediate clinical evaluation recommended."


# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(
    title="Sepsis Prediction API",
    description="ML-powered sepsis risk prediction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Endpoints
# ============================================================
@app.get("/", tags=["Health"])
async def root():
    """Health check."""
    return {
        "status": "healthy",
        "service": "Sepsis Prediction API",
        "model_loaded": MODEL_LOADED,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
async def get_model_info():
    """Get model metadata."""
    return ModelInfo(
        name=MODEL_NAME,
        version="1.0.0",
        features=FEATURE_NAMES,
        metrics={
            "test_roc_auc": 0.7518,
            "test_recall": 0.7182,
            "test_precision": 0.6870,
            "test_f1": 0.7022,
            "test_accuracy": 0.7009
        },
        loaded=MODEL_LOADED
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(request: PredictionRequest):
    """Predict sepsis risk for a patient."""
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        features = construct_features(request.observations)
        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
        risk_level, interpretation = get_risk_level(probability)
        
        return PredictionResponse(
            patient_id=request.patient_id,
            prediction=prediction,
            probability=round(probability, 4),
            risk_level=risk_level,
            interpretation=interpretation,
            timestamp=datetime.now().isoformat(),
            model_used=MODEL_NAME
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(request: BatchRequest):
    """Batch prediction for multiple patients."""
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results = []
    for patient in request.patients:
        try:
            features = construct_features(patient.observations)
            prediction = int(model.predict(features)[0])
            probability = float(model.predict_proba(features)[0][1])
            risk_level, _ = get_risk_level(probability)
            
            results.append({
                "patient_id": patient.patient_id,
                "prediction": prediction,
                "probability": round(probability, 4),
                "risk_level": risk_level
            })
        except Exception as e:
            results.append({"patient_id": patient.patient_id, "error": str(e)})
    
    return {
        "timestamp": datetime.now().isoformat(),
        "model_used": MODEL_NAME,
        "total": len(request.patients),
        "predictions": results
    }


# ============================================================
# Run with: uvicorn api:app --host 0.0.0.0 --port 8000 --reload
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
