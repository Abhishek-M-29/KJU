# MedAssist Diabetes Risk Prediction API

## Overview
The Diabetes Risk Prediction API provides machine learning-based predictions for diabetes risk using XGBoost models with SHAP explanations.

## Installation & Setup

### Prerequisites
- Python 3.8+
- Required packages (install with pip):

```bash
pip install -r diabetes_requirements.txt
```

### Running the API
```bash
cd /path/to/MedAssist/AI
python diabetes_api.py
```

The API will start on `http://localhost:5003`

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running and model is loaded.

**Response:**
```json
{
  "status": "healthy",
  "message": "MedAssist Diabetes Prediction API is running",
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
    "purpose": "Diabetes Risk Prediction",
    "features": ["age", "hypertension", "heart_disease", "bmi", "HbA1c_level", "blood_glucose_level", "gender_encoded", "smoking_encoded"]
  },
  "shap_explanations": "Available"
}
```

### 3. Diabetes Risk Prediction
**POST** `/predict`

Predict diabetes risk based on metabolic and lifestyle factors.

**Request Body:**
```json
{
  "age": 45,
  "gender": "Male",
  "hypertension": 1,
  "heart_disease": 0,
  "smoking_history": "former",
  "bmi": 28.5,
  "HbA1c_level": 6.2,
  "blood_glucose_level": 140
}
```

**Field Descriptions:**
- `age`: Age in years
- `gender`: "Female", "Male", or "Other"
- `hypertension`: 0 = No, 1 = Yes
- `heart_disease`: 0 = No, 1 = Yes
- `smoking_history`: "never", "No Info", "current", "former", "ever", "not current"
- `bmi`: Body Mass Index
- `HbA1c_level`: Hemoglobin A1c level (3.5-9.0)
- `blood_glucose_level`: Blood glucose level (80-300 mg/dL)

**Response:**
```json
{
  "prediction": 0,
  "risk_probability": 0.35,
  "confidence_score": 0.65,
  "risk_category": "Medium",
  "input_data": {
    "age": 45,
    "gender": "Male",
    "bmi": 28.5,
    "bmi_category": "Overweight",
    "hypertension": true,
    "heart_disease": false,
    "smoking_history": "former",
    "HbA1c_level": 6.2,
    "HbA1c_category": "Prediabetes",
    "blood_glucose_level": 140,
    "glucose_category": "Prediabetes"
  },
  "explanations": {
    "explanations": [...],
    "top_factors": [...],
    "summary": "The prediction is primarily influenced by: HbA1c_level (value: 6.20) increases the risk, Blood_glucose_level (value: 140.00) increases the risk, Age (value: 45.00) increases the risk."
  },
  "interpretation": {
    "result": "Low risk of diabetes",
    "recommendation": [
      "Schedule regular glucose monitoring and healthcare check-ups",
      "Implement diabetes prevention strategies",
      "Focus on blood sugar control through diet and lifestyle modifications",
      "Weight management through balanced diet and regular exercise"
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
curl http://localhost:5003/health

# Model info
curl http://localhost:5003/model/info

# Diabetes prediction
curl -X POST http://localhost:5003/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 45, "gender": "Male", "hypertension": 1, "heart_disease": 0, "smoking_history": "former", "bmi": 28.5, "HbA1c_level": 6.2, "blood_glucose_level": 140}'
```

## Integration Example

```javascript
async function predictDiabetes(patientData) {
  try {
    const response = await fetch('http://localhost:5003/predict', {
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