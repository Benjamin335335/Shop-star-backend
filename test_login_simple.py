#!/usr/bin/env python3
"""Quick login system verification"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import app

print("\n[STEP 1] Starting Flask server...")
with app.test_client() as client:
    print("[INFO] Test client ready\n")
    
    # Test 1: Admin Login
    print("[TEST 1] Admin Login")
    response = client.post('/api/auth/login',
        json={'username': 'admin', 'password': 'admin123'},
        content_type='application/json'
    )
    data = response.get_json()
    
    if response.status_code == 200 and data.get('success'):
        print("[PASS] Admin login works")
        print("  Username: " + data['user']['username'])
        print("  Email: " + data['user']['email'])
    else:
        print("[FAIL] Admin login failed: " + str(data.get('error')))
        sys.exit(1)
    
    # Test 2: Registration
    print("\n[TEST 2] User Registration")
    response = client.post('/api/auth/signup',
        json={
            'username': 'newuser_' + str(int(os.times()[4]*1000)),
            'email': 'newuser_' + str(int(os.times()[4]*1000)) + '@test.com',
            'password': 'testpass123',
            'full_name': 'New User'
        },
        content_type='application/json'
    )
    data = response.get_json()
    
    if response.status_code == 201 and data.get('success'):
        print("[PASS] User registration works")
        newuser_id = data['user']['id']
        print("  New User ID: " + str(newuser_id))
    else:
        print("[INFO] Registration: " + str(data.get('error')))
    
    # Test 3: Invalid Login
    print("\n[TEST 3] Invalid Password")
    response = client.post('/api/auth/login',
        json={'username': 'admin', 'password': 'wrongpassword'},
        content_type='application/json'
    )
    data = response.get_json()
    
    if response.status_code == 401 and not data.get('success'):
        print("[PASS] Wrong password rejected")
        print("  Error: " + data.get('error', 'Invalid credentials'))
    else:
        print("[FAIL] Wrong password not handled correctly")
    
    # Test 4: Auth Check
    print("\n[TEST 4] Authentication Check")
    response = client.post('/api/auth/check',
        json={'user_id': 1},
        content_type='application/json'
    )
    data = response.get_json()
    
    if response.status_code == 200 and data.get('authenticated'):
        print("[PASS] Auth check works")
    else:
        print("[FAIL] Auth check failed: " + str(data.get('error')))

print("\n" + "="*50)
print("[SUCCESS] All login tests completed!")
print("="*50)
