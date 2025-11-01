"""
Teste Simples: Sistema de Análise de Preferências
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from recommendations.preference_analyzer import (
    UserPreferenceAnalyzer,
    ShelfWeightConfig,
    print_user_preference_report
)

def main():
    print("\n" + "="*80)
    print("🧪 TESTE: Sistema de Análise de Preferências por Prateleiras")
    print("="*80)

    # Buscar usuário
    try:
        user = User.objects.get(username='claud')
    except User.DoesNotExist:
        print("\n❌ Usuário 'claud' não encontrado!")
        print("\nUsuários disponíveis:")
        for u in User.objects.all()[:10]:
            print(f"  - {u.username}")
        return

    # Exibir configuração de pesos
    print("\n📊 CONFIGURAÇÃO DE PESOS POR PRATELEIRA:")
    print("─"*80)
    for shelf_type in ['favorites', 'read', 'reading', 'to_read', 'abandoned']:
        desc = ShelfWeightConfig.get_description(shelf_type)
        weight = ShelfWeightConfig.get_weight(shelf_type)
        bar = "█" * int(weight * 50)  # Barra visual
        print(f"  {desc:<40} {bar} {weight:.0%}")

    # Analisar preferências do usuário
    print("\n")
    print_user_preference_report(user)

    # Testar pontuação de livros
    print("\n📈 TESTE: Pontuação de Livros Baseada em Preferências")
    print("─"*80)

    from core.models import Book

    analyzer = UserPreferenceAnalyzer(user)

    # Pegar alguns livros aleatórios para pontuar
    sample_books = Book.objects.all()[:10]

    print("\nPontuando 10 livros aleatórios baseado no perfil do usuário:\n")

    for book in sample_books:
        score = analyzer.score_book_by_preference(book)
        stars = "⭐" * int(score * 5)  # 0-5 estrelas
        print(f"  {book.title[:50]:<50} | Score: {score:.2f} {stars}")

    print("\n✅ Teste concluído!")
    print("─"*80 + "\n")


if __name__ == '__main__':
    main()
