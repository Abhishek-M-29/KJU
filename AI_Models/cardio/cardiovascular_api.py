"""
MedAssist Cardiovascular Disease Prediction API - FastAPI version
Converted from Flask to FastAPI
"""

import os
import logging
import warnings
from typing import List, Dict, Any

import joblib
import numpy as np
import shap
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MedAssist Cardiovascular Prediction API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
cardio_model = None
cardio_explainer = None


class CardioInput(BaseModel):
    age: float = Field(..., description="Age in days (or years if <=150)")
    gender: int
    height: float
    weight: float
    ap_hi: int
    ap_lo: int
    cholesterol: int
    gluc: int
    smoke: int
    alco: int
    active: int


<<<<<<< HEAD
def load_cardio_model(model_path: str = fr"C:\Users\Noodl\Projects\Big_O\Hackathon\Chanakya\MediMax\AI_Models\cardio\xgboost_model.pkl"):
=======
def load_cardio_model(model_path: str = "xgboost_model.pkl"):
>>>>>>> 66c408930077dcde7f6655ff57244aafa2ff1785
    global cardio_model, cardio_explainer
    try:
        cardio_model = joblib.load(model_path)
        logger.info("Cardiovascular model loaded.")
        cardio_explainer = shap.TreeExplainer(cardio_model)
        logger.info("SHAP explainer created.")
    except Exception as e:
        logger.exception("Failed to load model/explainer.")
        raise e


def get_risk_category(probability: float) -> str:
    if probability < 0.3:
        return "Low"
    if probability < 0.7:
        return "Medium"
    return "High"


def generate_explanation_summary(top_explanations: List[Dict]) -> str:
    if not top_explanations:
        return "Unable to generate explanation summary."
    parts = []
    for exp in top_explanations:
        feature = exp["feature"].replace("_", " ").title()
        impact = exp["impact"]
        value = exp["value"]
        parts.append(f"{feature} (value: {value:.2f}) {impact} the risk")
    return f"The prediction is primarily influenced by: {', '.join(parts)}."


def normalize_shap_values(shap_values):
    # SHAP can return a list (per-class) or an array. Choose the positive-class SHAP if list.
    if isinstance(shap_values, list):
        if len(shap_values) > 1:
            return np.array(shap_values[1])
        return np.array(shap_values[0])
    return np.array(shap_values)


def format_shap_explanation(shap_values: Any, feature_names: List[str], feature_values: np.ndarray) -> Dict[str, Any]:
    explanations = []
    shap_vals = normalize_shap_values(shap_values)

    # If shap_vals has shape (n_samples, n_features), take first sample
    if shap_vals.ndim == 2:
        shap_sample = shap_vals[0]
    else:
        shap_sample = shap_vals

    values_sample = feature_values[0]

    for feature, shap_val, feature_val in zip(feature_names, shap_sample, values_sample):
        impact = "increases" if shap_val > 0 else "decreases"
        explanations.append({
            "feature": feature,
            "value": float(feature_val),
            "shap_value": float(shap_val),
            "impact": impact,
            "importance": abs(float(shap_val))
        })

    explanations.sort(key=lambda x: x["importance"], reverse=True)
    top = explanations[:5]
    return {
        "explanations": explanations,
        "top_factors": top,
        "summary": generate_explanation_summary(explanations[:3])
    }


def get_cardio_recommendations(risk_category: str, top_factors: List[Dict]) -> List[str]:
    recommendations = []
    if risk_category == "High":
        recommendations += [
            "Consult with a cardiologist immediately for comprehensive evaluation",
            "Consider immediate lifestyle modifications including diet and exercise",
        ]
    elif risk_category == "Medium":
        recommendations += [
            "Schedule regular check-ups with your healthcare provider",
            "Implement preventive lifestyle changes",
        ]
    else:
        recommendations += [
            "Maintain current healthy lifestyle",
            "Continue regular health screenings",
        ]

    for factor in top_factors[:3]:
        feature = factor["feature"]
        if feature == "ap_hi" and factor["impact"] == "increases":
            recommendations.append("Monitor and manage blood pressure through diet, exercise, and medication if needed")
        elif feature == "cholesterol" and factor["impact"] == "increases":
            recommendations.append("Consider cholesterol management through diet and possible medication")
        elif feature == "smoke" and factor["impact"] == "increases":
            recommendations.append("Smoking cessation is highly recommended")
        elif feature == "active" and factor["impact"] == "decreases":
            recommendations.append("Increase physical activity and exercise regularly")

    return recommendations


