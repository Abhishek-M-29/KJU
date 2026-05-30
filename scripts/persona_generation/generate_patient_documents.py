"""
Generate Patient Documents for all 30 Personas
Creates condition-specific Lab Reports, Prescriptions, and Medical Documents
"""

import mariadb
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Database configuration
DB_CONFIG = {
    "host": "lkdncj.h.filess.io",
    "port": 3305,
    "user": "hospital_howeverwhy",
    "password": "379bcdd8edfc2dac1580190b74428fba1acf5cd3",
    "database": "hospital_howeverwhy"
}

# Lab test ranges by condition
LAB_PANELS = {
    "diabetes": {
        "HbA1c": {"unit": "%", "normal": (4.0, 5.6), "prediabetes": (5.7, 6.4), "diabetic": (6.5, 12.0)},
        "Fasting Glucose": {"unit": "mg/dL", "normal": (70, 99), "prediabetes": (100, 125), "diabetic": (126, 300)},
        "Fructosamine": {"unit": "umol/L", "normal": (200, 285), "diabetic": (286, 400)},
        "C-Peptide": {"unit": "ng/mL", "normal": (0.8, 3.1), "low": (0.1, 0.7)},
        "Insulin": {"unit": "uIU/mL", "normal": (2.6, 24.9), "high": (25, 60)},
    },
    "kidney": {
        "Creatinine": {"unit": "mg/dL", "normal_m": (0.7, 1.3), "normal_f": (0.6, 1.1), "elevated": (1.4, 6.0)},
        "BUN": {"unit": "mg/dL", "normal": (7, 20), "elevated": (21, 80)},
        "eGFR": {"unit": "mL/min/1.73m2", "normal": (90, 120), "ckd3": (30, 59), "ckd4": (15, 29), "ckd5": (0, 14)},
        "Potassium": {"unit": "mEq/L", "normal": (3.5, 5.0), "elevated": (5.1, 6.5)},
        "Phosphorus": {"unit": "mg/dL", "normal": (2.5, 4.5), "elevated": (4.6, 7.0)},
        "Albumin (urine)": {"unit": "mg/g Cr", "normal": (0, 30), "microalbuminuria": (31, 300)},
    },
    "cardiac": {
        "Troponin I": {"unit": "ng/mL", "normal": (0, 0.04), "elevated": (0.05, 5.0)},
        "BNP": {"unit": "pg/mL", "normal": (0, 100), "hf": (101, 2000)},
        "NT-proBNP": {"unit": "pg/mL", "normal": (0, 125), "hf": (126, 5000)},
        "CK-MB": {"unit": "ng/mL", "normal": (0, 3.0), "elevated": (3.1, 20)},
        "Myoglobin": {"unit": "ng/mL", "normal": (25, 72), "elevated": (73, 500)},
    },
    "lipid": {
        "Total Cholesterol": {"unit": "mg/dL", "optimal": (0, 199), "borderline": (200, 239), "high": (240, 350)},
        "LDL Cholesterol": {"unit": "mg/dL", "optimal": (0, 99), "near_optimal": (100, 129), "high": (130, 250)},
        "HDL Cholesterol": {"unit": "mg/dL", "low": (20, 39), "normal": (40, 59), "optimal": (60, 100)},
        "Triglycerides": {"unit": "mg/dL", "normal": (0, 149), "borderline": (150, 199), "high": (200, 500)},
        "VLDL": {"unit": "mg/dL", "normal": (5, 40), "high": (41, 80)},
    },
    "liver": {
        "ALT": {"unit": "U/L", "normal": (7, 56), "elevated": (57, 200)},
        "AST": {"unit": "U/L", "normal": (10, 40), "elevated": (41, 200)},
        "ALP": {"unit": "U/L", "normal": (44, 147), "elevated": (148, 400)},
        "Bilirubin Total": {"unit": "mg/dL", "normal": (0.1, 1.2), "elevated": (1.3, 10)},
        "Albumin": {"unit": "g/dL", "normal": (3.4, 5.4), "low": (1.5, 3.3)},
        "PT/INR": {"unit": "ratio", "normal": (0.8, 1.2), "elevated": (1.3, 3.0)},
    },
    "hematology": {
        "WBC": {"unit": "x10^3/uL", "low": (2.0, 3.9), "normal": (4.0, 11.0), "high": (11.1, 20)},
        "RBC": {"unit": "x10^6/uL", "low_m": (3.5, 4.4), "normal_m": (4.5, 5.5), "low_f": (3.5, 3.9), "normal_f": (4.0, 5.0)},
        "Hemoglobin": {"unit": "g/dL", "low_m": (10, 13.4), "normal_m": (13.5, 17.5), "low_f": (9, 11.9), "normal_f": (12, 16)},
        "Hematocrit": {"unit": "%", "low_m": (30, 38), "normal_m": (38.8, 50), "low_f": (28, 35), "normal_f": (36, 44)},
        "Platelets": {"unit": "x10^3/uL", "low": (50, 149), "normal": (150, 400), "high": (401, 600)},
    },
    "thyroid": {
        "TSH": {"unit": "mIU/L", "low": (0.01, 0.39), "normal": (0.4, 4.0), "high": (4.1, 15)},
        "Free T4": {"unit": "ng/dL", "low": (0.3, 0.79), "normal": (0.8, 1.8), "high": (1.9, 4.0)},
        "Free T3": {"unit": "pg/mL", "low": (1.0, 2.2), "normal": (2.3, 4.2), "high": (4.3, 8.0)},
    },
    "inflammation": {
        "CRP": {"unit": "mg/L", "normal": (0, 3), "elevated": (3.1, 50)},
        "ESR": {"unit": "mm/hr", "normal_m": (0, 15), "elevated_m": (16, 100), "normal_f": (0, 20), "elevated_f": (21, 100)},
        "Ferritin": {"unit": "ng/mL", "low": (10, 29), "normal_m": (30, 400), "normal_f": (20, 200), "high": (401, 1000)},
    },
}

