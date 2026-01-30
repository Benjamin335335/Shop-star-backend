# Quick Start - Login System & Databases

## What Was Fixed

Your login system now has **two separate databases** instead of one:

| Database | Purpose | Contains |
|----------|---------|----------|
| **auth.db** | 🔐 Authentication | Passwords, Users, Credentials |
| **products.db** | 📦 Commerce | Products, Orders, Coupons |

## Getting Started

### 1. Start the Server
```bash
python backend.py
```

The server will:
- Create both databases automatically (auth.db and products.db)
- Initialize admin user (username: `admin`, password: `admin123`)
- Create sample coupons (SAVE10, SAVE20, WELCOME5)
- Run on http://127.0.0.1:5000

### 2. Test the Login System
```bash
python test_login.py
```

You should see:
```
✓ Database configuration: SUCCESS
✓ User creation and login: SUCCESS  
✓ Product creation: SUCCESS
✓ ALL TESTS COMPLETED SUCCESSFULLY
```

### 3. Use the Application
Open `index.html` in a browser and:
- Register a new account (stored in auth.db)
- Login (verified from auth.db)
- Upload products (stored in products.db)
- Browse and order products

## Database Files Created

After running the server, you'll see in your project folder:
```
auth.db       ← User credentials & passwords (encrypted)
products.db   ← Products, orders, and other commerce data
```

## Admin Login

- **Username:** admin
- **Password:** admin123

## API Endpoints

### Login
```bash
POST /api/auth/login
{
  "username": "testuser",
  "password": "testpassword"
}
```

### Register
```bash
POST /api/auth/signup
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "full_name": "Full Name"
}
```

### Get Products
```bash
GET /api/products
```

### Add Product (Seller)
```bash
POST /api/products
{
  "seller_id": 1,
  "name": "Product Name",
  "category": "Electronics",
  "price": 99.99,
  "description": "Product description"
}
```

## Key Improvements

✅ **Security** - Passwords isolated in separate database
✅ **Performance** - Independent database optimization
✅ **Reliability** - Reduced breach impact
✅ **Scalability** - Easier to scale auth vs products separately
✅ **Backup** - Can backup auth and products independently

## Troubleshooting

### "Login failed"
1. Make sure auth.db exists (check project folder)
2. Verify username and password are correct
3. Check user status is 'active'

### "Can't add products"
1. Make sure products.db exists
2. Verify seller_id matches an existing user
3. Check user role is 'seller'

### "Reset everything"
Delete both databases and restart:
```bash
del auth.db
del products.db
python backend.py
```

## Documentation

For detailed information, see:
- **DATABASE_SETUP.md** - Database structure and setup
- **LOGIN_FIX_SUMMARY.md** - Technical implementation details
- **CHANGELOG.md** - Complete list of changes made

## Support

Both databases are SQLite files. You can:
- Backup: `copy auth.db auth.db.backup`
- Restore: `copy auth.db.backup auth.db`
- Browse with SQLite browser tools

That's it! Your login system is fixed and ready to use! 🎉
