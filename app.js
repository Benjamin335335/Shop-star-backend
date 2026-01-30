// ...existing code...
// API Configuration
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Global state
let currentUser = null;
let currentProduct = null;
let currentDiscount = 0;
// Store all products for filtering/sorting
let allProducts = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkUserSession();
    loadDarkMode();
});

// ==================== AUTHENTICATION ====================

async function checkUserSession() {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            const result = await apiCall('/auth/check', {
                method: 'POST',
                body: JSON.stringify({ user_id: currentUser.id })
            });
            
            if (result && result.authenticated) {
                showLoggedInUI();
                loadAppContent();
            } else {
                logout();
            }
        } catch (e) {
            console.error('Session check failed:', e);
            logout();
        }
    } else {
        showLoginUI();
    }
}

async function signup(event) {
    event.preventDefault();
    const username = document.getElementById('signup-username').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;
    const fullName = document.getElementById('signup-fullname').value.trim();

    // Validation
    if (!username || !email || !password) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }

    console.log('Attempting signup with username:', username);

    try {
        const result = await apiCall('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                full_name: fullName
            })
        });

        if (result && result.success) {
            showToast('Registration successful! Please login.', 'success');
            document.getElementById('signup-form').reset();
            showLoginPanel();
        } else {
            showToast(result?.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showToast('Signup failed: ' + error.message, 'error');
    }
}

async function login(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    // Validation
    if (!username || !password) {
        showToast('Please enter both username and password', 'error');
        return;
    }

    console.log('Attempting login with username:', username);
    console.log('API Base URL:', API_BASE_URL);

    try {
        const result = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        console.log('Login result:', result);

        if (result && result.success) {
            currentUser = result.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            console.log('User logged in:', currentUser);
            showToast('Login successful!', 'success');
            document.getElementById('login-form').reset();
            showLoggedInUI();
            loadAppContent();
        } else {
            const errorMsg = result?.error || 'Login failed - Invalid username or password';
            console.error('Login error:', errorMsg);
            showToast(errorMsg, 'error');
        }
    } catch (error) {
        console.error('Login exception:', error);
        showToast('Login error: ' + error.message, 'error');
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    console.log('User logged out');
    showToast('Logged out', 'info');
    showLoginUI();
    // Don't reload immediately - let UI update first
    setTimeout(() => {
        document.getElementById('login-form').reset();
        document.getElementById('signup-form').reset();
    }, 100);
}

// ==================== UI FUNCTIONS ====================

function showLoginUI() {
    document.getElementById('auth-container').style.display = 'flex';
    document.getElementById('app-container').style.display = 'none';
}

function showLoggedInUI() {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('app-container').style.display = 'block';
}

function showLoginPanel() {
    document.getElementById('login-panel').style.display = 'block';
    document.getElementById('signup-panel').style.display = 'none';
}

function showSignupPanel() {
    document.getElementById('login-panel').style.display = 'none';
    document.getElementById('signup-panel').style.display = 'block';
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
}

// ==================== API UTILITY ====================

async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    try {
        console.log('API Call:', method=options.method || 'GET', url);
        const response = await fetch(url, { ...defaultOptions, ...options });
        let data = null;
        
        // Try to parse JSON response
        try {
            data = await response.json();
        } catch (e) {
            console.warn('Could not parse response as JSON:', e);
            data = { success: false, error: 'Invalid response format' };
        }
        
        console.log('API Response Status:', response.status);
        console.log('API Response Data:', data);
        
        // For auth endpoints, return data as-is (frontend will check success field)
        if (endpoint.includes('/auth/')) {
            return data;
        }
        
        // For other endpoints, handle errors
        if (!response.ok) {
            const errorMsg = data?.error || data?.message || 'API Error (' + response.status + ')';
            console.error('API Error:', errorMsg);
            // Show toast but return the parsed data so callers can inspect error details
            showToast('Error: ' + errorMsg, 'error');
            return data;
        }
        
        return data;
    } catch (error) {
        console.error('API Exception:', error);
        // Return a structured error object so callers can handle it
        return { success: false, error: 'Connection error: ' + error.message };
    }
}

// ==================== NOTIFICATION ====================

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.zIndex = '10000';
    document.body.appendChild(toast);
    
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Hide and remove toast
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 4000);
}

// ==================== PRODUCT FUNCTIONS ====================

async function loadAppContent() {
    await displayProducts();
    await updateCartCount();
    displayStats();
    updateUserDisplay();
}