def generate_lab_value(test_info: dict, category: str, gender: str = "M") -> float:
    """Generate a realistic lab value based on category"""
    range_vals = None
    
    if category in test_info:
        range_vals = test_info[category]
    elif f"{category}_{gender.lower()}" in test_info:
        range_vals = test_info[f"{category}_{gender.lower()}"]
    else:
        # Default to normal
        for key in test_info:
            if "normal" in key and key != "unit":
                range_vals = test_info[key]
                break
        if range_vals is None:
            # Get first tuple value
            for key, val in test_info.items():
                if isinstance(val, tuple) and len(val) == 2:
                    range_vals = val
                    break
    
    if range_vals is None or not isinstance(range_vals, tuple):
        return random.uniform(50, 100)  # Default fallback
    
    low, high = range_vals
    return round(random.uniform(low, high), 2)


def generate_lab_report(persona: dict, report_type: str, report_date: datetime) -> dict:
    """Generate a condition-specific lab report"""
    conditions = persona.get("all_conditions_list", "") or ""
    gender = persona.get("gender", "M")
    
    report = {
        "patient_name": f"{persona['first_name']} {persona['last_name']}",
        "patient_id": persona["persona_id"],
        "dob": persona.get("birthdate"),
        "report_date": report_date.strftime("%Y-%m-%d %H:%M"),
        "report_type": report_type,
        "ordering_physician": random.choice([
            "Dr. Sarah Mitchell, MD", "Dr. James Chen, MD", "Dr. Maria Garcia, MD",
            "Dr. Robert Thompson, MD", "Dr. Lisa Patel, MD", "Dr. Michael Johnson, MD"
        ]),
        "lab_facility": "Central Medical Laboratory",
        "tests": []
    }
    
    # Determine which panels to run based on conditions
    panels_to_run = []
    
    conditions_lower = conditions.lower()
    
    if any(x in conditions_lower for x in ["diabetes", "hba1c", "glucose", "prediabetes"]):
        panels_to_run.append(("diabetes", "diabetic" if "type 2 diabetes" in conditions_lower else "prediabetes"))
    
    if any(x in conditions_lower for x in ["kidney", "ckd", "nephropathy", "creatinine", "renal"]):
        if "stage 4" in conditions_lower or "ckd4" in conditions_lower:
            panels_to_run.append(("kidney", "ckd4"))
        elif "stage 3" in conditions_lower or "ckd3" in conditions_lower:
            panels_to_run.append(("kidney", "ckd3"))
        else:
            panels_to_run.append(("kidney", "elevated"))
    
    if any(x in conditions_lower for x in ["heart", "cardiac", "mi ", "myocardial", "chf", "failure", "coronary", "cad", "angina"]):
        panels_to_run.append(("cardiac", "hf" if "failure" in conditions_lower else "normal"))
    
    if any(x in conditions_lower for x in ["cholesterol", "lipid", "hyperlipidemia", "hypercholesterolemia"]):
        panels_to_run.append(("lipid", "high"))
    
    if any(x in conditions_lower for x in ["liver", "cirrhosis", "hepat", "nash", "fatty liver"]):
        panels_to_run.append(("liver", "elevated"))
    
    if any(x in conditions_lower for x in ["anemia", "blood", "hematology"]):
        panels_to_run.append(("hematology", "low"))
    
    if any(x in conditions_lower for x in ["thyroid", "hypothyroid", "hyperthyroid"]):
        panels_to_run.append(("thyroid", "normal"))
    
    if any(x in conditions_lower for x in ["arthritis", "ra ", "rheumat", "inflammation"]):
        panels_to_run.append(("inflammation", "elevated"))
    
    # Add basic metabolic panel for everyone
    if not panels_to_run:
        panels_to_run.append(("hematology", "normal"))
        panels_to_run.append(("lipid", "normal"))
    
    # Generate test results
    for panel_name, severity in panels_to_run:
        panel = LAB_PANELS.get(panel_name, {})
        for test_name, test_info in panel.items():
            value = generate_lab_value(test_info, severity, gender)
            
            # Determine reference range
            ref_key = "normal" if "normal" in test_info else list(test_info.keys())[0]
            if f"normal_{gender.lower()}" in test_info:
                ref_key = f"normal_{gender.lower()}"
            ref_range = test_info.get(ref_key, test_info.get("normal", (0, 100)))
            
            # Ensure ref_range is a tuple of numbers
            if isinstance(ref_range, str):
                ref_range = (0, 100)
            
            # Determine if abnormal
            is_abnormal = value < ref_range[0] or value > ref_range[1]
            flag = ""
            if value < ref_range[0]:
                flag = "L"
            elif value > ref_range[1]:
                flag = "H"
            
            report["tests"].append({
                "test_name": test_name,
                "value": value,
                "unit": test_info["unit"],
                "reference_range": f"{ref_range[0]}-{ref_range[1]}",
                "flag": flag,
                "abnormal": is_abnormal
            })
    
    return report


