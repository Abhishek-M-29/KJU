"""
FastAPI version of MedAssist Diabetes Risk Prediction API
Converted from Flask to FastAPI.

Save as diabetes_api.py and run with:
    uvicorn diabetes_api:app --host 0.0.0.0 --port 5003 --reload
"""

from typing import List, Dict, Any, Literal
import os
import logging
import warnings
import joblib
import pickle
import numpy as np
import shap

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# Suppress warnings
warnings.filterwarnings("ignore")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MedAssist Diabetes Prediction API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
diabetes_model = None
diabetes_encoders = None
diabetes_features = None
diabetes_explainer = None


def load_diabetes_model():
    """Load diabetes model, encoders, and create SHAP explainer"""
    global diabetes_model, diabetes_encoders, diabetes_features, diabetes_explainer

    try:
        diabetes_model = joblib.load("diabetes_xgboost_model.pkl")
        with open("diabetes_label_encoders.pkl", "rb") as f:
            diabetes_encoders = pickle.load(f)
        with open("diabetes_feature_info.pkl", "rb") as f:
            diabetes_features = pickle.load(f)

        diabetes_explainer = shap.TreeExplainer(diabetes_model)
        logger.info("Model, encoders, and SHAP explainer loaded")
    except Exception as e:
        logger.exception("Failed to load model or artifacts")
        raise e


# Utility functions (copied/adapted from original)
def get_risk_category(probability: float) -> str:
    if probability < 0.3:
        return "Low"
    elif probability < 0.7:
        return "Medium"
    else:
        return "High"


def format_shap_explanation(shap_values: np.ndarray, feature_names: List[str],
                            feature_values: np.ndarray) -> Dict[str, Any]:
    explanations = []

    if len(shap_values.shape) == 2:
        shap_vals = shap_values[0]
    else:
        shap_vals = shap_values

    for i, (feature, shap_val, feature_val) in enumerate(zip(feature_names, shap_vals, feature_values[0])):
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


def generate_explanation_summary(top_explanations: List[Dict]) -> str:
    if not top_explanations:
        return "Unable to generate explanation summary."
    summary_parts = []
    for exp in top_explanations:
        feature = exp["feature"].replace("_", " ").title()
        impact = exp["impact"]
        value = exp["value"]
        summary_parts.append(f"{feature} (value: {value:.2f}) {impact} the risk")
    return f"The prediction is primarily influenced by: {', '.join(summary_parts)}."


def get_bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def get_hba1c_category(hba1c: float) -> str:
    if hba1c < 5.7:
        return "Normal"
    elif hba1c < 6.5:
        return "Prediabetes"
    else:
        return "Diabetes"


def get_glucose_category(glucose: int) -> str:
    if glucose < 100:
        return "Normal"
    elif glucose < 126:
        return "Prediabetes"
    else:
        return "Diabetes"


def get_diabetes_recommendations(risk_category: str, top_factors: List[Dict]) -> List[str]:
    recommendations = []
    if risk_category == "High":
        recommendations.extend([
            "Consult with an endocrinologist or diabetes specialist immediately",
            "Consider comprehensive diabetes screening and monitoring"
        ])
    elif risk_category == "Medium":
        recommendations.extend([
            "Schedule regular glucose monitoring and healthcare check-ups",
            "Implement diabetes prevention strategies"
        ])
    else:
        recommendations.extend([
            "Maintain current healthy lifestyle",
            "Continue regular health screenings"
        ])

    for factor in top_factors[:3]:
        feature = factor["feature"]
        if feature == "HbA1c_level" and factor["impact"] == "increases":
            recommendations.append("Focus on blood sugar control through diet and lifestyle modifications")
        elif feature == "blood_glucose_level" and factor["impact"] == "increases":
            recommendations.append("Monitor blood glucose levels regularly and maintain healthy diet")
        elif feature == "bmi" and factor["impact"] == "increases":
            recommendations.append("Weight management through balanced diet and regular exercise")
        elif feature == "age" and factor["impact"] == "increases":
            recommendations.append("Regular health screenings become more important with age")

    return recommendations


