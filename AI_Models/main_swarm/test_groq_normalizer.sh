#!/bin/bash
# Test script for Groq Normalizer API endpoints
# Run this after starting the API server with your GROQ_API_KEY set

API_URL="http://localhost:5001"

# Check if API key is provided
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY not set!"
    echo "   Set it with: export GROQ_API_KEY='your-api-key'"
    echo ""
    echo "   You can also pass it in the request body."
    echo ""
fi

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║         GROQ NORMALIZER - END-TO-END TEST                        ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TEST 1: Get Empty Schema"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s $API_URL/schema | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TEST 2: Normalize Natural Language (Cardiovascular Patient)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Input: '55 year old male, 170cm, 85kg, BP 150/95, high cholesterol,"
echo "        smoker, no alcohol, sedentary lifestyle'"
echo ""

curl -s -X POST $API_URL/normalize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "55 year old male, 170cm tall, weighs 85kg, blood pressure 150/95, high cholesterol level 3, glucose normal, smoker, no alcohol, physically inactive"
  }' | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TEST 3: Normalize Natural Language (Diabetes Patient)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Input: '52 year old female, has hypertension and heart disease,"
echo "        former smoker, BMI 32.5, HbA1c 7.2, blood glucose 180'"
echo ""

curl -s -X POST $API_URL/normalize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient is a 52 year old female with hypertension and heart disease. She is a former smoker with BMI of 32.5, HbA1c level is 7.2, and blood glucose level is 180."
  }' | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TEST 4: Normalize + Validate (Shows what would route where)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

curl -s -X POST $API_URL/normalize/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "55 year old male, 170cm, 85kg, blood pressure 150 over 95, cholesterol level 3, normal glucose, smokes, no alcohol, inactive"
  }' | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TEST 5: Full Pipeline - Natural Language → Prediction"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Input: Complete cardiovascular patient description"
echo ""

curl -s -X POST $API_URL/predict/natural \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient is a 55 year old male, height 170 centimeters, weight 85 kilograms. Blood pressure reading is 150/95. Cholesterol is well above normal (level 3), glucose is normal (level 1). He is a current smoker, does not consume alcohol, and is physically inactive."
  }' | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TEST 6: Incomplete Data - Should show missing fields"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Input: Only age and gender provided (not enough for any model)"
echo ""

curl -s -X POST $API_URL/predict/natural \
  -H "Content-Type: application/json" \
  -d '{
    "text": "50 year old male patient"
  }' | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TEST 7: Diabetes Prediction via Natural Language"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

curl -s -X POST $API_URL/predict/natural \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Female patient, 52 years old. Has hypertension (yes) and heart disease (yes). Former smoker. BMI is 32.5, HbA1c level 7.2 percent, blood glucose level 180 mg/dL."
  }' | python3 -m json.tool

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    TESTS COMPLETE                                ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
