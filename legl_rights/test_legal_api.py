#!/usr/bin/env python3
"""
Test script for the Digital Rights Legal Database API
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"\n{method} {endpoint}")
        print(f"Error: {e}")
        return False

def main():
    print("Testing Digital Rights Legal Database API")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    test_endpoint("/health")
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    test_endpoint("/")
    
    # Test setup endpoint
    print("\n3. Testing setup endpoint...")
    test_endpoint("/setup")
    
    # Wait a moment for setup to complete
    time.sleep(2)
    
    # Test various questions
    test_questions = [
        "What are my digital rights?",
        "What laws apply to data privacy?",
        "How do I file a complaint for online harassment?",
        "Who enforces net neutrality?",
        "What regions does digital accessibility apply to?"
    ]
    
    print("\n4. Testing question endpoints...")
    for i, question in enumerate(test_questions, 1):
        print(f"\n4.{i} Testing question: '{question}'")
        test_endpoint("/ask", method="POST", data={"question": question})
    
    print("\n" + "=" * 50)
    print("Testing completed!")

if __name__ == "__main__":
    main()