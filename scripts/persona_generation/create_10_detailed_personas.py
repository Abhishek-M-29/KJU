#!/usr/bin/env python3
"""
10 Synthea-Level Detailed Personas - Diverse Health Conditions
==============================================================
Each has: time-series vitals/labs, encounters, conditions, meds, family hx
"""

import mariadb, os
from datetime import datetime, date
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
DB_HOST, DB_USER, DB_PASSWORD = os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD')
DB_NAME, DB_PORT = os.getenv('DB_NAME'), int(os.getenv('DB_PORT', 3305))
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
AURA_USER, AURA_PASSWORD = os.getenv('AURA_USER', 'neo4j'), os.getenv('AURA_PASSWORD')

PERSONAS = [
# ============================================================================
# 1. COPD + CHF (No Diabetes) - Complex cardiopulmonary
# ============================================================================
{
    "id": "persona-det-001-copd-chf",
    "demo": {"first": "Walter", "last": "Brennan", "dob": "1948-06-20", "gender": "M", "city": "Louisville", "state": "Kentucky", "occupation": "Retired coal miner"},
    "narrative": """Walter is a 77-year-old former coal miner with severe COPD (GOLD Stage 3) and CHF with reduced EF (35%).
    45 pack-year smoking history, quit 10 years ago after first CHF hospitalization. On home oxygen 2L. 
    Three hospitalizations in past 2 years for COPD exacerbations. No diabetes - glucose always normal.
    Wife died last year, lives alone, daughter checks on him daily. Limited mobility due to dyspnea.""",
    "risk": {"diabetes": 1, "cardiovascular": 9},
    "vitals_trend": [
        {"date": "2022-03", "wt": 78, "bp_s": 128, "bp_d": 72, "hr": 88, "o2": 91},
        {"date": "2023-03", "wt": 75, "bp_s": 122, "bp_d": 68, "hr": 92, "o2": 89},
        {"date": "2024-03", "wt": 72, "bp_s": 118, "bp_d": 65, "hr": 95, "o2": 88},
        {"date": "2025-02", "wt": 70, "bp_s": 115, "bp_d": 62, "hr": 98, "o2": 87},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 92, "hba1c": 5.2, "bnp": 450, "creat": 1.2, "chol": 165},
        {"date": "2023-03", "glucose": 88, "hba1c": 5.1, "bnp": 680, "creat": 1.4, "chol": 158},
        {"date": "2024-03", "glucose": 95, "hba1c": 5.3, "bnp": 820, "creat": 1.5, "chol": 152},
        {"date": "2025-02", "glucose": 90, "hba1c": 5.2, "bnp": 950, "creat": 1.6, "chol": 148},
    ],
    "conditions": [("J44.1", "COPD GOLD Stage 3", "2015"), ("I50.22", "CHF reduced EF", "2018"), ("I10", "HTN", "2010"), ("F32.1", "Depression", "2024")],
    "meds": [("Tiotropium 18mcg", "daily"), ("Fluticasone/Salmeterol", "bid"), ("Furosemide 40mg", "daily"), ("Carvedilol 12.5mg", "bid"), ("Lisinopril 10mg", "daily")],
    "family_hx": [("Father", "Lung cancer", "Died 62"), ("Mother", "CHF", "Died 78")],
},

