from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import os

# Initialize Flask app with static and template folders
app = Flask(__name__, 
            static_folder=os.path.dirname(os.path.abspath(__file__)),
            static_url_path='')

# Configure separate databases
app.config['SQLALCHEMY_BINDS'] = {
    'auth_db': 'sqlite:///auth.db',  # Database for users and passwords
    'products_db': 'sqlite:///products.db'  # Database for products and orders
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'  # Main database (auth)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize database
db = SQLAlchemy(app)
CORS(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    __bind_key__ = 'auth_db'  # Store in auth database
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='buyer')  # 'buyer', 'seller', 'admin'
    shop_name = db.Column(db.String(120))  # For sellers
    shop_description = db.Column(db.Text)  # For sellers
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'banned'
    canUploadStock = db.Column(db.Boolean, default=False)  # Buyers with upload permission
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'shop_name': self.shop_name,
            'shop_description': self.shop_description,
            'status': self.status,
            'canUploadStock': self.canUploadStock,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Product(db.Model):
    __bind_key__ = 'products_db'  # Store in products database
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    priceType = db.Column(db.String(10), default='fixed')  # 'fixed' or 'range'
    price = db.Column(db.Float)
    priceMin = db.Column(db.Float)
    priceMax = db.Column(db.Float)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    contactMethods = db.Column(db.String(255))  # JSON string: 'email,phone,whatsapp'
    uploader_id = db.Column(db.Integer, nullable=False)  # Reference to User.id from auth_db
    uploader_name = db.Column(db.String(120))  # Seller/uploader name
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    ratings = db.relationship('Rating', backref='product', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'priceType': self.priceType,
            'price': self.price,
            'priceMin': self.priceMin,
            'priceMax': self.priceMax,
            'email': self.email,
            'phone': self.phone,
            'whatsapp': self.whatsapp,
            'contactMethods': self.contactMethods.split(',') if self.contactMethods else [],
            'uploader_id': self.uploader_id,
            'uploader_name': self.uploader_name,
            'createdAt': self.createdAt.strftime('%Y-%m-%d %H:%M:%S')
        }


class CartItem(db.Model):
    __bind_key__ = 'products_db'  # Store in products database
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)  # Reference to User.id from auth_db
    productId = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    addedAt = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product')

    def to_dict(self):
        product = self.product.to_dict()
        product['quantity'] = self.quantity
        product['cartItemId'] = self.id
        return product


class Order(db.Model):
    __bind_key__ = 'products_db'  # Store in products database
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)  # Reference to User.id from auth_db
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, processing, shipped, delivered, cancelled
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    discountApplied = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'items': [item.to_dict() for item in self.items],
            'total': self.total,
            'status': self.status,
            'date': self.createdAt.strftime('%Y-%m-%d %H:%M:%S'),
            'discountApplied': self.discountApplied
        }


class OrderItem(db.Model):
    __bind_key__ = 'products_db'  # Store in products database
    id = db.Column(db.Integer, primary_key=True)
    orderId = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    productId = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price
        }


class Rating(db.Model):
    __bind_key__ = 'products_db'  # Store in products database
    id = db.Column(db.Integer, primary_key=True)
    productId = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    userId = db.Column(db.Integer, nullable=False)  # Reference to User.id from auth_db
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'review': self.review,
            'createdAt': self.createdAt.strftime('%Y-%m-%d %H:%M:%S')
        }





class Coupon(db.Model):
    __bind_key__ = 'products_db'  # Store in products database
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount = db.Column(db.Integer, nullable=False)  # Discount percentage
    active = db.Column(db.Boolean, default=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'discount': self.discount,
            'active': self.active
        }


class UserProfile(db.Model):
    __bind_key__ = 'products_db'  # Store in products database
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, unique=True, nullable=False)  # Reference to User.id from auth_db
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    darkMode = db.Column(db.Boolean, default=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'darkMode': self.darkMode
        }


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/signup', methods=['POST', 'OPTIONS'])
def signup():
    """Register a new user (buyer)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400
        
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Username, email, and password required'}), 400
        
        # Check if username exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', ''),
            role='buyer',
            status='active'
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        print(f"New user created: {user.username}")
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Signup error: {str(e)}")
        return jsonify({'success': False, 'error': 'Signup failed: ' + str(e)}), 500


@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """Login user"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
        
        if user.status != 'active':
            return jsonify({'success': False, 'error': 'User account is inactive'}), 403
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': 'Login failed: ' + str(e)}), 500


