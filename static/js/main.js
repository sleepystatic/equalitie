// ==================== DARK MODE TOGGLE ====================
const themeToggle = document.getElementById('theme-toggle');
const moonIcon = document.getElementById('moon-icon');
const sunIcon = document.getElementById('sun-icon');
const body = document.body;

// Check for saved theme preference or default to light mode
const currentTheme = localStorage.getItem('theme') || 'light';
if (currentTheme === 'dark') {
    body.classList.add('dark-mode');
    moonIcon.style.display = 'none';
    sunIcon.style.display = 'block';
}

themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');

    if (body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
        moonIcon.style.display = 'none';
        sunIcon.style.display = 'block';
    } else {
        localStorage.setItem('theme', 'light');
        moonIcon.style.display = 'block';
        sunIcon.style.display = 'none';
    }
});

// ==================== HEADER SCROLL BEHAVIOR ====================
const header = document.getElementById('main-header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 0) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
});

// ==================== CART FUNCTIONALITY ====================
const cartToggle = document.getElementById('cart-toggle');
const cartSidebar = document.getElementById('cart-sidebar');
const cartClose = document.getElementById('cart-close');
const cartOverlay = document.querySelector('.cart-overlay');
const cartCount = document.getElementById('cart-count');
const cartSidebarCount = document.getElementById('cart-sidebar-count');
const cartItemsContainer = document.getElementById('cart-items-container');
const cartEmpty = document.getElementById('cart-empty');
const cartSummary = document.getElementById('cart-summary');
const cartSubtotal = document.getElementById('cart-subtotal');

// Open cart
cartToggle.addEventListener('click', () => {
    cartSidebar.classList.add('active');
    loadCart();
});

// Close cart
cartClose.addEventListener('click', () => {
    cartSidebar.classList.remove('active');
});

cartOverlay.addEventListener('click', () => {
    cartSidebar.classList.remove('active');
});

// Load cart items
async function loadCart() {
    try {
        const response = await fetch('/cart/items');
        const data = await response.json();

        updateCartDisplay(data);
    } catch (error) {
        console.error('Error loading cart:', error);
    }
}

// Update cart display
function updateCartDisplay(data) {
    const { items, subtotal, count } = data;

    // Update counts
    cartCount.textContent = count;
    cartSidebarCount.textContent = count;

    if (count === 0) {
        cartItemsContainer.innerHTML = '';
        cartEmpty.style.display = 'block';
        cartSummary.style.display = 'none';
    } else {
        cartEmpty.style.display = 'none';
        cartSummary.style.display = 'block';

        // Render cart items
        cartItemsContainer.innerHTML = items.map(item => `
            <div class="cart-item" data-item-id="${item.id}">
                <div class="cart-item-header">
                    <span class="cart-item-name">${item.product.name}</span>
                    <button class="remove-item" onclick="removeFromCart(${item.id})">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                <p class="cart-item-size">Size: ${item.size}</p>
                <p class="cart-item-price">$${item.total.toFixed(2)}</p>
            </div>
        `).join('');

        // Update subtotal
        cartSubtotal.textContent = `$${subtotal.toFixed(2)}`;
    }
}

// Remove item from cart
async function removeFromCart(itemId) {
    try {
        const response = await fetch(`/cart/remove/${itemId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            loadCart();
        }
    } catch (error) {
        console.error('Error removing item:', error);
    }
}

// Update cart count on page load
async function updateCartCount() {
    try {
        const response = await fetch('/cart/count');
        const data = await response.json();
        cartCount.textContent = data.count;
    } catch (error) {
        console.error('Error updating cart count:', error);
    }
}

// Initialize cart count
updateCartCount();

// ==================== PRODUCT MODAL ====================
const productModal = document.getElementById('product-modal');
const modalOverlay = document.querySelector('.modal-overlay');
const modalClose = document.querySelector('.modal-close');
const modalProductImage = document.getElementById('modal-product-image');
const modalProductName = document.getElementById('modal-product-name');
const modalProductPrice = document.getElementById('modal-product-price');
const modalProductDescription = document.getElementById('modal-product-description');
const modalSizeOptions = document.getElementById('modal-size-options');
const modalAddToCart = document.getElementById('modal-add-to-cart');

let currentProduct = null;
let selectedSize = null;

// Open product modal
document.addEventListener('click', async (e) => {
    const productCard = e.target.closest('.product-card');
    if (productCard) {
        const productId = productCard.dataset.productId;
        await openProductModal(productId);
    }
});

async function openProductModal(productId) {
    try {
        const response = await fetch(`/product/${productId}`);
        const product = await response.json();

        currentProduct = product;
        selectedSize = null;

        // Populate modal
        modalProductImage.src = `/static/images/${product.images[0]}`;
        modalProductImage.alt = product.name;
        modalProductName.textContent = product.name;
        modalProductPrice.innerHTML = `
            <span class="original-price">$${product.price.toFixed(2)}</span>
            <span class="sale-price">$${product.sale_price.toFixed(2)}</span>
        `;
        modalProductDescription.textContent = product.description;

        // Render size options
        modalSizeOptions.innerHTML = product.sizes.map(size => `
            <button class="size-btn" data-size="${size}">${size}</button>
        `).join('');

        // Reset add to cart button
        modalAddToCart.disabled = true;

        // Show modal
        productModal.classList.add('active');
    } catch (error) {
        console.error('Error loading product:', error);
    }
}

// Close modal
modalClose.addEventListener('click', () => {
    productModal.classList.remove('active');
});

modalOverlay.addEventListener('click', () => {
    productModal.classList.remove('active');
});

// Size selection
modalSizeOptions.addEventListener('click', (e) => {
    if (e.target.classList.contains('size-btn')) {
        // Remove selected class from all buttons
        document.querySelectorAll('.size-btn').forEach(btn => {
            btn.classList.remove('selected');
        });

        // Add selected class to clicked button
        e.target.classList.add('selected');
        selectedSize = e.target.dataset.size;

        // Enable add to cart button
        modalAddToCart.disabled = false;
    }
});

// Add to cart
modalAddToCart.addEventListener('click', async () => {
    if (!currentProduct || !selectedSize) return;

    try {
        const response = await fetch('/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: currentProduct.id,
                size: selectedSize
            })
        });

        const data = await response.json();

        if (data.success) {
            // Update cart count
            cartCount.textContent = data.cart_count;

            // Close modal
            productModal.classList.remove('active');

            // Show brief confirmation (optional)
            console.log('Item added to cart');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
    }
});

// ==================== SCROLL ANIMATIONS ====================
// Fade in up animation for products
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all product cards
document.querySelectorAll('.fade-in-up').forEach(card => {
    observer.observe(card);
});

// ==================== NEWSLETTER FORM ====================
const newsletterForm = document.querySelector('.newsletter-form');
if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = newsletterForm.querySelector('input').value;

        // TODO: Implement newsletter signup
        console.log('Newsletter signup:', email);

        // Clear form
        newsletterForm.reset();

        // Show confirmation (you can customize this)
        alert('Thank you for subscribing!');
    });
}

// ==================== UTILITY FUNCTIONS ====================
// Format price
function formatPrice(price) {
    return `$${price.toFixed(2)}`;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ==================== KEYBOARD ACCESSIBILITY ====================
// Close modals with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (productModal.classList.contains('active')) {
            productModal.classList.remove('active');
        }
        if (cartSidebar.classList.contains('active')) {
            cartSidebar.classList.remove('active');
        }
    }
});

// ==================== SMOOTH SCROLLING ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

console.log('Equalitie - Site loaded successfully');