async function displayProducts() {
    const result = await apiCall('/products');
    if (!result || !result.products) return;
    
    const productsGrid = document.getElementById('products-grid');
    productsGrid.innerHTML = '';
    
    result.products.forEach(product => {
        const productCard = createProductCard(product);
        productsGrid.appendChild(productCard);
    });
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    // Create contact buttons if contact info available
    let contactButtonsHTML = '';
    if (product.email || product.phone || product.whatsapp || product.instagram) {
        contactButtonsHTML = `
            <div class="contact-buttons-row">
                ${product.whatsapp ? `<button class="contact-btn whatsapp" title="Contact via WhatsApp" onclick="openContactPopup(${product.id}, 'whatsapp', '${product.name.replace(/'/g, "\\'")}')">💬 WhatsApp</button>` : ''}
                ${product.email ? `<button class="contact-btn email" title="Contact via Email" onclick="openContactPopup(${product.id}, 'email', '${product.name.replace(/'/g, "\\'")}')">📧 Email</button>` : ''}
                ${product.phone ? `<button class="contact-btn sms" title="Contact via SMS" onclick="openContactPopup(${product.id}, 'sms', '${product.name.replace(/'/g, "\\'")}')">📱 SMS</button>` : ''}
                ${product.instagram ? `<button class="contact-btn instagram" title="Contact via Instagram" onclick="openContactPopup(${product.id}, 'instagram', '${product.name.replace(/'/g, "\\'")}')">📷 Insta</button>` : ''}
            </div>
        `;
    }
    card.innerHTML = `
        <div class="product-image">
            <img src="https://via.placeholder.com/250?text=${product.name}" alt="${product.name}">
        </div>
        <div class="product-info">
            <h3>${product.name}</h3>
            <p class="seller-name">by ${product.uploader_name || 'Unknown'}</p>
            <p class="category">${product.category}</p>
            <p class="description">${product.description}</p>
            <div class="price">
                ${product.priceType === 'fixed' 
                    ? `$${product.price?.toFixed(2)}` 
                    : `$${product.priceMin?.toFixed(2)} - $${product.priceMax?.toFixed(2)}`}
            </div>
            ${contactButtonsHTML}
            <div class="actions">
                <button class="btn btn-primary" onclick="addToCart(${product.id})">❤️Store Order</button>
                <button class="btn btn-secondary" onclick="viewProduct(${product.id})">View Details</button>
            </div>
        </div>
    `;

    return card;
}

function openContactPopup(productId, method, productName) {
    const message = `Hi I am interested in ${productName}`;
    fetchAndContact(productId, method, message);
}

async function addToCart(productId) {
    if (!currentUser) {
        showToast('Please login first', 'error');
        return;
    }

    const result = await apiCall('/cart', {
        method: 'POST',
        body: JSON.stringify({
            user_id: currentUser.id,
            product_id: productId,
            quantity: 1
        })
    });

    if (result && result.success) {
        showToast('Added to cart!', 'success');
        await updateCartCount();
    }
}

async function updateCartCount() {
    if (!currentUser) return;
    
    const result = await apiCall(`/cart?user_id=${currentUser.id}`);
    if (result && result.items) {
        const count = result.items.length;
        document.getElementById('cart-count').textContent = count;
    }
}

async function viewProduct(productId) {
    const result = await apiCall(`/products/${productId}`);
    if (result && result.product) {
        currentProduct = result.product;
        displayProductModal();
    }
}

function displayProductModal() {
    if (!currentProduct) return;
    
    const modal = document.getElementById('product-modal');
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <div class="modal-body">
                <img src="https://via.placeholder.com/400?text=${currentProduct.name}" alt="${currentProduct.name}">
                <div class="modal-info">
                    <h2>${currentProduct.name}</h2>
                    <p class="seller"><strong>Seller:</strong> ${currentProduct.uploader_name}</p>
                    <p class="category"><strong>Category:</strong> ${currentProduct.category}</p>
                    <p class="description">${currentProduct.description}</p>
                    <div class="price">
                        ${currentProduct.priceType === 'fixed' 
                            ? `<strong>Price:</strong> $${currentProduct.price?.toFixed(2)}` 
                            : `<strong>Price Range:</strong> $${currentProduct.priceMin?.toFixed(2)} - $${currentProduct.priceMax?.toFixed(2)}`}
                    </div>
                    <div class="contact-methods">
                        <strong>Contact:</strong>
                        ${currentProduct.contactMethods?.includes('email') ? `<button class="btn-contact" onclick="contactSeller('email')">📧 Email</button>` : ''}
                        ${currentProduct.contactMethods?.includes('phone') ? `<button class="btn-contact" onclick="contactSeller('phone')">📱 Call</button>` : ''}
                        ${currentProduct.contactMethods?.includes('whatsapp') ? `<button class="btn-contact" onclick="contactSeller('whatsapp')">💬 WhatsApp</button>` : ''}
                    </div>
                    <button class="btn btn-primary" onclick="addToCart(${currentProduct.id})">Add to Cart</button>
                </div>
            </div>
        </div>
    `;
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('product-modal').style.display = 'none';
}

function contactSeller(method) {
    if (!currentProduct) return;
    
    const message = `Hi I am interested in ${currentProduct.name}`;
    
    switch(method) {
        case 'email':
            window.location.href = `mailto:${currentProduct.email}?subject=Interest in ${currentProduct.name}&body=${message}`;
            break;
        case 'phone':
            window.location.href = `tel:${currentProduct.phone}`;
            break;
        case 'sms':
            window.location.href = `sms:${currentProduct.phone}?body=${encodeURIComponent(message)}`;
            break;
        case 'whatsapp':
            const whatsappNumber = currentProduct.whatsapp?.replace(/\D/g, '') || currentProduct.phone?.replace(/\D/g, '');
            if (whatsappNumber) {
                window.location.href = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;
            }
            break;
        case 'instagram':
            if (currentProduct.instagram) {
                window.location.href = `https://instagram.com/${currentProduct.instagram.replace('@', '')}`;
            } else {
                showToast('Instagram not available', 'error');
            }
            break;
    }
}

// ==================== PRODUCT UPLOAD & DELETE ====================

// [Functions moved to SELLER FUNCTIONS section below]

// ==================== CART FUNCTIONS ====================

async function viewCart() {
    showSection('cart');
    if (!currentUser) return;
    
    const result = await apiCall(`/cart?user_id=${currentUser.id}`);
    if (result && result.items) {
        displayCartItems(result.items);
    }
}

function displayCartItems(items) {
    const cartContainer = document.getElementById('cart-items');
    cartContainer.innerHTML = '';
    
    if (items.length === 0) {
        cartContainer.innerHTML = '<p style="color: #999; text-align: center; padding: 2rem;">No favorite items yet. Click the heart icon on products to add them here!</p>';
        return;
    }
    


    items.forEach(item => {
        const cartItem = document.createElement('div');
        cartItem.className = 'favorite-item';
        cartItem.innerHTML = `
            <div class="favorite-item-card">
                <div class="favorite-item-content">
                    <h4>${item.name}</h4>
                    <p class="favorite-item-category">${item.category || 'General'}</p>
                    ${item.price ? `<p class="favorite-item-price">$${typeof item.price === 'number' ? item.price.toFixed(2) : item.price}</p>` : '<p class="favorite-item-price">Price on request</p>'}
                    ${item.description ? `<p class="favorite-item-desc">${item.description.substring(0, 100)}...</p>` : ''}
                </div>
                <div class="favorite-item-actions">
                    <button class="btn btn-small" onclick="contactSellerFromFavorite(${item.id}, 'whatsapp', '${item.name}')">💬 WhatsApp</button>
                    <button class="btn btn-small" onclick="contactSellerFromFavorite(${item.id}, 'email', '${item.name}')">📧 Email</button>
                    <button class="btn btn-small" onclick="contactSellerFromFavorite(${item.id}, 'sms', '${item.name}')">📱 SMS</button>
                    <button class="btn btn-small btn-danger" onclick="removeFromCart(${item.cartItemId || item.id})">Remove</button>
                </div>
            </div>
        `;
        cartContainer.appendChild(cartItem);
    });
}

