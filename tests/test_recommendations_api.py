"""
Testar API de recomendacoes diretamente para debug.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from django.contrib.auth.models import User
from recommendations.algorithms_preference_weighted import PreferenceWeightedHybrid

print("="*60)
print("TESTE API DE RECOMENDACOES - PERSONALIZADO")
print("="*60)

# Buscar usuario
user = User.objects.get(username='claud')
print(f"\nUsuario: {user.username}")
print(f"Is authenticated: {user.is_authenticated}")

# Testar algoritmo diretamente
print("\nTestando PreferenceWeightedHybrid...")
try:
    engine = PreferenceWeightedHybrid()
    recommendations = engine.recommend(user, n=6)

    print(f"\nResultado: {len(recommendations)} recomendacoes")

    if recommendations:
        print("\nPrimeiras 3 recomendacoes:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"\n  {i}. Recomendacao:")
            book = rec.get('book')
            if book:
                print(f"     Book type: {type(book)}")
                print(f"     Book ID: {book.id if hasattr(book, 'id') else 'N/A'}")
                print(f"     Book title: {book.title if hasattr(book, 'title') else 'N/A'}")
                print(f"     Has cover_image: {bool(book.cover_image) if hasattr(book, 'cover_image') else False}")
            score = rec.get('score', 0)
            reason = rec.get('reason', '')
            print(f"     Score: {score:.2f}")
            print(f"     Reason: {reason[:50]}..." if len(reason) > 50 else f"     Reason: {reason}")
    else:
        print("\nNENHUMA recomendacao retornada!")
        print("Isso pode indicar:")
        print("  - Usuario nao tem livros na biblioteca")
        print("  - Todos os livros do usuario ja foram excluidos")
        print("  - Problema com o algoritmo")

except Exception as e:
    print(f"\nERRO: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
