import requests
import json

try:
    print("Sending request to schemes search API...")
    url = "http://localhost:8002/api/v1/schemes/search"
    params = {"query": "disability", "top_k": 10}
    response = requests.get(url, params=params)
    
    print(f"Status Code: {response.status_code}")
    print("Response Headers:")
    print(response.headers)
    print("\nResponse Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