@app.route('/api/auth/check', methods=['POST', 'OPTIONS'])
def check_auth():
    """Check if user is authenticated"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        user_id = data.get('user_id') if data else None
        
        if not user_id:
            return jsonify({'success': False, 'authenticated': False, 'error': 'User ID required'}), 400
        
        user = User.query.get(user_id)
        
        if user and user.status == 'active':
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': user.to_dict()
            }), 200
        
        return jsonify({'success': False, 'authenticated': False, 'error': 'User not found or inactive'}), 401
    except Exception as e:
        print(f"Auth check error: {str(e)}")
        return jsonify({'success': False, 'authenticated': False, 'error': str(e)}), 500


# ==================== SELLER MANAGEMENT (ADMIN ONLY) ====================

@app.route('/api/admin/sellers', methods=['GET'])
def get_all_sellers():
    """Get all seller profiles - admin only"""
    admin_id = request.args.get('admin_id')
    admin = User.query.get(admin_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    sellers = User.query.filter_by(role='seller').all()
    return jsonify({
        'success': True,
        'sellers': [seller.to_dict() for seller in sellers]
    }), 200


@app.route('/api/admin/sellers/<int:seller_id>', methods=['GET'])
def get_seller(seller_id):
    """Get specific seller profile"""
    seller = User.query.get(seller_id)
    if not seller or seller.role != 'seller':
        return jsonify({'success': False, 'error': 'Seller not found'}), 404
    
    return jsonify({
        'success': True,
        'seller': seller.to_dict()
    }), 200


@app.route('/api/admin/sellers', methods=['POST'])
def create_seller_profile():
    """Create a new seller profile - admin only"""
    data = request.json or {}
    admin_id = data.get('admin_id')
    admin = User.query.get(admin_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    if not username or not email:
        return jsonify({'success': False, 'error': 'Username and email required'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'error': 'Username already exists'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email already exists'}), 400
    
    try:
        seller = User(
            username=username,
            email=email,
            full_name=data.get('full_name', ''),
            phone=data.get('phone', ''),
            shop_name=data.get('shop_name', ''),
            shop_description=data.get('shop_description', ''),
            role='seller',
            status='active'
        )
        # Set a temporary password
        seller.set_password(data.get('password', 'temp_password_123'))
        db.session.add(seller)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Seller profile created successfully',
            'seller': seller.to_dict()
        }), 201
    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Database integrity error (possible duplicate)'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/sellers/<int:seller_id>', methods=['PUT'])
def update_seller_profile(seller_id):
    """Update seller profile - admin only"""
    data = request.json
    admin_id = data.get('admin_id')
    admin = User.query.get(admin_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    seller = User.query.get(seller_id)
    if not seller or seller.role != 'seller':
        return jsonify({'success': False, 'error': 'Seller not found'}), 404
    
    try:
        seller.full_name = data.get('full_name', seller.full_name)
        seller.phone = data.get('phone', seller.phone)
        seller.shop_name = data.get('shop_name', seller.shop_name)
        seller.shop_description = data.get('shop_description', seller.shop_description)
        seller.status = data.get('status', seller.status)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Seller profile updated',
            'seller': seller.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/sellers/<int:seller_id>', methods=['DELETE'])
def delete_seller_profile(seller_id):
    """Delete seller profile - admin only"""
    admin_id = request.args.get('admin_id')
    admin = User.query.get(admin_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    seller = User.query.get(seller_id)
    if not seller or seller.role != 'seller':
        return jsonify({'success': False, 'error': 'Seller not found'}), 404
    
    try:
        db.session.delete(seller)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Seller profile deleted'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== USER MANAGEMENT (ADMIN ONLY) ====================

@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Get all users - admin only"""
    admin_id = request.args.get('admin_id')
    admin = User.query.get(admin_id)

    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    users = User.query.all()
    return jsonify({'success': True, 'users': [u.to_dict() for u in users]}), 200


