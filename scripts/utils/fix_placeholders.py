"""
Script para substituir placeholders externos por locais
"""
import os
import re

# Arquivos para processar
files = [
    'templates/core/book_detail.html',
    'templates/core/events.html',
    'templates/core/home.html',
    'templates/core/library.html',
    'templates/core/search_results.html',
    'templates/core/widgets/event_widget.html',
]

# Padrões para substituir
replacements = [
    # Padrão 1: URLs diretas
    (r'https://via\.placeholder\.com/[^"\']+', "{% static 'images/no-cover-placeholder.svg' %}"),
    # Padrão 2: Em onerror
    (r"onerror=\"this\.src='https://via\.placeholder\.com/[^']+';\"", "onerror=\"this.src='{% static 'images/no-cover-placeholder.svg' %}';\""),
]

print("=" * 80)
print("SUBSTITUINDO PLACEHOLDERS EXTERNOS POR LOCAIS")
print("=" * 80)

total_replacements = 0

for file_path in files:
    if not os.path.exists(file_path):
        print(f"\nArquivo nao encontrado: {file_path}")
        continue

    print(f"\nProcessando: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    file_replacements = 0

    for pattern, replacement in replacements:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            file_replacements += len(matches)
            print(f"  - Substituidas {len(matches)} ocorrencias do padrao {pattern[:50]}...")

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  OK - {file_replacements} substituicoes realizadas")
        total_replacements += file_replacements
    else:
        print(f"  - Nenhuma substituicao necessaria")

print("\n" + "=" * 80)
print(f"TOTAL: {total_replacements} substituicoes realizadas")
print("=" * 80)
