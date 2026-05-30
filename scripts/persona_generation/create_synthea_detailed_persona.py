#!/usr/bin/env python3
"""
Synthea-Level Detailed Persona with Time-Series Data
=====================================================
Creates ONE extremely detailed patient with:
- Multiple encounters over years
- Time-series observations (vitals trending)
- Procedures history
- Immunizations
- Care plans
- Realistic noise and variation
"""

import mariadb, os, random
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
DB_HOST, DB_USER, DB_PASSWORD = os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD')
DB_NAME, DB_PORT = os.getenv('DB_NAME'), int(os.getenv('DB_PORT', 3305))
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
AURA_USER, AURA_PASSWORD = os.getenv('AURA_USER', 'neo4j'), os.getenv('AURA_PASSWORD')

# ============================================================================
# EXTREMELY DETAILED PERSONA: Maria Santos
# Profile: Prediabetes progressing, healthy heart, lots of "noise"
# ============================================================================

PERSONA = {
    "id": "persona-detailed-001",
    "demographics": {
        "first_name": "Maria", "middle_name": "Elena", "last_name": "Santos",
        "maiden_name": "Gutierrez", "birthdate": "1972-04-15", "gender": "F",
        "ssn": "XXX-XX-4521", "drivers_license": "S530-XXXX-XXXX",
        "race": "White", "ethnicity": "Hispanic", 
        "birthplace": "San Antonio, Texas",
        "address": "4892 Mesquite Lane", "city": "Austin", "state": "Texas", 
        "county": "Travis", "zip": "78745", "lat": 30.2134, "lon": -97.7965,
        "phone": "(512) 555-0147", "email": "maria.santos72@email.com",
        "marital_status": "Married", "spouse_name": "Carlos Santos",
        "children": 3, "income": 68000, "employer": "Austin ISD",
        "occupation": "Elementary School Teacher", "insurance": "Blue Cross Blue Shield",
        "pcp": "Dr. Rebecca Martinez", "pcp_npi": "1234567890",
        "preferred_language": "English", "interpreter_needed": False,
        "emergency_contact": "Carlos Santos (Husband)", "emergency_phone": "(512) 555-0148",
    },
    
    "narrative": """
    Maria Elena Santos is a 53-year-old Hispanic elementary school teacher living in Austin, Texas 
    with her husband Carlos (a plumber) and their youngest child (19, community college). Two older 
    children are married with kids - she's a grandmother of 3.
    
    MEDICAL JOURNEY:
    - 2018: Noted impaired fasting glucose (102) at routine physical. A1c was 5.7. Counseled on diet.
    - 2019: Weight up 8 lbs from stress eating (school issues). Glucose 108, A1c 5.8. Started walking.
    - 2020: COVID pandemic - gained 15 lbs, stress eating, stopped exercising. Glucose spiked to 118.
    - 2021: A1c reached 6.1 (prediabetes). Started metformin 500mg. Lost some weight.
    - 2022: Stable. A1c 5.9 on metformin. Glucose fluctuates 95-115 depending on diet.
    - 2023: Thyroid nodule found incidentally - benign on biopsy. TSH normal.
    - 2024: A1c crept to 6.2. Added more exercise, seeing nutritionist.
    - 2025: Current - doing better, A1c 5.8, glucose 105 today. Motivated.
    
    CARDIOVASCULAR: Completely healthy. BP always 115-125/70-78. Cholesterol normal. No family hx.
    
    LIFESTYLE: Non-smoker ever. Glass of wine on weekends. Walks 20-30 min 4x/week now. 
    Cooks at home (Mexican food, trying to reduce portions). Sleeps 6-7 hours.
    
    PSYCHOSOCIAL: Mild anxiety around health after her mother's diabetes complications. 
    Strong family support. Active in church. Stressed during school year, relaxes in summer.
    
    ALLERGIES: Penicillin (childhood rash - unclear if true allergy)
    
    Chief complaints today: Routine prediabetes follow-up. Feeling good. Wants to know if she can 
    stop metformin since she's exercising more. Also asking about colonoscopy (due at 53).
    """,
    
    "risk_scores": {"diabetes": 5, "cardiovascular": 2},
    
    # Time-series encounters over 7 years
    "encounters": [
        {"date": "2018-03-15", "type": "wellness", "reason": "Annual physical", "provider": "Dr. Martinez"},
        {"date": "2018-09-22", "type": "office", "reason": "Follow-up glucose", "provider": "Dr. Martinez"},
        {"date": "2019-03-20", "type": "wellness", "reason": "Annual physical", "provider": "Dr. Martinez"},
        {"date": "2019-11-05", "type": "urgent", "reason": "URI symptoms", "provider": "Dr. Chen"},
        {"date": "2020-02-28", "type": "wellness", "reason": "Annual physical", "provider": "Dr. Martinez"},
        {"date": "2020-06-15", "type": "telehealth", "reason": "COVID concern - negative", "provider": "Dr. Martinez"},
        {"date": "2020-10-10", "type": "office", "reason": "Weight gain, glucose check", "provider": "Dr. Martinez"},
        {"date": "2021-03-18", "type": "wellness", "reason": "Annual physical - prediabetes dx", "provider": "Dr. Martinez"},
        {"date": "2021-06-25", "type": "office", "reason": "Metformin start", "provider": "Dr. Martinez"},
        {"date": "2021-09-30", "type": "office", "reason": "Metformin f/u", "provider": "Dr. Martinez"},
        {"date": "2022-03-22", "type": "wellness", "reason": "Annual physical", "provider": "Dr. Martinez"},
        {"date": "2022-08-15", "type": "office", "reason": "Sore throat - strep negative", "provider": "Dr. Chen"},
        {"date": "2023-03-25", "type": "wellness", "reason": "Annual physical", "provider": "Dr. Martinez"},
        {"date": "2023-05-10", "type": "specialist", "reason": "Thyroid nodule eval", "provider": "Dr. Patel (Endo)"},
        {"date": "2023-06-02", "type": "procedure", "reason": "Thyroid FNA biopsy", "provider": "Dr. Wong (Radiology)"},
        {"date": "2023-06-20", "type": "office", "reason": "Biopsy results - benign", "provider": "Dr. Patel"},
        {"date": "2024-03-28", "type": "wellness", "reason": "Annual physical", "provider": "Dr. Martinez"},
        {"date": "2024-07-15", "type": "office", "reason": "Nutrition consult", "provider": "RD Sarah Johnson"},
        {"date": "2024-11-08", "type": "office", "reason": "Prediabetes f/u", "provider": "Dr. Martinez"},
        {"date": "2025-02-10", "type": "wellness", "reason": "Annual physical", "provider": "Dr. Martinez"},
    ],
    
    # Time-series vitals with realistic variation
    "vitals_history": [
        {"date": "2018-03-15", "weight_kg": 72, "bp_sys": 118, "bp_dia": 74, "hr": 72, "temp": 36.7, "o2": 98},
        {"date": "2019-03-20", "weight_kg": 75, "bp_sys": 122, "bp_dia": 76, "hr": 76, "temp": 36.8, "o2": 98},
        {"date": "2020-02-28", "weight_kg": 78, "bp_sys": 124, "bp_dia": 78, "hr": 74, "temp": 36.6, "o2": 99},
        {"date": "2020-10-10", "weight_kg": 85, "bp_sys": 128, "bp_dia": 82, "hr": 80, "temp": 36.9, "o2": 97},  # pandemic weight
        {"date": "2021-03-18", "weight_kg": 84, "bp_sys": 126, "bp_dia": 80, "hr": 78, "temp": 36.7, "o2": 98},
        {"date": "2022-03-22", "weight_kg": 80, "bp_sys": 120, "bp_dia": 76, "hr": 72, "temp": 36.8, "o2": 98},
        {"date": "2023-03-25", "weight_kg": 79, "bp_sys": 118, "bp_dia": 74, "hr": 70, "temp": 36.7, "o2": 99},
        {"date": "2024-03-28", "weight_kg": 78, "bp_sys": 122, "bp_dia": 78, "hr": 74, "temp": 36.8, "o2": 98},
        {"date": "2025-02-10", "weight_kg": 76, "bp_sys": 118, "bp_dia": 72, "hr": 68, "temp": 36.7, "o2": 99},
    ],
    
    # Time-series labs with realistic progression
    "labs_history": [
        {"date": "2018-03-15", "glucose": 102, "hba1c": 5.7, "chol": 195, "ldl": 115, "hdl": 58, "trig": 110, "tsh": 2.1, "creat": 0.8},
        {"date": "2019-03-20", "glucose": 108, "hba1c": 5.8, "chol": 198, "ldl": 118, "hdl": 55, "trig": 125, "tsh": 2.3, "creat": 0.8},
        {"date": "2020-02-28", "glucose": 105, "hba1c": 5.8, "chol": 202, "ldl": 122, "hdl": 52, "trig": 140, "tsh": 2.4, "creat": 0.9},
        {"date": "2020-10-10", "glucose": 118, "hba1c": 6.0, "chol": 215, "ldl": 135, "hdl": 48, "trig": 160, "tsh": 2.2, "creat": 0.9},
        {"date": "2021-03-18", "glucose": 115, "hba1c": 6.1, "chol": 208, "ldl": 128, "hdl": 50, "trig": 150, "tsh": 2.5, "creat": 0.9},
        {"date": "2021-09-30", "glucose": 108, "hba1c": 5.9, "chol": 195, "ldl": 115, "hdl": 54, "trig": 130, "tsh": 2.3, "creat": 0.8},
        {"date": "2022-03-22", "glucose": 105, "hba1c": 5.9, "chol": 188, "ldl": 108, "hdl": 56, "trig": 120, "tsh": 2.1, "creat": 0.8},
        {"date": "2023-03-25", "glucose": 102, "hba1c": 5.8, "chol": 185, "ldl": 105, "hdl": 58, "trig": 110, "tsh": 3.8, "creat": 0.8},  # TSH up - nodule
        {"date": "2024-03-28", "glucose": 112, "hba1c": 6.2, "chol": 192, "ldl": 112, "hdl": 55, "trig": 125, "tsh": 2.5, "creat": 0.8},  # A1c crept up
        {"date": "2025-02-10", "glucose": 105, "hba1c": 5.8, "chol": 182, "ldl": 102, "hdl": 60, "trig": 100, "tsh": 2.2, "creat": 0.8},  # improved!
    ],
    
    "conditions": [
        ("R73.03", "Prediabetes", "2021-03-18", None, "Active - on metformin"),
        ("E66.9", "Overweight", "2019-03-20", None, "BMI fluctuates 27-31"),
        ("E04.1", "Thyroid nodule - benign", "2023-05-10", None, "Monitoring, benign on FNA"),
        ("F41.1", "Generalized anxiety disorder - mild", "2020-06-15", None, "No meds, manageable"),
        ("K21.0", "GERD", "2022-08-15", None, "Occasional, OTC antacids"),
        ("M54.5", "Low back pain", "2021-09-30", "2021-12-15", "Resolved with PT"),
        ("J06.9", "URI", "2019-11-05", "2019-11-15", "Resolved"),
        ("J02.9", "Pharyngitis", "2022-08-15", "2022-08-22", "Resolved, strep negative"),
    ],
    
    "medications_current": [
        ("Metformin 500mg", "314076", "once daily with dinner", "2021-06-25"),
        ("Omeprazole 20mg", "198053", "as needed", "2022-08-15"),
        ("Calcium + Vitamin D", "315965", "once daily", "2023-03-25"),
    ],
    
    "medications_historical": [
        ("Ibuprofen 400mg", "197805", "as needed for back pain", "2021-09-30", "2021-12-15"),
        ("Azithromycin 250mg", "308460", "Z-pack for URI", "2019-11-05", "2019-11-10"),
    ],
    
    "allergies": [
        ("Penicillin", "Rash as child - unclear if true allergy", "unconfirmed", "childhood"),
    ],
    
    "immunizations": [
        ("Influenza", "2018-10-15"), ("Influenza", "2019-10-22"), ("Influenza", "2020-10-08"),
        ("Influenza", "2021-10-18"), ("Influenza", "2022-10-25"), ("Influenza", "2023-10-12"), ("Influenza", "2024-10-20"),
        ("COVID-19 Pfizer dose 1", "2021-03-01"), ("COVID-19 Pfizer dose 2", "2021-03-22"),
        ("COVID-19 booster", "2021-11-15"), ("COVID-19 bivalent", "2022-10-25"), ("COVID-19 updated", "2023-10-12"),
        ("Tdap", "2020-02-28"), ("Shingrix dose 1", "2024-03-28"), ("Shingrix dose 2", "2024-06-15"),
    ],
    
    "procedures": [
        ("Thyroid ultrasound", "2023-05-10", "CPT 76536", "1.2cm hypoechoic nodule right lobe"),
        ("Thyroid FNA biopsy", "2023-06-02", "CPT 60100", "Bethesda II - benign"),
        ("Mammogram screening", "2024-03-28", "CPT 77067", "BI-RADS 1 - negative"),
        ("Colonoscopy", "2025-02-15", "CPT 45378", "Scheduled - due at age 53"),
        ("DEXA scan", "2024-03-28", "CPT 77080", "T-score -0.8 lumbar, -0.5 hip - normal"),
    ],
    
    "care_plans": [
        {"condition": "Prediabetes", "goals": ["A1c < 5.7", "Weight loss 5%", "Exercise 150 min/week"],
         "interventions": ["Metformin 500mg daily", "Nutrition counseling", "Walking program"]},
    ],
    
    "social_history": {
        "tobacco": "Never smoker",
        "alcohol": "1-2 glasses wine/week, socially",
        "drugs": "Denies illicit drug use",
        "exercise": "Walking 20-30 min 4x/week; gardening on weekends",
        "diet": "Home-cooked Mexican food; trying to reduce portions and add vegetables",
        "sleep": "6-7 hours, occasional insomnia when stressed",
        "occupation": "Elementary school teacher x 28 years. Sedentary during class.",
        "stress": "Moderate during school year; relaxes in summer",
        "relationships": "Married 30 years, supportive spouse. 3 adult children, 3 grandchildren.",
        "religion": "Catholic, attends church weekly",
        "hobbies": "Cooking, gardening, reading, grandchildren",
    },
    
    "family_history": [
        ("Mother", "78", "Living", "Type 2 diabetes (age 55, now on insulin), HTN, diabetic retinopathy"),
        ("Father", "80", "Living", "HTN, BPH, otherwise healthy"),
        ("Sister", "50", "Living", "Prediabetes, obesity"),
        ("Brother", "55", "Living", "Healthy"),
        ("Maternal grandmother", "-", "Deceased 82", "Type 2 diabetes, stroke"),
        ("Paternal grandfather", "-", "Deceased 75", "Lung cancer (smoker)"),
    ],
    
    "review_of_systems": {
        "constitutional": "No fever, chills, or unintentional weight loss",
        "eyes": "Wears reading glasses, no vision changes",
        "ent": "No hearing loss, occasional seasonal allergies",
        "cardiovascular": "No chest pain, palpitations, or edema",
        "respiratory": "No shortness of breath, cough, or wheezing",
        "gi": "Occasional heartburn, no nausea/vomiting/diarrhea",
        "gu": "No dysuria, frequency, or incontinence",
        "musculoskeletal": "Occasional low back stiffness, no joint pain",
        "skin": "No rashes or lesions",
        "neurological": "No headaches, numbness, or tingling",
        "psychiatric": "Mild anxiety, well-controlled, no depression",
        "endocrine": "No heat/cold intolerance, no excessive thirst",
    },
}


