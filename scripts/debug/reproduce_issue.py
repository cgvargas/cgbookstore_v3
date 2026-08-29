import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from chatbot_literario.models import ChatbotKnowledge
from django.db.models import Q

# 1. Test add_correction (Admin Action logic)
print("=== TESING ADMIN ACTION LOGIC ===")
try:
    knowledge = ChatbotKnowledge.objects.create(
        original_question="Teste de erro admin",
        correct_response="Resposta teste admin",
        keywords=["teste", "admin"],
        knowledge_type="general",
        confidence_score=1.0,
        is_active=True
    )
    print(f"Created knowledge: {knowledge.id}")
except Exception as e:
    print(f"ERROR in creation: {e}")

# 2. Test keywords__overlap (Search logic) - RAW
print("\n=== TESTING KEYWORDS OVERLAP RAW ===")
try:
    # Force the query that uses overlap
    qs = ChatbotKnowledge.objects.filter(keywords__overlap=["teste", "admin"])
    print(f"Query constructed. Executing...")
    count = qs.count()
    print(f"Query executed. Count: {count}")
except Exception as e:
    print(f"ERROR in overlap query: {e}")
