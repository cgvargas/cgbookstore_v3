"""
Testes automatizados para os models do app Accounts.
Cobertura: UserProfile, BookShelf, Achievement, Badge
"""
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone
from accounts.models import UserProfile, BookShelf, Badge, UserBadge
from core.models import Book


class UserProfileModelTest(TestCase):
    """Testes para o model UserProfile."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # UserProfile é criado automaticamente via signal
        self.profile = self.user.profile

    def test_profile_creation_via_signal(self):
        """Testa criação automática de perfil via signal."""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_str(self):
        """Testa representação string do perfil."""
        self.assertIn(self.user.username, str(self.profile))

    def test_profile_initial_xp(self):
        """Testa XP inicial do perfil."""
        self.assertEqual(self.profile.total_xp, 0)

    def test_profile_calculate_level(self):
        """Testa cálculo de nível baseado em XP."""
        # Nível 1 = 100 XP, Nível 2 = 400 XP, etc. (sqrt(XP/100) + 1)
        self.profile.total_xp = 0
        self.profile.save()
        self.assertEqual(self.profile.calculate_level(), 1)

        self.profile.total_xp = 100
        self.profile.save()
        self.assertEqual(self.profile.calculate_level(), 2)

        self.profile.total_xp = 400
        self.profile.save()
        self.assertEqual(self.profile.calculate_level(), 3)

    def test_profile_add_xp(self):
        """Testa adição de XP."""
        old_xp = self.profile.total_xp
        self.profile.add_xp(50)
        self.assertEqual(self.profile.total_xp, old_xp + 50)

    def test_profile_xp_for_next_level(self):
        """Testa cálculo de XP para próximo nível."""
        self.profile.total_xp = 0
        self.profile.save()
        xp_needed = self.profile.xp_for_next_level
        self.assertGreater(xp_needed, 0)

    def test_profile_level_name(self):
        """Testa nome do nível."""
        level_name = self.profile.level_name
        self.assertIsInstance(level_name, str)
        self.assertGreater(len(level_name), 0)

    def test_profile_streak_update(self):
        """Testa atualização de streak."""
        self.profile.update_streak()
        self.assertEqual(self.profile.streak_days, 1)

    def test_profile_streak_reset(self):
        """Testa reset de streak."""
        self.profile.streak_days = 5
        self.profile.save()
        self.profile.reset_streak()
        self.assertEqual(self.profile.streak_days, 0)

    def test_profile_is_premium_active_false(self):
        """Testa verificação de premium (não ativo)."""
        self.profile.is_premium = False
        self.profile.save()
        self.assertFalse(self.profile.is_premium_active())

    def test_profile_is_premium_active_true(self):
        """Testa verificação de premium (ativo)."""
        self.profile.is_premium = True
        self.profile.premium_expires_at = timezone.now() + timedelta(days=30)
        self.profile.save()
        self.assertTrue(self.profile.is_premium_active())

    def test_profile_is_premium_expired(self):
        """Testa verificação de premium (expirado)."""
        self.profile.is_premium = True
        self.profile.premium_expires_at = timezone.now() - timedelta(days=1)
        self.profile.save()
        self.assertFalse(self.profile.is_premium_active())


class BookShelfModelTest(TestCase):
    """Testes para o model BookShelf."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title="Test Book",
            publication_date=date(2024, 1, 1),
        )

    def test_bookshelf_add_to_shelf(self):
        """Testa adição de livro à prateleira."""
        shelf = BookShelf.objects.create(
            user=self.user,
            book=self.book,
            shelf_type='quer-ler'
        )
        self.assertEqual(shelf.user, self.user)
        self.assertEqual(shelf.book, self.book)
        self.assertEqual(shelf.shelf_type, 'quer-ler')

    def test_bookshelf_str(self):
        """Testa representação string da prateleira."""
        shelf = BookShelf.objects.create(
            user=self.user,
            book=self.book,
            shelf_type='lendo'
        )
        self.assertIn(self.user.username, str(shelf))
        self.assertIn(self.book.title, str(shelf))

    def test_bookshelf_shelf_types(self):
        """Testa diferentes tipos de prateleira."""
        shelf_types = ['favoritos', 'lidos', 'lendo', 'quer-ler']
        for i, shelf_type in enumerate(shelf_types):
            book = Book.objects.create(
                title=f"Book {i}",
                publication_date=date(2024, 1, 1),
            )
            shelf = BookShelf.objects.create(
                user=self.user,
                book=book,
                shelf_type=shelf_type
            )
            self.assertEqual(shelf.shelf_type, shelf_type)

    def test_bookshelf_unique_per_user_book(self):
        """Testa que não pode ter duplicatas na mesma prateleira."""
        BookShelf.objects.create(
            user=self.user,
            book=self.book,
            shelf_type='quer-ler',
            custom_shelf_name=''
        )
        # Tentar criar novamente deve falhar ou atualizar
        with self.assertRaises(Exception):
            BookShelf.objects.create(
                user=self.user,
                book=self.book,
                shelf_type='quer-ler',
                custom_shelf_name=''
            )


class BadgeModelTest(TestCase):
    """Testes para os models Badge e UserBadge."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.badge = Badge.objects.create(
            name="Primeiro Livro",
            description="Concedido ao adicionar o primeiro livro",
            icon="📚",
            rarity="bronze",
            category="reading"
        )

    def test_badge_creation(self):
        """Testa criação de badge."""
        self.assertEqual(self.badge.name, "Primeiro Livro")
        self.assertEqual(self.badge.rarity, "bronze")

    def test_badge_str(self):
        """Testa representação string do badge."""
        self.assertEqual(str(self.badge), "📚 Primeiro Livro (🥉 Bronze)")

    def test_user_badge_award(self):
        """Testa concessão de badge ao usuário."""
        user_badge = UserBadge.objects.create(
            user=self.user,
            badge=self.badge
        )
        self.assertEqual(user_badge.user, self.user)
        self.assertEqual(user_badge.badge, self.badge)
        self.assertIsNotNone(user_badge.earned_at)
