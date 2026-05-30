"""
Script to create appointments for all doctors with different patients
"""

import sys
sys.path.append('.')

import mariadb
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3305)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'hospitaldb')
}


def get_db_connection():
    """Get database connection"""
    return mariadb.connect(**DB_CONFIG)


def create_appointments_for_all_doctors():
    """Create appointments for each doctor with different patients"""
    print("\n" + "="*70)
    print("📅 CREATING APPOINTMENTS FOR ALL DOCTORS")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all doctors
        print("\n1️⃣ Fetching all doctors...")
        cursor.execute("SELECT * FROM Doctor ORDER BY doctor_id")
        doctors = cursor.fetchall()
        
        if not doctors:
            print("❌ No doctors found in database")
            return
        
        print(f"✅ Found {len(doctors)} doctors")
        
        # Get all patients
        print("\n2️⃣ Fetching all patients...")
        cursor.execute("SELECT * FROM Patient ORDER BY patient_id LIMIT 100")
        patients = cursor.fetchall()
        
        if not patients:
            print("❌ No patients found in database")
            return
        
        print(f"✅ Found {len(patients)} patients")
        
        # Create appointments for each doctor
        print("\n3️⃣ Creating appointments...")
        appointment_types = ["Regular", "Follow-up", "Emergency", "Consultation", "Check-up"]
        base_date = datetime.now()
        
        appointments_created = 0
        
        for i, doctor in enumerate(doctors):
            doctor_id = doctor["doctor_id"]
            doctor_name = f"Dr. {doctor['first_name']} {doctor['last_name']}"
            specialization = doctor["specialization"]
            
            print(f"\n   📋 {doctor_name} ({specialization}):")
            
            # Create 2-3 appointments per doctor with different patients
            num_appointments = min(3, len(patients))
            
            for j in range(num_appointments):
                # Cycle through patients
                patient_idx = (i * 3 + j) % len(patients)
                patient = patients[patient_idx]
                patient_id = patient["patient_id"]
                patient_name = patient['name']
                
                # Calculate appointment date (spread over next 2 weeks)
                days_ahead = (i * 3 + j) % 14 + 1
                appointment_date = (base_date + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                
                # Vary appointment times
                hours = [9, 10, 11, 14, 15, 16]
                hour = hours[(i + j) % len(hours)]
                appointment_time = f"{hour:02d}:00:00"
                
                # Select appointment type based on specialization
                if specialization == "Cardiology":
                    reason = "Cardiovascular health assessment"
                    appt_type = "Regular"
                elif specialization == "Endocrinology":
                    reason = "Diabetes management consultation"
                    appt_type = "Follow-up"
                elif specialization == "Internal Medicine":
                    reason = "General health check-up"
                    appt_type = "Check-up"
                elif specialization == "Pulmonology":
                    reason = "Respiratory function evaluation"
                    appt_type = "Regular"
                elif specialization == "Nephrology":
                    reason = "Kidney function assessment"
                    appt_type = "Consultation"
                else:
                    reason = f"{specialization} consultation"
                    appt_type = appointment_types[j % len(appointment_types)]
                
                try:
                    # Insert appointment
                    insert_query = """
                        INSERT INTO Appointment 
                        (patient_id, doctor_id, appointment_date, appointment_time, 
                         appointment_type, status, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        patient_id, doctor_id, appointment_date, appointment_time,
                        appt_type, "Scheduled", reason
                    ))
                    conn.commit()
                    
                    appt_id = cursor.lastrowid
                    print(f"      ✅ Appointment #{appt_id}: {patient_name} on {appointment_date} at {appointment_time}")
                    appointments_created += 1
                        
                except Exception as e:
                    print(f"      ❌ Error creating appointment: {e}")
                    conn.rollback()
        
        print("\n" + "="*70)
        print(f"✅ CREATED {appointments_created} APPOINTMENTS FOR {len(doctors)} DOCTORS")
        print("="*70)
        
    finally:
        cursor.close()
        conn.close()


def show_appointment_summary():
    """Show summary of appointments by doctor"""
    print("\n" + "="*70)
    print("📊 APPOINTMENT SUMMARY BY DOCTOR")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all doctors with appointment counts
        query = """
            SELECT 
                d.doctor_id,
                d.first_name,
                d.last_name,
                d.specialization,
                COUNT(a.appointment_id) as appointment_count
            FROM Doctor d
            LEFT JOIN Appointment a ON d.doctor_id = a.doctor_id
            GROUP BY d.doctor_id, d.first_name, d.last_name, d.specialization
            ORDER BY appointment_count DESC
        """
        cursor.execute(query)
        doctors = cursor.fetchall()
        
        for doctor in doctors:
            doctor_name = f"Dr. {doctor['first_name']} {doctor['last_name']}"
            specialization = doctor['specialization']
            count = doctor['appointment_count']
            
            print(f"\n{doctor_name} ({specialization}):")
            print(f"   📅 {count} appointments")
            
            # Get sample appointments for this doctor
            appt_query = """
                SELECT 
                    a.appointment_id,
                    a.appointment_date,
                    a.appointment_time,
                    a.status,
                    a.notes,
                    p.name as patient_name
                FROM Appointment a
                JOIN Patient p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s
                ORDER BY a.appointment_date, a.appointment_time
                LIMIT 3
            """
            cursor.execute(appt_query, (doctor['doctor_id'],))
            appointments = cursor.fetchall()
            
            for appt in appointments:
                patient_name = appt["patient_name"]
                date = appt["appointment_date"]
                time = appt.get("appointment_time", "N/A")
                status = appt["status"]
                print(f"      • {patient_name} - {date} {time} ({status})")
            
            if count > 3:
                print(f"      ... and {count - 3} more")
    
    finally:
        cursor.close()
        conn.close()


def main():
    """Main function"""
    try:
        create_appointments_for_all_doctors()
        show_appointment_summary()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

