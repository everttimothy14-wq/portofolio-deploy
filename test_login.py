#!/usr/bin/env python3
import requests
import json
from model import Database

# Test login endpoint
def test_login():
    print("=" * 50)
    print("TEST LOGIN EVERT")
    print("=" * 50)
    
    login_url = "http://localhost:5000/api/login"
    credentials = {
        "username": "Evert",
        "password": "admin"
    }
    
    try:
        response = requests.post(login_url, json=credentials, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ LOGIN BERHASIL!")
        else:
            print(f"\n❌ LOGIN GAGAL - Status {response.status_code}")
            
            # Try to insert Evert manually
            print("\n" + "=" * 50)
            print("MENCOBA INSERT USER EVERT KE DATABASE")
            print("=" * 50)
            
            db = Database()
            try:
                # Check if user exists
                check_query = "SELECT id FROM users WHERE username = %s"
                result = db.execute_query(check_query, ("Evert",), fetch=True)
                
                if result:
                    print(f"✓ User 'Evert' sudah ada di database dengan ID: {result[0]['id']}")
                else:
                    print("✗ User 'Evert' belum ada, mencoba insert...")
                    insert_query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
                    db.execute_query(insert_query, ("Evert", "admin", "admin"))
                    print("✓ User 'Evert' berhasil ditambahkan!")
                    
                    # Try login again
                    print("\nMencoba login ulang...")
                    response = requests.post(login_url, json=credentials, timeout=5)
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {json.dumps(response.json(), indent=2)}")
                    
                    if response.status_code == 200:
                        print("\n✅ LOGIN BERHASIL SETELAH INSERT!")
                    
            except Exception as e:
                print(f"❌ Error saat insert: {str(e)}")
                import traceback
                traceback.print_exc()
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connection: {str(e)}")
        print("Pastikan server Flask sudah running di localhost:5000")

if __name__ == "__main__":
    test_login()