def generate_prescription(persona: dict, rx_date: datetime) -> dict:
    """Generate prescription based on patient's medications"""
    medications = persona.get("all_medications_list", "") or ""
    
    prescription = {
        "patient_name": f"{persona['first_name']} {persona['last_name']}",
        "patient_id": persona["persona_id"],
        "dob": persona.get("birthdate"),
        "prescription_date": rx_date.strftime("%Y-%m-%d"),
        "prescriber": random.choice([
            "Dr. Sarah Mitchell, MD", "Dr. James Chen, MD", "Dr. Maria Garcia, MD",
            "Dr. Robert Thompson, MD", "Dr. Lisa Patel, MD"
        ]),
        "prescriber_dea": f"AM{random.randint(1000000, 9999999)}",
        "prescriber_npi": f"{random.randint(1000000000, 9999999999)}",
        "pharmacy": random.choice([
            "CVS Pharmacy #4521", "Walgreens #12345", "Rite Aid Pharmacy",
            "Community Health Pharmacy", "MedPlus Pharmacy"
        ]),
        "medications": []
    }
    
    if medications:
        med_list = [m.strip() for m in medications.split("|")]
        for med in med_list:
            if not med:
                continue
            
            # Parse medication string
            parts = med.split(" - ")
            med_name = parts[0].strip()
            frequency = parts[1].strip() if len(parts) > 1 else "as directed"
            
            prescription["medications"].append({
                "medication": med_name,
                "directions": frequency,
                "quantity": random.choice([30, 60, 90]),
                "refills": random.randint(0, 5),
                "dispense_as_written": random.choice([True, False])
            })
    
    return prescription


