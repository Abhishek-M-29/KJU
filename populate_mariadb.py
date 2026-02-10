#!/usr/bin/env python3
"""
MediMax MariaDB Population Script
================================
Creates comprehensive patient data with realistic medical scenarios
for the healthcare knowledge graph system.

Tables populated:
- Patient (central entity)
- Medical_History (allergies, surgeries, chronic conditions, family history, lifestyle)
- Appointment (healthcare visits)
- Appointment_Symptom (symptoms per appointment)
- Medication (prescriptions)
- Medication_Purpose (conditions treated by medications)
- Lab_Report (laboratory test reports)
- Lab_Finding (individual lab results)
- Report (clinical/radiology/pathology reports)
- Report_Finding (report findings)
- Chat_History (patient-provider communications)
"""

import mariadb
import os
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
import random

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))

# Sample data pools for realistic medical data
FIRST_NAMES_MALE = ["James", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Daniel"]
FIRST_NAMES_FEMALE = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee"]

DOCTORS = ["Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Chen", "Dr. Patel", "Dr. Martinez", "Dr. Thompson", "Dr. Garcia"]
LAB_FACILITIES = ["City Medical Lab", "HealthCare Diagnostics", "MediLab Central", "PathCare Labs", "QuickTest Laboratories"]

# Medical conditions and related data
CHRONIC_CONDITIONS = [
    ("Type 2 Diabetes", "Diagnosed with Type 2 Diabetes Mellitus", "Moderate"),
    ("Hypertension", "Essential hypertension, well controlled", "Moderate"),
    ("Hyperlipidemia", "Elevated cholesterol and triglycerides", "Mild"),
    ("Asthma", "Allergic asthma, seasonal exacerbations", "Mild"),
    ("GERD", "Gastroesophageal reflux disease", "Mild"),
    ("Hypothyroidism", "Underactive thyroid, on replacement therapy", "Mild"),
    ("Osteoarthritis", "Degenerative joint disease, knees and hips", "Moderate"),
    ("Atrial Fibrillation", "Paroxysmal atrial fibrillation", "Severe"),
    ("Chronic Kidney Disease Stage 3", "CKD stage 3, stable", "Moderate"),
    ("COPD", "Chronic obstructive pulmonary disease", "Moderate"),
]

ALLERGIES = [
    ("Penicillin", "Rash and hives on exposure", "Moderate"),
    ("Sulfa drugs", "Severe allergic reaction", "Severe"),
    ("Shellfish", "Anaphylactic reaction", "Critical"),
    ("Latex", "Contact dermatitis", "Mild"),
    ("Aspirin", "GI bleeding risk", "Moderate"),
    ("Codeine", "Nausea and vomiting", "Mild"),
    ("Iodine contrast", "Hives and swelling", "Moderate"),
    ("Eggs", "Mild allergic symptoms", "Mild"),
]

SURGERIES = [
    ("Appendectomy", "Laparoscopic appendectomy"),
    ("Cholecystectomy", "Gallbladder removal"),
    ("Knee Replacement", "Total knee arthroplasty"),
    ("Coronary Bypass", "CABG x3"),
    ("Cataract Surgery", "Phacoemulsification with IOL"),
    ("Hernia Repair", "Inguinal hernia repair"),
    ("Hysterectomy", "Total abdominal hysterectomy"),
    ("Tonsillectomy", "Childhood tonsillectomy"),
]

FAMILY_HISTORY = [
    ("Heart Disease", "Father had MI at age 55", "Moderate"),
    ("Diabetes", "Mother with Type 2 diabetes", "Moderate"),
    ("Cancer", "Brother diagnosed with colon cancer at 50", "Severe"),
    ("Hypertension", "Both parents with high blood pressure", "Mild"),
    ("Stroke", "Grandmother had stroke at 70", "Moderate"),
    ("Alzheimers", "Paternal grandfather with dementia", "Mild"),
]

LIFESTYLE_FACTORS = [
    ("Smoking History", "Former smoker, quit 5 years ago", "Mild"),
    ("Current Smoker", "1 pack per day for 20 years", "Severe"),
    ("Alcohol Use", "Moderate alcohol consumption, 2-3 drinks/week", "Mild"),
    ("Sedentary Lifestyle", "Minimal physical activity", "Moderate"),
    ("Obesity", "BMI > 30, counseled on weight management", "Moderate"),
    ("Exercise Regular", "Exercises 3-4 times per week", "Mild"),
]

SYMPTOMS = [
    ("Fatigue", "Persistent tiredness and lack of energy", "Moderate", "2 weeks", "Gradual"),
    ("Headache", "Throbbing headache, frontal region", "Moderate", "3 days", "Sudden"),
    ("Chest Pain", "Substernal pressure, worse with exertion", "Severe", "1 hour", "Sudden"),
    ("Shortness of Breath", "Dyspnea on exertion", "Moderate", "1 week", "Gradual"),
    ("Dizziness", "Lightheadedness, especially on standing", "Mild", "4 days", "Intermittent"),
    ("Nausea", "Feeling of nausea, no vomiting", "Mild", "2 days", "Intermittent"),
    ("Joint Pain", "Bilateral knee pain, worse in morning", "Moderate", "3 months", "Chronic"),
    ("Cough", "Dry cough, worse at night", "Mild", "1 week", "Gradual"),
    ("Fever", "Low grade fever, 100.4F", "Mild", "2 days", "Sudden"),
    ("Back Pain", "Lower back pain, radiating to left leg", "Severe", "1 week", "Sudden"),
    ("Increased Thirst", "Polydipsia, drinking 3L+ per day", "Moderate", "2 weeks", "Gradual"),
    ("Frequent Urination", "Polyuria, nocturia x3", "Moderate", "2 weeks", "Gradual"),
    ("Blurred Vision", "Intermittent blurry vision", "Mild", "1 week", "Intermittent"),
    ("Weight Loss", "Unintentional 10lb weight loss", "Moderate", "1 month", "Gradual"),
    ("Swelling", "Bilateral ankle swelling", "Moderate", "2 weeks", "Gradual"),
]

MEDICATIONS = [
    ("Metformin", "500mg", "Twice daily", ["Type 2 Diabetes"]),
    ("Lisinopril", "10mg", "Once daily", ["Hypertension", "Heart Failure"]),
    ("Atorvastatin", "20mg", "Once daily at bedtime", ["Hyperlipidemia", "Cardiovascular Prevention"]),
    ("Amlodipine", "5mg", "Once daily", ["Hypertension"]),
    ("Omeprazole", "20mg", "Once daily before breakfast", ["GERD", "Peptic Ulcer"]),
    ("Levothyroxine", "50mcg", "Once daily on empty stomach", ["Hypothyroidism"]),
    ("Albuterol", "90mcg", "As needed for shortness of breath", ["Asthma", "COPD"]),
    ("Aspirin", "81mg", "Once daily", ["Cardiovascular Prevention", "Atrial Fibrillation"]),
    ("Metoprolol", "25mg", "Twice daily", ["Hypertension", "Atrial Fibrillation", "Heart Failure"]),
    ("Gabapentin", "300mg", "Three times daily", ["Neuropathic Pain", "Fibromyalgia"]),
    ("Hydrochlorothiazide", "25mg", "Once daily", ["Hypertension", "Edema"]),
    ("Warfarin", "5mg", "Once daily", ["Atrial Fibrillation", "DVT Prevention"]),
    ("Insulin Glargine", "20 units", "Once daily at bedtime", ["Type 2 Diabetes", "Type 1 Diabetes"]),
    ("Prednisone", "10mg", "Once daily for 5 days", ["Asthma Exacerbation", "Inflammation"]),
    ("Tramadol", "50mg", "Every 6 hours as needed", ["Chronic Pain", "Osteoarthritis"]),
]

LAB_TESTS = {
    "Comprehensive Metabolic Panel": [
        ("Glucose", "mg/dL", "70-100"),
        ("BUN", "mg/dL", "7-20"),
        ("Creatinine", "mg/dL", "0.7-1.3"),
        ("Sodium", "mEq/L", "136-145"),
        ("Potassium", "mEq/L", "3.5-5.0"),
        ("Chloride", "mEq/L", "98-106"),
        ("CO2", "mEq/L", "23-29"),
        ("Calcium", "mg/dL", "8.5-10.5"),
        ("Total Protein", "g/dL", "6.0-8.3"),
        ("Albumin", "g/dL", "3.5-5.0"),
        ("Bilirubin", "mg/dL", "0.1-1.2"),
        ("ALT", "U/L", "7-56"),
        ("AST", "U/L", "10-40"),
    ],
    "Lipid Panel": [
        ("Total Cholesterol", "mg/dL", "<200"),
        ("LDL Cholesterol", "mg/dL", "<100"),
        ("HDL Cholesterol", "mg/dL", ">40"),
        ("Triglycerides", "mg/dL", "<150"),
        ("VLDL", "mg/dL", "5-40"),
    ],
    "Complete Blood Count": [
        ("WBC", "K/uL", "4.5-11.0"),
        ("RBC", "M/uL", "4.5-5.5"),
        ("Hemoglobin", "g/dL", "12.0-17.5"),
        ("Hematocrit", "%", "36-50"),
        ("MCV", "fL", "80-100"),
        ("MCH", "pg", "27-33"),
        ("MCHC", "g/dL", "32-36"),
        ("Platelets", "K/uL", "150-400"),
    ],
    "Diabetes Panel": [
        ("HbA1c", "%", "4.0-5.6"),
        ("Fasting Glucose", "mg/dL", "70-100"),
        ("Fasting Insulin", "uIU/mL", "2.6-24.9"),
        ("C-Peptide", "ng/mL", "0.8-3.1"),
    ],
    "Thyroid Panel": [
        ("TSH", "mIU/L", "0.4-4.0"),
        ("Free T4", "ng/dL", "0.8-1.8"),
        ("Free T3", "pg/mL", "2.3-4.2"),
    ],
    "Cardiac Markers": [
        ("Troponin I", "ng/mL", "<0.04"),
        ("BNP", "pg/mL", "<100"),
        ("CK-MB", "ng/mL", "<5"),
    ],
}

APPOINTMENT_TYPES = ["Regular", "Follow_up", "Consultation", "Emergency"]
APPOINTMENT_STATUS = ["Completed", "Scheduled", "Cancelled", "No_Show"]


def get_db_connection():
    """Establish database connection"""
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )


