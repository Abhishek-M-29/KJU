"""
Verify the one-to-one doctor-patient relationship across both databases.
"""
from neo4j import GraphDatabase
import mariadb
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 60)
    print("FINAL VERIFICATION: ONE DOCTOR PER PATIENT")
    print("=" * 60)
    
    # Neo4j verification
    print("\n--- NEO4J VERIFICATION ---")
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'), 
        auth=(os.getenv('AURA_USER'), os.getenv('AURA_PASSWORD'))
    )
    
    with driver.session() as session:
        # Sample patient-doctor assignments
        result = session.run('''
            MATCH (p:Patient)-[:TREATED_BY]->(d:Doctor)
            WHERE p.doctor_id = d.doctor_id
            RETURN p.name as patient, p.doctor_id as doctor_id, 
                   d.name as doctor, d.specialization as spec
            LIMIT 10
        ''')
        print("\nSample patient-doctor assignments:")
        for r in result:
            print(f"  {r['patient']} [doctor_id={r['doctor_id']}] -> {r['doctor']} ({r['spec']})")
        
        # Count by doctor
        result = session.run('''
            MATCH (p:Patient)-[:TREATED_BY]->(d:Doctor)
            RETURN d.name as doctor, d.specialization as spec, count(p) as patients
            ORDER BY patients DESC
        ''')
        print("\nDoctor patient counts:")
        for r in result:
            print(f"  {r['doctor']} ({r['spec']}): {r['patients']} patients")
        
        # Total stats
        result = session.run('''
            MATCH (p:Patient)
            RETURN 
                count(p) as total_patients,
                count(p.doctor_id) as with_doctor_id
        ''')
        stats = result.single()
        print(f"\nTotal patients: {stats['total_patients']}")
        print(f"Patients with doctor_id: {stats['with_doctor_id']}")
        
    driver.close()
    
    # MariaDB verification
    print("\n--- MARIADB VERIFICATION ---")
    conn = mariadb.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.name, p.doctor_id, 
               CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
               d.specialization 
        FROM Patient p 
        LEFT JOIN Doctor d ON p.doctor_id = d.doctor_id
    ''')
    
    print("\nPatient-doctor assignments:")
    for row in cursor.fetchall():
        print(f"  {row[0]} [doctor_id={row[1]}] -> Dr. {row[2]} ({row[3]})")
    
    cursor.execute('SELECT COUNT(*) FROM Patient WHERE doctor_id IS NOT NULL')
    count = cursor.fetchone()[0]
    print(f"\nMariaDB patients with doctor_id: {count}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
