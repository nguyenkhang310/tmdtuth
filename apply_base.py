import os
import re

templates_dir = 'templates'
files_to_modify = ['index.html', 'products.html', 'product-detail.html', 'login.html', 'cart.html', 'contact.html', 'policy.html', 'admin.html']

for filename in files_to_modify:
    filepath = os.path.join(templates_dir, filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine title
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1) if title_match else 'UTH Store'

    # Find the start of main content (we use <main...>)
    main_start_match = re.search(r'(<main[^>]*>)', content)
    
    # Wait, some pages might not have <main>, e.g., login.html might just have a <div>?
    # Let's check if they have <main>
    if not main_start_match:
        # Fallback: start right after <nav>
        nav_end_match = re.search(r'</nav>', content)
        if nav_end_match:
            main_start_idx = nav_end_match.end()
        else:
            main_start_idx = content.find('<body>') + 6
            if main_start_idx == 5: main_start_idx = 0
    else:
        main_start_idx = main_start_match.start()

    # Find the end of main content (right before <footer>)
    footer_start_match = re.search(r'<footer[^>]*>', content)
    if footer_start_match:
        main_end_idx = footer_start_match.start()
    else:
        # Fallback: end of body
        body_end_match = re.search(r'</body>', content)
        if body_end_match:
            main_end_idx = body_end_match.start()
        else:
            main_end_idx = len(content)

    # Extract the actual inner HTML
    inner_block = content[main_start_idx:main_end_idx].strip()
    
    # Clean up trailing scripts like spa.js or main.js inside inner_block just in case
    inner_block = re.sub(r'<script src=.*?</script>', '', inner_block)

    # Build the new content
    new_content = f"{{% extends 'base.html' %}}\n{{% block title %}}{title}{{% endblock %}}\n{{% block content %}}\n{inner_block}\n{{% endblock %}}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Refactored {filename} using base.html")
