import os
import re

index_path = 'templates/index.html'

with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the header/nav segment up to the <main> tag
head_match = re.search(r'(<!DOCTYPE html>.*?<body[^>]*>)', content, re.DOTALL)
head_part = head_match.group(1) if head_match else ''

nav_html = """
    <nav id="main-nav" class="fixed top-0 w-full border-b-[0.5rem] border-tertiary-fixed-dim bg-white/80 backdrop-blur-xl flex justify-between items-center px-12 h-24 z-50 font-['Epilogue'] tracking-tight shadow-sm">
        <div class="flex items-center gap-8">
            <a href="{{ url_for('index') }}" class="flex items-center">
                <img src="{{ url_for('static', filename='logo.png') }}" alt="UTH Store Logo" class="h-12 object-contain">
            </a>
            <div class="hidden md:flex gap-6">
                <!-- If path is /products and category=X highlight -->
                <a class="text-stone-600 hover:text-teal-800 transition-colors font-bold {% if request.args.get('category') == 'Áo thun' %}text-primary{% endif %}" href="{{ url_for('products', category='Áo thun') }}">Áo thun</a>
                <a class="text-stone-600 hover:text-teal-800 transition-colors font-bold {% if request.args.get('category') == 'Sơ mi' %}text-primary{% endif %}" href="{{ url_for('products', category='Sơ mi') }}">Sơ mi</a>
                <a class="text-stone-600 hover:text-teal-800 transition-colors font-bold {% if request.args.get('category') == 'Váy' %}text-primary{% endif %}" href="{{ url_for('products', category='Váy') }}">Váy</a>
                <a class="text-stone-600 hover:text-teal-800 transition-colors font-bold {% if request.args.get('category') == 'Quần' %}text-primary{% endif %}" href="{{ url_for('products', category='Quần') }}">Quần</a>
                <a class="text-secondary font-bold {% if request.args.get('sale') == 'true' %}text-primary{% endif %}" href="{{ url_for('products', sale='true') }}">Sale</a>
            </div>
        </div>
        <div class="flex items-center gap-6">
            <div class="relative hidden lg:block">
                <input class="bg-surface-container-high border-none rounded-full px-6 py-2 w-64 text-sm focus:ring-2 focus:ring-tertiary" placeholder="Tìm kiếm sản phẩm..." type="text"/>
            </div>
            <div class="flex gap-4 items-center">
                <a href="{{ url_for('cart') }}" class="scale-95 active:scale-90 transition-transform text-primary hover:text-teal-700">
                    <span class="material-symbols-outlined" data-icon="shopping_cart">shopping_cart</span>
                </a>
                {% if current_user.is_authenticated %}
                    {% if current_user.role == 'admin' %}
                        <a href="{{ url_for('admin_dashboard') }}" class="scale-95 active:scale-90 transition-transform text-primary hover:text-teal-700">
                            <span class="material-symbols-outlined">admin_panel_settings</span>
                        </a>
                    {% endif %}
                    <a href="{{ url_for('logout') }}" class="scale-95 active:scale-90 transition-transform text-primary hover:text-teal-700">
                        <span class="material-symbols-outlined">logout</span>
                    </a>
                {% else %}
                    <a href="{{ url_for('login') }}" class="scale-95 active:scale-90 transition-transform text-primary hover:text-teal-700">
                        <span class="material-symbols-outlined" data-icon="account_circle">account_circle</span>
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>
"""

# Extract footer manually
footer_match = re.search(r'(<footer.*?</footer>)', content, re.DOTALL)
footer_part = footer_match.group(1) if footer_match else ''

base_content = head_part + "\n" + nav_html + """
    <div id="wrapper" class="flex flex-col min-h-screen">
        {% block content %}{% endblock %}
    </div>
""" + footer_part + """
    <!-- Scripts -->
    <script src="{{ url_for('static', filename='js/main.js') }}" defer></script>
</body>
</html>
"""

# Dynamic title wrapper
base_content = re.sub(r'<title>.*?</title>', '<title>{% block title %}UTH Store{% endblock %}</title>', base_content)

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(base_content)

print("Created base.html successfully.")
