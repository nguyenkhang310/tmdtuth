import os

html_path = 'templates/products.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace product grid
start_marker = "<!-- Card 1 -->"
end_marker = "</div>\n<!-- Pagination -->"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    before = content[:start_idx]
    after = content[end_idx:]
    
    jinja_loop = """{% for product in products %}
<!-- Product Card -->
<div class="group relative">
<div class="relative overflow-hidden rounded-lg aspect-[3/4] bg-surface-container-highest">
<img class="object-cover w-full h-full transition-transform duration-700 group-hover:scale-110" src="{{ product.image_url }}" alt="{{ product.name }}"/>
<div class="absolute top-4 right-4 z-10">
<button class="w-10 h-10 rounded-full bg-white/80 backdrop-blur-sm flex items-center justify-center text-on-surface-variant hover:text-secondary hover:bg-white transition-all shadow-sm">
<span class="material-symbols-outlined" data-icon="favorite">favorite</span>
</button>
</div>
<div class="absolute bottom-0 left-0 right-0 p-4 translate-y-full group-hover:translate-y-0 transition-transform duration-300 bg-gradient-to-t from-black/60 to-transparent">
<a href="{{ url_for('product_detail', product_id=product.id) }}" class="block text-center w-full py-3 bg-primary text-on-primary rounded-full font-bold text-sm tracking-wide">Xem chi tiết</a>
</div>
{% if product.is_on_sale %}
<div class="absolute top-4 left-4">
<span class="bg-secondary text-on-secondary px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter">Sale</span>
</div>
{% endif %}
</div>
<div class="mt-4 space-y-1">
<p class="text-[10px] text-tertiary font-bold uppercase tracking-widest">{{ product.category.name if product.category else 'Store' }}</p>
<h4 class="font-headline font-semibold text-primary truncate">{{ product.name }}</h4>
<div class="flex items-center gap-3">
<span class="text-secondary font-headline font-bold">{{ "{:0,.0f}".format(product.price) }}đ</span>
{% if product.old_price %}
<span class="text-xs text-outline line-through">{{ "{:0,.0f}".format(product.old_price) }}đ</span>
{% endif %}
</div>
</div>
</div>
{% endfor %}
"""
    content = before + jinja_loop + after

# Rewrite Top Nav Buttons as we did for index.html
nav_buttons = """<button class="material-symbols-outlined text-teal-900 dark:text-teal-500 hover:scale-95 active:scale-90 transition-transform" onclick="window.location.href='cart.html'" data-icon="shopping_cart">shopping_cart</button>
<button class="material-symbols-outlined text-teal-900 dark:text-teal-500 hover:scale-95 active:scale-90 transition-transform" onclick="window.location.href='login.html'" data-icon="account_circle">account_circle</button>"""

new_nav_buttons = """<a href="{{ url_for('cart') }}" class="material-symbols-outlined text-teal-900 dark:text-teal-500 hover:scale-95 active:scale-90 transition-transform hover:text-primary">shopping_cart</a>
{% if current_user.is_authenticated %}
    {% if current_user.role == 'admin' %}
        <a href="{{ url_for('admin_dashboard') }}" class="material-symbols-outlined text-teal-900 dark:text-teal-500 hover:scale-95 active:scale-90 transition-transform hover:text-primary">admin_panel_settings</a>
    {% endif %}
    <a href="{{ url_for('logout') }}" class="material-symbols-outlined text-teal-900 dark:text-teal-500 hover:scale-95 active:scale-90 transition-transform hover:text-primary">logout</a>
{% else %}
    <a href="{{ url_for('login') }}" class="material-symbols-outlined text-teal-900 dark:text-teal-500 hover:scale-95 active:scale-90 transition-transform hover:text-primary">account_circle</a>
{% endif %}"""

content = content.replace(nav_buttons, new_nav_buttons)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("products.html template updated.")
