#!/usr/bin/env python3
"""
Synthea MariaDB to Neo4j Knowledge Graph Translation Layer
==========================================================
Translates Synthea patient data from MariaDB (relational) to Neo4j (graph)
with a one-to-one native translation providing rich medical knowledge graph.

This creates a comprehensive healthcare knowledge graph with:

Node Types:
- Patient (central node with demographics)
- Organization (healthcare facilities)
- Provider (doctors/clinicians)
- Encounter (visits/appointments)
- Condition (diagnoses, medical history)
- Medication (prescriptions)
- Allergy (patient allergies)
- Observation (labs, vitals)
- Procedure (medical procedures)
- CarePlan (treatment plans)
- Immunization (vaccines)
- Device (medical devices)
- ImagingStudy (radiology)

Relationships:
- Patient -> HAS_ENCOUNTER -> Encounter
- Patient -> HAS_CONDITION -> Condition
- Patient -> TAKES_MEDICATION -> Medication
- Patient -> HAS_ALLERGY -> Allergy
- Patient -> HAS_OBSERVATION -> Observation
- Patient -> HAD_PROCEDURE -> Procedure
- Patient -> HAS_CARE_PLAN -> CarePlan
- Patient -> RECEIVED_IMMUNIZATION -> Immunization
- Patient -> HAS_DEVICE -> Device
- Patient -> HAS_IMAGING_STUDY -> ImagingStudy
- Encounter -> AT_ORGANIZATION -> Organization
- Encounter -> WITH_PROVIDER -> Provider
- Encounter -> DIAGNOSED_CONDITION -> Condition
- Encounter -> PRESCRIBED_MEDICATION -> Medication
- Medication -> TREATS -> Condition
- Condition -> MAY_INDICATE -> Symptom
"""

import mariadb
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from datetime import datetime, date
import json
import argparse

# Load environment variables
load_dotenv()

# MariaDB configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))

# Neo4j configuration (local or Aura)
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
AURA_USER = os.getenv('AURA_USER', 'neo4j')
AURA_PASSWORD = os.getenv('AURA_PASSWORD')
NEO4J_AUTH = (AURA_USER, AURA_PASSWORD)

# Condition categorization for better graph organization
CONDITION_CATEGORIES = {
    'chronic': [
        'diabetes', 'hypertension', 'heart', 'copd', 'asthma', 'obesity',
        'chronic', 'arthritis', 'kidney disease', 'thyroid', 'depression',
        'anxiety', 'hyperlipidemia', 'atrial fibrillation'
    ],
    'acute': [
        'infection', 'fracture', 'injury', 'acute', 'appendicitis',
        'pneumonia', 'bronchitis', 'sinusitis', 'strep', 'flu'
    ],
    'preventive': [
        'screening', 'examination', 'checkup', 'wellness', 'prevention',
        'vaccination', 'immunization'
    ]
}


def get_mariadb_connection():
    """Establish MariaDB connection"""
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )


def fetch_all_from_mariadb(query, params=None):
    """Fetch all results from MariaDB"""
    conn = None
    try:
        conn = get_mariadb_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    
    except mariadb.Error as e:
        print(f"MariaDB error: {e}")
        return []
    finally:
        if conn:
            conn.close()