@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile - admin only"""
    admin_id = request.args.get('admin_id')
    admin = User.query.get(admin_id)

    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    return jsonify({'success': True, 'user': user.to_dict()}), 200


@app.route('/api/admin/users/<int:user_id>/promote', methods=['PUT','POST'])
def promote_user_to_seller(user_id):
    """Promote a buyer to seller - admin only"""
    data = request.json or {}
    admin_id = data.get('admin_id') or request.args.get('admin_id')
    admin = User.query.get(admin_id)

    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    try:
        if user.role == 'seller':
            return jsonify({'success': False, 'error': 'User is already a seller'}), 400

        # Promote user
        user.role = 'seller'
        user.shop_name = data.get('shop_name', user.shop_name or '')
        user.shop_description = data.get('shop_description', user.shop_description or '')
        user.canUploadStock = True
        db.session.commit()

        return jsonify({'success': True, 'message': 'User promoted to seller', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== USER UPDATE & DELETE (ADMIN ONLY) ====================

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """Update user profile (username, email, full_name, phone, role, password) - admin only"""
    data = request.json or {}
    admin_id = data.get('admin_id') or request.args.get('admin_id')
    admin = User.query.get(admin_id)

    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    # Admin users can be edited, but their role cannot be changed via this endpoint
    if user.role == 'admin' and 'role' in data and data.get('role') and data.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Cannot change role of admin users'}), 400

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    role = data.get('role')

    try:
        # uniqueness checks
        if username and username != user.username and User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        if email and email != user.email and User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email already exists'}), 400

        if username:
            user.username = username
        if email:
            user.email = email

        if 'full_name' in data:
            user.full_name = data.get('full_name')
        if 'phone' in data:
            user.phone = data.get('phone')
        if 'status' in data:
            user.status = data.get('status')

        # Allow role change only to buyer or seller (do not allow creating admin via this endpoint)
        if role and role in ('buyer', 'seller'):
            user.role = role
            user.canUploadStock = True if role == 'seller' else False

        if 'password' in data and data.get('password'):
            user.set_password(data.get('password'))

        db.session.commit()
        return jsonify({'success': True, 'message': 'User updated', 'user': user.to_dict()}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Database integrity error'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user_profile(user_id):
    """Delete a user - admin only (cannot delete admin users)"""
    admin_id = request.args.get('admin_id')
    admin = User.query.get(admin_id)

    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    if user.role == 'admin':
        return jsonify({'success': False, 'error': 'Cannot delete admin users'}), 400

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/admin/users/<int:user_id>/reset_password', methods=['POST'])
def admin_reset_password(user_id):
    """Admin resets their own password by answering 'What is your full name' question"""
    data = request.json or {}
    admin_id = data.get('admin_id') or request.args.get('admin_id')
    full_name_answer = (data.get('full_name_answer') or '').strip()
    new_password = data.get('new_password') or ''

    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    # Only allow an admin to reset their own admin password via this flow
    if int(admin_id) != int(user_id):
        return jsonify({'success': False, 'error': 'Can only reset your own admin password via this flow'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    # Require full_name to be set and match (case-insensitive)
    if not user.full_name or user.full_name.strip().lower() != full_name_answer.lower():
        return jsonify({'success': False, 'error': 'Security answer mismatch'}), 400

    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400

    try:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password reset successful'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== ADMIN: SELLER ANALYTICS ====================

@app.route('/api/admin/seller_analytics', methods=['GET'])
def admin_seller_analytics():
    """Return analytics for all sellers (admin only)

    Metrics per seller: product_count, avg_rating, date_joined, phone
    """
    admin_id = request.args.get('admin_id')
    admin = User.query.get(admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    sellers = User.query.filter_by(role='seller').all()
    analytics = []

    for s in sellers:
        # products count
        product_count = Product.query.filter_by(uploader_id=s.id).count()

        # average rating for seller's products
        avg_rating = db.session.query(db.func.avg(Rating.rating)).join(
            Product, Product.id == Rating.productId
        ).filter(Product.uploader_id == s.id).scalar() or None

        analytics.append({
            'seller_id': s.id,
            'username': s.username,
            'email': s.email,
            'shop_name': s.shop_name,
            'product_count': int(product_count or 0),
            'avg_rating': float(avg_rating) if avg_rating is not None else None,
            'date_joined': s.created_at.strftime('%Y-%m-%d') if s.created_at else None,
            'phone': s.phone or ''
        })

    return jsonify({'success': True, 'analytics': analytics}), 200


@app.route('/api/seller/<int:seller_id>/analytics', methods=['GET'])
def seller_analytics(seller_id):
    """Return analytics for a single seller.

    Sellers can view their own analytics. Admins can view any seller analytics.
    """
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    # Only allow if user is admin or the owner of the seller account
    if user.role != 'admin' and int(user.id) != int(seller_id):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    seller = User.query.get(seller_id)
    if not seller or seller.role != 'seller':
        return jsonify({'success': False, 'error': 'Seller not found'}), 404

    product_count = Product.query.filter_by(uploader_id=seller.id).count()
    avg_rating = db.session.query(db.func.avg(Rating.rating)).join(
        Product, Product.id == Rating.productId
    ).filter(Product.uploader_id == seller.id).scalar() or None

    analytics = {
        'seller_id': seller.id,
        'username': seller.username,
        'email': seller.email,
        'shop_name': seller.shop_name,
        'product_count': int(product_count or 0),
        'avg_rating': float(avg_rating) if avg_rating is not None else None,
        'date_joined': seller.created_at.strftime('%Y-%m-%d') if seller.created_at else None,
        'phone': seller.phone or ''
    }

    return jsonify({'success': True, 'analytics': analytics}), 200


# ==================== PRODUCT ENDPOINTS ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products or filter by seller_id"""
    seller_id = request.args.get('seller_id')
    
    if seller_id:
        try:
            seller_id = int(seller_id)
            products = Product.query.filter_by(uploader_id=seller_id).all()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid seller_id'}), 400
    else:
        products = Product.query.all()
    
    return jsonify({
        'success': True,
        'products': [p.to_dict() for p in products]
    }), 200


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    
    return jsonify({
        'success': True,
        'product': product.to_dict()
    }), 200


