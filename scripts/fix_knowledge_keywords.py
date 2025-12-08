"""
Script para gerar keywords nos conhecimentos da base do Dbit
"""
import sys
import os
import django

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chatbot_literario.models import ChatbotKnowledge
from chatbot_literario.knowledge_base_service import get_knowledge_service

print("Verificando conhecimentos sem keywords...\n")

kb_service = get_knowledge_service()
all_kbs = ChatbotKnowledge.objects.all()

print(f"Total de conhecimentos: {all_kbs.count()}\n")

updated = 0
for kb in all_kbs:
    if not kb.keywords or len(kb.keywords) == 0:
        keywords = kb_service._extract_keywords(kb.original_question.lower())
        if keywords:
            kb.keywords = keywords
            kb.save()
            print(f"[OK] ID {kb.id}: {kb.original_question[:50]}...")
            print(f"     Keywords: {', '.join(keywords)}\n")
            updated += 1

print(f"\n{'='*60}")
print(f"Atualizados: {updated}")
print(f"{'='*60}")