# ============================================================================
# 2. Type 1 Diabetes (Young) - Autoimmune, no CVD
# ============================================================================
{
    "id": "persona-det-002-t1dm",
    "demo": {"first": "Emma", "last": "Lindqvist", "dob": "2000-08-12", "gender": "F", "city": "Portland", "state": "Oregon", "occupation": "Graduate student"},
    "narrative": """Emma is a 25-year-old PhD student with Type 1 diabetes since age 8. Uses insulin pump + CGM.
    Excellent control most of the time (A1c 6.5-7.0) but occasional hypoglycemia. No complications yet.
    Cardiovascular perfectly healthy - BP 110/68, cholesterol excellent. Runs half-marathons.
    Vegetarian, very health-conscious. Anxiety about long-term complications.""",
    "risk": {"diabetes": 7, "cardiovascular": 1},
    "vitals_trend": [
        {"date": "2022-03", "wt": 58, "bp_s": 108, "bp_d": 66, "hr": 62, "o2": 99},
        {"date": "2023-03", "wt": 59, "bp_s": 110, "bp_d": 68, "hr": 60, "o2": 99},
        {"date": "2024-03", "wt": 58, "bp_s": 108, "bp_d": 65, "hr": 58, "o2": 99},
        {"date": "2025-02", "wt": 59, "bp_s": 112, "bp_d": 70, "hr": 56, "o2": 99},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 142, "hba1c": 6.8, "chol": 158, "ldl": 82, "hdl": 72, "creat": 0.7},
        {"date": "2023-03", "glucose": 128, "hba1c": 6.5, "chol": 162, "ldl": 85, "hdl": 70, "creat": 0.7},
        {"date": "2024-03", "glucose": 155, "hba1c": 7.1, "chol": 155, "ldl": 80, "hdl": 68, "creat": 0.7},
        {"date": "2025-02", "glucose": 135, "hba1c": 6.7, "chol": 160, "ldl": 82, "hdl": 72, "creat": 0.7},
    ],
    "conditions": [("E10.9", "Type 1 diabetes", "2008"), ("F41.1", "GAD", "2020")],
    "meds": [("Insulin pump (Humalog)", "continuous"), ("Escitalopram 10mg", "daily")],
    "family_hx": [("Mother", "Hypothyroidism", "Living"), ("Grandmother", "T1DM", "Living 78")],
},

# ============================================================================
# 3. Chronic Kidney Disease Stage 4 - Pre-dialysis
# ============================================================================
{
    "id": "persona-det-003-ckd4",
    "demo": {"first": "Jerome", "last": "Washington", "dob": "1960-02-28", "gender": "M", "city": "Baltimore", "state": "Maryland", "occupation": "Retired postal worker"},
    "narrative": """Jerome is a 65-year-old with CKD Stage 4 (eGFR 22) from hypertensive nephrosclerosis. 
    Prediabetic (A1c 5.8) but not diabetic. Severe HTN for 30 years, poorly controlled until recent years.
    Seeing nephrologist, preparing for possible dialysis in 1-2 years. Anemia on EPO.
    Strong church community support. Wife very involved in his care.""",
    "risk": {"diabetes": 4, "cardiovascular": 8},
    "vitals_trend": [
        {"date": "2022-03", "wt": 95, "bp_s": 158, "bp_d": 92, "hr": 78, "o2": 96},
        {"date": "2023-03", "wt": 92, "bp_s": 148, "bp_d": 88, "hr": 80, "o2": 96},
        {"date": "2024-03", "wt": 90, "bp_s": 142, "bp_d": 85, "hr": 82, "o2": 95},
        {"date": "2025-02", "wt": 88, "bp_s": 138, "bp_d": 82, "hr": 78, "o2": 95},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 105, "hba1c": 5.7, "creat": 2.8, "egfr": 28, "hgb": 10.2, "k": 4.8},
        {"date": "2023-03", "glucose": 108, "hba1c": 5.8, "creat": 3.2, "egfr": 25, "hgb": 9.8, "k": 5.0},
        {"date": "2024-03", "glucose": 102, "hba1c": 5.7, "creat": 3.8, "egfr": 22, "hgb": 9.5, "k": 5.2},
        {"date": "2025-02", "glucose": 110, "hba1c": 5.9, "creat": 4.1, "egfr": 20, "hgb": 9.2, "k": 5.4},
    ],
    "conditions": [("N18.4", "CKD Stage 4", "2022"), ("I10", "Severe HTN", "1995"), ("D63.1", "Anemia of CKD", "2023"), ("R73.03", "Prediabetes", "2024")],
    "meds": [("Amlodipine 10mg", "daily"), ("Losartan 100mg", "daily"), ("Labetalol 200mg", "bid"), ("Epoetin alfa", "weekly"), ("Sodium bicarbonate", "tid")],
    "family_hx": [("Father", "HTN, Stroke", "Died 68"), ("Mother", "ESRD on dialysis", "Died 72"), ("Brother", "CKD Stage 3", "Living 62")],
},

