import os
import re

templates_dir = r"c:\ProjectDjango\cgbookstore_v3\templates"

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'featured_image.url' not in content:
        return
        
    print(f"Fixing {file_path}")
    
    def replacer(match):
        prefix = match.group(1)
        return "{% if " + prefix + ".featured_image.name %}{{ " + prefix + ".featured_image.url }}{% else %}{% static 'images/no-cover-placeholder.svg' %}{% endif %}"
        
    new_content = re.sub(r'\{\{\s*([a-zA-Z0-9_]+)\.featured_image\.url\s*\}\}', replacer, content)
    
    if new_content != content:
        # Avoid double {% load static %}
        if "{% load static %}" not in new_content:
            new_content = "{% load static %}\n" + new_content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

for root, dirs, files in os.walk(templates_dir):
    for f in files:
        if f.endswith('.html'):
            process_file(os.path.join(root, f))

print("Done")