async function removeFromCart(cartItemId) {
    const result = await apiCall(`/cart/${cartItemId}`, {
        method: 'DELETE'
    });
    
    if (result && result.success) {
        showToast('Removed from favorites', 'success');
        viewCart();
    }
}

function contactSellerFromFavorite(productId, method, productName) {
    // Get the product from the current items
    const cartContainer = document.getElementById('cart-items');
    let product = null;
    
    // Try to find product data from DOM or stored data
    const message = `Hi I am interested in ${productName}`;
    
    switch(method) {
        case 'email':
            // We would need the email, so we'll need to fetch product details
            fetchAndContact(productId, method, message);
            break;
        case 'phone':
        case 'sms':
            fetchAndContact(productId, method, message);
            break;
        case 'whatsapp':
            fetchAndContact(productId, method, message);
            break;
        case 'instagram':
            fetchAndContact(productId, method, message);
            break;
    }
}

async function placeOrder() {
    if (!confirm('Place order for all items in your favorites?')) return;
    if (!currentUser) {
        showToast('Please login first', 'error');
        return;
    }

    const result = await apiCall('/orders', {
        method: 'POST',
        body: JSON.stringify({ user_id: currentUser.id })
    });

    if (result && result.success) {
        showToast('Order placed successfully', 'success');
        // Refresh cart and stats
        await updateCartCount();
        await displayStats();
        viewCart();
    } else {
        showToast(result?.error || 'Failed to place order', 'error');
    }
}

async function fetchAndContact(productId, method, message) {
    try {
        const result = await apiCall(`/products/${productId}`);
        if (result && result.product) {
            const product = result.product;
            
            switch(method) {
                case 'email':
                    if (product.email) {
                        window.location.href = `mailto:${product.email}?subject=Interest in ${product.name}&body=${message}`;
                    } else {
                        showToast('Email not available', 'error');
                    }
                    break;
                case 'phone':
                    if (product.phone) {
                        window.location.href = `tel:${product.phone}`;
                    } else {
                        showToast('Phone not available', 'error');
                    }
                    break;
                case 'sms':
                    if (product.phone) {
                        window.location.href = `sms:${product.phone}?body=${encodeURIComponent(message)}`;
                    } else {
                        showToast('Phone not available', 'error');
                    }
                    break;
                case 'whatsapp':
                    const whatsappNumber = product.whatsapp?.replace(/\D/g, '') || product.phone?.replace(/\D/g, '');
                    if (whatsappNumber) {
                        window.location.href = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;
                    } else {
                        showToast('WhatsApp not available', 'error');
                    }
                    break;
                case 'instagram':
                    if (product.instagram) {
                        window.location.href = `https://instagram.com/${product.instagram.replace('@', '')}`;
                    } else {
                        showToast('Instagram not available', 'error');
                    }
                    break;
            }
        }
    } catch (e) {
        console.error('Error fetching product:', e);
        showToast('Unable to contact seller', 'error');
    }
}

// ==================== SELLER FUNCTIONS ====================

async function viewSellerDashboard() {
    showSection('seller-dashboard');
    
    if (!currentUser || currentUser.role !== 'seller') {
        showToast('Only sellers can access this', 'error');
        showSection('home');
        return;
    }
    
    await loadSellerProducts();
    await loadMySellerAnalytics();
}

async function loadSellerProducts() {
    if (!currentUser) return;
    
    const result = await apiCall(`/seller/${currentUser.id}/products`);
    if (result) {
        displaySellerProducts(result.products || []);
    }
}

function displaySellerProducts(products) {
    const container = document.getElementById('seller-products');
    container.innerHTML = '';
    
    if (products.length === 0) {
        container.innerHTML = '<p>No products listed yet</p>';
    } else {
        products.forEach(product => {
            const productDiv = document.createElement('div');
            productDiv.className = 'seller-product-item';
            productDiv.innerHTML = `
                <h4>${product.name}</h4>
                <p>Category: ${product.category}</p>
                <p>Price: ${product.priceType === 'fixed' ? `$${product.price}` : `$${product.priceMin} - $${product.priceMax}`}</p>
                <div>
                    <button class="btn btn-secondary" onclick="editProduct(${product.id})">Edit</button>
                    <button class="btn btn-danger" onclick="deleteProduct(${product.id})">Delete</button>
                </div>
            `;
            container.appendChild(productDiv);
        });
    }
}

async function uploadProduct(event) {
    event.preventDefault();
    
    if (!currentUser || currentUser.role !== 'seller') {
        showToast('Only sellers can upload products', 'error');
        return;
    }
    
    const product = {
        name: document.getElementById('product-name').value,
        category: document.getElementById('product-category').value,
        description: document.getElementById('product-description').value,
        priceType: document.querySelector('input[name="price-type"]:checked').value,
        price: document.querySelector('input[name="price-type"]:checked').value === 'fixed' 
            ? parseFloat(document.getElementById('product-price').value) 
            : null,
        priceMin: document.querySelector('input[name="price-type"]:checked').value === 'range'
            ? parseFloat(document.getElementById('product-price-min').value)
            : null,
        priceMax: document.querySelector('input[name="price-type"]:checked').value === 'range'
            ? parseFloat(document.getElementById('product-price-max').value)
            : null,
        contactMethods: Array.from(document.querySelectorAll('input[name="contact-method"]:checked')).map(cb => cb.value),
        email: document.getElementById('product-email').value,
        phone: document.getElementById('product-phone').value,
        whatsapp: document.getElementById('product-whatsapp').value,
        instagram: document.getElementById('product-instagram').value || null,
        user_id: currentUser.id
    };
    
    const result = await apiCall('/products', {
        method: 'POST',
        body: JSON.stringify(product)
    });
    
    if (result && result.success) {
        showToast('Product uploaded successfully!', 'success');
        document.getElementById('product-form').reset();
        loadSellerProducts();
    } else {
        showToast(result?.error || 'Failed to upload product', 'error');
    }
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product permanently?')) return;
    
    const result = await apiCall(`/products/${productId}`, {
        method: 'DELETE',
        body: JSON.stringify({ user_id: currentUser.id })
    });
    
    if (result && result.success) {
        showToast('Product deleted permanently', 'success');
        loadSellerProducts();
    } else {
        showToast(result?.error || 'Failed to delete product. You can only delete your own products.', 'error');
    }
}

