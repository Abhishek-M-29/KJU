#!/usr/bin/env python3
"""
Nuanced Patient Personas - Varied Disease Profiles
===================================================
- Diabetes ONLY (healthy heart)
- CVD ONLY (no diabetes)
- Healthy with noisy data
- Mixed profiles
"""

import mariadb
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

DB_HOST, DB_USER, DB_PASSWORD = os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD')
DB_NAME, DB_PORT = os.getenv('DB_NAME'), int(os.getenv('DB_PORT', 3305))
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
AURA_USER, AURA_PASSWORD = os.getenv('AURA_USER', 'neo4j'), os.getenv('AURA_PASSWORD')

PERSONAS = [
    # ========== DIABETES ONLY - Healthy Heart ==========
    {
        "id": "persona-d01-diabetes-only",
        "demographics": {"first_name": "Lakshmi", "last_name": "Venkatesh", "birthdate": "1962-05-14", "gender": "F",
            "race": "Asian", "ethnicity": "Non-Hispanic", "city": "Houston", "state": "Texas", "income": 72000},
        "narrative": """Lakshmi is a 63-year-old Indian-American retired pharmacist with well-controlled Type 2 diabetes 
        diagnosed 12 years ago. Despite her diabetes, she has excellent cardiovascular health - normal BP, optimal 
        cholesterol, no family history of heart disease. She walks 45 min daily, follows a vegetarian diet, meditates.
        Her diabetes is managed with metformin alone. She monitors her glucose religiously and keeps detailed logs.
        Chief complaints: Routine diabetes follow-up, occasional foot tingling, wants to discuss if she can reduce meds.""",
        "risk_scores": {"diabetes": 6, "cardiovascular": 2},
        "vitals": {"height_cm": 158, "weight_kg": 62, "bp_systolic": 118, "bp_diastolic": 74, "heart_rate": 68},
        "labs": {"hba1c": 6.8, "fasting_glucose": 128, "total_cholesterol": 175, "ldl": 95, "hdl": 65, "triglycerides": 85},
        "conditions": [("E11.9", "Type 2 diabetes mellitus", "2014-03-20", None),
                       ("G62.9", "Mild peripheral neuropathy", "2022-08-15", None),
                       ("H52.4", "Presbyopia", "2018-06-10", None)],
        "medications": [("Metformin 500mg", "314076", "twice daily")],
        "lifestyle": {"smoking_status": "never", "smoking_pack_years": 0, "alcohol_use": "never",
                      "exercise_frequency": "daily", "diet_quality": "excellent"},
        "family_history": [("Mother", "Type 2 diabetes", "Living, 88"), ("Father", "Healthy", "Died 85, natural causes")],
    },
    
    # ========== CVD ONLY - No Diabetes ==========
    {
        "id": "persona-c01-cvd-only",
        "demographics": {"first_name": "Frank", "last_name": "Kowalski", "birthdate": "1956-11-22", "gender": "M",
            "race": "White", "ethnicity": "Non-Hispanic", "city": "Pittsburgh", "state": "Pennsylvania", "income": 48000},
        "narrative": """Frank is a 69-year-old retired steelworker with coronary artery disease and a history of CABG 
        (triple bypass) 8 years ago. Despite his heart disease, his glucose has always been completely normal - 
        HbA1c consistently 5.0-5.2. He quit smoking after his bypass, walks daily, but still eats a traditional 
        Polish diet high in sodium. His BP is controlled on meds. His father and two brothers had heart attacks.
        Chief complaints: Stable angina on exertion, wants stress test clearance for grandson's wedding travel.""",
        "risk_scores": {"diabetes": 1, "cardiovascular": 8},
        "vitals": {"height_cm": 175, "weight_kg": 88, "bp_systolic": 132, "bp_diastolic": 82, "heart_rate": 62},
        "labs": {"hba1c": 5.1, "fasting_glucose": 88, "total_cholesterol": 165, "ldl": 70, "hdl": 52, "triglycerides": 120},
        "conditions": [("I25.10", "CAD s/p CABG", "2018-02-15", None), ("I10", "Essential hypertension", "2005-06-20", None),
                       ("Z95.1", "Status post CABG", "2018-02-20", None), ("I20.9", "Stable angina", "2020-04-10", None)],
        "medications": [("Metoprolol 50mg", "866514", "twice daily"), ("Lisinopril 20mg", "314077", "daily"),
                        ("Atorvastatin 80mg", "617311", "daily"), ("Aspirin 81mg", "198466", "daily")],
        "lifestyle": {"smoking_status": "former", "smoking_pack_years": 30, "alcohol_use": "rare",
                      "exercise_frequency": "regularly", "diet_quality": "fair"},
        "family_history": [("Father", "MI at 55", "Died 58"), ("Brother", "MI, CABG", "Living, 72")],
    },
    
    # ========== HEALTHY WITH NOISY DATA ==========
    {
        "id": "persona-h01-healthy-noisy",
        "demographics": {"first_name": "Marcus", "last_name": "Thompson", "birthdate": "1988-03-08", "gender": "M",
            "race": "Black", "ethnicity": "Non-Hispanic", "city": "Chicago", "state": "Illinois", "income": 95000},
        "narrative": """Marcus is a 37-year-old healthy software developer. No diabetes, no heart disease, no significant 
        conditions. However, his data has realistic "noise": slightly elevated BP today (white coat effect), one high 
        glucose reading from last month when he was sick with flu, and borderline cholesterol from holiday eating.
        His repeat labs are all normal. He exercises, eats well, doesn't smoke. Anxiety about health runs in family.
        Chief complaints: Annual physical, worried because one glucose was 115 (normally 85-90). Reassurance needed.""",
        "risk_scores": {"diabetes": 2, "cardiovascular": 2},
        "vitals": {"height_cm": 185, "weight_kg": 82, "bp_systolic": 128, "bp_diastolic": 82, "heart_rate": 76},
        "labs": {"hba1c": 5.3, "fasting_glucose": 92, "total_cholesterol": 205, "ldl": 125, "hdl": 58, "triglycerides": 110},
        "conditions": [("Z00.00", "Annual wellness exam", "2026-02-01", "2026-02-01"),
                       ("F41.1", "Generalized anxiety disorder - mild", "2023-05-15", None)],
        "medications": [],
        "lifestyle": {"smoking_status": "never", "smoking_pack_years": 0, "alcohol_use": "occasional",
                      "exercise_frequency": "regularly", "diet_quality": "good"},
        "family_history": [("Father", "Healthy", "Living, 65"), ("Mother", "Anxiety", "Living, 63")],
    },
    
    # ========== PREDIABETES + MILD HYPERTENSION ==========
    {
        "id": "persona-pd01-prediabetes-htn",
        "demographics": {"first_name": "Carmen", "last_name": "Delgado", "birthdate": "1975-09-30", "gender": "F",
            "race": "White", "ethnicity": "Hispanic", "city": "Miami", "state": "Florida", "income": 55000},
        "narrative": """Carmen is a 50-year-old Cuban-American hotel manager with prediabetes (HbA1c 5.9) and Stage 1 
        hypertension. She's in the "gray zone" - not diabetic, not severe CVD, but at crossroads. Overweight, stressful 
        job, family history of both conditions. She's motivated to change - started walking, reduced carbs. 
        No medications yet - doctor gave her 3 months to try lifestyle changes before starting metformin.
        Chief complaints: Follow-up for prediabetes, wants to know if lifestyle changes are working.""",
        "risk_scores": {"diabetes": 5, "cardiovascular": 4},
        "vitals": {"height_cm": 163, "weight_kg": 78, "bp_systolic": 136, "bp_diastolic": 86, "heart_rate": 78},
        "labs": {"hba1c": 5.9, "fasting_glucose": 108, "total_cholesterol": 212, "ldl": 130, "hdl": 48, "triglycerides": 170},
        "conditions": [("R73.03", "Prediabetes", "2025-08-15", None), ("I10", "Stage 1 hypertension", "2025-08-15", None),
                       ("E66.9", "Overweight", "2020-03-10", None)],
        "medications": [],
        "lifestyle": {"smoking_status": "never", "smoking_pack_years": 0, "alcohol_use": "occasional",
                      "exercise_frequency": "sometimes", "diet_quality": "fair"},
        "family_history": [("Mother", "Type 2 diabetes, HTN", "Living, 75"), ("Father", "MI at 62", "Died 68")],
    },
    
    # ========== ATHLETE WITH FAMILY HISTORY ==========
    {
        "id": "persona-a01-athlete-fhx",
        "demographics": {"first_name": "Tyler", "last_name": "Jackson", "birthdate": "1992-07-12", "gender": "M",
            "race": "Black", "ethnicity": "Non-Hispanic", "city": "Atlanta", "state": "Georgia", "income": 125000},
        "narrative": """Tyler is a 33-year-old former college basketball player, now a fitness trainer. Perfect health 
        metrics - athletic bradycardia (HR 48), optimal BP, HDL of 78. However, terrifying family history: father died 
        of MI at 45, mother has diabetes, brother had CABG at 38. Tyler is obsessive about prevention - gets cardiac 
        CT every 2 years, tracks everything. His coronary calcium score is 0. No disease, all healthy data, but high-risk genes.
        Chief complaints: Wants advanced cardiac screening, asking about genetic testing for familial hypercholesterolemia.""",
        "risk_scores": {"diabetes": 3, "cardiovascular": 3},
        "vitals": {"height_cm": 193, "weight_kg": 95, "bp_systolic": 112, "bp_diastolic": 68, "heart_rate": 48},
        "labs": {"hba1c": 5.0, "fasting_glucose": 82, "total_cholesterol": 168, "ldl": 85, "hdl": 78, "triglycerides": 52},
        "conditions": [("Z82.49", "Family history of heart disease", "2020-01-15", None),
                       ("Z83.3", "Family history of diabetes", "2020-01-15", None)],
        "medications": [],
        "lifestyle": {"smoking_status": "never", "smoking_pack_years": 0, "alcohol_use": "rare",
                      "exercise_frequency": "daily", "diet_quality": "excellent"},
        "family_history": [("Father", "MI", "Died 45"), ("Mother", "T2DM", "Living, 60"), ("Brother", "CABG at 38", "Living, 40")],
    },
    
    # ========== ELDERLY DIABETIC - WELL CONTROLLED ==========
    {
        "id": "persona-d02-elderly-controlled",
        "demographics": {"first_name": "Dorothy", "last_name": "Henderson", "birthdate": "1940-12-25", "gender": "F",
            "race": "White", "ethnicity": "Non-Hispanic", "city": "Portland", "state": "Oregon", "income": 38000},
        "narrative": """Dorothy is an 85-year-old retired school teacher with Type 2 diabetes for 30 years. Remarkably, 
        she has avoided major complications through strict adherence. Lives independently, gardens daily, sharp mind.
        Only mild retinopathy. A1c consistently 6.5-7.0. Widowed 10 years, active church community. Takes 4 meds.
        Chief complaints: Routine follow-up, discussing goals of care, wants to stay independent.""",
        "risk_scores": {"diabetes": 5, "cardiovascular": 3},
        "vitals": {"height_cm": 160, "weight_kg": 58, "bp_systolic": 128, "bp_diastolic": 72, "heart_rate": 72},
        "labs": {"hba1c": 6.9, "fasting_glucose": 118, "total_cholesterol": 188, "ldl": 102, "hdl": 58, "triglycerides": 95},
        "conditions": [("E11.319", "T2DM with mild retinopathy", "1996-04-10", None), ("M81.0", "Osteoporosis", "2015-08-20", None)],
        "medications": [("Metformin 500mg", "314076", "twice daily"), ("Lisinopril 5mg", "314077", "daily")],
        "lifestyle": {"smoking_status": "never", "smoking_pack_years": 0, "alcohol_use": "rare", "exercise_frequency": "daily", "diet_quality": "good"},
        "family_history": [("Mother", "T2DM", "Died 92"), ("Sister", "T2DM", "Living, 82")],
    },
    
    # ========== YOUNG ONSET DIABETES - NO CVD ==========
    {
        "id": "persona-d03-young-onset",
        "demographics": {"first_name": "Brandon", "last_name": "Nguyen", "birthdate": "1998-06-18", "gender": "M",
            "race": "Asian", "ethnicity": "Non-Hispanic", "city": "San Jose", "state": "California", "income": 115000},
        "narrative": """Brandon is a 27-year-old software engineer diagnosed with Type 2 diabetes at age 24 - unusually young.
        BMI was 32 at diagnosis, now 28 after lifestyle changes. No CVD risk factors except diabetes. Perfect BP, excellent
        HDL. On metformin + Ozempic, A1c dropped from 9.2 to 6.4. Very tech-savvy, uses CGM, tracks everything in apps.
        Chief complaints: Wants to come off Ozempic, asking about remission possibility with more weight loss.""",
        "risk_scores": {"diabetes": 7, "cardiovascular": 2},
        "vitals": {"height_cm": 175, "weight_kg": 86, "bp_systolic": 116, "bp_diastolic": 72, "heart_rate": 70},
        "labs": {"hba1c": 6.4, "fasting_glucose": 112, "total_cholesterol": 165, "ldl": 88, "hdl": 62, "triglycerides": 75},
        "conditions": [("E11.9", "Type 2 diabetes - young onset", "2022-09-15", None)],
        "medications": [("Metformin 1000mg", "314076", "twice daily"), ("Semaglutide 0.5mg", "1991302", "weekly")],
        "lifestyle": {"smoking_status": "never", "smoking_pack_years": 0, "alcohol_use": "rare", "exercise_frequency": "regularly", "diet_quality": "good"},
        "family_history": [("Father", "T2DM at 40", "Living, 55"), ("Grandmother", "T2DM", "Died 78")],
    },
    
    # ========== AFIB ONLY - NO DIABETES ==========
    {
        "id": "persona-c02-afib-only",
        "demographics": {"first_name": "Richard", "last_name": "Sullivan", "birthdate": "1958-02-14", "gender": "M",
            "race": "White", "ethnicity": "Non-Hispanic", "city": "Boston", "state": "Massachusetts", "income": 92000},
        "narrative": """Richard is a 68-year-old attorney with paroxysmal atrial fibrillation diagnosed 5 years ago. 
        On Eliquis and metoprolol, rate well controlled. No diabetes - glucose always normal (A1c 5.2). Mild HTN. 
        Former marathon runner, still jogs 3x/week. Moderate alcohol use may have contributed to AFib. CHADS2-VASc = 2.
        Chief complaints: Palpitation episode last week lasting 4 hours, resolved spontaneously. Stress from work.""",
        "risk_scores": {"diabetes": 1, "cardiovascular": 6},
        "vitals": {"height_cm": 180, "weight_kg": 82, "bp_systolic": 134, "bp_diastolic": 82, "heart_rate": 68},
        "labs": {"hba1c": 5.2, "fasting_glucose": 92, "total_cholesterol": 195, "ldl": 115, "hdl": 55, "triglycerides": 125},
        "conditions": [("I48.0", "Paroxysmal atrial fibrillation", "2021-03-22", None), ("I10", "Essential HTN", "2018-06-15", None)],
        "medications": [("Apixaban 5mg", "1364430", "twice daily"), ("Metoprolol 25mg", "866514", "twice daily")],
        "lifestyle": {"smoking_status": "never", "smoking_pack_years": 0, "alcohol_use": "moderate", "exercise_frequency": "regularly", "diet_quality": "good"},
        "family_history": [("Father", "AFib at 70", "Living, 90"), ("Mother", "Healthy", "Living, 88")],
    },
    
    # ========== POST-MI RECOVERY - EXCELLENT REHAB ==========
    {
        "id": "persona-c03-post-mi-rehab",
        "demographics": {"first_name": "James", "last_name": "O'Connor", "birthdate": "1965-08-30", "gender": "M",
            "race": "White", "ethnicity": "Non-Hispanic", "city": "Cleveland", "state": "Ohio", "income": 78000},
        "narrative": """James is a 60-year-old firefighter who had a STEMI 2 years ago - complete RCA occlusion, stented.
        Quit smoking cold turkey that day (25 pack-year), completed cardiac rehab, lost 40 lbs, now runs 5Ks. His 
        transformation is remarkable - LDL went from 165 to 58 on Repatha. No diabetes. EF recovered from 40% to 55%.
        Chief complaints: Clearance for return to full firefighter duties, feeling better than he did at 40.""",
        "risk_scores": {"diabetes": 2, "cardiovascular": 5},
        "vitals": {"height_cm": 183, "weight_kg": 84, "bp_systolic": 118, "bp_diastolic": 74, "heart_rate": 58},
        "labs": {"hba1c": 5.4, "fasting_glucose": 88, "total_cholesterol": 128, "ldl": 58, "hdl": 52, "triglycerides": 90},
        "conditions": [("I21.11", "STEMI - RCA, s/p PCI", "2024-01-15", "2024-01-20"), ("Z95.5", "Status post coronary stent", "2024-01-15", None)],
        "medications": [("Evolocumab 140mg", "1657973", "every 2 weeks"), ("Atorvastatin 40mg", "617311", "daily"), ("Aspirin 81mg", "198466", "daily"), ("Clopidogrel 75mg", "309362", "daily")],
        "lifestyle": {"smoking_status": "former", "smoking_pack_years": 25, "alcohol_use": "rare", "exercise_frequency": "daily", "diet_quality": "excellent"},
        "family_history": [("Father", "MI at 58", "Died 62"), ("Uncle", "MI at 55", "Living, 70")],
    },
]

