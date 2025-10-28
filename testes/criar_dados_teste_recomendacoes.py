"""
Script para criar dados de teste para o Sistema de Recomendações.
Cria interações fictícias entre usuários e livros.
"""
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Book
from recommendations.models import UserBookInteraction, UserProfile


def criar_interacoes_teste():
    """Cria interações de teste para demonstrar o sistema de recomendações."""

    print("=" * 60)
    print("CRIANDO DADOS DE TESTE PARA RECOMENDACOES")
    print("=" * 60)

    # Verificar se há usuários e livros
    users = User.objects.all()
    books = Book.objects.all()

    if not users.exists():
        print("\n[ERRO] Nenhum usuario encontrado no banco de dados.")
        print("Crie pelo menos um usuario antes de executar este script.")
        return

    if not books.exists():
        print("\n[ERRO] Nenhum livro encontrado no banco de dados.")
        print("Adicione livros ao sistema antes de executar este script.")
        return

    print(f"\n[INFO] Usuarios disponiveis: {users.count()}")
    print(f"[INFO] Livros disponiveis: {books.count()}")

    # Tipos de interação possíveis
    interaction_types = [
        'view',       # Visualização (peso baixo)
        'click',      # Clique (peso baixo)
        'wishlist',   # Lista de desejos (peso médio)
        'reading',    # Lendo (peso alto)
        'read',       # Lido (peso alto)
        'completed',  # Finalizado (peso muito alto)
        'review',     # Avaliado (peso muito alto)
    ]

    total_criadas = 0

    # Para cada usuário, criar algumas interações
    for user in users:
        print(f"\n[{user.username}] Criando interacoes...")

        # Criar perfil se não existir
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            print(f"  [+] Perfil criado")

        # Limpar interações antigas (opcional)
        old_count = UserBookInteraction.objects.filter(user=user).count()
        if old_count > 0:
            print(f"  [INFO] Usuario ja tem {old_count} interacoes")
            resposta = input(f"  Deseja limpar e recriar? (s/N): ").strip().lower()
            if resposta == 's':
                UserBookInteraction.objects.filter(user=user).delete()
                print(f"  [!] {old_count} interacoes antigas removidas")

        # Selecionar livros aleatórios para este usuário
        num_livros = min(random.randint(8, 15), books.count())
        livros_selecionados = random.sample(list(books), num_livros)

        interacoes_usuario = 0

        for book in livros_selecionados:
            # Escolher tipo de interação (bias para interações mais fortes)
            if random.random() < 0.7:  # 70% chance de interação forte
                interaction_type = random.choice(['read', 'completed', 'review', 'wishlist'])
            else:
                interaction_type = random.choice(['view', 'click'])

            # Rating apenas para reviews
            rating = None
            if interaction_type == 'review':
                rating = random.randint(3, 5)  # Reviews positivas (3-5 estrelas)

            # Criar interação
            interaction, created = UserBookInteraction.objects.get_or_create(
                user=user,
                book=book,
                interaction_type=interaction_type,
                defaults={'rating': rating}
            )

            if created:
                print(f"  [+] {interaction_type.upper()}: {book.title[:40]}... {f'({rating}★)' if rating else ''}")
                interacoes_usuario += 1
                total_criadas += 1
            else:
                print(f"  [=] JA EXISTE: {interaction_type.upper()}: {book.title[:40]}...")

        # Atualizar estatísticas do perfil
        profile.update_statistics()
        print(f"  [✓] Total de interacoes criadas: {interacoes_usuario}")
        print(f"  [✓] Estatisticas atualizadas: {profile.total_books_read} livros lidos")

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Total de interacoes criadas: {total_criadas}")
    print(f"Usuarios com interacoes: {users.count()}")

    # Mostrar estatísticas por tipo
    print("\nInteracoes por tipo:")
    for interaction_type in interaction_types:
        count = UserBookInteraction.objects.filter(interaction_type=interaction_type).count()
        if count > 0:
            print(f"  - {interaction_type.upper()}: {count}")

    print("\n[SUCESSO] Dados de teste criados com sucesso!")
    print("\nProximo passo:")
    print("  1. Execute: python test_recommendations.py")
    print("  2. Acesse a home page para ver as recomendacoes")
    print("  3. Teste a API: /recommendations/api/recommendations/?algorithm=hybrid")


def criar_interacoes_para_usuario(username):
    """
    Cria interações apenas para um usuário específico.
    Útil para testar rapidamente.
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"[ERRO] Usuario '{username}' nao encontrado.")
        return

    print(f"\n[INFO] Criando interacoes para usuario: {username}")

    books = Book.objects.all()
    if not books.exists():
        print("[ERRO] Nenhum livro disponivel.")
        return

    # Limpar interações antigas
    old_count = UserBookInteraction.objects.filter(user=user).count()
    if old_count > 0:
        UserBookInteraction.objects.filter(user=user).delete()
        print(f"[!] {old_count} interacoes antigas removidas")

    # Criar interações
    num_livros = min(10, books.count())
    livros_selecionados = random.sample(list(books), num_livros)

    for book in livros_selecionados:
        interaction_type = random.choice(['read', 'completed', 'review', 'wishlist'])
        rating = random.randint(3, 5) if interaction_type == 'review' else None

        UserBookInteraction.objects.create(
            user=user,
            book=book,
            interaction_type=interaction_type,
            rating=rating
        )
        print(f"[+] {interaction_type.upper()}: {book.title[:50]}")

    # Atualizar perfil
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.update_statistics()

    print(f"\n[✓] {num_livros} interacoes criadas para {username}")
    print(f"[✓] Total de livros lidos: {profile.total_books_read}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # Criar apenas para um usuário específico
        username = sys.argv[1]
        criar_interacoes_para_usuario(username)
    else:
        # Criar para todos os usuários
        criar_interacoes_teste()