def execute_query(query, params=None, return_lastrowid=True):
    """Execute a database query"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if query.strip().upper().startswith('INSERT'):
            conn.commit()
            return cursor.lastrowid if return_lastrowid else cursor.rowcount
        elif query.strip().upper().startswith(('UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'TRUNCATE')):
            conn.commit()
            return cursor.rowcount
        else:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    except mariadb.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()


def execute_many(query, params_list):
    """Execute query with multiple parameter sets"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount
    except mariadb.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()


def generate_random_date(start_year=2020, end_year=2025):
    """Generate a random date within the given year range"""
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def generate_dob(min_age=25, max_age=75):
    """Generate a date of birth for given age range"""
    today = date.today()
    age = random.randint(min_age, max_age)
    year = today.year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return date(year, month, day)


def generate_lab_value(test_name, reference_range, is_abnormal=False):
    """Generate realistic lab values based on reference ranges"""
    # Parse reference range
    ref = reference_range.replace("<", "").replace(">", "").strip()
    
    try:
        if "-" in ref:
            low, high = map(float, ref.split("-"))
        else:
            # For single value references like "<200"
            high = float(ref)
            low = high * 0.3
        
        if is_abnormal:
            # Generate abnormal value (either high or low)
            if random.random() > 0.5:
                # High value
                value = high * random.uniform(1.1, 1.5)
                flag = "High"
            else:
                # Low value
                value = low * random.uniform(0.5, 0.9)
                flag = "Low"
        else:
            # Normal value within range
            value = random.uniform(low, high)
            flag = None
        
        # Round appropriately
        if value > 100:
            value = round(value, 0)
        elif value > 10:
            value = round(value, 1)
        else:
            value = round(value, 2)
        
        return str(value), flag
    except:
        return str(random.randint(50, 150)), None


