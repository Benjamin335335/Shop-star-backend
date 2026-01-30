#!/usr/bin/env python3
"""
Comprehensive login system test
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import app, db, User

def clean_database():
    """Delete all test users"""
    print("\n" + "="*60)
    print("CLEANING TEST USERS")
    print("="*60)
    
    with app.app_context():
        # Delete test users
        test_users = ['testuser', 'testuser2', 'testuser3']
        for username in test_users:
            user = User.query.filter_by(username=username).first()
            if user:
                db.session.delete(user)
                print("- Deleted test user: " + username)
        db.session.commit()

def test_database_setup():
    """Test database initialization"""
    print("\n" + "="*60)
    print("TEST 1: DATABASE SETUP")
    print("="*60)
    
    with app.app_context():
        db.create_all()
        print("[OK] Databases created successfully")
        
        # Check admin exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("[OK] Admin user exists")
        else:
            print("[FAIL] Admin user not found")
            return False
    
    return True

def test_user_registration():
    """Test user registration"""
    print("\n" + "="*60)
    print("TEST 2: USER REGISTRATION")
    print("="*60)
    
    with app.app_context():
        # Test 1: Valid registration
        user = User(
            username='testuser',
            email='testuser@example.com',
            full_name='Test User',
            role='buyer',
            status='active'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        print("[OK] User registration successful")
        
        # Test 2: Check user was created
        created_user = User.query.filter_by(username='testuser').first()
        if created_user:
            print("[OK] User found in database")
        else:
            print("[FAIL] User not found in database")
            return False
        
        # Test 3: Check password hashing
        if not created_user.password_hash.startswith('pbkdf2:sha256') and not created_user.password_hash.startswith('scrypt:'):
            print("[FAIL] Password not hashed properly")
            return False
        print("[OK] Password hashed correctly")
    
    return True

def test_user_authentication():
    """Test user authentication"""
    print("\n" + "="*60)
    print("TEST 3: USER AUTHENTICATION")
    print("="*60)
    
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        
        if not user:
            print("[FAIL] User not found")
            return False
        
        # Test 1: Correct password
        if user.check_password('testpass123'):
            print("[OK] Correct password verified")
        else:
            print("[FAIL] Correct password rejected")
            return False
        
        # Test 2: Wrong password
        if user.check_password('wrongpassword'):
            print("[FAIL] Wrong password accepted")
            return False
        print("[OK] Wrong password rejected")
        
        # Test 3: User status
        if user.status == 'active':
            print("[OK] User status is active")
        else:
            print("[FAIL] User status not active")
            return False
    
    return True

def test_admin_login():
    """Test admin login"""
    print("\n" + "="*60)
    print("TEST 4: ADMIN LOGIN")
    print("="*60)
    
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("[FAIL] Admin user not found")
            return False
        
        if admin.check_password('admin123'):
            print("[OK] Admin password verified")
        else:
            print("[FAIL] Admin password incorrect")
            return False
        
        if admin.status == 'active':
            print("[OK] Admin status is active")
        else:
            print("[FAIL] Admin status not active")
            return False
    
    return True

def test_api_endpoints():
    """Test API endpoints"""
    print("\n" + "="*60)
    print("TEST 5: API ENDPOINTS")
    print("="*60)
    
    with app.test_client() as client:
        # Test 1: Login endpoint exists
        response = client.post('/api/auth/login',
            json={'username': 'admin', 'password': 'admin123'},
            content_type='application/json'
        )
        print("[OK] Login endpoint responded with status " + str(response.status_code))
        
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print("[OK] Login successful")
                if data.get('user'):
                    print("[OK] User data returned: " + str(data['user'].get('username')))
            else:
                print("[FAIL] Login failed: " + str(data.get('error')))
                return False
        else:
            print("[FAIL] Login returned status " + str(response.status_code))
            return False
        
        # Test 2: Signup endpoint
        response = client.post('/api/auth/signup',
            json={
                'username': 'testuser2',
                'email': 'testuser2@example.com',
                'password': 'testpass123',
                'full_name': 'Test User 2'
            },
            content_type='application/json'
        )
        print("[OK] Signup endpoint responded with status " + str(response.status_code))
        
        if response.status_code == 201:
            data = response.get_json()
            if data.get('success'):
                print("[OK] Signup successful")
            else:
                print("[FAIL] Signup failed: " + str(data.get('error')))
                return False
        else:
            print("[FAIL] Signup returned status " + str(response.status_code))
        
        # Test 3: Check auth endpoint
        response = client.post('/api/auth/check',
            json={'user_id': 1},
            content_type='application/json'
        )
        print("[OK] Check auth endpoint responded with status " + str(response.status_code))
        
        if response.status_code == 200:
            data = response.get_json()
            if data.get('authenticated'):
                print("[OK] Authentication check successful")
            else:
                print("[FAIL] Authentication check failed: " + str(data.get('error')))
        else:
            print("[FAIL] Check auth returned status " + str(response.status_code))
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE LOGIN SYSTEM TEST")
    print("="*60)
    
    tests = [
        ("Database Setup", test_database_setup),
        ("User Registration", test_user_registration),
        ("User Authentication", test_user_authentication),
        ("Admin Login", test_admin_login),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print("[FAIL] Exception in " + test_name + ": " + str(e))
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(status + " " + test_name)
    
    print("\nTotal: " + str(passed) + "/" + str(total) + " tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED! Login system is ready!")
        return True
    else:
        print("\n[WARNING] " + str(total - passed) + " test(s) failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

def test_database_setup():
    """Test database initialization"""
    print("\n" + "="*60)
    print("TEST 1: DATABASE SETUP")
    print("="*60)
    
    with app.app_context():
        db.create_all()
        print("✓ Databases created successfully")
        
        # Check admin exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("✓ Admin user exists")
        else:
            print("✗ Admin user not found")
            return False
    
    return True

def test_user_registration():
    """Test user registration"""
    print("\n" + "="*60)
    print("TEST 2: USER REGISTRATION")
    print("="*60)
    
    with app.app_context():
        # Test 1: Valid registration
        user = User(
            username='testuser',
            email='testuser@example.com',
            full_name='Test User',
            role='buyer',
            status='active'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        print("✓ User registration successful")
        
        # Test 2: Check user was created
        created_user = User.query.filter_by(username='testuser').first()
        if created_user:
            print("✓ User found in database")
        else:
            print("✗ User not found in database")
            return False
        
        # Test 3: Check password hashing
        if not created_user.password_hash.startswith('pbkdf2:sha256'):
            print("✗ Password not hashed properly")
            return False
        print("✓ Password hashed correctly")
    
    return True

def test_user_authentication():
    """Test user authentication"""
    print("\n" + "="*60)
    print("TEST 3: USER AUTHENTICATION")
    print("="*60)
    
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        
        if not user:
            print("✗ User not found")
            return False
        
        # Test 1: Correct password
        if user.check_password('testpass123'):
            print("✓ Correct password verified")
        else:
            print("✗ Correct password rejected")
            return False
        
        # Test 2: Wrong password
        if user.check_password('wrongpassword'):
            print("✗ Wrong password accepted")
            return False
        print("✓ Wrong password rejected")
        
        # Test 3: User status
        if user.status == 'active':
            print("✓ User status is active")
        else:
            print("✗ User status not active")
            return False
    
    return True

def test_admin_login():
    """Test admin login"""
    print("\n" + "="*60)
    print("TEST 4: ADMIN LOGIN")
    print("="*60)
    
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("✗ Admin user not found")
            return False
        
        if admin.check_password('admin123'):
            print("✓ Admin password verified")
        else:
            print("✗ Admin password incorrect")
            return False
        
        if admin.status == 'active':
            print("✓ Admin status is active")
        else:
            print("✗ Admin status not active")
            return False
    
    return True

def test_api_endpoints():
    """Test API endpoints"""
    print("\n" + "="*60)
    print("TEST 5: API ENDPOINTS")
    print("="*60)
    
    with app.test_client() as client:
        # Test 1: Login endpoint exists
        response = client.post('/api/auth/login',
            json={'username': 'admin', 'password': 'admin123'},
            content_type='application/json'
        )
        print(f"✓ Login endpoint responded with status {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print("✓ Login successful")
                if data.get('user'):
                    print(f"✓ User data returned: {data['user'].get('username')}")
            else:
                print(f"✗ Login failed: {data.get('error')}")
                return False
        else:
            print(f"✗ Login returned status {response.status_code}")
            return False
        
        # Test 2: Signup endpoint
        response = client.post('/api/auth/signup',
            json={
                'username': 'testuser2',
                'email': 'testuser2@example.com',
                'password': 'testpass123',
                'full_name': 'Test User 2'
            },
            content_type='application/json'
        )
        print(f"✓ Signup endpoint responded with status {response.status_code}")
        
        if response.status_code == 201:
            data = response.get_json()
            if data.get('success'):
                print("✓ Signup successful")
            else:
                print(f"✗ Signup failed: {data.get('error')}")
                return False
        else:
            print(f"✗ Signup returned status {response.status_code}")
        
        # Test 3: Check auth endpoint
        response = client.post('/api/auth/check',
            json={'user_id': 1},
            content_type='application/json'
        )
        print(f"✓ Check auth endpoint responded with status {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            if data.get('authenticated'):
                print("✓ Authentication check successful")
            else:
                print(f"✗ Authentication check failed: {data.get('error')}")
        else:
            print(f"✗ Check auth returned status {response.status_code}")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE LOGIN SYSTEM TEST")
    print("="*60)
    
    tests = [
        ("Database Setup", test_database_setup),
        ("User Registration", test_user_registration),
        ("User Authentication", test_user_authentication),
        ("Admin Login", test_admin_login),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Exception in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Login system is ready!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