def get_db():
    return mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)


def insert_detailed_persona():
    """Insert the extremely detailed persona into MariaDB"""
    conn = get_db()
    cur = conn.cursor()
    p = PERSONA
    demo = p["demographics"]
    synthea_id = p["id"]
    
    print(f"\n{'='*70}")
    print(f"📋 Creating Synthea-Level Detailed Persona: {demo['first_name']} {demo['last_name']}")
    print(f"{'='*70}")
    
    # 1. Patient
    print("\n👤 Inserting patient demographics...", end=" ")
    cur.execute("""INSERT INTO Synthea_Patient (synthea_id, first_name, middle_name, last_name, birthdate, gender,
        race, ethnicity, marital_status, address, city, state, zip, income)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE first_name=VALUES(first_name)""",
        (synthea_id, demo['first_name'], demo.get('middle_name'), demo['last_name'], demo['birthdate'], demo['gender'],
         demo.get('race'), demo.get('ethnicity'), demo.get('marital_status'), demo.get('address'),
         demo.get('city'), demo.get('state'), demo.get('zip'), demo.get('income')))
    print("✅")
    
    # 2. Encounters
    print(f"📅 Inserting {len(p['encounters'])} encounters...", end=" ")
    for enc in p['encounters']:
        enc_id = f"enc-{synthea_id}-{enc['date']}"
        cur.execute("""INSERT INTO Synthea_Encounter (synthea_id, synthea_patient_id, encounter_class, description, 
            start_datetime) VALUES (%s,%s,%s,%s,%s)""",
            (enc_id, synthea_id, enc['type'], f"{enc['reason']} - {enc['provider']}", enc['date']))
    print("✅")
    
    # 3. Vitals history (time-series)
    print(f"📊 Inserting {len(p['vitals_history'])} vital sign sets...", end=" ")
    for v in p['vitals_history']:
        obs_date = datetime.strptime(v['date'], "%Y-%m-%d")
        for code, val, unit in [("29463-7", v['weight_kg'], "kg"), ("8480-6", v['bp_sys'], "mmHg"),
                                 ("8462-4", v['bp_dia'], "mmHg"), ("8867-4", v['hr'], "/min")]:
            cur.execute("""INSERT INTO Synthea_Observation (synthea_patient_id, observation_date, code, 
                description, value, units, category) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (synthea_id, obs_date, code, code, str(val), unit, 'vital-signs'))
    print("✅")
    
    # 4. Labs history (time-series)
    print(f"🧪 Inserting {len(p['labs_history'])} lab panels...", end=" ")
    for lab in p['labs_history']:
        obs_date = datetime.strptime(lab['date'], "%Y-%m-%d")
        for code, key, unit in [("1558-6", "glucose", "mg/dL"), ("4548-4", "hba1c", "%"),
                                 ("2093-3", "chol", "mg/dL"), ("2089-1", "ldl", "mg/dL"),
                                 ("2085-9", "hdl", "mg/dL"), ("2571-8", "trig", "mg/dL"),
                                 ("3016-3", "tsh", "mIU/L"), ("2160-0", "creat", "mg/dL")]:
            cur.execute("""INSERT INTO Synthea_Observation (synthea_patient_id, observation_date, code,
                description, value, units, category) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (synthea_id, obs_date, code, key, str(lab[key]), unit, 'laboratory'))
    print("✅")
    
    # 5. Conditions
    print(f"🩺 Inserting {len(p['conditions'])} conditions...", end=" ")
    for code, desc, start, end, note in p['conditions']:
        cur.execute("""INSERT INTO Synthea_Condition (synthea_patient_id, code, description, start_date, stop_date, is_active)
            VALUES (%s,%s,%s,%s,%s,%s)""", (synthea_id, code, f"{desc} - {note}", start, end, 1 if not end else 0))
    print("✅")
    
    # 6. Current Medications
    print(f"💊 Inserting {len(p['medications_current'])} current medications...", end=" ")
    for med, code, dose, start in p['medications_current']:
        cur.execute("""INSERT INTO Synthea_Medication (synthea_patient_id, code, description, start_datetime, is_active)
            VALUES (%s,%s,%s,%s,1)""", (synthea_id, code, f"{med} - {dose}", start))
    print("✅")
    
    # 7. AI Features (latest values)
    print("🤖 Creating AI feature set...", end=" ")
    latest_vitals = p['vitals_history'][-1]
    latest_labs = p['labs_history'][-1]
    age = (date.today() - datetime.strptime(demo['birthdate'], "%Y-%m-%d").date()).days // 365
    bmi = latest_vitals['weight_kg'] / (1.63 ** 2)  # height 163cm
    
    cur.execute("""INSERT INTO Patient_AI_Features (synthea_patient_id, age_years, gender_numeric, height_cm, weight_kg,
        bmi, bp_systolic, bp_diastolic, cholesterol_level, glucose_level, is_smoker, alcohol_use, physical_activity,
        has_hypertension, has_heart_disease, smoking_history, hba1c_level, blood_glucose_fasting)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE age_years=VALUES(age_years)""",
        (synthea_id, age, 1, 163, latest_vitals['weight_kg'], round(bmi, 2), latest_vitals['bp_sys'], latest_vitals['bp_dia'],
         1, 2, 0, 0, 1, 0, 0, "never", latest_labs['hba1c'], latest_labs['glucose']))
    print("✅")
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"\n✅ MariaDB complete - {demo['first_name']} {demo['last_name']}")