def generate_clinical_note(persona: dict, note_date: datetime, note_type: str = "Progress Note") -> dict:
    """Generate a clinical note based on patient's conditions"""
    conditions = persona.get("all_conditions_list", "") or ""
    medications = persona.get("all_medications_list", "") or ""
    
    conditions_list = [c.strip() for c in conditions.split("|") if c.strip()]
    
    # Generate vitals (use stored values or generate)
    vitals = {
        "BP": f"{persona.get('bp_systolic') or random.randint(110, 150)}/{persona.get('bp_diastolic') or random.randint(70, 95)} mmHg",
        "HR": f"{persona.get('heart_rate') or random.randint(60, 100)} bpm",
        "Weight": f"{persona.get('weight_kg') or random.randint(50, 120)} kg",
        "Temp": f"{round(random.uniform(97.0, 99.0), 1)} °F",
        "SpO2": f"{random.randint(95, 100)}%"
    }
    
    # Generate assessment based on conditions
    assessments = []
    for cond in conditions_list[:5]:  # Top 5 conditions
        status = random.choice(["stable", "improving", "controlled", "monitored", "unchanged"])
        assessments.append(f"{cond} - {status}")
    
    note = {
        "patient_name": f"{persona['first_name']} {persona['last_name']}",
        "patient_id": persona["persona_id"],
        "dob": persona.get("birthdate"),
        "note_date": note_date.strftime("%Y-%m-%d %H:%M"),
        "note_type": note_type,
        "provider": random.choice([
            "Dr. Sarah Mitchell, MD", "Dr. James Chen, MD", "Dr. Maria Garcia, MD"
        ]),
        "chief_complaint": random.choice([
            "Follow-up visit for chronic conditions",
            "Routine medication management",
            "Wellness check",
            "Management of multiple comorbidities"
        ]),
        "vitals": vitals,
        "subjective": f"Patient presents for {note_type.lower()}. Reports " + random.choice([
            "feeling well overall.", "some fatigue.", "no new complaints.", 
            "improved symptoms since last visit.", "stable condition."
        ]),
        "objective": f"Physical exam: Alert and oriented. " + random.choice([
            "No acute distress.", "Well-appearing.", "Comfortable at rest."
        ]),
        "assessment": assessments,
        "plan": [
            "Continue current medications",
            f"Follow up in {random.choice([2, 4, 6, 8, 12])} weeks",
            "Lab work ordered as indicated",
            "Patient educated on condition management"
        ]
    }
    
    return note


def generate_discharge_summary(persona: dict, discharge_date: datetime) -> dict:
    """Generate discharge summary for patients with serious conditions"""
    conditions = persona.get("all_conditions_list", "") or ""
    conditions_lower = conditions.lower()
    
    # Determine admission reason
    if "myocardial infarction" in conditions_lower or "mi " in conditions_lower or "stemi" in conditions_lower:
        admission_reason = "Acute Myocardial Infarction"
        hospital_course = "Patient presented with chest pain. Underwent cardiac catheterization with PCI. Remained stable."
    elif "heart failure" in conditions_lower or "chf" in conditions_lower:
        admission_reason = "Acute Exacerbation of Heart Failure"
        hospital_course = "Patient presented with dyspnea and lower extremity edema. Treated with IV diuretics. Symptoms improved."
    elif "stroke" in conditions_lower or "cva" in conditions_lower:
        admission_reason = "Cerebrovascular Accident"
        hospital_course = "Patient presented with neurological deficits. Imaging confirmed stroke. Started on anticoagulation."
    elif "copd" in conditions_lower:
        admission_reason = "COPD Exacerbation"
        hospital_course = "Patient presented with respiratory distress. Treated with bronchodilators and steroids."
    else:
        admission_reason = "Acute illness management"
        hospital_course = "Patient admitted for observation and management. Condition stabilized."
    
    admission_date = discharge_date - timedelta(days=random.randint(2, 7))
    
    return {
        "patient_name": f"{persona['first_name']} {persona['last_name']}",
        "patient_id": persona["persona_id"],
        "dob": persona.get("birthdate"),
        "admission_date": admission_date.strftime("%Y-%m-%d"),
        "discharge_date": discharge_date.strftime("%Y-%m-%d"),
        "admitting_diagnosis": admission_reason,
        "discharge_diagnosis": conditions.split("|")[0].strip() if conditions else admission_reason,
        "attending_physician": random.choice([
            "Dr. Sarah Mitchell, MD", "Dr. James Chen, MD", "Dr. Maria Garcia, MD"
        ]),
        "hospital": "Central Medical Center",
        "hospital_course": hospital_course,
        "discharge_medications": persona.get("all_medications_list", "Continue home medications"),
        "follow_up_instructions": [
            f"Follow up with primary care in {random.randint(1, 2)} weeks",
            "Return to ER if symptoms worsen",
            "Take all medications as prescribed"
        ],
        "activity": random.choice(["No restrictions", "Light activity only", "Bedrest for 48 hours"]),
        "diet": random.choice(["Regular", "Low sodium", "Diabetic diet", "Heart healthy"])
    }


