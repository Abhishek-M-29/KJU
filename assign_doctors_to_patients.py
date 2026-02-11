"""
Script to assign doctors to patients in both MariaDB and Neo4j
This creates coherent doctor-patient relationships across both databases.
"""

import mariadb
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import random

# Load environment variables
load_dotenv()

# MariaDB config
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3305)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Neo4j config
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
NEO4J_USER = os.getenv('AURA_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('AURA_PASSWORD', '123456789')


def get_mariadb_connection():
    """Get MariaDB connection"""
    return mariadb.connect(**DB_CONFIG)


def get_neo4j_driver():
    """Get Neo4j driver"""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_doctors_by_specialization(cursor):
    """Get doctors grouped by specialization"""
    cursor.execute("""
        SELECT doctor_id, first_name, last_name, specialization 
        FROM Doctor 
        ORDER BY specialization, doctor_id
    """)
    doctors = cursor.fetchall()
    
    # Group by specialization
    doctors_by_spec = {}
    for doc in doctors:
        spec = doc[3]
        if spec not in doctors_by_spec:
            doctors_by_spec[spec] = []
        doctors_by_spec[spec].append({
            'doctor_id': doc[0],
            'first_name': doc[1],
            'last_name': doc[2],
            'specialization': spec
        })
    
    return doctors_by_spec


def get_patients_mariadb(cursor):
    """Get all patients from MariaDB"""
    cursor.execute("SELECT patient_id, name FROM Patient")
    return [{'patient_id': p[0], 'name': p[1]} for p in cursor.fetchall()]


def get_patients_neo4j(driver):
    """Get all patients from Neo4j"""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Patient)
            RETURN p.synthea_id as synthea_id, 
                   p.first_name as first_name, 
                   p.last_name as last_name,
                   p.name as name
            ORDER BY p.synthea_id
        """)
        return [dict(record) for record in result]


def assign_doctors_to_patient_mariadb(cursor, patient_id, doctor_assignments):
    """Assign doctors to a patient in MariaDB Patient_Doctor table"""
    # Clear existing assignments for this patient
    cursor.execute("DELETE FROM Patient_Doctor WHERE patient_id = %s", (patient_id,))
    
    # Insert new assignments
    for i, assignment in enumerate(doctor_assignments):
        is_primary = 1 if i == 0 else 0  # First doctor is primary
        cursor.execute("""
            INSERT INTO Patient_Doctor (patient_id, doctor_id, is_primary_doctor, notes)
            VALUES (%s, %s, %s, %s)
        """, (patient_id, assignment['doctor_id'], is_primary, assignment.get('notes', '')))


def create_doctor_nodes_neo4j(driver, doctors):
    """Create Doctor nodes in Neo4j if they don't exist"""
    with driver.session() as session:
        for doc in doctors:
            session.run("""
                MERGE (d:Doctor {doctor_id: $doctor_id})
                SET d.first_name = $first_name,
                    d.last_name = $last_name,
                    d.name = $name,
                    d.specialization = $specialization
            """, {
                'doctor_id': doc['doctor_id'],
                'first_name': doc['first_name'],
                'last_name': doc['last_name'],
                'name': f"Dr. {doc['first_name']} {doc['last_name']}",
                'specialization': doc['specialization']
            })
    print(f"✅ Created/Updated {len(doctors)} Doctor nodes in Neo4j")


def assign_doctors_to_patient_neo4j(driver, patient_synthea_id, doctor_assignments):
    """Assign doctors to a patient in Neo4j using TREATED_BY relationship"""
    with driver.session() as session:
        # Remove existing TREATED_BY relationships for this patient
        session.run("""
            MATCH (p:Patient {synthea_id: $synthea_id})-[r:TREATED_BY]->(:Doctor)
            DELETE r
        """, {'synthea_id': patient_synthea_id})
        
        # Create new relationships
        for i, assignment in enumerate(doctor_assignments):
            is_primary = i == 0
            session.run("""
                MATCH (p:Patient {synthea_id: $synthea_id})
                MATCH (d:Doctor {doctor_id: $doctor_id})
                MERGE (p)-[r:TREATED_BY]->(d)
                SET r.is_primary = $is_primary,
                    r.reason = $reason
            """, {
                'synthea_id': patient_synthea_id,
                'doctor_id': assignment['doctor_id'],
                'is_primary': is_primary,
                'reason': assignment.get('notes', '')
            })


