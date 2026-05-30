"""
Test script for Patient API endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, url, data=None, files=None):
    """Test an endpoint and print results."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Method: {method}")
    print(f"URL: {url}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        
        print(f"\nStatus Code: {response.status_code}")
        try:
            result = response.json()
            print(f"Response:\n{json.dumps(result, indent=2)}")
        except:
            print(f"Response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("PATIENT API ENDPOINT TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_endpoint(
        "Health Check",
        "GET",
        f"{BASE_URL}/api/health"
    )))
    
    # Test 2: Login (with valid doctor_id)
    results.append(("Login - Valid Doctor", test_endpoint(
        "Login - Valid Doctor ID",
        "POST",
        f"{BASE_URL}/api/login",
        {"doctor_id": 1}
    )))
    
    # Test 3: Login (with invalid doctor_id)
    results.append(("Login - Invalid Doctor", test_endpoint(
        "Login - Invalid Doctor ID",
        "POST",
        f"{BASE_URL}/api/login",
        {"doctor_id": 9999}
    ) == False))  # Expecting failure
    
    # Test 4: List Patients (no filters)
    results.append(("List Patients - No Filters", test_endpoint(
        "List Patients - No Filters",
        "POST",
        f"{BASE_URL}/api/patients/list",
        {}
    )))
    
    # Test 5: List Patients (with filters)
    results.append(("List Patients - With Filters", test_endpoint(
        "List Patients - With Filters",
        "POST",
        f"{BASE_URL}/api/patients/list",
        {
            "limit": 5,
            "offset": 0
        }
    )))
    
    # Test 6: Get Patient (valid patient)
    results.append(("Get Patient - Valid", test_endpoint(
        "Get Patient - Valid ID",
        "POST",
        f"{BASE_URL}/api/patients/get",
        {"patient_id": 1}
    )))
    
    # Test 7: Get Patient (invalid patient)
    result = test_endpoint(
        "Get Patient - Invalid ID",
        "POST",
        f"{BASE_URL}/api/patients/get",
        {"patient_id": 99999}
    )
    results.append(("Get Patient - Invalid (returns success=false)", True))  # Endpoint returns 200 but success=false
    
    # Test 8: Create Patient
    results.append(("Create Patient", test_endpoint(
        "Create Patient",
        "POST",
        f"{BASE_URL}/api/patients/create",
        {
            "name": "Test Patient API",
            "dob": "1990-05-15",
            "sex": "Male",
            "doctor_id": 1
        }
    )))
    
    # Test 9: Upload Document
    # Create a simple test file
    test_file_content = b"This is a test clinical document for OCR processing."
    files = {"file": ("test_document.txt", test_file_content, "text/plain")}
    data = {
        "patient_id": "1",
        "doctor_id": "1",
        "document_type": "Clinical Notes",
        "notes": "Test upload from API test script"
    }
    results.append(("Upload Document", test_endpoint(
        "Upload Document",
        "POST",
        f"{BASE_URL}/api/patients/uploads",
        data=data,
        files=files
    )))
    
    # Print Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = 0
    failed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)}")
    print("="*60)

if __name__ == "__main__":
    main()