def format_lab_report_text(report: dict) -> str:
    """Format lab report as readable text"""
    lines = [
        "=" * 60,
        "LABORATORY REPORT",
        "=" * 60,
        f"Patient: {report['patient_name']}",
        f"DOB: {report['dob']}",
        f"Report Date: {report['report_date']}",
        f"Report Type: {report['report_type']}",
        f"Ordering Physician: {report['ordering_physician']}",
        f"Laboratory: {report['lab_facility']}",
        "-" * 60,
        "",
        f"{'Test Name':<25} {'Result':<12} {'Unit':<15} {'Reference':<15} {'Flag':<5}",
        "-" * 60
    ]
    
    for test in report["tests"]:
        flag = f"[{test['flag']}]" if test['flag'] else ""
        lines.append(f"{test['test_name']:<25} {test['value']:<12} {test['unit']:<15} {test['reference_range']:<15} {flag:<5}")
    
    lines.extend([
        "",
        "-" * 60,
        "END OF REPORT",
        "=" * 60
    ])
    
    return "\n".join(lines)


def format_prescription_text(rx: dict) -> str:
    """Format prescription as readable text"""
    lines = [
        "=" * 60,
        "PRESCRIPTION",
        "=" * 60,
        f"Patient: {rx['patient_name']}",
        f"DOB: {rx['dob']}",
        f"Date: {rx['prescription_date']}",
        "",
        f"Prescriber: {rx['prescriber']}",
        f"DEA: {rx['prescriber_dea']}",
        f"NPI: {rx['prescriber_npi']}",
        "-" * 60,
        "",
        "MEDICATIONS:",
        ""
    ]
    
    for i, med in enumerate(rx["medications"], 1):
        lines.extend([
            f"  {i}. {med['medication']}",
            f"     Sig: {med['directions']}",
            f"     Qty: {med['quantity']}    Refills: {med['refills']}",
            f"     DAW: {'Yes' if med['dispense_as_written'] else 'No'}",
            ""
        ])
    
    lines.extend([
        "-" * 60,
        f"Pharmacy: {rx['pharmacy']}",
        "=" * 60
    ])
    
    return "\n".join(lines)


def format_clinical_note_text(note: dict) -> str:
    """Format clinical note as readable text"""
    lines = [
        "=" * 60,
        f"{note['note_type'].upper()}",
        "=" * 60,
        f"Patient: {note['patient_name']}",
        f"DOB: {note['dob']}",
        f"Date: {note['note_date']}",
        f"Provider: {note['provider']}",
        "-" * 60,
        "",
        "CHIEF COMPLAINT:",
        f"  {note['chief_complaint']}",
        "",
        "VITALS:",
    ]
    
    for k, v in note["vitals"].items():
        lines.append(f"  {k}: {v}")
    
    lines.extend([
        "",
        "SUBJECTIVE:",
        f"  {note['subjective']}",
        "",
        "OBJECTIVE:",
        f"  {note['objective']}",
        "",
        "ASSESSMENT:",
    ])
    
    for assess in note["assessment"]:
        lines.append(f"  • {assess}")
    
    lines.extend([
        "",
        "PLAN:",
    ])
    
    for plan in note["plan"]:
        lines.append(f"  • {plan}")
    
    lines.extend([
        "",
        "-" * 60,
        f"Electronically signed by {note['provider']}",
        "=" * 60
    ])
    
    return "\n".join(lines)


