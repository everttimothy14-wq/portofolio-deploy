#!/usr/bin/env python3
"""
Direct database script untuk insert/verify user Evert dengan timeout handling
"""
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', '')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', '')

print("Connecting to database...")
print(f"Host: {DB_HOST}:{DB_PORT}")

try:
    import mysql.connector
    
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        connection_timeout=10,
        autocommit=False
    )
    cursor = conn.cursor(dictionary=True)
    print("✓ Connected!\n")
    
    # Insert or check Evert
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash)", ("Evert", "admin", "admin"))
    conn.commit()
    
    cursor.execute("SELECT id FROM users WHERE username = %s", ("Evert",))
    result = cursor.fetchone()
    
    if result:
        print(f"✓ SUCCESS! User 'Evert' dengan ID {result['id']} sudah di database")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
