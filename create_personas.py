#!/usr/bin/env python3
"""
Create 10 Detailed Patient Personas
====================================
Generates realistic patient personas spanning the risk spectrum for:
- Diabetes (Type 2)
- Cardiovascular Disease

Each persona includes:
- Full demographics and social history
- Complete medical history (conditions, medications, allergies)
- Lifestyle factors (diet, exercise, smoking, alcohol)
- Family history
- Vital signs and lab results over time
- Encounter history
- AI model features for ML inference

Risk Levels (1-10):
1-2: Very High Risk (multiple comorbidities, poor control)
3-4: High Risk (significant risk factors)
5-6: Moderate Risk (some risk factors)
7-8: Low Risk (minimal risk factors)
9-10: Very Low Risk (healthy individuals)
"""

import mariadb
import os
import uuid
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import random

load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))

def get_db_connection():
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

# ============================================================================
# 10 DETAILED PATIENT PERSONAS
# ============================================================================

PERSONAS = [
    # ========== PERSONA 1: VERY HIGH RISK (Diabetes: 10/10, CVD: 10/10) ==========
    {
        "id": "persona-001-highrisk-both",
        "demographics": {
            "first_name": "Harold",
            "last_name": "Morrison",
            "middle_name": "Eugene",
            "birthdate": "1958-03-15",
            "gender": "M",
            "race": "White",
            "ethnicity": "Non-Hispanic",
            "marital_status": "Divorced",
            "address": "1847 Oak Street, Apt 3B",
            "city": "Detroit",
            "state": "Michigan",
            "zip": "48201",
            "income": 28000,
        },
        "narrative": """
        Harold is a 67-year-old divorced man living alone in a small apartment in Detroit. 
        He worked as a truck driver for 35 years before retiring on disability due to his 
        deteriorating health. He has poorly controlled Type 2 diabetes diagnosed 18 years ago, 
        along with coronary artery disease, previous MI (2019), CHF, and CKD Stage 3.
        
        Harold smokes 1 pack/day (45 pack-year history), rarely exercises due to shortness of 
        breath, and his diet consists mainly of fast food and processed meals. He often forgets 
        to take his medications and has difficulty affording them. His wife left him 10 years ago, 
        and he has limited social support. His father died of a heart attack at 52, and his 
        mother had diabetes and died from stroke complications.
        
        Chief complaints: Increasing fatigue, swollen ankles, shortness of breath on exertion,
        numbness in feet (diabetic neuropathy), and chest pressure when climbing stairs.
        """,
        "risk_scores": {"diabetes": 10, "cardiovascular": 10},
        "vitals": {
            "height_cm": 175,
            "weight_kg": 108,
            "bp_systolic": 158,
            "bp_diastolic": 94,
            "heart_rate": 88,
            "respiratory_rate": 20,
            "temperature": 37.0,
            "oxygen_saturation": 93,
        },
        "labs": {
            "hba1c": 9.8,
            "fasting_glucose": 218,
            "total_cholesterol": 267,
            "ldl": 178,
            "hdl": 32,
            "triglycerides": 285,
            "creatinine": 1.8,
            "egfr": 38,
            "bun": 32,
            "potassium": 5.2,
            "bnp": 890,
        },
        "conditions": [
            ("E11.65", "Type 2 diabetes with hyperglycemia", "2007-05-20", None),
            ("I25.10", "Coronary artery disease", "2015-08-12", None),
            ("I21.09", "Acute myocardial infarction", "2019-11-03", "2019-11-15"),
            ("I50.9", "Congestive heart failure", "2020-02-10", None),
            ("N18.3", "Chronic kidney disease stage 3", "2021-06-15", None),
            ("E78.5", "Hyperlipidemia", "2010-03-22", None),
            ("I10", "Essential hypertension", "2008-09-14", None),
            ("G62.9", "Diabetic peripheral neuropathy", "2018-04-08", None),
            ("H36.0", "Diabetic retinopathy", "2020-11-20", None),
            ("F32.1", "Major depressive disorder", "2021-03-15", None),
        ],
        "medications": [
            ("Metformin 1000mg", "314076", "twice daily"),
            ("Insulin glargine 40 units", "311040", "once daily at bedtime"),
            ("Lisinopril 20mg", "314077", "once daily"),
            ("Carvedilol 25mg", "200031", "twice daily"),
            ("Furosemide 40mg", "200801", "once daily"),
            ("Atorvastatin 80mg", "617311", "once daily"),
            ("Aspirin 81mg", "198466", "once daily"),
            ("Gabapentin 300mg", "310430", "three times daily"),
            ("Sertraline 50mg", "312938", "once daily"),
        ],
        "allergies": [
            ("Penicillin", "Severe rash", "allergy"),
            ("Sulfa drugs", "Hives", "allergy"),
        ],
        "lifestyle": {
            "smoking_status": "current",
            "smoking_pack_years": 45,
            "alcohol_use": "moderate",  # 2-3 beers/day
            "exercise_frequency": "never",
            "diet_quality": "poor",
            "sleep_hours": 5,
            "stress_level": "high",
        },
        "family_history": [
            ("Father", "Myocardial infarction", "Died at 52"),
            ("Mother", "Type 2 diabetes, Stroke", "Died at 68"),
            ("Brother", "Type 2 diabetes, Hypertension", "Living, age 70"),
        ],
        "social_history": {
            "employment": "Disabled/Retired",
            "education": "High school diploma",
            "living_situation": "Lives alone",
            "social_support": "Limited - estranged from family",
            "transportation": "Unreliable - depends on neighbors",
            "food_security": "Sometimes skips meals due to cost",
            "health_literacy": "Low",
        },
    },
    
    # ========== PERSONA 2: HIGH RISK (Diabetes: 8/10, CVD: 9/10) ==========
    {
        "id": "persona-002-highrisk-cvd",
        "demographics": {
            "first_name": "Margaret",
            "last_name": "Chen",
            "middle_name": "Lin",
            "birthdate": "1952-08-22",
            "gender": "F",
            "race": "Asian",
            "ethnicity": "Non-Hispanic",
            "marital_status": "Widowed",
            "address": "892 Maple Avenue",
            "city": "San Francisco",
            "state": "California",
            "zip": "94112",
            "income": 42000,
        },
        "narrative": """
        Margaret is a 73-year-old widowed Chinese-American woman. Her husband passed away 
        5 years ago from a stroke, which deeply affected her. She was a restaurant owner 
        for 40 years and now lives with her daughter's family but often feels like a burden.
        
        She has prediabetes trending toward diabetes, severe hypertension, atrial fibrillation,
        and peripheral artery disease. She had a TIA (mini-stroke) last year that scared her.
        Margaret never smoked but has been sedentary since closing the restaurant. She cooks
        traditional Chinese food but uses a lot of sodium. She takes her medications but 
        sometimes gets confused about the schedule.
        
        Chief complaints: Occasional palpitations, leg pain when walking more than one block,
        dizziness when standing up, and worry about having a stroke like her husband.
        """,
        "risk_scores": {"diabetes": 8, "cardiovascular": 9},
        "vitals": {
            "height_cm": 157,
            "weight_kg": 68,
            "bp_systolic": 168,
            "bp_diastolic": 88,
            "heart_rate": 92,  # irregular due to AFib
            "respiratory_rate": 18,
            "temperature": 36.8,
            "oxygen_saturation": 96,
        },
        "labs": {
            "hba1c": 6.3,
            "fasting_glucose": 118,
            "total_cholesterol": 234,
            "ldl": 145,
            "hdl": 42,
            "triglycerides": 235,
            "creatinine": 1.2,
            "egfr": 52,
            "inr": 2.4,
            "tsh": 3.2,
        },
        "conditions": [
            ("R73.03", "Prediabetes", "2020-04-15", None),
            ("I10", "Essential hypertension - severe", "2005-11-08", None),
            ("I48.91", "Atrial fibrillation", "2018-07-22", None),
            ("I73.9", "Peripheral artery disease", "2021-03-10", None),
            ("G45.9", "Transient ischemic attack", "2024-06-18", "2024-06-20"),
            ("E78.0", "Hypercholesterolemia", "2012-09-14", None),
            ("M81.0", "Osteoporosis", "2019-05-20", None),
            ("H52.4", "Presbyopia", "2015-03-12", None),
        ],
        "medications": [
            ("Metoprolol succinate 100mg", "866514", "once daily"),
            ("Lisinopril 40mg", "314077", "once daily"),
            ("Amlodipine 10mg", "308135", "once daily"),
            ("Warfarin 5mg", "855350", "once daily"),
            ("Atorvastatin 40mg", "617311", "once daily"),
            ("Metformin 500mg", "314076", "twice daily"),
            ("Alendronate 70mg", "824876", "once weekly"),
            ("Calcium + Vitamin D", "315965", "once daily"),
        ],
        "allergies": [
            ("Codeine", "Nausea and vomiting", "intolerance"),
        ],
        "lifestyle": {
            "smoking_status": "never",
            "smoking_pack_years": 0,
            "alcohol_use": "rare",
            "exercise_frequency": "rarely",
            "diet_quality": "fair",  # High sodium
            "sleep_hours": 6,
            "stress_level": "moderate",
        },
        "family_history": [
            ("Husband", "Stroke", "Died at 70"),
            ("Father", "Hypertension, Heart disease", "Died at 65"),
            ("Mother", "Type 2 diabetes", "Died at 82"),
        ],
        "social_history": {
            "employment": "Retired",
            "education": "Some college",
            "living_situation": "Lives with daughter's family",
            "social_support": "Good - close family",
            "transportation": "Depends on family",
            "food_security": "Adequate",
            "health_literacy": "Moderate",
        },
    },
    
    # ========== PERSONA 3: HIGH RISK (Diabetes: 9/10, CVD: 7/10) ==========
    {
        "id": "persona-003-highrisk-diabetes",
        "demographics": {
            "first_name": "Darnell",
            "last_name": "Washington",
            "middle_name": "Marcus",
            "birthdate": "1970-11-30",
            "gender": "M",
            "race": "Black",
            "ethnicity": "Non-Hispanic",
            "marital_status": "Married",
            "address": "3421 Martin Luther King Jr Blvd",
            "city": "Atlanta",
            "state": "Georgia",
            "zip": "30331",
            "income": 55000,
        },
        "narrative": """
        Darnell is a 55-year-old African-American man who works as a bus driver for the 
        Atlanta transit system. He was diagnosed with Type 2 diabetes 8 years ago but 
        has struggled with control due to his irregular work schedule and eating on the go.
        
        He is obese (BMI 38), has diabetic nephropathy developing, and sleep apnea that
        he hasn't been treating because he can't tolerate the CPAP machine. His blood pressure
        is elevated but not severely. He quit smoking 5 years ago (20 pack-year history)
        after a health scare. He tries to exercise on weekends but his feet hurt due to
        neuropathy. His wife is supportive and tries to cook healthy meals.
        
        Chief complaints: Frequent urination at night (4-5 times), blurry vision that comes 
        and goes, fatigue despite sleeping, and numbness/tingling in feet worse at night.
        """,
        "risk_scores": {"diabetes": 9, "cardiovascular": 7},
        "vitals": {
            "height_cm": 183,
            "weight_kg": 127,
            "bp_systolic": 142,
            "bp_diastolic": 88,
            "heart_rate": 78,
            "respiratory_rate": 18,
            "temperature": 37.1,
            "oxygen_saturation": 94,
        },
        "labs": {
            "hba1c": 9.2,
            "fasting_glucose": 198,
            "total_cholesterol": 212,
            "ldl": 128,
            "hdl": 38,
            "triglycerides": 230,
            "creatinine": 1.5,
            "egfr": 48,
            "urine_albumin": 180,  # mg/g - moderately increased
            "vitamin_d": 18,
        },
        "conditions": [
            ("E11.65", "Type 2 diabetes with hyperglycemia", "2017-03-14", None),
            ("E11.21", "Diabetic nephropathy", "2023-08-22", None),
            ("E11.42", "Diabetic polyneuropathy", "2021-05-10", None),
            ("E66.01", "Morbid obesity", "2015-09-08", None),
            ("G47.33", "Obstructive sleep apnea", "2020-11-15", None),
            ("I10", "Essential hypertension", "2018-02-20", None),
            ("E78.5", "Mixed hyperlipidemia", "2019-04-12", None),
            ("K21.0", "GERD", "2022-07-08", None),
        ],
        "medications": [
            ("Metformin 1000mg", "314076", "twice daily"),
            ("Semaglutide 1mg", "1991302", "once weekly"),
            ("Lisinopril 20mg", "314077", "once daily"),
            ("Amlodipine 5mg", "308135", "once daily"),
            ("Rosuvastatin 20mg", "859751", "once daily"),
            ("Gabapentin 300mg", "310430", "at bedtime"),
            ("Omeprazole 20mg", "198053", "once daily"),
            ("Vitamin D3 2000 IU", "315966", "once daily"),
        ],
        "allergies": [],
        "lifestyle": {
            "smoking_status": "former",
            "smoking_pack_years": 20,
            "alcohol_use": "occasional",  # 2-3 drinks/week
            "exercise_frequency": "rarely",
            "diet_quality": "fair",
            "sleep_hours": 5,  # Poor due to apnea
            "stress_level": "moderate",
        },
        "family_history": [
            ("Mother", "Type 2 diabetes, Hypertension", "Living, age 78"),
            ("Father", "Type 2 diabetes, Stroke", "Died at 62"),
            ("Sister", "Type 2 diabetes", "Living, age 52"),
        ],
        "social_history": {
            "employment": "Bus driver - shift work",
            "education": "High school diploma",
            "living_situation": "Lives with wife",
            "social_support": "Good - supportive wife",
            "transportation": "Has own vehicle",
            "food_security": "Adequate",
            "health_literacy": "Moderate",
        },
    },
    
    # ========== PERSONA 4: MODERATE-HIGH RISK (Diabetes: 7/10, CVD: 6/10) ==========
    {
        "id": "persona-004-moderate-high",
        "demographics": {
            "first_name": "Patricia",
            "last_name": "Rodriguez",
            "middle_name": "Maria",
            "birthdate": "1965-04-18",
            "gender": "F",
            "race": "White",
            "ethnicity": "Hispanic",
            "marital_status": "Married",
            "address": "2156 Sunset Boulevard",
            "city": "Phoenix",
            "state": "Arizona",
            "zip": "85004",
            "income": 68000,
        },
        "narrative": """
        Patricia is a 60-year-old Hispanic woman who works as an office manager. She was
        diagnosed with Type 2 diabetes 5 years ago after gestational diabetes with her 
        last pregnancy 25 years ago. She has been trying to manage with diet and metformin
        but her A1c has been creeping up.
        
        She carries her weight around her middle ("apple shape"), has hypertension, and
        elevated cholesterol. She never smoked, drinks wine occasionally, and tries to walk
        but the Phoenix heat limits outdoor activity. She is the primary caregiver for her
        elderly mother who has dementia, which adds significant stress to her life.
        
        Chief complaints: Gradual weight gain despite efforts, stress eating, occasional
        headaches, and worry about developing complications like her mother did.
        """,
        "risk_scores": {"diabetes": 7, "cardiovascular": 6},
        "vitals": {
            "height_cm": 162,
            "weight_kg": 82,
            "bp_systolic": 138,
            "bp_diastolic": 86,
            "heart_rate": 76,
            "respiratory_rate": 16,
            "temperature": 36.9,
            "oxygen_saturation": 97,
        },
        "labs": {
            "hba1c": 7.8,
            "fasting_glucose": 156,
            "total_cholesterol": 218,
            "ldl": 132,
            "hdl": 48,
            "triglycerides": 190,
            "creatinine": 0.9,
            "egfr": 78,
            "alt": 42,
            "ast": 38,
        },
        "conditions": [
            ("E11.9", "Type 2 diabetes without complications", "2020-06-15", None),
            ("O24.419", "Gestational diabetes - historical", "1999-08-20", "1999-11-15"),
            ("I10", "Essential hypertension", "2018-03-22", None),
            ("E78.0", "Hypercholesterolemia", "2019-09-14", None),
            ("E66.9", "Obesity", "2017-05-10", None),
            ("K76.0", "Fatty liver disease", "2022-04-18", None),
            ("F41.1", "Generalized anxiety disorder", "2023-01-20", None),
            ("M54.5", "Low back pain", "2021-08-12", None),
        ],
        "medications": [
            ("Metformin 1000mg", "314076", "twice daily"),
            ("Lisinopril 10mg", "314077", "once daily"),
            ("Atorvastatin 20mg", "617311", "once daily"),
            ("Escitalopram 10mg", "352741", "once daily"),
            ("Ibuprofen 400mg", "197805", "as needed"),
        ],
        "allergies": [
            ("Latex", "Contact dermatitis", "allergy"),
        ],
        "lifestyle": {
            "smoking_status": "never",
            "smoking_pack_years": 0,
            "alcohol_use": "occasional",
            "exercise_frequency": "sometimes",
            "diet_quality": "fair",
            "sleep_hours": 6,
            "stress_level": "high",  # Caregiver stress
        },
        "family_history": [
            ("Mother", "Type 2 diabetes, Dementia", "Living, age 85"),
            ("Father", "Heart disease", "Died at 70"),
            ("Sister", "Prediabetes, Obesity", "Living, age 57"),
        ],
        "social_history": {
            "employment": "Office manager - sedentary job",
            "education": "Associate degree",
            "living_situation": "Lives with husband and mother",
            "social_support": "Good - but stressed as caregiver",
            "transportation": "Has own vehicle",
            "food_security": "Adequate",
            "health_literacy": "Good",
        },
    },
    
    # ========== PERSONA 5: MODERATE RISK (Diabetes: 6/10, CVD: 5/10) ==========
    {
        "id": "persona-005-moderate",
        "demographics": {
            "first_name": "Robert",
            "last_name": "O'Brien",
            "middle_name": "James",
            "birthdate": "1972-07-04",
            "gender": "M",
            "race": "White",
            "ethnicity": "Non-Hispanic",
            "marital_status": "Married",
            "address": "789 Elm Street",
            "city": "Boston",
            "state": "Massachusetts",
            "zip": "02108",
            "income": 95000,
        },
        "narrative": """
        Robert is a 53-year-old Irish-American man who works as a construction project
        manager. He was recently diagnosed with prediabetes during a routine physical,
        which surprised him. He has borderline high blood pressure and cholesterol.
        
        He quit smoking 10 years ago, drinks beer socially on weekends (maybe too much),
        and considers himself active because of his job, though it's more supervisory now.
        He's carrying an extra 30 pounds, mostly in his belly. His doctor warned him that
        he's heading toward diabetes if he doesn't make changes.
        
        Chief complaints: None acute - came in for follow-up after abnormal labs. Mentions
        occasional heartburn and knee pain from old sports injury. Concerned about diabetes
        because his father has it and lost a toe.
        """,
        "risk_scores": {"diabetes": 6, "cardiovascular": 5},
        "vitals": {
            "height_cm": 180,
            "weight_kg": 98,
            "bp_systolic": 134,
            "bp_diastolic": 84,
            "heart_rate": 72,
            "respiratory_rate": 16,
            "temperature": 36.8,
            "oxygen_saturation": 98,
        },
        "labs": {
            "hba1c": 6.1,
            "fasting_glucose": 112,
            "total_cholesterol": 228,
            "ldl": 142,
            "hdl": 44,
            "triglycerides": 210,
            "creatinine": 1.0,
            "egfr": 88,
            "alt": 48,
            "uric_acid": 7.8,
        },
        "conditions": [
            ("R73.03", "Prediabetes", "2025-10-15", None),
            ("R03.0", "Elevated blood pressure reading", "2024-06-20", None),
            ("E78.5", "Hyperlipidemia", "2024-06-20", None),
            ("E66.9", "Overweight", "2020-03-15", None),
            ("K21.0", "GERD", "2022-09-10", None),
            ("M17.11", "Primary osteoarthritis, right knee", "2019-05-22", None),
            ("F10.10", "Alcohol use, mild", "2025-01-10", None),
        ],
        "medications": [
            ("Omeprazole 20mg", "198053", "once daily"),
            ("Naproxen 500mg", "198012", "as needed"),
            ("Fish oil 1000mg", "315966", "once daily"),
        ],
        "allergies": [],
        "lifestyle": {
            "smoking_status": "former",
            "smoking_pack_years": 15,
            "alcohol_use": "moderate",  # 8-10 drinks/week
            "exercise_frequency": "sometimes",
            "diet_quality": "fair",
            "sleep_hours": 7,
            "stress_level": "moderate",
        },
        "family_history": [
            ("Father", "Type 2 diabetes, PAD", "Living, age 78"),
            ("Mother", "Hypertension", "Living, age 76"),
            ("Brother", "Prediabetes", "Living, age 50"),
        ],
        "social_history": {
            "employment": "Construction manager",
            "education": "Bachelor's degree",
            "living_situation": "Lives with wife and teenage children",
            "social_support": "Good",
            "transportation": "Has own vehicle",
            "food_security": "Adequate",
            "health_literacy": "Good",
        },
    },
    
    # ========== PERSONA 6: MODERATE-LOW RISK (Diabetes: 5/10, CVD: 4/10) ==========
    {
        "id": "persona-006-moderate-low",
        "demographics": {
            "first_name": "Aisha",
            "last_name": "Patel",
            "middle_name": "Priya",
            "birthdate": "1978-12-10",
            "gender": "F",
            "race": "Asian",
            "ethnicity": "Non-Hispanic",
            "marital_status": "Married",
            "address": "4521 Technology Drive",
            "city": "Seattle",
            "state": "Washington",
            "zip": "98109",
            "income": 145000,
        },
        "narrative": """
        Aisha is a 47-year-old Indian-American woman who works as a software engineer
        at a tech company. She has a family history of diabetes (both parents) and was
        told she has metabolic syndrome - slightly elevated glucose, blood pressure,
        and triglycerides with low HDL.
        
        She doesn't smoke, rarely drinks, but her job is sedentary and stressful with
        long hours. She's been trying to lose weight and started taking metformin 
        preventively. She does yoga twice a week and walks when weather permits.
        She's health-conscious and well-informed but struggles with consistency.
        
        Chief complaints: Wants to discuss her metabolic syndrome and diabetes prevention.
        Mentions fatigue that she attributes to work stress and occasional hot flashes
        (perimenopause). Asking about genetic testing for diabetes risk.
        """,
        "risk_scores": {"diabetes": 5, "cardiovascular": 4},
        "vitals": {
            "height_cm": 165,
            "weight_kg": 72,
            "bp_systolic": 128,
            "bp_diastolic": 82,
            "heart_rate": 70,
            "respiratory_rate": 14,
            "temperature": 36.7,
            "oxygen_saturation": 99,
        },
        "labs": {
            "hba1c": 5.9,
            "fasting_glucose": 104,
            "total_cholesterol": 198,
            "ldl": 118,
            "hdl": 46,
            "triglycerides": 170,
            "creatinine": 0.8,
            "egfr": 98,
            "vitamin_d": 28,
            "tsh": 2.8,
            "fsh": 35,
        },
        "conditions": [
            ("E88.81", "Metabolic syndrome", "2024-03-15", None),
            ("R73.09", "Abnormal glucose", "2024-03-15", None),
            ("E78.5", "Hyperlipidemia", "2024-03-15", None),
            ("N95.1", "Perimenopausal symptoms", "2025-06-10", None),
            ("D50.9", "Iron deficiency anemia - resolved", "2023-01-15", "2023-06-20"),
            ("M54.2", "Cervicalgia", "2024-08-05", None),
        ],
        "medications": [
            ("Metformin 500mg", "314076", "once daily"),
            ("Iron supplement", "315949", "once daily"),
            ("Vitamin D3 1000 IU", "315966", "once daily"),
        ],
        "allergies": [
            ("Shellfish", "Throat swelling", "allergy"),
        ],
        "lifestyle": {
            "smoking_status": "never",
            "smoking_pack_years": 0,
            "alcohol_use": "rare",
            "exercise_frequency": "sometimes",
            "diet_quality": "good",
            "sleep_hours": 6,
            "stress_level": "high",
        },
        "family_history": [
            ("Father", "Type 2 diabetes", "Living, age 75"),
            ("Mother", "Type 2 diabetes, Hypertension", "Living, age 72"),
            ("Brother", "Healthy", "Living, age 44"),
        ],
        "social_history": {
            "employment": "Software engineer - sedentary",
            "education": "Master's degree",
            "living_situation": "Lives with husband and 2 children",
            "social_support": "Good",
            "transportation": "Has own vehicle",
            "food_security": "Adequate",
            "health_literacy": "Excellent",
        },
    },
    
    # ========== PERSONA 7: LOW RISK (Diabetes: 4/10, CVD: 3/10) ==========
    {
        "id": "persona-007-low",
        "demographics": {
            "first_name": "Michael",
            "last_name": "Johansson",
            "middle_name": "Erik",
            "birthdate": "1985-02-28",
            "gender": "M",
            "race": "White",
            "ethnicity": "Non-Hispanic",
            "marital_status": "Single",
            "address": "1234 Nordic Way",
            "city": "Minneapolis",
            "state": "Minnesota",
            "zip": "55401",
            "income": 78000,
        },
        "narrative": """
        Michael is a 40-year-old Swedish-American man who works as a physical therapist.
        He's generally healthy but came in because his father was recently diagnosed
        with Type 2 diabetes, which prompted him to get checked. His labs show he's
        in the normal range but his fasting glucose is trending toward the upper limit.
        
        He exercises regularly (runs, cycles, lifts weights), eats a reasonably healthy
        diet, never smoked, and drinks socially. He's slightly overweight despite being
        active. His blood pressure and cholesterol are normal. He's motivated to stay
        healthy and prevent what happened to his father.
        
        Chief complaints: No acute issues - wellness visit prompted by family history.
        Occasional lower back strain from work. Wants guidance on diabetes prevention.
        """,
        "risk_scores": {"diabetes": 4, "cardiovascular": 3},
        "vitals": {
            "height_cm": 188,
            "weight_kg": 92,
            "bp_systolic": 122,
            "bp_diastolic": 78,
            "heart_rate": 64,
            "respiratory_rate": 14,
            "temperature": 36.8,
            "oxygen_saturation": 99,
        },
        "labs": {
            "hba1c": 5.6,
            "fasting_glucose": 98,
            "total_cholesterol": 192,
            "ldl": 110,
            "hdl": 56,
            "triglycerides": 130,
            "creatinine": 1.0,
            "egfr": 95,
            "vitamin_d": 42,
        },
        "conditions": [
            ("Z83.3", "Family history of diabetes", "2025-11-01", None),
            ("M54.5", "Low back pain", "2024-03-10", None),
            ("J30.1", "Allergic rhinitis", "2015-04-15", None),
        ],
        "medications": [
            ("Cetirizine 10mg", "998765", "as needed"),
            ("Ibuprofen 400mg", "197805", "as needed"),
        ],
        "allergies": [
            ("Pollen", "Seasonal allergies", "environmental"),
        ],
        "lifestyle": {
            "smoking_status": "never",
            "smoking_pack_years": 0,
            "alcohol_use": "occasional",
            "exercise_frequency": "regularly",
            "diet_quality": "good",
            "sleep_hours": 7,
            "stress_level": "low",
        },
        "family_history": [
            ("Father", "Type 2 diabetes - new diagnosis", "Living, age 68"),
            ("Mother", "Healthy", "Living, age 65"),
            ("Sister", "Healthy", "Living, age 37"),
        ],
        "social_history": {
            "employment": "Physical therapist - active job",
            "education": "Doctorate (DPT)",
            "living_situation": "Lives alone",
            "social_support": "Good - active social life",
            "transportation": "Has own vehicle, bikes to work",
            "food_security": "Adequate",
            "health_literacy": "Excellent",
        },
    },
    
    # ========== PERSONA 8: LOW RISK (Diabetes: 3/10, CVD: 4/10) ==========
    {
        "id": "persona-008-low-cvd",
        "demographics": {
            "first_name": "Sandra",
            "last_name": "Williams",
            "middle_name": "Grace",
            "birthdate": "1968-09-15",
            "gender": "F",
            "race": "Black",
            "ethnicity": "Non-Hispanic",
            "marital_status": "Divorced",
            "address": "567 Heritage Lane",
            "city": "Nashville",
            "state": "Tennessee",
            "zip": "37203",
            "income": 62000,
        },
        "narrative": """
        Sandra is a 57-year-old African-American woman who works as a school principal.
        She has mild hypertension that's well-controlled on medication and mildly elevated
        cholesterol. Her glucose levels are normal. She has a family history of heart
        disease but has been proactive about her health.
        
        She exercises by walking 30 minutes most days, watches her salt intake, and
        maintains a healthy weight. She never smoked and rarely drinks. Her main health
        concerns are managing stress from her demanding job and staying healthy as she
        approaches retirement.
        
        Chief complaints: Routine follow-up for hypertension. Mentions occasional tension
        headaches and wants to discuss stress management strategies.
        """,
        "risk_scores": {"diabetes": 3, "cardiovascular": 4},
        "vitals": {
            "height_cm": 168,
            "weight_kg": 70,
            "bp_systolic": 126,
            "bp_diastolic": 80,
            "heart_rate": 72,
            "respiratory_rate": 14,
            "temperature": 36.9,
            "oxygen_saturation": 98,
        },
        "labs": {
            "hba1c": 5.4,
            "fasting_glucose": 92,
            "total_cholesterol": 208,
            "ldl": 125,
            "hdl": 62,
            "triglycerides": 105,
            "creatinine": 0.9,
            "egfr": 82,
            "vitamin_d": 35,
        },
        "conditions": [
            ("I10", "Essential hypertension - controlled", "2018-05-22", None),
            ("E78.0", "Hypercholesterolemia - mild", "2020-09-14", None),
            ("G43.909", "Migraine, unspecified", "2015-03-10", None),
            ("N95.1", "Menopausal symptoms", "2022-08-15", None),
        ],
        "medications": [
            ("Lisinopril 10mg", "314077", "once daily"),
            ("Rosuvastatin 10mg", "859751", "once daily"),
            ("Sumatriptan 50mg", "828088", "as needed for migraine"),
        ],
        "allergies": [],
        "lifestyle": {
            "smoking_status": "never",
            "smoking_pack_years": 0,
            "alcohol_use": "rare",
            "exercise_frequency": "regularly",
            "diet_quality": "good",
            "sleep_hours": 7,
            "stress_level": "moderate",
        },
        "family_history": [
            ("Father", "Heart disease, Hypertension", "Died at 72"),
            ("Mother", "Hypertension", "Living, age 80"),
            ("Brother", "Hypertension", "Living, age 60"),
        ],
        "social_history": {
            "employment": "School principal - stressful",
            "education": "Master's degree",
            "living_situation": "Lives alone",
            "social_support": "Good - church community",
            "transportation": "Has own vehicle",
            "food_security": "Adequate",
            "health_literacy": "Excellent",
        },
    },
    
    # ========== PERSONA 9: VERY LOW RISK (Diabetes: 2/10, CVD: 2/10) ==========
    {
        "id": "persona-009-very-low",
        "demographics": {
            "first_name": "Jennifer",
            "last_name": "Park",
            "middle_name": "Sun",
            "birthdate": "1990-06-20",
            "gender": "F",
            "race": "Asian",
            "ethnicity": "Non-Hispanic",
            "marital_status": "Married",
            "address": "8901 Wellness Court",
            "city": "Denver",
            "state": "Colorado",
            "zip": "80202",
            "income": 112000,
        },
        "narrative": """
        Jennifer is a 35-year-old Korean-American woman who works as a dietitian at a
        hospital. She practices what she preaches - eating a balanced diet, exercising
        regularly (yoga, hiking, swimming), and maintaining a healthy weight. She never
        smoked and drinks minimally.
        
        She has no chronic conditions and her family history is unremarkable for
        cardiometabolic diseases. She came in for her annual wellness exam. All her
        vitals and labs are optimal. She's health-conscious and asks thoughtful questions
        about preventive care.
        
        Chief complaints: None - annual wellness exam. Interested in discussing optimal
        nutrition and considering starting a family soon.
        """,
        "risk_scores": {"diabetes": 2, "cardiovascular": 2},
        "vitals": {
            "height_cm": 163,
            "weight_kg": 58,
            "bp_systolic": 112,
            "bp_diastolic": 72,
            "heart_rate": 62,
            "respiratory_rate": 14,
            "temperature": 36.6,
            "oxygen_saturation": 99,
        },
        "labs": {
            "hba1c": 5.1,
            "fasting_glucose": 84,
            "total_cholesterol": 172,
            "ldl": 92,
            "hdl": 68,
            "triglycerides": 60,
            "creatinine": 0.7,
            "egfr": 112,
            "vitamin_d": 48,
            "ferritin": 65,
        },
        "conditions": [
            ("Z00.00", "Encounter for general exam", "2026-01-15", "2026-01-15"),
            ("J30.1", "Allergic rhinitis, seasonal", "2010-05-20", None),
        ],
        "medications": [
            ("Prenatal vitamins", "315949", "once daily"),
            ("Loratadine 10mg", "311372", "as needed"),
        ],
        "allergies": [
            ("Cats", "Sneezing, watery eyes", "environmental"),
        ],
        "lifestyle": {
            "smoking_status": "never",
            "smoking_pack_years": 0,
            "alcohol_use": "rare",
            "exercise_frequency": "daily",
            "diet_quality": "excellent",
            "sleep_hours": 8,
            "stress_level": "low",
        },
        "family_history": [
            ("Father", "Healthy", "Living, age 62"),
            ("Mother", "Healthy", "Living, age 60"),
            ("Brother", "Healthy", "Living, age 32"),
        ],
        "social_history": {
            "employment": "Hospital dietitian",
            "education": "Master's degree",
            "living_situation": "Lives with husband",
            "social_support": "Excellent",
            "transportation": "Has own vehicle, walks/bikes often",
            "food_security": "Adequate",
            "health_literacy": "Excellent",
        },
    },
    
    # ========== PERSONA 10: VERY LOW RISK (Diabetes: 1/10, CVD: 1/10) ==========
    {
        "id": "persona-010-optimal",
        "demographics": {
            "first_name": "David",
            "last_name": "Nakamura",
            "middle_name": "Kenji",
            "birthdate": "1995-01-08",
            "gender": "M",
            "race": "Asian",
            "ethnicity": "Non-Hispanic",
            "marital_status": "Single",
            "address": "1500 Fitness Boulevard",
            "city": "San Diego",
            "state": "California",
            "zip": "92101",
            "income": 85000,
        },
        "narrative": """
        David is a 31-year-old Japanese-American man who works as a fitness instructor
        and personal trainer. He is in excellent physical condition, exercises daily
        (weight training, cardio, martial arts), and follows a disciplined nutrition plan.
        
        He has never smoked, doesn't drink alcohol, and has optimal blood pressure,
        cholesterol, and glucose levels. His family has no history of diabetes or heart
        disease. He came in for a sports physical for a triathlon he's training for.
        
        Chief complaints: None - sports physical. Minor questions about optimizing
        athletic performance and recovery. Interested in tracking his metabolic health.
        """,
        "risk_scores": {"diabetes": 1, "cardiovascular": 1},
        "vitals": {
            "height_cm": 178,
            "weight_kg": 75,
            "bp_systolic": 108,
            "bp_diastolic": 68,
            "heart_rate": 52,  # Athletic bradycardia
            "respiratory_rate": 12,
            "temperature": 36.6,
            "oxygen_saturation": 100,
        },
        "labs": {
            "hba1c": 4.9,
            "fasting_glucose": 78,
            "total_cholesterol": 158,
            "ldl": 82,
            "hdl": 72,
            "triglycerides": 55,
            "creatinine": 1.0,
            "egfr": 108,
            "vitamin_d": 55,
            "testosterone": 650,
        },
        "conditions": [
            ("Z02.5", "Sports physical exam", "2026-02-01", "2026-02-01"),
        ],
        "medications": [
            ("Multivitamin", "315949", "once daily"),
            ("Protein supplement", "999999", "post-workout"),
        ],
        "allergies": [],
        "lifestyle": {
            "smoking_status": "never",
            "smoking_pack_years": 0,
            "alcohol_use": "never",
            "exercise_frequency": "daily",
            "diet_quality": "excellent",
            "sleep_hours": 8,
            "stress_level": "low",
        },
        "family_history": [
            ("Father", "Healthy", "Living, age 58"),
            ("Mother", "Healthy", "Living, age 55"),
            ("Sister", "Healthy", "Living, age 28"),
        ],
        "social_history": {
            "employment": "Fitness instructor/Personal trainer",
            "education": "Bachelor's degree",
            "living_situation": "Lives with roommate",
            "social_support": "Excellent",
            "transportation": "Bikes everywhere",
            "food_security": "Adequate",
            "health_literacy": "Excellent",
        },
    },
]


