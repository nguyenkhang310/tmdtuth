import os
import re

templates_dir = 'templates'

for filename in os.listdir(templates_dir):
    if not filename.endswith('.html'):
        continue
        
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace \' with ' inside the entire file
    new_content = content.replace("\\'", "'")
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filename}")

print("All HTML files fixed.")
