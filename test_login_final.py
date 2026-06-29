#!/usr/bin/env python3
"""Test login dengan requests"""
import requests
import json
import time

# Wait a bit for server to be ready
time.sleep(1)

print("=" * 60)
print("TEST LOGIN EVERT/ADMIN")
print("=" * 60)

login_url = "http://localhost:5000/api/login"
credentials = {
    "username": "Evert",
    "password": "admin"
}

try:
    print(f"POST {login_url}")
    print(f"Data: {json.dumps(credentials)}\n")
    
    response = requests.post(login_url, json=credentials, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n" + "=" * 60)
        print("✓ LOGIN BERHASIL!")
        print("=" * 60)
        token = response.json().get('token')
        print(f"Token: {token[:50]}...")
    else:
        print(f"\n✗ Login Failed")
        
except requests.exceptions.Timeout:
    print("✗ Request timeout")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to server")
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
