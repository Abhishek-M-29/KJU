"""
Main Swarm Router - Central Hub for AI Model Routing

This module acts as a gatekeeper that routes incoming patient data to the 
appropriate AI model based on strict feature-based validation.

Routing Priority:
    1. Cardiovascular Model (if all 11 required features are present)
    2. Diabetes Model (if all 8 required features are present)
    3. Error if no model requirements are fully met

Strict Policies:
    - NO data imputation, generation, or filling of missing values
    - NO calls to models unless 100% of requirements are satisfied
    - Individual SHAP explainability per model
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import joblib
import pickle
import shap

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Enumeration of available AI models."""
    CARDIOVASCULAR = "cardiovascular"
    DIABETES = "diabetes"


@dataclass
class ModelRequirements:
    """Defines the strict requirements schema for each model."""
    model_type: ModelType
    required_features: List[str]
    feature_types: Dict[str, type]
    categorical_values: Dict[str, List[Any]] = field(default_factory=dict)
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate if input data meets 100% of model requirements.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Tuple of (is_valid, list_of_missing_or_invalid_features)
        """
        missing_features = []
        invalid_features = []
        
        for feature in self.required_features:
            # Check if feature exists and is not None
            if feature not in data or data[feature] is None:
                missing_features.append(feature)
                continue
            
            value = data[feature]
            
            # Check type compatibility
            expected_type = self.feature_types.get(feature)
            if expected_type:
                # Allow numeric type flexibility (int can be float and vice versa)
                if expected_type in (int, float) and isinstance(value, (int, float)):
                    pass
                elif expected_type == str and isinstance(value, str):
                    pass
                elif not isinstance(value, expected_type):
                    invalid_features.append(f"{feature} (expected {expected_type.__name__}, got {type(value).__name__})")
                    continue
            
            # Check categorical constraints
            if feature in self.categorical_values:
                valid_values = self.categorical_values[feature]
                if value not in valid_values:
                    invalid_features.append(f"{feature} (value '{value}' not in {valid_values})")
        
        all_issues = missing_features + invalid_features
        is_valid = len(all_issues) == 0
        
        return is_valid, all_issues


# Define strict requirements for Cardiovascular Model
CARDIOVASCULAR_REQUIREMENTS = ModelRequirements(
    model_type=ModelType.CARDIOVASCULAR,
    required_features=[
        "age", "gender", "height", "weight", 
        "ap_hi", "ap_lo", "cholesterol", "gluc", 
        "smoke", "alco", "active"
    ],
    feature_types={
        "age": float,       # Age in years or days
        "gender": str,      # "Female" or "Male"
        "height": float,    # Height in cm
        "weight": float,    # Weight in kg
        "ap_hi": int,       # Systolic BP
        "ap_lo": int,       # Diastolic BP
        "cholesterol": int, # 1, 2, or 3
        "gluc": int,        # 1, 2, or 3
        "smoke": int,       # 0 or 1
        "alco": int,        # 0 or 1
        "active": int       # 0 or 1
    },
    categorical_values={
        "gender": ["Female", "Male"],
        "cholesterol": [1, 2, 3],
        "gluc": [1, 2, 3],
        "smoke": [0, 1],
        "alco": [0, 1],
        "active": [0, 1]
    }
)


# Define strict requirements for Diabetes Model
DIABETES_REQUIREMENTS = ModelRequirements(
    model_type=ModelType.DIABETES,
    required_features=[
        "age", "gender", "hypertension", "heart_disease",
        "smoking_history", "bmi", "HbA1c_level", "blood_glucose_level"
    ],
    feature_types={
        "age": float,
        "gender": str,              # "Female", "Male", "Other"
        "hypertension": int,        # 0 or 1
        "heart_disease": int,       # 0 or 1
        "smoking_history": str,     # Categorical
        "bmi": float,
        "HbA1c_level": float,
        "blood_glucose_level": int
    },
    categorical_values={
        "gender": ["Female", "Male", "Other"],
        "hypertension": [0, 1],
        "heart_disease": [0, 1],
        "smoking_history": ["never", "No Info", "current", "former", "ever", "not current"]
    }
)


class MainSwarmRouter:
    """
    Central hub router for AI model prediction requests.
    
    This router implements strict feature-based routing with:
    - Priority-based If-Elif-Else model selection
    - Zero tolerance for missing data (no imputation)
    - Individual SHAP explainability per model
    """
    
    def __init__(self, 
                 cardio_model_path: Optional[str] = None,
                 diabetes_model_path: Optional[str] = None,
                 diabetes_encoders_path: Optional[str] = None,
                 diabetes_features_path: Optional[str] = None):
        """
        Initialize the Main Swarm Router.
        
        Args:
            cardio_model_path: Path to cardiovascular XGBoost model
            diabetes_model_path: Path to diabetes XGBoost model
            diabetes_encoders_path: Path to diabetes label encoders
            diabetes_features_path: Path to diabetes feature info
        """
        self.models: Dict[ModelType, Any] = {}
        self.explainers: Dict[ModelType, Any] = {}
        self.encoders: Dict[str, Any] = {}
        self.feature_info: Dict[str, Any] = {}
        
        # Set default paths relative to module location
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.cardio_model_path = cardio_model_path or os.path.join(
            base_path, "cardio", "xgboost_model.pkl"
        )
        self.diabetes_model_path = diabetes_model_path or os.path.join(
            base_path, "diabetes", "diabetes_xgboost_model.pkl"
        )
        self.diabetes_encoders_path = diabetes_encoders_path or os.path.join(
            base_path, "diabetes", "diabetes_label_encoders.pkl"
        )
        self.diabetes_features_path = diabetes_features_path or os.path.join(
            base_path, "diabetes", "diabetes_feature_info.pkl"
        )
        
        # Load models
        self._load_models()
    
    def _load_models(self) -> None:
        """Load all available models and their SHAP explainers."""
        # Load Cardiovascular Model
        try:
            if os.path.exists(self.cardio_model_path):
                self.models[ModelType.CARDIOVASCULAR] = joblib.load(self.cardio_model_path)
                self.explainers[ModelType.CARDIOVASCULAR] = shap.TreeExplainer(
                    self.models[ModelType.CARDIOVASCULAR]
                )
                logger.info("Cardiovascular model and SHAP explainer loaded successfully")
            else:
                logger.warning(f"Cardiovascular model not found at: {self.cardio_model_path}")
        except Exception as e:
            logger.error(f"Failed to load cardiovascular model: {e}")
        
        # Load Diabetes Model
        try:
            if os.path.exists(self.diabetes_model_path):
                self.models[ModelType.DIABETES] = joblib.load(self.diabetes_model_path)
                self.explainers[ModelType.DIABETES] = shap.TreeExplainer(
                    self.models[ModelType.DIABETES]
                )
                logger.info("Diabetes model and SHAP explainer loaded successfully")
                
                # Load encoders and feature info
                if os.path.exists(self.diabetes_encoders_path):
                    with open(self.diabetes_encoders_path, "rb") as f:
                        self.encoders["diabetes"] = pickle.load(f)
                    logger.info("Diabetes encoders loaded successfully")
                
                if os.path.exists(self.diabetes_features_path):
                    with open(self.diabetes_features_path, "rb") as f:
                        self.feature_info["diabetes"] = pickle.load(f)
                    logger.info("Diabetes feature info loaded successfully")
            else:
                logger.warning(f"Diabetes model not found at: {self.diabetes_model_path}")
        except Exception as e:
            logger.error(f"Failed to load diabetes model: {e}")
    
    def _get_risk_category(self, probability: float) -> str:
        """Categorize risk based on probability threshold."""
        if probability < 0.3:
            return "Low"
        elif probability < 0.7:
            return "Medium"
        return "High"
    
    def _normalize_shap_values(self, shap_values) -> np.ndarray:
        """Normalize SHAP values to consistent format."""
        if isinstance(shap_values, list):
            if len(shap_values) > 1:
                return np.array(shap_values[1])
            return np.array(shap_values[0])
        return np.array(shap_values)
    
    def _format_shap_explanation(self, 
                                  shap_values: Any, 
                                  feature_names: List[str], 
                                  feature_values: np.ndarray) -> Dict[str, Any]:
        """Format SHAP values into human-readable explanations."""
        explanations = []
        shap_vals = self._normalize_shap_values(shap_values)
        
        if shap_vals.ndim == 2:
            shap_sample = shap_vals[0]
        else:
            shap_sample = shap_vals
        
        values_sample = feature_values[0] if feature_values.ndim == 2 else feature_values
        
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
        top_factors = explanations[:5]
        
        # Generate summary
        summary_parts = []
        for exp in explanations[:3]:
            feature = exp["feature"].replace("_", " ").title()
            summary_parts.append(
                f"{feature} (value: {exp['value']:.2f}) {exp['impact']} the risk"
            )
        summary = f"The prediction is primarily influenced by: {', '.join(summary_parts)}."
        
        return {
            "explanations": explanations,
            "top_factors": top_factors,
            "summary": summary
        }
    
    def _predict_cardiovascular(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cardiovascular prediction with SHAP explanation."""
        model = self.models[ModelType.CARDIOVASCULAR]
        explainer = self.explainers[ModelType.CARDIOVASCULAR]
        
        # Process age (convert days to years if needed)
        age_years = data["age"] / 365.25 if data["age"] > 150 else data["age"]
        
        # Convert gender string to int (1=Female, 2=Male) for model
        gender_int = 1 if data["gender"] == "Female" else 2
        
        # Prepare feature array in correct order
        features = np.array([[
            age_years,
            gender_int,
            data["height"],
            data["weight"],
            data["ap_hi"],
            data["ap_lo"],
            data["cholesterol"],
            data["gluc"],
            data["smoke"],
            data["alco"],
            data["active"]
        ]])
        
        feature_names = [
            "age", "gender", "height", "weight", "ap_hi", "ap_lo",
            "cholesterol", "gluc", "smoke", "alco", "active"
        ]
        
        # Make prediction
        prediction = int(model.predict(features)[0])
        proba = model.predict_proba(features)[0]
        confidence = float(max(proba))
        risk_probability = float(proba[1]) if len(proba) > 1 else float(proba[0])
        
        # Generate SHAP explanation
        shap_values = explainer.shap_values(features)
        explanation = self._format_shap_explanation(shap_values, feature_names, features)
        
        risk_category = self._get_risk_category(risk_probability)
        
        return {
            "selected_model": "cardiovascular",
            "prediction": prediction,
            "risk_probability": round(risk_probability, 4),
            "confidence_score": round(confidence, 4),
            "risk_category": risk_category,
            "input_data": {
                "age_years": round(age_years, 1),
                "bmi": round(data["weight"] / ((data["height"] / 100) ** 2), 2),
                "gender": data["gender"],
                "systolic_bp": data["ap_hi"],
                "diastolic_bp": data["ap_lo"],
                "cholesterol_level": data["cholesterol"],
                "glucose_level": data["gluc"],
                "smoking": bool(data["smoke"]),
                "alcohol": bool(data["alco"]),
                "physical_activity": bool(data["active"])
            },
            "explanation": explanation
        }
    
    def _predict_diabetes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute diabetes prediction with SHAP explanation."""
        model = self.models[ModelType.DIABETES]
        explainer = self.explainers[ModelType.DIABETES]
        encoders = self.encoders.get("diabetes", {})
        
        # Encode categorical variables
        gender_encoded = encoders["gender_encoder"].transform([data["gender"]])[0]
        smoking_encoded = encoders["smoking_encoder"].transform([data["smoking_history"]])[0]
        
        # Prepare feature array in correct order
        features = np.array([[
            data["age"],
            data["hypertension"],
            data["heart_disease"],
            data["bmi"],
            data["HbA1c_level"],
            data["blood_glucose_level"],
            gender_encoded,
            smoking_encoded
        ]])
        
        feature_names = self.feature_info.get("diabetes", {}).get("feature_names", [
            "age", "hypertension", "heart_disease", "bmi",
            "HbA1c_level", "blood_glucose_level", "gender_encoded", "smoking_encoded"
        ])
        
        # Make prediction
        prediction = int(model.predict(features)[0])
        proba = model.predict_proba(features)[0]
        confidence = float(np.max(proba))
        risk_probability = float(proba[1]) if len(proba) > 1 else float(proba[0])
        
        # Generate SHAP explanation
        shap_values = explainer.shap_values(features)
        explanation = self._format_shap_explanation(shap_values, feature_names, features)
        
        risk_category = self._get_risk_category(risk_probability)
        
        # BMI category
        bmi = data["bmi"]
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal weight"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"
        
        # HbA1c category
        hba1c = data["HbA1c_level"]
        if hba1c < 5.7:
            hba1c_category = "Normal"
        elif hba1c < 6.5:
            hba1c_category = "Prediabetes"
        else:
            hba1c_category = "Diabetes"
        
        # Glucose category
        glucose = data["blood_glucose_level"]
        if glucose < 100:
            glucose_category = "Normal"
        elif glucose < 126:
            glucose_category = "Prediabetes"
        else:
            glucose_category = "Diabetes"
        
        return {
            "selected_model": "diabetes",
            "prediction": prediction,
            "risk_probability": round(risk_probability, 4),
            "confidence_score": round(confidence, 4),
            "risk_category": risk_category,
            "input_data": {
                "age": data["age"],
                "gender": data["gender"],
                "bmi": data["bmi"],
                "bmi_category": bmi_category,
                "hypertension": bool(data["hypertension"]),
                "heart_disease": bool(data["heart_disease"]),
                "smoking_history": data["smoking_history"],
                "HbA1c_level": data["HbA1c_level"],
                "HbA1c_category": hba1c_category,
                "blood_glucose_level": data["blood_glucose_level"],
                "glucose_category": glucose_category
            },
            "explanation": explanation
        }
    
    def route(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route incoming data to ALL models whose requirements are met.
        
        Runs all eligible models and returns combined results.
        
        Args:
            data: Input patient data dictionary
            
        Returns:
            Prediction results from all eligible models with SHAP explanations,
            or error message if no model requirements are met.
        """
        logger.info(f"Routing request with keys: {list(data.keys())}")
        
        results = {}
        models_run = []
        
        # Check and run Cardiovascular Model
        cardio_valid, cardio_issues = CARDIOVASCULAR_REQUIREMENTS.validate(data)
        if cardio_valid:
            if ModelType.CARDIOVASCULAR in self.models:
                logger.info("Running Cardiovascular model - all requirements met")
                results["cardiovascular"] = self._predict_cardiovascular(data)
                models_run.append("cardiovascular")
            else:
                results["cardiovascular"] = {"error": "Model not loaded"}
        
        # Check and run Diabetes Model
        diabetes_valid, diabetes_issues = DIABETES_REQUIREMENTS.validate(data)
        if diabetes_valid:
            if ModelType.DIABETES in self.models:
                logger.info("Running Diabetes model - all requirements met")
                results["diabetes"] = self._predict_diabetes(data)
                models_run.append("diabetes")
            else:
                results["diabetes"] = {"error": "Model not loaded"}
        
        # If no models ran, return error with details
        if not models_run:
            logger.warning("No model requirements fully met")
            return {
                "error": "Requirements not met for any model.",
                "models_run": [],
                "validation_details": {
                    "cardiovascular": {
                        "valid": False,
                        "missing_or_invalid": cardio_issues
                    },
                    "diabetes": {
                        "valid": False,
                        "missing_or_invalid": diabetes_issues
                    }
                },
                "hint": "Ensure all required features are provided with correct types and values."
            }
        
        # Return results from all models that ran
        return {
            "models_run": models_run,
            "results": results,
            "summary": self._generate_combined_summary(results, models_run)
        }
    
    def _generate_combined_summary(self, results: Dict[str, Any], models_run: List[str]) -> Dict[str, Any]:
        """Generate a combined summary when multiple models run."""
        summary = {
            "total_models_run": len(models_run),
            "risk_overview": {}
        }
        
        for model_name in models_run:
            if model_name in results and "error" not in results[model_name]:
                result = results[model_name]
                summary["risk_overview"][model_name] = {
                    "risk_category": result.get("risk_category"),
                    "risk_probability": result.get("risk_probability"),
                    "prediction": result.get("prediction")
                }
        
        # Determine overall risk assessment
        risk_levels = {"High": 3, "Medium": 2, "Low": 1}
        max_risk = "Low"
        for model_name, overview in summary["risk_overview"].items():
            if overview["risk_category"] and risk_levels.get(overview["risk_category"], 0) > risk_levels.get(max_risk, 0):
                max_risk = overview["risk_category"]
        
        summary["highest_risk_level"] = max_risk
        summary["recommendation"] = self._get_recommendation(max_risk, models_run)
        
        return summary
    
    def _get_recommendation(self, risk_level: str, models_run: List[str]) -> str:
        """Generate recommendation based on overall risk level."""
        if risk_level == "High":
            return "Immediate medical consultation recommended. Multiple risk factors detected."
        elif risk_level == "Medium":
            return "Schedule follow-up with healthcare provider. Monitor risk factors closely."
        else:
            return "Continue healthy lifestyle. Regular check-ups recommended."
    
    def get_model_requirements(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the requirements schema for one or all models.
        
        Args:
            model_name: Optional specific model name ("cardiovascular" or "diabetes")
            
        Returns:
            Requirements schema dictionary
        """
        requirements = {
            "cardiovascular": {
                "required_features": CARDIOVASCULAR_REQUIREMENTS.required_features,
                "feature_types": {k: v.__name__ for k, v in CARDIOVASCULAR_REQUIREMENTS.feature_types.items()},
                "categorical_values": CARDIOVASCULAR_REQUIREMENTS.categorical_values,
                "model_loaded": ModelType.CARDIOVASCULAR in self.models
            },
            "diabetes": {
                "required_features": DIABETES_REQUIREMENTS.required_features,
                "feature_types": {k: v.__name__ for k, v in DIABETES_REQUIREMENTS.feature_types.items()},
                "categorical_values": DIABETES_REQUIREMENTS.categorical_values,
                "model_loaded": ModelType.DIABETES in self.models
            }
        }
        
        if model_name:
            return requirements.get(model_name.lower(), {"error": f"Unknown model: {model_name}"})
        return requirements
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against all model requirements without making predictions.
        
        Args:
            data: Input data to validate
            
        Returns:
            Validation results for all models
        """
        cardio_valid, cardio_issues = CARDIOVASCULAR_REQUIREMENTS.validate(data)
        diabetes_valid, diabetes_issues = DIABETES_REQUIREMENTS.validate(data)
        
        eligible_models = []
        if cardio_valid:
            eligible_models.append("cardiovascular")
        if diabetes_valid:
            eligible_models.append("diabetes")
        
        return {
            "eligible_models": eligible_models,
            "would_route_to": eligible_models[0] if eligible_models else None,
            "validation": {
                "cardiovascular": {
                    "valid": cardio_valid,
                    "issues": cardio_issues if not cardio_valid else []
                },
                "diabetes": {
                    "valid": diabetes_valid,
                    "issues": diabetes_issues if not diabetes_valid else []
                }
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status of the router and all models."""
        return {
            "status": "healthy",
            "router": "MainSwarmRouter",
            "models": {
                "cardiovascular": {
                    "loaded": ModelType.CARDIOVASCULAR in self.models,
                    "explainer_ready": ModelType.CARDIOVASCULAR in self.explainers
                },
                "diabetes": {
                    "loaded": ModelType.DIABETES in self.models,
                    "explainer_ready": ModelType.DIABETES in self.explainers,
                    "encoders_loaded": "diabetes" in self.encoders
                }
            }
        }


# Convenience function for module-level usage
_router_instance: Optional[MainSwarmRouter] = None


def get_router() -> MainSwarmRouter:
    """Get or create the singleton router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = MainSwarmRouter()
    return _router_instance


def route_prediction(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to route a prediction request.
    
    Args:
        data: Input patient data
        
    Returns:
        Prediction result or error
    """
    return get_router().route(data)


if __name__ == "__main__":
    # Simple test when run directly
    router = MainSwarmRouter()
    print("\n=== Main Swarm Router Health Check ===")
    print(router.health_check())
    
    print("\n=== Model Requirements ===")
    print(router.get_model_requirements())