async function editProduct(productId) {
    const result = await apiCall(`/products/${productId}`);
    if (result && result.product) {
        showEditProductModal(result.product);
    }
}

function showEditProductModal(product) {
    const modal = document.createElement('div');
    modal.className = 'modal edit-product-modal';
    modal.id = 'edit-product-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close" onclick="closeEditModal()">&times;</span>
            <h2>Edit Product</h2>
            <form id="edit-product-form" onsubmit="submitEditProduct(event, ${product.id})">
                <div class="form-group">
                    <label>Product Name *</label>
                    <input type="text" id="edit-product-name" value="${product.name}" required>
                </div>
                <div class="form-group">
                    <label>Category *</label>
                    <select id="edit-product-category" required>
                        <option value="electronics" ${product.category === 'electronics' ? 'selected' : ''}>Electronics</option>
                        <option value="clothing" ${product.category === 'clothing' ? 'selected' : ''}>Clothing</option>
                        <option value="books" ${product.category === 'books' ? 'selected' : ''}>Books</option>
                        <option value="home" ${product.category === 'home' ? 'selected' : ''}>Home & Garden</option>
                        <option value="sports" ${product.category === 'sports' ? 'selected' : ''}>Sports</option>
                        <option value="toys" ${product.category === 'toys' ? 'selected' : ''}>Toys</option>
                        <option value="other" ${product.category === 'other' ? 'selected' : ''}>Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="edit-product-description">${product.description || ''}</textarea>
                </div>
                <div class="form-group">
                    <label>Price Type</label>
                    <input type="radio" name="edit-price-type" value="fixed" ${product.priceType === 'fixed' ? 'checked' : ''}> Fixed Price
                    <input type="radio" name="edit-price-type" value="range" ${product.priceType === 'range' ? 'checked' : ''}> Price Range
                </div>
                <div class="form-group">
                    <label>Price</label>
                    <input type="number" id="edit-product-price" step="0.01" value="${product.price || ''}">
                </div>
                <div class="form-group">
                    <label>Price Range (Min - Max)</label>
                    <input type="number" id="edit-product-price-min" step="0.01" value="${product.priceMin || ''}">
                    <input type="number" id="edit-product-price-max" step="0.01" value="${product.priceMax || ''}">
                </div>
                <div class="form-group">
                    <label>Contact Methods</label>
                    <input type="checkbox" name="edit-contact-method" value="email" ${product.contactMethods?.includes('email') ? 'checked' : ''}> Email
                    <input type="checkbox" name="edit-contact-method" value="phone" ${product.contactMethods?.includes('phone') ? 'checked' : ''}> Phone
                    <input type="checkbox" name="edit-contact-method" value="whatsapp" ${product.contactMethods?.includes('whatsapp') ? 'checked' : ''}> WhatsApp
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="edit-product-email" value="${product.email || ''}">
                </div>
                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" id="edit-product-phone" value="${product.phone || ''}">
                </div>
                <div class="form-group">
                    <label>WhatsApp</label>
                    <input type="tel" id="edit-product-whatsapp" value="${product.whatsapp || ''}">
                </div>
                <button type="submit" class="btn btn-primary">Save Changes</button>
                <button type="button" class="btn btn-secondary" onclick="closeEditModal()">Cancel</button>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
    modal.style.display = 'block';
}

function closeEditModal() {
    const modal = document.getElementById('edit-product-modal');
    if (modal) modal.remove();
}

async function submitEditProduct(event, productId) {
    event.preventDefault();
    
    const product = {
        name: document.getElementById('edit-product-name').value,
        category: document.getElementById('edit-product-category').value,
        description: document.getElementById('edit-product-description').value,
        priceType: document.querySelector('input[name="edit-price-type"]:checked').value,
        price: document.querySelector('input[name="edit-price-type"]:checked').value === 'fixed' 
            ? parseFloat(document.getElementById('edit-product-price').value) 
            : null,
        priceMin: document.querySelector('input[name="edit-price-type"]:checked').value === 'range'
            ? parseFloat(document.getElementById('edit-product-price-min').value)
            : null,
        priceMax: document.querySelector('input[name="edit-price-type"]:checked').value === 'range'
            ? parseFloat(document.getElementById('edit-product-price-max').value)
            : null,
        contactMethods: Array.from(document.querySelectorAll('input[name="edit-contact-method"]:checked')).map(cb => cb.value),
        email: document.getElementById('edit-product-email').value,
        phone: document.getElementById('edit-product-phone').value,
        whatsapp: document.getElementById('edit-product-whatsapp').value,
        user_id: currentUser.id
    };
    
    const result = await apiCall(`/products/${productId}`, {
        method: 'PUT',
        body: JSON.stringify(product)
    });
    
    if (result && result.success) {
        showToast('Product updated successfully!', 'success');
        closeEditModal();
        loadSellerProducts();
    } else {
        showToast(result?.error || 'Failed to update product', 'error');
    }
}

// ==================== ADMIN FUNCTIONS ====================

async function viewAdminPanel() {
    if (!currentUser || currentUser.role !== 'admin') {
        showToast('Only admins can access this', 'error');
        return;
    }
    
    showSection('admin-panel');
    await loadAllSellers();
    await loadAllUsers();
    await loadSellerAnalytics();
}

async function loadAllSellers() {
    const result = await apiCall(`/admin/sellers?admin_id=${currentUser.id}`);
    if (result && result.sellers) {
        displaySellers(result.sellers);
    }
}

