"""
Comando Django para gerar keywords para conhecimentos existentes.
Uso: python manage.py generate_knowledge_keywords
"""
from django.core.management.base import BaseCommand
from chatbot_literario.models import ChatbotKnowledge
from chatbot_literario.knowledge_base_service import get_knowledge_service


class Command(BaseCommand):
    help = 'Gera keywords para conhecimentos que nao tem'

    def handle(self, *args, **options):
        kb_service = get_knowledge_service()

        # Buscar TODOS os conhecimentos e verificar manualmente
        all_knowledges = ChatbotKnowledge.objects.all()

        self.stdout.write(f"Verificando {all_knowledges.count()} conhecimento(s)...\n")

        updated_count = 0
        already_ok = 0

        for knowledge in all_knowledges:
            # Verificar se tem keywords vazias
            if not knowledge.keywords or len(knowledge.keywords) == 0:
                try:
                    # Extrair keywords da pergunta
                    keywords = kb_service._extract_keywords(knowledge.original_question.lower())

                    if keywords:
                        knowledge.keywords = keywords
                        knowledge.save()
                        self.stdout.write(
                            f"[OK] ID {knowledge.id}: {len(keywords)} keywords -> "
                            f"{', '.join(keywords[:5])}"
                        )
                        updated_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"[AVISO] ID {knowledge.id}: Nenhuma keyword extraida"
                            )
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[ERRO] ID {knowledge.id}: {str(e)}"
                        )
                    )
            else:
                already_ok += 1

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"RESUMO:")
        self.stdout.write(self.style.SUCCESS(f"   Atualizados: {updated_count}"))
        self.stdout.write(f"   Ja tinham keywords: {already_ok}")
        self.stdout.write(f"   Total: {all_knowledges.count()}")
        self.stdout.write(f"{'='*60}\n")

        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(f"{updated_count} conhecimento(s) atualizado(s) com sucesso!"))
        else:
            self.stdout.write(self.style.SUCCESS("Todos os conhecimentos ja tinham keywords!"))