# ============================================================================
# 4. Rheumatoid Arthritis + Osteoporosis - Autoimmune, steroid complications
# ============================================================================
{
    "id": "persona-det-004-ra",
    "demo": {"first": "Kathleen", "last": "Murphy", "dob": "1958-11-15", "gender": "F", "city": "Boston", "state": "Massachusetts", "occupation": "Retired librarian"},
    "narrative": """Kathleen is a 67-year-old with severe RA for 25 years, now on biologics (Humira). 
    Joint deformities in hands. Steroid-induced osteoporosis with T-score -2.8, had vertebral fracture.
    No diabetes, no heart disease. Glucose and BP always normal. Former smoker (quit 20 yrs ago).
    Lives with sister. Active in book club. Pain affects quality of life.""",
    "risk": {"diabetes": 2, "cardiovascular": 3},
    "vitals_trend": [
        {"date": "2022-03", "wt": 62, "bp_s": 118, "bp_d": 72, "hr": 72, "o2": 98},
        {"date": "2023-03", "wt": 60, "bp_s": 120, "bp_d": 74, "hr": 74, "o2": 98},
        {"date": "2024-03", "wt": 58, "bp_s": 116, "bp_d": 70, "hr": 70, "o2": 98},
        {"date": "2025-02", "wt": 57, "bp_s": 118, "bp_d": 72, "hr": 72, "o2": 98},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 92, "hba1c": 5.3, "crp": 12, "esr": 45, "chol": 185, "vitd": 28},
        {"date": "2023-03", "glucose": 88, "hba1c": 5.2, "crp": 8, "esr": 35, "chol": 182, "vitd": 32},
        {"date": "2024-03", "glucose": 95, "hba1c": 5.4, "crp": 5, "esr": 28, "chol": 178, "vitd": 38},
        {"date": "2025-02", "glucose": 90, "hba1c": 5.3, "crp": 4, "esr": 22, "chol": 175, "vitd": 42},
    ],
    "conditions": [("M05.79", "RA seropositive", "2000"), ("M80.08", "Osteoporosis with fracture", "2022"), ("M48.56", "Vertebral compression fx", "2022")],
    "meds": [("Adalimumab 40mg", "every 2 weeks"), ("Methotrexate 15mg", "weekly"), ("Prednisone 5mg", "daily"), ("Alendronate 70mg", "weekly"), ("Calcium/VitD", "daily")],
    "family_hx": [("Sister", "RA", "Living 65"), ("Mother", "Osteoporosis", "Died 88")],
},

