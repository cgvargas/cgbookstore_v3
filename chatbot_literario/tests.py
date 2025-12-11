"""
Testes automatizados para o app Chatbot Literário.
Cobertura: ChatSession, ChatMessage, ChatbotKnowledge
"""
from django.test import TestCase
from django.contrib.auth.models import User
from chatbot_literario.models import ChatSession, ChatMessage, ChatbotKnowledge, ConversationContext


class ChatSessionModelTest(TestCase):
    """Testes para o model ChatSession."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = ChatSession.objects.create(
            user=self.user,
            title="Conversa sobre ficção científica"
        )

    def test_session_creation(self):
        """Testa criação de sessão."""
        self.assertEqual(self.session.user, self.user)
        self.assertTrue(self.session.is_active)

    def test_session_str(self):
        """Testa representação string da sessão."""
        self.assertIn("Conversa sobre ficção", str(self.session))

    def test_session_messages_count(self):
        """Testa contagem de mensagens."""
        self.assertEqual(self.session.get_messages_count(), 0)
        
        ChatMessage.objects.create(
            session=self.session,
            role='user',
            content='Olá!'
        )
        self.assertEqual(self.session.get_messages_count(), 1)

    def test_session_generate_title(self):
        """Testa geração automática de título."""
        session = ChatSession.objects.create(user=self.user)
        ChatMessage.objects.create(
            session=session,
            role='user',
            content='Recomende livros de mistério'
        )
        session.generate_title()
        self.assertIsNotNone(session.title)

    def test_multiple_sessions_per_user(self):
        """Testa múltiplas sessões por usuário."""
        session2 = ChatSession.objects.create(
            user=self.user,
            title="Segunda conversa"
        )
        sessions = ChatSession.objects.filter(user=self.user)
        self.assertEqual(sessions.count(), 2)


class ChatMessageModelTest(TestCase):
    """Testes para o model ChatMessage."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.session = ChatSession.objects.create(
            user=self.user,
            title="Conversa teste"
        )

    def test_user_message_creation(self):
        """Testa criação de mensagem do usuário."""
        message = ChatMessage.objects.create(
            session=self.session,
            role='user',
            content='Qual é o melhor livro de Asimov?'
        )
        self.assertTrue(message.is_from_user)
        self.assertFalse(message.is_from_assistant)

    def test_assistant_message_creation(self):
        """Testa criação de mensagem do assistente."""
        message = ChatMessage.objects.create(
            session=self.session,
            role='assistant',
            content='Recomendo "Fundação", é um clássico!'
        )
        self.assertFalse(message.is_from_user)
        self.assertTrue(message.is_from_assistant)

    def test_message_str(self):
        """Testa representação string da mensagem."""
        message = ChatMessage.objects.create(
            session=self.session,
            role='user',
            content='Olá, chatbot!'
        )
        self.assertIn('user', str(message))

    def test_messages_ordering(self):
        """Testa ordenação de mensagens (cronológica)."""
        msg1 = ChatMessage.objects.create(
            session=self.session,
            role='user',
            content='Primeira mensagem'
        )
        msg2 = ChatMessage.objects.create(
            session=self.session,
            role='assistant',
            content='Segunda mensagem'
        )
        messages = ChatMessage.objects.filter(session=self.session)
        self.assertEqual(messages[0], msg1)
        self.assertEqual(messages[1], msg2)


class ChatbotKnowledgeModelTest(TestCase):
    """Testes para o model ChatbotKnowledge (Knowledge Base)."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.knowledge = ChatbotKnowledge.objects.create(
            question_pattern="Qual é o melhor livro de Asimov?",
            answer="O mais famoso é 'Fundação', mas 'Eu, Robô' também é excelente.",
            knowledge_type='book_info',
            created_by=self.admin,
            is_active=True,
            confidence_score=0.95
        )

    def test_knowledge_creation(self):
        """Testa criação de conhecimento."""
        self.assertIn("Asimov", self.knowledge.question_pattern)
        self.assertIn("Fundação", self.knowledge.answer)
        self.assertTrue(self.knowledge.is_active)

    def test_knowledge_str(self):
        """Testa representação string do conhecimento."""
        self.assertIn("melhor livro", str(self.knowledge))

    def test_knowledge_increment_usage(self):
        """Testa incremento de uso."""
        initial_count = self.knowledge.times_used
        self.knowledge.increment_usage()
        self.assertEqual(self.knowledge.times_used, initial_count + 1)

    def test_knowledge_types(self):
        """Testa diferentes tipos de conhecimento."""
        types = ['book_info', 'author_info', 'general', 'correction']
        for ktype in types:
            knowledge = ChatbotKnowledge.objects.create(
                question_pattern=f"Pergunta tipo {ktype}",
                answer=f"Resposta tipo {ktype}",
                knowledge_type=ktype,
                created_by=self.admin
            )
            self.assertEqual(knowledge.knowledge_type, ktype)


class ConversationContextModelTest(TestCase):
    """Testes para o model ConversationContext."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.context = ConversationContext.objects.create(user=self.user)

    def test_context_creation(self):
        """Testa criação de contexto."""
        self.assertEqual(self.context.user, self.user)

    def test_context_add_genre(self):
        """Testa adição de gênero favorito."""
        self.context.add_genre("Ficção Científica")
        self.assertIn("Ficção Científica", self.context.favorite_genres)

    def test_context_add_author(self):
        """Testa adição de autor favorito."""
        self.context.add_author("Isaac Asimov")
        self.assertIn("Isaac Asimov", self.context.favorite_authors)

    def test_context_add_interest(self):
        """Testa adição de interesse."""
        self.context.add_interest("Livros curtos")
        self.assertIn("Livros curtos", self.context.interests)

    def test_context_set_preference(self):
        """Testa definição de preferência."""
        self.context.set_preference("reading_speed", "fast")
        self.assertEqual(self.context.reading_preferences.get("reading_speed"), "fast")
