import os
import re

base_dir = r"c:\ProjectDjango\cgbookstore_v3"

def refactor_models():
    modified_files = []
    for root, dirs, files in os.walk(base_dir):
        # Ignorar dirs comuns
        if any(ignore in root for ignore in ['venv', '.git', '__pycache__', 'migrations']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(filepath, 'r', encoding='iso-8859-1') as f:
                        content = f.read()
                    
                if 'StdImageField' in content:
                    print(f"Refactoring: {filepath}")
                    
                    # 1. Replace the import
                    content = re.sub(
                        r'from\s+stdimage(\.models)?\s+import\s+StdImageField', 
                        'from pictures.models import PictureField', 
                        content
                    )
                    
                    # 2. Add aspect_ratios=[None] to avoid strict cropping when replacing StdImageField
                    content = content.replace("PictureField(", "PictureField(")
                    
                    # Remove the variations argument
                    content = re.sub(r'variations=\{[^}]*\}\s*,?', '', content, flags=re.DOTALL)
                    
                    # Clean trailing commas
                    content = re.sub(r',\s*\)', ')', content)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                    modified_files.append(filepath)
    
    return modified_files

if __name__ == '__main__':
    modified = refactor_models()
    print("Optimization applied on:")
    for m in modified:
        print(f" - {m}")