function displaySellers(sellers) {
    const container = document.getElementById('sellers-list');
    container.innerHTML = '';
    
    sellers.forEach(seller => {
        const sellerDiv = document.createElement('div');
        sellerDiv.className = 'seller-item';
        sellerDiv.innerHTML = `
            <h4>${seller.shop_name || seller.full_name}</h4>
            <p>Email: ${seller.email}</p>
            <p>Status: ${seller.status}</p>
            <button class="btn btn-secondary" onclick="editSeller(${seller.id})">Edit</button>
            <button class="btn btn-danger" onclick="deleteSeller(${seller.id})">Delete</button>
        `;
        container.appendChild(sellerDiv);
    });
}

async function loadSellerAnalytics() {
    const result = await apiCall(`/admin/seller_analytics?admin_id=${currentUser.id}`);
    if (result && result.analytics) {
        displaySellerAnalytics(result.analytics);
    }
}

function displaySellerAnalytics(rows) {
    const container = document.getElementById('seller-analytics');
    container.innerHTML = '';

    if (!rows || rows.length === 0) {
        container.innerHTML = '<p>No sellers found.</p>';
        return;
    }

    const table = document.createElement('table');
    table.className = 'analytics-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Seller</th>
                <th>Products</th>
                <th>Avg Rating</th>
                <th>Date Joined</th>
                <th>Phone</th>
            </tr>
        </thead>
        <tbody>
            ${rows.map(r => `
                <tr>
                    <td>${r.shop_name || r.username} <div class="muted">${r.email}</div></td>
                    <td>${r.product_count}</td>
                    <td>${r.avg_rating ? r.avg_rating.toFixed(2) : '-'}</td>
                    <td>${r.date_joined || '-'}</td>
                    <td>${r.phone || '-'}</td>
                </tr>
            `).join('')}
        </tbody>
    `;

    container.appendChild(table);
}

async function loadMySellerAnalytics() {
    if (!currentUser) return;
    const result = await apiCall(`/seller/${currentUser.id}/analytics?user_id=${currentUser.id}`);
    if (result && result.analytics) {
        displayMySellerAnalytics(result.analytics);
    }
}

function displayMySellerAnalytics(a) {
    const container = document.getElementById('seller-analytics');
    if (!container) return;

    container.innerHTML = `
        <div class="seller-analytics-card">
            <h3>My Analytics</h3>
            <p><strong>Products:</strong> ${a.product_count}</p>
            <p><strong>Avg Rating:</strong> ${a.avg_rating ? a.avg_rating.toFixed(2) : '-'}</p>
            <p><strong>Date Joined:</strong> ${a.date_joined || '-'}</p>
            <p><strong>Phone:</strong> ${a.phone || '-'}</p>
        </div>
    `;
}

// ------------------- Users (Admin) -------------------

async function loadAllUsers() {
    const result = await apiCall(`/admin/users?admin_id=${currentUser.id}`);
    if (result && result.users) {
        displayUsers(result.users);
    }
}

function displayUsers(users) {
    const container = document.getElementById('users-list');
    container.innerHTML = '';

    users.forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.className = 'seller-item';
        userDiv.innerHTML = `
            <h4>${user.username} ${user.role === 'seller' ? `(<strong>Seller</strong>)` : `(<em>${user.role}</em>)`}</h4>
            <p>Email: ${user.email}</p>
            <p>Full Name: ${user.full_name || '-'}</p>
            <p>Phone: ${user.phone || '-'}</p>
            <div>
                <button class="btn btn-secondary" onclick="showUserModal(${user.id})">View</button>
                ${user.role === 'buyer' ? `<button class="btn btn-primary" onclick="promoteUser(${user.id})">Promote to Seller</button>` : ''}
            </div>
        `;
        container.appendChild(userDiv);
    });
}

async function promoteUser(userId) {
    if (!confirm('Promote this user to a seller?')) return;
    
    const result = await apiCall(`/admin/users/${userId}/promote`, {
        method: 'PUT',
        body: JSON.stringify({ admin_id: currentUser.id })
    });

    if (result && result.success) {
        showToast('User promoted to seller', 'success');
        await loadAllUsers();
        await loadAllSellers();
    } else {
        showToast(result?.error || 'Failed to promote user', 'error');
    }
}

async function showUserModal(userId) {
    const result = await apiCall(`/admin/users/${userId}?admin_id=${currentUser.id}`);
    if (!result || !result.user) {
        showToast('Unable to load user', 'error');
        return;
    }

    const user = result.user;
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'user-modal';

    // If the user is an admin, show an editable form but do not allow delete or role changes
    if (user.role === 'admin') {
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" onclick="closeUserModal()">&times;</span>
                <h2>Edit Admin: ${user.username}</h2>
                <form id="edit-user-form" onsubmit="submitEditUser(event, ${user.id})">
                    <label>Username</label>
                    <input id="edit-user-username" type="text" value="${user.username}" required />

                    <label>Email</label>
                    <input id="edit-user-email" type="email" value="${user.email}" required />

                    <label>Full name</label>
                    <input id="edit-user-fullname" type="text" value="${user.full_name || ''}" />

                    <label>Phone</label>
                    <input id="edit-user-phone" type="text" value="${user.phone || ''}" />

                    <label>Role (admin)</label>
                    <select id="edit-user-role" disabled>
                        <option value="admin" selected>Admin</option>
                    </select>

                    <label>New password (leave blank to keep current)</label>
                    <input id="edit-user-password" type="password" />

                    <p class="muted"><em>Admin accounts cannot be deleted from this panel. Role changes are not allowed here.</em></p>

                    <div class="modal-actions">
                        <button type="submit" class="btn btn-primary">Save</button>
                        ${currentUser && currentUser.id === user.id ? `<button type="button" class="btn btn-warning" onclick="showResetPasswordModal(${user.id})">Reset Password (verify)</button>` : ''}
                        <button type="button" class="btn btn-secondary" onclick="closeUserModal()">Close</button>
                    </div>
                </form>
            </div>
        `;
    } else {
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" onclick="closeUserModal()">&times;</span>
                <h2>Edit User: ${user.username}</h2>
                <form id="edit-user-form" onsubmit="submitEditUser(event, ${user.id})">
                    <label>Username</label>
                    <input id="edit-user-username" type="text" value="${user.username}" required />

                    <label>Email</label>
                    <input id="edit-user-email" type="email" value="${user.email}" required />

                    <label>Full name</label>
                    <input id="edit-user-fullname" type="text" value="${user.full_name || ''}" />

                    <label>Phone</label>
                    <input id="edit-user-phone" type="text" value="${user.phone || ''}" />

                    <label>Role</label>
                    <select id="edit-user-role">
                        <option value="buyer" ${user.role === 'buyer' ? 'selected' : ''}>Buyer</option>
                        <option value="seller" ${user.role === 'seller' ? 'selected' : ''}>Seller</option>
                    </select>

                    <label>New password (leave blank to keep current)</label>
                    <input id="edit-user-password" type="password" />

                    <div class="modal-actions">
                        <button type="submit" class="btn btn-primary">Save</button>
                        <button type="button" class="btn btn-danger" onclick="deleteUser(${user.id})">Delete</button>
                        <button type="button" class="btn btn-secondary" onclick="closeUserModal()">Close</button>
                    </div>
                </form>
            </div>
        `;
    }

    document.body.appendChild(modal);
    modal.classList.add('show');
}

function closeUserModal() {
    const m = document.getElementById('user-modal');
    if (m && m.parentNode) m.parentNode.removeChild(m);
}

async function submitEditUser(event, userId) {
    event.preventDefault();

    const payload = {
        admin_id: currentUser.id,
        username: document.getElementById('edit-user-username').value.trim(),
        email: document.getElementById('edit-user-email').value.trim(),
        full_name: document.getElementById('edit-user-fullname').value.trim(),
        phone: document.getElementById('edit-user-phone').value.trim(),
        role: document.getElementById('edit-user-role').value,
        password: document.getElementById('edit-user-password').value || undefined
    };

    const result = await apiCall(`/admin/users/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(payload)
    });

    if (result && result.success) {
        showToast('User updated', 'success');
        closeUserModal();
        await loadAllUsers();
        await loadAllSellers();
    } else {
        showToast(result?.error || 'Failed to update user', 'error');
    }
}

