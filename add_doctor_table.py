"""
Script to add Doctor table and update Appointment table in MariaDB
This creates the Doctor table with specializations and links doctors to patients through appointments.
"""

import mariadb
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))


def execute_query(cursor, query, description=""):
    """Execute a query and handle errors"""
    try:
        cursor.execute(query)
        if description:
            print(f"✅ {description}")
        return True
    except mariadb.Error as e:
        print(f"❌ Error {description}: {e}")
        return False


def create_doctor_table(cursor):
    """Create the Doctor table with specializations"""
    print("\n📋 Creating Doctor table...")
    
    # Drop existing table if it exists
    execute_query(cursor, "DROP TABLE IF EXISTS Doctor", "Dropped existing Doctor table")
    
    # Create Doctor table
    create_table_query = """
    CREATE TABLE Doctor (
        doctor_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        specialization VARCHAR(100) NOT NULL,
        license_number VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(150),
        phone VARCHAR(20),
        years_of_experience INT DEFAULT 0,
        is_available TINYINT DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_specialization (specialization),
        INDEX idx_name (last_name, first_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    execute_query(cursor, create_table_query, "Created Doctor table")


def create_patient_doctor_table(cursor):
    """Create a junction table for patient-doctor relationships"""
    print("\n📋 Creating Patient_Doctor table...")
    
    execute_query(cursor, "DROP TABLE IF EXISTS Patient_Doctor", "Dropped existing Patient_Doctor table")
    
    create_table_query = """
    CREATE TABLE Patient_Doctor (
        patient_doctor_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT NOT NULL,
        doctor_id INT NOT NULL,
        assigned_date DATE DEFAULT CURRENT_DATE,
        is_primary_doctor TINYINT DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id) ON DELETE CASCADE,
        UNIQUE KEY unique_patient_doctor (patient_id, doctor_id),
        INDEX idx_patient (patient_id),
        INDEX idx_doctor (doctor_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    execute_query(cursor, create_table_query, "Created Patient_Doctor junction table")


def update_appointment_table(cursor):
    """Update Appointment table to include doctor_id foreign key"""
    print("\n📋 Updating Appointment table...")
    
    # Check if doctor_id column already exists
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'Appointment' 
        AND COLUMN_NAME = 'doctor_id'
    """, (DB_NAME,))
    
    result = cursor.fetchone()
    if result[0] > 0:
        print("⚠️  doctor_id column already exists in Appointment table")
    else:
        # Add doctor_id column
        execute_query(cursor, 
            "ALTER TABLE Appointment ADD COLUMN doctor_id INT AFTER appointment_id",
            "Added doctor_id column to Appointment table")
        
        # Add foreign key constraint
        execute_query(cursor,
            """ALTER TABLE Appointment 
               ADD CONSTRAINT fk_appointment_doctor 
               FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id) ON DELETE SET NULL""",
            "Added foreign key constraint for doctor_id")
        
        # Add index
        execute_query(cursor,
            "ALTER TABLE Appointment ADD INDEX idx_doctor (doctor_id)",
            "Added index on doctor_id")


def populate_doctors(cursor):
    """Populate the Doctor table with sample doctors"""
    print("\n👨‍⚕️ Populating Doctor table with sample data...")
    
    specializations = [
        "Cardiology", "Neurology", "Pediatrics", "Orthopedics", 
        "Dermatology", "Oncology", "Gastroenterology", "Psychiatry",
        "Endocrinology", "Pulmonology", "Nephrology", "Rheumatology",
        "General Practice", "Emergency Medicine", "Internal Medicine"
    ]
    
    first_names = [
        "John", "Sarah", "Michael", "Emily", "David", "Jessica", 
        "Robert", "Jennifer", "William", "Amanda", "James", "Lisa",
        "Daniel", "Patricia", "Christopher", "Linda", "Matthew", "Susan"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
        "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson"
    ]
    
    doctors_data = []
    used_licenses = set()
    
    # Create 30 doctors
    for i in range(30):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        specialization = random.choice(specializations)
        
        # Generate unique license number
        license_num = f"MD{random.randint(100000, 999999)}"
        while license_num in used_licenses:
            license_num = f"MD{random.randint(100000, 999999)}"
        used_licenses.add(license_num)
        
        email = f"{first_name.lower()}.{last_name.lower()}@hospital.com"
        phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        years = random.randint(2, 35)
        is_available = 1 if random.random() > 0.1 else 0  # 90% available
        
        doctors_data.append((first_name, last_name, specialization, license_num, 
                           email, phone, years, is_available))
    
    # Insert doctors
    insert_query = """
        INSERT INTO Doctor (first_name, last_name, specialization, license_number, 
                          email, phone, years_of_experience, is_available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    try:
        cursor.executemany(insert_query, doctors_data)
        print(f"✅ Inserted {len(doctors_data)} doctors")
    except mariadb.Error as e:
        print(f"❌ Error inserting doctors: {e}")


def assign_doctors_to_patients(cursor):
    """Assign doctors to existing patients"""
    print("\n🔗 Assigning doctors to patients...")
    
    # Get all patients
    cursor.execute("SELECT patient_id FROM Patient")
    patients = [row[0] for row in cursor.fetchall()]
    
    # Get all doctors
    cursor.execute("SELECT doctor_id, specialization FROM Doctor")
    doctors = cursor.fetchall()
    
    if not patients or not doctors:
        print("⚠️  No patients or doctors found")
        return
    
    assignments = []
    for patient_id in patients:
        # Assign 1-3 doctors to each patient
        num_doctors = random.randint(1, 3)
        selected_doctors = random.sample(doctors, min(num_doctors, len(doctors)))
        
        for idx, (doctor_id, specialization) in enumerate(selected_doctors):
            is_primary = 1 if idx == 0 else 0  # First doctor is primary
            assignments.append((patient_id, doctor_id, is_primary))
    
    # Insert assignments
    insert_query = """
        INSERT INTO Patient_Doctor (patient_id, doctor_id, is_primary_doctor)
        VALUES (?, ?, ?)
    """
    
    try:
        cursor.executemany(insert_query, assignments)
        print(f"✅ Created {len(assignments)} patient-doctor assignments")
    except mariadb.Error as e:
        print(f"❌ Error assigning doctors to patients: {e}")


def update_existing_appointments(cursor):
    """Update existing appointments to link them with doctors"""
    print("\n📅 Updating existing appointments with doctor assignments...")
    
    # Get all appointments
    cursor.execute("SELECT appointment_id, patient_id FROM Appointment WHERE doctor_id IS NULL")
    appointments = cursor.fetchall()
    
    if not appointments:
        print("ℹ️  No appointments to update")
        return
    
    # Get patient-doctor relationships
    cursor.execute("""
        SELECT pd.patient_id, pd.doctor_id, d.specialization
        FROM Patient_Doctor pd
        JOIN Doctor d ON pd.doctor_id = d.doctor_id
        WHERE pd.is_primary_doctor = 1
    """)
    primary_doctors = {row[0]: row[1] for row in cursor.fetchall()}
    
    updates = []
    for appointment_id, patient_id in appointments:
        # Assign primary doctor if exists, otherwise random available doctor
        if patient_id in primary_doctors:
            doctor_id = primary_doctors[patient_id]
        else:
            cursor.execute("SELECT doctor_id FROM Doctor WHERE is_available = 1 ORDER BY RAND() LIMIT 1")
            result = cursor.fetchone()
            doctor_id = result[0] if result else None
        
        if doctor_id:
            updates.append((doctor_id, appointment_id))
    
    # Update appointments
    if updates:
        update_query = "UPDATE Appointment SET doctor_id = ? WHERE appointment_id = ?"
        try:
            cursor.executemany(update_query, updates)
            print(f"✅ Updated {len(updates)} appointments with doctor assignments")
        except mariadb.Error as e:
            print(f"❌ Error updating appointments: {e}")


def main():
    """Main function to run all migrations"""
    print("=" * 60)
    print("🏥 MariaDB Doctor Table Migration")
    print("=" * 60)
    
    conn = None
    try:
        # Connect to database
        print(f"\n🔌 Connecting to MariaDB at {DB_HOST}:{DB_PORT}...")
        conn = mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        print("✅ Connected successfully")
        
        # Create tables
        create_doctor_table(cursor)
        create_patient_doctor_table(cursor)
        update_appointment_table(cursor)
        
        # Populate with data
        populate_doctors(cursor)
        assign_doctors_to_patients(cursor)
        update_existing_appointments(cursor)
        
        # Commit all changes
        conn.commit()
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        
        # Display summary
        cursor.execute("SELECT COUNT(*) FROM Doctor")
        doctor_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Patient_Doctor")
        assignment_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Appointment WHERE doctor_id IS NOT NULL")
        appointment_count = cursor.fetchone()[0]
        
        print(f"\n📊 Summary:")
        print(f"   - Doctors created: {doctor_count}")
        print(f"   - Patient-Doctor assignments: {assignment_count}")
        print(f"   - Appointments with doctors: {appointment_count}")
        
        # Show sample doctors by specialization
        cursor.execute("""
            SELECT specialization, COUNT(*) as count 
            FROM Doctor 
            GROUP BY specialization 
            ORDER BY count DESC
        """)
        print(f"\n👨‍⚕️ Doctors by Specialization:")
        for spec, count in cursor.fetchall():
            print(f"   - {spec}: {count}")
        
    except mariadb.Error as e:
        print(f"\n❌ Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("\n🔌 Database connection closed")


if __name__ == "__main__":
    main()
