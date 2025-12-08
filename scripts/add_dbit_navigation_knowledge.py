"""
Script para adicionar conhecimentos de navegação à base do Dbit.
Ensina o Dbit a direcionar usuários para recursos da plataforma.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

from chatbot_literario.models import ChatbotKnowledge
from django.contrib.auth.models import User

# Obter usuário admin para atribuir como criador
admin_user = User.objects.filter(is_superuser=True).first()

if not admin_user:
    print("❌ Nenhum superusuário encontrado. Crie um admin primeiro.")
    exit(1)

# Conhecimentos sobre navegação e recursos da plataforma
knowledge_entries = [
    {
        'knowledge_type': 'general',
        'original_question': 'Como posso debater sobre um livro com outros usuários?',
        'incorrect_response': 'Eu posso debater o livro com você aqui no chat.',
        'correct_response': '''Para debater sobre livros com outros usuários da comunidade, você tem várias opções na plataforma:

📚 **Avaliações Públicas de Livros:**
1. Acesse a página de detalhes do livro (no catálogo ou seção "Livros")
2. Role até a seção de avaliações
3. Escreva sua resenha e marque como "Pública" para que outros usuários vejam
4. Outros leitores poderão ver sua opinião e você pode ler as deles

✍️ **Seção Novos Autores (Livros Independentes):**
- Acesse "Novos Autores" no menu (ou /novos-autores/)
- Navegue pelos livros de autores independentes
- Na página de cada livro, você pode deixar avaliações e comentários
- Interaja com as avaliações de outros leitores marcando-as como "útil"

💬 **Dica:** Quando você escreve uma resenha detalhada e a marca como pública, você ganha XP extra e contribui para a comunidade!

Enquanto isso, eu posso te ajudar com recomendações, análises literárias e dúvidas sobre livros. 📖''',
        'confidence_score': 1.0,
        'admin_notes': 'Direciona usuários para recursos de debate e avaliação na plataforma'
    },
    {
        'knowledge_type': 'general',
        'original_question': 'Onde posso encontrar livros de autores novos ou independentes?',
        'incorrect_response': 'Posso te recomendar alguns autores conhecidos.',
        'correct_response': '''Para descobrir talentos emergentes e autores independentes:

🌟 **Seção Novos Autores:**
- Acesse o menu superior e clique em "Novos Autores"
- Ou vá direto para: /novos-autores/

📚 **Recursos disponíveis:**
- Lista completa de livros de autores independentes
- Filtro por gênero, popularidade e mais recentes
- Leia capítulos gratuitamente online
- Avalie, comente e siga seus autores favoritos
- Veja o perfil completo dos autores

🔥 **Em Alta:**
- Acesse /novos-autores/em-alta/ para ver os livros mais populares
- Descubra novos talentos que estão fazendo sucesso

💡 **Você também é escritor?** Pode se tornar um autor na plataforma em "Tornar-se Autor"!''',
        'confidence_score': 1.0,
        'admin_notes': 'Ensina usuários a encontrar a seção de Novos Autores'
    },
    {
        'knowledge_type': 'general',
        'original_question': 'Como faço para avaliar ou dar nota a um livro?',
        'incorrect_response': 'Me diga o que você achou que vou registrar.',
        'correct_response': '''Para avaliar e dar nota a um livro na plataforma:

⭐ **Passo a passo:**

1. **Encontre o livro:**
   - Navegue pelo catálogo ("Livros" no menu)
   - Ou acesse "Novos Autores" para livros independentes

2. **Abra a página do livro:**
   - Clique no livro desejado para ver os detalhes

3. **Deixe sua avaliação:**
   - Role até a seção de avaliações/reviews
   - Clique em "Avaliar" ou "Deixar Review"
   - Dê sua nota (1 a 5 estrelas)
   - Escreva sua resenha (opcional, mas recomendado!)

4. **Configure a visibilidade:**
   - Marque "Resenha Pública" para compartilhar com a comunidade
   - Marque "Contém Spoilers" se necessário
   - Indique se recomendaria o livro

✨ **Benefícios:**
- Ganhe XP (pontos de experiência) por deixar avaliações
- Ganhe XP extra se escrever uma resenha detalhada
- Ajude outros leitores a descobrir bons livros
- Participe da comunidade literária

📝 Cada usuário pode deixar apenas uma avaliação por livro, mas pode editá-la depois!''',
        'confidence_score': 1.0,
        'admin_notes': 'Ensina o processo completo de avaliação de livros'
    },
    {
        'knowledge_type': 'general',
        'original_question': 'Quais funcionalidades a plataforma oferece além de buscar livros?',
        'incorrect_response': 'Você pode conversar comigo sobre livros.',
        'correct_response': '''A CG.BookStore oferece muitos recursos além da busca de livros! 🚀

📚 **Biblioteca Pessoal:**
- Organize livros em estantes personalizadas
- Marque livros como "Lendo", "Lido", "Quero Ler"
- Acompanhe seu progresso de leitura

✍️ **Avaliações e Reviews:**
- Avalie livros com estrelas (1-5)
- Escreva resenhas públicas ou privadas
- Veja avaliações de outros leitores
- Marque reviews úteis

🌟 **Novos Autores (Talentos Emergentes):**
- Descubra autores independentes
- Leia capítulos gratuitamente online
- Siga seus autores favoritos
- Interaja com a comunidade

🎯 **Sistema de Gamificação:**
- Ganhe XP realizando atividades
- Suba de nível
- Desbloqueie conquistas
- Acompanhe seu ranking

🤖 **Assistente Literário (Eu!):**
- Recomendações personalizadas
- Análise de estilos literários
- Discussões sobre literatura
- Dúvidas sobre a plataforma

📊 **Dashboard Personalizado:**
- Estatísticas de leitura
- Recomendações baseadas em seu perfil
- Atividades recentes

🔍 **Busca Avançada:**
- Pesquise no catálogo local
- Busque no Google Books
- Importe livros externos

E muito mais! Explore o menu para descobrir todos os recursos. 📖✨''',
        'confidence_score': 1.0,
        'admin_notes': 'Visão geral completa dos recursos da plataforma'
    },
    {
        'knowledge_type': 'general',
        'original_question': 'Como posso ver o perfil de um autor ou escritor?',
        'incorrect_response': 'Posso te contar sobre o autor.',
        'correct_response': '''Para visualizar o perfil de autores na plataforma:

👤 **Autores Emergentes/Independentes:**

1. Acesse a seção "Novos Autores" no menu
2. Clique em qualquer livro de autor independente
3. Na página do livro, clique no nome do autor
4. Ou acesse diretamente: /novos-autores/autor/[username]/

**O que você encontra no perfil:**
- 📝 Biografia do autor
- 📚 Todos os livros publicados
- 📊 Estatísticas (visualizações, seguidores)
- 🌐 Links para redes sociais
- ⭐ Selo de "Verificado" (se aplicável)
- 📖 Foto e informações de contato

📚 **Autores do Catálogo Geral:**
Para autores tradicionais/estabelecidos, as informações aparecem na página de detalhes do livro.

💡 **Dica:** Você pode seguir autores emergentes para receber notificações sobre novos lançamentos!

Quer que eu te ajude a descobrir algum autor específico? 😊''',
        'confidence_score': 1.0,
        'admin_notes': 'Explica como acessar perfis de autores'
    }
]

print("🚀 Adicionando conhecimentos de navegação ao Dbit...\n")

created_count = 0
updated_count = 0
error_count = 0

for entry in knowledge_entries:
    try:
        # Verificar se já existe conhecimento similar
        existing = ChatbotKnowledge.objects.filter(
            original_question=entry['original_question']
        ).first()

        if existing:
            # Atualizar existente
            for key, value in entry.items():
                if key != 'original_question':
                    setattr(existing, key, value)
            existing.created_by = admin_user
            existing.is_active = True
            existing.save()
            print(f"✏️  Atualizado: {entry['original_question'][:60]}...")
            updated_count += 1
        else:
            # Criar novo
            ChatbotKnowledge.objects.create(
                created_by=admin_user,
                is_active=True,
                **entry
            )
            print(f"✅ Criado: {entry['original_question'][:60]}...")
            created_count += 1

    except Exception as e:
        print(f"❌ Erro ao processar: {entry['original_question'][:40]}...")
        print(f"   Erro: {str(e)}")
        error_count += 1

print(f"\n{'='*60}")
print(f"📊 RESUMO:")
print(f"   ✅ Criados: {created_count}")
print(f"   ✏️  Atualizados: {updated_count}")
print(f"   ❌ Erros: {error_count}")
print(f"   📚 Total processado: {len(knowledge_entries)}")
print(f"{'='*60}\n")

if error_count == 0:
    print("🎉 Todos os conhecimentos foram adicionados com sucesso!")
    print("\n💡 Agora o Dbit sabe direcionar usuários para:")
    print("   • Avaliações e reviews de livros")
    print("   • Seção de Novos Autores")
    print("   • Perfis de autores")
    print("   • Recursos gerais da plataforma")
    print("\n🧠 O Dbit está mais inteligente e útil!")
else:
    print(f"⚠️  Concluído com {error_count} erro(s). Verifique os detalhes acima.")