# ============================================================================
# 5. Bipolar Disorder + Metabolic Syndrome - Psych meds causing metabolic issues
# ============================================================================
{
    "id": "persona-det-005-bipolar",
    "demo": {"first": "Jason", "last": "Rivera", "dob": "1985-04-22", "gender": "M", "city": "Phoenix", "state": "Arizona", "occupation": "Graphic designer"},
    "narrative": """Jason is a 40-year-old with Bipolar I disorder, stable on lithium + quetiapine for 8 years.
    Quetiapine caused 50lb weight gain - now BMI 34, prediabetes, hypertriglyceridemia. No frank diabetes yet.
    Lithium caused mild CKD (eGFR 58). Trying to lose weight but meds make it hard.
    Creative, talented designer. Supportive girlfriend. Last manic episode was 6 years ago.""",
    "risk": {"diabetes": 6, "cardiovascular": 5},
    "vitals_trend": [
        {"date": "2022-03", "wt": 102, "bp_s": 132, "bp_d": 84, "hr": 78, "o2": 97},
        {"date": "2023-03", "wt": 105, "bp_s": 136, "bp_d": 86, "hr": 80, "o2": 97},
        {"date": "2024-03", "wt": 108, "bp_s": 138, "bp_d": 88, "hr": 82, "o2": 96},
        {"date": "2025-02", "wt": 104, "bp_s": 134, "bp_d": 84, "hr": 78, "o2": 97},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 105, "hba1c": 5.7, "chol": 225, "trig": 280, "creat": 1.2, "lithium": 0.8},
        {"date": "2023-03", "glucose": 112, "hba1c": 5.9, "chol": 238, "trig": 320, "creat": 1.3, "lithium": 0.9},
        {"date": "2024-03", "glucose": 118, "hba1c": 6.1, "chol": 245, "trig": 350, "creat": 1.4, "lithium": 0.8},
        {"date": "2025-02", "glucose": 108, "hba1c": 5.8, "chol": 218, "trig": 265, "creat": 1.3, "lithium": 0.9},
    ],
    "conditions": [("F31.9", "Bipolar I disorder", "2012"), ("E88.81", "Metabolic syndrome", "2022"), ("R73.03", "Prediabetes", "2024"), ("N18.3", "CKD Stage 3a", "2023")],
    "meds": [("Lithium 900mg", "daily"), ("Quetiapine 300mg", "bedtime"), ("Metformin 500mg", "daily"), ("Fenofibrate 145mg", "daily")],
    "family_hx": [("Mother", "Bipolar", "Living 65"), ("Uncle", "Schizophrenia", "Living 58"), ("Father", "T2DM", "Living 68")],
},

# ============================================================================
# 6. Post-Stroke Recovery - Residual deficits, doing well
# ============================================================================
{
    "id": "persona-det-006-stroke",
    "demo": {"first": "Helen", "last": "Nakamura", "dob": "1952-09-08", "gender": "F", "city": "Seattle", "state": "Washington", "occupation": "Retired accountant"},
    "narrative": """Helen is a 73-year-old who had ischemic stroke (MCA) 3 years ago with left hemiparesis.
    Recovered well with PT/OT - walks with cane, regained most arm function. Speech fully recovered.
    AFib discovered as stroke cause - now on Eliquis. No diabetes. BP well controlled.
    Very motivated, does exercises daily. Husband is primary caregiver. Grandchildren visit weekly.""",
    "risk": {"diabetes": 2, "cardiovascular": 7},
    "vitals_trend": [
        {"date": "2022-03", "wt": 65, "bp_s": 142, "bp_d": 82, "hr": 78, "o2": 97},
        {"date": "2023-03", "wt": 63, "bp_s": 132, "bp_d": 78, "hr": 72, "o2": 98},
        {"date": "2024-03", "wt": 62, "bp_s": 128, "bp_d": 76, "hr": 70, "o2": 98},
        {"date": "2025-02", "wt": 61, "bp_s": 124, "bp_d": 74, "hr": 68, "o2": 98},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 95, "hba1c": 5.4, "chol": 198, "ldl": 115, "inr": 0, "creat": 0.9},
        {"date": "2023-03", "glucose": 92, "hba1c": 5.3, "chol": 178, "ldl": 95, "inr": 0, "creat": 0.9},
        {"date": "2024-03", "glucose": 88, "hba1c": 5.2, "chol": 168, "ldl": 85, "inr": 0, "creat": 0.8},
        {"date": "2025-02", "glucose": 90, "hba1c": 5.3, "chol": 165, "ldl": 82, "inr": 0, "creat": 0.8},
    ],
    "conditions": [("I63.512", "CVA with left hemiparesis", "2022"), ("I48.91", "AFib", "2022"), ("I10", "HTN", "2015")],
    "meds": [("Apixaban 5mg", "bid"), ("Lisinopril 20mg", "daily"), ("Atorvastatin 40mg", "daily"), ("Aspirin 81mg", "daily")],
    "family_hx": [("Father", "Stroke at 75", "Died 78"), ("Mother", "AFib", "Died 85")],
},

