# Main Swarm Router - Unified Input Requirements Schema

## Overview

This document serves as the **master reference** for all input fields required by the AI prediction models in the Main Swarm Router system. All fields are initialized with `NaN` (Not a Number / Not Available) to indicate they need to be populated.

---

## Combined Request Body (All Fields)

```json
{
  "age": NaN,
  "gender": NaN,
  "height": NaN,
  "weight": NaN,
  "ap_hi": NaN,
  "ap_lo": NaN,
  "cholesterol": NaN,
  "gluc": NaN,
  "smoke": NaN,
  "alco": NaN,
  "active": NaN,
  "hypertension": NaN,
  "heart_disease": NaN,
  "smoking_history": NaN,
  "bmi": NaN,
  "HbA1c_level": NaN,
  "blood_glucose_level": NaN
}
```

---

## Complete Field Descriptions

| Field | Type | Used By | Valid Values | Description |
|-------|------|---------|--------------|-------------|
| `age` | float | Cardio, Diabetes | Any positive number | Age in years |
| `gender` | int/str | Cardio (int), Diabetes (str) | Cardio: 1=Female, 2=Male / Diabetes: "Female", "Male", "Other" | Patient gender |
| `height` | float | Cardio | Any positive number | Height in centimeters |
| `weight` | float | Cardio | Any positive number | Weight in kilograms |
| `ap_hi` | int | Cardio | Any positive number | Systolic blood pressure (mmHg) |
| `ap_lo` | int | Cardio | Any positive number | Diastolic blood pressure (mmHg) |
| `cholesterol` | int | Cardio | 1, 2, 3 | 1=Normal, 2=Above normal, 3=Well above normal |
| `gluc` | int | Cardio | 1, 2, 3 | Glucose level: 1=Normal, 2=Above normal, 3=Well above normal |
| `smoke` | int | Cardio | 0, 1 | Smoking status: 0=No, 1=Yes |
| `alco` | int | Cardio | 0, 1 | Alcohol consumption: 0=No, 1=Yes |
| `active` | int | Cardio | 0, 1 | Physical activity: 0=No, 1=Yes |
| `hypertension` | int | Diabetes | 0, 1 | Hypertension: 0=No, 1=Yes |
| `heart_disease` | int | Diabetes | 0, 1 | Heart disease: 0=No, 1=Yes |
| `smoking_history` | str | Diabetes | "never", "No Info", "current", "former", "ever", "not current" | Smoking history category |
| `bmi` | float | Diabetes | Any positive number | Body Mass Index (kg/m²) |
| `HbA1c_level` | float | Diabetes | 3.5 - 9.0 (typical) | Hemoglobin A1c level (%) |
| `blood_glucose_level` | int | Diabetes | 80 - 300 (typical) | Blood glucose level (mg/dL) |

---

## Model-Specific Requirements

### Cardiovascular Model (11 Required Fields)

```json
{
  "age": NaN,
  "gender": NaN,
  "height": NaN,
  "weight": NaN,
  "ap_hi": NaN,
  "ap_lo": NaN,
  "cholesterol": NaN,
  "gluc": NaN,
  "smoke": NaN,
  "alco": NaN,
  "active": NaN
}
```

| Field | Type | Valid Values | Description |
|-------|------|--------------|-------------|
| `age` | float | > 0 | Age in years |
| `gender` | int | 1, 2 | 1=Female, 2=Male |
| `height` | float | > 0 | Height in centimeters |
| `weight` | float | > 0 | Weight in kilograms |
| `ap_hi` | int | > 0 | Systolic blood pressure (mmHg) |
| `ap_lo` | int | > 0 | Diastolic blood pressure (mmHg) |
| `cholesterol` | int | 1, 2, 3 | 1=Normal, 2=Above normal, 3=Well above normal |
| `gluc` | int | 1, 2, 3 | 1=Normal, 2=Above normal, 3=Well above normal |
| `smoke` | int | 0, 1 | 0=No, 1=Yes |
| `alco` | int | 0, 1 | 0=No, 1=Yes |
| `active` | int | 0, 1 | 0=No, 1=Yes |

---

### Diabetes Model (8 Required Fields)

```json
{
  "age": NaN,
  "gender": NaN,
  "hypertension": NaN,
  "heart_disease": NaN,
  "smoking_history": NaN,
  "bmi": NaN,
  "HbA1c_level": NaN,
  "blood_glucose_level": NaN
}
```

| Field | Type | Valid Values | Description |
|-------|------|--------------|-------------|
| `age` | float | > 0 | Age in years |
| `gender` | str | "Female", "Male", "Other" | Patient gender |
| `hypertension` | int | 0, 1 | 0=No, 1=Yes |
| `heart_disease` | int | 0, 1 | 0=No, 1=Yes |
| `smoking_history` | str | "never", "No Info", "current", "former", "ever", "not current" | Smoking history |
| `bmi` | float | > 0 | Body Mass Index (kg/m²) |
| `HbA1c_level` | float | 3.5 - 9.0 | Hemoglobin A1c level (%) |
| `blood_glucose_level` | int | 80 - 300 | Blood glucose level (mg/dL) |

---

## Field Overlap Notes

| Shared Field | Cardiovascular Format | Diabetes Format | Notes |
|--------------|----------------------|-----------------|-------|
| `age` | float (years) | float (years) | Same format |
| `gender` | int (1=F, 2=M) | str ("Female", "Male", "Other") | **Different formats!** |

---

## Routing Logic

The Main Swarm Router uses **If-Elif-Else priority logic**:

1. **IF** all 11 Cardiovascular fields are valid → Route to **Cardiovascular Model**
2. **ELIF** all 8 Diabetes fields are valid → Route to **Diabetes Model**
3. **ELSE** → Return error: `"Requirements not met for any model."`

---

## Example: Populating the Schema

### For Cardiovascular Prediction:
```json
{
  "age": 55,
  "gender": 2,
  "height": 170,
  "weight": 85,
  "ap_hi": 150,
  "ap_lo": 95,
  "cholesterol": 3,
  "gluc": 2,
  "smoke": 1,
  "alco": 0,
  "active": 0
}
```

### For Diabetes Prediction:
```json
{
  "age": 52,
  "gender": "Female",
  "hypertension": 1,
  "heart_disease": 1,
  "smoking_history": "former",
  "bmi": 32.5,
  "HbA1c_level": 7.2,
  "blood_glucose_level": 180
}
```

---

## Version Info

- **Created**: February 10, 2026
- **Models Covered**: Cardiovascular, Diabetes
- **Total Unique Fields**: 17
