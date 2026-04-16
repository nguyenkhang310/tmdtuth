import os
import re

html_path = 'templates/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace "Hàng Mới Về" products grid
start_marker = "<!-- Product Card 1 -->"
end_marker = "</div>\n</div>\n</section>\n<!-- Sale Banner Strip -->"

# Find the start and end of the grid
start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    before = content[:start_idx]
    after = content[end_idx:]
    
    jinja_loop = """{% for product in new_products %}
<!-- Product Card -->
<div class="group">
<div class="relative overflow-hidden rounded-xl mb-6 bg-surface-container-low aspect-[3/4]">
<img alt="{{ product.name }}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" src="{{ product.image_url }}"/>
{% if product.is_new %}
<div class="absolute top-4 left-4 bg-secondary text-white px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest">
    New
</div>
{% elif product.is_on_sale %}
<div class="absolute top-4 left-4 bg-secondary text-white px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest">
    Sale
</div>
{% endif %}
<div class="absolute bottom-4 right-4 translate-y-12 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
<a href="{{ url_for('product_detail', product_id=product.id) }}" class="w-12 h-12 rounded-full bg-white text-primary flex items-center justify-center shadow-lg">
<span class="material-symbols-outlined">visibility</span>
</a>
</div>
</div>
<h3 class="font-headline font-bold text-lg mb-1">{{ product.name }}</h3>
<div class="flex items-center gap-3">
<span class="text-secondary font-bold text-xl">{{ "{:0,.0f}".format(product.price) }}đ</span>
{% if product.old_price %}
<span class="text-on-surface-variant/50 line-through text-sm">{{ "{:0,.0f}".format(product.old_price) }}đ</span>
{% endif %}
</div>
</div>
{% endfor %}
"""
    content = before + jinja_loop + after

# Rewrite Top Nav Buttons
nav_buttons = """<div class="flex gap-4">
<button class="material-symbols-outlined text-teal-900 scale-95 active:scale-90 transition-transform">shopping_cart</button>
<button class="material-symbols-outlined text-teal-900 scale-95 active:scale-90 transition-transform">account_circle</button>
</div>"""

new_nav_buttons = """<div class="flex gap-4 items-center">
<a href="{{ url_for('cart') }}" class="material-symbols-outlined text-teal-900 scale-95 active:scale-90 transition-transform hover:text-primary">shopping_cart</a>
{% if current_user.is_authenticated %}
    {% if current_user.role == 'admin' %}
        <a href="{{ url_for('admin_dashboard') }}" class="material-symbols-outlined text-teal-900 scale-95 active:scale-90 transition-transform hover:text-primary">admin_panel_settings</a>
    {% endif %}
    <a href="{{ url_for('logout') }}" class="material-symbols-outlined text-teal-900 scale-95 active:scale-90 transition-transform hover:text-primary">logout</a>
{% else %}
    <a href="{{ url_for('login') }}" class="material-symbols-outlined text-teal-900 scale-95 active:scale-90 transition-transform hover:text-primary">account_circle</a>
{% endif %}
</div>"""

content = content.replace(nav_buttons, new_nav_buttons)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html template updated.")