# Pydantic request model
class PredictRequest(BaseModel):
    age: float = Field(..., ge=0)
    gender: Literal["Female", "Male", "Other"]
    hypertension: int = Field(..., ge=0, le=1)
    heart_disease: int = Field(..., ge=0, le=1)
    smoking_history: Literal["never", "No Info", "current", "former", "ever", "not current"]
    bmi: float = Field(..., ge=0)
    HbA1c_level: float = Field(..., ge=0)
    blood_glucose_level: int = Field(..., ge=0)


@app.on_event("startup")
def startup_event():
    try:
        load_diabetes_model()
    except Exception as e:
        logger.error("Startup failed: %s", e)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "MedAssist Diabetes Prediction API is running",
        "model_loaded": diabetes_model is not None
    }


@app.post("/predict")
def predict_diabetes(req: PredictRequest):
    if diabetes_model is None or diabetes_encoders is None or diabetes_features is None or diabetes_explainer is None:
        raise HTTPException(status_code=503, detail="Model or artifacts not loaded")

    # Encode categorical variables
    try:
        gender_encoded = diabetes_encoders["gender_encoder"].transform([req.gender])[0]
        smoking_encoded = diabetes_encoders["smoking_encoder"].transform([req.smoking_history])[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid categorical value: {e}")

    features = np.array([[
        req.age,
        req.hypertension,
        req.heart_disease,
        req.bmi,
        req.HbA1c_level,
        req.blood_glucose_level,
        gender_encoded,
        smoking_encoded
    ]])

    feature_names = diabetes_features.get("feature_names", []) if diabetes_features else []

    try:
        prediction = int(diabetes_model.predict(features)[0])
        prediction_proba = diabetes_model.predict_proba(features)[0]
        confidence = float(np.max(prediction_proba))
        risk_probability = float(prediction_proba[1]) if prediction_proba.shape[0] > 1 else float(prediction_proba[0])
        shap_values = diabetes_explainer.shap_values(features)
        explanations = format_shap_explanation(shap_values, feature_names, features)
        risk_category = get_risk_category(risk_probability)

        result = {
            "prediction": prediction,
            "risk_probability": risk_probability,
            "confidence_score": confidence,
            "risk_category": risk_category,
            "input_data": {
                "age": req.age,
                "gender": req.gender,
                "bmi": req.bmi,
                "bmi_category": get_bmi_category(req.bmi),
                "hypertension": bool(req.hypertension),
                "heart_disease": bool(req.heart_disease),
                "smoking_history": req.smoking_history,
                "HbA1c_level": req.HbA1c_level,
                "HbA1c_category": get_hba1c_category(req.HbA1c_level),
                "blood_glucose_level": req.blood_glucose_level,
                "glucose_category": get_glucose_category(req.blood_glucose_level)
            },
            "explanations": explanations,
            "interpretation": {
                "result": "High risk of diabetes" if prediction == 1 else "Low risk of diabetes",
                "recommendation": get_diabetes_recommendations(risk_category, explanations["top_factors"])
            }
        }
        return result
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


@app.get("/model/info")
def model_info():
    return {
        "model_info": {
            "loaded": diabetes_model is not None,
            "type": "XGBoost Classifier",
            "purpose": "Diabetes Risk Prediction",
            "features": diabetes_features.get("feature_names", []) if diabetes_features else []
        },
        "shap_explanations": "Available" if diabetes_explainer is not None else "Unavailable"
    }


if __name__ == "__main__":
    import uvicorn
<<<<<<< HEAD
    import socket
    
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip+":5003"
    
=======
>>>>>>> 66c408930077dcde7f6655ff57244aafa2ff1785
    # ensure model loads when run directly
    try:
        load_diabetes_model()
    except Exception as e:
        logger.error("Failed to load model on direct run: %s", e)
<<<<<<< HEAD
    
    local_ip = get_local_ip()
    print(f"Server running on network IP: {local_ip}")
=======
>>>>>>> 66c408930077dcde7f6655ff57244aafa2ff1785
    uvicorn.run("diabetes_api:app", host="0.0.0.0", port=5003, reload=True)
