# Database Setup Guide

## Overview

Your application now uses **two separate SQLite databases** for better security and organization:

1. **auth.db** - Authentication & User Management
2. **products.db** - Products, Orders & Commerce

## Database Files

Both database files will be created automatically in the project root:
```
c:\Users\Benji\Desktop\New folder (3)\
├── auth.db           (Authentication database)
├── products.db       (Products database)
├── backend.py
├── app.js
└── ... other files
```

## Database Initialization

The databases are automatically created when you run:
```bash
python backend.py
```

The `init_admin()` function will:
- Create default admin user (username: admin, password: admin123)
- Initialize sample coupons (SAVE10, SAVE20, WELCOME5)

## Database Contents

### auth.db
| Table | Purpose |
|-------|---------|
| user | User accounts, login credentials, user profiles |
| user_profile | User preferences and settings |

### products.db
| Table | Purpose |
|-------|---------|
| product | Product listings and inventory |
| cart_item | Shopping cart items |
| order | Customer orders |
| order_item | Items within orders |
| rating | Product reviews and ratings |
| coupon | Discount codes |

## Login System Flow

1. **User Registration** → Data stored in `auth.db` (User table)
2. **User Login** → Credentials verified from `auth.db`
3. **Product Upload** → Product stored in `products.db` with uploader_id reference
4. **Create Order** → Order data stored in `products.db` with userId reference

## API Endpoints

### Authentication (auth.db)
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/check` - Verify session

### Products (products.db)
- `GET /api/products` - Get all products
- `POST /api/products` - Add product
- `GET /api/products/{id}` - Get product details

### Orders (products.db)
- `POST /api/orders` - Create order
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}/status` - Update order status

## Cross-Database References

Since the databases are separate, User IDs are referenced by value:
- Products store `uploader_id` (not a FK to auth.db)
- Orders store `userId` (not a FK to auth.db)
- CartItems store `userId` (not a FK to auth.db)

This allows complete isolation while maintaining data relationships.

## Backup & Maintenance

### Backup Files
```bash
# Backup auth database
copy auth.db auth.db.backup

# Backup products database
copy products.db products.db.backup
```

### Restoring
```bash
# Restore auth database
copy auth.db.backup auth.db

# Restore products database
copy products.db.backup products.db
```

## Performance Notes

- Separate databases allow independent optimization
- Authentication queries are isolated from product queries
- Scaling auth and products independently is possible
- Better concurrency: One DB write doesn't lock the other

## Troubleshooting

### Login Not Working?
1. Check if `auth.db` exists
2. Verify user credentials in `auth.db`
3. Check password hash verification in backend.py

### Products Not Showing?
1. Check if `products.db` exists
2. Verify uploader_id matches existing user ID
3. Check product query in `/api/products` endpoint

### Reset Everything
Delete both database files and restart the server:
```bash
del auth.db
del products.db
python backend.py
```

This will create fresh databases with the default admin user.