def convert_to_neo4j_compatible(value):
    """Convert Python values to Neo4j compatible format"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def run_neo4j_query(session, query, params=None):
    """Run a Neo4j query with error handling"""
    try:
        # Convert all params to Neo4j compatible format
        if params:
            params = {k: convert_to_neo4j_compatible(v) for k, v in params.items()}
        result = session.run(query, params or {})
        return result.consume()
    except Exception as e:
        print(f"Neo4j error: {e}")
        print(f"Query: {query[:200]}...")
        return None


def clear_neo4j_database(session):
    """Clear all nodes and relationships from Neo4j"""
    print("🗑️  Clearing existing Neo4j data...")
    
    # Delete in batches to avoid memory issues
    run_neo4j_query(session, "MATCH (n) DETACH DELETE n")
    
    print("✅ Neo4j database cleared")


def create_constraints_and_indexes(session):
    """Create necessary constraints and indexes in Neo4j"""
    print("📐 Creating constraints and indexes...")
    
    constraints = [
        # Patient
        "CREATE CONSTRAINT patient_synthea_id IF NOT EXISTS FOR (p:Patient) REQUIRE p.synthea_id IS UNIQUE",
        "CREATE INDEX patient_name IF NOT EXISTS FOR (p:Patient) ON (p.name)",
        
        # Organization
        "CREATE CONSTRAINT organization_synthea_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.synthea_id IS UNIQUE",
        "CREATE INDEX organization_name IF NOT EXISTS FOR (o:Organization) ON (o.name)",
        
        # Provider
        "CREATE CONSTRAINT provider_synthea_id IF NOT EXISTS FOR (pr:Provider) REQUIRE pr.synthea_id IS UNIQUE",
        "CREATE INDEX provider_name IF NOT EXISTS FOR (pr:Provider) ON (pr.name)",
        
        # Encounter
        "CREATE CONSTRAINT encounter_synthea_id IF NOT EXISTS FOR (e:Encounter) REQUIRE e.synthea_id IS UNIQUE",
        
        # Condition
        "CREATE INDEX condition_code IF NOT EXISTS FOR (c:Condition) ON (c.code)",
        "CREATE INDEX condition_description IF NOT EXISTS FOR (c:Condition) ON (c.description)",
        
        # Medication
        "CREATE INDEX medication_code IF NOT EXISTS FOR (m:Medication) ON (m.code)",
        "CREATE INDEX medication_description IF NOT EXISTS FOR (m:Medication) ON (m.description)",
        
        # Observation
        "CREATE INDEX observation_code IF NOT EXISTS FOR (o:Observation) ON (o.code)",
        "CREATE INDEX observation_category IF NOT EXISTS FOR (o:Observation) ON (o.category)",
        
        # Procedure
        "CREATE INDEX procedure_code IF NOT EXISTS FOR (p:Procedure) ON (p.code)",
    ]
    
    for constraint in constraints:
        try:
            run_neo4j_query(session, constraint)
        except Exception as e:
            # Constraints may already exist
            pass
    
    print("✅ Constraints and indexes ready")


def categorize_condition(description):
    """Categorize a condition based on its description"""
    if not description:
        return 'other'
    
    desc_lower = description.lower()
    for category, keywords in CONDITION_CATEGORIES.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category
    
    return 'other'


def sync_patients(session):
    """Sync Patient records from MariaDB to Neo4j"""
    print("\n👤 Syncing Patients...")
    
    patients = fetch_all_from_mariadb("SELECT * FROM Synthea_Patient")
    
    for patient in patients:
        # Build full name
        name_parts = [patient.get('prefix', ''), patient.get('first_name', ''), 
                      patient.get('middle_name', ''), patient.get('last_name', ''), 
                      patient.get('suffix', '')]
        full_name = ' '.join(p for p in name_parts if p).strip()
        
        # Calculate age if birthdate available
        age = None
        if patient.get('birthdate'):
            today = date.today()
            bd = patient['birthdate']
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        
        query = """
        MERGE (p:Patient:Person {synthea_id: $synthea_id})
        SET p.patient_id = $patient_id,
            p.name = $name,
            p.full_name = $full_name,
            p.first_name = $first_name,
            p.middle_name = $middle_name,
            p.last_name = $last_name,
            p.gender = $gender,
            p.birthdate = $birthdate,
            p.deathdate = $deathdate,
            p.age = $age,
            p.race = $race,
            p.ethnicity = $ethnicity,
            p.marital_status = $marital_status,
            p.address = $address,
            p.city = $city,
            p.state = $state,
            p.county = $county,
            p.zip = $zip,
            p.latitude = $latitude,
            p.longitude = $longitude,
            p.income = $income,
            p.healthcare_expenses = $healthcare_expenses,
            p.healthcare_coverage = $healthcare_coverage,
            p.is_deceased = $is_deceased,
            p.node_type = 'Patient',
            p.entity_type = 'person',
            p.data_source = 'Synthea',
            p.last_updated = datetime()
        """
        
        params = {
            'synthea_id': patient['synthea_id'],
            'patient_id': patient['patient_id'],
            'name': full_name,
            'full_name': full_name,
            'first_name': patient.get('first_name'),
            'middle_name': patient.get('middle_name'),
            'last_name': patient.get('last_name'),
            'gender': patient.get('gender'),
            'birthdate': patient.get('birthdate'),
            'deathdate': patient.get('deathdate'),
            'age': age,
            'race': patient.get('race'),
            'ethnicity': patient.get('ethnicity'),
            'marital_status': patient.get('marital_status'),
            'address': patient.get('address'),
            'city': patient.get('city'),
            'state': patient.get('state'),
            'county': patient.get('county'),
            'zip': patient.get('zip'),
            'latitude': float(patient.get('latitude') or 0),
            'longitude': float(patient.get('longitude') or 0),
            'income': patient.get('income'),
            'healthcare_expenses': float(patient.get('healthcare_expenses') or 0),
            'healthcare_coverage': float(patient.get('healthcare_coverage') or 0),
            'is_deceased': patient.get('deathdate') is not None
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(patients)} patients")
    return patients


def sync_organizations(session):
    """Sync Organization records from MariaDB to Neo4j"""
    print("\n🏥 Syncing Organizations...")
    
    orgs = fetch_all_from_mariadb("SELECT * FROM Synthea_Organization")
    
    for org in orgs:
        query = """
        MERGE (o:Organization:HealthcareFacility {synthea_id: $synthea_id})
        SET o.name = $name,
            o.address = $address,
            o.city = $city,
            o.state = $state,
            o.zip = $zip,
            o.phone = $phone,
            o.latitude = $latitude,
            o.longitude = $longitude,
            o.revenue = $revenue,
            o.utilization = $utilization,
            o.node_type = 'Organization',
            o.entity_type = 'facility',
            o.data_source = 'Synthea',
            o.last_updated = datetime()
        """
        
        params = {
            'synthea_id': org['synthea_id'],
            'name': org.get('name'),
            'address': org.get('address'),
            'city': org.get('city'),
            'state': org.get('state'),
            'zip': org.get('zip'),
            'phone': org.get('phone'),
            'latitude': float(org.get('latitude') or 0),
            'longitude': float(org.get('longitude') or 0),
            'revenue': float(org.get('revenue') or 0),
            'utilization': org.get('utilization')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(orgs)} organizations")
    return orgs


def sync_providers(session):
    """Sync Provider records from MariaDB to Neo4j"""
    print("\n👨‍⚕️ Syncing Providers...")
    
    providers = fetch_all_from_mariadb("SELECT * FROM Synthea_Provider")
    
    for provider in providers:
        query = """
        MERGE (pr:Provider:Clinician {synthea_id: $synthea_id})
        SET pr.name = $name,
            pr.gender = $gender,
            pr.speciality = $speciality,
            pr.address = $address,
            pr.city = $city,
            pr.state = $state,
            pr.zip = $zip,
            pr.latitude = $latitude,
            pr.longitude = $longitude,
            pr.utilization = $utilization,
            pr.organization_id = $organization_id,
            pr.node_type = 'Provider',
            pr.entity_type = 'clinician',
            pr.data_source = 'Synthea',
            pr.last_updated = datetime()
        
        WITH pr
        MATCH (o:Organization {synthea_id: $organization_id})
        MERGE (pr)-[:WORKS_AT]->(o)
        """
        
        params = {
            'synthea_id': provider['synthea_id'],
            'name': provider.get('name'),
            'gender': provider.get('gender'),
            'speciality': provider.get('speciality'),
            'address': provider.get('address'),
            'city': provider.get('city'),
            'state': provider.get('state'),
            'zip': provider.get('zip'),
            'latitude': float(provider.get('latitude') or 0),
            'longitude': float(provider.get('longitude') or 0),
            'utilization': provider.get('utilization'),
            'organization_id': provider.get('synthea_organization_id')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(providers)} providers")
    return providers


def sync_encounters(session):
    """Sync Encounter records from MariaDB to Neo4j"""
    print("\n📅 Syncing Encounters...")
    
    encounters = fetch_all_from_mariadb("SELECT * FROM Synthea_Encounter")
    
    for enc in encounters:
        query = """
        MATCH (p:Patient {synthea_id: $patient_id})
        MERGE (e:Encounter:Visit {synthea_id: $synthea_id})
        SET e.encounter_class = $encounter_class,
            e.code = $code,
            e.description = $description,
            e.start_datetime = $start_datetime,
            e.stop_datetime = $stop_datetime,
            e.base_cost = $base_cost,
            e.total_claim_cost = $total_claim_cost,
            e.payer_coverage = $payer_coverage,
            e.reason_code = $reason_code,
            e.reason_description = $reason_description,
            e.organization_id = $organization_id,
            e.provider_id = $provider_id,
            e.node_type = 'Encounter',
            e.entity_type = 'visit',
            e.data_source = 'Synthea',
            e.last_updated = datetime()
        
        MERGE (p)-[r:HAS_ENCOUNTER]->(e)
        SET r.date = $start_datetime,
            r.encounter_type = $encounter_class
        
        WITH e
        OPTIONAL MATCH (o:Organization {synthea_id: $organization_id})
        FOREACH (ignore IN CASE WHEN o IS NOT NULL THEN [1] ELSE [] END |
            MERGE (e)-[:AT_ORGANIZATION]->(o)
        )
        
        WITH e
        OPTIONAL MATCH (pr:Provider {synthea_id: $provider_id})
        FOREACH (ignore IN CASE WHEN pr IS NOT NULL THEN [1] ELSE [] END |
            MERGE (e)-[:WITH_PROVIDER]->(pr)
        )
        """
        
        params = {
            'synthea_id': enc['synthea_id'],
            'patient_id': enc['synthea_patient_id'],
            'encounter_class': enc.get('encounter_class'),
            'code': enc.get('code'),
            'description': enc.get('description'),
            'start_datetime': enc.get('start_datetime'),
            'stop_datetime': enc.get('stop_datetime'),
            'base_cost': float(enc.get('base_cost') or 0),
            'total_claim_cost': float(enc.get('total_claim_cost') or 0),
            'payer_coverage': float(enc.get('payer_coverage') or 0),
            'reason_code': enc.get('reason_code'),
            'reason_description': enc.get('reason_description'),
            'organization_id': enc.get('synthea_organization_id'),
            'provider_id': enc.get('synthea_provider_id')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(encounters)} encounters")
    return encounters


def sync_conditions(session):
    """Sync Condition records from MariaDB to Neo4j"""
    print("\n🩺 Syncing Conditions...")
    
    conditions = fetch_all_from_mariadb("SELECT * FROM Synthea_Condition")
    
    for cond in conditions:
        # Categorize the condition
        category = categorize_condition(cond.get('description'))
        
        # Determine severity based on category
        severity = 'moderate'
        if category == 'chronic':
            severity = 'significant'
        elif category == 'acute':
            severity = 'moderate'
        elif category == 'preventive':
            severity = 'low'
        
        query = """
        MATCH (p:Patient {synthea_id: $patient_id})
        CREATE (c:Condition:Diagnosis {
            condition_id: $condition_id,
            code: $code,
            code_system: $code_system,
            description: $description,
            name: $description,
            start_date: $start_date,
            stop_date: $stop_date,
            is_active: $is_active,
            category: $category,
            severity: $severity,
            encounter_id: $encounter_id,
            node_type: 'Condition',
            entity_type: 'diagnosis',
            data_source: 'Synthea',
            last_updated: datetime()
        })
        
        MERGE (p)-[r:HAS_CONDITION]->(c)
        SET r.onset_date = $start_date,
            r.resolved_date = $stop_date,
            r.is_active = $is_active,
            r.category = $category
        
        WITH c, p
        OPTIONAL MATCH (e:Encounter {synthea_id: $encounter_id})
        FOREACH (ignore IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END |
            MERGE (e)-[:DIAGNOSED_CONDITION]->(c)
        )
        """
        
        params = {
            'condition_id': cond['condition_id'],
            'patient_id': cond['synthea_patient_id'],
            'code': cond.get('code'),
            'code_system': cond.get('code_system'),
            'description': cond.get('description'),
            'start_date': cond.get('start_date'),
            'stop_date': cond.get('stop_date'),
            'is_active': cond.get('is_active', 1) == 1,
            'category': category,
            'severity': severity,
            'encounter_id': cond.get('synthea_encounter_id')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(conditions)} conditions")
    return conditions


def sync_medications(session):
    """Sync Medication records from MariaDB to Neo4j"""
    print("\n💊 Syncing Medications...")
    
    medications = fetch_all_from_mariadb("SELECT * FROM Synthea_Medication")
    
    for med in medications:
        query = """
        MATCH (p:Patient {synthea_id: $patient_id})
        CREATE (m:Medication:Prescription {
            medication_id: $medication_id,
            code: $code,
            description: $description,
            name: $description,
            start_datetime: $start_datetime,
            stop_datetime: $stop_datetime,
            base_cost: $base_cost,
            total_cost: $total_cost,
            dispenses: $dispenses,
            is_active: $is_active,
            reason_code: $reason_code,
            reason_description: $reason_description,
            encounter_id: $encounter_id,
            node_type: 'Medication',
            entity_type: 'prescription',
            data_source: 'Synthea',
            last_updated: datetime()
        })
        
        MERGE (p)-[r:TAKES_MEDICATION]->(m)
        SET r.start_date = $start_datetime,
            r.end_date = $stop_datetime,
            r.is_active = $is_active
        
        WITH m, p
        OPTIONAL MATCH (e:Encounter {synthea_id: $encounter_id})
        FOREACH (ignore IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END |
            MERGE (e)-[:PRESCRIBED_MEDICATION]->(m)
        )
        
        WITH m
        WHERE $reason_code IS NOT NULL AND $reason_code <> ''
        OPTIONAL MATCH (c:Condition)
        WHERE c.code = $reason_code
        FOREACH (ignore IN CASE WHEN c IS NOT NULL THEN [1] ELSE [] END |
            MERGE (m)-[:TREATS]->(c)
        )
        """
        
        params = {
            'medication_id': med['medication_id'],
            'patient_id': med['synthea_patient_id'],
            'code': med.get('code'),
            'description': med.get('description'),
            'start_datetime': med.get('start_datetime'),
            'stop_datetime': med.get('stop_datetime'),
            'base_cost': float(med.get('base_cost') or 0),
            'total_cost': float(med.get('total_cost') or 0),
            'dispenses': med.get('dispenses'),
            'is_active': med.get('is_active', 1) == 1,
            'reason_code': med.get('reason_code'),
            'reason_description': med.get('reason_description'),
            'encounter_id': med.get('synthea_encounter_id')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(medications)} medications")
    return medications


def sync_allergies(session):
    """Sync Allergy records from MariaDB to Neo4j"""
    print("\n🤧 Syncing Allergies...")
    
    allergies = fetch_all_from_mariadb("SELECT * FROM Synthea_Allergy")
    
    for allergy in allergies:
        # Determine severity from reactions
        severity = allergy.get('reaction1_severity') or 'mild'
        
        query = """
        MATCH (p:Patient {synthea_id: $patient_id})
        CREATE (a:Allergy {
            allergy_id: $allergy_id,
            code: $code,
            code_system: $code_system,
            description: $description,
            name: $description,
            allergy_type: $allergy_type,
            category: $category,
            reaction1: $reaction1,
            reaction1_severity: $reaction1_severity,
            reaction2: $reaction2,
            reaction2_severity: $reaction2_severity,
            start_date: $start_date,
            stop_date: $stop_date,
            is_active: $is_active,
            severity: $severity,
            node_type: 'Allergy',
            entity_type: 'allergy',
            data_source: 'Synthea',
            last_updated: datetime()
        })
        
        MERGE (p)-[r:HAS_ALLERGY]->(a)
        SET r.onset_date = $start_date,
            r.is_active = $is_active,
            r.severity = $severity
        """
        
        params = {
            'allergy_id': allergy['allergy_id'],
            'patient_id': allergy['synthea_patient_id'],
            'code': allergy.get('code'),
            'code_system': allergy.get('code_system'),
            'description': allergy.get('description'),
            'allergy_type': allergy.get('allergy_type'),
            'category': allergy.get('category'),
            'reaction1': allergy.get('reaction1_description'),
            'reaction1_severity': allergy.get('reaction1_severity'),
            'reaction2': allergy.get('reaction2_description'),
            'reaction2_severity': allergy.get('reaction2_severity'),
            'start_date': allergy.get('start_date'),
            'stop_date': allergy.get('stop_date'),
            'is_active': allergy.get('is_active', 1) == 1,
            'severity': severity
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(allergies)} allergies")
    return allergies


def sync_observations(session):
    """Sync Observation records from MariaDB to Neo4j"""
    print("\n📊 Syncing Observations (this may take a while)...")
    
    # Sync vital signs and important lab observations only to reduce graph size
    observations = fetch_all_from_mariadb("""
        SELECT * FROM Synthea_Observation 
        WHERE category IN ('vital-signs', 'laboratory')
        ORDER BY observation_date DESC
    """)
    
    batch_size = 500
    total_synced = 0
    
    for i in range(0, len(observations), batch_size):
        batch = observations[i:i+batch_size]
        
        for obs in batch:
            # Determine observation type label
            obs_label = "Observation"
            if obs.get('category') == 'vital-signs':
                obs_label = "Observation:VitalSign"
            elif obs.get('category') == 'laboratory':
                obs_label = "Observation:LabResult"
            
            query = f"""
            MATCH (p:Patient {{synthea_id: $patient_id}})
            CREATE (o:{obs_label} {{
                observation_id: $observation_id,
                code: $code,
                description: $description,
                name: $description,
                value: $value,
                units: $units,
                value_type: $value_type,
                category: $category,
                observation_date: $observation_date,
                encounter_id: $encounter_id,
                node_type: 'Observation',
                entity_type: $category,
                data_source: 'Synthea',
                last_updated: datetime()
            }})
            
            MERGE (p)-[r:HAS_OBSERVATION]->(o)
            SET r.date = $observation_date,
                r.category = $category
            
            WITH o
            OPTIONAL MATCH (e:Encounter {{synthea_id: $encounter_id}})
            FOREACH (ignore IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END |
                MERGE (e)-[:RECORDED_OBSERVATION]->(o)
            )
            """
            
            params = {
                'observation_id': obs['observation_id'],
                'patient_id': obs['synthea_patient_id'],
                'code': obs.get('code'),
                'description': obs.get('description'),
                'value': obs.get('value'),
                'units': obs.get('units'),
                'value_type': obs.get('value_type'),
                'category': obs.get('category'),
                'observation_date': obs.get('observation_date'),
                'encounter_id': obs.get('synthea_encounter_id')
            }
            
            run_neo4j_query(session, query, params)
        
        total_synced += len(batch)
        print(f"   ... {total_synced}/{len(observations)} observations synced", end='\r')
    
    print(f"\n   ✓ Synced {len(observations)} observations")
    return observations


def sync_procedures(session):
    """Sync Procedure records from MariaDB to Neo4j"""
    print("\n🔧 Syncing Procedures...")
    
    procedures = fetch_all_from_mariadb("SELECT * FROM Synthea_Procedure")
    
    for proc in procedures:
        query = """
        MATCH (p:Patient {synthea_id: $patient_id})
        CREATE (pr:Procedure:MedicalProcedure {
            procedure_id: $procedure_id,
            code: $code,
            code_system: $code_system,
            description: $description,
            name: $description,
            start_datetime: $start_datetime,
            stop_datetime: $stop_datetime,
            base_cost: $base_cost,
            reason_code: $reason_code,
            reason_description: $reason_description,
            encounter_id: $encounter_id,
            node_type: 'Procedure',
            entity_type: 'procedure',
            data_source: 'Synthea',
            last_updated: datetime()
        })
        
        MERGE (p)-[r:HAD_PROCEDURE]->(pr)
        SET r.date = $start_datetime,
            r.reason = $reason_description
        
        WITH pr
        OPTIONAL MATCH (e:Encounter {synthea_id: $encounter_id})
        FOREACH (ignore IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END |
            MERGE (e)-[:PERFORMED_PROCEDURE]->(pr)
        )
        """
        
        params = {
            'procedure_id': proc['procedure_id'],
            'patient_id': proc['synthea_patient_id'],
            'code': proc.get('code'),
            'code_system': proc.get('code_system'),
            'description': proc.get('description'),
            'start_datetime': proc.get('start_datetime'),
            'stop_datetime': proc.get('stop_datetime'),
            'base_cost': float(proc.get('base_cost') or 0),
            'reason_code': proc.get('reason_code'),
            'reason_description': proc.get('reason_description'),
            'encounter_id': proc.get('synthea_encounter_id')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(procedures)} procedures")
    return procedures


def sync_careplans(session):
    """Sync CarePlan records from MariaDB to Neo4j"""
    print("\n📋 Syncing Care Plans...")
    
    careplans = fetch_all_from_mariadb("SELECT * FROM Synthea_CarePlan")
    
    for cp in careplans:
        query = """
        MATCH (p:Patient {synthea_id: $patient_id})
        CREATE (c:CarePlan:TreatmentPlan {
            careplan_id: $careplan_id,
            synthea_id: $synthea_id,
            code: $code,
            description: $description,
            name: $description,
            start_date: $start_date,
            stop_date: $stop_date,
            is_active: $is_active,
            reason_code: $reason_code,
            reason_description: $reason_description,
            encounter_id: $encounter_id,
            node_type: 'CarePlan',
            entity_type: 'careplan',
            data_source: 'Synthea',
            last_updated: datetime()
        })
        
        MERGE (p)-[r:HAS_CARE_PLAN]->(c)
        SET r.start_date = $start_date,
            r.is_active = $is_active
        
        WITH c
        OPTIONAL MATCH (e:Encounter {synthea_id: $encounter_id})
        FOREACH (ignore IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END |
            MERGE (e)-[:CREATED_CARE_PLAN]->(c)
        )
        """
        
        params = {
            'careplan_id': cp['careplan_id'],
            'synthea_id': cp.get('synthea_id'),
            'patient_id': cp['synthea_patient_id'],
            'code': cp.get('code'),
            'description': cp.get('description'),
            'start_date': cp.get('start_date'),
            'stop_date': cp.get('stop_date'),
            'is_active': cp.get('is_active', 1) == 1,
            'reason_code': cp.get('reason_code'),
            'reason_description': cp.get('reason_description'),
            'encounter_id': cp.get('synthea_encounter_id')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(careplans)} care plans")
    return careplans


def sync_immunizations(session):
    """Sync Immunization records from MariaDB to Neo4j"""
    print("\n💉 Syncing Immunizations...")
    
    immunizations = fetch_all_from_mariadb("SELECT * FROM Synthea_Immunization")
    
    for imm in immunizations:
        query = """
        MATCH (p:Patient {synthea_id: $patient_id})
        CREATE (i:Immunization:Vaccine {
            immunization_id: $immunization_id,
            code: $code,
            description: $description,
            name: $description,
            immunization_date: $immunization_date,
            base_cost: $base_cost,
            encounter_id: $encounter_id,
            node_type: 'Immunization',
            entity_type: 'vaccine',
            data_source: 'Synthea',
            last_updated: datetime()
        })
        
        MERGE (p)-[r:RECEIVED_IMMUNIZATION]->(i)
        SET r.date = $immunization_date
        
        WITH i
        OPTIONAL MATCH (e:Encounter {synthea_id: $encounter_id})
        FOREACH (ignore IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END |
            MERGE (e)-[:ADMINISTERED_IMMUNIZATION]->(i)
        )
        """
        
        params = {
            'immunization_id': imm['immunization_id'],
            'patient_id': imm['synthea_patient_id'],
            'code': imm.get('code'),
            'description': imm.get('description'),
            'immunization_date': imm.get('immunization_date'),
            'base_cost': float(imm.get('base_cost') or 0),
            'encounter_id': imm.get('synthea_encounter_id')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(immunizations)} immunizations")
    return immunizations


def sync_devices(session):
    """Sync Device records from MariaDB to Neo4j"""
    print("\n🔌 Syncing Devices...")
    
    devices = fetch_all_from_mariadb("SELECT * FROM Synthea_Device")
    
    for dev in devices:
        query = """
        MATCH (p:Patient {synthea_id: $patient_id})
        CREATE (d:Device:MedicalDevice {
            device_id: $device_id,
            code: $code,
            description: $description,
            name: $description,
            udi: $udi,
            start_datetime: $start_datetime,
            stop_datetime: $stop_datetime,
            encounter_id: $encounter_id,
            node_type: 'Device',
            entity_type: 'device',
            data_source: 'Synthea',
            last_updated: datetime()
        })
        
        MERGE (p)-[r:HAS_DEVICE]->(d)
        SET r.start_date = $start_datetime,
            r.end_date = $stop_datetime
        
        WITH d
        OPTIONAL MATCH (e:Encounter {synthea_id: $encounter_id})
        FOREACH (ignore IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END |
            MERGE (e)-[:IMPLANTED_DEVICE]->(d)
        )
        """
        
        params = {
            'device_id': dev['device_id'],
            'patient_id': dev['synthea_patient_id'],
            'code': dev.get('code'),
            'description': dev.get('description'),
            'udi': dev.get('udi'),
            'start_datetime': dev.get('start_datetime'),
            'stop_datetime': dev.get('stop_datetime'),
            'encounter_id': dev.get('synthea_encounter_id')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(devices)} devices")
    return devices


def sync_imaging_studies(session):
    """Sync Imaging Study records from MariaDB to Neo4j"""
    print("\n🔬 Syncing Imaging Studies...")
    
    imaging = fetch_all_from_mariadb("SELECT * FROM Synthea_ImagingStudy")
    
    for img in imaging:
        query = """
        MATCH (p:Patient {synthea_id: $patient_id})
        CREATE (i:ImagingStudy:Radiology {
            imaging_id: $imaging_id,
            synthea_id: $synthea_id,
            series_uid: $series_uid,
            study_date: $study_date,
            bodysite_code: $bodysite_code,
            bodysite_description: $bodysite_description,
            modality_code: $modality_code,
            modality_description: $modality_description,
            procedure_code: $procedure_code,
            encounter_id: $encounter_id,
            node_type: 'ImagingStudy',
            entity_type: 'radiology',
            data_source: 'Synthea',
            last_updated: datetime()
        })
        
        MERGE (p)-[r:HAS_IMAGING_STUDY]->(i)
        SET r.date = $study_date,
            r.modality = $modality_code
        
        WITH i
        OPTIONAL MATCH (e:Encounter {synthea_id: $encounter_id})
        FOREACH (ignore IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END |
            MERGE (e)-[:ORDERED_IMAGING]->(i)
        )
        """
        
        params = {
            'imaging_id': img['imaging_id'],
            'synthea_id': img.get('synthea_id'),
            'patient_id': img['synthea_patient_id'],
            'series_uid': img.get('series_uid'),
            'study_date': img.get('study_date'),
            'bodysite_code': img.get('bodysite_code'),
            'bodysite_description': img.get('bodysite_description'),
            'modality_code': img.get('modality_code'),
            'modality_description': img.get('modality_description'),
            'procedure_code': img.get('procedure_code'),
            'encounter_id': img.get('synthea_encounter_id')
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced {len(imaging)} imaging studies")
    return imaging


def create_medical_knowledge_relationships(session):
    """Create additional knowledge graph relationships"""
    print("\n🔗 Creating Medical Knowledge Relationships...")
    
    # Link medications to conditions they treat
    query1 = """
    MATCH (m:Medication)
    WHERE m.reason_code IS NOT NULL AND m.reason_code <> ''
    MATCH (c:Condition {code: m.reason_code})
    WHERE NOT (m)-[:TREATS]->(c)
    MERGE (m)-[:TREATS]->(c)
    """
    run_neo4j_query(session, query1)
    print("   ✓ Linked medications to conditions")
    
    # Create SAME_DIAGNOSIS relationships between conditions with same code
    query2 = """
    MATCH (c1:Condition), (c2:Condition)
    WHERE c1.code = c2.code AND id(c1) < id(c2)
    MERGE (c1)-[:SAME_DIAGNOSIS]->(c2)
    """
    run_neo4j_query(session, query2)
    print("   ✓ Linked same diagnoses")
    
    # Create relationships between chronic conditions and related procedures
    query3 = """
    MATCH (p:Patient)-[:HAS_CONDITION]->(c:Condition {is_active: true})
    MATCH (p)-[:HAD_PROCEDURE]->(pr:Procedure)
    WHERE pr.reason_code = c.code
    MERGE (pr)-[:TREATMENT_FOR]->(c)
    """
    run_neo4j_query(session, query3)
    print("   ✓ Linked procedures to conditions")
    
    print("   ✓ Medical knowledge relationships created")


def sync_ai_features(session):
    """
    Sync AI model features from MariaDB to Neo4j.
    Creates AIFeatureSet nodes linked to patients with all ML model inputs.
    """
    print("\n🤖 Syncing AI Model Features...")
    
    # Fetch AI features from MariaDB
    features = fetch_all_from_mariadb("""
        SELECT * FROM Patient_AI_Features
    """)
    
    if not features:
        print("   ℹ️  No AI features found - run synthea_to_mariadb.py first")
        return
    
    for feature in features:
        # Create AIFeatureSet node and link to patient
        query = """
        MATCH (p:Patient {synthea_id: $synthea_patient_id})
        MERGE (ai:AIFeatureSet {patient_id: $synthea_patient_id})
        SET ai.age_years = $age_years,
            ai.gender = $gender,
            ai.gender_numeric = $gender_numeric,
            ai.height_cm = $height_cm,
            ai.weight_kg = $weight_kg,
            ai.bmi = $bmi,
            ai.bp_systolic = $bp_systolic,
            ai.bp_diastolic = $bp_diastolic,
            ai.cholesterol_level = $cholesterol_level,
            ai.glucose_level = $glucose_level,
            ai.is_smoker = $is_smoker,
            ai.alcohol_use = $alcohol_use,
            ai.physical_activity = $physical_activity,
            ai.has_hypertension = $has_hypertension,
            ai.has_heart_disease = $has_heart_disease,
            ai.smoking_history = $smoking_history,
            ai.hba1c_level = $hba1c_level,
            ai.blood_glucose_fasting = $blood_glucose_fasting,
            ai.total_cholesterol = $total_cholesterol,
            ai.hdl_cholesterol = $hdl_cholesterol,
            ai.ldl_cholesterol = $ldl_cholesterol,
            ai.triglycerides = $triglycerides,
            ai.cardio_risk_score = $cardio_risk_score,
            ai.diabetes_risk_score = $diabetes_risk_score,
            ai.node_type = 'AIFeatureSet',
            ai.data_source = 'Synthea_AI',
            ai.last_updated = datetime()
        MERGE (p)-[:HAS_AI_FEATURES]->(ai)
        """
        
        params = {
            'synthea_patient_id': feature['synthea_patient_id'],
            'age_years': feature.get('age_years'),
            'gender': feature.get('gender'),
            'gender_numeric': feature.get('gender_numeric'),
            'height_cm': float(feature['height_cm']) if feature.get('height_cm') else None,
            'weight_kg': float(feature['weight_kg']) if feature.get('weight_kg') else None,
            'bmi': float(feature['bmi']) if feature.get('bmi') else None,
            'bp_systolic': float(feature['bp_systolic']) if feature.get('bp_systolic') else None,
            'bp_diastolic': float(feature['bp_diastolic']) if feature.get('bp_diastolic') else None,
            'cholesterol_level': feature.get('cholesterol_level'),
            'glucose_level': feature.get('glucose_level'),
            'is_smoker': feature.get('is_smoker'),
            'alcohol_use': feature.get('alcohol_use'),
            'physical_activity': feature.get('physical_activity'),
            'has_hypertension': feature.get('has_hypertension'),
            'has_heart_disease': feature.get('has_heart_disease'),
            'smoking_history': feature.get('smoking_history'),
            'hba1c_level': float(feature['hba1c_level']) if feature.get('hba1c_level') else None,
            'blood_glucose_fasting': float(feature['blood_glucose_fasting']) if feature.get('blood_glucose_fasting') else None,
            'total_cholesterol': float(feature['total_cholesterol']) if feature.get('total_cholesterol') else None,
            'hdl_cholesterol': float(feature['hdl_cholesterol']) if feature.get('hdl_cholesterol') else None,
            'ldl_cholesterol': float(feature['ldl_cholesterol']) if feature.get('ldl_cholesterol') else None,
            'triglycerides': float(feature['triglycerides']) if feature.get('triglycerides') else None,
            'cardio_risk_score': float(feature['cardio_risk_score']) if feature.get('cardio_risk_score') else None,
            'diabetes_risk_score': float(feature['diabetes_risk_score']) if feature.get('diabetes_risk_score') else None,
        }
        
        run_neo4j_query(session, query, params)
    
    print(f"   ✓ Synced AI features for {len(features)} patients")
    
    # Create RiskFactor nodes for common conditions
    print("\n   Creating Risk Factor knowledge nodes...")
    
    risk_factors_query = """
    // Create common risk factor nodes
    MERGE (rf1:RiskFactor {name: 'Hypertension'})
    SET rf1.description = 'High blood pressure - systolic ≥140 or diastolic ≥90',
        rf1.category = 'cardiovascular',
        rf1.threshold_systolic = 140,
        rf1.threshold_diastolic = 90
    
    MERGE (rf2:RiskFactor {name: 'Diabetes'})
    SET rf2.description = 'Diabetes mellitus - HbA1c ≥6.5% or fasting glucose ≥126',
        rf2.category = 'metabolic',
        rf2.threshold_hba1c = 6.5,
        rf2.threshold_glucose = 126
    
    MERGE (rf3:RiskFactor {name: 'Obesity'})
    SET rf3.description = 'Body mass index ≥30',
        rf3.category = 'metabolic',
        rf3.threshold_bmi = 30
    
    MERGE (rf4:RiskFactor {name: 'Hypercholesterolemia'})
    SET rf4.description = 'High cholesterol - total cholesterol ≥240',
        rf4.category = 'cardiovascular',
        rf4.threshold_total_cholesterol = 240
    
    MERGE (rf5:RiskFactor {name: 'Smoking'})
    SET rf5.description = 'Current or former tobacco use',
        rf5.category = 'lifestyle'
    
    MERGE (rf6:RiskFactor {name: 'Physical Inactivity'})
    SET rf6.description = 'Sedentary lifestyle',
        rf6.category = 'lifestyle'
    """
    run_neo4j_query(session, risk_factors_query)
    
    # Link patients to relevant risk factors based on their AI features
    risk_links_query = """
    // Link hypertensive patients
    MATCH (p:Patient)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
    WHERE ai.has_hypertension = 1 OR ai.bp_systolic >= 140 OR ai.bp_diastolic >= 90
    MATCH (rf:RiskFactor {name: 'Hypertension'})
    MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
    
    WITH 1 as dummy
    
    // Link diabetic/pre-diabetic patients
    MATCH (p:Patient)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
    WHERE ai.hba1c_level >= 6.5 OR ai.blood_glucose_fasting >= 126
    MATCH (rf:RiskFactor {name: 'Diabetes'})
    MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
    
    WITH 1 as dummy
    
    // Link obese patients
    MATCH (p:Patient)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
    WHERE ai.bmi >= 30
    MATCH (rf:RiskFactor {name: 'Obesity'})
    MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
    
    WITH 1 as dummy
    
    // Link high cholesterol patients
    MATCH (p:Patient)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
    WHERE ai.total_cholesterol >= 240
    MATCH (rf:RiskFactor {name: 'Hypercholesterolemia'})
    MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
    
    WITH 1 as dummy
    
    // Link smokers
    MATCH (p:Patient)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
    WHERE ai.is_smoker = 1
    MATCH (rf:RiskFactor {name: 'Smoking'})
    MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
    
    WITH 1 as dummy
    
    // Link inactive patients
    MATCH (p:Patient)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
    WHERE ai.physical_activity = 0
    MATCH (rf:RiskFactor {name: 'Physical Inactivity'})
    MERGE (p)-[:HAS_RISK_FACTOR]->(rf)
    """
    run_neo4j_query(session, risk_links_query)
    
    print("   ✓ Risk factor nodes and relationships created")


def get_sync_statistics(session):
    """Get statistics about the synced data"""
    stats = {}
    
    queries = {
        'Patients': "MATCH (n:Patient) RETURN count(n) as count",
        'Organizations': "MATCH (n:Organization) RETURN count(n) as count",
        'Providers': "MATCH (n:Provider) RETURN count(n) as count",
        'Encounters': "MATCH (n:Encounter) RETURN count(n) as count",
        'Conditions': "MATCH (n:Condition) RETURN count(n) as count",
        'Medications': "MATCH (n:Medication) RETURN count(n) as count",
        'Allergies': "MATCH (n:Allergy) RETURN count(n) as count",
        'Observations': "MATCH (n:Observation) RETURN count(n) as count",
        'Procedures': "MATCH (n:Procedure) RETURN count(n) as count",
        'Care Plans': "MATCH (n:CarePlan) RETURN count(n) as count",
        'Immunizations': "MATCH (n:Immunization) RETURN count(n) as count",
        'Devices': "MATCH (n:Device) RETURN count(n) as count",
        'Imaging Studies': "MATCH (n:ImagingStudy) RETURN count(n) as count",
        'AI Feature Sets': "MATCH (n:AIFeatureSet) RETURN count(n) as count",
        'Risk Factors': "MATCH (n:RiskFactor) RETURN count(n) as count",
        'Total Nodes': "MATCH (n) RETURN count(n) as count",
        'Total Relationships': "MATCH ()-[r]->() RETURN count(r) as count"
    }
    
    for label, query in queries.items():
        try:
            result = session.run(query)
            record = result.single()
            stats[label] = record['count'] if record else 0
        except:
            stats[label] = 0
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='Sync Synthea data from MariaDB to Neo4j')
    parser.add_argument('--clear', action='store_true',
                        help='Clear existing Neo4j data before syncing')
    parser.add_argument('--skip-observations', action='store_true',
                        help='Skip syncing observations (for faster sync)')
    parser.add_argument('--skip-ai-features', action='store_true',
                        help='Skip syncing AI model features')
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔄 Synthea MariaDB to Neo4j Knowledge Graph Translator")
    print("   (with AI Model Feature Integration)")
    print("=" * 70)
    
    # Connect to Neo4j
    print("\n🔌 Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        driver.verify_connectivity()
        print("✅ Connected to Neo4j Aura")
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        return
    
    with driver.session() as session:
        # Clear if requested
        if args.clear:
            clear_neo4j_database(session)
        
        # Create constraints and indexes
        create_constraints_and_indexes(session)
        
        # Sync all data
        print("\n" + "=" * 70)
        print("📥 Translating Synthea Data to Neo4j Knowledge Graph")
        print("=" * 70)
        
        sync_patients(session)
        sync_organizations(session)
        sync_providers(session)
        sync_encounters(session)
        sync_conditions(session)
        sync_medications(session)
        sync_allergies(session)
        
        if not args.skip_observations:
            sync_observations(session)
        else:
            print("\n📊 Skipping Observations (--skip-observations flag)")
        
        sync_procedures(session)
        sync_careplans(session)
        sync_immunizations(session)
        sync_devices(session)
        sync_imaging_studies(session)
        
        # Create medical knowledge relationships
        create_medical_knowledge_relationships(session)
        
        # Sync AI model features
        if not args.skip_ai_features:
            sync_ai_features(session)
        else:
            print("\n🤖 Skipping AI Features (--skip-ai-features flag)")
        
        # Show statistics
        print("\n" + "=" * 70)
        print("📊 Neo4j Knowledge Graph Statistics")
        print("=" * 70)
        
        stats = get_sync_statistics(session)
        for label, count in stats.items():
            print(f"   {label}: {count:,}")
    
    driver.close()
    
    print("\n" + "=" * 70)
    print("✅ Synthea data successfully translated to Neo4j Knowledge Graph!")
    print("=" * 70)
    print("\nAI Model Integration:")
    print("  - AIFeatureSet nodes created with ML model inputs")
    print("  - RiskFactor nodes linked to patients based on vitals/conditions")
    print("\nExample queries:")
    print("  - MATCH (p:Patient)-[:HAS_AI_FEATURES]->(ai) RETURN p.name, ai.bmi, ai.bp_systolic")
    print("  - MATCH (p:Patient)-[:HAS_RISK_FACTOR]->(rf) RETURN p.name, rf.name")
    print("  - MATCH (p:Patient) WHERE p.synthea_id = 'xxx' RETURN p, [(p)-[r]-(n) | {rel: type(r), node: n}]")


if __name__ == '__main__':
    main()
