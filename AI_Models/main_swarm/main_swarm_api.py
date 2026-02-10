"""
Main Swarm Router API - FastAPI Web Service

This API exposes the Main Swarm Router functionality as REST endpoints.

Endpoints:
    - GET  /health              - Health check
    - GET  /requirements        - Get model requirements schema
    - GET  /schema              - Get empty input schema (all NaN)
    - POST /validate            - Validate data without prediction
    - POST /predict             - Route and predict (structured JSON)
    - POST /predict/natural     - Natural language input → normalize → predict
    - POST /normalize           - Convert natural language to structured JSON

Run with:
    uvicorn main_swarm_api:app --host 0.0.0.0 --port 5001 --reload
"""

import os
import logging
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from main_swarm_router import MainSwarmRouter
from groq_normalizer import GroqInputNormalizer, MASTER_SCHEMA

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Main Swarm Router API",
    description="Central hub for routing patient data to appropriate AI prediction models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize router (singleton)
router_instance: Optional[MainSwarmRouter] = None
normalizer_instance: Optional[GroqInputNormalizer] = None


def get_router() -> MainSwarmRouter:
    """Get or initialize the router instance."""
    global router_instance
    if router_instance is None:
        router_instance = MainSwarmRouter()
    return router_instance


def get_normalizer(api_key: Optional[str] = None) -> GroqInputNormalizer:
    """Get or initialize the normalizer instance."""
    global normalizer_instance
    if normalizer_instance is None or api_key:
        normalizer_instance = GroqInputNormalizer(api_key)
    return normalizer_instance


class PredictionRequest(BaseModel):
    """
    Flexible prediction request that can contain features for any model.
    The router will determine which model to use based on available features.
    """
    # Cardiovascular features
    age: Optional[float] = Field(None, description="Age in years (or days if > 150)")
    gender: Optional[Any] = Field(None, description="Gender: int (1=F, 2=M) for cardio, str for diabetes")
    height: Optional[float] = Field(None, description="Height in cm (cardiovascular)")
    weight: Optional[float] = Field(None, description="Weight in kg (cardiovascular)")
    ap_hi: Optional[int] = Field(None, description="Systolic blood pressure (cardiovascular)")
    ap_lo: Optional[int] = Field(None, description="Diastolic blood pressure (cardiovascular)")
    cholesterol: Optional[int] = Field(None, description="Cholesterol: 1=normal, 2=above, 3=well above (cardiovascular)")
    gluc: Optional[int] = Field(None, description="Glucose: 1=normal, 2=above, 3=well above (cardiovascular)")
    smoke: Optional[int] = Field(None, description="Smoking: 0=no, 1=yes (cardiovascular)")
    alco: Optional[int] = Field(None, description="Alcohol: 0=no, 1=yes (cardiovascular)")
    active: Optional[int] = Field(None, description="Physical activity: 0=no, 1=yes (cardiovascular)")
    
    # Diabetes features
    hypertension: Optional[int] = Field(None, description="Hypertension: 0=no, 1=yes (diabetes)")
    heart_disease: Optional[int] = Field(None, description="Heart disease: 0=no, 1=yes (diabetes)")
    smoking_history: Optional[str] = Field(None, description="Smoking history category (diabetes)")
    bmi: Optional[float] = Field(None, description="Body Mass Index (diabetes)")
    HbA1c_level: Optional[float] = Field(None, description="Hemoglobin A1c level (diabetes)")
    blood_glucose_level: Optional[int] = Field(None, description="Blood glucose level mg/dL (diabetes)")

    class Config:
        extra = "allow"  # Allow additional fields


class ValidationRequest(BaseModel):
    """Request model for data validation."""
    data: Dict[str, Any] = Field(..., description="Patient data to validate")


class NaturalLanguageRequest(BaseModel):
    """Request model for natural language input."""
    text: str = Field(..., description="Natural language description of patient data")
    api_key: Optional[str] = Field(None, description="Groq API key (optional, uses env var if not provided)")