def get_suitable_doctors_for_conditions(doctors_by_spec, patient_conditions):
    """Select suitable doctors based on patient conditions"""
    # Mapping of conditions to specializations
    condition_to_specialization = {
        'diabetes': ['Endocrinology', 'Internal Medicine'],
        'hypertension': ['Cardiology', 'Internal Medicine', 'Nephrology'],
        'heart': ['Cardiology', 'Internal Medicine'],
        'cardiovascular': ['Cardiology'],
        'kidney': ['Nephrology'],
        'renal': ['Nephrology'],
        'lung': ['Pulmonology'],
        'respiratory': ['Pulmonology'],
        'asthma': ['Pulmonology'],
        'copd': ['Pulmonology'],
        'arthritis': ['Rheumatology', 'Orthopedics'],
        'joint': ['Rheumatology', 'Orthopedics'],
        'bone': ['Orthopedics'],
        'skin': ['Dermatology'],
        'depression': ['Psychiatry'],
        'anxiety': ['Psychiatry'],
        'mental': ['Psychiatry'],
        'stomach': ['Gastroenterology'],
        'digestive': ['Gastroenterology'],
        'liver': ['Gastroenterology'],
        'thyroid': ['Endocrinology'],
        'brain': ['Neurology'],
        'nerve': ['Neurology'],
        'child': ['Pediatrics'],
        'emergency': ['Emergency Medicine'],
    }
    
    selected_specs = set()
    
    # Match conditions to specializations
    for condition in patient_conditions:
        condition_lower = condition.lower()
        for keyword, specs in condition_to_specialization.items():
            if keyword in condition_lower:
                selected_specs.update(specs)
    
    # Always include a general practitioner
    selected_specs.add('General Practice')
    
    # If no specific specialization found, add Internal Medicine
    if len(selected_specs) == 1:  # Only General Practice
        selected_specs.add('Internal Medicine')
    
    # Select doctors
    selected_doctors = []
    for spec in selected_specs:
        if spec in doctors_by_spec:
            # Pick a random doctor from this specialization
            doc = random.choice(doctors_by_spec[spec])
            if doc not in selected_doctors:
                selected_doctors.append(doc)
    
    return selected_doctors


