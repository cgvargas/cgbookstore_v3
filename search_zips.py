import os

search_paths = [
    r"C:\Users\claud\Downloads",
    r"C:\Users\claud\OneDrive",
    r"c:\ProjectDjango\cgbookstore_v3"
]

print("Buscando arquivos ZIP nas pastas do usuario...")
found_zips = []
for path in search_paths:
    if not os.path.exists(path):
        continue
    print(f"Buscando em {path}...")
    for root, dirs, files in os.walk(path):
        # Limit recursion depth for OneDrive to avoid freezing
        if root.count(os.sep) - path.count(os.sep) > 3:
            dirs[:] = []  # Don't go deeper than 3 levels
            continue
        # Exclude large system/developer directories
        exclude_dirs = ['node_modules', '.venv', '.git', 'appdata']
        dirs[:] = [d for d in dirs if d.lower() not in exclude_dirs]
        for f in files:
            if f.endswith('.zip'):
                full_path = os.path.join(root, f)
                found_zips.append(full_path)
                print(f"  Encontrado: {full_path}")

print("-" * 60)
print(f"Total de arquivos ZIP encontrados: {len(found_zips)}")