@app.route('/api/products', methods=['POST'])
def add_product():
    """Add new product - seller only"""
    data = request.json
    user_id = data.get('seller_id') or data.get('user_id')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    if user.role != 'seller':
        return jsonify({'success': False, 'error': 'Only sellers can upload products'}), 403
    
    if user.status != 'active':
        return jsonify({'success': False, 'error': 'Seller account is inactive'}), 403
    
    try:
        contactMethods = data.get('contactMethods', [])
        product = Product(
            name=data['name'],
            category=data['category'],
            description=data.get('description', ''),
            priceType=data.get('priceType', 'fixed'),
            price=data.get('price'),
            priceMin=data.get('priceMin'),
            priceMax=data.get('priceMax'),
            email=data.get('email', user.email),
            phone=data.get('phone', user.phone),
            whatsapp=data.get('whatsapp', ''),
            contactMethods=','.join(contactMethods) if contactMethods else '',
            uploader_id=user_id,
            uploader_name=user.shop_name or user.full_name or user.username
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product added successfully',
            'product': product.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product - seller or admin only"""
    data = request.json
    user_id = data.get('user_id')
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Only product owner or admin can update
    if user.role != 'admin' and product.uploader_id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        product.name = data.get('name', product.name)
        product.category = data.get('category', product.category)
        product.description = data.get('description', product.description)
        product.priceType = data.get('priceType', product.priceType)
        product.price = data.get('price', product.price)
        product.priceMin = data.get('priceMin', product.priceMin)
        product.priceMax = data.get('priceMax', product.priceMax)
        product.email = data.get('email', product.email)
        product.phone = data.get('phone', product.phone)
        product.whatsapp = data.get('whatsapp', product.whatsapp)
        
        if 'contactMethods' in data:
            product.contactMethods = ','.join(data['contactMethods'])
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product - seller or admin only"""
    # Use silent JSON parsing to avoid BadRequest when Content-Type is present but body is empty
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id') or request.args.get('user_id')
    
    try:
        user_id = int(user_id) if user_id is not None else None
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid user_id'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Only product owner or admin can delete
    if user.role != 'admin' and product.uploader_id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/seller/<int:seller_id>/products', methods=['GET'])
def get_seller_products(seller_id):
    """Get all products by a specific seller"""
    seller = User.query.get(seller_id)
    if not seller or seller.role != 'seller':
        return jsonify({'success': False, 'error': 'Seller not found'}), 404
    
    products = Product.query.filter_by(uploader_id=seller_id).all()
    return jsonify({
        'success': True,
        'seller': seller.to_dict(),
        'products': [p.to_dict() for p in products],
        'product_count': len(products)
    }), 200


# ==================== CART ENDPOINTS ====================

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get user's shopping cart"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'User ID required'}), 400
    
    cart_items = CartItem.query.filter_by(userId=user_id).all()
    return jsonify({
        'success': True,
        'items': [item.to_dict() for item in cart_items]
    }), 200


@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not user_id or not product_id:
        return jsonify({'success': False, 'error': 'User ID and product ID required'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    
    try:
        existing_item = CartItem.query.filter_by(userId=user_id, productId=product_id).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_item = CartItem(userId=user_id, productId=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item added to cart'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/cart/<int:cart_item_id>', methods=['DELETE'])
def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item:
        return jsonify({'success': False, 'error': 'Cart item not found'}), 404
    
    try:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item removed from cart'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== ORDER ENDPOINTS ====================

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order from cart"""
    data = request.json
    user_id = data.get('user_id')
    discount_code = data.get('discountCode')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'User ID required'}), 400
    
    cart_items = CartItem.query.filter_by(userId=user_id).all()
    
    if not cart_items:
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400
    
    try:
        total = 0
        order = Order(userId=user_id)
        
        for cart_item in cart_items:
            product = cart_item.product
            order_item = OrderItem(
                productId=product.id,
                name=product.name,
                quantity=cart_item.quantity,
                price=product.price or 0
            )
            total += (product.price or 0) * cart_item.quantity
            db.session.add(order_item)
            order.items.append(order_item)
        
        # Apply coupon discount if provided
        discount_percent = 0
        if discount_code:
            coupon = Coupon.query.filter_by(code=discount_code.upper(), active=True).first()
            if coupon:
                discount_percent = coupon.discount
                order.discountApplied = discount_code.upper()
        
        # Calculate final total with discount
        if discount_percent > 0:
            total = total * (1 - discount_percent / 100)
        
        order.total = total
        db.session.add(order)
        
        # Clear cart
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order': order.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get user's orders"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'User ID required'}), 400
    
    orders = Order.query.filter_by(userId=user_id).all()
    return jsonify({
        'success': True,
        'orders': [order.to_dict() for order in orders]
    }), 200


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404
    
    return jsonify({
        'success': True,
        'order': order.to_dict()
    }), 200





# ==================== RATING ENDPOINTS ====================

@app.route('/api/ratings/<int:product_id>', methods=['GET'])
def get_product_ratings(product_id):
    """Get all ratings for a product"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    
    ratings = Rating.query.filter_by(productId=product_id).all()
    return jsonify({
        'success': True,
        'ratings': [rating.to_dict() for rating in ratings]
    }), 200


@app.route('/api/ratings', methods=['POST'])
def add_rating():
    """Add rating/review to product"""
    data = request.json
    product_id = data.get('product_id')
    user_id = data.get('user_id')
    rating = data.get('rating')
    review = data.get('review', '')
    
    if not product_id or not rating:
        return jsonify({'success': False, 'error': 'Product ID and rating required'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    
    try:
        new_rating = Rating(
            productId=product_id,
            userId=user_id,
            rating=rating,
            review=review
        )
        db.session.add(new_rating)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating added successfully',
            'rating': new_rating.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== PROFILE ENDPOINTS ====================

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    user_id = request.args.get('userId')
    profile = UserProfile.query.filter_by(userId=user_id).first()
    if not profile:
        profile = UserProfile(userId=user_id)
        db.session.add(profile)
        db.session.commit()
    return jsonify(profile.to_dict())


@app.route('/api/profile', methods=['POST'])
def update_profile():
    """Update user profile"""
    data = request.json
    user_id = data.get('userId')
    
    try:
        profile = UserProfile.query.filter_by(userId=user_id).first()
        if not profile:
            profile = UserProfile(userId=user_id)
        
        profile.name = data.get('name', profile.name)
        profile.email = data.get('email', profile.email)
        profile.phone = data.get('phone', profile.phone)
        profile.address = data.get('address', profile.address)
        profile.darkMode = data.get('darkMode', profile.darkMode)
        
        db.session.add(profile)
        db.session.commit()
        return jsonify({'success': True, 'profile': profile.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ==================== COUPON ENDPOINTS ====================

@app.route('/api/validate-coupon', methods=['POST'])
def validate_coupon():
    """Validate and get discount for coupon code"""
    data = request.json
    code = data.get('code', '').upper()
    
    coupon = Coupon.query.filter_by(code=code, active=True).first()
    
    if not coupon:
        return jsonify({'success': False, 'error': 'Invalid coupon code'}), 404
    
    return jsonify({
        'success': True,
        'discount': coupon.discount,
        'message': f'{coupon.discount}% discount applied'
    }), 200


# ==================== SEARCH & FILTER ENDPOINTS ====================

@app.route('/api/search', methods=['GET'])
def search_products():
    """Search products by name or description"""
    query = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'newest')
    
    products = Product.query
    
    if query:
        products = products.filter(
            (Product.name.ilike(f'%{query}%')) |
            (Product.description.ilike(f'%{query}%'))
        )
    
    if category:
        products = products.filter_by(category=category)
    
    products = products.all()
    
    # Sort products
    if sort_by == 'price-low':
        products.sort(key=lambda p: p.price or p.priceMin or 0)
    elif sort_by == 'price-high':
        products.sort(key=lambda p: p.price or p.priceMax or 0, reverse=True)
    else:  # newest
        products.sort(key=lambda p: p.createdAt or datetime.utcnow(), reverse=True)
    
    return jsonify({
        'success': True,
        'products': [p.to_dict() for p in products]
    }), 200


# ==================== EXPORT/IMPORT ENDPOINTS ====================

@app.route('/api/export', methods=['GET'])
def export_data():
    """Export user data as JSON"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'User ID required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    try:
        export_data_dict = {
            'user': user.to_dict(),
            'products': [p.to_dict() for p in user.products],
            'orders': [o.to_dict() for o in Order.query.filter_by(userId=user_id).all()],
            'ratings': [r.to_dict() for r in Rating.query.filter_by(userId=user_id).all()],
            'profile': UserProfile.query.filter_by(userId=user_id).first().to_dict() if UserProfile.query.filter_by(userId=user_id).first() else {}
        }
        
        return jsonify({
            'success': True,
            'data': export_data_dict
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/import', methods=['POST'])
def import_data():
    """Import user data from JSON"""
    data = request.json
    user_id = data.get('user_id')
    import_data_dict = data.get('data', {})
    
    if not user_id:
        return jsonify({'success': False, 'error': 'User ID required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    try:
        # Note: In production, implement more robust import with conflict resolution
        # For now, we'll just acknowledge the import
        return jsonify({
            'success': True,
            'message': 'Data import started'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Shop Pro API is running'})


# ==================== FRONTEND ROUTES ====================

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def serve_index():
    """Serve index.html"""
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html'), 'r') as f:
            return f.read()
    except:
        return jsonify({'error': 'index.html not found'}), 404

@app.route('/styles.css', methods=['GET'])
def serve_styles():
    """Serve styles.css"""
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'styles.css'), 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/css'}
    except:
        return jsonify({'error': 'styles.css not found'}), 404

@app.route('/app.js', methods=['GET'])
def serve_app_js():
    """Serve app.js"""
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.js'), 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/javascript'}
    except:
        return jsonify({'error': 'app.js not found'}), 404



# ==================== ERROR HANDLERS ====================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'error': 'Bad request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'success': False, 'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'success': False, 'error': 'Forbidden'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    print(f"Server error: {str(error)}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.before_request
def before_request():
    """Log incoming requests"""
    print(f"[{request.method}] {request.path}")
    
@app.after_request
def after_request(response):
    """Add CORS headers to response"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# ==================== INITIALIZATION ====================

def init_admin():
    """Create default admin user and sample coupons

    This routine now checks for any existing admin by role to avoid creating
    a second admin with a conflicting email/username (which previously caused
    sqlite IntegrityError on server start).
    """
    # Prefer any existing admin (by role) rather than strictly looking for username 'admin'
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        try:
            admin = User(
                username='admin',
                email='admin@shoppro.com',
                full_name='Shop Pro Admin',
                role='admin',
                status='active'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
        except IntegrityError:
            # If there's a unique conflict (email/username exists), rollback and skip
            db.session.rollback()
            existing = User.query.filter((User.username == 'admin') | (User.email == 'admin@shoppro.com')).first()
            if existing:
                print(f"Admin creation skipped; existing account found: {existing.username} ({existing.email})")
            else:
                # Unknown integrity error -- re-raise for visibility
                raise
    
    # Create sample coupons if they don't exist
    if not Coupon.query.filter_by(code='SAVE10').first():
        coupons = [
            Coupon(code='SAVE10', discount=10, active=True),
            Coupon(code='SAVE20', discount=20, active=True),
            Coupon(code='WELCOME5', discount=5, active=True)
        ]
        for coupon in coupons:
            db.session.add(coupon)
        db.session.commit()
        print("Sample coupons created: SAVE10 (10%), SAVE20 (20%), WELCOME5 (5%)")


# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_admin()
    app.run(debug=True, host='127.0.0.1', port=5000)
