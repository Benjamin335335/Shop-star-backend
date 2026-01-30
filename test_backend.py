#!/usr/bin/env python3
"""
Quick diagnostic script to test the backend and login functionality.
Run this to verify the backend is working properly.
"""

import sys
import os
import sqlite3
import json

# Add the workspace to path
workspace_path = r'c:\Users\Benji\Desktop\New folder (3)'
sys.path.insert(0, workspace_path)
os.chdir(workspace_path)

print("=" * 60)
print("SHOP PRO BACKEND DIAGNOSTIC")
print("=" * 60)

# Step 1: Check if backend.py exists
print("\n[1] Checking backend.py exists...")
if os.path.exists('backend.py'):
    print("✓ backend.py found")
else:
    print("✗ backend.py not found!")
    sys.exit(1)

# Step 2: Check if we can import Flask
print("\n[2] Checking Flask import...")
try:
    from flask import Flask
    print("✓ Flask imported successfully")
except ImportError as e:
    print(f"✗ Flask import failed: {e}")
    sys.exit(1)

# Step 3: Check if we can import backend
print("\n[3] Checking backend.py imports...")
try:
    import backend
    print("✓ backend.py imported successfully")
except Exception as e:
    print(f"✗ backend.py import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Check if app was created
print("\n[4] Checking Flask app...")
if hasattr(backend, 'app'):
    print("✓ Flask app instance found")
else:
    print("✗ Flask app not found!")
    sys.exit(1)

# Step 5: Check if database exists and has admin user
print("\n[5] Checking database...")
db_path = 'instance/shop-pro.db'
if os.path.exists(db_path):
    print(f"✓ Database file exists: {db_path}")
    
    # Check admin user
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, status FROM user WHERE username='admin'")
        admin = cursor.fetchone()
        conn.close()
        
        if admin:
            print(f"✓ Admin user found: id={admin[0]}, username={admin[1]}, role={admin[2]}, status={admin[3]}")
        else:
            print("⚠ Admin user NOT found in database")
    except Exception as e:
        print(f"✗ Error querying database: {e}")
else:
    print(f"⚠ Database file not found at {db_path}")
    print("  This is expected - it will be created on first backend run")

# Step 6: Check if routes are registered
print("\n[6] Checking Flask routes...")
try:
    with backend.app.app_context():
        # Check if login route exists
        routes = [str(rule) for rule in backend.app.url_map.iter_rules()]
        login_route = any('/api/auth/login' in route for route in routes)
        check_route = any('/api/auth/check' in route for route in routes)
        
        if login_route:
            print("✓ /api/auth/login route registered")
        else:
            print("✗ /api/auth/login route NOT found!")
            
        if check_route:
            print("✓ /api/auth/check route registered")
        else:
            print("✗ /api/auth/check route NOT found!")
            
        # List some routes
        print("\nRegistered routes:")
        for route in sorted(routes)[:10]:
            if 'api' in route or 'auth' in route:
                print(f"  - {route}")
except Exception as e:
    print(f"✗ Error checking routes: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print("\nTo start the backend, run:")
print("  python backend.py")
print("\nThen test login with:")
print("  Username: admin")
print("  Password: admin123")