def get_patient_conditions_neo4j(driver, synthea_id):
    """Get patient conditions from Neo4j"""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Patient {synthea_id: $synthea_id})-[:HAS_CONDITION]->(c:Condition)
            RETURN c.description as condition
        """, {'synthea_id': synthea_id})
        return [record['condition'] for record in result]


def main():
    """Main function to assign doctors to patients in both databases"""
    print("\n" + "="*70)
    print("🏥 ASSIGNING DOCTORS TO PATIENTS")
    print("="*70)
    
    # Connect to MariaDB
    print("\n1️⃣ Connecting to MariaDB...")
    conn = get_mariadb_connection()
    cursor = conn.cursor()
    print("✅ Connected to MariaDB")
    
    # Connect to Neo4j
    print("\n2️⃣ Connecting to Neo4j...")
    driver = get_neo4j_driver()
    driver.verify_connectivity()
    print("✅ Connected to Neo4j")
    
    try:
        # Get doctors grouped by specialization
        print("\n3️⃣ Loading doctors...")
        doctors_by_spec = get_doctors_by_specialization(cursor)
        all_doctors = []
        for spec, docs in doctors_by_spec.items():
            all_doctors.extend(docs)
            print(f"   {spec}: {len(docs)} doctors")
        
        # Create Doctor nodes in Neo4j
        print("\n4️⃣ Creating Doctor nodes in Neo4j...")
        create_doctor_nodes_neo4j(driver, all_doctors)
        
        # Get patients from Neo4j (they have conditions)
        print("\n5️⃣ Loading patients from Neo4j...")
        neo4j_patients = get_patients_neo4j(driver)
        print(f"✅ Found {len(neo4j_patients)} patients in Neo4j")
        
        # Get patients from MariaDB
        print("\n6️⃣ Loading patients from MariaDB...")
        mariadb_patients = get_patients_mariadb(cursor)
        print(f"✅ Found {len(mariadb_patients)} patients in MariaDB")
        
        # Process each Neo4j patient
        print("\n7️⃣ Assigning doctors to patients...")
        assignments_made = 0
        
        for patient in neo4j_patients:
            synthea_id = patient.get('synthea_id')
            patient_name = patient.get('name') or f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip()
            
            if not synthea_id:
                continue
            
            # Get patient conditions from Neo4j
            conditions = get_patient_conditions_neo4j(driver, synthea_id)
            
            # Select suitable doctors based on conditions
            selected_doctors = get_suitable_doctors_for_conditions(doctors_by_spec, conditions)
            
            # Limit to 3-5 doctors per patient
            selected_doctors = selected_doctors[:5]
            
            if not selected_doctors:
                # Assign a general practitioner if no conditions
                if 'General Practice' in doctors_by_spec:
                    selected_doctors = [random.choice(doctors_by_spec['General Practice'])]
            
            # Create assignments with notes
            doctor_assignments = []
            for doc in selected_doctors:
                notes = f"Treating for {doc['specialization']} related conditions"
                doctor_assignments.append({
                    'doctor_id': doc['doctor_id'],
                    'notes': notes
                })
            
            # Assign in Neo4j
            assign_doctors_to_patient_neo4j(driver, synthea_id, doctor_assignments)
            
            print(f"\n   📋 {patient_name} (ID: {synthea_id}):")
            print(f"      Conditions: {len(conditions)}")
            for doc in selected_doctors:
                is_primary = "⭐ Primary" if doc == selected_doctors[0] else ""
                print(f"      → Dr. {doc['first_name']} {doc['last_name']} ({doc['specialization']}) {is_primary}")
            
            assignments_made += len(doctor_assignments)
        
        # Now handle MariaDB patients
        print("\n8️⃣ Updating MariaDB Patient_Doctor table...")
        for patient in mariadb_patients:
            patient_id = patient['patient_id']
            patient_name = patient['name']
            
            # Assign a mix of doctors (random selection since we don't have conditions in MariaDB)
            specs_to_assign = ['General Practice', 'Internal Medicine', 'Cardiology']
            selected_doctors = []
            for spec in specs_to_assign:
                if spec in doctors_by_spec:
                    selected_doctors.append(random.choice(doctors_by_spec[spec]))
            
            doctor_assignments = [
                {'doctor_id': doc['doctor_id'], 'notes': f"{doc['specialization']} care"}
                for doc in selected_doctors
            ]
            
            assign_doctors_to_patient_mariadb(cursor, patient_id, doctor_assignments)
            
            print(f"\n   📋 {patient_name} (MariaDB ID: {patient_id}):")
            for doc in selected_doctors:
                is_primary = "⭐ Primary" if doc == selected_doctors[0] else ""
                print(f"      → Dr. {doc['first_name']} {doc['last_name']} ({doc['specialization']}) {is_primary}")
        
        conn.commit()
        
        print("\n" + "="*70)
        print(f"✅ COMPLETED: {assignments_made} doctor-patient relationships created")
        print("="*70)
        
    finally:
        cursor.close()
        conn.close()
        driver.close()
    
    return True


def verify_assignments():
    """Verify the assignments in both databases"""
    print("\n" + "="*70)
    print("🔍 VERIFYING DOCTOR-PATIENT ASSIGNMENTS")
    print("="*70)
    
    # Verify MariaDB
    print("\n📊 MariaDB Patient_Doctor Table:")
    conn = get_mariadb_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.name as patient_name, 
               CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
               d.specialization,
               pd.is_primary_doctor
        FROM Patient_Doctor pd
        JOIN Patient p ON pd.patient_id = p.patient_id
        JOIN Doctor d ON pd.doctor_id = d.doctor_id
        ORDER BY p.patient_id, pd.is_primary_doctor DESC
    """)
    
    results = cursor.fetchall()
    for row in results:
        primary = "⭐" if row[3] else "  "
        print(f"   {primary} {row[0]} → Dr. {row[1]} ({row[2]})")
    
    cursor.close()
    conn.close()
    
    # Verify Neo4j
    print("\n📊 Neo4j TREATED_BY Relationships:")
    driver = get_neo4j_driver()
    
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Patient)-[r:TREATED_BY]->(d:Doctor)
            RETURN p.name as patient_name, 
                   p.synthea_id as patient_id,
                   d.name as doctor_name,
                   d.specialization as specialization,
                   r.is_primary as is_primary
            ORDER BY p.synthea_id, r.is_primary DESC
            LIMIT 50
        """)
        
        for record in result:
            primary = "⭐" if record['is_primary'] else "  "
            patient_name = record['patient_name'] or record['patient_id']
            print(f"   {primary} {patient_name} → {record['doctor_name']} ({record['specialization']})")
    
    driver.close()
    
    print("\n✅ Verification complete!")


if __name__ == "__main__":
    success = main()
    if success:
        verify_assignments()
