"""
Extrair apenas BookShelf do backup
"""
import json

print("Carregando backup...")
with open('backup_supabase_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total de registros no backup: {len(data)}")

# Filtrar apenas BookShelf
bookshelves = [item for item in data if item['model'] == 'accounts.bookshelf']
print(f"Total de BookShelf encontrados: {len(bookshelves)}")

if bookshelves:
    # Salvar arquivo separado
    with open('bookshelf_only.json', 'w', encoding='utf-8') as f:
        json.dump(bookshelves, f, indent=2, ensure_ascii=False)

    print("Arquivo 'bookshelf_only.json' criado com sucesso!")

    # Mostrar preview
    print("\nPrimeiros 3 registros:")
    for i, bs in enumerate(bookshelves[:3], 1):
        print(f"{i}. User: {bs['fields']['user']}, Book: {bs['fields']['book']}, Shelf: {bs['fields']['shelf']}")
else:
    print("NENHUM BookShelf encontrado no backup!")
