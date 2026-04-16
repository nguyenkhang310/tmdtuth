import os
import re

templates_dir = 'templates'

for filename in os.listdir(templates_dir):
    if not filename.endswith('.html'):
        continue
        
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix js sources
    content = re.sub(r'src="js/([^"]+)"', r'src="{{ url_for(\'static\', filename=\'js/\1\') }}"', content)
    
    # Fix style.css if existed
    content = re.sub(r'href="style\.css"', r'href="{{ url_for(\'static\', filename=\'style.css\') }}"', content)
    
    # Fix html links
    content = re.sub(r'href="index\.html"', r'href="{{ url_for(\'index\') }}"', content)
    content = re.sub(r'href="products\.html"', r'href="{{ url_for(\'products\') }}"', content)
    content = re.sub(r'href="product-detail\.html"', r'href="{{ url_for(\'product_detail\') }}"', content)
    content = re.sub(r'href="cart\.html"', r'href="{{ url_for(\'cart\') }}"', content)
    content = re.sub(r'href="login\.html"', r'href="{{ url_for(\'login\') }}"', content)
    content = re.sub(r'href="contact\.html"', r'href="{{ url_for(\'contact\') }}"', content)
    content = re.sub(r'href="policy\.html"', r'href="{{ url_for(\'policy\') }}"', content)
    content = re.sub(r'href="admin\.html"', r'href="{{ url_for(\'admin_dashboard\') }}"', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Links fixed.")
