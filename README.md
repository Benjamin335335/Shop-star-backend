# Shop Pro - Full Featured E-Commerce Platform

A fully functional, premium e-commerce website built with HTML, CSS, and JavaScript. No backend required! All data is stored locally in your browser.

**Owner:** Francis Benjamin | Email: francisbenjamin.official@gmail.com | Phone: +23278335335

## 🚀 Features (Full Version)

### Core Shopping Features
- 🛍️ **Product Marketplace** - Browse, search, and filter products
- 📦 **Product Management** - Add your own products to sell
- 💬 **Contact Integration** - Email, Phone, WhatsApp buttons with pre-filled "I want [Product Name]" messages
- 💰 **Flexible Pricing** - Fixed price or price range options
- ⭐ **Product Ratings** - View and submit product reviews
- 🛒 **Shopping Cart** - Add products with quantity management
- 🎁 **Coupon System** - Apply discount codes (SAVE10, SAVE20, WELCOME5)
- 🔍 **Search & Filter** - Find products by name, description, or category
- 📊 **Sorting** - Sort by newest, price, or ratings

### User Experience
- 🌙 **Dark Mode** - Toggle between light and dark themes
- ❤️ **Favorites/Wishlist** - Mark and organize favorite products
- 📱 **Fully Responsive** - Works on desktop, tablet, and mobile devices
- 👤 **User Profile** - Save personal information and preferences
- 📈 **Dashboard Statistics** - View total products, cart items, and orders

### Advanced Features
- 💳 **Order Management** - Create and track orders
- 📋 **Order History** - View all past and current orders
- 📥 **Data Export** - Backup your products and cart as JSON
- 📤 **Data Import** - Restore your data from backup
- 🔒 **Local Storage** - All data saved securely in browser

## 📁 File Structure

```
shop-website/
├── index.html       # Main HTML file
├── styles.css       # Complete responsive styles
├── app.js           # Full JavaScript with all features
├── backend.py       # Flask API backend
├── requirements.txt # Python dependencies
└── README.md        # Documentation
```

## 🎯 Quick Start

1. **Open the website** - Simply open `index.html` in your web browser
2. **Start shopping** - Click "Shop" to browse products
3. **Search & Filter** - Use search bar and filters to find products
4. **Manage favorites** - Click ❤️ to add products to favorites
5. **Add to cart** - Click products and add to shopping cart
6. **Apply coupons** - Use coupon codes for discounts
7. **Checkout** - Place orders from your cart
8. **Sell products** - Click "Sell" to add your own products
9. **View reviews** - Leave and read product reviews

## 🛍️ Sample Products

The website comes with 5 premium sample products:
1. **Wireless Headphones** - $79.99 (Electronics)
2. **Running Shoes** - $89.99 (Sports)
3. **JavaScript Book** - $34.99 (Books)
4. **Gaming Mouse** - $49.99 (Electronics)
5. **Cotton T-Shirt** - $15.99 - $24.99 (Clothing)

## 🎁 Coupon Codes

Available discount codes:
- **SAVE10** - 10% discount
- **SAVE20** - 20% discount
- **WELCOME5** - 5% discount (newcomers)

## 💾 Data Management

### What Gets Saved?
- ✅ Products you add
- ✅ Cart items
- ✅ Orders placed
- ✅ Favorite products
- ✅ Product reviews and ratings
- ✅ User profile information
- ✅ Dark mode preference

### Local Storage Keys
- `shop-pro-products` - Your products
- `shop-pro-cart` - Shopping cart items
- `shop-pro-orders` - Order history
- `shop-pro-favorites` - Favorite products
- `shop-pro-ratings` - Reviews and ratings
- `shop-pro-user-profile` - User information
- `dark-mode` - Theme preference
- `coupon-discount` - Applied discount

## 🔧 Backend Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Server
```bash
python backend.py
```

The API will be available at `http://127.0.0.1:5000/api`

