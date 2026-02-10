# MedAssist Cardiovascular Disease Prediction API

## Overview
The Cardiovascular Disease Prediction API provides machine learning-based predictions for cardiovascular disease risk using XGBoost models with SHAP explanations.

## Installation & Setup

### Prerequisites
- Python 3.8+
- Required packages (install with pip):

```bash
pip install -r cardiovascular_requirements.txt
```

### Running the API
```bash
cd /path/to/MedAssist/AI
python cardiovascular_api.py
```

The API will start on `http://localhost:5002`

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running and model is loaded.

**Response:**
```json
{
  "status": "healthy",
  "message": "MedAssist Cardiovascular Prediction API is running",
  "model_loaded": true
}
```

### 2. Model Information
**GET** `/model/info`

Get information about the loaded model.

**Response:**
```json
{
  "model_info": {
    "loaded": true,
    "type": "XGBoost Classifier",
    "purpose": "Cardiovascular Disease Prediction",
    "features": ["age", "gender", "height", "weight", "ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", "alco", "active"]
  },
  "shap_explanations": "Available"
}
```

### 3. Cardiovascular Disease Prediction
**POST** `/predict`

Predict cardiovascular disease risk based on patient health metrics.

**Request Body:**
```json
{
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
}
```

**Field Descriptions:**
- `age`: Age in years (numeric)
- `gender`: 1 = Female, 2 = Male
- `height`: Height in centimeters
- `weight`: Weight in kilograms
- `ap_hi`: Systolic blood pressure
- `ap_lo`: Diastolic blood pressure
- `cholesterol`: 1 = Normal, 2 = Above normal, 3 = Well above normal
- `gluc`: Glucose level (1 = Normal, 2 = Above normal, 3 = Well above normal)
- `smoke`: 0 = No, 1 = Yes
- `alco`: Alcohol consumption (0 = No, 1 = Yes)
- `active`: Physical activity (0 = No, 1 = Yes)

**Response:**
```json
{
  "prediction": 1,
  "risk_probability": 0.75,
  "confidence_score": 0.82,
  "risk_category": "High",
  "input_data": {
    "age_years": 50.0,
    "bmi": 26.12,
    "gender": "Male",
    "systolic_bp": 140,
    "diastolic_bp": 90,
    "cholesterol_level": 2,
    "glucose_level": 1,
    "smoking": true,
    "alcohol": false,
    "physical_activity": true
  },
  "explanations": {
    "explanations": [...],
    "top_factors": [...],
    "summary": "The prediction is primarily influenced by: Ap_Hi (value: 140.00) increases the risk, Smoke (value: 1.00) increases the risk, Cholesterol (value: 2.00) increases the risk."
  },
  "interpretation": {
    "result": "High risk of cardiovascular disease",
    "recommendation": [
      "Consult with a cardiologist immediately for comprehensive evaluation",
      "Consider immediate lifestyle modifications including diet and exercise",
      "Monitor and manage blood pressure through diet, exercise, and medication if needed",
      "Smoking cessation is highly recommended"
    ]
  }
}
```

## Risk Categories

- **Low Risk**: Probability < 0.3
- **Medium Risk**: Probability 0.3 - 0.7
- **High Risk**: Probability > 0.7

## Testing

Use curl to test the API:

```bash
# Health check
curl http://localhost:5002/health

# Model info
curl http://localhost:5002/model/info

# Cardiovascular prediction
curl -X POST http://localhost:5002/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 50, "gender": 2, "height": 175, "weight": 80, "ap_hi": 140, "ap_lo": 90, "cholesterol": 2, "gluc": 1, "smoke": 1, "alco": 0, "active": 1}'
```

## Integration Example

```javascript
async function predictCardiovascular(patientData) {
  try {
    const response = await fetch('http://localhost:5002/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(patientData)
    });

    const result = await response.json();

    if (response.ok) {
      console.log('Prediction:', result.prediction);
      console.log('Risk Category:', result.risk_category);
      console.log('Recommendations:', result.interpretation.recommendation);
      return result;
    } else {
      console.error('Error:', result.error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}
```