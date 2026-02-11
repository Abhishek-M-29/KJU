"""
Test script for the new Doctor and Appointment MCP tools
"""

import sys
sys.path.append('.')

from connect_to_database import (
    get_doctors_mariadb,
    get_doctor_details_mariadb,
    get_appointments_by_doctor_mariadb,
    get_appointments_by_patient_mariadb,
    create_appointment_mariadb,
    get_database_stats
)


def test_doctor_tools():
    """Test doctor-related MCP tools"""
    print("\n" + "="*60)
    print("🧪 Testing Doctor MCP Tools")
    print("="*60)
    
    # Test 1: Get all doctors
    print("\n1️⃣ Testing GetDoctors_MariaDB...")
    doctors = get_doctors_mariadb(limit=5)
    if doctors.get("results"):
        print(f"✅ Found {doctors['count']} doctors")
        for doc in doctors["results"][:3]:
            print(f"   - Dr. {doc['first_name']} {doc['last_name']} ({doc['specialization']})")
    else:
        print("❌ No doctors found")
    
    # Test 2: Get doctors by specialization
    print("\n2️⃣ Testing GetDoctors_MariaDB with specialization filter...")
    cardio_doctors = get_doctors_mariadb(specialization="Cardiology")
    if cardio_doctors.get("results"):
        print(f"✅ Found {cardio_doctors['count']} cardiologists")
        for doc in cardio_doctors["results"]:
            print(f"   - Dr. {doc['first_name']} {doc['last_name']}")
    else:
        print("ℹ️  No cardiologists found")
    
    # Test 3: Get doctor details
    if doctors.get("results") and len(doctors["results"]) > 0:
        doctor_id = doctors["results"][0]["doctor_id"]
        print(f"\n3️⃣ Testing GetDoctorDetails_MariaDB for doctor_id={doctor_id}...")
        details = get_doctor_details_mariadb(doctor_id)
        if details.get("basic_info"):
            doc = details["basic_info"]
            print(f"✅ Doctor: Dr. {doc['first_name']} {doc['last_name']}")
            print(f"   Specialization: {doc['specialization']}")
            print(f"   Experience: {doc['years_of_experience']} years")
            print(f"   Assigned Patients: {len(details['patients'])}")
            print(f"   Appointments: {len(details['appointments'])}")
        else:
            print("❌ Could not get doctor details")


def test_appointment_tools():
    """Test appointment-related MCP tools"""
    print("\n" + "="*60)
    print("🧪 Testing Appointment MCP Tools")
    print("="*60)
    
    # Get a doctor and patient first
    doctors = get_doctors_mariadb(limit=1)
    if not doctors.get("results"):
        print("❌ No doctors found - skipping appointment tests")
        return
    
    doctor_id = doctors["results"][0]["doctor_id"]
    doctor_name = f"Dr. {doctors['results'][0]['first_name']} {doctors['results'][0]['last_name']}"
    
    # Test 1: Get appointments by doctor
    print(f"\n1️⃣ Testing GetAppointmentsByDoctor_MariaDB for {doctor_name}...")
    appointments = get_appointments_by_doctor_mariadb(doctor_id, limit=5)
    if appointments.get("results"):
        print(f"✅ Found {appointments['count']} appointments")
        for appt in appointments["results"][:3]:
            print(f"   - Patient: {appt['patient_name']}, Date: {appt['appointment_date']}, Status: {appt['status']}")
    else:
        print("ℹ️  No appointments found")
    
    # Test 2: Get appointments by patient
    if appointments.get("results") and len(appointments["results"]) > 0:
        patient_id = appointments["results"][0]["patient_id"]
        print(f"\n2️⃣ Testing GetAppointmentsByPatient_MariaDB for patient_id={patient_id}...")
        patient_appts = get_appointments_by_patient_mariadb(patient_id)
        if patient_appts.get("results"):
            print(f"✅ Found {patient_appts['count']} appointments for this patient")
            for appt in patient_appts["results"][:3]:
                doc_name = f"Dr. {appt['doctor_first_name']} {appt['doctor_last_name']}"
                print(f"   - {doc_name} ({appt['doctor_specialization']}), Date: {appt['appointment_date']}")
        else:
            print("ℹ️  No appointments found")
    
    # Test 3: Create new appointment
    print(f"\n3️⃣ Testing CreateAppointment_MariaDB...")
    try:
        # Get any patient
        from connect_to_database import get_patients_mariadb
        patients = get_patients_mariadb(limit=1)
        if patients.get("results"):
            patient_id = patients["results"][0]["patient_id"]
            result = create_appointment_mariadb(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date="2026-03-15",
                appointment_time="14:30:00",
                appointment_type="Regular",
                status="Scheduled",
                notes="Test appointment created by test script"
            )
            if result.get("appointment"):
                appt = result["appointment"]
                print(f"✅ Created appointment_id={appt['appointment_id']}")
                print(f"   Patient: {appt['patient_name']}")
                print(f"   Doctor: Dr. {appt['doctor_first_name']} {appt['doctor_last_name']}")
                print(f"   Date: {appt['appointment_date']} at {appt['appointment_time']}")
            else:
                print(f"⚠️  Appointment creation result: {result}")
    except Exception as e:
        print(f"❌ Error creating appointment: {e}")


def test_database_stats():
    """Test database statistics"""
    print("\n" + "="*60)
    print("🧪 Testing Database Statistics")
    print("="*60)
    
    print("\n📊 Getting database statistics...")
    stats = get_database_stats()
    
    if stats.get("mariadb"):
        print("\n📈 MariaDB Statistics:")
        for table, count in sorted(stats["mariadb"].items()):
            print(f"   {table:25s}: {count:5d} records")
    
    if stats.get("neo4j", {}).get("nodes"):
        print("\n📈 Neo4j Node Statistics:")
        for label, count in sorted(stats["neo4j"]["nodes"].items(), key=lambda x: x[1], reverse=True):
            print(f"   {label:25s}: {count:5d} nodes")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🏥 TESTING NEW DOCTOR AND APPOINTMENT MCP TOOLS")
    print("="*70)
    
    try:
        test_doctor_tools()
        test_appointment_tools()
        test_database_stats()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
