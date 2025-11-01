"""
Script para executar via: python manage.py shell < test_preference_shell.py
"""

from django.contrib.auth.models import User
from recommendations.preference_analyzer import (
    UserPreferenceAnalyzer,
    ShelfWeightConfig,
    print_user_preference_report
)

# Buscar usuário
user = User.objects.first()
print(f"\n🧪 Testando com usuário: {user.username}\n")

# Mostrar configuração de pesos
print("="*80)
print("📊 CONFIGURAÇÃO DE PESOS POR PRATELEIRA:")
print("="*80)
for shelf_type in ['favorites', 'read', 'reading', 'to_read', 'abandoned']:
    desc = ShelfWeightConfig.get_description(shelf_type)
    weight = ShelfWeightConfig.get_weight(shelf_type)
    bar = "█" * int(weight * 50)
    print(f"{desc:<45} {bar} {weight:.0%}")

# Relatório de preferências
print("\n")
print_user_preference_report(user)

print("\n✅ Teste concluído!")