# ============================================================================
# 7. Liver Cirrhosis (NASH) - Non-alcoholic, metabolic
# ============================================================================
{
    "id": "persona-det-007-cirrhosis",
    "demo": {"first": "Roberto", "last": "Gonzalez", "dob": "1965-12-10", "gender": "M", "city": "Houston", "state": "Texas", "occupation": "Restaurant manager"},
    "narrative": """Roberto is a 60-year-old with NASH cirrhosis (Child-Pugh A, compensated). Never drank alcohol.
    T2DM for 15 years drove his fatty liver to cirrhosis. Now has portal HTN, small varices, mild ascites.
    Lost 40 lbs in past 2 years, A1c improved 9.0→7.2. Liver team considering transplant evaluation.
    Works part-time, very fatigued. Wife and adult children very supportive.""",
    "risk": {"diabetes": 8, "cardiovascular": 4},
    "vitals_trend": [
        {"date": "2022-03", "wt": 115, "bp_s": 128, "bp_d": 78, "hr": 82, "o2": 96},
        {"date": "2023-03", "wt": 102, "bp_s": 122, "bp_d": 74, "hr": 78, "o2": 97},
        {"date": "2024-03", "wt": 92, "bp_s": 118, "bp_d": 70, "hr": 75, "o2": 97},
        {"date": "2025-02", "wt": 88, "bp_s": 115, "bp_d": 68, "hr": 72, "o2": 97},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 185, "hba1c": 9.0, "alt": 68, "ast": 72, "plt": 95, "alb": 3.2, "inr": 1.3},
        {"date": "2023-03", "glucose": 155, "hba1c": 7.8, "alt": 52, "ast": 58, "plt": 88, "alb": 3.4, "inr": 1.2},
        {"date": "2024-03", "glucose": 138, "hba1c": 7.4, "alt": 42, "ast": 48, "plt": 82, "alb": 3.5, "inr": 1.2},
        {"date": "2025-02", "glucose": 128, "hba1c": 7.2, "alt": 38, "ast": 42, "plt": 78, "alb": 3.6, "inr": 1.1},
    ],
    "conditions": [("K74.69", "NASH Cirrhosis", "2022"), ("E11.65", "T2DM", "2010"), ("K76.6", "Portal HTN", "2023"), ("I85.00", "Esophageal varices", "2023")],
    "meds": [("Metformin 1000mg", "bid"), ("Propranolol 40mg", "bid"), ("Spironolactone 50mg", "daily"), ("Lactulose", "prn"), ("Rifaximin 550mg", "bid")],
    "family_hx": [("Mother", "T2DM", "Living 82"), ("Father", "T2DM, MI", "Died 65")],
},

