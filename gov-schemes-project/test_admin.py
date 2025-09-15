#!/usr/bin/env python3
"""
Test script for admin functionality.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_registration():
    """Test admin registration."""
    print("Testing admin registration...")
    
    data = {
        "username": "testadmin",
        "email": "admin@test.com",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "role": "admin"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/admin/register", json=data)
    print(f"Registration response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Admin registration successful!")
        return response.json()
    else:
        print(f"❌ Registration failed: {response.text}")
        return None

def test_admin_login():
    """Test admin login."""
    print("\nTesting admin login...")
    
    data = {
        "username": "testadmin",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/admin/login", json=data)
    print(f"Login response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Admin login successful!")
        return result["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_scheme_management(token):
    """Test scheme management operations."""
    print("\nTesting scheme management...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test listing schemes
    print("Testing list schemes...")
    response = requests.get(f"{BASE_URL}/api/v1/admin/schemes", headers=headers)
    print(f"List schemes response: {response.status_code}")
    if response.status_code == 200:
        schemes = response.json()
        print(f"✅ Found {schemes['total']} schemes")
    else:
        print(f"❌ List schemes failed: {response.text}")
        return
    
    # Test adding a new scheme
    print("\nTesting add scheme...")
    scheme_data = {
        "name": "Test Scheme",
        "description": "A test scheme for demonstration",
        "state": "Test State",
        "disability_type": "visual_impairment",
        "support_type": "educational",
        "apply_link": "https://example.com/apply",
        "eligibility": "Test eligibility criteria",
        "benefits": "Test benefits",
        "contact_info": "Test contact info",
        "validity_period": "2025"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/admin/schemes", 
                           json=scheme_data, headers=headers)
    print(f"Add scheme response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        scheme_id = result["scheme_id"]
        print(f"✅ Scheme added successfully! ID: {scheme_id}")
        
        # Test updating the scheme
        print("\nTesting update scheme...")
        update_data = {
            "name": "Updated Test Scheme",
            "description": "Updated description"
        }
        
        response = requests.put(f"{BASE_URL}/api/v1/admin/schemes/{scheme_id}", 
                              json=update_data, headers=headers)
        print(f"Update scheme response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Scheme updated successfully!")
        else:
            print(f"❌ Update failed: {response.text}")
        
        # Test deleting the scheme
        print("\nTesting delete scheme...")
        response = requests.delete(f"{BASE_URL}/api/v1/admin/schemes/{scheme_id}", 
                                 headers=headers)
        print(f"Delete scheme response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Scheme deleted successfully!")
        else:
            print(f"❌ Delete failed: {response.text}")
    else:
        print(f"❌ Add scheme failed: {response.text}")

def main():
    """Run all tests."""
    print("🚀 Starting admin functionality tests...")
    
    try:
        # Test registration
        reg_result = test_admin_registration()
        if not reg_result:
            print("❌ Registration failed, skipping other tests")
            return
        
        # Test login
        token = test_admin_login()
        if not token:
            print("❌ Login failed, skipping scheme management tests")
            return
        
        # Test scheme management
        test_scheme_management(token)
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
