#!/usr/bin/env python3
"""
Direct database script untuk insert/verify user Evert
"""
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

DB_HOST = os.getenv('DB_HOST', '')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', '')

print("=" * 60)
print("CONNECTING TO DATABASE")
print("=" * 60)
print(f"Host: {DB_HOST}")
print(f"Port: {DB_PORT}")
print(f"User: {DB_USER}")
print(f"Database: {DB_NAME}")
print()

try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    print("✓ Connected to database successfully!\n")
    
    # Check if users table exists
    cursor.execute("""
        SELECT TABLE_NAME FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users'
    """, (DB_NAME,))
    
    if cursor.fetchone():
        print("✓ Table 'users' exists\n")
        
        # Check for Evert user
        cursor.execute("SELECT id, username FROM users WHERE username = %s", ("Evert",))
        evert = cursor.fetchone()
        
        if evert:
            print(f"✓ User 'Evert' sudah ada")
            print(f"  - ID: {evert['id']}")
            print(f"  - Username: {evert['username']}")
        else:
            print("✗ User 'Evert' tidak ada, mencoba insert...\n")
            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    ("Evert", "admin", "admin")
                )
                conn.commit()
                new_id = cursor.lastrowid
                print(f"✓ User 'Evert' berhasil ditambahkan!")
                print(f"  - ID: {new_id}")
                print(f"  - Username: Evert")
                print(f"  - Password: admin (plain text)")
                print(f"  - Role: admin")
            except Exception as e:
                print(f"✗ Error insert: {str(e)}")
                conn.rollback()
        
        # List all users
        print("\n" + "=" * 60)
        print("DAFTAR SEMUA USERS")
        print("=" * 60)
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"ID: {user['id']:3} | Username: {user['username']:15} | Role: {user['role']}")
    else:
        print("✗ Table 'users' tidak ada di database!")
        print("  Jalankan Flask app terlebih dahulu untuk initialize tabel")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"✗ Database Error: {err}")
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