def get_db(): return mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)
def calc_age(bd): return (date.today() - datetime.strptime(bd, "%Y-%m-%d").date()).days // 365

def insert_persona(p):
    conn, synthea_id, demo, vitals, labs = get_db(), p["id"], p["demographics"], p["vitals"], p["labs"]
    cur = conn.cursor()
    print(f"\n📋 {demo['first_name']} {demo['last_name']} (D:{p['risk_scores']['diabetes']}/10, CVD:{p['risk_scores']['cardiovascular']}/10)")
    
    cur.execute("INSERT INTO Synthea_Patient (synthea_id,first_name,last_name,birthdate,gender,race,ethnicity,city,state,income) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE first_name=VALUES(first_name)",
        (synthea_id, demo['first_name'], demo['last_name'], demo['birthdate'], demo['gender'], demo.get('race'), demo.get('ethnicity'), demo.get('city'), demo.get('state'), demo.get('income')))
    
    for code, desc, start, end in p['conditions']:
        cur.execute("INSERT INTO Synthea_Condition (synthea_patient_id,code,description,start_date,stop_date,is_active) VALUES (%s,%s,%s,%s,%s,%s)", (synthea_id, code, desc, start, end, 1 if not end else 0))
    
    for med, code, dose in p['medications']:
        cur.execute("INSERT INTO Synthea_Medication (synthea_patient_id,code,description,start_datetime,is_active) VALUES (%s,%s,%s,%s,1)", (synthea_id, code, f"{med} - {dose}", datetime.now()))
    
    obs_date = datetime.now()
    for k, v in {**vitals, **labs}.items():
        cur.execute("INSERT INTO Synthea_Observation (synthea_patient_id,observation_date,code,description,value,units,category) VALUES (%s,%s,%s,%s,%s,%s,%s)", 
            (synthea_id, obs_date, k[:10], k.replace('_',' ').title(), str(v), 'unit', 'vital-signs' if k in vitals else 'laboratory'))
    
    age, bmi = calc_age(demo['birthdate']), vitals['weight_kg'] / (vitals['height_cm']/100)**2
    conds = ' '.join([c[1].lower() for c in p['conditions']])
    ls = p['lifestyle']
    cur.execute("""INSERT INTO Patient_AI_Features (synthea_patient_id,age_years,gender_numeric,height_cm,weight_kg,bmi,bp_systolic,bp_diastolic,
        cholesterol_level,glucose_level,is_smoker,alcohol_use,physical_activity,has_hypertension,has_heart_disease,smoking_history,hba1c_level,blood_glucose_fasting)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE age_years=VALUES(age_years)""",
        (synthea_id, age, 1 if demo['gender']=='F' else 2, vitals['height_cm'], vitals['weight_kg'], round(bmi,2), vitals['bp_systolic'], vitals['bp_diastolic'],
         3 if labs['total_cholesterol']>=240 else 2 if labs['total_cholesterol']>=200 else 1, 3 if labs['fasting_glucose']>=126 else 2 if labs['fasting_glucose']>=100 else 1,
         1 if ls['smoking_status']=='current' else 0, 1 if ls['alcohol_use'] in ['moderate','heavy'] else 0, 1 if ls['exercise_frequency'] in ['regularly','daily'] else 0,
         1 if 'hypertension' in conds else 0, 1 if any(x in conds for x in ['heart','cardiac','coronary','mi','cabg']) else 0, ls['smoking_status'], labs['hba1c'], labs['fasting_glucose']))
    
    conn.commit(); cur.close(); conn.close(); print(f"   ✅ MariaDB done")

