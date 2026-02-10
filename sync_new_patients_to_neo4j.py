#!/usr/bin/env python3
"""
Incremental Sync to Neo4j
=========================
Syncs ONLY new/specified patients from MariaDB to Neo4j without
affecting the existing knowledge graph.

This script:
1. Takes a list of synthea_ids OR finds patients not yet in Neo4j
2. Creates Patient nodes with all relationships
3. Creates AIFeatureSet nodes for ML model integration
4. Links to existing RiskFactor nodes
5. PRESERVES all existing Neo4j data

Usage:
    python sync_new_patients_to_neo4j.py [--all-new] [--patient-ids ID1 ID2 ...]
"""

import mariadb
import os
from datetime import datetime, date
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

# MariaDB configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))

# Neo4j configuration
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
NEO4J_USER = os.getenv('AURA_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('AURA_PASSWORD')


def get_mariadb_connection():
    """Get MariaDB connection"""
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )


def get_neo4j_driver():
    """Get Neo4j driver"""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def execute_mariadb_query(query, params=None):
    """Execute MariaDB query and return results"""
    conn = None
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"MariaDB error: {e}")
        return []
    finally:
        if conn:
            conn.close()


def serialize_value(value):
    """Convert Python values to Neo4j-compatible types"""
    if value is None:
        return None
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, bytes):
        return value.decode('utf-8')
    return value