def calculate_age(birthdate_str):
    """Calculate age from birthdate string"""
    birth = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
    today = date.today()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def insert_persona_to_mariadb(persona):
    """Insert a single persona into MariaDB with all related data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    synthea_id = persona["id"]
    demo = persona["demographics"]
    vitals = persona["vitals"]
    labs = persona["labs"]
    
    print(f"\n{'='*60}")
    print(f"📋 Inserting: {demo['first_name']} {demo['last_name']}")
    print(f"   Risk Scores - Diabetes: {persona['risk_scores']['diabetes']}/10, CVD: {persona['risk_scores']['cardiovascular']}/10")
    print(f"{'='*60}")
    
    try:
        # 1. Insert Patient
        print("   👤 Creating patient record...", end=" ")
        cursor.execute("""
            INSERT INTO Synthea_Patient (
                synthea_id, first_name, middle_name, last_name, 
                birthdate, gender, race, ethnicity, marital_status,
                address, city, state, zip, income
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                first_name = VALUES(first_name),
                last_name = VALUES(last_name),
                birthdate = VALUES(birthdate)
        """, (
            synthea_id, demo['first_name'], demo.get('middle_name'), demo['last_name'],
            demo['birthdate'], demo['gender'], demo.get('race'), demo.get('ethnicity'),
            demo.get('marital_status'), demo.get('address'), demo.get('city'),
            demo.get('state'), demo.get('zip'), demo.get('income')
        ))
        print("✅")
        
        # 2. Insert Conditions
        print(f"   🩺 Adding {len(persona['conditions'])} conditions...", end=" ")
        for code, desc, start_date, end_date in persona['conditions']:
            is_active = 1 if end_date is None else 0
            cursor.execute("""
                INSERT INTO Synthea_Condition (
                    synthea_patient_id, code, description, start_date, stop_date, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (synthea_id, code, desc, start_date, end_date, is_active))
        print("✅")
        
        # 3. Insert Medications
        print(f"   💊 Adding {len(persona['medications'])} medications...", end=" ")
        for med_name, code, dosage in persona['medications']:
            cursor.execute("""
                INSERT INTO Synthea_Medication (
                    synthea_patient_id, code, description, start_datetime, is_active
                ) VALUES (%s, %s, %s, %s, %s)
            """, (synthea_id, code, f"{med_name} - {dosage}", datetime.now(), 1))
        print("✅")
        
        # 4. Insert Allergies
        if persona['allergies']:
            print(f"   🤧 Adding {len(persona['allergies'])} allergies...", end=" ")
            for allergen, reaction, allergy_type in persona['allergies']:
                cursor.execute("""
                    INSERT INTO Synthea_Allergy (
                        synthea_patient_id, code, description, start_date, allergy_type, reaction1_description
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (synthea_id, allergen[:20], allergen, date.today().isoformat(), allergy_type, reaction))
            print("✅")
        
        # 5. Insert Observations (Vitals and Labs)
        print("   📊 Adding vital signs and lab results...", end=" ")
        obs_date = datetime.now()
        
        # LOINC codes for vitals
        vital_codes = {
            'height_cm': ('8302-2', 'cm'),
            'weight_kg': ('29463-7', 'kg'),
            'bp_systolic': ('8480-6', 'mmHg'),
            'bp_diastolic': ('8462-4', 'mmHg'),
            'heart_rate': ('8867-4', '/min'),
            'respiratory_rate': ('9279-1', '/min'),
            'temperature': ('8310-5', 'Cel'),
            'oxygen_saturation': ('2708-6', '%'),
        }
        
        for vital_name, value in vitals.items():
            if vital_name in vital_codes:
                code, unit = vital_codes[vital_name]
                cursor.execute("""
                    INSERT INTO Synthea_Observation (
                        synthea_patient_id, observation_date, code, description, value, units, category
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (synthea_id, obs_date, code, vital_name.replace('_', ' ').title(), str(value), unit, 'vital-signs'))
        
        # Lab codes
        lab_codes = {
            'hba1c': ('4548-4', '%'),
            'fasting_glucose': ('1558-6', 'mg/dL'),
            'total_cholesterol': ('2093-3', 'mg/dL'),
            'ldl': ('2089-1', 'mg/dL'),
            'hdl': ('2085-9', 'mg/dL'),
            'triglycerides': ('2571-8', 'mg/dL'),
            'creatinine': ('2160-0', 'mg/dL'),
            'egfr': ('33914-3', 'mL/min/1.73m2'),
            'vitamin_d': ('1989-3', 'ng/mL'),
            'alt': ('1742-6', 'U/L'),
            'ast': ('1920-8', 'U/L'),
            'bun': ('3094-0', 'mg/dL'),
            'potassium': ('2823-3', 'mEq/L'),
            'bnp': ('30934-4', 'pg/mL'),
            'inr': ('6301-6', '{ratio}'),
            'tsh': ('3016-3', 'mIU/L'),
            'uric_acid': ('3084-1', 'mg/dL'),
            'fsh': ('15067-2', 'mIU/mL'),
            'ferritin': ('2276-4', 'ng/mL'),
            'testosterone': ('2986-8', 'ng/dL'),
            'urine_albumin': ('14959-1', 'mg/g'),
        }
        
        for lab_name, value in labs.items():
            if lab_name in lab_codes:
                code, unit = lab_codes[lab_name]
                cursor.execute("""
                    INSERT INTO Synthea_Observation (
                        synthea_patient_id, observation_date, code, description, value, units, category
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (synthea_id, obs_date, code, lab_name.replace('_', ' ').title(), str(value), unit, 'laboratory'))
        print("✅")
        
        # 6. Insert AI Features
        print("   🤖 Creating AI feature set...", end=" ")
        age = calculate_age(demo['birthdate'])
        gender_numeric = 1 if demo['gender'] == 'F' else 2
        
        # Calculate BMI
        height_m = vitals['height_cm'] / 100
        bmi = vitals['weight_kg'] / (height_m * height_m)
        
        # Determine condition flags
        conditions_text = ' '.join([c[1].lower() for c in persona['conditions']])
        has_hypertension = 1 if 'hypertension' in conditions_text else 0
        has_heart_disease = 1 if any(x in conditions_text for x in ['heart', 'cardiac', 'coronary', 'myocardial', 'chf']) else 0
        
        # Smoking status
        lifestyle = persona['lifestyle']
        is_smoker = 1 if lifestyle['smoking_status'] == 'current' else 0
        smoking_history = lifestyle['smoking_status']
        
        # Alcohol use
        alcohol_use = 1 if lifestyle['alcohol_use'] in ['moderate', 'heavy'] else 0
        
        # Physical activity
        physical_activity = 1 if lifestyle['exercise_frequency'] in ['regularly', 'daily'] else 0
        
        # Cholesterol level (1=normal, 2=above, 3=well above)
        chol = labs.get('total_cholesterol', 180)
        cholesterol_level = 3 if chol >= 240 else (2 if chol >= 200 else 1)
        
        # Glucose level
        gluc = labs.get('fasting_glucose', 90)
        glucose_level = 3 if gluc >= 126 else (2 if gluc >= 100 else 1)
        
        cursor.execute("""
            INSERT INTO Patient_AI_Features (
                synthea_patient_id, age_years, gender_numeric,
                height_cm, weight_kg, bmi,
                bp_systolic, bp_diastolic, cholesterol_level, glucose_level,
                is_smoker, alcohol_use, physical_activity,
                has_hypertension, has_heart_disease,
                smoking_history, hba1c_level, blood_glucose_fasting
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                age_years = VALUES(age_years),
                bmi = VALUES(bmi),
                bp_systolic = VALUES(bp_systolic),
                hba1c_level = VALUES(hba1c_level)
        """, (
            synthea_id, age, gender_numeric,
            vitals['height_cm'], vitals['weight_kg'], round(bmi, 2),
            vitals['bp_systolic'], vitals['bp_diastolic'], cholesterol_level, glucose_level,
            is_smoker, alcohol_use, physical_activity,
            has_hypertension, has_heart_disease,
            smoking_history, labs.get('hba1c'), labs.get('fasting_glucose')
        ))
        print("✅")
        
        # 7. Create an encounter for this visit
        print("   📅 Creating encounter record...", end=" ")
        encounter_id = f"enc-{synthea_id}-{date.today().isoformat()}"
        cursor.execute("""
            INSERT INTO Synthea_Encounter (
                synthea_id, synthea_patient_id, encounter_class, code, 
                description, start_datetime, stop_datetime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            encounter_id, synthea_id, 'outpatient', '185349003',
            'Encounter for check up', datetime.now(), datetime.now() + timedelta(hours=1)
        ))
        print("✅")
        
        conn.commit()
        print(f"   ✅ Successfully inserted {demo['first_name']} {demo['last_name']}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n   ❌ Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    return synthea_id


def sync_persona_to_neo4j(persona):
    """Sync a persona to Neo4j knowledge graph"""
    from neo4j import GraphDatabase
    
    NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
    AURA_USER = os.getenv('AURA_USER', 'neo4j')
    AURA_PASSWORD = os.getenv('AURA_PASSWORD')
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(AURA_USER, AURA_PASSWORD))
    
    synthea_id = persona["id"]
    demo = persona["demographics"]
    vitals = persona["vitals"]
    labs = persona["labs"]
    risk_scores = persona["risk_scores"]
    
    print(f"   🔗 Syncing to Neo4j Knowledge Graph...", end=" ")
    
    try:
        with driver.session() as session:
            age = calculate_age(demo['birthdate'])
            height_m = vitals['height_cm'] / 100
            bmi = vitals['weight_kg'] / (height_m * height_m)
            
            # Create Patient/Person node with rich properties
            session.run("""
                MERGE (p:Person:Patient {synthea_id: $synthea_id})
                SET p.first_name = $first_name,
                    p.last_name = $last_name,
                    p.full_name = $first_name + ' ' + $last_name,
                    p.birthdate = $birthdate,
                    p.age = $age,
                    p.gender = $gender,
                    p.race = $race,
                    p.ethnicity = $ethnicity,
                    p.city = $city,
                    p.state = $state,
                    p.narrative = $narrative,
                    p.diabetes_risk = $diabetes_risk,
                    p.cvd_risk = $cvd_risk,
                    p.is_persona = true
            """, {
                'synthea_id': synthea_id,
                'first_name': demo['first_name'],
                'last_name': demo['last_name'],
                'birthdate': demo['birthdate'],
                'age': age,
                'gender': demo['gender'],
                'race': demo.get('race'),
                'ethnicity': demo.get('ethnicity'),
                'city': demo.get('city'),
                'state': demo.get('state'),
                'narrative': persona['narrative'].strip(),
                'diabetes_risk': risk_scores['diabetes'],
                'cvd_risk': risk_scores['cardiovascular'],
            })
            
            # Create AI Feature Set node
            session.run("""
                MATCH (p:Person {synthea_id: $synthea_id})
                MERGE (ai:AIFeatureSet {patient_id: $synthea_id})
                SET ai.age = $age,
                    ai.gender = $gender,
                    ai.height_cm = $height,
                    ai.weight_kg = $weight,
                    ai.bmi = $bmi,
                    ai.bp_systolic = $bp_sys,
                    ai.bp_diastolic = $bp_dia,
                    ai.heart_rate = $hr,
                    ai.hba1c = $hba1c,
                    ai.fasting_glucose = $glucose,
                    ai.total_cholesterol = $chol,
                    ai.ldl = $ldl,
                    ai.hdl = $hdl,
                    ai.triglycerides = $trig,
                    ai.smoking_status = $smoking,
                    ai.diabetes_risk_score = $diabetes_risk,
                    ai.cvd_risk_score = $cvd_risk
                MERGE (p)-[:HAS_AI_FEATURES]->(ai)
            """, {
                'synthea_id': synthea_id,
                'age': age,
                'gender': demo['gender'],
                'height': vitals['height_cm'],
                'weight': vitals['weight_kg'],
                'bmi': round(bmi, 2),
                'bp_sys': vitals['bp_systolic'],
                'bp_dia': vitals['bp_diastolic'],
                'hr': vitals['heart_rate'],
                'hba1c': labs.get('hba1c'),
                'glucose': labs.get('fasting_glucose'),
                'chol': labs.get('total_cholesterol'),
                'ldl': labs.get('ldl'),
                'hdl': labs.get('hdl'),
                'trig': labs.get('triglycerides'),
                'smoking': persona['lifestyle']['smoking_status'],
                'diabetes_risk': risk_scores['diabetes'],
                'cvd_risk': risk_scores['cardiovascular'],
            })
            
            # Create Condition nodes
            for code, desc, start_date, end_date in persona['conditions']:
                session.run("""
                    MATCH (p:Person {synthea_id: $synthea_id})
                    MERGE (c:Condition {code: $code, patient_id: $synthea_id})
                    SET c.description = $description,
                        c.onset_date = $onset_date,
                        c.abatement_date = $abatement_date,
                        c.is_active = CASE WHEN $abatement_date IS NULL THEN true ELSE false END
                    MERGE (p)-[:HAS_CONDITION]->(c)
                """, {
                    'synthea_id': synthea_id,
                    'code': code,
                    'description': desc,
                    'onset_date': start_date,
                    'abatement_date': end_date
                })
            
            # Create Medication nodes
            for med_name, code, dosage in persona['medications']:
                session.run("""
                    MATCH (p:Person {synthea_id: $synthea_id})
                    MERGE (m:Medication {code: $code, patient_id: $synthea_id})
                    SET m.name = $name,
                        m.dosage = $dosage,
                        m.status = 'active'
                    MERGE (p)-[:TAKES_MEDICATION]->(m)
                """, {
                    'synthea_id': synthea_id,
                    'code': code,
                    'name': med_name,
                    'dosage': dosage
                })
            
            # Create Allergy nodes
            for allergen, reaction, allergy_type in persona['allergies']:
                session.run("""
                    MATCH (p:Person {synthea_id: $synthea_id})
                    MERGE (a:Allergy {allergen: $allergen, patient_id: $synthea_id})
                    SET a.reaction = $reaction,
                        a.type = $type
                    MERGE (p)-[:HAS_ALLERGY]->(a)
                """, {
                    'synthea_id': synthea_id,
                    'allergen': allergen,
                    'reaction': reaction,
                    'type': allergy_type
                })
            
            # Create Lifestyle node
            lifestyle = persona['lifestyle']
            session.run("""
                MATCH (p:Person {synthea_id: $synthea_id})
                MERGE (l:Lifestyle {patient_id: $synthea_id})
                SET l.smoking_status = $smoking,
                    l.smoking_pack_years = $pack_years,
                    l.alcohol_use = $alcohol,
                    l.exercise_frequency = $exercise,
                    l.diet_quality = $diet,
                    l.sleep_hours = $sleep,
                    l.stress_level = $stress
                MERGE (p)-[:HAS_LIFESTYLE]->(l)
            """, {
                'synthea_id': synthea_id,
                'smoking': lifestyle['smoking_status'],
                'pack_years': lifestyle['smoking_pack_years'],
                'alcohol': lifestyle['alcohol_use'],
                'exercise': lifestyle['exercise_frequency'],
                'diet': lifestyle['diet_quality'],
                'sleep': lifestyle['sleep_hours'],
                'stress': lifestyle['stress_level'],
            })
            
            # Create Family History nodes
            for relative, conditions, status in persona['family_history']:
                session.run("""
                    MATCH (p:Person {synthea_id: $synthea_id})
                    MERGE (fh:FamilyHistory {patient_id: $synthea_id, relative: $relative})
                    SET fh.conditions = $conditions,
                        fh.status = $status
                    MERGE (p)-[:HAS_FAMILY_HISTORY]->(fh)
                """, {
                    'synthea_id': synthea_id,
                    'relative': relative,
                    'conditions': conditions,
                    'status': status
                })
            
            # Create Social History node
            social = persona['social_history']
            session.run("""
                MATCH (p:Person {synthea_id: $synthea_id})
                MERGE (sh:SocialHistory {patient_id: $synthea_id})
                SET sh.employment = $employment,
                    sh.education = $education,
                    sh.living_situation = $living,
                    sh.social_support = $support,
                    sh.transportation = $transport,
                    sh.food_security = $food,
                    sh.health_literacy = $literacy
                MERGE (p)-[:HAS_SOCIAL_HISTORY]->(sh)
            """, {
                'synthea_id': synthea_id,
                'employment': social['employment'],
                'education': social['education'],
                'living': social['living_situation'],
                'support': social['social_support'],
                'transport': social['transportation'],
                'food': social['food_security'],
                'literacy': social['health_literacy'],
            })
            
            # Link to risk factor nodes
            # Diabetes risk factors
            if risk_scores['diabetes'] >= 7:
                session.run("""
                    MATCH (p:Person {synthea_id: $synthea_id})
                    MERGE (rf:RiskFactor {name: 'Diabetes'})
                    MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
                """, {'synthea_id': synthea_id})
            
            if risk_scores['cardiovascular'] >= 7:
                session.run("""
                    MATCH (p:Person {synthea_id: $synthea_id})
                    MERGE (rf:RiskFactor {name: 'Hypertension'})
                    MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
                """, {'synthea_id': synthea_id})
            
            if vitals['weight_kg'] / ((vitals['height_cm']/100)**2) >= 30:
                session.run("""
                    MATCH (p:Person {synthea_id: $synthea_id})
                    MERGE (rf:RiskFactor {name: 'Obesity'})
                    MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
                """, {'synthea_id': synthea_id})
        
        print("✅")
        
    finally:
        driver.close()


def main():
    print("=" * 70)
    print("🏥 Creating 10 Detailed Patient Personas")
    print("   Spanning Diabetes & Cardiovascular Risk Spectrum")
    print("=" * 70)
    
    print("\n📋 Personas Overview:")
    print("-" * 70)
    print(f"{'#':<3} {'Name':<25} {'Age':<5} {'Diabetes':<10} {'CVD':<10} {'Category'}")
    print("-" * 70)
    
    for i, persona in enumerate(PERSONAS, 1):
        demo = persona['demographics']
        age = calculate_age(demo['birthdate'])
        d_risk = persona['risk_scores']['diabetes']
        c_risk = persona['risk_scores']['cardiovascular']
        
        if d_risk >= 8 or c_risk >= 8:
            category = "Very High Risk"
        elif d_risk >= 6 or c_risk >= 6:
            category = "High Risk"
        elif d_risk >= 4 or c_risk >= 4:
            category = "Moderate Risk"
        elif d_risk >= 2 or c_risk >= 2:
            category = "Low Risk"
        else:
            category = "Very Low Risk"
        
        print(f"{i:<3} {demo['first_name']} {demo['last_name']:<18} {age:<5} {d_risk}/10{'':<5} {c_risk}/10{'':<5} {category}")
    
    print("-" * 70)
    
    print("\n📥 Phase 1: Inserting personas into MariaDB...")
    
    for persona in PERSONAS:
        insert_persona_to_mariadb(persona)
    
    print("\n🔗 Phase 2: Syncing personas to Neo4j Knowledge Graph...")
    
    for persona in PERSONAS:
        demo = persona['demographics']
        print(f"\n   Processing: {demo['first_name']} {demo['last_name']}")
        sync_persona_to_neo4j(persona)
    
    print("\n" + "=" * 70)
    print("✅ All 10 personas created successfully!")
    print("=" * 70)
    print("\n📊 Summary:")
    print("   - 10 detailed patient personas inserted into MariaDB")
    print("   - All personas synced to Neo4j Knowledge Graph")
    print("   - Each persona includes:")
    print("     • Full demographics and narrative")
    print("     • Conditions, medications, allergies")
    print("     • Vital signs and lab results")
    print("     • Lifestyle and social history")
    print("     • Family history")
    print("     • AI model features for ML inference")
    print("\n🔍 Query examples:")
    print("   MariaDB: SELECT * FROM Synthea_Patient WHERE synthea_id LIKE 'persona-%'")
    print("   Neo4j:   MATCH (p:Person) WHERE p.is_persona = true RETURN p")


if __name__ == '__main__':
    main()
