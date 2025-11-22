"""
Script para atualizar automaticamente o nome do modelo no gemini_service.py
"""
import os
import sys
import re

def update_model_name(new_model_name):
    """Atualiza o nome do modelo no arquivo gemini_service.py"""

    service_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'chatbot_literario',
        'gemini_service.py'
    )

    print("=" * 70)
    print("  🔧 ATUALIZAR NOME DO MODELO GEMINI")
    print("=" * 70)
    print()

    if not os.path.exists(service_file):
        print(f"❌ Arquivo não encontrado: {service_file}")
        return False

    # Ler o arquivo
    with open(service_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Padrão para encontrar a linha do modelo
    pattern = r"(self\.model_name\s*=\s*['\"])([^'\"]+)(['\"])"

    # Verificar se o padrão existe
    if not re.search(pattern, content):
        print(f"❌ Não foi possível encontrar 'self.model_name' no arquivo")
        return False

    # Obter nome atual
    current_match = re.search(pattern, content)
    current_model = current_match.group(2) if current_match else "desconhecido"

    print(f"📋 Arquivo: {service_file}")
    print(f"📌 Modelo atual: {current_model}")
    print(f"🎯 Novo modelo: {new_model_name}")
    print()

    # Confirmar mudança
    response = input("Deseja continuar com a atualização? (s/n): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Atualização cancelada pelo usuário")
        return False

    # Fazer backup
    backup_file = service_file + '.bak'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_file}")

    # Atualizar o conteúdo
    new_content = re.sub(
        pattern,
        rf"\g<1>{new_model_name}\g<3>",
        content
    )

    # Escrever o arquivo atualizado
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Modelo atualizado com sucesso!")
    print()
    print("=" * 70)
    print("  🧪 PRÓXIMOS PASSOS")
    print("=" * 70)
    print()
    print("1. Testar o novo modelo:")
    print("   python manage.py test_gemini")
    print()
    print("2. Se funcionar, commitar a mudança:")
    print(f"   git add chatbot_literario/gemini_service.py")
    print(f"   git commit -m \"Fix: Atualizar modelo Gemini para {new_model_name}\"")
    print()
    print("3. Se não funcionar, restaurar o backup:")
    print(f"   copy {backup_file} {service_file}")
    print()
    print("=" * 70)

    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python update_model_name.py <nome-do-modelo>")
        print()
        print("Exemplos:")
        print("  python update_model_name.py gemini-pro")
        print("  python update_model_name.py gemini-1.5-flash-latest")
        sys.exit(1)

    new_model = sys.argv[1]
    update_model_name(new_model)
