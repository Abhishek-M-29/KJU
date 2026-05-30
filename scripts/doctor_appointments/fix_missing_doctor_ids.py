"""Fix patients without doctor_id"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'), 
    auth=(os.getenv('AURA_USER'), os.getenv('AURA_PASSWORD'))
)

with driver.session() as session:
    # Check patients without doctor_id
    result = session.run('''
        MATCH (p:Patient)
        WHERE p.doctor_id IS NULL
        RETURN count(p) as count
    ''')
    missing = result.single()['count']
    print(f'Patients without doctor_id: {missing}')
    
    if missing > 0:
        # Fix: assign Internal Medicine doctor (id=5) to patients without doctor_id
        session.run('''
            MATCH (p:Patient)
            WHERE p.doctor_id IS NULL
            MATCH (d:Doctor {doctor_id: 5})
            SET p.doctor_id = d.doctor_id
            MERGE (p)-[:TREATED_BY]->(d)
        ''')
        print(f'Fixed {missing} patients - assigned to Dr. John Martinez (Internal Medicine)')
    
    # Verify all have doctor_id now
    result = session.run('''
        MATCH (p:Patient)
        WHERE p.doctor_id IS NOT NULL
        RETURN count(p) as count
    ''')
    print(f'Patients with doctor_id: {result.single()["count"]}')
    
    # Total patients
    result = session.run('MATCH (p:Patient) RETURN count(p) as count')
    print(f'Total patients: {result.single()["count"]}')
    
    # Verify coherence
    result = session.run('''
        MATCH (p:Patient)-[:TREATED_BY]->(d:Doctor)
        WHERE p.doctor_id = d.doctor_id
        RETURN count(p) as count
    ''')
    print(f'Coherent relationships (doctor_id matches TREATED_BY): {result.single()["count"]}')

driver.close()
print('\n✅ Done!')