# ============================================================================
# 8. Breast Cancer Survivor - 5 years out, doing well
# ============================================================================
{
    "id": "persona-det-008-brca-survivor",
    "demo": {"first": "Linda", "last": "Thompson", "dob": "1968-03-25", "gender": "F", "city": "Denver", "state": "Colorado", "occupation": "School counselor"},
    "narrative": """Linda is a 57-year-old breast cancer survivor - Stage 2A ER+ in 2020, s/p lumpectomy + radiation.
    On anastrozole x 5 years (now finishing). No recurrence. Developed treatment-related osteopenia.
    No diabetes, mild HTN on lisinopril. Active - hikes, yoga. Cancer anxiety during scans.
    Married, 2 adult children. Active in survivor support group. Optimistic but vigilant.""",
    "risk": {"diabetes": 2, "cardiovascular": 3},
    "vitals_trend": [
        {"date": "2022-03", "wt": 68, "bp_s": 132, "bp_d": 82, "hr": 72, "o2": 98},
        {"date": "2023-03", "wt": 66, "bp_s": 128, "bp_d": 78, "hr": 70, "o2": 98},
        {"date": "2024-03", "wt": 65, "bp_s": 124, "bp_d": 76, "hr": 68, "o2": 99},
        {"date": "2025-02", "wt": 64, "bp_s": 122, "bp_d": 74, "hr": 66, "o2": 99},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 92, "hba1c": 5.3, "chol": 195, "vitd": 32, "ca125": 12},
        {"date": "2023-03", "glucose": 88, "hba1c": 5.2, "chol": 188, "vitd": 38, "ca125": 10},
        {"date": "2024-03", "glucose": 90, "hba1c": 5.3, "chol": 182, "vitd": 42, "ca125": 11},
        {"date": "2025-02", "glucose": 88, "hba1c": 5.2, "chol": 178, "vitd": 45, "ca125": 9},
    ],
    "conditions": [("Z85.3", "Hx breast cancer", "2020"), ("C50.912", "Breast cancer Stage 2A (resolved)", "2020"), ("I10", "HTN", "2021"), ("M85.80", "Osteopenia", "2023")],
    "meds": [("Anastrozole 1mg", "daily - completing"), ("Lisinopril 10mg", "daily"), ("Calcium/VitD", "daily")],
    "family_hx": [("Mother", "Breast cancer at 62", "Living 82"), ("Aunt", "Ovarian cancer", "Died 58")],
},

# ============================================================================
# 9. HIV Well-Controlled - On ART, undetectable
# ============================================================================
{
    "id": "persona-det-009-hiv",
    "demo": {"first": "Marcus", "last": "Williams", "dob": "1978-07-14", "gender": "M", "city": "Atlanta", "state": "Georgia", "occupation": "Social worker"},
    "narrative": """Marcus is a 47-year-old living with HIV for 18 years, undetectable on Biktarvy for 10 years.
    CD4 count stable >700. No AIDS-defining illnesses ever. Mild lipodystrophy from old meds.
    No diabetes - glucose normal. BP normal. Cholesterol slightly elevated (med-related).
    Openly HIV+, works as HIV counselor. In long-term relationship. Exercises regularly.""",
    "risk": {"diabetes": 2, "cardiovascular": 4},
    "vitals_trend": [
        {"date": "2022-03", "wt": 78, "bp_s": 122, "bp_d": 76, "hr": 68, "o2": 98},
        {"date": "2023-03", "wt": 79, "bp_s": 124, "bp_d": 78, "hr": 70, "o2": 98},
        {"date": "2024-03", "wt": 80, "bp_s": 126, "bp_d": 78, "hr": 68, "o2": 98},
        {"date": "2025-02", "wt": 79, "bp_s": 122, "bp_d": 76, "hr": 66, "o2": 99},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 92, "hba1c": 5.3, "chol": 218, "cd4": 720, "vl": 0, "creat": 0.9},
        {"date": "2023-03", "glucose": 95, "hba1c": 5.4, "chol": 225, "cd4": 750, "vl": 0, "creat": 0.9},
        {"date": "2024-03", "glucose": 90, "hba1c": 5.2, "chol": 215, "cd4": 780, "vl": 0, "creat": 1.0},
        {"date": "2025-02", "glucose": 88, "hba1c": 5.3, "chol": 208, "cd4": 810, "vl": 0, "creat": 0.9},
    ],
    "conditions": [("B20", "HIV infection", "2007"), ("Z21", "Asymptomatic HIV", "2015"), ("E78.0", "Hypercholesterolemia", "2020")],
    "meds": [("Biktarvy", "daily"), ("Rosuvastatin 10mg", "daily")],
    "family_hx": [("Father", "HTN, T2DM", "Living 72"), ("Mother", "Healthy", "Living 70")],
},

