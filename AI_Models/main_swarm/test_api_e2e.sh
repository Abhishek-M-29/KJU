#!/bin/bash
# End-to-End Test Script for Main Swarm Router API
# Run this after starting the API server

API_URL="http://localhost:5001"

echo "========================================"
echo "  MAIN SWARM ROUTER - E2E API TESTS"
echo "========================================"

# 1. Health Check
echo -e "\n=== 1. HEALTH CHECK ==="
curl -s $API_URL/health | python3 -m json.tool

# 2. Get Model Requirements
echo -e "\n=== 2. MODEL REQUIREMENTS ==="
curl -s $API_URL/requirements | python3 -m json.tool

# 3. Model Info
echo -e "\n=== 3. MODEL INFO ==="
curl -s $API_URL/model/info | python3 -m json.tool

# 4. Successful Cardiovascular Prediction (Complete Data)
echo -e "\n=== 4. CARDIOVASCULAR PREDICTION (Complete Data) ==="
curl -s -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | python3 -m json.tool

# 5. Successful Diabetes Prediction (Complete Data)
echo -e "\n=== 5. DIABETES PREDICTION (Complete Data) ==="
curl -s -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "gender": "Male",
    "hypertension": 1,
    "heart_disease": 0,
    "smoking_history": "former",
    "bmi": 28.5,
    "HbA1c_level": 6.2,
    "blood_glucose_level": 140
  }' | python3 -m json.tool

# 6. FAILED - Incomplete Data (Missing Features)
echo -e "\n=== 6. INCOMPLETE DATA - Should FAIL ==="
echo "Sending: {age, gender, height} - missing 8 required fields"
curl -s -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 50,
    "gender": 2,
    "height": 175
  }' | python3 -m json.tool

# 7. FAILED - Invalid Categorical Value
echo -e "\n=== 7. INVALID CATEGORICAL - Should FAIL ==="
echo "Sending: gender=5 (invalid, should be 1 or 2)"
curl -s -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 50,
    "gender": 5,
    "height": 175,
    "weight": 80,
    "ap_hi": 140,
    "ap_lo": 90,
    "cholesterol": 2,
    "gluc": 1,
    "smoke": 1,
    "alco": 0,
    "active": 1
  }' | python3 -m json.tool

# 8. FAILED - Empty Data
echo -e "\n=== 8. EMPTY DATA - Should FAIL ==="
curl -s -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool

# 9. Validate Data (without prediction)
echo -e "\n=== 9. VALIDATE DATA (Pre-check without prediction) ==="
curl -s -X POST $API_URL/validate \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
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
  }' | python3 -m json.tool

echo -e "\n========================================"
echo "  TESTS COMPLETE"
echo "========================================"