async function deleteUser(userId) {
    if (!confirm('Delete this user? This is permanent.')) return;

    const result = await apiCall(`/admin/users/${userId}?admin_id=${currentUser.id}`, {
        method: 'DELETE'
    });

    if (result && result.success) {
        showToast('User deleted', 'success');
        closeUserModal();
        await loadAllUsers();
        await loadAllSellers();
    } else {
        showToast(result?.error || 'Failed to delete user', 'error');
    }
}

function showResetPasswordModal(userId) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'reset-password-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close" onclick="closeResetPasswordModal()">&times;</span>
            <h2>Reset Password</h2>
            <form id="reset-password-form" onsubmit="submitResetPassword(event, ${userId})">
                <label>What is your full name?</label>
                <input id="reset-fullname" type="text" required />

                <label>New password</label>
                <input id="reset-new-password" type="password" required />

                <label>Confirm new password</label>
                <input id="reset-confirm-password" type="password" required />

                <div class="modal-actions">
                    <button class="btn btn-primary" type="submit">Reset Password</button>
                    <button type="button" class="btn btn-secondary" onclick="closeResetPasswordModal()">Cancel</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
    modal.classList.add('show');
}

function closeResetPasswordModal() {
    const m = document.getElementById('reset-password-modal');
    if (m && m.parentNode) m.parentNode.removeChild(m);
}

function showMessageModal(productId, recipientId) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'message-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close" onclick="closeMessageModal()">&times;</span>
            <h2>Message Seller</h2>
            <form id="message-form" onsubmit="submitMessage(event, ${productId}, ${recipientId || 'null'})">
                <label>Message</label>
                <textarea id="message-content" required></textarea>
                <div class="modal-actions">
                    <button class="btn btn-primary" type="submit">Send</button>
                    <button class="btn btn-secondary" type="button" onclick="closeMessageModal()">Cancel</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
    modal.classList.add('show');
}

// ...existing code...

async function submitResetPassword(event, userId) {
    event.preventDefault();

    const full_name_answer = document.getElementById('reset-fullname').value.trim();
    const new_password = document.getElementById('reset-new-password').value;
    const confirm = document.getElementById('reset-confirm-password').value;

    if (new_password !== confirm) {
        showToast('Passwords do not match', 'error');
        return;
    }
    if (new_password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }

    const result = await apiCall(`/admin/users/${userId}/reset_password`, {
        method: 'POST',
        body: JSON.stringify({
            admin_id: currentUser.id,
            full_name_answer,
            new_password
        })
    });

    if (result && result.success) {
        showToast('Password reset successfully', 'success');
        closeResetPasswordModal();
        closeUserModal();
    } else {
        showToast(result?.error || 'Failed to reset password', 'error');
    }
}

async function createNewSeller(event) {
    event.preventDefault();

    if (!currentUser || currentUser.role !== 'admin') {
        showToast('Only admin users can create sellers', 'error');
        return;
    }
    
    const seller = {
        username: document.getElementById('new-seller-username').value.trim(),
        email: document.getElementById('new-seller-email').value.trim(),
        full_name: document.getElementById('new-seller-fullname').value.trim(),
        phone: document.getElementById('new-seller-phone').value.trim(),
        shop_name: document.getElementById('new-seller-shopname').value.trim(),
        shop_description: document.getElementById('new-seller-description').value.trim(),
        password: document.getElementById('new-seller-password').value,
        admin_id: currentUser.id
    };
    
    const result = await apiCall('/admin/sellers', {
        method: 'POST',
        body: JSON.stringify(seller)
    });
    
    // apiCall now returns parsed data even on errors
    if (result && result.success) {
        showToast('Seller created successfully!', 'success');
        document.getElementById('create-seller-form').reset();
        await loadAllSellers();
    } else {
        const err = result?.error || result?.message || 'Failed to create seller';
        showToast(err, 'error');
    }
}

async function deleteSeller(sellerId) {
    if (!confirm('Delete this seller and all their products?')) return;
    
    const result = await apiCall(`/admin/sellers/${sellerId}?admin_id=${currentUser.id}`, {
        method: 'DELETE'
    });
    
    if (result && result.success) {
        showToast('Seller deleted', 'success');
        loadAllSellers();
    }
}

