import mariadb
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mariadb.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT'))
    )
    cursor = conn.cursor()

    # 1. Get and Drop Foreign Keys referencing Patient
    print("Finding constraints referencing Patient table...")
    cursor.execute("""
        SELECT CONSTRAINT_NAME, TABLE_NAME 
        FROM information_schema.KEY_COLUMN_USAGE 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND REFERENCED_TABLE_NAME = 'Patient'
    """)
    constraints = cursor.fetchall()
    
    for const_name, table_name in constraints:
        print(f"Dropping constraint {const_name} on {table_name}")
        try:
            cursor.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {const_name}")
            print(f"Successfully dropped {const_name}")
        except mariadb.Error as e:
            print(f"Error dropping constraint {const_name}: {e}")

    # 2. Migrate Patient_Documents IDs
    print('Migrating Document IDs...')
    cursor.execute('SELECT persona_id, patient_data_id FROM Patient_Data WHERE is_persona=1 AND persona_id IS NOT NULL')
    mapping = cursor.fetchall()

    total_updated = 0
    for persona_id, new_id in mapping:
        # Check if documents exist for this old ID
        cursor.execute('SELECT COUNT(*) FROM Patient_Documents WHERE patient_id = %s', (persona_id,))
        doc_count = cursor.fetchall()[0][0]
        
        if doc_count > 0:
            print(f"Migrating {doc_count} documents for Persona {persona_id} -> Patient_Data ID {new_id}")
            cursor.execute('UPDATE Patient_Documents SET patient_id = %s WHERE patient_id = %s', (new_id, persona_id))
            total_updated += cursor.rowcount
            
        # Check if doctor assignments exist for this old ID
        cursor.execute('SELECT COUNT(*) FROM Patient_Doctor WHERE patient_id = %s', (persona_id,))
        doc_relation_count = cursor.fetchall()[0][0]
        
        if doc_relation_count > 0:
            print(f"Migrating {doc_relation_count} doctor assignments for Persona {persona_id} -> Patient_Data ID {new_id}")
            cursor.execute('UPDATE Patient_Doctor SET patient_id = %s WHERE patient_id = %s', (new_id, persona_id))

        # Migrate other tables
        tables_to_migrate = ['Medical_History', 'Appointment', 'Medication', 'Lab_Report', 'Report', 'Chat_History']
        for table in tables_to_migrate:
            cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE patient_id = %s', (persona_id,))
            count = cursor.fetchall()[0][0]
            if count > 0:
                print(f"Migrating {count} {table} records for Persona {persona_id} -> Patient_Data ID {new_id}")
                cursor.execute(f'UPDATE {table} SET patient_id = %s WHERE patient_id = %s', (new_id, persona_id))


    print(f'Migrated {total_updated} document records total.')

    conn.commit()
    conn.close()
    print("Migration complete.")

except mariadb.Error as e:
    print(f"Database error: {e}")
