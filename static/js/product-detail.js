document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');

    const container = document.getElementById('product-detail-container');
    const notFound = document.getElementById('product-not-found');

    if (!productId) {
        showNotFound();
        return;
    }

    const product = products.find(p => p.id === productId);

    if (!product) {
        showNotFound();
        return;
    }

    // State
    let selectedSize = product.sizes ? product.sizes[0] : null;
    let selectedColor = product.colors ? product.colors[0] : null;
    let quantity = 1;

    renderProductInfo(product);

    function showNotFound() {
        container.classList.add('hidden');
        notFound.classList.remove('hidden');
    }

    function renderProductInfo(p) {
        container.classList.remove('hidden');

        // Text & Links
        document.getElementById('pd-name').textContent = p.name;
        document.getElementById('pd-name-breadcrumb').textContent = p.name;
        document.getElementById('pd-image').src = p.image;
        
        document.getElementById('pd-price').textContent = formatCurrency(p.price);
        if (p.originalPrice && p.originalPrice > p.price) {
            const org = document.getElementById('pd-original-price');
            org.textContent = formatCurrency(p.originalPrice);
            org.classList.remove('hidden');
        }

        // Generate Colors
        if (p.colors && p.colors.length > 0) {
            const colorContainer = document.getElementById('pd-colors');
            colorContainer.innerHTML = p.colors.map(col => `
                <button class="w-10 h-10 rounded-full border-2 focus:outline-none transition-transform color-btn" 
                        style="background-color: ${col}; ${col === '#FFFFFF' ? 'border-color: #bdc9c8;' : 'border-color: transparent;'}"
                        data-color="${col}">
                </button>
            `).join('');
            
            // Set first color active
            updateActiveColor(selectedColor);

            document.querySelectorAll('.color-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    selectedColor = e.target.dataset.color;
                    updateActiveColor(selectedColor);
                });
            });
        }

        // Generate Sizes
        if (p.sizes && p.sizes.length > 0) {
            const sizeContainer = document.getElementById('pd-sizes');
            sizeContainer.innerHTML = p.sizes.map(s => `
                <button class="min-w-[3rem] px-3 h-12 border border-outline-variant rounded-lg font-bold transition-colors size-btn"
                        data-size="${s}">
                    ${s}
                </button>
            `).join('');

            updateActiveSize(selectedSize);

            document.querySelectorAll('.size-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    selectedSize = e.target.dataset.size;
                    updateActiveSize(selectedSize);
                });
            });
        }

        // Qty logic
        const qtyInput = document.getElementById('pd-qty');
        document.getElementById('btn-minus').addEventListener('click', () => {
            if (quantity > 1) {
                quantity--;
                qtyInput.value = quantity;
            }
        });
        document.getElementById('btn-plus').addEventListener('click', () => {
            quantity++;
            qtyInput.value = quantity;
        });
        qtyInput.addEventListener('change', (e) => {
            const val = parseInt(e.target.value);
            if (val > 0) {
                quantity = val;
            } else {
                qtyInput.value = quantity;
            }
        });

        // Add to cart
        document.getElementById('btn-add-to-cart').addEventListener('click', () => {
            window.addToCart(p.id, quantity, selectedSize, selectedColor);
        });

        // Show gently
        setTimeout(() => {
            container.classList.remove('opacity-0');
        }, 50);
    }

    function updateActiveColor(color) {
        document.querySelectorAll('.color-btn').forEach(btn => {
            if(btn.dataset.color === color) {
                btn.classList.add('ring-2', 'ring-offset-2', 'ring-primary', 'scale-110');
            } else {
                btn.classList.remove('ring-2', 'ring-offset-2', 'ring-primary', 'scale-110');
            }
        });
    }

    function updateActiveSize(size) {
        document.querySelectorAll('.size-btn').forEach(btn => {
            if(btn.dataset.size === size) {
                btn.classList.add('bg-primary', 'text-white', 'border-primary');
                btn.classList.remove('text-on-surface');
            } else {
                btn.classList.remove('bg-primary', 'text-white', 'border-primary');
                btn.classList.add('text-on-surface');
            }
        });
    }
});