def format_discharge_summary_text(summary: dict) -> str:
    """Format discharge summary as readable text"""
    lines = [
        "=" * 60,
        "DISCHARGE SUMMARY",
        "=" * 60,
        f"Patient: {summary['patient_name']}",
        f"DOB: {summary['dob']}",
        f"Admission Date: {summary['admission_date']}",
        f"Discharge Date: {summary['discharge_date']}",
        f"Attending: {summary['attending_physician']}",
        f"Facility: {summary['hospital']}",
        "-" * 60,
        "",
        "ADMITTING DIAGNOSIS:",
        f"  {summary['admitting_diagnosis']}",
        "",
        "DISCHARGE DIAGNOSIS:",
        f"  {summary['discharge_diagnosis']}",
        "",
        "HOSPITAL COURSE:",
        f"  {summary['hospital_course']}",
        "",
        "DISCHARGE MEDICATIONS:",
        f"  {summary['discharge_medications']}",
        "",
        "FOLLOW-UP INSTRUCTIONS:",
    ]
    
    for instr in summary["follow_up_instructions"]:
        lines.append(f"  • {instr}")
    
    lines.extend([
        "",
        f"Activity: {summary['activity']}",
        f"Diet: {summary['diet']}",
        "",
        "-" * 60,
        f"Prepared by {summary['attending_physician']}",
        "=" * 60
    ])
    
    return "\n".join(lines)


def insert_document(cursor, persona_id: int, doc_type: str, doc_name: str, ocr_text: str, notes: str = None):
    """Insert a document into Patient_Documents table"""
    cursor.execute("""
        INSERT INTO Patient_Documents 
        (patient_id, document_type, document_name, ocr_text, ocr_status, notes, is_verified, created_at)
        VALUES (?, ?, ?, ?, 'completed', ?, 1, NOW())
    """, (persona_id, doc_type, doc_name, ocr_text, notes))


