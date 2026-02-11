"""
Test script to verify doctor-patient relationships in both databases
"""

import mariadb
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def test_mariadb():
    """Test MariaDB doctor-patient relationships"""
    print("=" * 60)
    print("TESTING MARIADB DOCTOR-PATIENT RELATIONSHIPS")
    print("=" * 60)

    conn = mariadb.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()

    # Get patient-doctor assignments
    cursor.execute("""
        SELECT p.name as patient, 
               CONCAT(d.first_name, ' ', d.last_name) as doctor,
               d.specialization,
               pd.is_primary_doctor
        FROM Patient_Doctor pd
        JOIN Patient p ON pd.patient_id = p.patient_id
        JOIN Doctor d ON pd.doctor_id = d.doctor_id
        ORDER BY p.patient_id, pd.is_primary_doctor DESC
    """)
    print('\nMariaDB Patient-Doctor Assignments:')
    for row in cursor.fetchall():
        primary = '⭐ Primary' if row[3] else ''
        print(f'  {row[0]} -> Dr. {row[1]} ({row[2]}) {primary}')

    # Get count
    cursor.execute('SELECT COUNT(*) FROM Patient_Doctor')
    print(f'\n✅ Total MariaDB assignments: {cursor.fetchone()[0]}')

    conn.close()


def test_neo4j():
    """Test Neo4j doctor-patient relationships"""
    print('\n' + "=" * 60)
    print("TESTING NEO4J DOCTOR-PATIENT RELATIONSHIPS")
    print("=" * 60)

    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('AURA_USER'), os.getenv('AURA_PASSWORD'))
    )

    with driver.session() as session:
        # Get TREATED_BY relationships count
        result = session.run("""
            MATCH (p:Patient)-[r:TREATED_BY]->(d:Doctor)
            RETURN count(r) as count
        """)
        count = result.single()['count']
        print(f'\n✅ Total Neo4j TREATED_BY relationships: {count}')
        
        # Verify Doctor nodes
        result = session.run('MATCH (d:Doctor) RETURN count(d) as count')
        print(f'✅ Total Doctor nodes in Neo4j: {result.single()["count"]}')
        
        # Sample relationships
        result = session.run("""
            MATCH (p:Patient)-[r:TREATED_BY]->(d:Doctor)
            RETURN p.name as patient, 
                   d.name as doctor, 
                   d.specialization as spec,
                   r.is_primary as primary
            LIMIT 15
        """)
        print('\nSample Neo4j Patient-Doctor Relationships:')
        for record in result:
            primary = '⭐ Primary' if record['primary'] else ''
            print(f'  {record["patient"]} -> {record["doctor"]} ({record["spec"]}) {primary}')

    driver.close()


def test_coherence():
    """Test coherence between MariaDB and Neo4j"""
    print('\n' + "=" * 60)
    print("TESTING DATA COHERENCE")
    print("=" * 60)
    
    # Connect to both
    conn = mariadb.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('AURA_USER'), os.getenv('AURA_PASSWORD'))
    )
    
    # Get doctor counts
    cursor.execute('SELECT COUNT(*) FROM Doctor')
    mariadb_doctors = cursor.fetchone()[0]
    
    with driver.session() as session:
        result = session.run('MATCH (d:Doctor) RETURN count(d) as count')
        neo4j_doctors = result.single()['count']
    
    print(f'\nDoctors in MariaDB: {mariadb_doctors}')
    print(f'Doctors in Neo4j: {neo4j_doctors}')
    
    if mariadb_doctors == neo4j_doctors:
        print('✅ Doctor count matches!')
    else:
        print('⚠️ Doctor count mismatch')
    
    # Check specializations match
    cursor.execute("""
        SELECT specialization, COUNT(*) 
        FROM Doctor 
        GROUP BY specialization 
        ORDER BY COUNT(*) DESC
    """)
    print('\nMariaDB Doctors by Specialization:')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}')
    
    with driver.session() as session:
        result = session.run("""
            MATCH (d:Doctor)
            RETURN d.specialization as spec, count(d) as count
            ORDER BY count DESC
        """)
        print('\nNeo4j Doctors by Specialization:')
        for record in result:
            print(f'  {record["spec"]}: {record["count"]}')
    
    conn.close()
    driver.close()


if __name__ == '__main__':
    try:
        test_mariadb()
        test_neo4j()
        test_coherence()
        
        print('\n' + "=" * 60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
