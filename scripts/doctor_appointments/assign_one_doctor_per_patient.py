"""
Script to assign ONE doctor to each patient in both MariaDB and Neo4j
One doctor can have many patients, but each patient has exactly one doctor.
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
    return mariadb.connect(**DB_CONFIG)


def get_neo4j_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def add_doctor_id_column_to_patient(cursor):
    """Add doctor_id column to Patient table if not exists"""
    print("\n1️⃣ Checking Patient table for doctor_id column...")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'Patient' 
        AND COLUMN_NAME = 'doctor_id'
    """, (DB_CONFIG['database'],))
    
    if cursor.fetchone()[0] == 0:
        print("   Adding doctor_id column to Patient table...")
        cursor.execute("""
            ALTER TABLE Patient 
            ADD COLUMN doctor_id INT,
            ADD CONSTRAINT fk_patient_doctor 
            FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id) ON DELETE SET NULL
        """)
        print("   ✅ Added doctor_id column to Patient table")
    else:
        print("   ✅ doctor_id column already exists")


def get_doctors(cursor):
    """Get all doctors from MariaDB"""
    cursor.execute("""
        SELECT doctor_id, first_name, last_name, specialization 
        FROM Doctor 
        ORDER BY doctor_id
    """)
    return [{'doctor_id': d[0], 'first_name': d[1], 'last_name': d[2], 'specialization': d[3]} 
            for d in cursor.fetchall()]


def get_patients_mariadb(cursor):
    """Get all patients from MariaDB"""
    cursor.execute("SELECT patient_id, name FROM Patient")
    return [{'patient_id': p[0], 'name': p[1]} for p in cursor.fetchall()]