def create_tables():
    """Create all necessary tables if they don't exist"""
    tables_sql = """
    -- Patient table
    CREATE TABLE IF NOT EXISTS Patient (
        patient_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        dob DATE,
        sex ENUM('Male', 'Female', 'Other'),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

    -- Medical History table
    CREATE TABLE IF NOT EXISTS Medical_History (
        history_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT,
        history_type ENUM('allergy', 'surgery', 'chronic_condition', 'family_history', 'lifestyle'),
        history_item VARCHAR(200),
        history_details TEXT,
        history_date DATE,
        severity ENUM('Mild', 'Moderate', 'Severe', 'Critical'),
        is_active TINYINT DEFAULT 1,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE
    );

    -- Appointment table
    CREATE TABLE IF NOT EXISTS Appointment (
        appointment_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT,
        appointment_date DATE NOT NULL,
        appointment_time TIME,
        status ENUM('Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show'),
        appointment_type ENUM('Regular', 'Emergency', 'Follow_up', 'Consultation', 'Surgery'),
        doctor_name VARCHAR(100),
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE
    );

    -- Appointment Symptom table
    CREATE TABLE IF NOT EXISTS Appointment_Symptom (
        symptom_id INT AUTO_INCREMENT PRIMARY KEY,
        appointment_id INT,
        symptom_name VARCHAR(100) NOT NULL,
        symptom_description TEXT,
        severity ENUM('Mild', 'Moderate', 'Severe', 'Critical'),
        duration VARCHAR(50),
        onset_type ENUM('Sudden', 'Gradual', 'Chronic', 'Intermittent'),
        FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id) ON DELETE CASCADE
    );

    -- Medication table
    CREATE TABLE IF NOT EXISTS Medication (
        medication_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT,
        medicine_name VARCHAR(100) NOT NULL,
        is_continued TINYINT DEFAULT 1,
        prescribed_date DATE NOT NULL,
        discontinued_date DATE,
        dosage VARCHAR(50),
        frequency VARCHAR(100),
        prescribed_by VARCHAR(100),
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE
    );

    -- Medication Purpose table
    CREATE TABLE IF NOT EXISTS Medication_Purpose (
        purpose_id INT AUTO_INCREMENT PRIMARY KEY,
        medication_id INT,
        condition_name VARCHAR(200) NOT NULL,
        purpose_description TEXT,
        FOREIGN KEY (medication_id) REFERENCES Medication(medication_id) ON DELETE CASCADE
    );

    -- Lab Report table
    CREATE TABLE IF NOT EXISTS Lab_Report (
        lab_report_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT,
        lab_date DATE NOT NULL,
        lab_type VARCHAR(100),
        ordering_doctor VARCHAR(100),
        lab_facility VARCHAR(200),
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE
    );

    -- Lab Finding table
    CREATE TABLE IF NOT EXISTS Lab_Finding (
        lab_finding_id INT AUTO_INCREMENT PRIMARY KEY,
        lab_report_id INT,
        test_name VARCHAR(100) NOT NULL,
        test_value VARCHAR(50) NOT NULL,
        test_unit VARCHAR(50),
        reference_range VARCHAR(50),
        is_abnormal TINYINT DEFAULT 0,
        abnormal_flag ENUM('High', 'Low', 'Critical_High', 'Critical_Low'),
        FOREIGN KEY (lab_report_id) REFERENCES Lab_Report(lab_report_id) ON DELETE CASCADE
    );

    -- Report table
    CREATE TABLE IF NOT EXISTS Report (
        report_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT,
        report_type ENUM('Radiology', 'Pathology', 'Clinical', 'Discharge', 'Consultation'),
        report_date DATE NOT NULL,
        complete_report LONGTEXT,
        report_summary TEXT,
        doctor_name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE
    );

    -- Report Finding table
    CREATE TABLE IF NOT EXISTS Report_Finding (
        finding_id INT AUTO_INCREMENT PRIMARY KEY,
        report_id INT,
        finding_key VARCHAR(100) NOT NULL,
        finding_value VARCHAR(200) NOT NULL,
        finding_unit VARCHAR(50),
        normal_range VARCHAR(50),
        is_abnormal TINYINT DEFAULT 0,
        abnormal_severity ENUM('Mild', 'Moderate', 'Severe', 'Critical'),
        FOREIGN KEY (report_id) REFERENCES Report(report_id) ON DELETE CASCADE
    );

    -- Chat History table
    CREATE TABLE IF NOT EXISTS Chat_History (
        chat_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT,
        message_text TEXT NOT NULL,
        message_type ENUM('Patient', 'Provider', 'System', 'Bot'),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_id VARCHAR(100),
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE
    );
    """
    
    # Execute each table creation separately
    for table_sql in tables_sql.split(';'):
        if table_sql.strip():
            execute_query(table_sql.strip())
    
    print("✅ All tables created/verified")