def main():
    print("=" * 60)
    print("GENERATING PATIENT DOCUMENTS FOR ALL 30 PERSONAS")
    print("=" * 60)
    
    conn = mariadb.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    # Get all personas
    cursor.execute("""
        SELECT persona_id, synthea_id, first_name, last_name, age_years, gender, birthdate,
               all_conditions_list, all_medications_list,
               bp_systolic, bp_diastolic, heart_rate, glucose, hba1c, creatinine,
               cholesterol_total, ldl, hdl, hemoglobin, bmi, weight_kg, height_cm
        FROM Patient_Data 
        WHERE is_persona = 1 
        ORDER BY persona_id
    """)
    personas = cursor.fetchall()
    
    cursor_insert = conn.cursor()
    
    # Clear existing documents for personas
    print("\nClearing existing documents...")
    cursor_insert.execute("DELETE FROM Patient_Documents WHERE patient_id <= 30")
    conn.commit()
    
    total_docs = 0
    
    for persona in personas:
        pid = persona["persona_id"]
        name = f"{persona['first_name']} {persona['last_name']}"
        conditions = persona.get("all_conditions_list", "") or ""
        
        print(f"\n[{pid}/30] Processing {name}...")
        print(f"         Conditions: {conditions[:80]}..." if len(conditions) > 80 else f"         Conditions: {conditions}")
        
        docs_created = 0
        
        # Generate multiple lab reports (2-4 based on complexity)
        conditions_lower = conditions.lower()
        num_labs = 2
        if any(x in conditions_lower for x in ["diabetes", "kidney", "heart", "liver"]):
            num_labs = 4
        elif any(x in conditions_lower for x in ["hypertension", "cholesterol", "prediabetes"]):
            num_labs = 3
        
        for i in range(num_labs):
            report_date = datetime.now() - timedelta(days=random.randint(30, 365) + i * 90)
            
            # Determine report type based on conditions
            if "diabetes" in conditions_lower and i == 0:
                report_type = "Diabetes Panel"
            elif any(x in conditions_lower for x in ["kidney", "ckd", "nephropathy"]) and i == 1:
                report_type = "Renal Function Panel"
            elif any(x in conditions_lower for x in ["heart", "cardiac", "mi", "chf"]):
                report_type = "Cardiac Markers"
            elif any(x in conditions_lower for x in ["lipid", "cholesterol"]):
                report_type = "Lipid Panel"
            elif any(x in conditions_lower for x in ["liver", "cirrhosis"]):
                report_type = "Hepatic Function Panel"
            else:
                report_type = random.choice(["Comprehensive Metabolic Panel", "Complete Blood Count", "Basic Metabolic Panel"])
            
            lab_report = generate_lab_report(persona, report_type, report_date)
            lab_text = format_lab_report_text(lab_report)
            
            insert_document(
                cursor_insert, pid, "Lab Report",
                f"Lab Report - {report_type} - {report_date.strftime('%Y%m%d')}",
                lab_text,
                f"Automated lab report for {report_type}"
            )
            docs_created += 1
        
        # Generate prescriptions (1-3 based on medications)
        medications = persona.get("all_medications_list", "") or ""
        if medications:
            num_rx = min(3, len([m for m in medications.split("|") if m.strip()]) // 3 + 1)
            
            for i in range(num_rx):
                rx_date = datetime.now() - timedelta(days=random.randint(7, 180) + i * 60)
                prescription = generate_prescription(persona, rx_date)
                rx_text = format_prescription_text(prescription)
                
                insert_document(
                    cursor_insert, pid, "Prescription",
                    f"Prescription - {rx_date.strftime('%Y%m%d')}",
                    rx_text,
                    "Prescription for current medications"
                )
                docs_created += 1
        
        # Generate clinical notes (2-3)
        for i in range(random.randint(2, 3)):
            note_date = datetime.now() - timedelta(days=random.randint(14, 300) + i * 60)
            note_type = random.choice(["Progress Note", "Follow-up Visit", "Annual Physical", "Specialist Consultation"])
            
            clinical_note = generate_clinical_note(persona, note_date, note_type)
            note_text = format_clinical_note_text(clinical_note)
            
            insert_document(
                cursor_insert, pid, "Clinical Note",
                f"{note_type} - {note_date.strftime('%Y%m%d')}",
                note_text,
                f"{note_type} documentation"
            )
            docs_created += 1
        
        # Generate discharge summary for serious conditions
        if any(x in conditions_lower for x in ["myocardial", "heart failure", "stroke", "cva", "copd exacerbation", "stemi", "cabg"]):
            discharge_date = datetime.now() - timedelta(days=random.randint(60, 365))
            discharge = generate_discharge_summary(persona, discharge_date)
            discharge_text = format_discharge_summary_text(discharge)
            
            insert_document(
                cursor_insert, pid, "Discharge Summary",
                f"Discharge Summary - {discharge_date.strftime('%Y%m%d')}",
                discharge_text,
                "Hospital discharge documentation"
            )
            docs_created += 1
        
        conn.commit()
        print(f"         Created {docs_created} documents")
        total_docs += docs_created
    
    # Summary
    print("\n" + "=" * 60)
    print("DOCUMENT GENERATION COMPLETE")
    print("=" * 60)
    
    # Get counts by type
    cursor.execute("""
        SELECT document_type, COUNT(*) as count 
        FROM Patient_Documents 
        WHERE patient_id <= 30
        GROUP BY document_type
    """)
    
    print("\nDocuments created by type:")
    for row in cursor.fetchall():
        print(f"  {row['document_type']}: {row['count']}")
    
    print(f"\nTotal documents created: {total_docs}")
    
    cursor.close()
    cursor_insert.close()
    conn.close()


if __name__ == "__main__":
    main()