def get_patients_neo4j(driver):
    """Get all patients from Neo4j"""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Patient)
            OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
            WITH p, collect(c.description) as conditions
            RETURN p.synthea_id as synthea_id, 
                   p.name as name,
                   p.first_name as first_name,
                   p.last_name as last_name,
                   conditions
            ORDER BY p.synthea_id
        """)
        return [dict(record) for record in result]


def select_doctor_for_patient(doctors, conditions):
    """Select ONE doctor based on patient conditions"""
    
    # Mapping of conditions to best specializations
    condition_to_specialization = {
        'diabetes': 'Endocrinology',
        'hypertension': 'Cardiology',
        'heart': 'Cardiology',
        'cardiovascular': 'Cardiology',
        'kidney': 'Nephrology',
        'renal': 'Nephrology',
        'lung': 'Pulmonology',
        'respiratory': 'Pulmonology',
        'asthma': 'Pulmonology',
        'copd': 'Pulmonology',
        'arthritis': 'Rheumatology',
        'joint': 'Orthopedics',
        'bone': 'Orthopedics',
        'skin': 'Dermatology',
        'depression': 'Psychiatry',
        'anxiety': 'Psychiatry',
        'mental': 'Psychiatry',
        'stomach': 'Gastroenterology',
        'digestive': 'Gastroenterology',
        'liver': 'Gastroenterology',
        'thyroid': 'Endocrinology',
        'brain': 'Neurology',
        'nerve': 'Neurology',
        'stroke': 'Neurology',
    }
    
    # Find best matching specialization
    best_spec = None
    for condition in (conditions or []):
        if condition:
            condition_lower = condition.lower()
            for keyword, spec in condition_to_specialization.items():
                if keyword in condition_lower:
                    best_spec = spec
                    break
        if best_spec:
            break
    
    # If no specific match, use Internal Medicine or General Practice
    if not best_spec:
        best_spec = random.choice(['Internal Medicine', 'General Practice'])
    
    # Find a doctor with that specialization
    matching_doctors = [d for d in doctors if d['specialization'] == best_spec]
    
    if matching_doctors:
        return random.choice(matching_doctors)
    
    # Fallback to any doctor
    return random.choice(doctors)


def create_doctor_nodes_neo4j(driver, doctors):
    """Create/update Doctor nodes in Neo4j"""
    print("\n2️⃣ Creating Doctor nodes in Neo4j...")
    
    with driver.session() as session:
        # Clear old TREATED_BY relationships
        session.run("MATCH ()-[r:TREATED_BY]->() DELETE r")
        
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
    
    print(f"   ✅ Created/Updated {len(doctors)} Doctor nodes")


def assign_doctor_to_patient_neo4j(driver, patient_synthea_id, doctor_id):
    """Set doctor_id on patient node and create TREATED_BY relationship"""
    with driver.session() as session:
        session.run("""
            MATCH (p:Patient {synthea_id: $synthea_id})
            MATCH (d:Doctor {doctor_id: $doctor_id})
            SET p.doctor_id = $doctor_id
            MERGE (p)-[:TREATED_BY]->(d)
        """, {
            'synthea_id': patient_synthea_id,
            'doctor_id': doctor_id
        })


def assign_doctor_to_patient_mariadb(cursor, patient_id, doctor_id):
    """Set doctor_id on patient record"""
    cursor.execute("""
        UPDATE Patient SET doctor_id = %s WHERE patient_id = %s
    """, (doctor_id, patient_id))


def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("🏥 ASSIGNING ONE DOCTOR PER PATIENT")
    print("    (One doctor can have many patients)")
    print("=" * 70)
    
    # Connect to databases
    print("\n📡 Connecting to databases...")
    conn = get_mariadb_connection()
    cursor = conn.cursor()
    driver = get_neo4j_driver()
    driver.verify_connectivity()
    print("   ✅ Connected to MariaDB and Neo4j")
    
    try:
        # Add doctor_id column to Patient table
        add_doctor_id_column_to_patient(cursor)
        conn.commit()
        
        # Get all doctors
        doctors = get_doctors(cursor)
        print(f"\n3️⃣ Loaded {len(doctors)} doctors")
        
        # Create doctor nodes in Neo4j
        create_doctor_nodes_neo4j(driver, doctors)
        
        # Get Neo4j patients and assign doctors
        print("\n4️⃣ Assigning doctors to Neo4j patients...")
        neo4j_patients = get_patients_neo4j(driver)
        print(f"   Found {len(neo4j_patients)} patients in Neo4j")
        
        doctor_patient_count = {}  # Track how many patients each doctor has
        
        for patient in neo4j_patients:
            synthea_id = patient.get('synthea_id')
            if not synthea_id:
                continue
            
            # Select ONE doctor for this patient
            doctor = select_doctor_for_patient(doctors, patient.get('conditions', []))
            
            # Assign in Neo4j
            assign_doctor_to_patient_neo4j(driver, synthea_id, doctor['doctor_id'])
            
            # Track count
            doc_id = doctor['doctor_id']
            doctor_patient_count[doc_id] = doctor_patient_count.get(doc_id, 0) + 1
        
        print(f"   ✅ Assigned doctors to {len(neo4j_patients)} Neo4j patients")
        
        # Get MariaDB patients and assign doctors
        print("\n5️⃣ Assigning doctors to MariaDB patients...")
        mariadb_patients = get_patients_mariadb(cursor)
        print(f"   Found {len(mariadb_patients)} patients in MariaDB")
        
        for patient in mariadb_patients:
            # Pick a doctor (General Practice for MariaDB patients without condition info)
            gp_doctors = [d for d in doctors if d['specialization'] == 'General Practice']
            doctor = random.choice(gp_doctors) if gp_doctors else random.choice(doctors)
            
            assign_doctor_to_patient_mariadb(cursor, patient['patient_id'], doctor['doctor_id'])
            
            doc_id = doctor['doctor_id']
            doctor_patient_count[doc_id] = doctor_patient_count.get(doc_id, 0) + 1
        
        conn.commit()
        print(f"   ✅ Assigned doctors to {len(mariadb_patients)} MariaDB patients")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 DOCTOR PATIENT DISTRIBUTION")
        print("=" * 70)
        
        for doc in sorted(doctors, key=lambda d: doctor_patient_count.get(d['doctor_id'], 0), reverse=True):
            count = doctor_patient_count.get(doc['doctor_id'], 0)
            if count > 0:
                print(f"   Dr. {doc['first_name']} {doc['last_name']} ({doc['specialization']}): {count} patients")
        
        print("\n" + "=" * 70)
        print("✅ COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
    finally:
        cursor.close()
        conn.close()
        driver.close()


def verify():
    """Verify the assignments"""
    print("\n" + "=" * 70)
    print("🔍 VERIFYING ONE-TO-ONE PATIENT-DOCTOR RELATIONSHIP")
    print("=" * 70)
    
    conn = get_mariadb_connection()
    cursor = conn.cursor()
    driver = get_neo4j_driver()
    
    try:
        # Check MariaDB
        print("\n📊 MariaDB Patients with doctor_id:")
        cursor.execute("""
            SELECT p.patient_id, p.name, p.doctor_id, 
                   CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                   d.specialization
            FROM Patient p
            LEFT JOIN Doctor d ON p.doctor_id = d.doctor_id
        """)
        for row in cursor.fetchall():
            print(f"   Patient {row[0]}: {row[1]} -> Dr. {row[3]} ({row[4]}) [doctor_id={row[2]}]")
        
        # Check Neo4j
        print("\n📊 Neo4j Patients with doctor_id (sample):")
        with driver.session() as session:
            result = session.run("""
                MATCH (p:Patient)
                WHERE p.doctor_id IS NOT NULL
                OPTIONAL MATCH (p)-[:TREATED_BY]->(d:Doctor)
                RETURN p.synthea_id as patient_id, 
                       p.name as patient_name,
                       p.doctor_id as doctor_id,
                       d.name as doctor_name,
                       d.specialization as spec
                LIMIT 20
            """)
            for record in result:
                print(f"   {record['patient_name']} -> {record['doctor_name']} ({record['spec']}) [doctor_id={record['doctor_id']}]")
            
            # Count patients with doctor_id
            result = session.run("""
                MATCH (p:Patient)
                WHERE p.doctor_id IS NOT NULL
                RETURN count(p) as count
            """)
            count = result.single()['count']
            print(f"\n   ✅ Total Neo4j patients with doctor_id: {count}")
            
            # Verify coherence - check that doctor_id matches TREATED_BY relationship
            result = session.run("""
                MATCH (p:Patient)-[:TREATED_BY]->(d:Doctor)
                WHERE p.doctor_id = d.doctor_id
                RETURN count(p) as matching
            """)
            matching = result.single()['matching']
            print(f"   ✅ Patients with matching doctor_id and TREATED_BY: {matching}")
        
        print("\n✅ Verification complete!")
        
    finally:
        cursor.close()
        conn.close()
        driver.close()


if __name__ == "__main__":
    main()
    verify()