class NormalizeRequest(BaseModel):
    """Request model for normalization only."""
    text: str = Field(..., description="Natural language description of patient data")
    api_key: Optional[str] = Field(None, description="Groq API key (optional, uses env var if not provided)")


@app.on_event("startup")
def startup_event():
    """Initialize the router on startup."""
    try:
        router = get_router()
        health = router.health_check()
        logger.info(f"Main Swarm Router initialized: {health}")
    except Exception as e:
        logger.error(f"Failed to initialize router: {e}")


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    
    Returns the status of the router and all loaded models.
    """
    try:
        router = get_router()
        return router.health_check()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Router not healthy: {e}")


@app.get("/requirements")
def get_requirements(model: Optional[str] = None):
    """
    Get the requirements schema for models.
    
    Args:
        model: Optional model name ("cardiovascular" or "diabetes")
               If not provided, returns requirements for all models.
    
    Returns:
        Requirements schema including required features, types, and valid values.
    """
    router = get_router()
    return router.get_model_requirements(model)


@app.post("/validate")
def validate_data(request: ValidationRequest):
    """
    Validate input data against all model requirements without making predictions.
    
    This endpoint allows you to check if your data meets the requirements
    for any model before attempting a prediction.
    
    Returns:
        Validation results showing which models the data is eligible for.
    """
    router = get_router()
    return router.validate_data(request.data)


@app.post("/predict")
def predict(request: PredictionRequest):
    """
    Route patient data to the appropriate model and get a prediction.
    
    The router uses strict If-Elif-Else priority logic:
    1. If ALL cardiovascular features are present → Cardiovascular Model
    2. Elif ALL diabetes features are present → Diabetes Model
    3. Else → Error with "Requirements not met for any model."
    
    STRICT POLICIES:
    - NO data imputation or generation
    - NO predictions if requirements aren't 100% met
    - Individual SHAP explainability for the selected model
    
    Returns:
        {
            "selected_model": "model_name",
            "prediction": 0 or 1,
            "risk_probability": float,
            "confidence_score": float,
            "risk_category": "Low" | "Medium" | "High",
            "input_data": {...},
            "explanation": {
                "explanations": [...],
                "top_factors": [...],
                "summary": "..."
            }
        }
        
    Or error:
        {
            "error": "Requirements not met for any model.",
            "selected_model": null,
            "validation_details": {...}
        }
    """
    router = get_router()
    
    # Convert request to dict, excluding None values
    data = {k: v for k, v in request.dict().items() if v is not None}
    
    result = router.route(data)
    
    # If there's an error in the result, we still return 200 but with error info
    # This allows the client to see the validation details
    return result


@app.get("/model/info")
def model_info():
    """
    Get detailed information about all available models.
    """
    router = get_router()
    health = router.health_check()
    requirements = router.get_model_requirements()
    
    return {
        "router": "MainSwarmRouter",
        "routing_priority": [
            "1. Cardiovascular Model (11 features)",
            "2. Diabetes Model (8 features)",
            "3. Error if no model requirements met"
        ],
        "strict_policies": [
            "No data imputation or generation",
            "100% feature requirements must be met",
            "Individual SHAP explainability per model"
        ],
        "models": health["models"],
        "requirements": requirements
    }


# ============================================================================
# GROQ NORMALIZER ENDPOINTS
# ============================================================================

@app.get("/schema")
def get_empty_schema():
    """
    Get the empty input schema with all fields set to null/NaN.
    
    This is the master schema that the normalizer populates.
    """
    return {
        "description": "Master input schema - all fields initialized to null",
        "schema": MASTER_SCHEMA,
        "total_fields": len(MASTER_SCHEMA),
        "models": {
            "cardiovascular": ["age", "gender", "height", "weight", "ap_hi", "ap_lo", 
                              "cholesterol", "gluc", "smoke", "alco", "active"],
            "diabetes": ["age", "gender", "hypertension", "heart_disease", 
                        "smoking_history", "bmi", "HbA1c_level", "blood_glucose_level"]
        }
    }


@app.post("/normalize")
def normalize_input(request: NormalizeRequest):
    """
    Convert natural language input to structured JSON schema.
    
    This endpoint ONLY normalizes the data - it does NOT make predictions.
    Use this to see what the LLM extracts from your input.
    
    STRICT POLICY: 
    - NEVER augments or generates data
    - Missing values remain null/NaN
    - Only extracts explicitly stated information
    
    Example input:
        "55 year old male, 170cm tall, weighs 85kg, blood pressure 150/95, 
         high cholesterol, smoker, doesn't drink, sedentary lifestyle"
    
    Returns:
        {
            "success": true,
            "normalized_data": { extracted fields with null for missing },
            "raw_input": "original text"
        }
    """
    api_key = request.api_key or os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="Groq API key required. Provide in request or set GROQ_API_KEY environment variable."
        )
    
    try:
        normalizer = get_normalizer(api_key)
        result = normalizer.normalize(request.text)
        return result
    except Exception as e:
        logger.error(f"Normalization error: {e}")
        raise HTTPException(status_code=500, detail=f"Normalization failed: {str(e)}")


@app.post("/predict/natural")
def predict_natural_language(request: NaturalLanguageRequest):
    """
    Accept natural language input, normalize it, and route to appropriate model.
    
    This is the main endpoint for natural language predictions. It:
    1. Uses Groq LLM to extract structured data from text
    2. Validates against model requirements
    3. Routes to the appropriate model if requirements are met
    4. Returns prediction with SHAP explanation
    
    STRICT POLICIES:
    - NO data augmentation - only extracts what is explicitly stated
    - Missing values stay as null/NaN
    - If requirements aren't met, returns error with what's missing
    
    Example input:
        "Patient is a 52 year old female with hypertension and heart disease.
         Former smoker, BMI of 32.5, HbA1c level is 7.2, blood glucose 180."
    
    Returns:
        Success: Prediction result with SHAP explanation
        Failure: Error with validation details showing missing fields
    """
    api_key = request.api_key or os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Groq API key required. Provide in request or set GROQ_API_KEY environment variable."
        )
    
    try:
        # Get normalizer and router
        normalizer = get_normalizer(api_key)
        router = get_router()
        
        # Normalize and route
        result = normalizer.normalize_and_route(request.text, router)
        return result
        
    except Exception as e:
        logger.error(f"Natural language prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/normalize/validate")
def normalize_and_validate(request: NormalizeRequest):
    """
    Normalize natural language input and validate against model requirements.
    Does NOT make a prediction - just shows what was extracted and if it's valid.
    
    Useful for debugging and understanding what the LLM extracts.
    
    Returns:
        {
            "normalized_data": { extracted fields },
            "validation": {
                "cardiovascular": { valid: bool, missing: [...] },
                "diabetes": { valid: bool, missing: [...] }
            },
            "would_route_to": "model_name" or null
        }
    """
    api_key = request.api_key or os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Groq API key required. Provide in request or set GROQ_API_KEY environment variable."
        )
    
    try:
        # Normalize
        normalizer = get_normalizer(api_key)
        norm_result = normalizer.normalize(request.text)
        
        if not norm_result.get("success", False):
            return norm_result
        
        # Get non-null values for validation
        data = norm_result["normalized_data"]
        filtered_data = {k: v for k, v in data.items() if v is not None}
        
        # Validate
        router = get_router()
        validation = router.validate_data(filtered_data)
        
        return {
            "success": True,
            "raw_input": request.text,
            "normalized_data": data,
            "extracted_fields": filtered_data,
            "missing_fields": [k for k, v in data.items() if v is None],
            "validation": validation
        }
        
    except Exception as e:
        logger.error(f"Normalize and validate error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_swarm_api:app", host="0.0.0.0", port=5001, reload=True)
