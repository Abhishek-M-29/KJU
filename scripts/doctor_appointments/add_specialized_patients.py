#!/usr/bin/env python3
"""
Add Specialized Patient Cases
=============================
Adds highly specialized patient cases directly to MariaDB with all
necessary data for ML model predictions (cardiovascular and diabetes).

These patients are designed as edge cases and specific scenarios for
demonstrating and testing the AI prediction models.

Usage:
    python add_specialized_patients.py [--sync-to-neo4j]
"""

import mariadb
import os
import uuid
import json
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))


def get_db_connection():
    """Establish database connection"""
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )


def execute_query(query, params=None):
    """Execute a database query"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            return cursor.lastrowid
    except mariadb.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()


def generate_synthea_id():
    """Generate a UUID like Synthea does"""
    return str(uuid.uuid4())


# =============================================================================
# SPECIALIZED PATIENT CASES FOR ML TESTING
# =============================================================================

SPECIALIZED_PATIENTS = [
    # Case 1: HIGH CARDIOVASCULAR RISK - Elderly male with multiple risk factors
    {
        "demographics": {
            "first_name": "Harold",
            "last_name": "Cardiovascular_HighRisk",
            "gender": "M",
            "birthdate": date(1955, 3, 15),  # ~71 years old
            "race": "white",
            "ethnicity": "nonhispanic",
            "city": "Boston",
            "state": "Massachusetts"
        },
        "ai_features": {
            "age_years": 71,
            "gender_numeric": 0,  # Male
            "height_cm": 175.0,
            "weight_kg": 98.0,
            "bmi": 32.0,  # Obese
            "bp_systolic": 165,  # High
            "bp_diastolic": 98,  # High
            "cholesterol_level": 3,  # Well above normal
            "glucose_level": 2,  # Above normal
            "is_smoker": 1,  # Yes
            "smoking_history": "current",
            "alcohol_use": 1,  # Yes
            "physical_activity": 0,  # Inactive
            "has_hypertension": 1,
            "has_heart_disease": 0,
            "hba1c_level": 6.2,
            "blood_glucose_fasting": 118
        },
        "conditions": [
            {"code": "59621000", "description": "Essential hypertension (disorder)", "is_active": 1},
            {"code": "13644009", "description": "Hypercholesterolemia (disorder)", "is_active": 1},
            {"code": "414545008", "description": "Ischemic heart disease (disorder)", "is_active": 0},
            {"code": "414916001", "description": "Obesity (disorder)", "is_active": 1},
            {"code": "266918002", "description": "Tobacco smoking behavior (finding)", "is_active": 1}
        ],
        "medications": [
            {"code": "314076", "description": "Lisinopril 20 MG Oral Tablet", "is_active": 1},
            {"code": "310436", "description": "Atorvastatin 40 MG Oral Tablet", "is_active": 1},
            {"code": "197361", "description": "Aspirin 81 MG Oral Tablet", "is_active": 1}
        ],
        "observations": [
            {"code": "8480-6", "description": "Systolic Blood Pressure", "value": "165", "units": "mm[Hg]"},
            {"code": "8462-4", "description": "Diastolic Blood Pressure", "value": "98", "units": "mm[Hg]"},
            {"code": "2093-3", "description": "Total Cholesterol", "value": "285", "units": "mg/dL"},
            {"code": "18262-6", "description": "LDL Cholesterol", "value": "180", "units": "mg/dL"},
            {"code": "2085-9", "description": "HDL Cholesterol", "value": "35", "units": "mg/dL"},
            {"code": "29463-7", "description": "Body Weight", "value": "98", "units": "kg"},
            {"code": "8302-2", "description": "Body Height", "value": "175", "units": "cm"},
            {"code": "39156-5", "description": "Body Mass Index", "value": "32.0", "units": "kg/m2"},
            {"code": "4548-4", "description": "Hemoglobin A1c", "value": "6.2", "units": "%"},
            {"code": "2339-0", "description": "Blood Glucose (Fasting)", "value": "118", "units": "mg/dL"}
        ],
        "expected_risk": {"cardiovascular": "HIGH", "diabetes": "MODERATE"}
    },
    
    # Case 2: HIGH DIABETES RISK - Prediabetic obese female
    {
        "demographics": {
            "first_name": "Maria",
            "last_name": "Diabetes_HighRisk",
            "gender": "F",
            "birthdate": date(1968, 7, 22),  # ~57 years old
            "race": "hispanic",
            "ethnicity": "hispanic",
            "city": "Miami",
            "state": "Florida"
        },
        "ai_features": {
            "age_years": 57,
            "gender_numeric": 1,  # Female
            "height_cm": 160.0,
            "weight_kg": 95.0,
            "bmi": 37.1,  # Severely obese
            "bp_systolic": 142,
            "bp_diastolic": 88,
            "cholesterol_level": 2,  # Above normal
            "glucose_level": 3,  # Well above normal
            "is_smoker": 0,
            "smoking_history": "never",
            "alcohol_use": 0,
            "physical_activity": 0,  # Inactive
            "has_hypertension": 1,
            "has_heart_disease": 0,
            "hba1c_level": 7.8,  # Diabetic range
            "blood_glucose_fasting": 185
        },
        "conditions": [
            {"code": "44054006", "description": "Diabetes mellitus type 2 (disorder)", "is_active": 1},
            {"code": "59621000", "description": "Essential hypertension (disorder)", "is_active": 1},
            {"code": "414916001", "description": "Obesity (disorder)", "is_active": 1},
            {"code": "237599002", "description": "Insulin resistance (disorder)", "is_active": 1},
            {"code": "190966007", "description": "Hyperlipidemia (disorder)", "is_active": 1}
        ],
        "medications": [
            {"code": "860975", "description": "Metformin 1000 MG Extended Release Oral Tablet", "is_active": 1},
            {"code": "314076", "description": "Lisinopril 10 MG Oral Tablet", "is_active": 1},
            {"code": "200031", "description": "Glipizide 10 MG Oral Tablet", "is_active": 1}
        ],
        "observations": [
            {"code": "8480-6", "description": "Systolic Blood Pressure", "value": "142", "units": "mm[Hg]"},
            {"code": "8462-4", "description": "Diastolic Blood Pressure", "value": "88", "units": "mm[Hg]"},
            {"code": "29463-7", "description": "Body Weight", "value": "95", "units": "kg"},
            {"code": "8302-2", "description": "Body Height", "value": "160", "units": "cm"},
            {"code": "39156-5", "description": "Body Mass Index", "value": "37.1", "units": "kg/m2"},
            {"code": "4548-4", "description": "Hemoglobin A1c", "value": "7.8", "units": "%"},
            {"code": "2339-0", "description": "Blood Glucose (Fasting)", "value": "185", "units": "mg/dL"},
            {"code": "2093-3", "description": "Total Cholesterol", "value": "245", "units": "mg/dL"}
        ],
        "expected_risk": {"cardiovascular": "MODERATE", "diabetes": "HIGH"}
    },
    
    # Case 3: LOW RISK - Healthy young adult
    {
        "demographics": {
            "first_name": "Alex",
            "last_name": "Healthy_LowRisk",
            "gender": "M",
            "birthdate": date(1995, 11, 8),  # ~30 years old
            "race": "asian",
            "ethnicity": "nonhispanic",
            "city": "Seattle",
            "state": "Washington"
        },
        "ai_features": {
            "age_years": 30,
            "gender_numeric": 0,  # Male
            "height_cm": 178.0,
            "weight_kg": 72.0,
            "bmi": 22.7,  # Normal
            "bp_systolic": 118,  # Normal
            "bp_diastolic": 76,  # Normal
            "cholesterol_level": 1,  # Normal
            "glucose_level": 1,  # Normal
            "is_smoker": 0,
            "smoking_history": "never",
            "alcohol_use": 0,
            "physical_activity": 1,  # Active
            "has_hypertension": 0,
            "has_heart_disease": 0,
            "hba1c_level": 5.1,  # Normal
            "blood_glucose_fasting": 88
        },
        "conditions": [],
        "medications": [],
        "observations": [
            {"code": "8480-6", "description": "Systolic Blood Pressure", "value": "118", "units": "mm[Hg]"},
            {"code": "8462-4", "description": "Diastolic Blood Pressure", "value": "76", "units": "mm[Hg]"},
            {"code": "29463-7", "description": "Body Weight", "value": "72", "units": "kg"},
            {"code": "8302-2", "description": "Body Height", "value": "178", "units": "cm"},
            {"code": "39156-5", "description": "Body Mass Index", "value": "22.7", "units": "kg/m2"},
            {"code": "4548-4", "description": "Hemoglobin A1c", "value": "5.1", "units": "%"},
            {"code": "2339-0", "description": "Blood Glucose (Fasting)", "value": "88", "units": "mg/dL"},
            {"code": "2093-3", "description": "Total Cholesterol", "value": "175", "units": "mg/dL"},
            {"code": "2085-9", "description": "HDL Cholesterol", "value": "55", "units": "mg/dL"}
        ],
        "expected_risk": {"cardiovascular": "LOW", "diabetes": "LOW"}
    },
    
    # Case 4: DUAL HIGH RISK - Both cardiovascular and diabetes high risk
    {
        "demographics": {
            "first_name": "Robert",
            "last_name": "DualRisk_Critical",
            "gender": "M",
            "birthdate": date(1960, 2, 28),  # ~65 years old
            "race": "black",
            "ethnicity": "nonhispanic",
            "city": "Chicago",
            "state": "Illinois"
        },
        "ai_features": {
            "age_years": 65,
            "gender_numeric": 0,  # Male
            "height_cm": 180.0,
            "weight_kg": 110.0,
            "bmi": 33.9,  # Obese
            "bp_systolic": 175,  # Very high
            "bp_diastolic": 105,  # Very high
            "cholesterol_level": 3,  # Well above normal
            "glucose_level": 3,  # Well above normal
            "is_smoker": 1,
            "smoking_history": "current",
            "alcohol_use": 1,
            "physical_activity": 0,  # Inactive
            "has_hypertension": 1,
            "has_heart_disease": 1,
            "hba1c_level": 9.2,  # Uncontrolled diabetes
            "blood_glucose_fasting": 220
        },
        "conditions": [
            {"code": "44054006", "description": "Diabetes mellitus type 2 (disorder)", "is_active": 1},
            {"code": "59621000", "description": "Essential hypertension (disorder)", "is_active": 1},
            {"code": "53741008", "description": "Coronary arteriosclerosis (disorder)", "is_active": 1},
            {"code": "22298006", "description": "Myocardial infarction (disorder)", "is_active": 0},
            {"code": "414916001", "description": "Obesity (disorder)", "is_active": 1},
            {"code": "13644009", "description": "Hypercholesterolemia (disorder)", "is_active": 1},
            {"code": "127014009", "description": "Diabetic retinopathy (disorder)", "is_active": 1},
            {"code": "90781000119102", "description": "Chronic kidney disease stage 3 (disorder)", "is_active": 1}
        ],
        "medications": [
            {"code": "860975", "description": "Metformin 1000 MG Extended Release Oral Tablet", "is_active": 1},
            {"code": "261551", "description": "Insulin glargine 100 UNT/ML Injectable Solution", "is_active": 1},
            {"code": "314076", "description": "Lisinopril 40 MG Oral Tablet", "is_active": 1},
            {"code": "310436", "description": "Atorvastatin 80 MG Oral Tablet", "is_active": 1},
            {"code": "197361", "description": "Aspirin 81 MG Oral Tablet", "is_active": 1},
            {"code": "866924", "description": "Metoprolol Succinate 100 MG Extended Release Oral Tablet", "is_active": 1},
            {"code": "197770", "description": "Amlodipine 10 MG Oral Tablet", "is_active": 1}
        ],
        "observations": [
            {"code": "8480-6", "description": "Systolic Blood Pressure", "value": "175", "units": "mm[Hg]"},
            {"code": "8462-4", "description": "Diastolic Blood Pressure", "value": "105", "units": "mm[Hg]"},
            {"code": "29463-7", "description": "Body Weight", "value": "110", "units": "kg"},
            {"code": "8302-2", "description": "Body Height", "value": "180", "units": "cm"},
            {"code": "39156-5", "description": "Body Mass Index", "value": "33.9", "units": "kg/m2"},
            {"code": "4548-4", "description": "Hemoglobin A1c", "value": "9.2", "units": "%"},
            {"code": "2339-0", "description": "Blood Glucose (Fasting)", "value": "220", "units": "mg/dL"},
            {"code": "2093-3", "description": "Total Cholesterol", "value": "310", "units": "mg/dL"},
            {"code": "18262-6", "description": "LDL Cholesterol", "value": "200", "units": "mg/dL"},
            {"code": "2085-9", "description": "HDL Cholesterol", "value": "28", "units": "mg/dL"},
            {"code": "2571-8", "description": "Triglycerides", "value": "450", "units": "mg/dL"},
            {"code": "33914-3", "description": "eGFR", "value": "45", "units": "mL/min/1.73m2"}
        ],
        "expected_risk": {"cardiovascular": "CRITICAL", "diabetes": "CRITICAL"}
    },
    
    # Case 5: BORDERLINE CASE - Edge case for model decision boundary
    {
        "demographics": {
            "first_name": "Jennifer",
            "last_name": "Borderline_Edge",
            "gender": "F",
            "birthdate": date(1975, 5, 10),  # ~50 years old
            "race": "white",
            "ethnicity": "nonhispanic",
            "city": "Denver",
            "state": "Colorado"
        },
        "ai_features": {
            "age_years": 50,
            "gender_numeric": 1,  # Female
            "height_cm": 165.0,
            "weight_kg": 78.0,
            "bmi": 28.7,  # Overweight (borderline obese)
            "bp_systolic": 138,  # Borderline high
            "bp_diastolic": 88,  # Borderline high
            "cholesterol_level": 2,  # Above normal
            "glucose_level": 2,  # Above normal
            "is_smoker": 0,
            "smoking_history": "former",
            "alcohol_use": 0,
            "physical_activity": 1,  # Active
            "has_hypertension": 0,  # Not diagnosed yet
            "has_heart_disease": 0,
            "hba1c_level": 6.4,  # Prediabetic
            "blood_glucose_fasting": 115
        },
        "conditions": [
            {"code": "15777000", "description": "Prediabetes (disorder)", "is_active": 1},
            {"code": "162573006", "description": "Suspected hypertension (situation)", "is_active": 1},
            {"code": "238136002", "description": "Overweight (disorder)", "is_active": 1}
        ],
        "medications": [],
        "observations": [
            {"code": "8480-6", "description": "Systolic Blood Pressure", "value": "138", "units": "mm[Hg]"},
            {"code": "8462-4", "description": "Diastolic Blood Pressure", "value": "88", "units": "mm[Hg]"},
            {"code": "29463-7", "description": "Body Weight", "value": "78", "units": "kg"},
            {"code": "8302-2", "description": "Body Height", "value": "165", "units": "cm"},
            {"code": "39156-5", "description": "Body Mass Index", "value": "28.7", "units": "kg/m2"},
            {"code": "4548-4", "description": "Hemoglobin A1c", "value": "6.4", "units": "%"},
            {"code": "2339-0", "description": "Blood Glucose (Fasting)", "value": "115", "units": "mg/dL"},
            {"code": "2093-3", "description": "Total Cholesterol", "value": "220", "units": "mg/dL"}
        ],
        "expected_risk": {"cardiovascular": "MODERATE", "diabetes": "MODERATE"}
    },
    
    # Case 6: GESTATIONAL DIABETES - Young pregnant woman
    {
        "demographics": {
            "first_name": "Sarah",
            "last_name": "Gestational_Special",
            "gender": "F",
            "birthdate": date(1992, 8, 15),  # ~33 years old
            "race": "white",
            "ethnicity": "nonhispanic",
            "city": "Austin",
            "state": "Texas"
        },
        "ai_features": {
            "age_years": 33,
            "gender_numeric": 1,  # Female
            "height_cm": 168.0,
            "weight_kg": 82.0,
            "bmi": 29.1,  # Overweight (pregnancy)
            "bp_systolic": 125,
            "bp_diastolic": 80,
            "cholesterol_level": 2,
            "glucose_level": 2,
            "is_smoker": 0,
            "smoking_history": "never",
            "alcohol_use": 0,
            "physical_activity": 1,
            "has_hypertension": 0,
            "has_heart_disease": 0,
            "hba1c_level": 6.0,
            "blood_glucose_fasting": 105
        },
        "conditions": [
            {"code": "11687002", "description": "Gestational diabetes mellitus (disorder)", "is_active": 1},
            {"code": "72892002", "description": "Normal pregnancy (finding)", "is_active": 1}
        ],
        "medications": [
            {"code": "860975", "description": "Metformin 500 MG Oral Tablet", "is_active": 1},
            {"code": "315266", "description": "Prenatal Vitamin Oral Tablet", "is_active": 1}
        ],
        "observations": [
            {"code": "8480-6", "description": "Systolic Blood Pressure", "value": "125", "units": "mm[Hg]"},
            {"code": "8462-4", "description": "Diastolic Blood Pressure", "value": "80", "units": "mm[Hg]"},
            {"code": "29463-7", "description": "Body Weight", "value": "82", "units": "kg"},
            {"code": "8302-2", "description": "Body Height", "value": "168", "units": "cm"},
            {"code": "39156-5", "description": "Body Mass Index", "value": "29.1", "units": "kg/m2"},
            {"code": "4548-4", "description": "Hemoglobin A1c", "value": "6.0", "units": "%"},
            {"code": "2339-0", "description": "Blood Glucose (Fasting)", "value": "105", "units": "mg/dL"}
        ],
        "expected_risk": {"cardiovascular": "LOW", "diabetes": "MODERATE"}
    },
    
    # Case 7: ELDERLY FRAIL - Very old patient with multiple comorbidities
    {
        "demographics": {
            "first_name": "Eleanor",
            "last_name": "Elderly_Complex",
            "gender": "F",
            "birthdate": date(1938, 12, 1),  # ~87 years old
            "race": "white",
            "ethnicity": "nonhispanic",
            "city": "Phoenix",
            "state": "Arizona"
        },
        "ai_features": {
            "age_years": 87,
            "gender_numeric": 1,  # Female
            "height_cm": 155.0,
            "weight_kg": 52.0,
            "bmi": 21.6,  # Normal but low for elderly
            "bp_systolic": 158,
            "bp_diastolic": 70,  # Wide pulse pressure
            "cholesterol_level": 2,
            "glucose_level": 2,
            "is_smoker": 0,
            "smoking_history": "former",
            "alcohol_use": 0,
            "physical_activity": 0,
            "has_hypertension": 1,
            "has_heart_disease": 1,
            "hba1c_level": 6.8,
            "blood_glucose_fasting": 130
        },
        "conditions": [
            {"code": "59621000", "description": "Essential hypertension (disorder)", "is_active": 1},
            {"code": "49436004", "description": "Atrial fibrillation (disorder)", "is_active": 1},
            {"code": "84114007", "description": "Heart failure (disorder)", "is_active": 1},
            {"code": "44054006", "description": "Diabetes mellitus type 2 (disorder)", "is_active": 1},
            {"code": "396275006", "description": "Osteoarthritis (disorder)", "is_active": 1},
            {"code": "64859006", "description": "Osteoporosis (disorder)", "is_active": 1}
        ],
        "medications": [
            {"code": "855332", "description": "Warfarin 5 MG Oral Tablet", "is_active": 1},
            {"code": "866924", "description": "Metoprolol Succinate 50 MG Extended Release Oral Tablet", "is_active": 1},
            {"code": "310437", "description": "Furosemide 40 MG Oral Tablet", "is_active": 1},
            {"code": "314076", "description": "Lisinopril 10 MG Oral Tablet", "is_active": 1},
            {"code": "860975", "description": "Metformin 500 MG Oral Tablet", "is_active": 1}
        ],
        "observations": [
            {"code": "8480-6", "description": "Systolic Blood Pressure", "value": "158", "units": "mm[Hg]"},
            {"code": "8462-4", "description": "Diastolic Blood Pressure", "value": "70", "units": "mm[Hg]"},
            {"code": "29463-7", "description": "Body Weight", "value": "52", "units": "kg"},
            {"code": "8302-2", "description": "Body Height", "value": "155", "units": "cm"},
            {"code": "39156-5", "description": "Body Mass Index", "value": "21.6", "units": "kg/m2"},
            {"code": "4548-4", "description": "Hemoglobin A1c", "value": "6.8", "units": "%"},
            {"code": "2339-0", "description": "Blood Glucose (Fasting)", "value": "130", "units": "mg/dL"},
            {"code": "8867-4", "description": "Heart Rate", "value": "82", "units": "/min"}
        ],
        "expected_risk": {"cardiovascular": "HIGH", "diabetes": "MODERATE"}
    },
    
    # Case 8: ATHLETE - Unusual vitals due to athletic conditioning
    {
        "demographics": {
            "first_name": "Michael",
            "last_name": "Athlete_Unusual",
            "gender": "M",
            "birthdate": date(1990, 4, 20),  # ~35 years old
            "race": "black",
            "ethnicity": "nonhispanic",
            "city": "Los Angeles",
            "state": "California"
        },
        "ai_features": {
            "age_years": 35,
            "gender_numeric": 0,  # Male
            "height_cm": 190.0,
            "weight_kg": 95.0,
            "bmi": 26.3,  # High due to muscle mass
            "bp_systolic": 105,  # Athletic low
            "bp_diastolic": 62,  # Athletic low
            "cholesterol_level": 1,
            "glucose_level": 1,
            "is_smoker": 0,
            "smoking_history": "never",
            "alcohol_use": 0,
            "physical_activity": 1,
            "has_hypertension": 0,
            "has_heart_disease": 0,
            "hba1c_level": 4.8,
            "blood_glucose_fasting": 78
        },
        "conditions": [],
        "medications": [],
        "observations": [
            {"code": "8480-6", "description": "Systolic Blood Pressure", "value": "105", "units": "mm[Hg]"},
            {"code": "8462-4", "description": "Diastolic Blood Pressure", "value": "62", "units": "mm[Hg]"},
            {"code": "29463-7", "description": "Body Weight", "value": "95", "units": "kg"},
            {"code": "8302-2", "description": "Body Height", "value": "190", "units": "cm"},
            {"code": "39156-5", "description": "Body Mass Index", "value": "26.3", "units": "kg/m2"},
            {"code": "4548-4", "description": "Hemoglobin A1c", "value": "4.8", "units": "%"},
            {"code": "2339-0", "description": "Blood Glucose (Fasting)", "value": "78", "units": "mg/dL"},
            {"code": "8867-4", "description": "Heart Rate", "value": "48", "units": "/min"},
            {"code": "2093-3", "description": "Total Cholesterol", "value": "160", "units": "mg/dL"},
            {"code": "2085-9", "description": "HDL Cholesterol", "value": "68", "units": "mg/dL"}
        ],
        "expected_risk": {"cardiovascular": "LOW", "diabetes": "LOW"}
    }
]


def add_patient_to_mariadb(patient_data):
    """Add a single patient with all related data to MariaDB"""
    
    synthea_id = f"CUSTOM-{generate_synthea_id()}"
    demo = patient_data["demographics"]
    ai_feat = patient_data["ai_features"]
    
    print(f"\n📝 Adding patient: {demo['first_name']} {demo['last_name']}")
    
    # 1. Insert patient
    patient_query = """
    INSERT INTO Synthea_Patient (
        synthea_id, first_name, last_name, gender, birthdate,
        race, ethnicity, city, state
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    patient_id = execute_query(patient_query, (
        synthea_id,
        demo["first_name"],
        demo["last_name"],
        demo["gender"],
        demo["birthdate"],
        demo["race"],
        demo["ethnicity"],
        demo["city"],
        demo["state"]
    ))
    
    if not patient_id:
        print(f"  ❌ Failed to insert patient")
        return None
    
    print(f"  ✅ Patient created with ID: {patient_id}, Synthea ID: {synthea_id}")
    
    # 2. Create an encounter for observations
    encounter_id = f"ENC-{generate_synthea_id()}"
    enc_date = datetime.now()
    
    encounter_query = """
    INSERT INTO Synthea_Encounter (
        synthea_id, synthea_patient_id, encounter_class, description,
        start_datetime, stop_datetime
    ) VALUES (?, ?, ?, ?, ?, ?)
    """
    execute_query(encounter_query, (
        encounter_id,
        synthea_id,
        "outpatient",
        "Comprehensive Health Assessment",
        enc_date,
        enc_date + timedelta(hours=1)
    ))
    print(f"  ✅ Created encounter: {encounter_id}")
    
    # 3. Insert conditions
    for cond in patient_data.get("conditions", []):
        cond_query = """
        INSERT INTO Synthea_Condition (
            synthea_patient_id, synthea_encounter_id, code, description,
            start_date, is_active
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        execute_query(cond_query, (
            synthea_id,
            encounter_id,
            cond["code"],
            cond["description"],
            date.today(),
            cond["is_active"]
        ))
    print(f"  ✅ Added {len(patient_data.get('conditions', []))} conditions")
    
    # 4. Insert medications
    for med in patient_data.get("medications", []):
        med_query = """
        INSERT INTO Synthea_Medication (
            synthea_patient_id, synthea_encounter_id, code, description,
            start_datetime, is_active
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        execute_query(med_query, (
            synthea_id,
            encounter_id,
            med["code"],
            med["description"],
            datetime.now(),
            med["is_active"]
        ))
    print(f"  ✅ Added {len(patient_data.get('medications', []))} medications")
    
    # 5. Insert observations
    for obs in patient_data.get("observations", []):
        obs_query = """
        INSERT INTO Synthea_Observation (
            synthea_patient_id, synthea_encounter_id, observation_date,
            category, code, description, value, units
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(obs_query, (
            synthea_id,
            encounter_id,
            datetime.now(),
            "vital-signs" if obs["code"].startswith(("8", "2", "3", "4")) else "laboratory",
            obs["code"],
            obs["description"],
            obs["value"],
            obs["units"]
        ))
    print(f"  ✅ Added {len(patient_data.get('observations', []))} observations")
    
    # 6. Insert AI Features
    ai_query = """
    INSERT INTO Patient_AI_Features (
        synthea_patient_id, age_years, gender_numeric, height_cm, weight_kg,
        bmi, bp_systolic, bp_diastolic, cholesterol_level, glucose_level,
        is_smoker, smoking_history, alcohol_use, physical_activity,
        has_hypertension, has_heart_disease, hba1c_level, blood_glucose_fasting,
        last_observation_date, data_completeness_score
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON DUPLICATE KEY UPDATE
        age_years = VALUES(age_years),
        bp_systolic = VALUES(bp_systolic),
        bp_diastolic = VALUES(bp_diastolic),
        updated_at = CURRENT_TIMESTAMP
    """
    execute_query(ai_query, (
        synthea_id,
        ai_feat["age_years"],
        ai_feat["gender_numeric"],
        ai_feat["height_cm"],
        ai_feat["weight_kg"],
        ai_feat["bmi"],
        ai_feat["bp_systolic"],
        ai_feat["bp_diastolic"],
        ai_feat["cholesterol_level"],
        ai_feat["glucose_level"],
        ai_feat["is_smoker"],
        ai_feat["smoking_history"],
        ai_feat["alcohol_use"],
        ai_feat["physical_activity"],
        ai_feat["has_hypertension"],
        ai_feat["has_heart_disease"],
        ai_feat["hba1c_level"],
        ai_feat["blood_glucose_fasting"],
        date.today(),
        1.0  # Full data completeness for these cases
    ))
    print(f"  ✅ Added AI features")
    
    return {
        "synthea_id": synthea_id,
        "patient_id": patient_id,
        "name": f"{demo['first_name']} {demo['last_name']}",
        "expected_risk": patient_data.get("expected_risk", {})
    }


def add_all_specialized_patients():
    """Add all specialized patient cases"""
    print("\n" + "="*60)
    print("🏥 ADDING SPECIALIZED PATIENT CASES")
    print("="*60)
    
    results = []
    for patient in SPECIALIZED_PATIENTS:
        result = add_patient_to_mariadb(patient)
        if result:
            results.append(result)
    
    print("\n" + "="*60)
    print(f"✅ Successfully added {len(results)} specialized patients")
    print("="*60)
    
    # Summary table
    print("\n📊 PATIENT SUMMARY:")
    print("-" * 80)
    print(f"{'Name':<30} {'Synthea ID':<45} {'Expected Risk'}")
    print("-" * 80)
    for r in results:
        risk_str = f"CV: {r['expected_risk'].get('cardiovascular', 'N/A')}, DM: {r['expected_risk'].get('diabetes', 'N/A')}"
        print(f"{r['name']:<30} {r['synthea_id']:<45} {risk_str}")
    print("-" * 80)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add specialized patient cases")
    parser.add_argument("--sync-to-neo4j", action="store_true", help="Also sync to Neo4j after adding")
    args = parser.parse_args()
    
    # Add patients
    results = add_all_specialized_patients()
    
    if args.sync_to_neo4j and results:
        print("\n🔄 Syncing new patients to Neo4j...")
        # Get the synthea_ids to sync
        new_ids = [r["synthea_id"] for r in results]
        
        # Import and run incremental sync
        try:
            from sync_new_patients_to_neo4j import sync_specific_patients
            sync_specific_patients(new_ids)
        except ImportError:
            print("⚠️  Incremental sync module not found. Run sync manually.")
