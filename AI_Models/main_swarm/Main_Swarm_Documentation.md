# Main Swarm Router - Central Hub for AI Model Routing

## Overview

The Main Swarm Router is the central hub for the KJU healthcare AI system. It acts as a **gatekeeper** that routes incoming patient data to the appropriate AI prediction model based on strict feature validation.

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           MAIN SWARM ROUTER             │
                    │         (Central Gatekeeper)            │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │         STRICT VALIDATION           │
                    │   - 100% feature requirements       │
                    │   - No imputation/generation        │
                    │   - Type & value validation         │
                    └─────────────────┬───────────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
           ▼                          ▼                          ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│  CARDIOVASCULAR     │   │     DIABETES        │   │       ERROR         │
│     MODEL           │   │      MODEL          │   │     RESPONSE        │
│  (Priority 1)       │   │   (Priority 2)      │   │   (No match)        │
│                     │   │                     │   │                     │
│  11 Required        │   │  8 Required         │   │  "Requirements      │
│  Features           │   │  Features           │   │   not met for       │
│                     │   │                     │   │   any model."       │
│  + SHAP Explainer   │   │  + SHAP Explainer   │   │                     │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
```

## Routing Priority Logic

The router uses **If-Elif-Else** priority logic:

1. **IF** all 11 Cardiovascular features are present → Route to Cardiovascular Model
2. **ELIF** all 8 Diabetes features are present → Route to Diabetes Model  
3. **ELSE** → Return error: "Requirements not met for any model."

## Strict Policies

### 1. No Data Imputation
- **NEVER** generate, impute, or fill missing values
- **NEVER** substitute zeros, NaNs, or defaults for missing data
- Missing data = Rejected request

### 2. 100% Feature Requirements
- All required features must be present
- All values must be of the correct type
- All categorical values must be valid

### 3. Individual SHAP Explainability
- Each model has its own SHAP TreeExplainer
- Only the selected model's explainer is triggered
- Explanations include feature importance and impact direction

## Model Requirements

### Cardiovascular Model (11 Features)

| Feature | Type | Valid Values | Description |
|---------|------|--------------|-------------|
| `age` | float | Any positive number | Age in years (or days if >150) |
| `gender` | int | 1, 2 | 1=Female, 2=Male |
| `height` | float | Any positive number | Height in centimeters |
| `weight` | float | Any positive number | Weight in kilograms |
| `ap_hi` | int | Any positive number | Systolic blood pressure |
| `ap_lo` | int | Any positive number | Diastolic blood pressure |
| `cholesterol` | int | 1, 2, 3 | 1=Normal, 2=Above, 3=Well above |
| `gluc` | int | 1, 2, 3 | 1=Normal, 2=Above, 3=Well above |
| `smoke` | int | 0, 1 | 0=No, 1=Yes |
| `alco` | int | 0, 1 | 0=No, 1=Yes |
| `active` | int | 0, 1 | 0=No, 1=Yes |

### Diabetes Model (8 Features)

| Feature | Type | Valid Values | Description |
|---------|------|--------------|-------------|
| `age` | float | Any positive number | Age in years |
| `gender` | str | "Female", "Male", "Other" | Gender string |
| `hypertension` | int | 0, 1 | 0=No, 1=Yes |
| `heart_disease` | int | 0, 1 | 0=No, 1=Yes |
| `smoking_history` | str | "never", "No Info", "current", "former", "ever", "not current" | Smoking category |
| `bmi` | float | Any positive number | Body Mass Index |
| `HbA1c_level` | float | 3.5-9.0 typical | Hemoglobin A1c level |
| `blood_glucose_level` | int | 80-300 typical | Blood glucose in mg/dL |

## API Endpoints

### Health Check
```
GET /health
```

### Get Requirements
```
GET /requirements
GET /requirements?model=cardiovascular
GET /requirements?model=diabetes
```

### Validate Data (without prediction)
```
POST /validate
Content-Type: application/json

{
    "data": { ... patient features ... }
}
```

### Predict (route and execute)
```
POST /predict
Content-Type: application/json

{
    "age": 50,
    "gender": 2,
    "height": 175,
    ...
}
```

## Response Format

### Successful Prediction
```json
{
    "selected_model": "cardiovascular",
    "prediction": 1,
    "risk_probability": 0.75,
    "confidence_score": 0.82,
    "risk_category": "High",
    "input_data": { ... },
    "explanation": {
        "explanations": [...],
        "top_factors": [...],
        "summary": "The prediction is primarily influenced by..."
    }
}
```

### Requirements Not Met
```json
{
    "error": "Requirements not met for any model.",
    "selected_model": null,
    "validation_details": {
        "cardiovascular": {
            "valid": false,
            "missing_or_invalid": ["smoke", "alco", "active"]
        },
        "diabetes": {
            "valid": false,
            "missing_or_invalid": ["HbA1c_level", "blood_glucose_level", ...]
        }
    },
    "hint": "Ensure all required features are provided with correct types and values."
}
```

## Usage Examples

### Python Usage
```python
from main_swarm import MainSwarmRouter

router = MainSwarmRouter()

# Complete cardiovascular data
result = router.route({
    "age": 50,
    "gender": 2,
    "height": 175,
    "weight": 80,
    "ap_hi": 140,
    "ap_lo": 90,
    "cholesterol": 2,
    "gluc": 1,
    "smoke": 1,
    "alco": 0,
    "active": 1
})

print(result["selected_model"])  # "cardiovascular"
print(result["prediction"])       # 0 or 1
print(result["explanation"])      # SHAP explanation
```

### cURL Examples
```bash
# Health check
curl http://localhost:5001/health

# Get requirements
curl http://localhost:5001/requirements

# Predict (complete data)
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 50, "gender": 2, "height": 175, "weight": 80, "ap_hi": 140, "ap_lo": 90, "cholesterol": 2, "gluc": 1, "smoke": 1, "alco": 0, "active": 1}'

# Predict (incomplete data - will fail)
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 50, "gender": 2, "height": 175}'
```

## Running the API

```bash
cd /path/to/KJU/AI_Models/main_swarm

# Activate your virtual environment first
source venv/bin/activate  # or your environment

# Run the API
uvicorn main_swarm_api:app --host 0.0.0.0 --port 5001 --reload
```

## Running Tests

```bash
cd /path/to/KJU/AI_Models/main_swarm
python test_main_swarm.py
```

## File Structure

```
AI_Models/
├── main_swarm/
│   ├── __init__.py                 # Module exports
│   ├── main_swarm_router.py        # Core router logic
│   ├── main_swarm_api.py           # FastAPI web service
│   ├── main_swarm_requirements.txt # Dependencies
│   ├── Main_Swarm_Documentation.md # This file
│   └── test_main_swarm.py          # Test suite
├── cardio/
│   ├── cardiovascular_api.py
│   └── xgboost_model.pkl
└── diabetes/
    ├── diabetes_api.py
    ├── diabetes_xgboost_model.pkl
    ├── diabetes_label_encoders.pkl
    └── diabetes_feature_info.pkl
```

## Integration Notes

1. The router looks for model files relative to its location in `AI_Models/main_swarm/`
2. Custom model paths can be provided during initialization
3. Models are loaded once at startup for performance
4. SHAP explainers are created per-model at load time