def create_patient(name, dob, sex):
    """Create a patient record"""
    query = """
    INSERT INTO Patient (name, dob, sex, created_at, updated_at)
    VALUES (?, ?, ?, NOW(), NOW())
    """
    return execute_query(query, (name, dob, sex))


def create_medical_history(patient_id, history_type, history_item, history_details, history_date, severity, is_active=1):
    """Create a medical history entry"""
    query = """
    INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, history_date, severity, is_active, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
    """
    return execute_query(query, (patient_id, history_type, history_item, history_details, history_date, severity, is_active))


def create_appointment(patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name, notes):
    """Create an appointment record"""
    query = """
    INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    return execute_query(query, (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name, notes))


def create_appointment_symptom(appointment_id, symptom_name, symptom_description, severity, duration, onset_type):
    """Create an appointment symptom record"""
    query = """
    INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration, onset_type)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    return execute_query(query, (appointment_id, symptom_name, symptom_description, severity, duration, onset_type))


def create_medication(patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by):
    """Create a medication record"""
    query = """
    INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    return execute_query(query, (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by))


def create_medication_purpose(medication_id, condition_name, purpose_description):
    """Create a medication purpose entry"""
    query = """
    INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
    VALUES (?, ?, ?)
    """
    return execute_query(query, (medication_id, condition_name, purpose_description))


def create_lab_report(patient_id, lab_date, lab_type, ordering_doctor, lab_facility):
    """Create a lab report"""
    query = """
    INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
    VALUES (?, ?, ?, ?, ?)
    """
    return execute_query(query, (patient_id, lab_date, lab_type, ordering_doctor, lab_facility))


def create_lab_finding(lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag):
    """Create a lab finding"""
    query = """
    INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    return execute_query(query, (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag))