async function editSeller(sellerId) {
    const result = await apiCall(`/admin/sellers/${sellerId}`);
    if (result && result.seller) {
        showEditSellerModal(result.seller);
    }
}

function showEditSellerModal(seller) {
    const modal = document.createElement('div');
    modal.className = 'modal edit-seller-modal';
    modal.id = 'edit-seller-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close" onclick="closeEditSellerModal()">&times;</span>
            <h2>Edit Seller</h2>
            <form id="edit-seller-form" onsubmit="submitEditSeller(event, ${seller.id})">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" value="${seller.username}" readonly>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="edit-seller-email" value="${seller.email}" required>
                </div>
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" id="edit-seller-fullname" value="${seller.full_name || ''}">
                </div>
                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" id="edit-seller-phone" value="${seller.phone || ''}">
                </div>
                <div class="form-group">
                    <label>Shop Name</label>
                    <input type="text" id="edit-seller-shopname" value="${seller.shop_name || ''}">
                </div>
                <div class="form-group">
                    <label>Shop Description</label>
                    <textarea id="edit-seller-description">${seller.shop_description || ''}</textarea>
                </div>
                <div class="form-group">
                    <label>Status</label>
                    <select id="edit-seller-status">
                        <option value="active" ${seller.status === 'active' ? 'selected' : ''}>Active</option>
                        <option value="inactive" ${seller.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                        <option value="banned" ${seller.status === 'banned' ? 'selected' : ''}>Banned</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Save Changes</button>
                <button type="button" class="btn btn-secondary" onclick="closeEditSellerModal()">Cancel</button>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
    modal.style.display = 'block';
}

function closeEditSellerModal() {
    const modal = document.getElementById('edit-seller-modal');
    if (modal) modal.remove();
}

async function submitEditSeller(event, sellerId) {
    event.preventDefault();
    
    const seller = {
        email: document.getElementById('edit-seller-email').value,
        full_name: document.getElementById('edit-seller-fullname').value,
        phone: document.getElementById('edit-seller-phone').value,
        shop_name: document.getElementById('edit-seller-shopname').value,
        shop_description: document.getElementById('edit-seller-description').value,
        status: document.getElementById('edit-seller-status').value,
        admin_id: currentUser.id
    };
    
    const result = await apiCall(`/admin/sellers/${sellerId}`, {
        method: 'PUT',
        body: JSON.stringify(seller)
    });
    
    if (result && result.success) {
        showToast('Seller updated successfully!', 'success');
        closeEditSellerModal();
        loadAllSellers();
    } else {
        showToast(result?.error || 'Failed to update seller', 'error');
    }
}

// ==================== UTILITY FUNCTIONS ====================

function updateUserDisplay() {
    if (currentUser) {
        const userDisplay = document.getElementById('user-info');
        if (userDisplay) {
            userDisplay.innerHTML = `
                <span>${currentUser.username} (${currentUser.role})</span>
                <button class="btn btn-secondary" onclick="logout()">Logout</button>
            `;
        }
        
        // Show/hide seller and admin nav items based on role
        const sellerNav = document.getElementById('seller-nav');
        const adminNav = document.getElementById('admin-nav');
        const sellBtn = document.getElementById('sell-btn');
        
        if (sellerNav) {
            sellerNav.style.display = (currentUser.role === 'seller' || currentUser.role === 'admin') ? 'block' : 'none';
        }
        if (adminNav) {
            adminNav.style.display = currentUser.role === 'admin' ? 'block' : 'none';
        }
        if (sellBtn) {
            sellBtn.style.display = (currentUser.role === 'seller' || currentUser.role === 'admin') ? 'block' : 'none';
        }
    }
}

async function displayStats() {
    if (!currentUser) return;
    
    const products = await apiCall('/products');
    const orders = await apiCall(`/orders?user_id=${currentUser.id}`);
    const cart = await apiCall(`/cart?user_id=${currentUser.id}`);
    
    const statsDiv = document.getElementById('stats');
    if (statsDiv) {
        statsDiv.innerHTML = `
            <div class="stat">
                <h3>${products?.products?.length || 0}</h3>
                <p>Products</p>
            </div>
            <div class="stat">
                <h3>${cart?.items?.length || 0}</h3>
                <p>In Cart</p>
            </div>
            <div class="stat">
                <h3>${orders?.orders?.length || 0}</h3>
                <p>Orders</p>
            </div>
        `;
    }
}

function loadDarkMode() {
    if (localStorage.getItem('dark-mode') === 'enabled') {
        document.body.classList.add('dark-mode');
    }
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('dark-mode', 'enabled');
    } else {
        localStorage.removeItem('dark-mode');
    }
}

// ==================== RATINGS ====================

async function loadProductRatings(productId) {
    const result = await apiCall(`/ratings/${productId}`);
    if (result && result.ratings) {
        return result.ratings;
    }
    return [];
}

async function addProductRating(productId) {
    if (!currentUser) {
        showToast('Please login to rate products', 'error');
        return;
    }
    
    const rating = prompt('Rate this product (1-5 stars):');
    if (!rating || rating < 1 || rating > 5) {
        showToast('Please enter a rating between 1-5', 'error');
        return;
    }
    
    const review = prompt('Add a review (optional):');
    
    const result = await apiCall('/ratings', {
        method: 'POST',
        body: JSON.stringify({
            product_id: productId,
            user_id: currentUser.id,
            rating: parseInt(rating),
            review: review || ''
        })
    });
    
    if (result && result.success) {
        showToast('Rating added successfully!', 'success');
        displayProductModal();
    } else {
        showToast('Failed to add rating', 'error');
    }
}

function calculateAverageRating(ratings) {
    if (!ratings || ratings.length === 0) return 0;
    const sum = ratings.reduce((acc, r) => acc + r.rating, 0);
    return (sum / ratings.length).toFixed(1);
}

// ==================== FAVORITES ====================

async function toggleFavorite(productId) {
    if (!currentUser) {
        showToast('Please login to save favorites', 'error');
        return;
    }
    
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    const index = favorites.indexOf(productId);
    
    if (index > -1) {
        favorites.splice(index, 1);
        showToast('Removed from favorites', 'success');
    } else {
        favorites.push(productId);
        showToast('Added to favorites', 'success');
    }
    
    localStorage.setItem('favorites', JSON.stringify(favorites));
}

