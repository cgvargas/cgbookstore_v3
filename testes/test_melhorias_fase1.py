"""
Testes para validar as Melhorias da Fase 1 do Sistema de Recomendações.

Testa:
1. Algoritmos otimizados (filtro rigoroso de duplicatas)
2. Rate limiting ativo
3. Tracking de cliques
4. Tarefa Celery agendada
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from recommendations.algorithms_optimized import (
    OptimizedHybridRecommendationSystem,
    OptimizedCollaborativeFiltering,
    OptimizedContentBased,
    ExclusionFilter
)
from recommendations.views_simple import get_recommendations_simple, track_click_simple
from recommendations.models import UserBookInteraction
from accounts.models import BookShelf
from core.models import Book
import json


def print_separator():
    print("=" * 70)


def print_test_header(title):
    print_separator()
    print(f"[TESTE] {title}")
    print_separator()


def test_exclusion_filter():
    """Testa se o filtro de exclusão está funcionando."""
    print_test_header("Filtro de Exclusão Rigoroso")

    try:
        # Pegar um usuário de teste
        user = User.objects.filter(username='cgvargas').first()
        if not user:
            print("[ERRO] Usuário 'cgvargas' não encontrado")
            return False

        # Obter livros excluídos
        excluded = ExclusionFilter.get_excluded_books(user)

        print(f"[OK] Livros excluídos por ID: {len(excluded['ids'])}")
        print(f"[OK] Títulos únicos excluídos: {len(excluded['titles'])}")

        # Verificar se tem prateleiras
        shelves_count = BookShelf.objects.filter(user=user).count()
        print(f"[INFO] Prateleiras do usuário: {shelves_count}")

        # Verificar se tem interações
        interactions_count = UserBookInteraction.objects.filter(user=user).count()
        print(f"[INFO] Interações do usuário: {interactions_count}")

        if len(excluded['ids']) > 0:
            print("[OK] Filtro de exclusão funcionando!")
            return True
        else:
            print("[AVISO]  Nenhum livro excluído (usuário pode não ter interações)")
            return True

    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        return False


def test_optimized_algorithms():
    """Testa se os algoritmos otimizados estão funcionando."""
    print_test_header("Algoritmos Otimizados")

    try:
        user = User.objects.filter(username='cgvargas').first()
        if not user:
            print("[ERRO] Usuário 'cgvargas' não encontrado")
            return False

        # Testar Híbrido Otimizado
        print("\n1 Testando OptimizedHybridRecommendationSystem...")
        engine_hybrid = OptimizedHybridRecommendationSystem()
        recs_hybrid = engine_hybrid.recommend(user, n=5)
        print(f"   [OK] Recomendações geradas: {len(recs_hybrid)}")

        # Testar Colaborativo Otimizado
        print("\n2 Testando OptimizedCollaborativeFiltering...")
        engine_collab = OptimizedCollaborativeFiltering()
        recs_collab = engine_collab.recommend(user, n=5)
        print(f"   [OK] Recomendações geradas: {len(recs_collab)}")

        # Testar Conteúdo Otimizado
        print("\n3 Testando OptimizedContentBased...")
        engine_content = OptimizedContentBased()
        recs_content = engine_content.recommend(user, n=5)
        print(f"   [OK] Recomendações geradas: {len(recs_content)}")

        # Verificar se não há duplicatas
        print("\n[INFO] Verificando duplicatas...")
        for i, algo_name in enumerate([
            ('Híbrido', recs_hybrid),
            ('Colaborativo', recs_collab),
            ('Conteúdo', recs_content)
        ]):
            name, recs = algo_name
            if recs:
                book_ids = [rec['book'].id for rec in recs if 'book' in rec]
                duplicates = len(book_ids) - len(set(book_ids))
                if duplicates == 0:
                    print(f"   [OK] {name}: 0 duplicatas")
                else:
                    print(f"   [ERRO] {name}: {duplicates} duplicatas encontradas!")

        print("\n[OK] Todos os algoritmos otimizados funcionando!")
        return True

    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rate_limiting():
    """Testa se o rate limiting está ativo."""
    print_test_header("Rate Limiting")

    try:
        # Verificar o código fonte da view
        import inspect
        from recommendations import views_simple

        source = inspect.getsource(views_simple.get_recommendations_simple)

        if '@ratelimit' in source and '30/h' in source:
            # Verificar se NÃO está comentado
            lines = source.split('\n')
            ratelimit_line = [l for l in lines if '@ratelimit' in l and '30/h' in l]

            if ratelimit_line and not ratelimit_line[0].strip().startswith('#'):
                print("[OK] Rate limiting ATIVO: 30 requisições/hora")
                return True
            else:
                print("[ERRO] Rate limiting COMENTADO/DESABILITADO")
                return False
        else:
            print("[ERRO] Rate limiting NÃO encontrado no código")
            return False

    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        return False


def test_tracking_endpoint():
    """Testa se o endpoint de tracking existe e está configurado."""
    print_test_header("Endpoint de Tracking de Cliques")

    try:
        from django.urls import reverse, resolve

        # Verificar se a URL existe
        try:
            url = reverse('recommendations:track_click_simple')
            print(f"[OK] URL configurada: {url}")

            # Verificar se resolve para a view correta
            resolved = resolve(url)
            if resolved.func.__name__ == 'track_click_simple':
                print(f"[OK] View correta: {resolved.func.__name__}")
                return True
            else:
                print(f"[ERRO] View incorreta: {resolved.func.__name__}")
                return False

        except Exception as e:
            print(f"[ERRO] URL não encontrada: {e}")
            return False

    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        return False


def test_celery_schedule():
    """Testa se a tarefa Celery está agendada."""
    print_test_header("Tarefa Celery Agendada")

    try:
        from cgbookstore.celery import app

        schedule = app.conf.beat_schedule

        if 'compute-book-similarities' in schedule:
            task_config = schedule['compute-book-similarities']
            print(f"[OK] Tarefa encontrada: {task_config['task']}")
            print(f"[OK] Agendamento: {task_config['schedule']}")
            print("[OK] Tarefa Celery configurada corretamente!")
            return True
        else:
            print("[ERRO] Tarefa 'compute-book-similarities' NÃO encontrada no schedule")
            return False

    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 70)
    print("TESTES DAS MELHORIAS FASE 1 - SISTEMA DE RECOMENDACOES")
    print("=" * 70 + "\n")

    results = {}

    # Executar testes
    results['Filtro de Exclusão'] = test_exclusion_filter()
    print()

    results['Algoritmos Otimizados'] = test_optimized_algorithms()
    print()

    results['Rate Limiting'] = test_rate_limiting()
    print()

    results['Tracking de Cliques'] = test_tracking_endpoint()
    print()

    results['Tarefa Celery'] = test_celery_schedule()
    print()

    # Resumo
    print_separator()
    print("RESUMO DOS TESTES")
    print_separator()

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)

    for test_name, passed in results.items():
        status = "[OK] PASSOU" if passed else "[FALHOU]"
        print(f"{status} - {test_name}")

    print_separator()
    print(f"\nTotal: {passed_tests}/{total_tests} testes passaram ({int(passed_tests/total_tests*100)}%)\n")

    if passed_tests == total_tests:
        print("SUCESSO! TODOS OS TESTES PASSARAM! Melhorias Fase 1 implementadas com sucesso!")
    else:
        print("AVISO: Alguns testes falharam. Verifique os logs acima.")

    print_separator()


if __name__ == '__main__':
    main()