def get_existing_neo4j_patient_ids(driver):
    """Get list of synthea_ids already in Neo4j"""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Person)
            WHERE p.synthea_id IS NOT NULL
            RETURN p.synthea_id as id
        """)
        return set(r["id"] for r in result)


def get_new_patients_from_mariadb(existing_ids=None):
    """Get patients from MariaDB that are not in Neo4j"""
    
    # Get all patients from MariaDB with their AI features
    query = """
        SELECT 
            p.synthea_id,
            p.first_name,
            p.middle_name,
            p.last_name,
            p.prefix,
            p.gender,
            p.birthdate,
            p.deathdate,
            p.race,
            p.ethnicity,
            p.city,
            p.state,
            p.zip,
            ai.age_years,
            ai.gender_numeric,
            ai.height_cm,
            ai.weight_kg,
            ai.bmi,
            ai.bp_systolic,
            ai.bp_diastolic,
            ai.cholesterol_level,
            ai.glucose_level,
            ai.is_smoker,
            ai.smoking_history,
            ai.alcohol_use,
            ai.physical_activity,
            ai.has_hypertension,
            ai.has_heart_disease,
            ai.hba1c_level,
            ai.blood_glucose_fasting
        FROM Synthea_Patient p
        LEFT JOIN Patient_AI_Features ai ON p.synthea_id = ai.synthea_patient_id
    """
    
    patients = execute_mariadb_query(query)
    
    if existing_ids:
        patients = [p for p in patients if p['synthea_id'] not in existing_ids]
    
    return patients


def get_specific_patients_from_mariadb(synthea_ids):
    """Get specific patients by synthea_id"""
    if not synthea_ids:
        return []
    
    placeholders = ', '.join(['%s'] * len(synthea_ids))
    query = f"""
        SELECT 
            p.synthea_id,
            p.first_name,
            p.middle_name,
            p.last_name,
            p.prefix,
            p.gender,
            p.birthdate,
            p.deathdate,
            p.race,
            p.ethnicity,
            p.city,
            p.state,
            p.zip,
            ai.age_years,
            ai.gender_numeric,
            ai.height_cm,
            ai.weight_kg,
            ai.bmi,
            ai.bp_systolic,
            ai.bp_diastolic,
            ai.cholesterol_level,
            ai.glucose_level,
            ai.is_smoker,
            ai.smoking_history,
            ai.alcohol_use,
            ai.physical_activity,
            ai.has_hypertension,
            ai.has_heart_disease,
            ai.hba1c_level,
            ai.blood_glucose_fasting
        FROM Synthea_Patient p
        LEFT JOIN Patient_AI_Features ai ON p.synthea_id = ai.synthea_patient_id
        WHERE p.synthea_id IN ({placeholders})
    """
    
    return execute_mariadb_query(query, tuple(synthea_ids))


def get_patient_conditions(synthea_id):
    """Get conditions for a patient"""
    query = """
        SELECT code, description, is_active, start_date, stop_date
        FROM Synthea_Condition
        WHERE synthea_patient_id = %s
    """
    return execute_mariadb_query(query, (synthea_id,))


def get_patient_medications(synthea_id):
    """Get medications for a patient"""
    query = """
        SELECT code, description, is_active, start_datetime, stop_datetime
        FROM Synthea_Medication
        WHERE synthea_patient_id = %s
    """
    return execute_mariadb_query(query, (synthea_id,))


def get_patient_observations(synthea_id):
    """Get observations for a patient"""
    query = """
        SELECT code, description, value, units, observation_date, category
        FROM Synthea_Observation
        WHERE synthea_patient_id = %s
        ORDER BY observation_date DESC
    """
    return execute_mariadb_query(query, (synthea_id,))


def get_patient_allergies(synthea_id):
    """Get allergies for a patient"""
    query = """
        SELECT code, description, category, reaction1_description, is_active
        FROM Synthea_Allergy
        WHERE synthea_patient_id = %s
    """
    return execute_mariadb_query(query, (synthea_id,))


def create_patient_in_neo4j(session, patient):
    """Create a patient node with all relationships in Neo4j"""
    
    synthea_id = patient['synthea_id']
    
    # Build name
    name_parts = []
    if patient.get('prefix'):
        name_parts.append(patient['prefix'])
    if patient.get('first_name'):
        name_parts.append(patient['first_name'])
    if patient.get('middle_name'):
        name_parts.append(patient['middle_name'])
    if patient.get('last_name'):
        name_parts.append(patient['last_name'])
    full_name = ' '.join(name_parts)
    
    # Calculate age
    age = None
    if patient.get('birthdate'):
        birth = patient['birthdate']
        if isinstance(birth, str):
            birth = datetime.strptime(birth, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    
    # 1. Create Patient/Person node (with dual labels like Synthea data)
    patient_query = """
        MERGE (p:Person:Patient {synthea_id: $synthea_id})
        SET p.name = $name,
            p.first_name = $first_name,
            p.last_name = $last_name,
            p.gender = $gender,
            p.birthdate = $birthdate,
            p.deathdate = $deathdate,
            p.age = $age,
            p.race = $race,
            p.ethnicity = $ethnicity,
            p.city = $city,
            p.state = $state,
            p.zip = $zip,
            p.data_source = 'MariaDB_Custom',
            p.last_updated = datetime()
        RETURN p
    """
    
    session.run(patient_query, {
        "synthea_id": synthea_id,
        "name": full_name,
        "first_name": serialize_value(patient.get('first_name')),
        "last_name": serialize_value(patient.get('last_name')),
        "gender": serialize_value(patient.get('gender')),
        "birthdate": serialize_value(patient.get('birthdate')),
        "deathdate": serialize_value(patient.get('deathdate')),
        "age": str(age) if age else None,
        "race": serialize_value(patient.get('race')),
        "ethnicity": serialize_value(patient.get('ethnicity')),
        "city": serialize_value(patient.get('city')),
        "state": serialize_value(patient.get('state')),
        "zip": serialize_value(patient.get('zip'))
    })
    
    # 2. Create AIFeatureSet node if AI features exist
    if patient.get('bmi') is not None or patient.get('bp_systolic') is not None:
        ai_query = """
            MATCH (p:Person {synthea_id: $synthea_id})
            MERGE (ai:AIFeatureSet {patient_id: $synthea_id})
            SET ai.node_type = 'AIFeatureSet',
                ai.data_source = 'MariaDB_Custom',
                ai.last_updated = datetime(),
                ai.age_years = $age_years,
                ai.gender_numeric = $gender_numeric,
                ai.height_cm = $height_cm,
                ai.weight_kg = $weight_kg,
                ai.bmi = $bmi,
                ai.bp_systolic = $bp_systolic,
                ai.bp_diastolic = $bp_diastolic,
                ai.cholesterol_level = $cholesterol_level,
                ai.glucose_level = $glucose_level,
                ai.is_smoker = $is_smoker,
                ai.smoking_history = $smoking_history,
                ai.alcohol_use = $alcohol_use,
                ai.physical_activity = $physical_activity,
                ai.has_hypertension = $has_hypertension,
                ai.has_heart_disease = $has_heart_disease,
                ai.hba1c_level = $hba1c_level,
                ai.blood_glucose_fasting = $blood_glucose_fasting
            MERGE (p)-[:HAS_AI_FEATURES]->(ai)
            RETURN ai
        """
        
        session.run(ai_query, {
            "synthea_id": synthea_id,
            "age_years": str(patient.get('age_years')) if patient.get('age_years') else None,
            "gender_numeric": str(patient.get('gender_numeric')) if patient.get('gender_numeric') is not None else None,
            "height_cm": str(patient.get('height_cm')) if patient.get('height_cm') else None,
            "weight_kg": str(patient.get('weight_kg')) if patient.get('weight_kg') else None,
            "bmi": str(patient.get('bmi')) if patient.get('bmi') else None,
            "bp_systolic": str(patient.get('bp_systolic')) if patient.get('bp_systolic') else None,
            "bp_diastolic": str(patient.get('bp_diastolic')) if patient.get('bp_diastolic') else None,
            "cholesterol_level": str(patient.get('cholesterol_level')) if patient.get('cholesterol_level') else None,
            "glucose_level": str(patient.get('glucose_level')) if patient.get('glucose_level') else None,
            "is_smoker": str(patient.get('is_smoker')) if patient.get('is_smoker') is not None else None,
            "smoking_history": serialize_value(patient.get('smoking_history')),
            "alcohol_use": str(patient.get('alcohol_use')) if patient.get('alcohol_use') is not None else None,
            "physical_activity": str(patient.get('physical_activity')) if patient.get('physical_activity') is not None else None,
            "has_hypertension": str(patient.get('has_hypertension')) if patient.get('has_hypertension') is not None else None,
            "has_heart_disease": str(patient.get('has_heart_disease')) if patient.get('has_heart_disease') is not None else None,
            "hba1c_level": str(patient.get('hba1c_level')) if patient.get('hba1c_level') else None,
            "blood_glucose_fasting": str(patient.get('blood_glucose_fasting')) if patient.get('blood_glucose_fasting') else None
        })
    
    # 3. Create Conditions
    conditions = get_patient_conditions(synthea_id)
    for cond in conditions:
        cond_query = """
            MATCH (p:Person {synthea_id: $synthea_id})
            MERGE (c:Condition:Diagnosis {code: $code, patient_id: $synthea_id})
            SET c.description = $description,
                c.is_active = $is_active,
                c.start_date = $start_date,
                c.stop_date = $stop_date,
                c.data_source = 'MariaDB_Custom'
            MERGE (p)-[:HAS_CONDITION]->(c)
        """
        session.run(cond_query, {
            "synthea_id": synthea_id,
            "code": cond['code'],
            "description": cond['description'],
            "is_active": str(cond.get('is_active', 1)),
            "start_date": serialize_value(cond.get('start_date')),
            "stop_date": serialize_value(cond.get('stop_date'))
        })
    
    # 4. Create Medications
    medications = get_patient_medications(synthea_id)
    for med in medications:
        med_query = """
            MATCH (p:Person {synthea_id: $synthea_id})
            MERGE (m:Medication:Prescription {code: $code, patient_id: $synthea_id})
            SET m.description = $description,
                m.is_active = $is_active,
                m.start_datetime = $start_datetime,
                m.data_source = 'MariaDB_Custom'
            MERGE (p)-[:TAKES_MEDICATION]->(m)
        """
        session.run(med_query, {
            "synthea_id": synthea_id,
            "code": med['code'],
            "description": med['description'],
            "is_active": str(med.get('is_active', 1)),
            "start_datetime": serialize_value(med.get('start_datetime'))
        })
    
    # 5. Create Observations (vitals & labs)
    observations = get_patient_observations(synthea_id)
    for obs in observations:
        obs_query = """
            MATCH (p:Person {synthea_id: $synthea_id})
            MERGE (o:Observation {code: $code, patient_id: $synthea_id, date: $date})
            SET o.description = $description,
                o.value = $value,
                o.units = $units,
                o.category = $category,
                o.data_source = 'MariaDB_Custom'
            MERGE (p)-[:HAS_OBSERVATION]->(o)
        """
        # Add appropriate secondary label
        if obs.get('category') == 'vital-signs':
            obs_query = obs_query.replace('Observation {', 'Observation:VitalSign {')
        else:
            obs_query = obs_query.replace('Observation {', 'Observation:LabResult {')
        
        session.run(obs_query, {
            "synthea_id": synthea_id,
            "code": obs['code'],
            "description": obs['description'],
            "value": serialize_value(obs.get('value')),
            "units": serialize_value(obs.get('units')),
            "category": serialize_value(obs.get('category')),
            "date": serialize_value(obs.get('observation_date'))
        })
    
    # 6. Create Allergies
    allergies = get_patient_allergies(synthea_id)
    for allergy in allergies:
        allergy_query = """
            MATCH (p:Person {synthea_id: $synthea_id})
            MERGE (a:Allergy {code: $code, patient_id: $synthea_id})
            SET a.description = $description,
                a.category = $category,
                a.reaction = $reaction,
                a.data_source = 'MariaDB_Custom'
            MERGE (p)-[:HAS_ALLERGY]->(a)
        """
        session.run(allergy_query, {
            "synthea_id": synthea_id,
            "code": allergy['code'],
            "description": allergy['description'],
            "category": serialize_value(allergy.get('category')),
            "reaction": serialize_value(allergy.get('reaction1_description'))
        })
    
    # 7. Link to existing RiskFactor nodes based on conditions/features
    link_risk_factors(session, synthea_id, patient, conditions)
    
    return {
        "synthea_id": synthea_id,
        "name": full_name,
        "conditions": len(conditions),
        "medications": len(medications),
        "observations": len(observations)
    }


def link_risk_factors(session, synthea_id, patient, conditions):
    """Link patient to existing RiskFactor nodes based on their data"""
    
    condition_codes = [c['code'] for c in conditions]
    condition_descriptions = [c['description'].lower() for c in conditions]
    
    # Check for Hypertension
    has_hypertension = (
        patient.get('has_hypertension') == 1 or
        '59621000' in condition_codes or
        any('hypertension' in d for d in condition_descriptions) or
        (patient.get('bp_systolic') and patient.get('bp_systolic') >= 140) or
        (patient.get('bp_diastolic') and patient.get('bp_diastolic') >= 90)
    )
    
    # Check for Diabetes
    has_diabetes = (
        patient.get('hba1c_level') and float(patient.get('hba1c_level', 0)) >= 6.5 or
        patient.get('blood_glucose_fasting') and int(patient.get('blood_glucose_fasting', 0)) >= 126 or
        '44054006' in condition_codes or
        any('diabetes' in d for d in condition_descriptions)
    )
    
    # Check for Obesity
    has_obesity = (
        patient.get('bmi') and float(patient.get('bmi', 0)) >= 30 or
        '414916001' in condition_codes or
        any('obesity' in d for d in condition_descriptions)
    )
    
    # Link to RiskFactor nodes
    if has_hypertension:
        session.run("""
            MATCH (p:Person {synthea_id: $synthea_id})
            MERGE (rf:RiskFactor {name: 'Hypertension'})
            ON CREATE SET rf.category = 'cardiovascular', rf.description = 'High blood pressure'
            MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
        """, {"synthea_id": synthea_id})
    
    if has_diabetes:
        session.run("""
            MATCH (p:Person {synthea_id: $synthea_id})
            MERGE (rf:RiskFactor {name: 'Diabetes'})
            ON CREATE SET rf.category = 'metabolic', rf.description = 'Diabetes mellitus'
            MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
        """, {"synthea_id": synthea_id})
    
    if has_obesity:
        session.run("""
            MATCH (p:Person {synthea_id: $synthea_id})
            MERGE (rf:RiskFactor {name: 'Obesity'})
            ON CREATE SET rf.category = 'metabolic', rf.description = 'BMI >= 30'
            MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
        """, {"synthea_id": synthea_id})


def sync_specific_patients(synthea_ids):
    """Sync specific patients by their synthea_ids"""
    print("\n" + "="*60)
    print("🔄 INCREMENTAL SYNC TO NEO4J")
    print("="*60)
    print(f"Syncing {len(synthea_ids)} specific patients...")
    
    patients = get_specific_patients_from_mariadb(synthea_ids)
    
    if not patients:
        print("❌ No patients found with the specified IDs")
        return []
    
    driver = get_neo4j_driver()
    results = []
    
    try:
        with driver.session() as session:
            for patient in patients:
                result = create_patient_in_neo4j(session, patient)
                results.append(result)
                print(f"  ✅ Synced: {result['name']} ({result['synthea_id'][:20]}...)")
                print(f"      - {result['conditions']} conditions, {result['medications']} meds, {result['observations']} obs")
    finally:
        driver.close()
    
    print("\n" + "="*60)
    print(f"✅ Successfully synced {len(results)} patients to Neo4j")
    print("="*60)
    
    return results


def sync_all_new_patients():
    """Find and sync all patients in MariaDB that aren't in Neo4j"""
    print("\n" + "="*60)
    print("🔄 SYNCING ALL NEW PATIENTS TO NEO4J")
    print("="*60)
    
    driver = get_neo4j_driver()
    
    try:
        # Get existing patient IDs from Neo4j
        existing_ids = get_existing_neo4j_patient_ids(driver)
        print(f"📊 Found {len(existing_ids)} existing patients in Neo4j")
        
        # Get new patients from MariaDB
        patients = get_new_patients_from_mariadb(existing_ids)
        print(f"📊 Found {len(patients)} new patients in MariaDB")
        
        if not patients:
            print("✅ No new patients to sync!")
            return []
        
        results = []
        with driver.session() as session:
            for patient in patients:
                result = create_patient_in_neo4j(session, patient)
                results.append(result)
                print(f"  ✅ Synced: {result['name']} ({result['synthea_id'][:20]}...)")
        
        print("\n" + "="*60)
        print(f"✅ Successfully synced {len(results)} new patients to Neo4j")
        print("="*60)
        
        return results
        
    finally:
        driver.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Incremental sync patients to Neo4j")
    parser.add_argument("--all-new", action="store_true", help="Sync all patients not yet in Neo4j")
    parser.add_argument("--patient-ids", nargs="+", help="Specific synthea_ids to sync")
    args = parser.parse_args()
    
    if args.patient_ids:
        sync_specific_patients(args.patient_ids)
    elif args.all_new:
        sync_all_new_patients()
    else:
        print("Usage: python sync_new_patients_to_neo4j.py [--all-new] [--patient-ids ID1 ID2 ...]")
        print("\nOptions:")
        print("  --all-new       Find and sync all patients in MariaDB not in Neo4j")
        print("  --patient-ids   Sync specific patients by their synthea_id")