def sync_neo4j(p):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(AURA_USER, AURA_PASSWORD))
    synthea_id, demo, vitals, labs, rs = p["id"], p["demographics"], p["vitals"], p["labs"], p["risk_scores"]
    age, bmi = calc_age(demo['birthdate']), vitals['weight_kg'] / (vitals['height_cm']/100)**2
    
    with driver.session() as s:
        s.run("""MERGE (p:Person:Patient {synthea_id:$id}) SET p.first_name=$fn, p.last_name=$ln, p.full_name=$fn+' '+$ln,
            p.birthdate=$bd, p.age=$age, p.gender=$g, p.narrative=$narr, p.diabetes_risk=$dr, p.cvd_risk=$cr, p.is_persona=true""",
            {"id":synthea_id,"fn":demo['first_name'],"ln":demo['last_name'],"bd":demo['birthdate'],"age":age,"g":demo['gender'],"narr":p['narrative'].strip(),"dr":rs['diabetes'],"cr":rs['cardiovascular']})
        
        s.run("""MATCH (p:Person {synthea_id:$id}) MERGE (ai:AIFeatureSet {patient_id:$id}) SET ai.age=$age, ai.bmi=$bmi,
            ai.bp_systolic=$bps, ai.hba1c=$hba1c, ai.diabetes_risk_score=$dr, ai.cvd_risk_score=$cr MERGE (p)-[:HAS_AI_FEATURES]->(ai)""",
            {"id":synthea_id,"age":age,"bmi":round(bmi,2),"bps":vitals['bp_systolic'],"hba1c":labs['hba1c'],"dr":rs['diabetes'],"cr":rs['cardiovascular']})
        
        for code, desc, _, end in p['conditions']:
            s.run("MATCH (p:Person {synthea_id:$id}) MERGE (c:Condition {code:$c,patient_id:$id}) SET c.description=$d,c.is_active=$a MERGE (p)-[:HAS_CONDITION]->(c)",
                {"id":synthea_id,"c":code,"d":desc,"a":end is None})
        
        for rel, cond, _ in p['family_history']:
            s.run("MATCH (p:Person {synthea_id:$id}) MERGE (fh:FamilyHistory {patient_id:$id,relative:$r}) SET fh.conditions=$c MERGE (p)-[:HAS_FAMILY_HISTORY]->(fh)",
                {"id":synthea_id,"r":rel,"c":cond})
        
        ls = p['lifestyle']
        s.run("MATCH (p:Person {synthea_id:$id}) MERGE (l:Lifestyle {patient_id:$id}) SET l.smoking_status=$sm,l.exercise_frequency=$ex,l.diet_quality=$di MERGE (p)-[:HAS_LIFESTYLE]->(l)",
            {"id":synthea_id,"sm":ls['smoking_status'],"ex":ls['exercise_frequency'],"di":ls['diet_quality']})
    
    driver.close(); print(f"   ✅ Neo4j done")

if __name__ == '__main__':
    print("🏥 Creating 5 Nuanced Personas (Varied Disease Profiles)\n" + "="*55)
    for p in PERSONAS:
        insert_persona(p)
        sync_neo4j(p)
    print("\n✅ All 5 nuanced personas created!")
