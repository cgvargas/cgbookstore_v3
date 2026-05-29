from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Book
from debates.models import DebateTopic, DebatePost, DebateVote

@override_settings(RATELIMIT_ENABLE=False)
class DebateXPTests(TestCase):
    """Testes unitários para validar a lógica de concessão de XP no app debates."""

    def setUp(self):
        # Criar usuários
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Criar livro
        self.book = Book.objects.create(
            title="Livro de Teste",
            publication_date="2026-01-01"
        )
        
    def test_topic_creation_grants_xp(self):
        """Testa se a criação de um tópico de debate concede +30 XP ao criador."""
        self.client.login(username='user1', password='pass123')
        initial_xp = self.user1.profile.total_xp
        
        # Criar tópico via post
        response = self.client.post(
            reverse('debates:create_topic', kwargs={'book_id': self.book.id}),
            {'title': 'Tópico de Teste', 'description': 'Descrição do tópico'}
        )
        self.assertEqual(response.status_code, 302) # Redireciona para o tópico criado
        
        # Atualizar user
        self.user1.profile.refresh_from_db()
        self.assertEqual(self.user1.profile.total_xp, initial_xp + 30)

    def test_post_creation_grants_xp(self):
        """Testa se a criação de uma resposta em tópico concede +5 XP ao autor do post."""
        # Criar tópico primeiro
        topic = DebateTopic.objects.create(
            book=self.book,
            creator=self.user1,
            title="Tópico",
            description="Descrição"
        )
        
        # Login user2
        self.client.login(username='user2', password='pass123')
        initial_xp = self.user2.profile.total_xp
        
        # Criar resposta via AJAX (retorna JSON)
        response = self.client.post(
            reverse('debates:create_post', kwargs={'topic_slug': topic.slug}),
            {'content': 'Uma resposta de teste'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        self.user2.profile.refresh_from_db()
        self.assertEqual(self.user2.profile.total_xp, initial_xp + 5)

    def test_upvote_grants_and_removes_xp(self):
        """Testa se receber upvote concede +2 XP, e remover/trocar reverte a pontuação."""
        # Criar tópico e post do user1
        topic = DebateTopic.objects.create(
            book=self.book,
            creator=self.user1,
            title="Tópico",
            description="Descrição"
        )
        post = DebatePost.objects.create(
            topic=topic,
            author=self.user1,
            content="Conteúdo do post"
        )
        
        # User 1 tem XP inicial
        self.user1.profile.refresh_from_db()
        initial_xp = self.user1.profile.total_xp
        
        # Login user2 para votar no post do user1
        self.client.login(username='user2', password='pass123')
        
        # 1. Dar upvote (+2 XP)
        response = self.client.post(
            reverse('debates:vote_post', kwargs={'post_id': post.id}),
            {'vote_type': 'up'}
        )
        self.assertEqual(response.status_code, 200)
        self.user1.profile.refresh_from_db()
        self.assertEqual(self.user1.profile.total_xp, initial_xp + 2)
        
        # 2. Remover upvote (-2 XP)
        response = self.client.post(
            reverse('debates:vote_post', kwargs={'post_id': post.id}),
            {'vote_type': 'up'}
        )
        self.assertEqual(response.status_code, 200)
        self.user1.profile.refresh_from_db()
        self.assertEqual(self.user1.profile.total_xp, initial_xp)
        
        # 3. Dar downvote (não altera XP do autor)
        response = self.client.post(
            reverse('debates:vote_post', kwargs={'post_id': post.id}),
            {'vote_type': 'down'}
        )
        self.assertEqual(response.status_code, 200)
        self.user1.profile.refresh_from_db()
        self.assertEqual(self.user1.profile.total_xp, initial_xp)
        
        # 4. Trocar downvote para upvote (+2 XP)
        response = self.client.post(
            reverse('debates:vote_post', kwargs={'post_id': post.id}),
            {'vote_type': 'up'}
        )
        self.assertEqual(response.status_code, 200)
        self.user1.profile.refresh_from_db()
        self.assertEqual(self.user1.profile.total_xp, initial_xp + 2)
        
        # 5. Trocar upvote para downvote (-2 XP)
        response = self.client.post(
            reverse('debates:vote_post', kwargs={'post_id': post.id}),
            {'vote_type': 'down'}
        )
        self.assertEqual(response.status_code, 200)
        self.user1.profile.refresh_from_db()
        self.assertEqual(self.user1.profile.total_xp, initial_xp)