# ============================================================================
# 10. Healthy Elder - 82yo with minimal issues
# ============================================================================
{
    "id": "persona-det-010-healthy-elder",
    "demo": {"first": "Eleanor", "last": "Chen", "dob": "1943-05-18", "gender": "F", "city": "San Francisco", "state": "California", "occupation": "Retired professor"},
    "narrative": """Eleanor is an 82-year-old remarkably healthy retired chemistry professor. 
    Only mild HTN on low-dose lisinopril. No diabetes - A1c 5.1. No heart disease. Sharp cognition.
    Walks 2 miles daily, does Tai Chi, eats Mediterranean diet. Drives herself. Lives alone in condo.
    Widowed 5 years, active social life. Travels internationally. 'I plan to live to 100.'""",
    "risk": {"diabetes": 1, "cardiovascular": 2},
    "vitals_trend": [
        {"date": "2022-03", "wt": 55, "bp_s": 132, "bp_d": 74, "hr": 68, "o2": 98},
        {"date": "2023-03", "wt": 54, "bp_s": 128, "bp_d": 72, "hr": 66, "o2": 98},
        {"date": "2024-03", "wt": 54, "bp_s": 126, "bp_d": 70, "hr": 64, "o2": 98},
        {"date": "2025-02", "wt": 53, "bp_s": 124, "bp_d": 68, "hr": 62, "o2": 99},
    ],
    "labs_trend": [
        {"date": "2022-03", "glucose": 88, "hba1c": 5.2, "chol": 185, "ldl": 98, "hdl": 68, "creat": 0.8},
        {"date": "2023-03", "glucose": 85, "hba1c": 5.1, "chol": 178, "ldl": 92, "hdl": 70, "creat": 0.8},
        {"date": "2024-03", "glucose": 88, "hba1c": 5.2, "chol": 175, "ldl": 88, "hdl": 72, "creat": 0.9},
        {"date": "2025-02", "glucose": 84, "hba1c": 5.1, "chol": 172, "ldl": 85, "hdl": 74, "creat": 0.9},
    ],
    "conditions": [("I10", "Mild HTN", "2015"), ("H52.4", "Presbyopia", "2000"), ("M19.90", "Mild OA knees", "2020")],
    "meds": [("Lisinopril 5mg", "daily")],
    "family_hx": [("Mother", "Lived to 95", "Died natural causes"), ("Father", "Lived to 88", "Died natural causes")],
},
]


def get_db():
    return mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)


def insert_all():
    conn = get_db()
    cur = conn.cursor()
    
    print("="*70)
    print("🏥 Creating 10 Synthea-Level Detailed Personas")
    print("="*70)
    
    for p in PERSONAS:
        demo, synthea_id = p["demo"], p["id"]
        print(f"\n📋 {demo['first']} {demo['last']} - {p['conditions'][0][1][:30]}...")
        
        # Patient
        cur.execute("""INSERT INTO Synthea_Patient (synthea_id, first_name, last_name, birthdate, gender, city, state)
            VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE first_name=VALUES(first_name)""",
            (synthea_id, demo['first'], demo['last'], demo['dob'], demo['gender'], demo['city'], demo['state']))
        
        # Vitals time-series
        for v in p['vitals_trend']:
            dt = datetime.strptime(v['date'], "%Y-%m")
            for code, val in [("29463-7", v['wt']), ("8480-6", v['bp_s']), ("8462-4", v['bp_d']), ("8867-4", v['hr'])]:
                cur.execute("INSERT INTO Synthea_Observation (synthea_patient_id, observation_date, code, value, category) VALUES (%s,%s,%s,%s,'vital-signs')",
                    (synthea_id, dt, code, str(val)))
        
        # Labs time-series
        for lab in p['labs_trend']:
            dt = datetime.strptime(lab['date'], "%Y-%m")
            for key, val in lab.items():
                if key != 'date':
                    cur.execute("INSERT INTO Synthea_Observation (synthea_patient_id, observation_date, code, value, category) VALUES (%s,%s,%s,%s,'laboratory')",
                        (synthea_id, dt, key, str(val)))
        
        # Conditions
        for code, desc, start in [(c[0], c[1], c[2]) for c in p['conditions']]:
            cur.execute("INSERT INTO Synthea_Condition (synthea_patient_id, code, description, start_date, is_active) VALUES (%s,%s,%s,%s,1)",
                (synthea_id, code, desc, f"{start}-01-01" if len(start)==4 else start))
        
        # Meds
        for med, dose in p['meds']:
            cur.execute("INSERT INTO Synthea_Medication (synthea_patient_id, description, start_datetime, is_active) VALUES (%s,%s,%s,1)",
                (synthea_id, f"{med} - {dose}", datetime.now()))
        
        # AI Features
        age = (date.today() - datetime.strptime(demo['dob'], "%Y-%m-%d").date()).days // 365
        latest = p['labs_trend'][-1]
        cur.execute("""INSERT INTO Patient_AI_Features (synthea_patient_id, age_years, gender_numeric, bp_systolic, bp_diastolic,
            hba1c_level, blood_glucose_fasting, has_hypertension, has_heart_disease)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE age_years=VALUES(age_years)""",
            (synthea_id, age, 1 if demo['gender']=='F' else 2, p['vitals_trend'][-1]['bp_s'], p['vitals_trend'][-1]['bp_d'],
             latest.get('hba1c', 5.5), latest.get('glucose', 90),
             1 if 'HTN' in str(p['conditions']) or 'hypertension' in str(p['conditions']).lower() else 0,
             1 if any(x in str(p['conditions']).lower() for x in ['chf', 'cad', 'heart', 'mi', 'afib', 'stroke']) else 0))
        
        print(f"   ✅ {len(p['vitals_trend'])} vitals, {len(p['labs_trend'])} labs, {len(p['conditions'])} conditions")
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"\n{'='*70}")
    print("✅ All 10 detailed personas inserted into MariaDB!")