def create_report(patient_id, report_type, report_date, complete_report, report_summary, doctor_name):
    """Create a medical report"""
    query = """
    INSERT INTO Report (patient_id, report_type, report_date, complete_report, report_summary, doctor_name, created_at)
    VALUES (?, ?, ?, ?, ?, ?, NOW())
    """
    return execute_query(query, (patient_id, report_type, report_date, complete_report, report_summary, doctor_name))


def create_report_finding(report_id, finding_key, finding_value, finding_unit, normal_range, is_abnormal, abnormal_severity):
    """Create a report finding"""
    query = """
    INSERT INTO Report_Finding (report_id, finding_key, finding_value, finding_unit, normal_range, is_abnormal, abnormal_severity)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    return execute_query(query, (report_id, finding_key, finding_value, finding_unit, normal_range, is_abnormal, abnormal_severity))


def create_chat_history(patient_id, message_text, message_type, session_id):
    """Create a chat history entry"""
    query = """
    INSERT INTO Chat_History (patient_id, message_text, message_type, timestamp, session_id)
    VALUES (?, ?, ?, NOW(), ?)
    """
    return execute_query(query, (patient_id, message_text, message_type, session_id))


def populate_comprehensive_patient(patient_num, custom_data=None):
    """Create a comprehensive patient with full medical data"""
    
    # Generate patient demographics
    sex = random.choice(["Male", "Female"])
    if sex == "Male":
        first_name = random.choice(FIRST_NAMES_MALE)
    else:
        first_name = random.choice(FIRST_NAMES_FEMALE)
    
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    dob = generate_dob(30, 70)
    
    # Override with custom data if provided
    if custom_data:
        name = custom_data.get('name', name)
        dob = custom_data.get('dob', dob)
        sex = custom_data.get('sex', sex)
    
    # Create patient
    patient_id = create_patient(name, dob, sex)
    if not patient_id:
        print(f"❌ Failed to create patient {patient_num}")
        return None
    
    print(f"\n{'='*60}")
    print(f"📋 Creating Patient {patient_num}: {name} (ID: {patient_id})")
    print(f"   DOB: {dob}, Sex: {sex}")
    print(f"{'='*60}")
    
    # Add medical history
    print("  📜 Adding medical history...")
    
    # Add 1-2 chronic conditions
    num_conditions = random.randint(1, 2)
    conditions = random.sample(CHRONIC_CONDITIONS, num_conditions)
    for condition, details, severity in conditions:
        history_date = generate_random_date(2018, 2023)
        create_medical_history(patient_id, "chronic_condition", condition, details, history_date, severity, 1)
        print(f"     - Chronic: {condition}")
    
    # Add 0-2 allergies
    num_allergies = random.randint(0, 2)
    if num_allergies > 0:
        allergies = random.sample(ALLERGIES, num_allergies)
        for allergy, details, severity in allergies:
            history_date = generate_random_date(2015, 2022)
            create_medical_history(patient_id, "allergy", allergy, details, history_date, severity, 1)
            print(f"     - Allergy: {allergy}")
    
    # Add 0-1 surgery
    if random.random() > 0.5:
        surgery, details = random.choice(SURGERIES)
        history_date = generate_random_date(2015, 2023)
        create_medical_history(patient_id, "surgery", surgery, details, history_date, "Moderate", 0)
        print(f"     - Surgery: {surgery}")
    
    # Add 0-1 family history
    if random.random() > 0.4:
        family, details, severity = random.choice(FAMILY_HISTORY)
        history_date = generate_random_date(2020, 2024)
        create_medical_history(patient_id, "family_history", family, details, history_date, severity, 1)
        print(f"     - Family History: {family}")
    
    # Add 1 lifestyle factor
    lifestyle, details, severity = random.choice(LIFESTYLE_FACTORS)
    history_date = generate_random_date(2020, 2024)
    create_medical_history(patient_id, "lifestyle", lifestyle, details, history_date, severity, 1)
    print(f"     - Lifestyle: {lifestyle}")
    
    # Add appointments with symptoms
    print("  📅 Adding appointments...")
    num_appointments = random.randint(2, 4)
    appointment_ids = []
    
    for i in range(num_appointments):
        appt_date = generate_random_date(2024, 2025)
        appt_time = f"{random.randint(8, 17):02d}:{random.choice(['00', '15', '30', '45'])}:00"
        status = random.choice(APPOINTMENT_STATUS)
        appt_type = random.choice(APPOINTMENT_TYPES)
        doctor = random.choice(DOCTORS)
        notes = f"{appt_type} visit for ongoing care"
        
        appt_id = create_appointment(patient_id, appt_date, appt_time, status, appt_type, doctor, notes)
        appointment_ids.append(appt_id)
        print(f"     - {appt_type} on {appt_date} with {doctor} ({status})")
        
        # Add symptoms to appointments
        if status in ["Completed", "Scheduled"]:
            num_symptoms = random.randint(1, 3)
            symptoms = random.sample(SYMPTOMS, num_symptoms)
            for symptom_name, description, severity, duration, onset in symptoms:
                create_appointment_symptom(appt_id, symptom_name, description, severity, duration, onset)
                print(f"       └─ Symptom: {symptom_name} ({severity})")
    
    # Add medications
    print("  💊 Adding medications...")
    num_medications = random.randint(2, 4)
    selected_meds = random.sample(MEDICATIONS, num_medications)
    
    for med_name, dosage, frequency, purposes in selected_meds:
        prescribed_date = generate_random_date(2022, 2024)
        is_continued = random.choice([0, 1, 1, 1])  # 75% chance of being continued
        discontinued_date = generate_random_date(prescribed_date.year + 1, 2025) if not is_continued else None
        doctor = random.choice(DOCTORS)
        
        med_id = create_medication(patient_id, med_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, doctor)
        status = "Active" if is_continued else "Discontinued"
        print(f"     - {med_name} {dosage} ({status})")
        
        # Add medication purposes
        for purpose in purposes[:2]:  # Max 2 purposes per medication
            create_medication_purpose(med_id, purpose, f"Treatment for {purpose}")
            print(f"       └─ Purpose: {purpose}")
    
    # Add lab reports and findings
    print("  🔬 Adding lab reports...")
    num_reports = random.randint(2, 3)
    lab_types = random.sample(list(LAB_TESTS.keys()), num_reports)
    
    for lab_type in lab_types:
        lab_date = generate_random_date(2024, 2025)
        doctor = random.choice(DOCTORS)
        facility = random.choice(LAB_FACILITIES)
        
        lab_id = create_lab_report(patient_id, lab_date, lab_type, doctor, facility)
        print(f"     - {lab_type} on {lab_date}")
        
        # Add findings for this lab type
        tests = LAB_TESTS[lab_type]
        for test_name, unit, ref_range in tests:
            is_abnormal = random.random() > 0.7  # 30% chance of abnormal
            value, flag = generate_lab_value(test_name, ref_range, is_abnormal)
            
            create_lab_finding(lab_id, test_name, value, unit, ref_range, 1 if is_abnormal else 0, flag)
            abnormal_marker = f" ⚠️ {flag}" if flag else ""
            print(f"       └─ {test_name}: {value} {unit}{abnormal_marker}")
    
    # Add a clinical report
    print("  📝 Adding clinical reports...")
    report_types = ["Clinical", "Consultation"]
    for _ in range(random.randint(1, 2)):
        report_type = random.choice(report_types)
        report_date = generate_random_date(2024, 2025)
        doctor = random.choice(DOCTORS)
        
        summary = f"Patient seen for {random.choice(['routine follow-up', 'new complaint evaluation', 'medication review', 'preventive care'])}. "
        summary += f"Overall condition is {random.choice(['stable', 'improving', 'requiring monitoring'])}."
        complete_report = summary + f"\n\nPlan: Continue current management. Follow up in {random.choice(['1 month', '3 months', '6 months'])}."
        
        report_id = create_report(patient_id, report_type, report_date, complete_report, summary, doctor)
        print(f"     - {report_type} Report on {report_date}")
        
        # Add some findings
        create_report_finding(report_id, "Vital Signs", "Within normal limits", None, None, 0, None)
        create_report_finding(report_id, "General Appearance", random.choice(["Alert and oriented", "No acute distress", "Well-appearing"]), None, None, 0, None)
    
    # Add chat history
    print("  💬 Adding chat history...")
    session_id = f"session_{patient_id}_{random.randint(1000, 9999)}"
    
    chat_messages = [
        ("Patient", f"Hi, I have a question about my {random.choice(['medication', 'test results', 'appointment', 'symptoms'])}."),
        ("Bot", "Hello! I'm here to help. What would you like to know?"),
        ("Patient", "Can you tell me more about my current prescriptions?"),
        ("Provider", "I've reviewed your records. Please let me know if you have any specific concerns."),
    ]
    
    for msg_type, msg_text in chat_messages:
        create_chat_history(patient_id, msg_text, msg_type, session_id)
    print(f"     - Added {len(chat_messages)} chat messages")
    
    return patient_id


def clear_all_data():
    """Clear all existing data from tables (in correct order for foreign keys)"""
    tables = [
        "Chat_History",
        "Report_Finding",
        "Report",
        "Lab_Finding",
        "Lab_Report",
        "Medication_Purpose",
        "Medication",
        "Appointment_Symptom",
        "Appointment",
        "Medical_History",
        "Patient"
    ]
    
    print("\n🗑️  Clearing existing data...")
    for table in tables:
        try:
            execute_query(f"DELETE FROM {table}")
            print(f"   ✓ Cleared {table}")
        except Exception as e:
            print(f"   ⚠️  Could not clear {table}: {e}")
    
    # Reset auto-increment
    for table in reversed(tables):
        try:
            execute_query(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
        except:
            pass
    
    print("✅ All data cleared\n")


def populate_database(num_patients=10, clear_existing=True):
    """Main function to populate the database"""
    print("\n" + "="*60)
    print("🏥 MediMax Database Population Script")
    print("="*60)
    
    # Create tables if needed
    create_tables()
    
    # Clear existing data if requested
    if clear_existing:
        clear_all_data()
    
    # Create patients
    print(f"\n📊 Creating {num_patients} comprehensive patient records...\n")
    
    patient_ids = []
    for i in range(1, num_patients + 1):
        patient_id = populate_comprehensive_patient(i)
        if patient_id:
            patient_ids.append(patient_id)
    
    # Summary
    print("\n" + "="*60)
    print("✅ DATABASE POPULATION COMPLETE")
    print("="*60)
    print(f"   Created {len(patient_ids)} patients with IDs: {patient_ids}")
    print(f"   Each patient has:")
    print(f"   - 3-6 Medical History entries")
    print(f"   - 2-4 Appointments with symptoms")
    print(f"   - 2-4 Medications with purposes")
    print(f"   - 2-3 Lab Reports with findings")
    print(f"   - 1-2 Clinical Reports")
    print(f"   - Chat history entries")
    print("="*60)
    
    return patient_ids


if __name__ == "__main__":
    import sys
    
    num_patients = 10
    if len(sys.argv) > 1:
        try:
            num_patients = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number of patients: {sys.argv[1]}")
            sys.exit(1)
    
    populate_database(num_patients=num_patients, clear_existing=True)