@app.on_event("startup")
def startup_event():
    try:
        load_cardio_model()
    except Exception as e:
        logger.error("Startup failed to load model: %s", e)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "MedAssist Cardiovascular Prediction API is running",
        "model_loaded": cardio_model is not None
    }


@app.get("/model/info")
def model_info():
    return {
        "model_info": {
            "loaded": cardio_model is not None,
            "type": "XGBoost Classifier",
            "purpose": "Cardiovascular Disease Prediction",
            "features": ["age", "gender", "height", "weight", "ap_hi", "ap_lo",
                         "cholesterol", "gluc", "smoke", "alco", "active"]
        },
        "shap_explanations": "Available" if cardio_explainer is not None else "Unavailable"
    }


@app.post("/predict")
def predict_cardio(payload: CardioInput):
    if cardio_model is None or cardio_explainer is None:
        raise HTTPException(status_code=503, detail="Model or explainer not loaded")

    data = payload.dict()
    try:
        age_years = data["age"] / 365.25 if data["age"] > 150 else data["age"]
        height_m = data["height"] / 100.0
        bmi = data["weight"] / (height_m ** 2)

        features = np.array([[
            age_years,
            data["gender"],
            data["height"],
            data["weight"],
            data["ap_hi"],
            data["ap_lo"],
            data["cholesterol"],
            data["gluc"],
            data["smoke"],
            data["alco"],
            data["active"],
        ]])

        feature_names = ["age", "gender", "height", "weight", "ap_hi", "ap_lo",
                         "cholesterol", "gluc", "smoke", "alco", "active"]

        prediction = int(cardio_model.predict(features)[0])
        proba = cardio_model.predict_proba(features)[0]
        confidence = float(max(proba))
        risk_probability = float(proba[1]) if len(proba) > 1 else float(proba[0])

        shap_values = cardio_explainer.shap_values(features)
        explanations = format_shap_explanation(shap_values, feature_names, features)
        risk_category = get_risk_category(risk_probability)

        result = {
            "prediction": prediction,
            "risk_probability": risk_probability,
            "confidence_score": confidence,
            "risk_category": risk_category,
            "input_data": {
                "age_years": round(age_years, 1),
                "bmi": round(bmi, 2),
                "gender": "Female" if data["gender"] == 1 else "Male",
                "systolic_bp": data["ap_hi"],
                "diastolic_bp": data["ap_lo"],
                "cholesterol_level": data["cholesterol"],
                "glucose_level": data["gluc"],
                "smoking": bool(data["smoke"]),
                "alcohol": bool(data["alco"]),
                "physical_activity": bool(data["active"]),
            },
            "explanations": explanations,
            "interpretation": {
                "result": "High risk of cardiovascular disease" if prediction == 1 else "Low risk of cardiovascular disease",
                "recommendation": get_cardio_recommendations(risk_category, explanations["top_factors"])
            }
        }
        return result

    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


if __name__ == "__main__":
    # Run with: python cardiovascular_api_fastapi.py
    import uvicorn
<<<<<<< HEAD
    import socket

    # Get the local network IP address
    host = socket.gethostbyname(socket.gethostname())
    uvicorn.run(app, host=host, port=5002, log_level="info")
=======
    uvicorn.run(app, host="0.0.0.0", port=5002, log_level="info")
>>>>>>> 66c408930077dcde7f6655ff57244aafa2ff1785