def sync_neo4j():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(AURA_USER, AURA_PASSWORD))
    print("\n🔗 Syncing to Neo4j...")
    
    with driver.session() as s:
        for p in PERSONAS:
            demo, synthea_id = p["demo"], p["id"]
            age = (date.today() - datetime.strptime(demo['dob'], "%Y-%m-%d").date()).days // 365
            
            s.run("""MERGE (p:Person:Patient {synthea_id: $id})
                SET p.first_name=$fn, p.last_name=$ln, p.full_name=$fn+' '+$ln, p.age=$age, p.gender=$g,
                    p.narrative=$narr, p.diabetes_risk=$dr, p.cvd_risk=$cr, p.is_persona=true, p.is_detailed=true""",
                {"id": synthea_id, "fn": demo['first'], "ln": demo['last'], "age": age, "g": demo['gender'],
                 "narr": p['narrative'].strip(), "dr": p['risk']['diabetes'], "cr": p['risk']['cardiovascular']})
            
            for code, desc, _ in [(c[0], c[1], c[2]) for c in p['conditions']]:
                s.run("""MATCH (p:Person {synthea_id:$id}) MERGE (c:Condition {code:$c, patient_id:$id})
                    SET c.description=$d MERGE (p)-[:HAS_CONDITION]->(c)""", {"id": synthea_id, "c": code, "d": desc})
            
            for rel, cond, status in p['family_hx']:
                s.run("""MATCH (p:Person {synthea_id:$id}) MERGE (fh:FamilyHistory {patient_id:$id, relative:$r})
                    SET fh.conditions=$c, fh.status=$s MERGE (p)-[:HAS_FAMILY_HISTORY]->(fh)""",
                    {"id": synthea_id, "r": rel, "c": cond, "s": status})
    
    driver.close()
    print("✅ Neo4j sync complete!")


if __name__ == '__main__':
    insert_all()
    sync_neo4j()
    print("\n" + "="*70)
    print("CREATED 10 DIVERSE DETAILED PERSONAS:")
    print("-"*70)
    for i, p in enumerate(PERSONAS, 1):
        print(f"{i:2}. {p['demo']['first']:12} {p['demo']['last']:12} | {p['conditions'][0][1][:35]}")
    print("="*70)