async function viewFavorites() {
    showSection('favorites');
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    
    const result = await apiCall('/products');
    if (!result || !result.products) return;
    
    const favoriteProducts = result.products.filter(p => favorites.includes(p.id));
    
    const container = document.getElementById('favorites-grid');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (favoriteProducts.length === 0) {
        container.innerHTML = '<p>No favorite products yet</p>';
        return;
    }
    
    favoriteProducts.forEach(product => {
        const productCard = createProductCard(product);
        container.appendChild(productCard);
    });
}

function isFavorite(productId) {
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    return favorites.includes(productId);
}

// ==================== COUPON SYSTEM ====================



function updateCartTotal() {
    const cartTotal = document.getElementById('cart-total');
    if (cartTotal) {
        const currentTotal = parseFloat(cartTotal.textContent.replace('$', ''));
        const discountedTotal = currentTotal * (1 - currentDiscount / 100);
        cartTotal.textContent = `$${discountedTotal.toFixed(2)}`;
        if (currentDiscount > 0) {
            cartTotal.innerHTML += `<p style="font-size: 0.9em; color: green;">Discount: -$${(currentTotal - discountedTotal).toFixed(2)}</p>`;
        }
    }
}

// ==================== USER PROFILE ====================

async function viewProfile() {
    showSection('profile');
    
    if (!currentUser) {
        showToast('Please login first', 'error');
        return;
    }
    
    const result = await apiCall(`/profile?userId=${currentUser.id}`);
    if (result) {
        document.getElementById('profile-name').value = result.name || '';
        document.getElementById('profile-email').value = result.email || '';
        document.getElementById('profile-phone').value = result.phone || '';
        document.getElementById('profile-address').value = result.address || '';
    }
}

async function updateProfile(event) {
    event.preventDefault();
    
    if (!currentUser) {
        showToast('Please login first', 'error');
        return;
    }
    
    const profile = {
        userId: currentUser.id,
        name: document.getElementById('profile-name').value,
        email: document.getElementById('profile-email').value,
        phone: document.getElementById('profile-phone').value,
        address: document.getElementById('profile-address').value,
        darkMode: document.body.classList.contains('dark-mode')
    };
    
    const result = await apiCall('/profile', {
        method: 'POST',
        body: JSON.stringify(profile)
    });
    
    if (result && result.success) {
        showToast('Profile updated successfully!', 'success');
    } else {
        showToast('Failed to update profile', 'error');
    }
}

// ==================== DATA EXPORT/IMPORT ====================

async function exportData() {
    if (!currentUser) {
        showToast('Please login first', 'error');
        return;
    }
    
    const result = await apiCall(`/export?user_id=${currentUser.id}`);
    if (result && result.data) {
        const dataStr = JSON.stringify(result.data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `shop-pro-backup-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        showToast('Data exported successfully!', 'success');
    } else {
        showToast('Failed to export data', 'error');
    }
}

async function importData(event) {
    if (!currentUser) {
        showToast('Please login first', 'error');
        return;
    }
    
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = async function(e) {
        try {
            const data = JSON.parse(e.target.result);
            const result = await apiCall('/import', {
                method: 'POST',
                body: JSON.stringify({ user_id: currentUser.id, data: data })
            });
            
            if (result && result.success) {
                showToast('Data imported successfully!', 'success');
                location.reload();
            } else {
                showToast('Failed to import data', 'error');
            }
        } catch (error) {
            showToast('Invalid file format', 'error');
        }
    };
    reader.readAsText(file);
}

async function loadAllProducts() {
    const result = await apiCall('/products');
    if (result && result.products) {
        allProducts = result.products;
    }
}

function filterProducts() {
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
    const categoryFilter = document.getElementById('category-filter')?.value || '';
    
    let filtered = allProducts;
    // Filter by search term
    if (searchTerm) {
        filtered = filtered.filter(p => 
            p.name.toLowerCase().includes(searchTerm) ||
            p.description.toLowerCase().includes(searchTerm)
        );
    }
    // Filter by category (case-insensitive, robust)
    if (categoryFilter) {
        filtered = filtered.filter(p => {
            if (!p.category) return false;
            return String(p.category).toLowerCase() === String(categoryFilter).toLowerCase();
        });
    }
    // Now apply sort
    const sortBy = document.getElementById('sort-filter')?.value || 'newest';
    switch(sortBy) {
        case 'newest':
            filtered.sort((a, b) => {
                const dateA = b.createdAt ? new Date(b.createdAt) : 0;
                const dateB = a.createdAt ? new Date(a.createdAt) : 0;
                return dateA - dateB;
            });
            break;
        case 'price-low':
            filtered.sort((a, b) => {
                const priceA = a.priceType === 'fixed' ? a.price : a.priceMin;
                const priceB = b.priceType === 'fixed' ? b.price : b.priceMin;
                return priceA - priceB;
            });
            break;
        case 'price-high':
            filtered.sort((a, b) => {
                const priceA = a.priceType === 'fixed' ? a.price : a.priceMax || a.price;
                const priceB = b.priceType === 'fixed' ? b.price : b.priceMax || b.price;
                return priceB - priceA;
            });
            break;
    }
    displayFilteredProducts(filtered);
}

function sortProducts() {
    // Always apply filters before sorting
    filterProducts();
}

function displayFilteredProducts(products) {
    const productsGrid = document.getElementById('products-grid');
    productsGrid.innerHTML = '';
    
    if (products.length === 0) {
        productsGrid.innerHTML = '<p>No products found</p>';
        return;
    }
    
    products.forEach(product => {
        const productCard = createProductCard(product);
        productsGrid.appendChild(productCard);
    });
}

// Update displayProducts to also load allProducts
async function displayProducts() {
    const result = await apiCall('/products');
    if (!result || !result.products) return;
    
    allProducts = result.products;
    
    const productsGrid = document.getElementById('products-grid');
    productsGrid.innerHTML = '';
    
    result.products.forEach(product => {
        const productCard = createProductCard(product);
        productsGrid.appendChild(productCard);
    });
}
