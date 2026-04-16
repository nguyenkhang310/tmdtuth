document.addEventListener('DOMContentLoaded', () => {
    
    if (!document.getElementById('cart-items-container')) return;

    renderCart();

    function renderCart() {
        const cart = window.getCart();
        const container = document.getElementById('cart-items-container');
        const emptyState = document.getElementById('empty-cart');
        const contentState = document.getElementById('cart-content');

        if (cart.length === 0) {
            emptyState.classList.remove('hidden');
            emptyState.classList.add('flex');
            contentState.classList.add('hidden');
            return;
        }

        emptyState.classList.add('hidden');
        emptyState.classList.remove('flex');
        contentState.classList.remove('hidden');

        container.innerHTML = cart.map((item, index) => `
            <div class="grid grid-cols-1 sm:grid-cols-12 gap-4 items-center pb-6 border-b border-surface-variant">
                <!-- Product Info -->
                <div class="sm:col-span-6 flex gap-4">
                    <img src="${item.image}" class="w-24 h-32 object-cover rounded-lg bg-surface-container-high" alt="${item.name}">
                    <div class="flex flex-col justify-center">
                        <a href="product-detail.html?id=${item.id}" class="font-headline font-bold text-on-surface hover:text-primary transition-colors text-lg">${item.name}</a>
                        <div class="text-sm text-on-surface-variant mt-1 flex flex-wrap gap-x-3 gap-y-1">
                            ${item.size ? `<span>Size: <span class="font-bold text-on-surface">${item.size}</span></span>` : ''}
                            ${item.color ? `<span class="flex items-center gap-1">Màu: <span class="w-4 h-4 inline-block rounded-full border border-outline-variant" style="background-color: ${item.color}"></span></span>` : ''}
                        </div>
                        <div class="font-bold mt-2 sm:hidden text-primary">${formatCurrency(item.price)}</div>
                    </div>
                </div>

                <!-- Qty Control -->
                <div class="sm:col-span-3 flex justify-center">
                    <div class="flex items-center border border-outline-variant rounded-lg overflow-hidden bg-surface h-10 w-28">
                        <button class="w-8 h-full hover:bg-surface-container-high transition-colors text-on-surface-variant btn-decrease" data-index="${index}"><span class="material-symbols-outlined text-sm">remove</span></button>
                        <input type="number" readonly value="${item.quantity}" class="w-full h-full text-center border-none focus:ring-0 font-bold bg-transparent text-sm">
                        <button class="w-8 h-full hover:bg-surface-container-high transition-colors text-on-surface-variant btn-increase" data-index="${index}"><span class="material-symbols-outlined text-sm">add</span></button>
                    </div>
                </div>

                <!-- Line Total -->
                <div class="sm:col-span-2 text-right hidden sm:block font-bold text-primary text-lg">
                    ${formatCurrency(item.price * item.quantity)}
                </div>

                <!-- Delete Action -->
                <div class="sm:col-span-1 text-right sm:text-center mt-2 sm:mt-0">
                    <button class="text-error opacity-70 hover:opacity-100 hover:scale-110 btn-delete transition-all" data-index="${index}" title="Xóa khỏi giỏ hàng">
                        <span class="material-symbols-outlined">delete</span>
                    </button>
                </div>
            </div>
        `).join('');

        attachCartEvents();
        updateSummary(cart);
    }

    function attachCartEvents() {
        document.querySelectorAll('.btn-decrease').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.currentTarget.dataset.index;
                updateItemQty(idx, -1);
            });
        });

        document.querySelectorAll('.btn-increase').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.currentTarget.dataset.index;
                updateItemQty(idx, 1);
            });
        });

        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.currentTarget.dataset.index;
                removeItem(idx);
            });
        });
    }

    function updateItemQty(index, change) {
        const cart = window.getCart();
        if (cart[index]) {
            cart[index].quantity += change;
            if (cart[index].quantity <= 0) {
                cart[index].quantity = 1; // Minimum 1, use delete for 0
            }
            saveCart(cart);
            renderCart();
            window.updateCartCount(); // from main.js
        }
    }

    function removeItem(index) {
        const cart = window.getCart();
        if (cart[index]) {
            const confirmed = confirm(`Bạn có chắc muốn xóa "${cart[index].name}" khỏi giỏ hàng?`);
            if (confirmed) {
                cart.splice(index, 1);
                saveCart(cart);
                renderCart();
                window.updateCartCount();
                showNotification("Đã xóa sản phẩm khỏi giỏ hàng.");
            }
        }
    }

    function saveCart(cart) {
        localStorage.setItem('uthstore_cart', JSON.stringify(cart));
    }

    function updateSummary(cart) {
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        document.getElementById('summary-subtotal').textContent = formatCurrency(total);
        document.getElementById('summary-total').textContent = formatCurrency(total);
        
        // Shipping logic could be added here
        const shippingEl = document.getElementById('summary-shipping');
        if (total < 1000000 && cart.length > 0) {
            shippingEl.textContent = '35.000đ';
            document.getElementById('summary-total').textContent = formatCurrency(total + 35000);
        } else if (cart.length > 0) {
            shippingEl.textContent = 'Miễn phí';
            document.getElementById('summary-total').textContent = formatCurrency(total);
        }
    }
});