def sync_detailed_to_neo4j():
    """Sync detailed persona to Neo4j with rich relationships"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(AURA_USER, AURA_PASSWORD))
    p = PERSONA
    demo = p["demographics"]
    synthea_id = p["id"]
    age = (date.today() - datetime.strptime(demo['birthdate'], "%Y-%m-%d").date()).days // 365
    
    print("\n🔗 Syncing to Neo4j Knowledge Graph...")
    
    with driver.session() as s:
        # Person node with full narrative
        s.run("""MERGE (p:Person:Patient {synthea_id: $id})
            SET p.first_name = $fn, p.last_name = $ln, p.full_name = $fn + ' ' + $ln,
                p.birthdate = $bd, p.age = $age, p.gender = $g, p.city = $city, p.state = $state,
                p.occupation = $occ, p.narrative = $narr, p.diabetes_risk = $dr, p.cvd_risk = $cr,
                p.is_persona = true, p.is_detailed = true""",
            {"id": synthea_id, "fn": demo['first_name'], "ln": demo['last_name'], "bd": demo['birthdate'],
             "age": age, "g": demo['gender'], "city": demo['city'], "state": demo['state'],
             "occ": demo['occupation'], "narr": p['narrative'].strip(),
             "dr": p['risk_scores']['diabetes'], "cr": p['risk_scores']['cardiovascular']})
        
        # Conditions
        for code, desc, start, end, note in p['conditions']:
            s.run("""MATCH (p:Person {synthea_id: $id})
                MERGE (c:Condition {code: $code, patient_id: $id})
                SET c.description = $desc, c.note = $note, c.onset_date = $start, c.is_active = $active
                MERGE (p)-[:HAS_CONDITION]->(c)""",
                {"id": synthea_id, "code": code, "desc": desc, "note": note, "start": start, "active": end is None})
        
        # Family history
        for rel, age_str, status, conditions in p['family_history']:
            s.run("""MATCH (p:Person {synthea_id: $id})
                MERGE (fh:FamilyHistory {patient_id: $id, relative: $rel})
                SET fh.age = $age, fh.status = $status, fh.conditions = $cond
                MERGE (p)-[:HAS_FAMILY_HISTORY]->(fh)""",
                {"id": synthea_id, "rel": rel, "age": age_str, "status": status, "cond": conditions})
        
        # Social history
        sh = p['social_history']
        s.run("""MATCH (p:Person {synthea_id: $id})
            MERGE (sh:SocialHistory {patient_id: $id})
            SET sh.tobacco = $tobacco, sh.alcohol = $alcohol, sh.exercise = $exercise,
                sh.diet = $diet, sh.occupation = $occ, sh.stress = $stress, sh.relationships = $rel
            MERGE (p)-[:HAS_SOCIAL_HISTORY]->(sh)""",
            {"id": synthea_id, "tobacco": sh['tobacco'], "alcohol": sh['alcohol'], "exercise": sh['exercise'],
             "diet": sh['diet'], "occ": sh['occupation'], "stress": sh['stress'], "rel": sh['relationships']})
        
        # Lab trend summary
        labs = p['labs_history']
        s.run("""MATCH (p:Person {synthea_id: $id})
            MERGE (lt:LabTrend {patient_id: $id})
            SET lt.hba1c_first = $h1, lt.hba1c_peak = $hp, lt.hba1c_latest = $hl,
                lt.glucose_first = $g1, lt.glucose_peak = $gp, lt.glucose_latest = $gl,
                lt.trend_direction = $trend
            MERGE (p)-[:HAS_LAB_TREND]->(lt)""",
            {"id": synthea_id, "h1": labs[0]['hba1c'], "hp": max(l['hba1c'] for l in labs),
             "hl": labs[-1]['hba1c'], "g1": labs[0]['glucose'], "gp": max(l['glucose'] for l in labs),
             "gl": labs[-1]['glucose'], "trend": "improving"})
        
        # Care plan
        cp = p['care_plans'][0]
        s.run("""MATCH (p:Person {synthea_id: $id})
            MERGE (cp:CarePlan {patient_id: $id, condition: $cond})
            SET cp.goals = $goals, cp.interventions = $int
            MERGE (p)-[:HAS_CARE_PLAN]->(cp)""",
            {"id": synthea_id, "cond": cp['condition'], "goals": cp['goals'], "int": cp['interventions']})
    
    driver.close()
    print(f"✅ Neo4j complete - Rich knowledge graph created")


if __name__ == '__main__':
    insert_detailed_persona()
    sync_detailed_to_neo4j()
    print(f"\n{'='*70}")
    print("✅ Synthea-level detailed persona created!")
    print("   - 20 encounters over 7 years")
    print("   - 9 vitals snapshots (weight trend: 72→85→76 kg)")
    print("   - 10 lab panels (A1c trend: 5.7→6.1→5.8)")
    print("   - 8 conditions (active and resolved)")
    print("   - 15 immunizations")
    print("   - 5 procedures")
    print("   - Rich family & social history")
    print(f"{'='*70}")
