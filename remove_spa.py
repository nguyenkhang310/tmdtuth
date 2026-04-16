import os

templates_dir = 'templates'

for filename in os.listdir(templates_dir):
    if not filename.endswith('.html'):
        continue
        
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the spa.js script tag
    new_content = content.replace('<script src="{{ url_for(\'static\', filename=\'js/spa.js\') }}" defer></script>', '')
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Removed spa.js from {filename}")

print("Cleaned up spa.js.")
