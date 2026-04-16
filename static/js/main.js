// Main JavaScript for UTH Store
document.addEventListener('DOMContentLoaded', () => {
    initCart();
    renderNewArrivals();
    setupEventListeners();
});

// Cart Logic
function initCart() {
    updateCartCount();
}

function getCart() {
    const cart = localStorage.getItem('uthstore_cart');
    return cart ? JSON.parse(cart) : [];
}

function updateCartCount() {
    const cart = getCart();
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    const cartCountElements = document.querySelectorAll('#cart-count');
    cartCountElements.forEach(el => {
        el.textContent = count;
        // Animation effect
        el.classList.add('scale-150');
        setTimeout(() => el.classList.remove('scale-150'), 200);
    });
}

function addToCart(productId, quantity = 1, size = null, color = null) {
    const cart = getCart();
    const product = products.find(p => p.id === productId);
    
    if (!product) return false;
    
    // Default variations if none provided
    if (!size && product.sizes) size = product.sizes[0];
    if (!color && product.colors) color = product.colors[0];

    const existingItemIndex = cart.findIndex(item => 
        item.id === productId && item.size === size && item.color === color
    );
    
    if (existingItemIndex > -1) {
        cart[existingItemIndex].quantity += quantity;
    } else {
        cart.push({
            id: productId,
            name: product.name,
            price: product.price,
            image: product.image,
            size: size,
            color: color,
            quantity: quantity
        });
    }
    
    localStorage.setItem('uthstore_cart', JSON.stringify(cart));
    updateCartCount();
    showNotification(`Đã thêm ${product.name} vào giỏ hàng!`);
    return true;
}

// Notification System
function showNotification(message) {
    // Create notification element if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed bottom-6 right-6 z-[100] flex flex-col gap-2';
        document.body.appendChild(container);
    }
    
    const notification = document.createElement('div');
    notification.className = 'bg-surface-tint text-white px-6 py-3 rounded-lg shadow-xl translate-y-10 opacity-0 transition-all duration-300 flex items-center gap-3';
    notification.innerHTML = `
        <span class="material-symbols-outlined text-tertiary">check_circle</span>
        <span class="font-medium">${message}</span>
    `;
    
    container.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => {
        notification.classList.remove('translate-y-10', 'opacity-0');
    }, 10);
    
    // Remove after 3s
    setTimeout(() => {
        notification.classList.add('opacity-0', 'translate-x-10');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Render Products on Home Page
function renderNewArrivals() {
    const container = document.getElementById('new-arrivals-container');
    if (!container) return; // Not on home page
    
    const newProducts = products.slice(0, 4); // Just take first 4 for demo
    
    container.innerHTML = newProducts.map(product => {
        const hasDiscount = product.originalPrice && product.originalPrice > product.price;
        const discountBadge = product.discountLabel ? 
            `<div class="absolute top-4 left-4 bg-tertiary text-on-tertiary px-4 py-1 rounded-full text-xs font-black uppercase tracking-widest">${product.discountLabel}</div>` : 
            (product.isNew ? `<div class="absolute top-4 left-4 bg-secondary text-white px-4 py-1 rounded-full text-xs font-black uppercase tracking-widest">New</div>` : '');
            
        const originalPriceHtml = hasDiscount ? `<span class="text-on-surface-variant/50 line-through text-sm">${formatCurrency(product.originalPrice)}</span>` : '';
        
        return `
        <div class="group h-full flex flex-col">
            <div class="relative overflow-hidden rounded-xl mb-4 bg-surface-container-low aspect-[3/4] block group cursor-pointer" onclick="window.location.href='product-detail.html?id=${product.id}'">
                <img alt="${product.name}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" src="${product.image}"/>
                ${discountBadge}
                
                <!-- Quick action: Add to cart overlay -->
                <div class="absolute bottom-4 right-4 translate-y-12 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 z-10">
                    <button class="add-to-cart-quick w-12 h-12 rounded-full bg-white text-primary flex items-center justify-center shadow-xl hover:bg-primary-container hover:text-white transition-colors" data-id="${product.id}" onclick="event.stopPropagation(); window.addToCart('${product.id}')">
                        <span class="material-symbols-outlined">add_shopping_cart</span>
                    </button>
                </div>
            </div>
            <h3 class="font-headline font-bold text-lg mb-1 leading-tight"><a href="product-detail.html?id=${product.id}" class="hover:text-primary transition-colors">${product.name}</a></h3>
            <div class="flex items-center gap-3 mt-auto pt-2">
                <span class="text-secondary font-black text-xl">${formatCurrency(product.price)}</span>
                ${originalPriceHtml}
            </div>
        </div>
        `;
    }).join('');
}

function setupEventListeners() {
    // Make nav glass-nav change opacity on scroll
    const nav = document.getElementById('main-nav');
    if (nav) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                nav.classList.add('shadow-md');
                nav.classList.remove('py-4');
            } else {
                nav.classList.remove('shadow-md');
            }
        });
    }
}
