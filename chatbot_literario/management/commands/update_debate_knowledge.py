"""
Atualiza o conhecimento sobre debate para a resposta correta
"""
from django.core.management.base import BaseCommand
from chatbot_literario.models import ChatbotKnowledge


class Command(BaseCommand):
    help = 'Atualiza conhecimento sobre debate'

    def handle(self, *args, **options):
        try:
            # Buscar o conhecimento sobre debate
            kb = ChatbotKnowledge.objects.filter(
                original_question__icontains='debater'
            ).first()

            if not kb:
                self.stdout.write(self.style.ERROR("Conhecimento sobre debate nao encontrado!"))
                return

            # Nova resposta conforme solicitado
            new_response = '''Voce pode compartilhar suas ideias e perguntas sobre o livro aqui comigo, e eu posso ajudar a direcionar a conversa.

No entanto, se voce quiser debater com a comunidade como um todo:

1. **Atraves do seu Perfil:**
   - Clique no seu perfil
   - La voce encontrara um link para debates da comunidade

2. **Atraves da Pagina do Livro:**
   - Acesse a pagina de detalhes do livro
   - Role ate a secao de avaliacoes e reviews
   - Escreva sua resenha e marque como "Publica"
   - Outros leitores poderao ver sua opiniao e interagir

3. **Secao Novos Autores:**
   - Acesse "Novos Autores" no menu (/novos-autores/)
   - Na pagina de cada livro, deixe avaliacoes e comentarios
   - Interaja com as avaliacoes de outros leitores marcando-as como "util"

Dica: Quando voce escreve uma resenha detalhada e a marca como publica, voce ganha XP extra e contribui para a comunidade!

Enquanto isso, posso te ajudar com recomendacoes, analises literarias e duvidas sobre livros. O que voce gostaria de discutir?'''

            # Atualizar
            kb.correct_response = new_response
            kb.confidence_score = 1.0
            kb.save()

            self.stdout.write(self.style.SUCCESS(f"Conhecimento ID {kb.id} atualizado com sucesso!"))
            self.stdout.write(f"\nPergunta: {kb.original_question}")
            self.stdout.write(f"\nKeywords: {', '.join(kb.keywords)}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro: {str(e)}"))
