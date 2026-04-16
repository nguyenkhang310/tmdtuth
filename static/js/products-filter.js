document.addEventListener('DOMContentLoaded', () => {
    // Only run if on products page
    if (!document.getElementById('products-grid-container')) return;

    const filterForm = document.getElementById('filter-form');
    const sortSelect = document.getElementById('sort-select');
    const resetBtn = document.getElementById('reset-filter');

    // Parse URL params for initial category
    const urlParams = new URLSearchParams(window.location.search);
    const initialCategory = urlParams.get('category');
    const isSale = urlParams.get('sale');

    if (initialCategory) {
        const catRadio = filterForm.querySelector(`input[name="category"][value="${initialCategory}"]`);
        if (catRadio) catRadio.checked = true;
    }
    
    // Initial Render
    renderFilteredProducts();

    // Event Listeners for Filters
    filterForm.addEventListener('change', renderFilteredProducts);
    sortSelect.addEventListener('change', renderFilteredProducts);
    resetBtn.addEventListener('click', () => {
        // Reset custom radio buttons
        filterForm.querySelector('input[name="category"][value="all"]').checked = true;
        filterForm.querySelector('input[name="price"][value="all"]').checked = true;
        const sizeCheckboxes = filterForm.querySelectorAll('input[name="size"]');
        sizeCheckboxes.forEach(cb => cb.checked = false);
        renderFilteredProducts();
    });

    function renderFilteredProducts() {
        const container = document.getElementById('products-grid-container');
        const countDisplay = document.getElementById('product-count');
        
        // 1. Get filter values
        const category = filterForm.querySelector('input[name="category"]:checked').value;
        const priceRange = filterForm.querySelector('input[name="price"]:checked').value;
        
        const sizeNodes = filterForm.querySelectorAll('input[name="size"]:checked');
        const sizes = Array.from(sizeNodes).map(node => node.value);
        
        const sortBy = sortSelect.value;

        // 2. Filter products array
        let filtered = products.filter(product => {
            // Category Filter
            if (category !== 'all' && !product.categories?.includes(category) && product.category !== category) return false;
            
            // Only Sale
            if (isSale === 'true' && !product.isSale) return false;

            // Price Filter
            if (priceRange !== 'all') {
                const [min, max] = priceRange.split('-');
                const p = product.price;
                if (max === 'max') {
                    if (p < parseInt(min)) return false;
                } else {
                    if (p < parseInt(min) || p > parseInt(max)) return false;
                }
            }

            // Size Filter
            if (sizes.length > 0) {
                // If product doesn't have ANY of the selected sizes
                if (!product.sizes) return false;
                const hasSize = sizes.some(s => product.sizes.includes(s));
                if (!hasSize) return false;
            }

            return true;
        });

        // 3. Sort
        if (sortBy === 'price-asc') {
            filtered.sort((a, b) => a.price - b.price);
        } else if (sortBy === 'price-desc') {
            filtered.sort((a, b) => b.price - a.price);
        } // 'newest' keeps original order for now

        // 4. Update UI title conditionally 
        updatePageTitle(category, isSale);

        // 5. Render
        countDisplay.textContent = filtered.length;
        
        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="col-span-full py-12 text-center text-on-surface-variant flex flex-col items-center justify-center">
                    <span class="material-symbols-outlined text-6xl mb-4 opacity-50">search_off</span>
                    <h3 class="text-xl font-bold mb-2">Không tìm thấy sản phẩm nào</h3>
                    <p>Vui lòng thử thay đổi bộ lọc hoặc xem tất cả danh mục.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = filtered.map(product => {
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
                    <div class="absolute bottom-4 right-4 translate-y-12 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 z-10">
                        <button class="add-to-cart-quick w-12 h-12 rounded-full bg-white text-primary flex items-center justify-center shadow-xl hover:bg-primary-container hover:text-white transition-colors" onclick="event.stopPropagation(); window.addToCart('${product.id}')">
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

    function updatePageTitle(category, isSale) {
        const titleEl = document.getElementById('page-title');
        if (isSale === 'true') {
            titleEl.textContent = 'Sản Phẩm Khuyến Mãi';
            return;
        }
        const mapping = {
            'all': 'Tất Cả Sản Phẩm',
            'ao': 'Áo Thời Trang',
            'quan': 'Quần Hiện Đại',
            'vay': 'Váy Sinh Viên',
            'dam': 'Đầm Thanh Lịch',
            'phu-kien': 'Phụ Kiện'
        };
        titleEl.textContent = mapping[category] || 'Tất Cả Sản Phẩm';
    }
});
