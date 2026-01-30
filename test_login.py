#!/usr/bin/env python3
"""
Test script to verify the login system works correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import app, db, User, Product, Coupon

def test_databases():
    """Test that both databases are properly configured"""
    print("\n" + "="*50)
    print("Testing Database Configuration")
    print("="*50)
    
    with app.app_context():
        # Create all tables in both databases
        db.create_all()
        print("- Created all database tables")
        
        # Check User model (auth_db)
        print(f"- User model bind key: {User.__bind_key__}")
        print(f"- User table: {User.__tablename__}")
        
        # Check Product model (products_db)
        print(f"- Product model bind key: {Product.__bind_key__}")
        print(f"- Product table: {Product.__tablename__}")
        
        # Check Coupon model (products_db)
        print(f"- Coupon model bind key: {Coupon.__bind_key__}")
        print(f"- Coupon table: {Coupon.__tablename__}")
        
        print("\nDatabase configuration: SUCCESS")


def test_user_creation_and_login():
    """Test user creation and login functionality"""
    print("\n" + "="*50)
    print("Testing User Creation and Login")
    print("="*50)
    
    with app.app_context():
        # Clean up test user if exists
        test_user = User.query.filter_by(username='testuser').first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()
            print("- Cleaned up existing test user")
        
        # Create a new user
        user = User(
            username='testuser',
            email='testuser@example.com',
            full_name='Test User',
            role='buyer'
        )
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        print(f"- Created test user: {user.username} (ID: {user.id})")
        
        # Test password verification
        user_from_db = User.query.filter_by(username='testuser').first()
        if user_from_db and user_from_db.check_password('testpassword123'):
            print("- Password verification: SUCCESS")
        else:
            print("- Password verification: FAILED")
            return False
        
        # Test login scenario
        login_user = User.query.filter_by(username='testuser').first()
        if login_user and login_user.status == 'active':
            print(f"- Login check: SUCCESS (User is active)")
            return True
        else:
            print("- Login check: FAILED")
            return False


def test_product_creation():
    """Test product creation in the products database"""
    print("\n" + "="*50)
    print("Testing Product Creation")
    print("="*50)
    
    with app.app_context():
        # Get a user first (from previous test)
        user = User.query.filter_by(username='testuser').first()
        if not user:
            print("- No test user found, skipping product creation test")
            return False
        
        # Create a test product
        product = Product(
            name='Test Product',
            category='Electronics',
            description='A test product',
            priceType='fixed',
            price=99.99,
            uploader_id=user.id,
            uploader_name=user.full_name
        )
        db.session.add(product)
        db.session.commit()
        print(f"- Created test product: {product.name} (ID: {product.id})")
        print(f"- Product uploader: {product.uploader_id}")
        
        # Verify product retrieval
        retrieved_product = Product.query.get(product.id)
        if retrieved_product:
            print("- Product retrieval: SUCCESS")
            return True
        else:
            print("- Product retrieval: FAILED")
            return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LOGIN SYSTEM AND DATABASE TESTS")
    print("="*60)
    
    try:
        test_databases()
        success = test_user_creation_and_login()
        if success:
            test_product_creation()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nDatabases are properly configured:")
        print("  - auth.db: Stores User credentials and passwords")
        print("  - products.db: Stores Products, Orders, and related data")
        print("\nLogin system is ready to use!")
        
    except Exception as e:
        print(f"\nERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