### API Endpoints
- `GET /api/products` - Get all products
- `POST /api/products` - Create new product
- `GET /api/products/<id>` - Get product by ID
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product
- `GET /api/cart` - Get shopping cart
- `POST /api/cart` - Add to cart
- `DELETE /api/cart/<id>` - Remove from cart
- `POST /api/orders` - Create order
- `GET /api/orders` - Get user orders
- `POST /api/ratings` - Add product rating
- `GET /api/ratings/<product_id>` - Get product ratings
- `GET /api/profile` - Get user profile
- `POST /api/profile` - Update user profile
- `GET /api/health` - Health check

## 🎨 Customization

### Change Owner Contact Info
Update `OWNER_INFO` in `app.js`:
```javascript
const OWNER_INFO = {
    name: 'Your Name',
    email: 'your@email.com',
    phone: '+1234567890',
    whatsapp: '+1234567890'
};
```

### Change Colors
Edit CSS variables in `styles.css`:
```css
:root {
    --primary-color: #3498db;
    --secondary-color: #2c3e50;
    --accent-color: #e74c3c;
    --success-color: #27ae60;
    --light-bg: #ecf0f1;
    --text-color: #333;
}
```

## 🔒 Privacy & Security

- **Local processing** - Frontend handles most operations
- **Backend storage** - Optional Flask backend for data persistence
- **No tracking** - Your activity is private
- **Local storage** - Browser-based database

## 🌍 Deployment Options

### Option 1: GitHub Pages (Free)
1. Create a GitHub repository
2. Upload files
3. Enable GitHub Pages in settings
4. Access at `yourusername.github.io/repo-name`

### Option 2: Netlify (Free)
1. Go to netlify.com
2. Drag and drop your files
3. Get instant live URL

### Option 3: Any Web Host
Upload all files to any web hosting service

### Option 4: Local Use
Just open `index.html` in your browser

## 🎓 Learning Resources

Perfect for learning:
- HTML5 semantic markup
- CSS3 (Grid, Flexbox, Animations, Dark Mode)
- JavaScript (ES6+, LocalStorage, DOM manipulation)
- Python Flask and SQLAlchemy
- RESTful API design
- Responsive web design

## 📊 Statistics & Dashboard

The home page displays:
- Total products listed
- Items in cart
- Orders placed
- Cart total value

## 🛒 Order System

### Creating Orders
1. Add products to cart
2. Adjust quantities as needed
3. Apply coupon (optional)
4. Click "Place Order"
5. Order is saved to history

### Order Details
- Unique order ID
- Item list with quantities
- Order total
- Timestamp
- Order status

## ⭐ Review System

### Leaving Reviews
1. Open product details
2. Scroll to reviews section
3. Select rating (1-5 stars)
4. Write your review
5. Click "Submit Review"

### Viewing Reviews
- See average rating on product card
- Read all reviews in product detail modal
- Review count displays on product

## 💳 Cart Management

### Shopping Cart Features
- Add/remove items
- Adjust quantities
- View item prices
- Apply coupon codes
- See subtotal and total
- Place order from cart

## 🐛 Troubleshooting

### Products not saving?
- Check if database connection is working
- Run backend server: `python backend.py`
- Check browser console (F12) for errors

### Contact buttons not working?
- For email: Configure default email app
- For phone: Have phone app installed
- For WhatsApp: Install WhatsApp app

### Styles not loading?
- Make sure `styles.css` is in same folder as `index.html`
- Clear browser cache
- Check browser console (F12) for errors

### Backend connection issues?
- Ensure Flask backend is running
- Check API URL in `app.js`
- Verify CORS is enabled

## 📞 Contact & Support

**Shop Owner:** Francis Benjamin
- 📧 Email: francisbenjamin.official@gmail.com
- 📱 Phone: +23278335335
- 💬 WhatsApp: +23278335335

## 📄 License

This project is free to use for personal and commercial purposes. Feel free to modify and distribute!

---

**Version:** 2.0 Premium with Backend
**Last Updated:** January 27, 2026
**Status:** Fully Functional ✅

**Happy selling! 🛍️**
